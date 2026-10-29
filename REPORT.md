# Evaluation Report

## Summary

I built a clause search system for contracts. For a question it returns the top passages with the contract name, character start and end, and a score, or it returns nothing and says "No relevant clause found". The final pipeline searches inside the contract named in the question, cuts contracts at paragraph breaks, ranks chunks with a mix of BM25 and MiniLM embeddings (80 percent dense, 20 percent BM25), and abstains using thresholds fitted on the train split. On the test split (54 answerable and 12 unanswerable queries) it gets Recall@3 of 0.554 and Precision@3 of 0.109, against 0.086 and 0.013 for the BM25 baseline. It wrongly abstained on 1 of 54 answerable test queries and correctly abstained on 7 of 12 unanswerable ones (58 percent). The abstention targets were not reached: on train the true abstention rate is 79 percent (target above 80) and the false abstention rate is 5.7 percent (target below 5), and on test the true abstention rate is only 58 percent. No LLM is used.

## System design

| Part | Choice | Alternatives considered |
|---|---|---|
| Chunking | Paragraph chunks: neighbouring paragraphs are joined up to 1000 characters, longer paragraphs are cut into windows (overlap 100). Every chunk stores its exact start and end, so it can be compared with the ground truth directly | Fixed windows of 400 to 1000 characters (was the choice in round 1), smaller chunks with hybrid scoring |
| Ranking | BM25 and MiniLM dense score, combined as (1 - alpha) * BM25 + alpha * dense, alpha = 0.8 | BM25 only, other alpha values from 0.2 to 1.0 (dense only) |
| Score scale | BM25 is divided by the best score a chunk could reach for that question, so scores are comparable across questions | Min-max scaling per question. It always gives the top chunk 1.0, which makes a threshold useless |
| Contract scoping | The benchmark queries look like "Consider the <contract title>; <question>". The title is matched to a contract (TF-IDF on file name and first 3000 characters) and only that contract is searched, using only the question part | Searching all contracts with the full query text |
| Abstention | Abstain if the contract match is weak, or the best chunk score is under a threshold. An optional second rule uses the gap between first and second chunk (tried, not kept) | One global threshold only |
| Threshold fitting | Search all thresholds on train and keep the ones that meet the guardrails, then the best Recall@3. Thresholds are placed halfway between neighbouring train scores | F1 of abstention (not used, because the guardrails state the goal directly) |
| Word stemming | Porter stemmer for BM25, available as a setting, not in the final configuration | none |

Why these choices: BM25 is good at exact legal words and numbers, dense vectors help when the clause uses different words than the question. Both run on a CPU, so no confidential contract text leaves the machine.

## LLM use

No LLM was used. The brief makes it optional. The main problems found in the error analysis are about ranking inside one contract and wording differences, and a small local reranker or embedding model could be tried for those before an LLM. An LLM would add latency and, if hosted, would send confidential contracts to a third party. I did not measure an LLM, so I make no claim about how much it would help.

## Evaluation setup

- Data: LegalBench-RAG mini, CUAD only. 194 queries over 29 contracts. Offsets were checked: `document[start:end]` equals the answer text for all 272 spans.
- Split with the given hash function: 140 train queries and 54 test queries.
- Unanswerable queries: 36 written before the first loop run and not edited afterwards. 24 are in train and 12 in test. 22 name a real contract with an unrelated question, 6 name a contract that is not in the corpus, 8 have no contract title.
- Metrics: character level Precision@k and Recall@k for k = 1, 3, 5 over answerable queries, as in the LegalBench-RAG paper. Precision@k is overlap divided by total retrieved length. Recall@k is the share of answer characters retrieved. When the system abstains on an answerable query, both are 0 for that query.
- Abstention: True Abstention Rate (TAR) is the share of unanswerable queries where nothing was returned. False Abstention Rate (FAR) is the share of answerable queries where nothing was returned.
- Retrieval is over all 29 contracts, not only the contract in the question.
- **The test split was run 3 times in total** (see `test_run_log.jsonl`): once for the baseline, once for the round 1 final configuration, and once for the round 2 final configuration reported here. I did the work in two rounds. In round 1 the loop ended with fixed 1000 character chunks and a hybrid score. After seeing its test numbers I did a second round (stemming, a wider alpha grid, a chunk size search with hybrid scoring, a precision guardrail and a retry of stemming). The round 2 ideas came from the train error analysis and from the low precision, not from test failures, but I had seen the round 1 test numbers, so the test set is not completely untouched. The round 1 log is kept in `experiment_log_round1.json` and `configs/final_config_round1.json`.

