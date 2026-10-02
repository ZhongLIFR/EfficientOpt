# Technique judge

From the repository root, prepare the endpoint configuration:

```bash
cp evaluation/judge/configs/judge_model.example.json evaluation/judge/configs/judge_model.json
python judge.py --help
```

Edit the model name and set `EFFICIENTOPT_JUDGE_BASE_URL` and
`EFFICIENTOPT_JUDGE_API_KEY` in the environment. A judging run calls the configured
LLM endpoint; `--help` is offline. No API retries are made by default.

Candidate files use this layout:

```text
runs/formal/<model_name>/<problem_id>/
  evaluation.json
  candidate_model.py
  parsed.json        # optional formulation summary
```

```bash
python judge.py --formal-root runs/formal \
  --judge-config evaluation/judge/configs/judge_model.json \
  --out-dir output/judge
```

The default dataset root is `dataset/main`. The loader reads each task's
`problem.md` and `ground_truth/` reference code, results, metadata, and verified
`reference.json`. Use `--dataset-root` to choose another split. `--limit`,
`--models`, and `--problems` filter cases; `--resume` reuses saved judgments.

Verified objectives take precedence over candidate correctness flags. With no
reference or explicit correctness evidence, successful execution remains
unjudged rather than incorrect. The final category is `null`, and manual review
is required; LLM technique attribution cannot override this missing evidence.
Clear solver failures and verified wrong objectives remain category 5.

Reports provide `classified_n`, `unjudged_count`, category counts and proportions.
Proportions exclude unjudged cases, so report coverage with them. This public
entry point does not regenerate the paper's saved judgments automatically.
