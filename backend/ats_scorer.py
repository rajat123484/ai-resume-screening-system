# backend/ats_scorer.py

import os
import re
import math
import pymupdf

from collections import Counter
from docx import Document


# ============================================================
# ATS CHECKER
# Standalone Resume ATS Analysis
# Supports PDF + DOCX
# ============================================================


# ============================================================
# STANDARD ATS SECTION HEADINGS
# ============================================================

SECTION_ALIASES = {

    "summary": {
        "SUMMARY",
        "PROFESSIONAL SUMMARY",
        "PROFILE",
        "OBJECTIVE",
        "CAREER OBJECTIVE",
    },

    "experience": {
        "EXPERIENCE",
        "WORK EXPERIENCE",
        "PROFESSIONAL EXPERIENCE",
        "EMPLOYMENT",
        "INTERNSHIP",
        "INTERNSHIPS",
    },

    "education": {
        "EDUCATION",
        "ACADEMIC BACKGROUND",
        "QUALIFICATIONS",
    },

    "skills": {
        "SKILLS",
        "TECHNICAL SKILLS",
        "TECHNOLOGY",
        "TECHNOLOGIES",
        "TECHNICAL SKILLS & TOOLS",
    },

    "projects": {
        "PROJECTS",
        "ACADEMIC PROJECTS",
        "PERSONAL PROJECTS",
        "PROJECT EXPERIENCE",
    },

    "certifications": {
        "CERTIFICATIONS",
        "CERTIFICATES",
    },

    "training": {
        "TRAINING",
        "COURSES",
        "TRAINING & COURSES",
        "TRAINING / COURSES",
        "TRAINING AND COURSES",
    },

    "achievements": {
        "ACHIEVEMENTS",
        "AWARDS",
        "ACCOMPLISHMENTS",
    },

    "leadership": {
        "LEADERSHIP",
        "LEADERSHIP EXPERIENCE",
    },

    "volunteering": {
        "VOLUNTEERING",
        "VOLUNTEER EXPERIENCE",
    },
}


# ============================================================
# ACTION VERBS
# ============================================================

ACTION_VERBS = {

    "achieved",
    "analyzed",
    "automated",
    "built",
    "created",
    "designed",
    "developed",
    "deployed",
    "engineered",
    "evaluated",
    "implemented",
    "improved",
    "integrated",
    "launched",
    "led",
    "managed",
    "optimized",
    "organized",
    "performed",
    "processed",
    "programmed",
    "reduced",
    "resolved",
    "tested",
    "trained",
    "visualized",
    "configured",
    "conducted",
    "delivered",
    "generated",
    "extracted",
    "maintained",
    "migrated",
    "monitored",
    "researched",
    "streamlined",
    "transformed",
    "wrote",
}


# ============================================================
# WEAK / FILLER WORDS
# ============================================================

FILLER_WORDS = {

    "hardworking",
    "motivated",
    "passionate",
    "dedicated",
    "enthusiastic",
    "dynamic",
    "responsible",
    "excellent",
    "outstanding",
    "successful",
    "results-driven",
    "team player",
    "go-getter",
    "self-motivated",
    "detail-oriented",
    "quick learner",
}


# ============================================================
# CONTACT PATTERNS
# ============================================================

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?\d{1,3}[\s.-]?)?"
    r"(?:\d{10}|\d{5}[\s.-]\d{5})(?!\d)"
)

URL_PATTERN = re.compile(
    r"(https?://|www\.|linkedin\.com|github\.com)"
    r"[^\s]+",
    re.IGNORECASE,
)


# ============================================================
# DEGREE PATTERNS
# ============================================================

DEGREE_PATTERNS = [

    r"\bb\.?\s*tech\b",
    r"\bbtech\b",
    r"\bb\.?\s*e\.?\b",
    r"\bbachelor\b",
    r"\bbachelors\b",

    r"\bm\.?\s*tech\b",
    r"\bmtech\b",
    r"\bm\.?\s*e\.?\b",
    r"\bmaster\b",
    r"\bmasters\b",

    r"\bmca\b",
    r"\bbca\b",
    r"\bmba\b",
    r"\bphd\b",
    r"\bdiploma\b",
]


# ============================================================
# COMMON WORDS
# ============================================================

COMMON_WORDS = {

    "the",
    "and",
    "for",
    "with",
    "from",
    "this",
    "that",
    "using",
    "used",
    "into",
    "have",
    "has",
    "been",
    "was",
    "were",
    "are",
    "is",
    "to",
    "of",
    "in",
    "on",
    "at",
    "by",
    "as",
    "an",
    "a",
    "or",
    "but",
    "it",
    "its",
    "their",
    "our",
    "your",
    "they",
    "them",
    "these",
    "those",
    "through",
    "based",
    "work",
    "working",
    "experience",
    "project",
    "projects",
    "skills",
    "data",
    "role",
    "job",
    "team",
    "business",
}