## Results

Train (140 answerable, 24 unanswerable queries):

| Metric | Baseline | Final |
|---|---|---|
| Precision@1 | 0.0048 | 0.1712 |
| Precision@3 | 0.0112 | 0.1078 |
| Recall@1 | 0.0152 | 0.3066 |
| Recall@3 | 0.0653 | 0.5375 |
| Recall@5 | 0.1615 | 0.6384 |
| True abstention rate | 0.000 (0 of 24) | 0.792 (19 of 24) |
| False abstention rate | 0.000 (0 of 140) | 0.057 (8 of 140) |

Test (54 answerable, 12 unanswerable queries):

| Metric | Baseline | Final |
|---|---|---|
| Precision@1 | 0.0031 | 0.1738 |
| Precision@3 | 0.0126 | 0.1085 |
| Recall@1 | 0.0185 | 0.4006 |
| Recall@3 | 0.0863 | 0.5536 |
| Recall@5 | 0.1328 | 0.6487 |
| True abstention rate | 0.000 (0 of 12) | 0.583 (7 of 12) |
| False abstention rate | 0.000 (0 of 54) | 0.019 (1 of 54) |

Round 1 final configuration (fixed 1000 character windows, for comparison): train Recall@3 0.543, Precision@3 0.093, TAR 0.79, FAR 0.043. Test Recall@3 0.485, Precision@3 0.084, TAR 0.58, FAR 0.0. Round 2 raised Precision@3 by 15 percent on train and 29 percent on test, left Recall@3 about the same on train, and raised it on test.

Train to test gap for the final configuration:
- Retrieval: Recall@3 is 0.538 on train and 0.554 on test, and Precision@3 is 0.108 and 0.109. There is no sign of overfitting in retrieval. The baseline is also slightly higher on test than on train (0.086 against 0.065), so the test queries look a little easier. With 54 queries a gap of this size is within normal noise.
- Abstention: TAR drops from 0.79 on train to 0.58 on test. Thresholds were fitted on only 24 unanswerable queries, so they are partly fitted to those examples, and the test set has 12 queries, where one query is 8 points. This is the least reliable number in the report. FAR is low on both splits (5.7 percent on train, 1.9 percent on test), so the thresholds are slightly too lenient on test.
- Precision is low in absolute terms because chunks are up to 1000 characters while many answers are 100 to 500 characters. A perfect chunk containing a 250 character answer scores at most 0.25.
- The big gain over the baseline comes from using the contract title. Without it (train queries with the title removed, searching all contracts, no abstention) Recall@3 for the final pipeline is only 0.091, because questions like "What is the governing law?" are the same for every contract. So the numbers above assume the user names the contract.

## Iteration history

Objective: maximise Recall@3 on train. Guardrails: FAR below 5 percent, TAR above 80 percent, and Precision@3 not below 85 percent of the current best. Recall@3 says whether the right clause is in the three shown to a user. The abstention guardrails stop the system from winning by always answering or always refusing, and the precision guardrail stops it from winning by returning big chunks.

Acceptance rule: a candidate is rejected if Precision@3 falls below 85 percent of the current best. Otherwise it is accepted if its distance from the abstention guardrails is clearly smaller than the current best (by more than 0.01), or if that distance is about equal and Recall@3 rises by at least 0.005, or if Recall@3 stays within 0.01 and Precision@3 rises by at least 10 percent.

How the loop works (`self_improvement.py`, one command): it diagnoses the current best on train (failure counts such as right contract wrong section, partly covered, false abstention), applies the next proposal (a rule or a grid search), scores each candidate on train, calibrates thresholds when the proposal says so, accepts or rejects, and logs everything in `experiment_log.json`. The list of ideas is written in advance, and the diagnosis counts are logged with each step. The loop only reads train data. In the first chunk size search, sizes are never larger than the baseline, because Recall@3 alone would otherwise reward returning huge chunks.

