from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

JOBS_PATH = (
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


# ============================================================
# MODEL
# ============================================================

@st.cache_resource(show_spinner=False)
def load_embedding_model():

    device = "cuda"

    try:
        import torch

        if not torch.cuda.is_available():
            device = "cpu"

    except Exception:
        device = "cpu"

    return SentenceTransformer(
        MODEL_NAME,
        device=device,
    )


# ============================================================
# JOB DATA
# ============================================================

@st.cache_data(show_spinner=False)
def load_jobs():

    if not JOBS_PATH.exists():
        raise FileNotFoundError(
            f"Jobs file not found:\n{JOBS_PATH}"
        )

    return pd.read_parquet(
        JOBS_PATH
    )


# ============================================================
# PRECOMPUTED EMBEDDINGS
# ============================================================

@st.cache_data(show_spinner=False)
def load_job_embeddings():

    if not EMBEDDINGS_PATH.exists():
        raise FileNotFoundError(
            f"Job embeddings not found:\n"
            f"{EMBEDDINGS_PATH}"
        )

    df = pd.read_parquet(
        EMBEDDINGS_PATH
    )

    embedding_columns = [
        str(i)
        for i in range(384)
        if str(i) in df.columns
    ]

    if len(embedding_columns) != 384:
        raise ValueError(
            "Expected 384 embedding columns, "
            f"but found {len(embedding_columns)}."
        )

    embeddings = df[
        embedding_columns
    ].to_numpy(
        dtype=np.float32
    )

    # Normalize once.
    norms = np.linalg.norm(
        embeddings,
        axis=1,
        keepdims=True,
    )

    norms[norms == 0] = 1

    embeddings = (
        embeddings / norms
    ).astype(
        np.float32
    )

    if "job_index" in df.columns:
        job_indices = (
            df["job_index"]
            .to_numpy()
        )
    else:
        job_indices = np.arange(
            len(df)
        )

    return (
        embeddings,
        job_indices,
    )


# ============================================================
# QUERY TEXT
# ============================================================

def build_query_text(
    title="",
    skills=None,
    experience="",
    education="",
    summary="",
    description="",
):

    parts = []

    if title:
        parts.append(
            f"Target role: {title}"
        )

    if skills:
        if isinstance(
            skills,
            str,
        ):
            skills_text = skills
        else:
            skills_text = ", ".join(
                map(
                    str,
                    skills,
                )
            )

        parts.append(
            f"Skills: {skills_text}"
        )

    if experience:
        parts.append(
            f"Experience: {experience}"
        )

    if education:
        parts.append(
            f"Education: {education}"
        )

    if summary:
        parts.append(
            f"Professional summary: {summary}"
        )

    if description:
        parts.append(
            f"Resume content: {description}"
        )

    return "\n".join(parts)


# ============================================================
# SEMANTIC MATCHING
# ============================================================

def semantic_match(
    query_text,
    top_k=10,
    min_score=0.0,
    work_model=None,
):

    if not query_text or not query_text.strip():
        return pd.DataFrame()

    # --------------------------------------------------------
    # Load cached resources
    # --------------------------------------------------------

    model = load_embedding_model()

    jobs = load_jobs()

    job_embeddings, job_indices = (
        load_job_embeddings()
    )

    # --------------------------------------------------------
    # Encode ONLY the candidate
    # --------------------------------------------------------

    query_embedding = model.encode(
        query_text,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).astype(
        np.float32
    )

    # --------------------------------------------------------
    # Vectorized cosine similarity
    # --------------------------------------------------------

    scores = np.dot(
        job_embeddings,
        query_embedding,
    )

    # --------------------------------------------------------
    # Optional work-model filtering
    # --------------------------------------------------------

    valid_mask = np.ones(
        len(jobs),
        dtype=bool,
    )

    if work_model and work_model != "All":

        if "work_model" in jobs.columns:

            normalized_filter = (
                str(work_model)
                .strip()
                .lower()
            )

            job_work_models = (
                jobs["work_model"]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
                .str.lower()
            )

            valid_mask = (
                job_work_models
                == normalized_filter
            )

    # --------------------------------------------------------
    # Match embedding rows to job rows
    # --------------------------------------------------------

    valid_embedding_mask = np.array(
        [
            (
                idx < len(jobs)
                and valid_mask[int(idx)]
            )
            for idx in job_indices
        ],
        dtype=bool,
    )

    candidate_indices = np.where(
        valid_embedding_mask
    )[0]

    if len(candidate_indices) == 0:
        return pd.DataFrame()

    candidate_scores = scores[
        candidate_indices
    ]

    # --------------------------------------------------------
    # Minimum score
    # --------------------------------------------------------

    score_mask = (
        candidate_scores >= min_score
    )

    candidate_indices = (
        candidate_indices[
            score_mask
        ]
    )

    candidate_scores = (
        candidate_scores[
            score_mask
        ]
    )

    if len(candidate_indices) == 0:
        return pd.DataFrame()

    # --------------------------------------------------------
    # Top K
    # --------------------------------------------------------

    k = min(
        int(top_k),
        len(candidate_scores),
    )

    if k <= 0:
        return pd.DataFrame()

    # Efficient partial sorting
    if len(candidate_scores) > k:

        top_positions = np.argpartition(
            -candidate_scores,
            k - 1,
        )[:k]

    else:

        top_positions = np.arange(
            len(candidate_scores)
        )

    top_positions = top_positions[
        np.argsort(
            -candidate_scores[
                top_positions
            ]
        )
    ]

    selected_embedding_positions = (
        candidate_indices[
            top_positions
        ]
    )

    selected_scores = (
        candidate_scores[
            top_positions
        ]
    )

    # --------------------------------------------------------
    # Convert embedding position -> original job row
    # --------------------------------------------------------

    selected_job_indices = (
        job_indices[
            selected_embedding_positions
        ]
    )

    selected_job_indices = (
        selected_job_indices.astype(int)
    )

    # --------------------------------------------------------
    # Return jobs
    # --------------------------------------------------------

    results = jobs.iloc[
        selected_job_indices
    ].copy()

    results["similarity_score"] = (
        selected_scores
    )

    results["similarity_score"] = (
        results[
            "similarity_score"
        ].round(4)
    )

    return results


# ============================================================
# QUICK TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("JobInsight - Semantic Matcher")
    print("=" * 70)

    print(
        f"Jobs file: {JOBS_PATH}"
    )

    print(
        f"Embeddings: {EMBEDDINGS_PATH}"
    )

    embeddings, indices = (
        load_job_embeddings()
    )

    print(
        f"Loaded embeddings: "
        f"{embeddings.shape}"
    )

    print(
        "Semantic matcher ready."
    )