# ============================================================
# TEXT EXTRACTION
# PDF + DOCX
# ============================================================

def extract_text(file_path):

    extension = os.path.splitext(
        file_path
    )[1].lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    elif extension == ".docx":
        return extract_text_from_docx(file_path)

    return ""


# ============================================================
# PDF TEXT EXTRACTION
# ============================================================

def extract_text_from_pdf(file_path):

    doc = pymupdf.open(file_path)

    text = ""

    for page in doc:

        text += page.get_text()
        text += "\n"

    doc.close()

    return text.strip()


# ============================================================
# DOCX TEXT EXTRACTION
# ============================================================

def extract_text_from_docx(file_path):

    document = Document(file_path)

    extracted_text = []

    # Paragraphs
    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            extracted_text.append(text)

    # Tables
    for table in document.tables:

        for row in table.rows:

            row_text = []

            for cell in row.cells:

                cell_text = cell.text.strip()

                if cell_text:
                    row_text.append(cell_text)

            if row_text:

                extracted_text.append(
                    " | ".join(row_text)
                )

    return "\n".join(
        extracted_text
    ).strip()


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(text):

    text = text.lower()

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# SECTION DETECTION
# ============================================================

def detect_sections(text):

    sections = {}

    current_section = None

    for raw_line in text.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        cleaned = re.sub(
            r"[:\-\u2013\u2014]+$",
            "",
            line
        )

        cleaned = re.sub(
            r"\s+",
            " ",
            cleaned
        ).upper()

        found_section = None

        for section, aliases in SECTION_ALIASES.items():

            if cleaned in aliases:

                found_section = section
                break

        if found_section:

            current_section = found_section

            if current_section not in sections:

                sections[current_section] = []

            continue

        if current_section:

            sections[current_section].append(
                line
            )

    return {

        key: "\n".join(value)

        for key, value in sections.items()

    }


# ============================================================
# 1. PARSING QUALITY
# ============================================================

def check_parsing_quality(text):

    char_count = len(text.strip())

    word_count = len(text.split())

    score = 0

    issues = []

    if char_count >= 1500:

        score = 10

    elif char_count >= 1000:

        score = 9

    elif char_count >= 700:

        score = 8

    elif char_count >= 500:

        score = 7

    elif char_count >= 300:

        score = 5

    else:

        score = 3

        issues.append(
            "Very little text could be extracted from the resume."
        )

    if word_count < 100:

        issues.append(
            "Very low word count; verify that the document is text-readable."
        )

    return score, issues


# ============================================================
# 2. CONTACT INFORMATION
# ============================================================

def check_contact_information(text):

    checks = {

        "email":
            bool(
                EMAIL_PATTERN.search(text)
            ),

        "phone":
            bool(
                PHONE_PATTERN.search(text)
            ),

        "linkedin":
            "linkedin.com" in text.lower(),

        "github":
            "github.com" in text.lower(),

    }

    score = sum(
        checks.values()
    )

    return {

        "score":
            round(
                score / 4 * 100
            ),

        "email":
            checks["email"],

        "phone":
            checks["phone"],

        "linkedin":
            checks["linkedin"],

        "github":
            checks["github"],
    }


# ============================================================
# 3. STANDARD SECTIONS
# ============================================================

def check_standard_sections(sections):

    important = [

        "experience",
        "education",
        "skills",
        "projects",

    ]

    found = [

        section

        for section in important

        if section in sections

    ]

    score = round(

        len(found)
        / len(important)
        * 100

    )

    return score, found


# ============================================================
# 4. SECTION COMPLETENESS
# ============================================================

def check_section_completeness(sections):

    recommended = [

        "summary",
        "experience",
        "education",
        "skills",
        "projects",
        "certifications",

    ]

    present = sum(

        1

        for section in recommended

        if section in sections

    )

    return round(

        present
        / len(recommended)
        * 100

    )


# ============================================================
# 5. EDUCATION
# ============================================================

def check_education(
    text,
    sections
):

    education_text = sections.get(
        "education",
        ""
    )

    degree = any(

        re.search(
            pattern,
            education_text,
            re.I
        )

        for pattern in DEGREE_PATTERNS

    )

    institution = bool(

        re.search(

            r"\b(college|university|institute|school)\b",

            education_text,

            re.I

        )

    )

    year = bool(

        re.search(

            r"\b(?:19|20)\d{2}\b",

            education_text

        )

    )

    score = (

        int(degree)
        +
        int(institution)
        +
        int(year)

    )

    return {

        "score":
            round(
                score / 3 * 100
            ),

        "degree":
            degree,

        "institution":
            institution,

        "year":
            year,

    }


