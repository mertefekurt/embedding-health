from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from embedding_health.models import EmbeddingRecord


def read_jsonl(path: Path) -> list[EmbeddingRecord]:
    records: list[EmbeddingRecord] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON on line {line_number}: {exc.msg}") from exc
        if not isinstance(raw, dict):
            raise ValueError(f"line {line_number} must contain a JSON object")
        records.append(_record_from_mapping(raw, str(line_number)))
    return records


def _record_from_mapping(raw: dict[str, Any], fallback_id: str) -> EmbeddingRecord:
    vector = raw.get("embedding", raw.get("vector"))
    if not isinstance(vector, list):
        raise ValueError(f"record {fallback_id} requires an embedding or vector list")
    try:
        clean_vector = tuple(float(value) for value in vector)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"record {fallback_id} has a non-numeric vector value") from exc
    record_id = str(raw.get("id") or raw.get("doc_id") or fallback_id)
    text = str(raw.get("text") or raw.get("content") or "")
    metadata = {
        key: value
        for key, value in raw.items()
        if key not in {"id", "doc_id", "text", "content", "embedding", "vector"}
    }
    return EmbeddingRecord(id=record_id, text=text, vector=clean_vector, metadata=metadata)
