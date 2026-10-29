"""Search: score every chunk, rank them, and decide whether to abstain."""
import numpy as np

from .indexer import encode, tokenize

NO_ANSWER = "No relevant clause found"


def split_query(query):
    """Benchmark style queries look like 'Consider the <contract title>; <question>'.

    Returns (title, question). The title is None when the query does not name a contract.
    """
    q = query.strip()
    if q.lower().startswith("consider the") and ";" in q:
        title, question = q.split(";", 1)
        return title[len("consider the"):].strip(), question.strip()
    return None, q


class Retriever:
    def __init__(self, index, cfg):
        self.index = index
        self.cfg = cfg

    def _bm25_scores(self, question):
        """BM25 divided by the best score a chunk could get for this question.

        The best possible score is the sum of idf * (k1 + 1) over the question words.
        This keeps scores between 0 and 1 and comparable across questions,
        which a threshold needs. Min-max scaling per question would always give the top chunk 1.0.
        """
        bm25 = self.index.bm25
        tokens = [t for t in tokenize(question, self.cfg.stem) if t in bm25.idf]
        if not tokens:
            return np.zeros(len(self.index.chunks))
        raw = bm25.get_scores(tokens)
        best = sum(bm25.idf[t] for t in tokens) * (bm25.k1 + 1)
        return raw / best if best > 0 else np.zeros_like(raw)

    def rank(self, query, k=10):
        """Top k chunks with scores. No abstention is applied here."""
        cfg, idx = self.cfg, self.index
        title, question = split_query(query) if cfg.scope_to_document else (None, query)

        scores = self._bm25_scores(question)
        if cfg.method == "hybrid":
            dense = idx.dense @ encode(cfg.embedding_model, [question])[0]
            scores = (1 - cfg.alpha) * scores + cfg.alpha * dense

        doc_score = None
        if title is not None:
            doc_pos, doc_score = idx.match_document(title)
            scores = np.where(idx.chunk_doc == doc_pos, scores, -np.inf)

        order = np.argsort(-scores)[:k]
        passages = []
        for i in order:
            if not np.isfinite(scores[i]):
                continue
            c = idx.chunks[i]
            passages.append({"doc_id": c["doc_id"], "start": c["start"], "end": c["end"],
                             "score": float(scores[i]), "text": c["text"]})
        top1 = passages[0]["score"] if passages else 0.0
        gap = top1 - passages[1]["score"] if len(passages) > 1 else top1
        return {"passages": passages, "doc_score": doc_score, "top1": top1, "gap": gap}

    def should_abstain(self, info, cfg=None):
        cfg = cfg or self.cfg
        if not info["passages"]:
            return True
        if info["doc_score"] is not None and info["doc_score"] < cfg.doc_threshold:
            return True
        if info["top1"] < cfg.threshold:
            return True
        return info["top1"] < cfg.soft_threshold and info["gap"] < cfg.min_gap

    def search(self, query, top_k=None, threshold=None):
        """Final answer for a user. Returns abstained flag and the passages (empty when abstained).

        threshold, if given, replaces the configured main threshold (the web app slider uses this).
        """
        cfg = self.cfg if threshold is None else self.cfg.copy(threshold=threshold)
        info = self.rank(query, k=max(10, top_k or cfg.top_k))
        abstained = self.should_abstain(info, cfg)
        passages = [] if abstained else info["passages"][: top_k or cfg.top_k]
        return {"abstained": abstained, "message": NO_ANSWER if abstained else "",
                "passages": passages, "top1": info["top1"], "doc_score": info["doc_score"]}
