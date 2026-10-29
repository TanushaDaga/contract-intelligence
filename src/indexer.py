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

# slow results are saved in this folder so we do not compute them again
CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"

# very common words that tell us nothing, they are ignored in keyword search
STOPWORDS = set(
    "a an the of to in on for and or is are be by with as at this that these those it its any "
    "there under does do can what which who how when where from has have not".split()
)

# the meaning model is kept here after it is loaded once
_encoders = {}


# the tool that cuts a word down to its root
_porter = PorterStemmer()


# lru_cache remembers the answer for words we already stemmed, which makes it faster
@lru_cache(maxsize=None)
def _stem(word):
    return _porter.stem(word)


def tokenize(text, stem=False):
    # lowercase everything and pull out the words and numbers, dropping punctuation
    words = re.findall(r"[a-z0-9]+", text.lower())
    # remove the very common words
    words = [w for w in words if w not in STOPWORDS]
    # if asked, cut each word to its root so governing and governed match
    return [_stem(w) for w in words] if stem else words


def get_encoder(model_name):
    """Load the sentence embedding model once and reuse it."""
    if model_name not in _encoders:
        # imported here so keyword-only runs do not pay the cost of loading this big library
        from sentence_transformers import SentenceTransformer

        _encoders[model_name] = SentenceTransformer(model_name)
    return _encoders[model_name]


def encode(model_name, texts):
    """Unit length vectors, so the dot product is the cosine similarity."""
    enc = get_encoder(model_name)
    # turn each text into a list of 384 numbers, 64 texts at a time, each list scaled to length 1
    return enc.encode(texts, batch_size=64, normalize_embeddings=True, show_progress_bar=False)


# an Index holds everything needed to search: the chunks, the keyword index and the meaning numbers
class Index:
    def __init__(self, corpus, cfg, use_cache=True):
        self.corpus = corpus
        self.cfg = cfg
        # contract names in a fixed order
        self.doc_ids = sorted(corpus)
        self.chunks = self._load_chunks(use_cache)
        # give every contract a number, then note for every chunk which contract number it belongs to
        doc_pos = {d: i for i, d in enumerate(self.doc_ids)}
        self.chunk_doc = np.array([doc_pos[c["doc_id"]] for c in self.chunks])
        # the keyword index is built from the word list of every chunk
        self.bm25 = BM25Okapi([tokenize(c["text"], cfg.stem) for c in self.chunks])
        # meaning numbers are only needed for the hybrid method
        self.dense = self._load_dense(use_cache) if cfg.method == "hybrid" else None
        self._build_doc_matcher()

    # make a short unique name for cache files from the settings that change the chunks
    def _key(self, with_model):
        sig = [self.cfg.chunk_mode, self.cfg.chunk_size, self.cfg.overlap]
        sig += [(d, len(self.corpus[d])) for d in self.doc_ids]
        if with_model:
            sig.append(self.cfg.embedding_model)
        return hashlib.md5(json.dumps(sig).encode()).hexdigest()[:12]

    def _load_chunks(self, use_cache):
        path = CACHE_DIR / f"chunks_{self._key(False)}.json"
        # if we saved these chunks before, just read them
        if use_cache and path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        # otherwise cut every contract into chunks
        chunks = []
        for d in self.doc_ids:
            chunks += make_chunks(self.corpus[d], d, self.cfg)
        # and save them for next time
        if use_cache:
            CACHE_DIR.mkdir(exist_ok=True)
            path.write_text(json.dumps(chunks), encoding="utf-8")
        return chunks

    def _load_dense(self, use_cache):
        path = CACHE_DIR / f"dense_{self._key(True)}.npy"
        if use_cache and path.exists():
            return np.load(path)
        # this is the slow step: turn every chunk into its meaning numbers
        vecs = encode(self.cfg.embedding_model, [c["text"] for c in self.chunks])
        if use_cache:
            CACHE_DIR.mkdir(exist_ok=True)
            np.save(path, vecs)
        return vecs

    def _build_doc_matcher(self):
        """Used when a query names its contract. Compares the title in the query with the start of each contract."""
        heads = []
        for d in self.doc_ids:
            # the file name has company names in it, so use it along with the first 3000 characters
            name = Path(d).stem.replace("_", " ").replace("-", " ")
            heads.append(name + " " + self.corpus[d][:3000])
        # TF-IDF turns each text into word importance numbers, rare words count more
        self.doc_vectorizer = TfidfVectorizer(stop_words="english", sublinear_tf=True)
        self.doc_matrix = self.doc_vectorizer.fit_transform(heads)

    def match_document(self, title):
        """Returns (position of best contract, similarity from 0 to 1)."""
        # compare the title with every contract at once and get one similarity per contract
        sims = (self.doc_matrix @ self.doc_vectorizer.transform([title]).T).toarray().ravel()
        # the contract with the highest similarity wins
        best = int(sims.argmax())
        return best, float(sims[best])


def build_index(corpus, cfg, use_cache=True):
    return Index(corpus, cfg, use_cache)
