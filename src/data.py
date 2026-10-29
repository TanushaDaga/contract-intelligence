"""Small helpers for loading the benchmark queries and the contract text."""
import hashlib
import json
import random
from pathlib import Path

# the main project folder and the places where data files are kept
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
CORPUS_DIR = DATA_DIR / "corpus"
QUERIES_FILE = DATA_DIR / "cuad_mini.json"
UNANSWERABLE_FILE = DATA_DIR / "unanswerable_queries.json"


def mini(tests, n=194):
    """Pick the 194 queries of LegalBench-RAG-mini using the benchmark authors' own rule."""
    # if there are already few enough queries, keep all of them
    if len(tests) <= n:
        return tests

    # each query gets a random looking number, but it is always the same number for the same contract file
    def key(t):
        random.seed(t["snippets"][0]["file_path"])
        return random.random()

    # sort by that number and keep the first n
    return sorted(tests, key=key)[:n]


def assign_split(query):
    """Same query always goes to the same split, about 30 percent go to test."""
    # turn the query text into a long fixed fingerprint number
    h = int(hashlib.sha256(query.strip().encode("utf-8")).hexdigest(), 16)
    # the last digit of that number decides: 0, 1 or 2 means test, the rest means train
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
    # if a split name is given, keep only the queries of that split
    if split:
        items = [q for q in items if q["split"] == split]
    return items


def load_unanswerable(split=None):
    items = json.loads(UNANSWERABLE_FILE.read_text(encoding="utf-8"))
    # same filtering as above, for the questions the contracts cannot answer
    if split:
        items = [q for q in items if q["split"] == split]
    return items
