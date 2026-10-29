"""Download the CUAD part of LegalBench-RAG and prepare the 194 mini queries.

Run from the project folder:  python data/download_data.py

It does three things:
1. downloads benchmarks/cuad.json and the contract files from Hugging Face
2. keeps the 194 mini queries and gives each one a train or test split
3. copies only the contracts used by those queries into data/corpus and checks the offsets
"""
import json
import shutil
import sys
from pathlib import Path

# this lets the script find the src folder even though it is run from inside data
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from huggingface_hub import hf_hub_download

from src.data import CORPUS_DIR, QUERIES_FILE, assign_split, mini

# the place on Hugging Face where the benchmark is stored
REPO = "awinml/legalbench-rag"


def main():
    # download the benchmark file and read all the queries from it
    bench_path = hf_hub_download(REPO, "benchmarks/cuad.json", repo_type="dataset")
    raw = Path(bench_path).read_text(encoding="utf-8")
    tests = json.loads(raw)["tests"]
    print("queries in full cuad benchmark:", len(tests))

    # keep only the 194 queries of the mini version
    chosen = mini(tests)
    print("queries in mini:", len(chosen))

    # only the contracts that the mini queries point to
    files = sorted({s["file_path"] for t in chosen for s in t["snippets"]})
    print("contracts needed:", len(files))
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    for f in files:
        # file_path looks like 'cuad/<name>.txt' in the benchmark
        local = hf_hub_download(REPO, "corpus/" + f, repo_type="dataset")
        # copy the contract into our own data/corpus folder
        shutil.copyfile(local, CORPUS_DIR / Path(f).name)

    out = []
    # bad counts answers whose positions do not match the contract text
    bad = 0
    n_spans = 0
    for t in chosen:
        snippets = []
        for s in t["snippets"]:
            doc_id = Path(s["file_path"]).name
            with open(CORPUS_DIR / doc_id, encoding="utf-8") as fh:
                doc = fh.read()
            start, end = s["span"]
            n_spans += 1
            # sanity check: the text between start and end must be exactly the answer text
            if doc[start:end] != s["answer"]:
                bad += 1
            snippets.append({"doc_id": doc_id, "start": start, "end": end, "answer": s["answer"]})
        # save the query, its train or test split, and its true answer positions
        out.append({"query": t["query"], "split": assign_split(t["query"]), "snippets": snippets})

    QUERIES_FILE.write_text(json.dumps(out, indent=1), encoding="utf-8")
    train = sum(q["split"] == "train" for q in out)
    print("train:", train, "test:", len(out) - train)
    print("spans checked:", n_spans, "offset mismatches:", bad)
    if bad:
        print("WARNING: some offsets do not match the answer text")


if __name__ == "__main__":
    main()
