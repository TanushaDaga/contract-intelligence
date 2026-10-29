"""Tests for the core pieces. They use tiny made-up contracts, so no download is needed."""
import numpy as np

from src.chunking import paragraph_chunks, window_chunks
from src.config import Config
from src.data import assign_split, mini
from src.evaluate import calibrate, collect, summarize
from src.indexer import build_index, tokenize
from src.metrics import abstention_rates, precision_recall
from src.retriever import Retriever, split_query

DOC_A = ("Section 1. Term.\n\nThis agreement lasts five years from the effective date.\n\n"
         "Section 2. Termination.\n\nEither party may terminate for convenience with thirty days notice.\n\n"
         "Section 3. Governing law.\n\nThis agreement is governed by the laws of Delaware.")
DOC_B = ("Pricing schedule.\n\nThe price per unit is ten dollars and payment is due in sixty days.\n\n"
         "Delivery.\n\nGoods are shipped by sea freight to the warehouse.")
CORPUS = {"a.txt": DOC_A, "b.txt": DOC_B}


def test_window_chunk_offsets_match_text():
    chunks = window_chunks(DOC_A, "a.txt", 60, 10)
    assert chunks[0]["start"] == 0
    assert chunks[-1]["end"] == len(DOC_A)
    for c in chunks:
        assert DOC_A[c["start"]:c["end"]] == c["text"]
        assert c["end"] - c["start"] <= 60
    assert chunks[1]["start"] == 50


def test_paragraph_chunk_offsets_match_text_and_respect_limit():
    chunks = paragraph_chunks(DOC_A, "a.txt", 120, 10)
    assert len(chunks) > 1
    for c in chunks:
        assert DOC_A[c["start"]:c["end"]] == c["text"]
        assert len(c["text"]) <= 120


def test_long_paragraph_is_split():
    text = "word " * 100
    chunks = paragraph_chunks(text, "x.txt", 100, 20)
    assert len(chunks) > 1
    assert all(text[c["start"]:c["end"]] == c["text"] for c in chunks)


def test_bm25_retrieval_finds_right_chunk():
    cfg = Config(chunk_size=120, overlap=20)
    r = Retriever(build_index(CORPUS, cfg, use_cache=False), cfg)
    top = r.rank("which law governs this agreement Delaware")["passages"][0]
    assert top["doc_id"] == "a.txt"
    assert "Delaware" in top["text"]


def test_scoping_restricts_to_named_document():
    cfg = Config(chunk_size=120, overlap=20, scope_to_document=True)
    r = Retriever(build_index(CORPUS, cfg, use_cache=False), cfg)
    info = r.rank("Consider the Pricing schedule; what is the governing law of the agreement?")
    assert {p["doc_id"] for p in info["passages"]} == {"b.txt"}
    assert split_query("no title here") == (None, "no title here")


def test_precision_and_recall_values():
    truth = [{"doc_id": "a.txt", "start": 100, "end": 200}]
    hit = {"doc_id": "a.txt", "start": 150, "end": 250}
    p, r = precision_recall([hit], truth)
    assert p == 0.5 and r == 0.5
    other_doc = {"doc_id": "b.txt", "start": 100, "end": 200}
    assert precision_recall([other_doc], truth) == (0.0, 0.0)
    assert precision_recall([], truth) == (0.0, 0.0)


def test_recall_does_not_double_count_overlapping_chunks():
    truth = [{"doc_id": "a.txt", "start": 0, "end": 100}]
    chunks = [{"doc_id": "a.txt", "start": 0, "end": 80}, {"doc_id": "a.txt", "start": 50, "end": 100}]
    p, r = precision_recall(chunks, truth)
    assert r == 1.0
    assert p == 1.0


def test_abstention_rates():
    tar, far = abstention_rates([True, False, False, False], [True, True, False])
    assert far == 0.25
    assert abs(tar - 2 / 3) < 1e-9


def test_abstains_below_threshold_and_answers_above():
    cfg = Config(chunk_size=120, overlap=20)
    r = Retriever(build_index(CORPUS, cfg, use_cache=False), cfg)
    good = r.search("governing law Delaware", top_k=2)
    assert not good["abstained"] and good["passages"]
    strict = cfg.copy(threshold=0.99)
    r2 = Retriever(r.index, strict)
    result = r2.search("governing law Delaware")
    assert result["abstained"] and result["passages"] == []
    assert result["message"] == "No relevant clause found"


def test_calibration_separates_easy_cases():
    cfg = Config(chunk_size=120, overlap=20)
    r = Retriever(build_index(CORPUS, cfg, use_cache=False), cfg)
    truth_a = [{"doc_id": "a.txt", "start": DOC_A.index("This agreement is governed"), "end": len(DOC_A)}]
    answerable = [{"query": "governing law Delaware", "snippets": truth_a}]
    unanswerable = [{"query": "zebra helicopter catering"}]
    rec = collect(r, answerable, unanswerable)
    tuned = calibrate(rec, cfg)
    m = summarize(rec, tuned)
    assert m["TAR"] == 1.0 and m["FAR"] == 0.0


def test_split_is_stable_and_mini_size():
    assert assign_split("some query") == assign_split("  some query  ")
    assert assign_split("some query") in ("train", "test")
    tests = [{"snippets": [{"file_path": f"f{i}.txt"}]} for i in range(300)]
    assert len(mini(tests)) == 194
    assert mini(tests) == mini(tests)


def test_stemming_joins_word_forms():
    assert tokenize("governing governed", stem=True) == ["govern", "govern"]
    assert tokenize("governing governed") == ["governing", "governed"]
    cfg = Config(chunk_size=120, overlap=20, stem=True)
    r = Retriever(build_index(CORPUS, cfg, use_cache=False), cfg)
    assert "Delaware" in r.rank("which law is governing")["passages"][0]["text"]