| # | Change | Proposed by | R@3 | P@3 | TAR | FAR | Decision |
|---|---|---|---|---|---|---|---|
| 1 | Baseline: BM25, 1000 chars, overlap 150, never abstains | start | 0.065 | 0.011 | 0.00 | 0.00 | accepted |
| 2 | Grid over chunk size 400 to 1000 and overlap 0 to 150. Best was 1000 with overlap 100 | grid search | 0.083 | 0.017 | 0.00 | 0.00 | accepted (+0.018). Smaller chunks were much worse for BM25 |
| 3 | Search only inside the contract named in the query | rule from diagnosis (125 of 140 failures were right contract, wrong section) | 0.400 | 0.064 | 0.00 | 0.00 | accepted, large gain |
| 4 | Fit abstention thresholds on train | calibration | 0.360 | 0.060 | 0.50 | 0.093 | accepted, because it moved the guardrails much closer (distance 0.80 to 0.34), at a cost in recall |
| 5 | Porter stemming for BM25 | rule from error analysis | 0.471 | 0.081 | 0.50 | 0.136 | rejected. Retrieval is clearly better (+0.11 Recall@3) but thresholds could not hold FAR down, so the distance from the guardrails rose (0.34 to 0.39) |
| 6 | Hybrid with MiniLM, alpha 0.5, thresholds refitted | rule | 0.504 | 0.089 | 0.58 | 0.029 | accepted, better recall and better guardrails |
| 7 | Alpha grid 0.2, 0.35, 0.65, 0.8, 0.9, 1.0. Best was 0.8 | grid search | 0.543 | 0.093 | 0.79 | 0.043 | accepted (distance 0.008). 0.9 gave 0.529 and dense only gave 0.497, so 0.8 is a real peak |
| 8 | Stemming again, now on the hybrid | retry of a rejected idea | 0.567 | 0.098 | 0.79 | 0.071 | rejected. Recall@3 +0.024 but FAR rose to 7.1 percent (distance 0.008 to 0.030) |
| 9 | Chunk size search with hybrid, sizes 400 to 800 | grid search | 0.397 | 0.165 | 0.79 | 0.014 | rejected. Best candidate was 400 characters. Precision rose by 77 percent but Recall@3 fell by 0.146 |
| 10 | Paragraph chunks, thresholds refitted | rule | 0.538 | 0.108 | 0.79 | 0.057 | accepted. Recall@3 about the same (-0.006), Precision@3 up 16 percent, but FAR rose from 4.3 to 5.7 percent |
| 11 | Second abstention rule using the gap between rank 1 and rank 2 | calibration | 0.538 | 0.108 | 0.79 | 0.057 | rejected, no setting improved on the single threshold |

Notes on the history:
- Stemming helped retrieval both times (iterations 5 and 8) but was rejected both times because the abstention thresholds could not keep false abstentions down. With only 24 unanswerable queries the calibration is noisy, so I cannot say if stemming is really worse for abstention or if the thresholds were just unlucky. This is the most promising idea to revisit with a bigger unanswerable set. It also shows the acceptance rule puts the abstention guardrails first, which is a design choice that can be argued.
- Iteration 10 traded a little abstention for precision. The accepted final configuration misses both abstention targets on train (TAR 0.792, FAR 0.057), narrowly. It is the closest the loop found that also kept good precision.
- The best alpha of 0.8 is not at the edge of the grid any more: 0.9 and 1.0 were tested and were worse.
- Iteration 9 shows a real trade-off. Small chunks give much higher precision and a much lower FAR, but lose recall. If users care more about seeing the exact clause than about finding it in the top 3, 400 character chunks would be a better choice.

## Error analysis

All cases below are train queries from the final configuration (listed in `error_analysis_train.md`, produced by `error_analysis.py`). On the 140 train answerable queries: 69 well covered, 12 partly covered, 51 right contract wrong section, 8 false abstentions, and 0 wrong contract. Contract matching never failed because the queries name the contract. The cause groups were first assigned by simple rules and then read by hand, so some cases could sit in two groups.

