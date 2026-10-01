from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re


model = SentenceTransformer("all-MiniLM-L6-v2")


SKILLS = [
    "Python",
    "Java",
    "C++",
    "JavaScript",
    "SQL",
    "MySQL",
    "PostgreSQL",
    "Excel",
    "Power BI",
    "Tableau",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "TensorFlow",
    "PyTorch",
    "spaCy",
    "Git",
    "GitHub",
    "AWS",
    "Docker",
    "FastAPI",
    "React",
    "HTML",
    "CSS",
    "Data Analysis",
    "Data Analytics",
    "Data Visualization",
    "Machine Learning",
    "Deep Learning",
    "Generative AI",
    "Gen AI",
    "DSA",
    "DBMS",
    "OOP",
]


def extract_skills(text):
    """
    Extract known technical skills from text.
    """

    found = []
    text_lower = text.lower()

    for skill in SKILLS:

        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        if re.search(pattern, text_lower):
            found.append(skill)

    return found


def calculate_similarity(resume_text, job_description):
    """
    Calculate semantic similarity between resume and JD.
    """

    if not resume_text.strip() or not job_description.strip():
        return 0

    resume_embedding = model.encode([resume_text])
    jd_embedding = model.encode([job_description])

    similarity = cosine_similarity(
        resume_embedding,
        jd_embedding
    )[0][0]

    score = round(float(similarity) * 100, 2)

    return score


def analyze_jd_match(resume_text, job_description):
    """
    Complete JD matching analysis.
    """

    semantic_score = calculate_similarity(
        resume_text,
        job_description
    )

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    matching_skills = [
        skill
        for skill in jd_skills
        if skill.lower() in [s.lower() for s in resume_skills]
    ]

    missing_skills = [
        skill
        for skill in jd_skills
        if skill.lower() not in [s.lower() for s in resume_skills]
    ]

    if jd_skills:

        skill_match_score = round(
            (len(matching_skills) / len(jd_skills)) * 100,
            2
        )

    else:
        skill_match_score = 0

    final_jd_score = round(
        (semantic_score * 0.7) +
        (skill_match_score * 0.3),
        2
    )

    return {
        "jd_match_score": final_jd_score,
        "semantic_score": semantic_score,
        "skill_match_score": skill_match_score,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "jd_skills": jd_skills
    }