from pathlib import Path
import re

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "jobs_processed.parquet"
)


# Transparent baseline skill vocabulary.
# We will expand this substantially as the NLP pipeline develops.
SKILL_DICTIONARY = {
    "python": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "c++": "C++",
    "c#": "C#",
    "sql": "SQL",
    "r programming": "R",
    "excel": "Microsoft Excel",
    "power bi": "Power BI",
    "tableau": "Tableau",
    "aws": "AWS",
    "azure": "Microsoft Azure",
    "google cloud": "Google Cloud",
    "gcp": "Google Cloud",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "git": "Git",
    "github": "GitHub",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "artificial intelligence": "Artificial Intelligence",
    "natural language processing": "Natural Language Processing",
    "nlp": "Natural Language Processing",
    "data analysis": "Data Analysis",
    "data analytics": "Data Analytics",
    "data science": "Data Science",
    "statistics": "Statistics",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scikit-learn": "Scikit-learn",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "spark": "Apache Spark",
    "hadoop": "Hadoop",
    "etl": "ETL",
    "rest api": "REST API",
    "api": "API",
    "agile": "Agile",
    "scrum": "Scrum",
    "project management": "Project Management",
}


def normalize_text(text: str) -> str:
    """Normalize text for skill matching."""

    if pd.isna(text):
        return ""

    text = str(text).lower()

    # Normalize common separators.
    text = text.replace("/", " ")
    text = text.replace("-", " ")

    # Collapse repeated whitespace.
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_skills(text: str) -> list[str]:
    """
    Extract skills using the controlled baseline dictionary.

    Returns canonical skill names.
    """

    normalized_text = normalize_text(text)

    if not normalized_text:
        return []

    found_skills = set()

    for skill_pattern, canonical_skill in SKILL_DICTIONARY.items():

        pattern = r"(?<!\w)" + re.escape(skill_pattern) + r"(?!\w)"

        if re.search(pattern, normalized_text):
            found_skills.add(canonical_skill)

    return sorted(found_skills)


def extract_skills_from_job(row: pd.Series) -> list[str]:
    """Extract skills from the main job-text fields."""

    text_fields = [
        "job_description",
        "skills_required",
        "minimum_qualifications",
        "preferred_qualifications",
        "responsibilities",
        "certifications",
    ]

    combined_text = " ".join(
        str(row[field])
        for field in text_fields
        if field in row.index and pd.notna(row[field])
    )

    return extract_skills(combined_text)


if __name__ == "__main__":
    print("=" * 60)
    print("JobInsight - Baseline Skill Extractor")
    print("=" * 60)

    if not PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at: {PROCESSED_DATA_PATH}"
        )

    jobs = pd.read_parquet(PROCESSED_DATA_PATH)

    # Test on the first job.
    first_job = jobs.iloc[0]

    skills = extract_skills_from_job(first_job)

    print(f"Job title: {first_job['title']}")
    print(f"Company: {first_job['company_name']}")
    print(f"Extracted skills: {skills}")

    print("=" * 60)
    print("Baseline skill extraction successful.")
    print("=" * 60)