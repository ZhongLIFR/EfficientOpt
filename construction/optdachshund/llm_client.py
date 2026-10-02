from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any

JsonDict = dict[str, Any]


class LLMClientError(RuntimeError):
    pass


def call_openai_compatible_chat(
    model_cfg: JsonDict,
    messages: list[JsonDict],
    timeout_seconds: int = 120,
) -> JsonDict:
    api_key = str(model_cfg.get("api_key", "") or "").strip()
    if not api_key:
        api_key_env = str(model_cfg.get("api_key_env", "") or "").strip()
        api_key = os.environ.get(api_key_env, "").strip() if api_key_env else ""
    if not api_key:
        raise LLMClientError("Missing api_key in reformulation model config.")

    base_url = str(model_cfg.get("base_url", "") or "").strip()
    if not base_url:
        base_url_env = str(model_cfg.get("base_url_env", "") or "").strip()
        base_url = os.environ.get(base_url_env, "").strip() if base_url_env else ""
    base_url = base_url.rstrip("/")
    if not base_url:
        raise LLMClientError("Missing base_url in reformulation model config.")

    payload: JsonDict = {
        "model": model_cfg["model"],
        "messages": messages,
        "temperature": model_cfg.get("temperature", 0.2),
        "max_tokens": model_cfg.get("max_tokens", 4096),
    }
    if "top_p" in model_cfg:
        payload["top_p"] = model_cfg["top_p"]
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8")
            data = json.loads(raw)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise LLMClientError(f"HTTP {exc.code}: {body[:1000]}") from exc
    except urllib.error.URLError as exc:
        raise LLMClientError(f"URL error: {exc}") from exc

    choice = data.get("choices", [{}])[0]
    content = choice.get("message", {}).get("content", "") or ""
    finish_reason = choice.get("finish_reason")
    if not content.strip():
        raise LLMClientError(f"Empty content from model; finish_reason={finish_reason}")
    return {
        "content": content,
        "finish_reason": finish_reason,
        "latency_seconds": time.perf_counter() - start,
        "usage": data.get("usage", {}),
        "raw_response": data,
    }


def extract_json(text: str) -> Any:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end_obj = cleaned.rfind("}")
        start_arr = cleaned.find("[")
        end_arr = cleaned.rfind("]")
        if start_arr != -1 and end_arr > start_arr and (start == -1 or start_arr < start):
            return json.loads(cleaned[start_arr : end_arr + 1])
        if start != -1 and end_obj > start:
            return json.loads(cleaned[start : end_obj + 1])
        raise
