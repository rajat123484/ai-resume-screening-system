from backend.resume_parser import extract_text
from backend.ats_scorer import analyze_resume
from backend.jd_matcher import analyze_jd_match

import os


def calculate_final_score(ats_score, jd_match_score):
    """
    Final score:
    30% ATS Compatibility
    70% JD Match
    """

    final_score = (
        ats_score * 0.30
        + jd_match_score * 0.70
    )

    return round(final_score, 2)


def get_decision(score):
    """
    Candidate decision based on final score.
    """

    if score >= 80:
        return "SHORTLIST"

    elif score >= 60:
        return "REVIEW"

    else:
        return "NOT SHORTLIST"


def rank_candidates(resume_folder, job_description):

    candidates = []

    for filename in os.listdir(resume_folder):

        # Support both PDF and DOCX
        if not filename.lower().endswith(
            (".pdf", ".docx")
        ):
            continue

        file_path = os.path.join(
            resume_folder,
            filename
        )

        # -------------------------
        # 1. Extract Resume Text
        # -------------------------

        resume_text = extract_text(
            file_path
        )

        # -------------------------
        # 2. ATS Analysis
        # -------------------------

        ats_result = analyze_resume(
            file_path
        )

        ats_score = ats_result[
            "ats_score"
        ]

        # -------------------------
        # 3. JD Matching
        # -------------------------

        jd_result = analyze_jd_match(
            resume_text,
            job_description
        )

        semantic_score = jd_result[
            "semantic_score"
        ]

        skill_match_score = jd_result[
            "skill_match_score"
        ]

        jd_match_score = jd_result[
            "jd_match_score"
        ]

        # -------------------------
        # 4. Final Score
        # -------------------------

        final_score = calculate_final_score(
            ats_score,
            jd_match_score
        )

        # -------------------------
        # 5. Candidate Result
        # -------------------------

        candidates.append({

            "filename": filename,

            "ats_score": ats_score,

            "semantic_score":
                semantic_score,

            "skill_match_score":
                skill_match_score,

            "jd_match_score":
                jd_match_score,

            "final_score":
                final_score,

            "matching_skills":
                jd_result[
                    "matching_skills"
                ],

            "missing_skills":
                jd_result[
                    "missing_skills"
                ]
        })

    # -------------------------
    # 6. Rank Candidates
    # -------------------------

    candidates.sort(
        key=lambda x: x["final_score"],
        reverse=True
    )

    # -------------------------
    # 7. Assign Rank + Decision
    # -------------------------

    for index, candidate in enumerate(
        candidates,
        start=1
    ):

        candidate["rank"] = index

        candidate["decision"] = get_decision(
            candidate["final_score"]
        )

    return candidates