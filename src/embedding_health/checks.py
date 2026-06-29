from __future__ import annotations

import json
import math
from collections import Counter, defaultdict

from embedding_health.models import EmbeddingRecord, Finding

SEVERITY_ORDER = {"low": 1, "medium": 2, "high": 3}


def check_embeddings(
    records: list[EmbeddingRecord],
    *,
    similarity_threshold: float = 0.999,
    sample_pairs: int = 20000,
) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(_dimension_findings(records))
    findings.extend(_vector_value_findings(records))
    findings.extend(_duplicate_vector_findings(records))
    findings.extend(_similarity_findings(records, similarity_threshold, sample_pairs))
    return findings


def findings_to_json(findings: list[Finding]) -> str:
    return json.dumps([finding.to_dict() for finding in findings], indent=2) + "\n"


def findings_to_markdown(findings: list[Finding]) -> str:
    if not findings:
        return "# embedding-health report\n\nNo findings.\n"
    lines = ["# embedding-health report", ""]
    counts = Counter(finding.severity for finding in findings)
    lines.append(
        "Findings: "
        + ", ".join(f"{severity}={count}" for severity, count in sorted(counts.items()))
    )
    lines.append("")
    for finding in findings:
        lines.append(
            f"- **{finding.severity}** `{finding.code}` for `{finding.record_id}`: "
            f"{finding.message}"
        )
    return "\n".join(lines) + "\n"


def has_failure(findings: list[Finding], fail_on: str) -> bool:
    threshold = SEVERITY_ORDER[fail_on]
    return any(SEVERITY_ORDER[finding.severity] >= threshold for finding in findings)


def _dimension_findings(records: list[EmbeddingRecord]) -> list[Finding]:
    dimensions = Counter(len(record.vector) for record in records)
    if not dimensions:
        return []
    expected = dimensions.most_common(1)[0][0]
    return [
        Finding(
            code="dimension-mismatch",
            severity="high",
            record_id=record.id,
            message=f"vector has dimension {len(record.vector)}, expected {expected}",
        )
        for record in records
        if len(record.vector) != expected
    ]


def _vector_value_findings(records: list[EmbeddingRecord]) -> list[Finding]:
    findings: list[Finding] = []
    norms: list[tuple[str, float]] = []

    for record in records:
        if any(not math.isfinite(value) for value in record.vector):
            findings.append(
                Finding(
                    code="non-finite-value",
                    severity="high",
                    record_id=record.id,
                    message="vector contains NaN or infinite values",
                )
            )
            continue
        norm = _norm(record.vector)
        norms.append((record.id, norm))
        if norm == 0:
            findings.append(
                Finding(
                    code="zero-vector",
                    severity="high",
                    record_id=record.id,
                    message="vector norm is zero and cannot be used for cosine search",
                )
            )

    positive = [norm for _, norm in norms if norm > 0]
    if not positive:
        return findings
    median = sorted(positive)[len(positive) // 2]
    for record_id, norm in norms:
        if norm > 0 and median > 0 and (norm > median * 3 or norm < median / 3):
            findings.append(
                Finding(
                    code="norm-outlier",
                    severity="medium",
                    record_id=record_id,
                    message=f"vector norm {norm:.4f} is far from median {median:.4f}",
                )
            )
    return findings


def _duplicate_vector_findings(records: list[EmbeddingRecord]) -> list[Finding]:
    groups: dict[tuple[float, ...], list[str]] = defaultdict(list)
    for record in records:
        groups[tuple(round(value, 8) for value in record.vector)].append(record.id)

    findings: list[Finding] = []
    for ids in groups.values():
        if len(ids) > 1:
            findings.append(
                Finding(
                    code="duplicate-vector",
                    severity="medium",
                    record_id=ids[0],
                    message=f"same rounded vector appears in records: {', '.join(ids)}",
                )
            )
    return findings


def _similarity_findings(
    records: list[EmbeddingRecord],
    threshold: float,
    sample_pairs: int,
) -> list[Finding]:
    findings: list[Finding] = []
    checked = 0
    clean = [record for record in records if record.vector and _norm(record.vector) > 0]
    for index, left in enumerate(clean):
        for right in clean[index + 1 :]:
            if len(left.vector) != len(right.vector):
                continue
            checked += 1
            if checked > sample_pairs:
                return findings
            score = _cosine(left.vector, right.vector)
            if score >= threshold and left.text.strip() != right.text.strip():
                findings.append(
                    Finding(
                        code="near-duplicate-vector",
                        severity="low",
                        record_id=left.id,
                        message=f"cosine {score:.4f} with {right.id} but text differs",
                    )
                )
    return findings


def _norm(vector: tuple[float, ...]) -> float:
    return math.sqrt(sum(value * value for value in vector))


def _cosine(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True)) / (_norm(left) * _norm(right))

