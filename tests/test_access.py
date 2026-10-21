"""Task 3: prove search() never returns a chunk the user may not read.

These tests must pass with no API key and no live model. Build the index with
a fake embed_fn (any deterministic function of the text works) so CI can run
them.
"""
import zlib

import pytest

from app import search as search_mod


def fake_embed(texts: list[str]) -> list[list[float]]:
    """Deterministic stand-in for a real embedding model. Replace if you like."""
    vecs = []
    for t in texts:
        v = [0.0] * 64
        for word in t.lower().split():
            v[zlib.crc32(word.encode()) % 64] += 1.0
        vecs.append(v)
    return vecs


@pytest.fixture(scope="module", autouse=True)
def index(tmp_path_factory):
    # TODO: point INDEX_DIR at a temp folder and build the index with fake_embed.
    pytest.fail("TODO: build a test index")


def test_staff_only_sees_everyone_documents():
    # TODO: for several queries, every chunk returned for staff_1 must be
    # allowed for "everyone". Include a query aimed at the finance-only memo.
    pytest.fail("TODO")


def test_multi_group_and_single_group_users():
    # TODO: analyst_1 (finance + legal) can get legal and finance chunks but
    # never leasing-only ones; leasing_1 never gets finance or legal ones.
    pytest.fail("TODO")