# ============================================================
# 6. DATES / TIMELINE
# ============================================================

def check_dates(text):

    years = re.findall(

        r"\b(?:19|20)\d{2}\b",

        text

    )

    date_ranges = re.findall(

        r"\b(?:19|20)\d{2}\s*[-–]\s*"
        r"(?:(?:19|20)\d{2}|present|current)\b",

        text,

        re.I

    )

    score = 0

    issues = []

    if len(years) >= 2:

        score += 50

    if date_ranges:

        score += 50

    if not years:

        issues.append(
            "No clear dates or years were detected."
        )

    return min(
        score,
        100
    ), issues


# ============================================================
# 7. BULLET STRUCTURE
# ============================================================

def check_bullets(
    text,
    sections
):

    bullet_symbols = (
        "•●▪◦‣⁃∙■□➢➤"
    )

    glyph_count = sum(

        1

        for char in text

        if char in bullet_symbols

    )

    action_bullets = 0

    relevant_text = (

        sections.get(
            "experience",
            ""
        )

        + "\n"

        + sections.get(
            "projects",
            ""
        )

        + "\n"

        + sections.get(
            "achievements",
            ""
        )

    )

    for line in relevant_text.splitlines():

        clean = line.strip()

        if not clean:
            continue

        first_word = re.findall(

            r"[A-Za-z]+",

            clean.lower()

        )

        if (
            first_word
            and
            first_word[0]
            in ACTION_VERBS
        ):

            action_bullets += 1

    bullet_count = max(
        glyph_count,
        action_bullets
    )

    if bullet_count >= 8:

        score = 100

    elif bullet_count >= 5:

        score = 90

    elif bullet_count >= 3:

        score = 75

    elif bullet_count >= 1:

        score = 60

    else:

        score = 40

    return score, bullet_count


# ============================================================
# 8. ACTION VERBS
# ============================================================

def check_action_verbs(text):

    words = re.findall(

        r"\b[a-zA-Z]+\b",

        text.lower()

    )

    found = [

        word

        for word in words

        if word in ACTION_VERBS

    ]

    unique_found = set(found)

    if len(unique_found) >= 10:

        score = 100

    elif len(unique_found) >= 7:

        score = 90

    elif len(unique_found) >= 5:

        score = 80

    elif len(unique_found) >= 3:

        score = 65

    elif len(unique_found) >= 1:

        score = 50

    else:

        score = 30

    return score, sorted(
        unique_found
    )


# ============================================================
# 9. QUANTIFIED ACHIEVEMENTS
# ============================================================

def check_quantified_achievements(text):

    patterns = [

        r"\b\d+(?:\.\d+)?\s*%",

        r"\b\d+(?:,\d{3})?\+?\s*"
        r"(?:users|customers|clients|records|rows|files)\b",

        r"\b(?:increased|improved|reduced|decreased|saved|grew|boosted)\b"
        r".{0,60}\b\d+\b",

        r"\b\d+(?:,\d{3})?\+?\s*"
        r"(?:projects|applications|datasets|employees|students)\b",

    ]

    matches = []

    for pattern in patterns:

        matches.extend(

            re.findall(

                pattern,

                text,

                re.I

            )

        )

    count = len(matches)

    if count >= 6:

        score = 100

    elif count >= 4:

        score = 90

    elif count >= 3:

        score = 80

    elif count >= 2:

        score = 70

    elif count >= 1:

        score = 55

    else:

        score = 30

    return score, matches


# ============================================================
# 10. REPETITION
# ============================================================

def check_repetition(text):

    words = re.findall(

        r"\b[a-zA-Z]{4,}\b",

        text.lower()

    )

    counter = Counter(words)

    repeated = []

    for word, count in counter.items():

        if word in COMMON_WORDS:
            continue

        if count >= 6:

            repeated.append(
                (word, count)
            )

    if len(repeated) == 0:

        score = 100

    elif len(repeated) <= 2:

        score = 90

    elif len(repeated) <= 4:

        score = 75

    elif len(repeated) <= 6:

        score = 60

    else:

        score = 40

    return score, repeated


# ============================================================
# 11. FILLER / BUZZWORDS
# ============================================================

def check_filler_words(text):

    lower = normalize(text)

    found = []

    for phrase in FILLER_WORDS:

        if phrase in lower:

            found.append(
                phrase
            )

    if len(found) == 0:

        score = 100

    elif len(found) <= 2:

        score = 85

    elif len(found) <= 4:

        score = 70

    else:

        score = 50

    return score, found


