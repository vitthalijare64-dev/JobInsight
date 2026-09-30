from pathlib import Path

import pandas as pd
import torch
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "jobs_processed.parquet"
)

EMBEDDINGS_PATH = (
    PROJECT_ROOT
    / "models"
    / "matching"
    / "job_embeddings.parquet"
)

MODEL_NAME = "all-MiniLM-L6-v2"

# Smaller batches are safer for a 4 GB GPU.
BATCH_SIZE = 16


def build_job_text(row: pd.Series) -> str:
    """Build a compact semantic representation of a job."""

    fields = [
        row.get("title"),
        row.get("normalized_title"),
        row.get("skills_required"),
        row.get("minimum_qualifications"),
        row.get("preferred_qualifications"),
        row.get("responsibilities"),
        row.get("job_description"),
    ]

    text_parts = []

    for value in fields:
        if pd.notna(value):
            value = str(value).strip()

            if value:
                text_parts.append(value)

    return " ".join(text_parts)


def main():
    print("=" * 60)
    print("JobInsight - Semantic Job Embeddings")
    print("=" * 60)

    if not PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Processed dataset not found at: "
            f"{PROCESSED_DATA_PATH}"
        )

    jobs = pd.read_parquet(
        PROCESSED_DATA_PATH
    )

    print(f"Input jobs: {len(jobs):,}")

    # Use GPU if PyTorch can access it.
    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print(f"Device: {device}")

    if device == "cuda":
        print(
            f"GPU: {torch.cuda.get_device_name(0)}"
        )

    print(f"Loading model: {MODEL_NAME}")

    model = SentenceTransformer(
        MODEL_NAME,
        device=device
    )

    print("Building job text...")

    texts = jobs.apply(
        build_job_text,
        axis=1
    ).tolist()

    print(
        f"Prepared {len(texts):,} job texts."
    )

    print(
        f"Generating embeddings "
        f"with batch size {BATCH_SIZE}..."
    )

    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=True,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    print(
        f"Embedding shape: {embeddings.shape}"
    )

    EMBEDDINGS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    embedding_df = pd.DataFrame(
        embeddings
    )

    embedding_df.insert(
        0,
        "job_index",
        range(len(jobs))
    )

    embedding_df.to_parquet(
        EMBEDDINGS_PATH,
        index=False
    )

    print("\nSaved:")
    print(EMBEDDINGS_PATH)

    print("=" * 60)
    print(
        "Semantic embedding generation "
        "completed successfully."
    )
    print("=" * 60)


if __name__ == "__main__":
    main()