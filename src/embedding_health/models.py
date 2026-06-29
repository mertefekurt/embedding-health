from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EmbeddingRecord:
    id: str
    text: str
    vector: tuple[float, ...]
    metadata: dict[str, Any]


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    record_id: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity,
            "record_id": self.record_id,
            "message": self.message,
        }

