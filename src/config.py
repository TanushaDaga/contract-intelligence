"""All pipeline choices live here so the improvement loop can change them without touching code."""
import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "configs"


@dataclass
class Config:
    name: str = "baseline"
    # how the contracts are cut into chunks: "window" (fixed size) or "paragraph" (blank line boundaries)
    chunk_mode: str = "window"
    chunk_size: int = 1000
    overlap: int = 150
    # "bm25" or "hybrid" (bm25 plus dense embeddings)
    method: str = "bm25"
    # reduce words to their stem for BM25 (governing and governed both become govern)
    stem: bool = False
    # weight of the dense score in the hybrid score, the rest goes to bm25
    alpha: float = 0.5
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    # if the query names a contract ("Consider the X; question"), search only inside that contract
    scope_to_document: bool = False
    # abstain when the best contract match is weaker than this (only used when scoped)
    doc_threshold: float = 0.0
    # abstain when the best chunk score is lower than this
    threshold: float = 0.0
    # extra rule: abstain when best score is below soft_threshold and best minus second best is below min_gap
    soft_threshold: float = 0.0
    min_gap: float = 0.0
    top_k: int = 3

    def save(self, path):
        Path(path).write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})

    def copy(self, **changes):
        data = asdict(self)
        data.update(changes)
        return Config(**data)


def baseline_config():
    return Config(name="baseline")
