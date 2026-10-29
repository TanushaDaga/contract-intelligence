"""Automated improvement loop.  Run with:  python self_improvement.py

The loop only ever reads the TRAIN split (benchmark queries and unanswerable queries).

Objective
    primary metric: Recall@3 on train answerable queries
    guardrails:     false abstention rate below 5 percent, true abstention rate above 80 percent,
                    and Precision@3 must not fall by more than 15 percent from the current best

How one iteration works
1. diagnose the current best configuration (why do train queries fail?)
2. a proposal makes one change, or a small grid of changes, to the current best
3. each candidate is retrieved and scored on train, thresholds are calibrated when the proposal asks for it
4. the candidate is accepted only if it is better by the rule in is_better(), otherwise rejected
5. everything is written to experiment_log.json
"""
import json
import time
from dataclasses import asdict

from src.config import CONFIG_DIR, Config, baseline_config
from src.data import ROOT, load_answerable, load_corpus, load_unanswerable
from src.evaluate import calibrate, collect, diagnose, guardrails_ok, summarize, violation
from src.indexer import build_index
from src.retriever import Retriever

# the file where every iteration is written down
LOG_FILE = ROOT / "experiment_log.json"
# the numbers used by the accept or reject rule
# recall must rise by at least this much to count as a real gain
MIN_GAIN = 0.005
# two guardrail distances closer than this count as about equal
VIOLATION_TOLERANCE = 0.01
# precision may not fall below this share of the current best precision
PRECISION_FLOOR = 0.85
# recall may move by this much and still count as about the same
RECALL_TOLERANCE = 0.01
# precision must rise to at least this multiple of the current best (1.10 means 10 percent better)
PRECISION_GAIN = 1.10

# the goal and the rules written in words, saved into the log so a reader can see them
OBJECTIVE = {
    "primary_metric": "Recall@3 on train answerable queries",
    "guardrails": {"false_abstention_rate": "< 0.05", "true_abstention_rate": "> 0.80",
                   "precision_at_3": "not below 85 percent of the current best"},
    "why": ("Recall@3 says whether the right clause is among the three shown to the user. "
            "The guardrails stop the system from winning by always answering or by always refusing."),
    "acceptance_rule": ("Rejected if Precision@3 falls below 85 percent of the current best. Otherwise accepted if its "
                        "abstention guardrail violation is clearly smaller than the current best, or if the violation is "
                        "about equal and Recall@3 rises by at least 0.005, or if Recall@3 stays within 0.01 and "
                        "Precision@3 rises by at least 10 percent."),
}


class Runner:
    """Holds the data and caches indexes so repeated candidates do not rebuild them."""

    def __init__(self):
        self.corpus = load_corpus()
        # only the train split is loaded here, so the loop can never look at test queries
        self.ans = load_answerable("train")
        self.un = load_unanswerable("train")
        self._indexes = {}

    def index_for(self, cfg):
        # settings that change the chunks or the keyword words decide which index we need
        key = (cfg.chunk_mode, cfg.chunk_size, cfg.overlap, cfg.method, cfg.stem)
        # build it only the first time it is needed
        if key not in self._indexes:
            self._indexes[key] = build_index(self.corpus, cfg)
        return self._indexes[key]

    def evaluate(self, cfg, calibrate_thresholds=False, use_gap=False):
        # search every train query once
        rec = collect(Retriever(self.index_for(cfg), cfg), self.ans, self.un)
        # if asked, choose the abstention thresholds from these results
        if calibrate_thresholds:
            cfg = calibrate(rec, cfg, use_gap=use_gap)
        return {"cfg": cfg, "rec": rec, "metrics": summarize(rec, cfg), "diagnosis": diagnose(rec, cfg)}


