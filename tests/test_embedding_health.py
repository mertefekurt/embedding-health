import json

from embedding_health.checks import check_embeddings
from embedding_health.cli import main
from embedding_health.io import read_jsonl
from embedding_health.models import EmbeddingRecord


def test_reads_embedding_jsonl(tmp_path) -> None:
    path = tmp_path / "embeddings.jsonl"
    path.write_text('{"id":"a","text":"hello","embedding":[1,2,3]}\n', encoding="utf-8")

    records = read_jsonl(path)

    assert records == [EmbeddingRecord(id="a", text="hello", vector=(1.0, 2.0, 3.0), metadata={})]


def test_finds_dimension_mismatch() -> None:
    findings = check_embeddings(
        [
            EmbeddingRecord("a", "one", (1.0, 0.0, 0.0), {}),
            EmbeddingRecord("b", "two", (1.0, 0.0), {}),
        ]
    )

    assert any(
        finding.code == "dimension-mismatch" and finding.record_id == "b"
        for finding in findings
    )


def test_finds_zero_and_non_finite_vectors() -> None:
    findings = check_embeddings(
        [
            EmbeddingRecord("zero", "zero", (0.0, 0.0), {}),
            EmbeddingRecord("bad", "bad", (float("nan"), 1.0), {}),
        ]
    )

    codes = {finding.code for finding in findings}
    assert "zero-vector" in codes
    assert "non-finite-value" in codes


def test_finds_duplicate_and_near_duplicate_vectors() -> None:
    findings = check_embeddings(
        [
            EmbeddingRecord("a", "alpha", (1.0, 0.0), {}),
            EmbeddingRecord("b", "beta", (1.0, 0.0), {}),
        ],
        similarity_threshold=0.99,
    )

    codes = {finding.code for finding in findings}
    assert "duplicate-vector" in codes
    assert "near-duplicate-vector" in codes


def test_cli_outputs_json_and_exit_code(tmp_path, capsys) -> None:
    path = tmp_path / "embeddings.jsonl"
    path.write_text('{"id":"bad","text":"empty","embedding":[0,0]}\n', encoding="utf-8")

    exit_code = main([str(path), "--format", "json"])

    captured = capsys.readouterr()
    assert exit_code == 2
    assert json.loads(captured.out)[0]["code"] == "zero-vector"
