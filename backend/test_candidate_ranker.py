from backend.candidate_ranker import rank_candidates


resume_folder = "data/resumes"


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


results = rank_candidates(
    resume_folder,
    job_description
)


print("=" * 70)
print("AI CANDIDATE SHORTLISTING SYSTEM")
print("=" * 70)


if not results:

    print("\nNo PDF resumes found.")

else:

    for candidate in results:

        print(f"\nRank: {candidate['rank']}")

        print(
            f"Resume: {candidate['filename']}"
        )

        print(
            f"ATS Score: {candidate['ats_score']}"
        )

        print(
            f"JD Match Score: {candidate['jd_match_score']}"
        )

        print(
            f"Final Score: {candidate['final_score']}"
        )

        print(
            f"Decision: {candidate['decision']}"
        )

        print("\nMatching Skills:")

        if candidate["matching_skills"]:
            print(
                ", ".join(
                    candidate["matching_skills"]
                )
            )
        else:
            print("None")

        print("\nMissing Skills:")

        if candidate["missing_skills"]:
            print(
                ", ".join(
                    candidate["missing_skills"]
                )
            )
        else:
            print("None")

        print("-" * 70)