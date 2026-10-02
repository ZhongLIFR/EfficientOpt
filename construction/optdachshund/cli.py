"""Main CLI for the LLM-driven multi-agent reformulation framework.

This command intentionally points to the backbone-LLM batch reformulation path.
There is no deterministic template generation path in this package.
"""

from __future__ import annotations

from .batch_reformulate import build_parser, run_batch


def main() -> None:
    run_batch(build_parser().parse_args())


if __name__ == "__main__":
    main()
