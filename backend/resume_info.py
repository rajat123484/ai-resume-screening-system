import re


# =========================================================
# EMAIL
# =========================================================

def extract_email(text):

    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )

    if match:
        return match.group(0)

    return None


# =========================================================
# PHONE
# =========================================================

def extract_phone(text):

    match = re.search(
        r"(?:\+91[\s-]?)?[6-9]\d{9}",
        text
    )

    if match:
        return match.group(0)

    return None


# =========================================================
# LINKEDIN
# =========================================================

def extract_linkedin(text):

    match = re.search(
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9._-]+",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(0)

    return None


# =========================================================
# GITHUB
# =========================================================

def extract_github(text):

    match = re.search(
        r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9._-]+",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(0)

    return None


# =========================================================
# NAME
# =========================================================

def extract_name(text):

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    for line in lines[:10]:

        # Ignore common headings
        if line.upper() in [
            "RESUME",
            "CURRICULUM VITAE",
            "CV",
            "CONTACT",
            "PROFILE"
        ]:
            continue

        # Ignore lines containing contact information
        if "@" in line:
            continue

        if re.search(r"\d", line):
            continue

        # Name usually has 2-4 words
        words = line.split()

        if 2 <= len(words) <= 4:

            if all(
                re.match(
                    r"^[A-Za-z.'-]+$",
                    word
                )
                for word in words
            ):
                return line.title()

    return None


# =========================================================
# MAIN FUNCTION
# =========================================================

def extract_candidate_info(text):

    return {

        "name":
            extract_name(text),

        "email":
            extract_email(text),

        "phone":
            extract_phone(text),

        "linkedin":
            extract_linkedin(text),

        "github":
            extract_github(text)
    }