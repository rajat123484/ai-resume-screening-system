from backend.ats_scorer import analyze_resume


FILE_PATH = "data/resumes/RajatResume (1).pdf"


result = analyze_resume(FILE_PATH)


print("=" * 55)
print("AI ATS RESUME CHECKER")
print("=" * 55)

print()
print(f"ATS SCORE: {result['ats_score']} / 100")

print()
print("-" * 55)
print("PARSING & STRUCTURE")
print("-" * 55)

print(
    "Parsing:",
    result["parsing_quality"]["score"]
)

print(
    "Contact:",
    result["contact"]["score"]
)

print(
    "Standard Sections:",
    result["standard_sections"]["score"]
)

print(
    "Section Completeness:",
    result["section_completeness"]
)

print(
    "Education:",
    result["education"]["score"]
)

print(
    "Dates:",
    result["dates"]["score"]
)

print(
    "Columns:",
    result["columns"]["score"]
)

print(
    "Tables:",
    result["tables"]["score"]
)

print(
    "Images:",
    result["images"]["score"]
)

print(
    "Headers/Footers:",
    result["headers_footers"]["score"]
)

print()
print("-" * 55)
print("CONTENT CHECKS")
print("-" * 55)

print(
    "Bullets:",
    result["bullets"]["score"]
)

print(
    "Action Verbs:",
    result["action_verbs"]["score"]
)

print(
    "Quantified Achievements:",
    result["quantified_achievements"]["score"]
)

print(
    "Repetition:",
    result["repetition"]["score"]
)

print(
    "Filler Words:",
    result["filler_words"]["score"]
)

print(
    "Passive Voice:",
    result["passive_voice"]["score"]
)

print(
    "Personal Pronouns:",
    result["personal_pronouns"]["score"]
)

print(
    "Length:",
    result["length"]["score"]
)

print(
    "Bullet Length:",
    result["bullet_length"]["score"]
)

print(
    "Skills Section:",
    result["skills"]["score"]
)

print(
    "Professional Links:",
    result["links"]["score"]
)

print(
    "Language:",
    result["language"]["score"]
)

print(
    "Keyword Stuffing:",
    result["keyword_stuffing"]["score"]
)

print()
print("-" * 55)
print("RESUME INFORMATION")
print("-" * 55)

print(
    "Pages:",
    result["pages"]["count"]
)

print(
    "Word Count:",
    result["length"]["word_count"]
)

print(
    "Bullet Count:",
    result["bullets"]["count"]
)

print(
    "Images:",
    result["images"]["total_images"]
)

print(
    "Tables:",
    result["tables"]["count"]
)

print(
    "Columns Detected:",
    result["columns"]["detected"]
)

print()
print("-" * 55)
print("DETECTED SECTIONS")
print("-" * 55)

for section in result["detected_sections"]:
    print("-", section)

print()
print("-" * 55)
print("ISSUES")
print("-" * 55)

if result["issues"]:

    for issue in result["issues"]:
        print("-", issue)

else:

    print("No major ATS issues detected.")