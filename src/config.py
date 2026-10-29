"""All pipeline choices live here so the improvement loop can change them without touching code."""
# json is used to save and read the settings as a text file
import json
# dataclass gives us a simple box of settings, asdict turns the box into a dictionary
from dataclasses import asdict, dataclass, fields
from pathlib import Path

# ROOT is the main project folder (two folders up from this file)
ROOT = Path(__file__).resolve().parent.parent
# the folder where the saved settings files live
CONFIG_DIR = ROOT / "configs"


# every setting of the search system is one field below, the values after = are the baseline values
@dataclass
class Config:
    # just a label so we know which setting set this is
    name: str = "baseline"
    # how the contracts are cut into chunks: "window" (fixed size) or "paragraph" (blank line boundaries)
    chunk_mode: str = "window"
    # the biggest number of characters allowed in one chunk
    chunk_size: int = 1000
    # how many characters two neighbouring window chunks share
    overlap: int = 150
    # "bm25" or "hybrid" (bm25 plus dense embeddings)
    method: str = "bm25"
    # reduce words to their stem for BM25 (governing and governed both become govern)
    stem: bool = False
    # weight of the dense score in the hybrid score, the rest goes to bm25
    alpha: float = 0.5
    # the model that turns text into numbers that capture meaning
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
    # how many passages are shown to the user by default
    top_k: int = 3

    # write these settings to a json file
    def save(self, path):
        Path(path).write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    # read a json file and make a Config from it
    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        # only keep keys that are real settings, so old files with extra keys still load
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})

    # make a new Config that is the same as this one except for the changes given
    # example: cfg.copy(alpha=0.8)
    def copy(self, **changes):
        data = asdict(self)
        data.update(changes)
        return Config(**data)


# the simple starting setup that every improvement is compared against
def baseline_config():
    return Config(name="baseline")
