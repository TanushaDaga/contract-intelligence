"""Run a pipeline over the queries, compute metrics, diagnose failures and calibrate thresholds.

The slow part (retrieval) is done once in collect(). After that the abstention rule can be
changed and re-scored instantly, which is what the threshold calibration relies on.
"""
import numpy as np

from .metrics import precision_recall

KS = (1, 3, 5)
MAX_FAR = 0.05
MIN_TAR = 0.80


def collect(retriever, answerable, unanswerable):
    """Retrieve for every query. Abstention is not applied yet."""
    k = max(KS)
    ans = []
    for q in answerable:
        info = retriever.rank(q["query"], k=k)
        pr = {kk: precision_recall(info["passages"][:kk], q["snippets"]) for kk in KS}
        ans.append({"query": q["query"], "snippets": q["snippets"], "info": info, "pr": pr})
    un = [{"query": q["query"], "info": retriever.rank(q["query"], k=k)} for q in unanswerable]
    return {"ans": ans, "un": un}


def _arrays(records):
    infos = [r["info"] for r in records]
    return {
        "top1": np.array([i["top1"] for i in infos], dtype=float),
        "gap": np.array([i["gap"] for i in infos], dtype=float),
        "doc": np.array([np.inf if i["doc_score"] is None else i["doc_score"] for i in infos], dtype=float),
        "empty": np.array([not i["passages"] for i in infos], dtype=bool),
    }


def _abstain_mask(a, doc_t, t, soft, gap):
    """Same rule as Retriever.should_abstain, for many queries at once."""
    return a["empty"] | (a["doc"] < doc_t) | (a["top1"] < t) | ((a["top1"] < soft) & (a["gap"] < gap))


def summarize(rec, cfg):
    """All headline numbers for a configuration. Abstained answerable queries count as zero precision and recall."""
    a_ans, a_un = _arrays(rec["ans"]), _arrays(rec["un"])
    m_ans = _abstain_mask(a_ans, cfg.doc_threshold, cfg.threshold, cfg.soft_threshold, cfg.min_gap)
    m_un = _abstain_mask(a_un, cfg.doc_threshold, cfg.threshold, cfg.soft_threshold, cfg.min_gap)
    out = {"n_answerable": len(rec["ans"]), "n_unanswerable": len(rec["un"])}
    for k in KS:
        p = np.array([r["pr"][k][0] for r in rec["ans"]])
        r_ = np.array([r["pr"][k][1] for r in rec["ans"]])
        out[f"P@{k}"] = float(np.where(m_ans, 0, p).mean()) if len(p) else 0.0
        out[f"R@{k}"] = float(np.where(m_ans, 0, r_).mean()) if len(r_) else 0.0
    out["TAR"] = float(m_un.mean()) if len(m_un) else 0.0
    out["FAR"] = float(m_ans.mean()) if len(m_ans) else 0.0
    return out


def guardrails_ok(m):
    return m["FAR"] < MAX_FAR and m["TAR"] > MIN_TAR


def violation(m):
    """How far the guardrails are from being met. 0 means both are met."""
    v = max(0.0, m["FAR"] - MAX_FAR) + max(0.0, MIN_TAR - m["TAR"])
    return v if guardrails_ok(m) or v > 0 else 1e-6


def diagnose(rec, cfg):
    """Count why answerable queries fail, looking at the top 3 results."""
    a = _arrays(rec["ans"])
    m = _abstain_mask(a, cfg.doc_threshold, cfg.threshold, cfg.soft_threshold, cfg.min_gap)
    counts = {"false_abstention": 0, "wrong_document": 0, "right_document_wrong_section": 0,
              "partly_covered": 0, "well_covered": 0}
    for r, abstained in zip(rec["ans"], m):
        if abstained:
            counts["false_abstention"] += 1
            continue
        top3 = r["info"]["passages"][:3]
        gt_docs = {s["doc_id"] for s in r["snippets"]}
        recall3 = r["pr"][3][1]
        if not any(p["doc_id"] in gt_docs for p in top3):
            counts["wrong_document"] += 1
        elif recall3 == 0:
            counts["right_document_wrong_section"] += 1
        elif recall3 < 0.95:
            counts["partly_covered"] += 1
        else:
            counts["well_covered"] += 1
    return counts


def _midpoints(values):
    """Candidate thresholds halfway between neighbouring score values, plus 0 (never abstain on this rule)."""
    v = np.unique(np.round(values[np.isfinite(values)], 6))
    mids = (v[:-1] + v[1:]) / 2 if len(v) > 1 else v
    return np.concatenate([[0.0], mids, [v[-1] + 1e-6]]) if len(v) else np.array([0.0])


def calibrate(rec, cfg, use_gap=False):
    """Pick abstention thresholds on the records given (train only).

    Goal: meet both guardrails (low FAR, high TAR). Among settings with the same guardrail
    status, keep the one with the best Recall@3. Thresholds sit halfway between neighbouring
    training scores so they are not glued to one query.
    """
    a_ans, a_un = _arrays(rec["ans"]), _arrays(rec["un"])
    r3 = np.array([r["pr"][3][1] for r in rec["ans"]])

    def score(doc_t, t, soft, gap):
        m_a = _abstain_mask(a_ans, doc_t, t, soft, gap)
        m_u = _abstain_mask(a_un, doc_t, t, soft, gap)
        far, tar = m_a.mean(), m_u.mean()
        v = max(0.0, far - MAX_FAR) + max(0.0, MIN_TAR - tar)
        if v == 0 and not (far < MAX_FAR and tar > MIN_TAR):
            v = 1e-6
        return (round(v, 9), -float((r3 * ~m_a).mean()), doc_t + t + soft)

    all_top1 = np.concatenate([a_ans["top1"], a_un["top1"]])
    t_cands = _midpoints(all_top1)
    d_cands = _midpoints(np.concatenate([a_ans["doc"], a_un["doc"]])) if cfg.scope_to_document else [0.0]

    best = min(((score(d, t, 0.0, 0.0), d, t) for d in d_cands for t in t_cands), key=lambda x: x[0])
    _, doc_t, t = best
    soft, gap = 0.0, 0.0

    if use_gap:
        all_gap = np.concatenate([a_ans["gap"], a_un["gap"]])
        gap_cands = np.quantile(all_gap, [0.05, 0.1, 0.2, 0.3, 0.5])
        soft_cands = [s for s in t_cands if s > t]
        base = score(doc_t, t, 0.0, 0.0)
        best_gap = min(((score(doc_t, t, s, g), s, g) for s in soft_cands for g in gap_cands),
                       key=lambda x: x[0], default=None)
        if best_gap is not None and best_gap[0] < base:
            _, soft, gap = best_gap

    return cfg.copy(doc_threshold=float(doc_t), threshold=float(t), soft_threshold=float(soft), min_gap=float(gap))
