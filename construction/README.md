# OptDachshund construction

The original multi-agent construction code and 50 OptTips cards are retained in
`optdachshund/`. It generates reformulated tasks and paired reference programs
from separately supplied source problems. Existing benchmark tasks need no
construction step.

From the repository root:

```bash
cd construction
cp optdachshund/configs/reformulation_model.example.json optdachshund/configs/reformulation_model.json
python -m optdachshund.cli --help
python -m optdachshund.cli --raw-problems path/to/source.jsonl --limit 1
```

Set model names in the configuration, plus `OPTDACHSHUND_REFORMULATION_BASE_URL`
and `OPTDACHSHUND_REFORMULATION_API_KEY` in your environment. Commands other than
`--help` call the LLM endpoint; `--plan-only` also calls it. Generated reference
validation additionally needs the dependencies in the root `requirements.txt`.

Source JSONL records have the following fields; source benchmark pools are not
bundled:

```json
{"source_id":"example","dataset":"MAMO","split":"easy_lp","source_question":"...","source_answer":"..."}
```

Outputs go to `optdachshund/outputs/reformulated_benchmark/` by default. Use
`--out-dir` to choose another location. `--repair-rounds` and
`--reference-repair-rounds` bound the repair loops; use `--help` for their defaults.