### 1. Lexical mismatch (words in the question differ from the clause, or the wrong words match)

1. HPIL Energytech, "What is the expiration date?" The answer is "The term of this Agreement shall be one (1) year ...". No word is shared with the question. The top chunk was the "No Reliance" clause.
2. HPIL Energytech, "Is there an anti-assignment clause?" The answer is "shall not be assignable by any Party". "Assignment" and "assignable" are different words without stemming. The top chunk was again the "No Reliance" clause, so one generic chunk wins for several unrelated questions.
3. Information System Associates, "What is the governing law?" The answer is "governed by and interpreted under the laws of the State of Florida". The top chunk was a clause about the agreement being a "legal, valid and binding obligation".
4. Flotek, "What is the governing law?" The answer is "governed by and construed in accordance with the laws of the state of Delaware". The top chunk was the environmental indemnity clause, which mentions "applicable ... law". Governing law is among the easiest clause types, so this is a clear weakness of the general embedding model.
5. Information System Associates, "Is there a clause preventing the solicitation of employees?" The answer is "shall not solicit any employee". "Solicitation" and "solicit" do not match, and the top chunk was the confidentiality clause.
6. Theravance, "Is there a covenant not to sue?" The answer span is a long clause about employment ending in a reconstruction, which does not look like a covenant not to sue. The top chunk was the third party rights clause. This label looks debatable, so part of this failure may be label noise.

Diagnosis: no stemming in the final setting, a small general purpose embedding model, and a few "generic" chunks that match everything weakly. Next step: stemming (it improved recall both times) once abstention is calibrated better, and a stronger or legal-tuned embedding model.

### 2. Over-chunking and span truncation (right place, wrong chunk edge or neighbour)

7. MJ Syndicated, "What are the audit rights?" The answer is the paragraph about books of account "open to inspection and examination by any Participant". The top chunk was the next paragraph, about where the venture's funds are held, with a high score (0.514) and a large gap (0.149). The right paragraph ranked lower and only part of it was covered (Recall@3 is 0.56).
8. Papa John's, "Is there an anti-assignment clause?" The answer is the sub-contracting paragraph. The top chunk was 181 characters long, the sentence right after it ("All acts of all Sub-Contractors shall be deemed ...") and Recall@3 is 0. Paragraph chunks can split one provision across two chunks.
9. Because paragraph chunks are up to 1000 characters and many answers are 100 to 500 characters, Precision@3 stays near 0.1 even when the right paragraph is found. Iteration 9 shows shorter chunks raise precision to 0.16 but cost recall.

Diagnosis: provisions often span several neighbouring paragraphs, and neighbouring paragraphs look alike. Next step: merge neighbouring top chunks and show surrounding context to the user.

### 3. Cross-reference ambiguity

10. HPIL Energytech, "Is there a cap on liability?" The answer says the sole and exclusive remedy is "the rights to indemnification set forth in this Section 9". The word "cap" or "limit" never appears, and the meaning depends on Section 9, which is elsewhere. The system returned the "No Reliance" clause (Recall@3 is 0.50, so the answer was only half found).
11. Theravance, "Can this contract be terminated for convenience?" The answer is clause 17, where the company may terminate "in its sole and absolute discretion". The top chunk was clause 24.7 about "agreed termination", chosen because it shares the word "termination". The two termination clauses use similar words and the gap between ranks 1 and 2 was only 0.001.
12. BicycleTX, "Are there any exceptions to competitive restrictions?" The answer is the exception in paragraph 13.2 (holding up to 3 percent of shares). The top chunk was the sibling exception in paragraph 14.4, "nothing in this paragraph 14 shall prevent you ...". Restriction paragraphs and their exceptions refer to each other and use the same words.
13. Jacksonville Jaguars, "What licenses are granted?" The answer is the grant in Section 2.1 ("Club hereby grants to Sponsor ..."). The top chunk was the following text, "The rights granted to Sponsor pursuant to this Section 2 may not be used ...", which talks about the grant and points back to it (Recall@3 is 0.87).
14. Information System Associates, "Does this contract include an exclusivity agreement?" The answer grants an "exclusive, non-transferable license ... subject to the exclusions described in 2.4 below". It depends on a section and on defined terms. The top chunk was boilerplate about the agreement being a legal and binding obligation.

