from backend.resume_parser import extract_text_from_pdf
from backend.jd_matcher import analyze_jd_match


resume_path = "data/resumes/RajatResume (1).pdf"


job_description = """
We are looking for a Data Analyst.

Required skills:
Python, SQL, Excel, Power BI, Tableau,
Pandas, NumPy, Data Analysis,
Data Visualization and Statistics.

The candidate should be able to analyze datasets,
create dashboards, generate business insights,
and communicate data-driven findings.
"""


resume_text = extract_text_from_pdf(resume_path)

result = analyze_jd_match(
    resume_text,
    job_description
)


print("=" * 60)
print("AI JD MATCHING SYSTEM")
print("=" * 60)

print(f"\nJD MATCH SCORE: {result['jd_match_score']} / 100")

print(f"\nSemantic Score: {result['semantic_score']} / 100")

print(f"Skill Match Score: {result['skill_match_score']} / 100")

print("\nMatching Skills:")
for skill in result["matching_skills"]:
    print(f"✓ {skill}")

print("\nMissing Skills:")
for skill in result["missing_skills"]:
    print(f"✗ {skill}")

print("\nJD Skills:")
for skill in result["jd_skills"]:
    print(f"- {skill}")