# ============================================================
# 12. PASSIVE VOICE
# ============================================================

def check_passive_voice(text):

    sentences = re.split(

        r"[.!?]\s+",

        text

    )

    passive_count = 0

    total_sentences = 0

    for sentence in sentences:

        words = sentence.lower().split()

        if len(words) < 4:
            continue

        total_sentences += 1

        for i, word in enumerate(
            words[:-1]
        ):

            if word in {
                "was",
                "were",
                "been",
                "being",
                "is",
                "are"
            }:

                next_word = re.sub(

                    r"[^a-z]",

                    "",

                    words[i + 1]

                )

                if next_word.endswith("ed"):

                    passive_count += 1
                    break

    if total_sentences == 0:

        return 100, 0

    percentage = (

        passive_count
        /
        total_sentences
        *
        100

    )

    if percentage <= 5:

        score = 100

    elif percentage <= 10:

        score = 90

    elif percentage <= 20:

        score = 75

    else:

        score = 55

    return score, passive_count


# ============================================================
# 13. PERSONAL PRONOUNS
# ============================================================

def check_personal_pronouns(text):

    pronouns = re.findall(

        r"\b(?:I|me|my|mine|we|our|ours)\b",

        text,

        re.I

    )

    count = len(pronouns)

    if count == 0:

        score = 100

    elif count <= 2:

        score = 90

    elif count <= 5:

        score = 75

    else:

        score = 50

    return score, count


# ============================================================
# 14. WORD COUNT / LENGTH
# ============================================================

def check_length(text):

    words = re.findall(

        r"\b\w+\b",

        text

    )

    count = len(words)

    if 250 <= count <= 1000:

        score = 100

    elif 150 <= count <= 1200:

        score = 90

    elif 100 <= count <= 1400:

        score = 75

    elif count < 100:

        score = 45

    else:

        score = 60

    return score, count


# ============================================================
# 15. BULLET LENGTH
# ============================================================

def check_bullet_length(sections):

    lines = []

    for section in [

        "experience",
        "projects",
        "achievements"

    ]:

        content = sections.get(
            section,
            ""
        )

        lines.extend(

            line.strip()

            for line in content.splitlines()

            if line.strip()

        )

    if not lines:

        return 60, []

    long_lines = []

    for line in lines:

        word_count = len(
            line.split()
        )

        if word_count > 35:

            long_lines.append(
                line
            )

    ratio = (

        len(long_lines)
        /
        len(lines)

    )

    if ratio <= 0.10:

        score = 100

    elif ratio <= 0.20:

        score = 90

    elif ratio <= 0.35:

        score = 75

    else:

        score = 60

    return score, long_lines


# ============================================================
# 16. SKILLS SECTION
# ============================================================

def check_skills_section(sections):

    skills = sections.get(
        "skills",
        ""
    )

    if not skills:

        return 0, []

    lines = [

        line.strip()

        for line in skills.splitlines()

        if line.strip()

    ]

    if len(lines) >= 10:

        score = 100

    elif len(lines) >= 6:

        score = 90

    elif len(lines) >= 3:

        score = 75

    else:

        score = 60

    return score, lines


# ============================================================
# 17. PROFESSIONAL LINKS
# ============================================================

def check_links(text):

    lower = text.lower()

    links = {

        "linkedin":
            "linkedin.com" in lower,

        "github":
            "github.com" in lower,

        "portfolio":
            (
                "portfolio" in lower
                or
                "website" in lower
            )

    }

    count = sum(
        links.values()
    )

    if count >= 2:

        score = 100

    elif count == 1:

        score = 85

    else:

        score = 70

    return score, links


# ============================================================
# 18. IMAGE / SCANNED DOCUMENT
# ============================================================

