"""Lists concrete failures of a configuration on the TRAIN split, grouped by cause.

  python error_analysis.py                         uses configs/final_config.json
  python error_analysis.py --config configs/baseline_config.json

Writes error_analysis_train.md. Causes are guessed with simple rules, so read the cases yourself.
"""
import argparse
import re

from src.config import CONFIG_DIR, Config
from src.data import ROOT, load_answerable, load_corpus, load_unanswerable
from src.evaluate import collect
from src.indexer import build_index, tokenize
from src.retriever import Retriever, split_query

CROSS_REF = re.compile(r"\b(section|article|clause|subject to|pursuant to|as defined)\b", re.I)


def clip(text, n=260):
    return " ".join(text.split())[:n]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=str(CONFIG_DIR / "final_config.json"))
    args = parser.parse_args()

    cfg = Config.load(args.config)
    corpus = load_corpus()
    r = Retriever(build_index(corpus, cfg), cfg)
    rec = collect(r, load_answerable("train"), load_unanswerable("train"))

    groups = {"false_abstention": [], "span_truncation": [], "cross_reference": [],
              "lexical_mismatch": [], "other_wrong_section": [], "wrong_document": [], "hallucinated_match": []}

    for x in rec["ans"]:
        info = x["info"]
        if r.should_abstain(info):
            groups["false_abstention"].append(x)
            continue
        top3 = info["passages"][:3]
        gt_text = " ".join(s["answer"] for s in x["snippets"])
        recall3 = x["pr"][3][1]
        if recall3 >= 0.95:
            continue
        if not any(p["doc_id"] in {s["doc_id"] for s in x["snippets"]} for p in top3):
            groups["wrong_document"].append(x)
        elif CROSS_REF.search(gt_text):
            groups["cross_reference"].append(x)
        elif recall3 > 0:
            groups["span_truncation"].append(x)
        elif not set(tokenize(split_query(x["query"])[1], cfg.stem)) & set(tokenize(gt_text, cfg.stem)):
            groups["lexical_mismatch"].append(x)
        else:
            groups["other_wrong_section"].append(x)

    for x in rec["un"]:
        if not r.should_abstain(x["info"]):
            groups["hallucinated_match"].append(x)

    lines = [f"# Failure cases on train, config {cfg.name}", ""]
    for name, items in groups.items():
        lines += [f"## {name} ({len(items)})", ""]
        for x in items[:6]:
            info = x["info"]
            top = info["passages"][0] if info["passages"] else None
            lines.append(f"- query: {x['query']}")
            if "snippets" in x:
                s = x["snippets"][0]
                lines.append(f"  - truth: {s['doc_id']} {s['start']}:{s['end']} R@3={x['pr'][3][1]:.2f}: {clip(s['answer'])}")
            if top:
                lines.append(f"  - top1: {top['doc_id']} {top['start']}:{top['end']} score={top['score']:.3f}: {clip(top['text'])}")
            lines.append(f"  - doc_score={info['doc_score']}, top1={info['top1']:.3f}, gap={info['gap']:.3f}")
        lines.append("")
    out = ROOT / "error_analysis_train.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print({k: len(v) for k, v in groups.items()})
    print("written", out.name)


if __name__ == "__main__":
    main()
