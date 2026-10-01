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
    "NLTK",
    "BeautifulSoup",
    "Requests",
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
    "EDA",
    "Dashboarding",
    "Machine Learning",
    "Deep Learning",
    "Generative AI",
    "Gen AI",
    "DSA",
    "DBMS",
    "OOP"
]


def extract_skills(text):

    found_skills = []

    text_lower = text.lower()

    for skill in SKILLS:
        if skill.lower() in text_lower:
            found_skills.append(skill)

    return found_skills


def extract_sections(text):

    sections = {}

    lines = text.splitlines()

    current_section = None

    for line in lines:

        line = line.strip()

        if not line:
            continue

        heading = line.upper()

        if heading == "EDUCATION":
            current_section = "education"
            sections[current_section] = []
            continue

        elif heading == "EXPERIENCE":
            current_section = "experience"
            sections[current_section] = []
            continue

        elif heading == "PROJECTS":
            current_section = "projects"
            sections[current_section] = []
            continue

        elif heading == "SKILLS":
            current_section = "skills"
            sections[current_section] = []
            continue

        elif heading in ["TRAINING & COURSES", "TRAINING", "COURSES"]:
            current_section = "training"
            sections[current_section] = []
            continue

        elif heading == "ACHIEVEMENTS":
            current_section = "achievements"
            sections[current_section] = []
            continue

        if current_section:
            sections[current_section].append(line)

    return sections