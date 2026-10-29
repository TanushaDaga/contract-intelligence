"""Character level precision and recall, and the two abstention rates.

A span is (doc_id, start, end) with end not included. All lengths are counted in characters.
"""


def merge(intervals):
    """Join overlapping (start, end) intervals so no character is counted twice."""
    out = []
    # go through the ranges from the earliest start to the latest
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:
            # this range starts before the last one ends, so stretch the last one
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return out


def overlap(start, end, intervals):
    """How many characters of [start, end) fall inside the merged intervals."""
    # for each range, the shared part runs from the later start to the earlier end (never below zero)
    return sum(max(0, min(end, e) - max(start, s)) for s, e in intervals)


# group the ranges by contract, because characters in different contracts can never match
def group_by_doc(spans):
    docs = {}
    for sp in spans:
        docs.setdefault(sp["doc_id"], []).append((sp["start"], sp["end"]))
    return {d: merge(iv) for d, iv in docs.items()}


def precision_recall(retrieved, truth):
    """Precision and recall for one query.

    precision = overlap of the retrieved spans with the truth / total length of retrieved spans
    recall    = truth characters that were retrieved / total truth characters
    retrieved and truth are lists of dicts with doc_id, start, end.
    """
    # the true answer ranges per contract, and how many characters the true answer has in total
    gt = group_by_doc(truth)
    gt_len = sum(e - s for iv in gt.values() for s, e in iv)

    # precision: of all characters we returned, how many are inside the true answer
    total_len = sum(r["end"] - r["start"] for r in retrieved)
    hit = sum(overlap(r["start"], r["end"], gt.get(r["doc_id"], [])) for r in retrieved)
    precision = hit / total_len if total_len else 0.0

    # recall: of all true answer characters, how many did we return (merge first so overlaps count once)
    covered = 0
    for doc, iv in group_by_doc(retrieved).items():
        covered += sum(overlap(s, e, gt.get(doc, [])) for s, e in iv)
    recall = covered / gt_len if gt_len else 0.0
    return precision, recall


def abstention_rates(abstained_answerable, abstained_unanswerable):
    """TAR: share of unanswerable queries where the system returned nothing (higher is better).
    FAR: share of answerable queries where the system wrongly returned nothing (lower is better).
    """
    # each input is a list of True or False, and adding up True values counts them
    tar = sum(abstained_unanswerable) / len(abstained_unanswerable) if len(abstained_unanswerable) else 0.0
    far = sum(abstained_answerable) / len(abstained_answerable) if len(abstained_answerable) else 0.0
    return tar, far