def check_images(file_path):

    extension = os.path.splitext(
        file_path
    )[1].lower()

    # DOCX does not use PyMuPDF page/image analysis.
    if extension == ".docx":

        try:

            document = Document(
                file_path
            )

            image_count = 0

            for paragraph in document.paragraphs:

                for run in paragraph.runs:

                    xml = run._element.xml

                    if (
                        "drawing" in xml
                        or
                        "pict" in xml
                    ):

                        image_count += 1

            if image_count > 0:

                return {

                    "score": 70,

                    "total_images":
                        image_count,

                    "image_heavy_pages":
                        0

                }

            return {

                "score": 100,

                "total_images": 0,

                "image_heavy_pages": 0

            }

        except Exception:

            return {

                "score": 100,

                "total_images": 0,

                "image_heavy_pages": 0

            }

    doc = pymupdf.open(
        file_path
    )

    total_images = 0

    image_heavy_pages = 0

    for page in doc:

        images = page.get_images(
            full=True
        )

        total_images += len(images)

        image_area = 0

        for image in images:

            try:

                rects = page.get_image_rects(
                    image
                )

                for rect in rects:

                    image_area += (
                        rect.width
                        *
                        rect.height
                    )

            except Exception:

                pass

        page_area = (
            page.rect.width
            *
            page.rect.height
        )

        text_length = len(
            page.get_text()
        )

        if page_area > 0:

            ratio = (
                image_area
                /
                page_area
            )

            if (
                ratio > 0.45
                and
                text_length < 500
            ):

                image_heavy_pages += 1

    doc.close()

    if image_heavy_pages > 0:

        score = 40

    else:

        score = 100

    return {

        "score": score,

        "total_images":
            total_images,

        "image_heavy_pages":
            image_heavy_pages

    }


# ============================================================
# 19. TABLE DETECTION
# ============================================================

def check_tables(file_path):

    extension = os.path.splitext(
        file_path
    )[1].lower()

    # DOCX tables are directly accessible.
    if extension == ".docx":

        try:

            document = Document(
                file_path
            )

            table_count = len(
                document.tables
            )

            if table_count == 0:

                score = 100

            elif table_count == 1:

                score = 70

            else:

                score = 45

            return score, table_count

        except Exception:

            return 100, 0

    doc = pymupdf.open(
        file_path
    )

    possible_tables = 0

    for page in doc:

        try:

            tables = page.find_tables()

            if tables.tables:

                possible_tables += len(
                    tables.tables
                )

        except Exception:

            pass

    doc.close()

    if possible_tables == 0:

        score = 100

    elif possible_tables == 1:

        score = 70

    else:

        score = 45

    return score, possible_tables


# ============================================================
# 20. COLUMN DETECTION
# ============================================================

def check_columns(file_path):

    extension = os.path.splitext(
        file_path
    )[1].lower()

    # DOCX layout cannot reliably be detected
    # using the same PDF coordinate logic.
    if extension == ".docx":

        return 100, False

    doc = pymupdf.open(
        file_path
    )

    detected = False

    for page in doc:

        blocks = page.get_text(
            "blocks"
        )

        page_width = page.rect.width
        page_height = page.rect.height

        content = []

        for block in blocks:

            if len(block) < 7:
                continue

            x0, y0, x1, y1, text = block[:5]

            if not text.strip():
                continue

            if y0 < page_height * 0.15:
                continue

            content.append(
                (x0, y0, x1, y1)
            )

        if len(content) < 8:
            continue

        left = []
        right = []

        for block in content:

            x0, y0, x1, y1 = block

            center = (
                x0 + x1
            ) / 2

            if center < page_width * 0.42:

                left.append(block)

            elif center > page_width * 0.58:

                right.append(block)

        if (
            len(left) >= 4
            and
            len(right) >= 4
        ):

            left_top = min(
                b[1]
                for b in left
            )

            left_bottom = max(
                b[3]
                for b in left
            )

            right_top = min(
                b[1]
                for b in right
            )

            right_bottom = max(
                b[3]
                for b in right
            )

            left_span = (
                left_bottom
                -
                left_top
            )

            right_span = (
                right_bottom
                -
                right_top
            )

            if (
                left_span > page_height * 0.30
                and
                right_span > page_height * 0.30
            ):

                detected = True

    doc.close()

    return (
        45 if detected else 100,
        detected
    )


# ============================================================
# 21. HEADER / FOOTER TEXT
# ============================================================

def check_headers_footers(file_path):

    extension = os.path.splitext(
        file_path
    )[1].lower()

    # DOCX header/footer detection.
    if extension == ".docx":

        try:

            document = Document(
                file_path
            )

            suspicious = 0

            for section in document.sections:

                header_text = "\n".join(

                    p.text.strip()

                    for p in section.header.paragraphs

                    if p.text.strip()

                )

                footer_text = "\n".join(

                    p.text.strip()

                    for p in section.footer.paragraphs

                    if p.text.strip()

                )

                if header_text:
                    suspicious += 1

                if footer_text:
                    suspicious += 1

            if suspicious == 0:
                return 100, 0

            if suspicious <= 2:
                return 90, suspicious

            return 70, suspicious

        except Exception:

            return 100, 0

    doc = pymupdf.open(
        file_path
    )

    suspicious = 0

    for page in doc:

        blocks = page.get_text(
            "blocks"
        )

        page_height = page.rect.height

        for block in blocks:

            if len(block) < 7:
                continue

            x0, y0, x1, y1, text = block[:5]

            text = text.strip()

            if not text:
                continue

            if (
                y0 < page_height * 0.05
                or
                y1 > page_height * 0.95
            ):

                if len(text) < 100:

                    suspicious += 1

    doc.close()

    if suspicious == 0:

        return 100, 0

    if suspicious <= 2:

        return 90, suspicious

    return 70, suspicious


