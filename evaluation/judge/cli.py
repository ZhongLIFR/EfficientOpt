from __future__ import annotations

import argparse
from pathlib import Path

from .core.runner import run_judge


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the path-configurable EfficientOpt LLM Judge.")
    parser.add_argument("--dataset-root", type=Path, default=Path(__file__).resolve().parents[2] / "dataset/main")
    parser.add_argument("--formal-root", required=True)
    parser.add_argument("--baseline-root", default=None, help="Optional ordinary/ and technique/ runner results; defaults to packaged private results.")
    parser.add_argument("--judge-config", required=True)
    parser.add_argument("--knowledge-base", default=None)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--dataset-id", default="efficientopt")
    parser.add_argument("--case-file", default=None, help="JSON/JSONL list of model_name/problem_id pairs.")
    parser.add_argument("--models", default="")
    parser.add_argument("--problems", default="")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--api-retries", type=int, choices=range(4), default=0, help="Additional attempts per failed API call (0-3; default: 0).")
    parser.add_argument("--max-direct-code-chars", type=int, default=24000)
    parser.add_argument("--code-chunk-chars", type=int, default=12000)
    parser.add_argument("--resume", action="store_true")
    return parser


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    run_judge(
        dataset_root=args.dataset_root,
        formal_root=args.formal_root,
        baseline_root=args.baseline_root,
        judge_config_path=args.judge_config,
        out_dir=args.out_dir,
        knowledge_base_path=args.knowledge_base,
        dataset_id=args.dataset_id,
        case_file=args.case_file,
        models=[value.strip() for value in args.models.split(",") if value.strip()],
        problems=[value.strip() for value in args.problems.split(",") if value.strip()],
        limit=args.limit,
        timeout=args.timeout,
        api_retries=max(0, args.api_retries),
        resume=args.resume,
        max_direct_code_chars=args.max_direct_code_chars,
        code_chunk_chars=args.code_chunk_chars,
    )


if __name__ == "__main__":
    main()
