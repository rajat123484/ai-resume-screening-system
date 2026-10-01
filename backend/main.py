from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

import os
import shutil
import tempfile
import json

from backend.ats_scorer import analyze_resume
from backend.candidate_ranker import (
    rank_candidates,
    get_decision
)
from backend.database import get_connection
from backend.resume_parser import extract_text


app = FastAPI(
    title="AI Resume Screening System",
    description="AI-Based Resume Screening and Candidate Shortlisting System",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# CUSTOM OPENAPI
# =========================================================

def custom_openapi():

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["openapi"] = "3.0.3"

    if (
        "components" in openapi_schema
        and "schemas" in openapi_schema["components"]
    ):

        if (
            "Body_upload_resume_upload_resume_post"
            in openapi_schema["components"]["schemas"]
        ):

            upload_schema = openapi_schema["components"]["schemas"][
                "Body_upload_resume_upload_resume_post"
            ]

            upload_schema["properties"]["file"] = {
                "type": "string",
                "format": "binary"
            }

        if (
            "Body_screen_candidates_screen_candidates_post"
            in openapi_schema["components"]["schemas"]
        ):

            screen_schema = openapi_schema["components"]["schemas"][
                "Body_screen_candidates_screen_candidates_post"
            ]

            screen_schema["properties"]["resumes"] = {
                "type": "array",
                "items": {
                    "type": "string",
                    "format": "binary"
                },
                "description": "Upload multiple PDF or DOCX resumes"
            }

    app.openapi_schema = openapi_schema

    return app.openapi_schema


app.openapi = custom_openapi


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "AI Resume Screening System API is running!"
    }


# =========================================================
# UPLOAD SINGLE RESUME
# =========================================================