# ============================================================
# 22. SPELLING / LANGUAGE BASIC CHECK
# ============================================================

def check_language(text):

    sentences = re.split(
        r"[.!?]",
        text
    )

    fragments = 0

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        words = sentence.split()

        if len(words) == 1:

            fragments += 1

    if fragments <= 3:

        score = 100

    elif fragments <= 6:

        score = 90

    else:

        score = 75

    return score, fragments


# ============================================================
# 23. DATE CONSISTENCY
# ============================================================

def check_date_consistency(text):

    years = [

        int(year)

        for year in re.findall(

            r"\b(?:19|20)\d{2}\b",

            text

        )

    ]

    if not years:

        return 60, []

    invalid = [

        year

        for year in years

        if year < 1950
        or
        year > 2100

    ]

    if invalid:

        return 60, invalid

    return 100, []


# ============================================================
# 24. FILE / PAGE COUNT
# ============================================================

def check_pages(file_path):

    extension = os.path.splitext(
        file_path
    )[1].lower()

    # DOCX page count cannot be reliably calculated
    # without a rendering engine.
    if extension == ".docx":

        return 100, None

    doc = pymupdf.open(
        file_path
    )

    pages = len(doc)

    doc.close()

    if pages <= 2:

        score = 100

    elif pages <= 3:

        score = 90

    elif pages <= 4:

        score = 75

    else:

        score = 55

    return score, pages


# ============================================================
# 25. SPECIAL CHARACTER / PARSING NOISE
# ============================================================

def check_parsing_noise(text):

    if not text:

        return 0, 0

    strange = re.findall(

        r"[^\x00-\x7F]",

        text

    )

    ratio = (

        len(strange)
        /
        max(
            len(text),
            1
        )

    )

    if ratio < 0.01:

        score = 100

    elif ratio < 0.03:

        score = 90

    elif ratio < 0.06:

        score = 75

    else:

        score = 55

    return score, len(strange)


# ============================================================
# 26. SKILL REPETITION / KEYWORD STUFFING
# ============================================================

def check_keyword_stuffing(text):

    words = re.findall(

        r"\b[a-zA-Z]{4,}\b",

        text.lower()

    )

    counter = Counter(words)

    suspicious = []

    total_words = len(words)

    for word, count in counter.items():

        if word in COMMON_WORDS:
            continue

        if count >= 10:

            suspicious.append(
                (word, count)
            )

    if total_words == 0:

        return 100, suspicious

    if len(suspicious) == 0:

        score = 100

    elif len(suspicious) <= 2:

        score = 85

    else:

        score = 65

    return score, suspicious


# ============================================================
# 27. SECTION HEADING QUALITY
# ============================================================

def check_heading_quality(sections):

    standard_count = len(
        sections
    )

    if standard_count >= 6:

        return 100

    elif standard_count >= 4:

        return 90

    elif standard_count >= 3:

        return 75

    elif standard_count >= 2:

        return 60

    return 40


# ============================================================
# 28. EXPERIENCE QUALITY
# ============================================================

def check_experience_quality(sections):

    experience = sections.get(
        "experience",
        ""
    )

    if not experience:

        return 50

    lines = [

        line.strip()

        for line in experience.splitlines()

        if line.strip()

    ]

    if len(lines) >= 6:

        return 100

    elif len(lines) >= 4:

        return 90

    elif len(lines) >= 2:

        return 75

    return 60


# ============================================================
# 29. PROJECT QUALITY
# ============================================================

def check_project_quality(sections):

    projects = sections.get(
        "projects",
        ""
    )

    if not projects:

        return 50

    lines = [

        line.strip()

        for line in projects.splitlines()

        if line.strip()

    ]

    if len(lines) >= 6:

        return 100

    elif len(lines) >= 4:

        return 90

    elif len(lines) >= 2:

        return 75

    return 60


# ============================================================
# 30. CERTIFICATION / TRAINING
# ============================================================

def check_certifications(sections):

    certification_text = (

        sections.get(
            "certifications",
            ""
        )

        + "\n"

        + sections.get(
            "training",
            ""
        )

    )

    if not certification_text.strip():

        return 60

    count = len([

        line

        for line in certification_text.splitlines()

        if line.strip()

    ])

    if count >= 5:

        return 100

    elif count >= 3:

        return 90

    elif count >= 1:

        return 80

    return 60


