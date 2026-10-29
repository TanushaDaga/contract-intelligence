"""Build the search indexes: BM25 over chunks, optional dense vectors, and a small contract name matcher.

Chunks and dense vectors are saved in .cache so they are only computed once per setting.
"""
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
from nltk.stem import PorterStemmer
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer

from .chunking import make_chunks

CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"

STOPWORDS = set(
    "a an the of to in on for and or is are be by with as at this that these those it its any "
    "there under does do can what which who how when where from has have not".split()
)

_encoders = {}


_porter = PorterStemmer()


@lru_cache(maxsize=None)
def _stem(word):
    return _porter.stem(word)


def tokenize(text, stem=False):
    words = re.findall(r"[a-z0-9]+", text.lower())
    words = [w for w in words if w not in STOPWORDS]
    return [_stem(w) for w in words] if stem else words


def get_encoder(model_name):
    """Load the sentence embedding model once and reuse it."""
    if model_name not in _encoders:
        from sentence_transformers import SentenceTransformer

        _encoders[model_name] = SentenceTransformer(model_name)
    return _encoders[model_name]


def encode(model_name, texts):
    """Unit length vectors, so the dot product is the cosine similarity."""
    enc = get_encoder(model_name)
    return enc.encode(texts, batch_size=64, normalize_embeddings=True, show_progress_bar=False)


class Index:
    def __init__(self, corpus, cfg, use_cache=True):
        self.corpus = corpus
        self.cfg = cfg
        self.doc_ids = sorted(corpus)
        self.chunks = self._load_chunks(use_cache)
        doc_pos = {d: i for i, d in enumerate(self.doc_ids)}
        self.chunk_doc = np.array([doc_pos[c["doc_id"]] for c in self.chunks])
        self.bm25 = BM25Okapi([tokenize(c["text"], cfg.stem) for c in self.chunks])
        self.dense = self._load_dense(use_cache) if cfg.method == "hybrid" else None
        self._build_doc_matcher()

    def _key(self, with_model):
        sig = [self.cfg.chunk_mode, self.cfg.chunk_size, self.cfg.overlap]
        sig += [(d, len(self.corpus[d])) for d in self.doc_ids]
        if with_model:
            sig.append(self.cfg.embedding_model)
        return hashlib.md5(json.dumps(sig).encode()).hexdigest()[:12]

    def _load_chunks(self, use_cache):
        path = CACHE_DIR / f"chunks_{self._key(False)}.json"
        if use_cache and path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        chunks = []
        for d in self.doc_ids:
            chunks += make_chunks(self.corpus[d], d, self.cfg)
        if use_cache:
            CACHE_DIR.mkdir(exist_ok=True)
            path.write_text(json.dumps(chunks), encoding="utf-8")
        return chunks

    def _load_dense(self, use_cache):
        path = CACHE_DIR / f"dense_{self._key(True)}.npy"
        if use_cache and path.exists():
            return np.load(path)
        vecs = encode(self.cfg.embedding_model, [c["text"] for c in self.chunks])
        if use_cache:
            CACHE_DIR.mkdir(exist_ok=True)
            np.save(path, vecs)
        return vecs

    def _build_doc_matcher(self):
        """Used when a query names its contract. Compares the title in the query with the start of each contract."""
        heads = []
        for d in self.doc_ids:
            name = Path(d).stem.replace("_", " ").replace("-", " ")
            heads.append(name + " " + self.corpus[d][:3000])
        self.doc_vectorizer = TfidfVectorizer(stop_words="english", sublinear_tf=True)
        self.doc_matrix = self.doc_vectorizer.fit_transform(heads)

    def match_document(self, title):
        """Returns (position of best contract, similarity from 0 to 1)."""
        sims = (self.doc_matrix @ self.doc_vectorizer.transform([title]).T).toarray().ravel()
        best = int(sims.argmax())
        return best, float(sims[best])


def build_index(corpus, cfg, use_cache=True):
    return Index(corpus, cfg, use_cache)