Diagnosis: the system matches text but does not follow references or definitions. Next step: resolve "Section N" references and defined terms at indexing time, or add the referenced clause to the chunk.

### 4. Over-sensitive abstention (false abstention: 8 of 140 on train, 1 of 54 on test)

15. Glu Mobile, "What is the expiration date?" The correct clause ("shall expire on December 31, 2006") was in the top 3 (Recall@3 is 1.0) but the best score was 0.271 and the threshold is 0.315, so the system returned nothing. This is the most damaging kind of error because retrieval was right.
16. Roanoke Gas, "What is the expiration date?" The correct clause ("The term of the Franchise shall be twenty (20) years") was also in the top 3 (Recall@3 is 1.0) but the best score was 0.209, so it abstained.
17. Flotek, "Does this contract include any volume restrictions?" The answer is the definition of "Maximum Quantity". The top score was 0.311 and the system abstained, but retrieval was also wrong here, so the abstention hid a miss rather than a hit.
18. Several of the shown cases are "expiration date" questions. The clause says "term" and not "expiration", so scores for that question type are low. One global threshold does not fit every question type.

Next step: question-type specific thresholds, or a score that is calibrated per question.

### 5. Under-sensitive abstention (answer returned for an unanswerable query, 5 of 24 on train)

19. Dynamex, "Are limousine services provided to executives?" The word "limousine" is not in the corpus. The top chunk about overnight courier service scored 0.459 because of the general transport and service meaning.
20. Union Dental, "Can the affiliate promote the services on TikTok?" The system returned the clause on the services the affiliate will provide (0.420), which matches the words "services" and "affiliate".
21. "Does the agreement cover broadcast rights for the next Olympic Games?" (no contract named). The system returned a Jaguars sponsorship clause on selling food products at the stadium (0.359).
22. "Does the contract mention a sabbatical policy for creative staff?" The system returned the BicycleTX garden leave clause (0.358), which is about time away from work.
23. "What meal allowance is paid during a pandemic lockdown?" The system returned the BicycleTX sick pay clause (0.412). Both are about pay while absent.

Diagnosis: a relevance score only says "similar in topic", not "answers the question". Questions with no contract title are the hardest because they search all 29 contracts and always find some close clause. Next step: a reranker or answer-check model that decides if the passage really answers the question.

## Limitations and next steps

What does not work yet:
- The system depends on the question naming the contract. Without a title, Recall@3 is about 0.09 on train.
- The abstention targets are missed: train TAR 0.79 and FAR 0.057, test TAR 0.58 on only 12 queries. Thresholds were fitted on 24 unanswerable queries, so they are noisy. More unanswerable queries are needed.
- Many questions are not answered even when the contract is right: 51 of 140 train queries had the right contract but the wrong section in the top 3.
- Cross-references and defined terms are not followed, and the embedding model is a general purpose one.
- Stemming helped retrieval but was rejected by the abstention rule, so the final system does not use it.
- Some labels are debatable (for example the covenant not to sue case above). I did not correct any labels.
- The unanswerable queries are only assumed to be unanswerable. I searched the corpus for their key words, but did not read every contract.
- The test split was used three times, and I had seen the round 1 test numbers before the second round of changes (see Evaluation setup).

Before legal users could rely on it:
- Add a reranker or answer check, with a local model, and measure it against this pipeline.
- Show the user the whole clause (merge neighbouring chunks) and flag cross-references.
- Collect many more unanswerable examples and recalibrate. Report confidence intervals, not single numbers.
- Confidentiality: JioStar agreements must not go to an outside service. Everything here runs locally, and the embedding model weights are downloaded once. For production it should run on company servers, with access controls and no logging of contract text. Any LLM would have to be self-hosted.
- Latency: after the index is built, a search over 29 contracts is quick on a CPU. Loading the model takes most of the time of a CLI call (about 30 seconds in my runs), which is why the web app keeps it in memory. For thousands of contracts a vector database and a precomputed index are needed.
