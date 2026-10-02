from __future__ import annotations

from pathlib import Path


def discover_case_keys(
    formal_root: str | Path,
    *,
    model_filter: set[str] | None = None,
    problem_filter: set[str] | None = None,
) -> list[tuple[str, str]]:
    """Discover unique (model_name, problem_id) pairs from a run directory."""
    root = Path(formal_root)
    found: set[tuple[str, str]] = set()
    if not root.exists():
        return []
    for model_dir in sorted(path for path in root.iterdir() if path.is_dir()):
        if model_filter and model_dir.name not in model_filter:
            continue
        for problem_dir in sorted(path for path in model_dir.iterdir() if path.is_dir()):
            if problem_filter and problem_dir.name not in problem_filter:
                continue
            if (problem_dir / "evaluation.json").exists():
                found.add((model_dir.name, problem_dir.name))
    return sorted(found)
