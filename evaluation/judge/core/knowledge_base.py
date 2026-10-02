from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KB_PATH = PACKAGE_ROOT / "configs" / "technique_kb_v8.json"


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


class TechniqueKnowledgeBase:
    def __init__(self, entries: dict[str, dict[str, Any]], source_path: str | None = None):
        self._entries = entries
        self.source_path = source_path

    @classmethod
    def from_json(cls, path: str | Path) -> "TechniqueKnowledgeBase":
        source = Path(path)
        data = json.loads(source.read_text(encoding="utf-8"))
        rows = data.get("techniques", data) if isinstance(data, dict) else data
        entries: dict[str, dict[str, Any]] = {}
        for row in rows if isinstance(rows, list) else []:
            if not isinstance(row, dict) or not row.get("tech_id"):
                continue
            item = dict(row)
            item["tech_id"] = str(item["tech_id"])
            item["semantic_equivalents"] = list(dict.fromkeys(
                _as_list(item.get("semantic_equivalents"))
                + _as_list(item.get("expert_actions"))
                + _as_list(item.get("model_examples"))
            ))
            entries[item["tech_id"]] = item
        return cls(entries, str(source))

    @classmethod
    def default(cls) -> "TechniqueKnowledgeBase":
        return cls.from_json(DEFAULT_KB_PATH)

    def ids(self) -> list[str]:
        return sorted(self._entries)

    def get(self, tech_id: str) -> dict[str, Any]:
        return dict(self._entries.get(str(tech_id), {"tech_id": str(tech_id), "name": "unknown"}))

    def all(self) -> list[dict[str, Any]]:
        return [self.get(tech_id) for tech_id in self.ids()]