def is_better(new, best):
    """Returns (accepted, reason) comparing metrics dicts."""
    # rule 1: precision must not fall too much
    if new["P@3"] < PRECISION_FLOOR * best["P@3"]:
        return False, f"Precision@3 fell from {best['P@3']:.3f} to {new['P@3']:.3f}, more than 15 percent"
    # how far each one is from meeting the abstention goals
    v_new, v_best = violation(new), violation(best)
    # rule 2: clearly closer to the abstention goals means accept
    if v_new < v_best - VIOLATION_TOLERANCE:
        return True, f"guardrail violation fell from {v_best:.3f} to {v_new:.3f}"
    # rule 3: clearly further from the abstention goals means reject
    if v_new > v_best + VIOLATION_TOLERANCE:
        return False, f"guardrail violation rose from {v_best:.3f} to {v_new:.3f}"
    # the goals are about equal, so look at recall
    gain = new["R@3"] - best["R@3"]
    # rule 4: recall rose enough means accept
    if gain >= MIN_GAIN:
        return True, f"Recall@3 rose by {gain:.3f} with guardrails about the same"
    # rule 5: recall about the same but precision is clearly better means accept
    if gain >= -RECALL_TOLERANCE and new["P@3"] >= PRECISION_GAIN * best["P@3"]:
        return True, (f"Recall@3 about the same ({gain:+.3f}) and Precision@3 rose from "
                      f"{best['P@3']:.3f} to {new['P@3']:.3f}")
    # otherwise there is not enough reason to switch
    return False, f"Recall@3 changed by {gain:+.3f}, below the {MIN_GAIN} needed"


def pick_best(results):
    """Best candidate of a search: lowest violation first, then Recall@3, then Precision@3."""
    # the violation is rounded into 0.01 steps so nearly equal ones are compared by recall instead
    return min(results, key=lambda r: (round(violation(r["metrics"]) / VIOLATION_TOLERANCE),
                                       -r["metrics"]["R@3"], -r["metrics"]["P@3"]))


# list which settings are different between two configs, used for the log
def diff(old, new):
    a, b = asdict(old), asdict(new)
    return {k: [a[k], b[k]] for k in a if k != "name" and a[k] != b[k]}


# round the decimals so the log is easy to read
def short(m):
    return {k: round(v, 4) if isinstance(v, float) else v for k, v in m.items()}


def proposals():
    """The ordered list of ideas. Each one is (name, proposer, why, candidate maker, calibrate?, use_gap?)."""
    return [
        # idea 1: try smaller chunks and other overlaps with keyword search
        ("chunk_size_grid", "grid search",
         "Chunks that are too big hold many topics and hurt precision. Try smaller chunks and other overlaps, never bigger than the baseline.",
         lambda b: [b.copy(chunk_size=s, overlap=o) for s in (400, 600, 800, 1000) for o in (0, 100, 150) if o < s],
         False, False),
        # idea 2: search only inside the contract named in the question
        ("scope_to_named_document", "rule from diagnosis",
         "Most failures are the right contract but the wrong section. The query names its contract, "
         "so move the title out of the query and search only inside that contract.",
         lambda b: [b.copy(scope_to_document=True)], False, False),
        # idea 3: choose the abstention thresholds from the train queries
        ("calibrate_abstention", "threshold calibration",
         "The system never abstains yet. Pick the score thresholds on the train queries so both guardrails are met.",
         lambda b: [b.copy()], True, False),
        # idea 4: cut words to their roots before keyword search
        ("stemming", "rule from error analysis",
         "Misses like governing against governed, solicit against solicitation, expire against expiration. "
         "Reduce words to their stem (Porter) before BM25.",
         lambda b: [b.copy(stem=True)], True, False),
        # idea 5: add the meaning model, half and half
        ("hybrid_alpha_0.5", "rule",
         "BM25 cannot match synonyms (for example 'exclusivity' and 'sole right'). Add MiniLM dense scores with equal weight.",
         lambda b: [b.copy(method="hybrid", alpha=0.5)], True, False),
        # idea 6: find the best share for the meaning score
        ("hybrid_alpha_grid", "grid search",
         "Tune how much weight the dense score gets, including values above 0.8 and dense only.",
         lambda b: [b.copy(method="hybrid", alpha=a) for a in (0.2, 0.35, 0.65, 0.8, 0.9, 1.0)], True, False),
        # idea 7: try stemming again now that the base is different
        ("stemming_with_hybrid", "retry of a rejected idea",
         "Stemming was rejected earlier when BM25 was the only signal. The base has changed since, so try it again on the hybrid.",
         lambda b: [b.copy(stem=True)], True, False),
        # idea 8: smaller chunks again, now with the meaning score
        ("hybrid_chunk_size_grid", "grid search",
         "The first chunk search used BM25 only. With dense scores, smaller chunks may rank better and raise precision.",
         lambda b: [b.copy(chunk_size=s, overlap=o) for s in (400, 600, 800) for o in (0, 100)], True, False),
        # idea 9: cut at paragraph breaks instead of fixed sizes
        ("paragraph_chunks", "rule",
         "Legal clauses end at paragraph breaks. Cut chunks on blank lines so a chunk is whole clauses and not half of one.",
         lambda b: [b.copy(chunk_mode="paragraph")], True, False),
        # idea 10: a second abstention rule that looks at the gap between first and second
        ("gap_gate", "threshold calibration",
         "Add a second abstention rule: refuse when the best score is lowish and the best chunk barely beats the second.",
         lambda b: [b.copy()], True, True),
    ]