# ============================================================
# ISSUE GENERATION
# ============================================================

def generate_issues(results):

    issues = []

    if results["parsing_quality"]["score"] < 80:

        issues.append(
            "Resume text extraction may be incomplete."
        )

    if not results["contact"]["email"]:

        issues.append(
            "Email address was not detected."
        )

    if not results["contact"]["phone"]:

        issues.append(
            "Phone number was not detected."
        )

    if results["standard_sections"]["score"] < 100:

        issues.append(
            "Some standard ATS-friendly sections are missing."
        )

    education = results["education"]

    if not education["degree"]:

        issues.append(
            "Degree/qualification was not clearly detected."
        )

    if not education["institution"]:

        issues.append(
            "Educational institution was not clearly detected."
        )

    if results["columns"]["detected"]:

        issues.append(
            "Possible multi-column layout detected."
        )

    if results["tables"]["count"] > 0:

        issues.append(
            "Possible table structure detected."
        )

    if results["images"]["image_heavy_pages"] > 0:

        issues.append(
            "Image-heavy/scanned content may not parse reliably."
        )

    if results["bullets"]["score"] < 75:

        issues.append(
            "Experience/project content needs stronger bullet structure."
        )

    if results["quantified_achievements"]["score"] < 70:

        issues.append(
            "Few measurable achievements or quantified results detected."
        )

    if results["action_verbs"]["score"] < 70:

        issues.append(
            "More strong action verbs could be used."
        )

    if results["filler_words"]["score"] < 80:

        issues.append(
            "Filler or generic resume buzzwords detected."
        )

    if results["passive_voice"]["score"] < 80:

        issues.append(
            "Some passive-voice constructions were detected."
        )

    if results["length"]["score"] < 75:

        issues.append(
            "Resume length may need adjustment."
        )

    if results["keyword_stuffing"]["score"] < 80:

        issues.append(
            "Some words appear excessively repeated."
        )

    if results["headers_footers"]["score"] < 80:

        issues.append(
            "Possible header/footer parsing issues detected."
        )

    return issues


# ============================================================
# FINAL ATS SCORE
# ============================================================

def calculate_final_ats_score(results):

    weights = {

        "parsing_quality": 0.10,
        "contact": 0.06,
        "standard_sections": 0.08,
        "section_completeness": 0.04,
        "education": 0.05,
        "dates": 0.05,
        "bullets": 0.06,
        "action_verbs": 0.06,
        "quantified_achievements": 0.08,
        "repetition": 0.05,
        "filler_words": 0.04,
        "passive_voice": 0.04,
        "length": 0.05,
        "bullet_length": 0.04,
        "skills": 0.05,
        "links": 0.03,
        "images": 0.04,
        "tables": 0.03,
        "columns": 0.04,
        "headers_footers": 0.03,
        "language": 0.03,

    }

    values = {

        "parsing_quality":
            results["parsing_quality"]["score"],

        "contact":
            results["contact"]["score"],

        "standard_sections":
            results["standard_sections"]["score"],

        "section_completeness":
            results["section_completeness"],

        "education":
            results["education"]["score"],

        "dates":
            results["dates"]["score"],

        "bullets":
            results["bullets"]["score"],

        "action_verbs":
            results["action_verbs"]["score"],

        "quantified_achievements":
            results["quantified_achievements"]["score"],

        "repetition":
            results["repetition"]["score"],

        "filler_words":
            results["filler_words"]["score"],

        "passive_voice":
            results["passive_voice"]["score"],

        "length":
            results["length"]["score"],

        "bullet_length":
            results["bullet_length"]["score"],

        "skills":
            results["skills"]["score"],

        "links":
            results["links"]["score"],

        "images":
            results["images"]["score"],

        "tables":
            results["tables"]["score"],

        "columns":
            results["columns"]["score"],

        "headers_footers":
            results["headers_footers"]["score"],

        "language":
            results["language"]["score"],

    }

    score = sum(

        values[key]
        *
        weights[key]

        for key in weights

    )

    return round(score)


# ============================================================
# MAIN FUNCTION
# ============================================================

