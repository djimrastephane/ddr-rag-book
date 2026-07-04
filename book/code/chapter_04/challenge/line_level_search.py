"""Chapter 4 challenge solution: reproduce the Field Notes line-level result.

Embeds three isolated lines -- report #39's high-torque line, report #39's
hole-drag line, and a genuinely unrelated line from report #36 -- and
confirms the high-torque line scores meaningfully higher against
"stuck pipe" than the other two, which should score close to each other.

Usage:
    python code/chapter_04/challenge/line_level_search.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from semantic_search import MODEL_NAME  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402

LINES = {
    "r39_high_torque": "Due to high torque decision to pull out of hole",
    "r39_hole_drag": "Trip out of hole with BHA 21, Hole drag from 6,050 feet to 5,901 feet no issues",
    "r36_unrelated": "Trip out of hole with BHA number 17 core assembly, lay down core barrels",
}


if __name__ == "__main__":
    # device="cpu" pinned explicitly -- see code/chapter_04/semantic_search.py
    # for why: Apple Silicon otherwise auto-selects the MPS backend, which
    # produces meaningfully different embeddings than CPU.
    model = SentenceTransformer(MODEL_NAME, device="cpu")
    keys = list(LINES.keys())
    texts = list(LINES.values())

    emb = model.encode(texts, normalize_embeddings=True)
    query_vec = model.encode(["stuck pipe"], normalize_embeddings=True)[0]
    scores = emb @ query_vec

    order = np.argsort(-scores)
    for i in order:
        print(f"{scores[i]:.4f}  {keys[i]}: {texts[i]}")

    high_torque_score = scores[keys.index("r39_high_torque")]
    hole_drag_score = scores[keys.index("r39_hole_drag")]
    unrelated_score = scores[keys.index("r36_unrelated")]

    assert high_torque_score > hole_drag_score
    assert high_torque_score > unrelated_score
    print(f"\nConfirmed: high-torque line ({high_torque_score:.4f}) scores "
          f"clearly above both hole-drag ({hole_drag_score:.4f}) and "
          f"unrelated content ({unrelated_score:.4f}).")