def main():
    start = time.time()
    runner = Runner()
    CONFIG_DIR.mkdir(exist_ok=True)
    # the log starts with the goal and the size of the train data
    log = {"objective": OBJECTIVE, "data": "train split only",
           "n_train_answerable": len(runner.ans), "n_train_unanswerable": len(runner.un), "iterations": []}

    # step 1: score the baseline, save its settings, and treat it as the best so far
    base = runner.evaluate(baseline_config())
    baseline_config().save(CONFIG_DIR / "baseline_config.json")
    best = base
    log["iterations"].append({
        "iteration": 1, "name": "baseline", "proposed_by": "starting point",
        "rationale": "Simplest reasonable pipeline: BM25 over fixed 1000 character chunks, always answers.",
        "config": asdict(base["cfg"]), "train_metrics": short(base["metrics"]),
        "guardrails_met": guardrails_ok(base["metrics"]), "diagnosis": base["diagnosis"],
        "decision": "accepted", "reason": "baseline"})
    print("1 baseline", short(base["metrics"]))

    # go through the ideas one by one, numbering them from 2
    for n, (name, proposer, why, make, do_cal, use_gap) in enumerate(proposals(), start=2):
        # build the candidate settings from the current best and score each one
        candidates = [runner.evaluate(c, do_cal, use_gap) for c in make(best["cfg"])]
        # if the idea has several candidates keep the best of them
        chosen = pick_best(candidates)
        # compare it with the current best using the written rule
        accepted, reason = is_better(chosen["metrics"], best["metrics"])
        entry = {
            "iteration": n, "name": name, "proposed_by": proposer, "rationale": why,
            "diagnosis_before": best["diagnosis"],
            "change": diff(best["cfg"], chosen["cfg"]),
            "candidates_tried": len(candidates),
            "config": asdict(chosen["cfg"]), "train_metrics": short(chosen["metrics"]),
            "guardrails_met": guardrails_ok(chosen["metrics"]), "diagnosis_after": chosen["diagnosis"],
            "decision": "accepted" if accepted else "rejected", "reason": reason,
        }
        # when several candidates were tried, write down all of them
        if len(candidates) > 1:
            entry["all_candidates"] = [{"change": diff(best["cfg"], c["cfg"]), "metrics": short(c["metrics"])}
                                       for c in candidates]
        log["iterations"].append(entry)
        print(n, name, entry["decision"], reason, short(chosen["metrics"]))
        # only an accepted idea becomes the new best
        if accepted:
            best = chosen

    # save the best settings as the final configuration and write the whole log
    final = best["cfg"].copy(name="final")
    final.save(CONFIG_DIR / "final_config.json")
    log["final_train_metrics"] = short(best["metrics"])
    log["baseline_train_metrics"] = short(base["metrics"])
    log["seconds"] = round(time.time() - start)
    LOG_FILE.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print("final config saved to configs/final_config.json")
    print("final train metrics", short(best["metrics"]))


if __name__ == "__main__":
    main()