def analyze_resume(file_path):

    text = extract_text(
        file_path
    )

    sections = detect_sections(
        text
    )

    results = {}


    # 1
    parsing_score, parsing_issues = (
        check_parsing_quality(text)
    )

    results["parsing_quality"] = {

        "score":
            parsing_score,

        "issues":
            parsing_issues

    }


    # 2
    results["contact"] = (
        check_contact_information(text)
    )


    # 3
    standard_score, found_sections = (
        check_standard_sections(
            sections
        )
    )

    results["standard_sections"] = {

        "score":
            standard_score,

        "found":
            found_sections

    }


    # 4
    results["section_completeness"] = (
        check_section_completeness(
            sections
        )
    )


    # 5
    results["education"] = (
        check_education(
            text,
            sections
        )
    )


    # 6
    dates_score, date_issues = (
        check_dates(text)
    )

    results["dates"] = {

        "score":
            dates_score,

        "issues":
            date_issues

    }


    # 7
    bullet_score, bullet_count = (
        check_bullets(
            text,
            sections
        )
    )

    results["bullets"] = {

        "score":
            bullet_score,

        "count":
            bullet_count

    }


    # 8
    action_score, action_verbs = (
        check_action_verbs(text)
    )

    results["action_verbs"] = {

        "score":
            action_score,

        "found":
            action_verbs

    }


    # 9
    quantified_score, quantified = (
        check_quantified_achievements(
            text
        )
    )

    results["quantified_achievements"] = {

        "score":
            quantified_score,

        "matches":
            quantified

    }


    # 10
    repetition_score, repeated = (
        check_repetition(text)
    )

    results["repetition"] = {

        "score":
            repetition_score,

        "repeated":
            repeated

    }


    # 11
    filler_score, filler = (
        check_filler_words(text)
    )

    results["filler_words"] = {

        "score":
            filler_score,

        "found":
            filler

    }


    # 12
    passive_score, passive_count = (
        check_passive_voice(text)
    )

    results["passive_voice"] = {

        "score":
            passive_score,

        "count":
            passive_count

    }


    # 13
    pronoun_score, pronoun_count = (
        check_personal_pronouns(text)
    )

    results["personal_pronouns"] = {

        "score":
            pronoun_score,

        "count":
            pronoun_count

    }


    # 14
    length_score, word_count = (
        check_length(text)
    )

    results["length"] = {

        "score":
            length_score,

        "word_count":
            word_count

    }


    # 15
    bullet_length_score, long_bullets = (
        check_bullet_length(
            sections
        )
    )

    results["bullet_length"] = {

        "score":
            bullet_length_score,

        "long_bullets":
            long_bullets

    }


    # 16
    skills_score, skills = (
        check_skills_section(
            sections
        )
    )

    results["skills"] = {

        "score":
            skills_score,

        "skills":
            skills

    }


    # 17
    links_score, links = (
        check_links(text)
    )

    results["links"] = {

        "score":
            links_score,

        **links

    }


    # 18
    results["images"] = (
        check_images(
            file_path
        )
    )


    # 19
    table_score, table_count = (
        check_tables(
            file_path
        )
    )

    results["tables"] = {

        "score":
            table_score,

        "count":
            table_count

    }


    # 20
    column_score, column_detected = (
        check_columns(
            file_path
        )
    )

    results["columns"] = {

        "score":
            column_score,

        "detected":
            column_detected

    }


    # 21
    header_score, header_count = (
        check_headers_footers(
            file_path
        )
    )

    results["headers_footers"] = {

        "score":
            header_score,

        "count":
            header_count

    }


    # 22
    language_score, fragment_count = (
        check_language(text)
    )

    results["language"] = {

        "score":
            language_score,

        "fragments":
            fragment_count

    }


    # 23
    date_consistency_score, invalid_dates = (
        check_date_consistency(
            text
        )
    )

    results["date_consistency"] = {

        "score":
            date_consistency_score,

        "invalid":
            invalid_dates

    }


    # 24
    page_score, page_count = (
        check_pages(
            file_path
        )
    )

    results["pages"] = {

        "score":
            page_score,

        "count":
            page_count

    }


    # 25
    noise_score, noise_count = (
        check_parsing_noise(
            text
        )
    )

    results["parsing_noise"] = {

        "score":
            noise_score,

        "count":
            noise_count

    }


    # 26
    stuffing_score, suspicious_words = (
        check_keyword_stuffing(
            text
        )
    )

    results["keyword_stuffing"] = {

        "score":
            stuffing_score,

        "suspicious":
            suspicious_words

    }


    # 27
    results["heading_quality"] = (
        check_heading_quality(
            sections
        )
    )


    # 28
    results["experience_quality"] = (
        check_experience_quality(
            sections
        )
    )


    # 29
    results["project_quality"] = (
        check_project_quality(
            sections
        )
    )


    # 30
    results["certifications"] = (
        check_certifications(
            sections
        )
    )


    # FINAL ATS SCORE

    final_score = calculate_final_ats_score(
        results
    )

    results["ats_score"] = final_score


    # ISSUES

    results["issues"] = generate_issues(
        results
    )


    # DETECTED SECTIONS

    results["detected_sections"] = list(
        sections.keys()
    )


    return results