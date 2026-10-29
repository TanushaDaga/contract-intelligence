# Contract Clause Search

## Overview

Given a question about a contract, the system returns the passages most likely to hold the answer. Each passage comes with its contract file name, character start and end, and a score. If no passage scores high enough, it returns nothing and says "No relevant clause found". It has a command line tool and a Streamlit web app, and it runs fully on a local machine with no paid API.

It is built on the CUAD part of the LegalBench-RAG benchmark (194 queries, 29 contracts), plus 36 questions that the contracts do not answer. No LLM is used.

## Setup

Python 3.10 or newer (developed on 3.14).

```bash
pip install -r requirements.txt
python data/download_data.py
```

The download script fetches the benchmark and only the 29 contracts the 194 queries use, from Hugging Face. It also checks that `document[start:end]` equals the answer text for every span. The first run of the hybrid method downloads the `all-MiniLM-L6-v2` embedding model (about 90 MB) once.

## How to run

```bash
# web app
streamlit run app.py

# command line search
python cli.py query "Consider the Endorsement Agreement between ABG-Shaq, LLC and Papa John's International, Inc.; Is there a non-compete clause in this contract?"
python cli.py query "Does this agreement allow sublicensing?" --top-k 5

# evaluation (choose train or test, and optionally a config file)
python cli.py evaluate --split train
python cli.py evaluate --split test --config configs/baseline_config.json

# improvement loop (train split only)
python self_improvement.py

# list failure cases on train
python error_analysis.py

# tests
pytest
```

## Architecture

```
data/download_data.py     downloads benchmark and contracts, builds cuad_mini.json with splits
data/build_unanswerable.py  writes the 36 unanswerable queries with splits
src/data.py               mini(), assign_split(), loading helpers
src/config.py             Config dataclass, every pipeline choice is a field
src/chunking.py           window and paragraph chunkers that keep exact character offsets
src/indexer.py            BM25 index (optional Porter stemming), dense vectors, contract name matcher, cache in .cache
src/retriever.py          scores chunks, ranks them, decides to abstain
src/metrics.py            character level precision, recall, abstention rates
src/evaluate.py           runs a pipeline on queries, summary numbers, failure diagnosis, threshold calibration
self_improvement.py       the improvement loop, writes experiment_log.json and configs/final_config.json
cli.py, app.py            the two interfaces
error_analysis.py         lists failures on train
```

Data flow: contract text, then chunks (with offsets), then BM25 and optional dense vectors, then a score per chunk, then the top k chunks, then the abstention check.

Configuration lives in `configs/*.json` and is read into `src/config.py`. `baseline_config.json` is the simple BM25 starting point. `final_config.json` is what the improvement loop ended with. The app and CLI use the final config by default. `experiment_log_round1.json` and `configs/final_config_round1.json` are the results of an earlier first run of the loop, kept for the record (the report explains why there were two rounds).

How scoring works:
- BM25 score is divided by the highest score a chunk could reach for that question, so it lies between 0 and 1 and can be compared across questions.
- Dense score is the cosine similarity between question and chunk embeddings.
- Hybrid score = (1 - alpha) * BM25 + alpha * dense.
- If a query looks like "Consider the <contract title>; <question>", the title is matched to a contract (TF-IDF over the contract file name and first 3000 characters) and only that contract is searched, using only the question part. Queries without a title search all contracts.
- The system abstains if the contract match is weak, or the best chunk score is under a threshold, or (optional) the best score is lowish and the gap to the second chunk is tiny. All thresholds are calibrated on train.

## Reproducing results

Run these in order from the project folder. Times are on a laptop CPU.

| Step | Command | Time |
|---|---|---|
| Download data | `python data/download_data.py` | about 1 minute |
| Improvement loop (train only) | `python self_improvement.py` | about 15 minutes with an empty `.cache` (embeddings are computed for each chunk size tried), about 2 minutes once the cache exists |
| Train numbers | `python cli.py evaluate --split train` and the same with `--config configs/baseline_config.json` | about 30 to 60 seconds each, most of it loading the embedding model |
| Test numbers | `python cli.py evaluate --split test` and the same with `--config configs/baseline_config.json` | about 30 to 60 seconds each, most of it loading the embedding model |

The pipeline has no randomness, so the same code and data give the same numbers. Each test evaluation is appended to `test_run_log.jsonl`, which is how the number of test runs is counted. The file in this repository holds 3 entries (baseline, round 1 final, round 2 final). Running the test evaluation again adds more entries, so please do not treat those as part of the development.

## Assumptions

- Offsets: files are read with Python default text mode and UTF-8, as the benchmark needs. No text normalisation is done, so offsets always match the original file.
- Several answer spans: 52 of the 194 queries have more than one span. Recall counts all spans together, and a retrieved passage is correct if it overlaps any span of that query. Retrieval is over all 29 contracts, not just the contract in the question.
- Precision: sum of overlap with the truth divided by the sum of retrieved lengths, as defined in the benchmark paper. Recall: share of truth characters covered, with overlapping chunks counted once.
- Abstention in metrics: if the system abstains on an answerable query, its precision and recall for that query are zero.
- Chunk edges: windows can cut a sentence in half. Overlap reduces this but does not remove it. The final configuration uses paragraph chunks, which join neighbouring paragraphs up to 1000 characters and cut only paragraphs that are longer than that (with the overlap setting).
- Query titles: the benchmark queries start with the contract title. The system uses that to pick the contract. This is an assumption about how users ask, and the unanswerable set was written in the same style (plus some with no title) so abstention is not made easy by the format.
- Unanswerable queries: no contract can be proven to lack an answer, so before writing them I searched the corpus for their key words and found none. Three kinds are used: a real contract with an unrelated question, a contract that is not in the corpus, and a question with no title.
- Calibration uses few unanswerable examples (24 on train), so thresholds are noisy. This is discussed in the report.
- The test split is only used for final numbers. It was run 3 times in total, and every run is recorded in `test_run_log.jsonl`. The report explains this.

## AI tool usage

I used Claude Code (Anthropic's coding assistant) to help build this project. It wrote the first drafts of the code, tests, README and report from my instructions and the assignment brief, and it ran the experiments I asked for. I read the code, ran the pipeline and tests, and checked the numbers in the report against the logs. The search system itself does not call any AI model at run time.
