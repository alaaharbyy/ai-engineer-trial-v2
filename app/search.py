"""Task 1: permission-aware retrieval.

Implement the functions below. You choose the chunking strategy, the embedding
model and how the index is stored.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

DOCS_DIR = Path(__file__).resolve().parent.parent / "documents"
ACL_FILE = DOCS_DIR / "acl.yaml"
INDEX_DIR = Path(os.environ.get("INDEX_DIR", "/var/lib/app/index"))

# A function that turns a list of texts into a list of vectors.
EmbedFn = Callable[[list[str]], list[list[float]]]


@dataclass
class Chunk:
    chunk_id: str  # stable and unique, e.g. "capex_approval_matrix.txt#2"
    doc_id: str  # the document file name
    text: str
    allowed_groups: list[str] = field(default_factory=list)
    score: float = 0.0


def build_index(embed_fn: EmbedFn | None = None) -> None:
    """Chunk every document, embed each chunk, store it with its allowed groups
    (from acl.yaml) and save the index under INDEX_DIR.

    Accepting an injectable embed_fn lets tests run without a real model.
    """
    raise NotImplementedError


def search(query: str, user_id: str, k: int = 4) -> list[Chunk]:
    """Return up to k chunks the user may read, most similar first.

    Look up the user's groups with app.accounts.groups_for(). A chunk is
    readable if its allowed_groups include "everyone" or any of the user's
    groups. The permission filter must run inside this function: never return
    chunks the user can't read, even to filter them afterwards.
    """
    raise NotImplementedError


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--rebuild", action="store_true", help="rebuild the index")
    args = parser.parse_args()
    if args.rebuild:
        try:
            build_index()
        except NotImplementedError:
            print("build_index() is not implemented yet (Task 1). Starting without an index.")
        else:
            print(f"Index rebuilt in {INDEX_DIR}")
