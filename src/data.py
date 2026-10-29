"""Small helpers for loading the benchmark queries and the contract text."""
import hashlib
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CORPUS_DIR = DATA_DIR / "corpus"
QUERIES_FILE = DATA_DIR / "cuad_mini.json"
UNANSWERABLE_FILE = DATA_DIR / "unanswerable_queries.json"


def mini(tests, n=194):
    """Pick the 194 queries of LegalBench-RAG-mini using the benchmark authors' own rule."""
    if len(tests) <= n:
        return tests

    def key(t):
        random.seed(t["snippets"][0]["file_path"])
        return random.random()

    return sorted(tests, key=key)[:n]


def assign_split(query):
    """Same query always goes to the same split, about 30 percent go to test."""
    h = int(hashlib.sha256(query.strip().encode("utf-8")).hexdigest(), 16)
    return "test" if h % 10 < 3 else "train"


def doc_path(doc_id):
    """doc_id is the file name, for example 'ABC Agreement.txt'."""
    return CORPUS_DIR / doc_id


def read_doc(doc_id):
    """Read a contract the same way the benchmark offsets were made (default text mode, utf-8)."""
    with open(doc_path(doc_id), encoding="utf-8") as f:
        return f.read()


def load_corpus():
    """Return {doc_id: text} for every contract that was downloaded."""
    return {p.name: read_doc(p.name) for p in sorted(CORPUS_DIR.glob("*.txt"))}


def load_answerable(split=None):
    """Benchmark queries. Each item has: query, split, snippets (doc_id, start, end)."""
    items = json.loads(QUERIES_FILE.read_text(encoding="utf-8"))
    if split:
        items = [q for q in items if q["split"] == split]
    return items


def load_unanswerable(split=None):
    items = json.loads(UNANSWERABLE_FILE.read_text(encoding="utf-8"))
    if split:
        items = [q for q in items if q["split"] == split]
    return items