@app.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...)
):

    upload_folder = "data/resumes"

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    allowed_extensions = [
        ".pdf",
        ".docx"
    ]

    file_extension = os.path.splitext(
        file.filename
    )[1].lower()

    if file_extension not in allowed_extensions:

        return {
            "error": "Only PDF and DOCX resumes are supported."
        }

    file_path = os.path.join(
        upload_folder,
        file.filename
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    result = analyze_resume(
        file_path
    )

    return {
        "filename": file.filename,
        "analysis": result
    }


# =========================================================
# SCREEN CANDIDATES
# =========================================================

@app.post("/screen-candidates")
async def screen_candidates(

    job_description: str = Form(...),

    resumes: list[UploadFile] = File(...)
):

    if not resumes:

        return {
            "message": "No resumes uploaded.",
            "candidates": []
        }


    # =====================================================
    # TEMPORARY FOLDER
    # =====================================================

    with tempfile.TemporaryDirectory() as temp_folder:

        uploaded_files = []


        # =================================================
        # SAVE TEMPORARY RESUMES
        # =================================================

        for resume in resumes:

            if not resume.filename:
                continue

            file_extension = os.path.splitext(
                resume.filename
            )[1].lower()

            if file_extension not in [
                ".pdf",
                ".docx"
            ]:
                continue

            file_path = os.path.join(
                temp_folder,
                resume.filename
            )

            with open(
                file_path,
                "wb"
            ) as buffer:

                shutil.copyfileobj(
                    resume.file,
                    buffer
                )

            uploaded_files.append(
                resume.filename
            )


        # =================================================
        # CHECK FILES
        # =================================================

        if not uploaded_files:

            return {
                "message": "No valid PDF or DOCX resumes uploaded.",
                "candidates": []
            }


        # =================================================
        # EXTRACT JOB TITLE
        # =================================================

        job_title = "Resume Screening Job"

        first_lines = job_description.splitlines()

        for line in first_lines:

            line = line.strip()

            if line:

                job_title = line[:255]

                break


        # =================================================
        # CONNECT DATABASE
        # =================================================

        connection = get_connection()

        cursor = connection.cursor()


        try:

            # =============================================
            # 1. CREATE JOB
            # =============================================

            cursor.execute(
                """
                INSERT INTO jobs (
                    job_title,
                    job_description
                )
                VALUES (%s, %s)
                RETURNING id;
                """,
                (
                    job_title,
                    job_description
                )
            )

            job_id = cursor.fetchone()[0]


            # =============================================
            # 2. CREATE SCREENING RUN
            # =============================================

            cursor.execute(
                """
                INSERT INTO screening_runs (
                    job_id,
                    total_candidates,
                    status
                )
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (
                    job_id,
                    len(uploaded_files),
                    "PROCESSING"
                )
            )

            screening_run_id = cursor.fetchone()[0]


            # =============================================
            # 3. RUN AI SCREENING
            # =============================================

            candidates = rank_candidates(
                temp_folder,
                job_description
            )


            # =============================================
            # 4. SAVE CANDIDATES + RESULTS
            # =============================================

            for candidate in candidates:

                filename = candidate["filename"]

                file_path = os.path.join(
                    temp_folder,
                    filename
                )


                # =========================================
                # EXTRACT RESUME TEXT
                # =========================================

                resume_text = extract_text(
                    file_path
                )


                # =========================================
                # INSERT CANDIDATE
                # =========================================

                cursor.execute(
                    """
                    INSERT INTO candidates (
                        resume_filename,
                        resume_file_type,
                        extracted_text
                    )
                    VALUES (%s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        filename,
                        os.path.splitext(filename)[1].lower(),
                        resume_text
                    )
                )

                candidate_id = cursor.fetchone()[0]


                # =========================================
                # ATS ANALYSIS
                # =========================================

                ats_analysis = analyze_resume(
                    file_path
                )


                # =========================================
                # DECISION
                # =========================================

                decision = get_decision(
                    candidate["final_score"]
                )

                candidate["decision"] = decision


                # =========================================
                # SAVE SCREENING RESULT
                # =========================================

                cursor.execute(
                    """
                    INSERT INTO screening_results (

                        screening_run_id,

                        job_id,

                        candidate_id,

                        ats_score,

                        semantic_score,

                        skill_match_score,

                        jd_match_score,

                        final_score,

                        decision,

                        rank,

                        matching_skills,

                        missing_skills,

                        jd_skills,

                        ats_analysis

                    )
                    VALUES (

                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s::jsonb,
                        %s::jsonb,
                        %s::jsonb,
                        %s::jsonb

                    );
                    """,
                    (

                        screening_run_id,

                        job_id,

                        candidate_id,

                        candidate["ats_score"],

                        candidate["semantic_score"],

                        candidate["skill_match_score"],

                        candidate["jd_match_score"],

                        candidate["final_score"],

                        decision,

                        candidate["rank"],

                        json.dumps(
                            candidate["matching_skills"]
                        ),

                        json.dumps(
                            candidate["missing_skills"]
                        ),

                        json.dumps(
                            ats_analysis.get(
                                "jd_skills",
                                []
                            )
                        ),

                        json.dumps(
                            ats_analysis
                        )

                    )
                )


            # =============================================
            # 5. COUNT DECISIONS
            # =============================================

            shortlisted_count = sum(
                1
                for candidate in candidates
                if candidate["decision"] == "SHORTLIST"
            )

            review_count = sum(
                1
                for candidate in candidates
                if candidate["decision"] == "REVIEW"
            )

            rejected_count = sum(
                1
                for candidate in candidates
                if candidate["decision"] == "NOT SHORTLIST"
            )


            # =============================================
            # 6. UPDATE SCREENING RUN
            # =============================================

            cursor.execute(
                """
                UPDATE screening_runs
                SET
                    total_candidates = %s,
                    shortlisted_count = %s,
                    review_count = %s,
                    rejected_count = %s,
                    completed_at = NOW(),
                    status = 'COMPLETED'
                WHERE id = %s;
                """,
                (
                    len(candidates),

                    shortlisted_count,

                    review_count,

                    rejected_count,

                    screening_run_id
                )
            )


            # =============================================
            # 7. COMMIT DATABASE
            # =============================================

            connection.commit()


            # =============================================
            # 8. RETURN RESULT
            # =============================================

            return {
                "message":
                    "Candidate screening completed successfully.",

                "job_id":
                    str(job_id),

                "screening_run_id":
                    str(screening_run_id),

                "total_candidates":
                    len(candidates),

                "shortlisted_count":
                    shortlisted_count,

                "review_count":
                    review_count,

                "rejected_count":
                    rejected_count,

                "candidates":
                    candidates
            }


        except Exception as error:

            # =============================================
            # ROLLBACK IF ERROR
            # =============================================

            connection.rollback()

            return {
                "error":
                    "Database screening failed.",

                "details":
                    str(error)
            }


        finally:

            cursor.close()

            connection.close()