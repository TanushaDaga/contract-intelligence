"""Command line interface.

  python cli.py query "Does this agreement allow sublicensing?"
  python cli.py evaluate --split train
  python cli.py evaluate --split test --config configs/baseline_config.json
"""
import argparse
import json
import time
from pathlib import Path

from src.config import CONFIG_DIR, Config
from src.data import ROOT, load_answerable, load_corpus, load_unanswerable
from src.evaluate import KS, collect, diagnose, summarize
from src.indexer import build_index
from src.retriever import Retriever

TEST_LOG = ROOT / "test_run_log.jsonl"


def load_retriever(config_path):
    cfg = Config.load(config_path)
    corpus = load_corpus()
    return Retriever(build_index(corpus, cfg), cfg), cfg


def run_query(args):
    retriever, cfg = load_retriever(args.config)
    result = retriever.search(args.text, top_k=args.top_k)
    if result["abstained"]:
        print("Abstained: No relevant clause found in contract corpus.")
        print(f"(best score {result['top1']:.3f})")
        return
    for i, p in enumerate(result["passages"], start=1):
        print(f"[{i}] {p['doc_id']}  chars {p['start']}:{p['end']}  score {p['score']:.3f}")
        print("    " + " ".join(p["text"].split())[:400])
        print()


def run_evaluate(args):
    retriever, cfg = load_retriever(args.config)
    answerable = load_answerable(args.split)
    unanswerable = load_unanswerable(args.split)
    rec = collect(retriever, answerable, unanswerable)
    m = summarize(rec, cfg)
    print(f"config: {cfg.name}   split: {args.split}")
    print(f"answerable queries: {m['n_answerable']}   unanswerable queries: {m['n_unanswerable']}")
    for k in KS:
        print(f"Precision@{k}: {m[f'P@{k}']:.4f}   Recall@{k}: {m[f'R@{k}']:.4f}")
    print(f"True abstention rate (unanswerable): {m['TAR']:.4f}")
    print(f"False abstention rate (answerable):  {m['FAR']:.4f}")
    print("failure breakdown:", json.dumps(diagnose(rec, cfg)))
    if args.split == "test":
        # keep count of how many times the test split was used
        with open(TEST_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"time": time.strftime("%Y-%m-%d %H:%M:%S"), "config": cfg.name, "metrics": m}) + "\n")
        print(f"test run recorded in {TEST_LOG.name}")


def main():
    default_config = str(CONFIG_DIR / "final_config.json")
    parser = argparse.ArgumentParser(description="Contract clause search")
    sub = parser.add_subparsers(dest="command", required=True)

    q = sub.add_parser("query", help="search the contracts")
    q.add_argument("text")
    q.add_argument("--top-k", type=int, default=3)
    q.add_argument("--config", default=default_config)
    q.set_defaults(func=run_query)

    e = sub.add_parser("evaluate", help="score a configuration on a split")
    e.add_argument("--split", choices=["train", "test"], required=True)
    e.add_argument("--config", default=default_config)
    e.set_defaults(func=run_evaluate)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
