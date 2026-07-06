<p align="center">
  <img src="assets/readme-cover.svg" alt="Embedding Health cover" width="100%" />
</p>

# Embedding Health

![stack](https://img.shields.io/badge/stack-Python-0891b2?style=flat-square) ![python](https://img.shields.io/badge/python-3.11-b45309?style=flat-square) ![license](https://img.shields.io/badge/license-MIT-be185d?style=flat-square) ![ci](https://img.shields.io/badge/ci-GitHub%20Actions-4b5563?style=flat-square)

Check embedding JSONL files for vector quality and retrieval-risk issues.

## Good for

- quick local checks around embedding systems
- small CI jobs where a readable report is enough
- review workflows that need deterministic output
- examples based on `examples/embeddings.jsonl`

## Run it

```bash
python -m pip install -e ".[dev]"
embedding-health examples/embeddings.jsonl
```

## Project notes

- Command: `embedding-health`
- Language: Python
- Python: `>=3.11`
- Tests: `pytest`

## Layout

```text
.github/        CI workflow
examples/       sample inputs
src/            package source
tests/          test coverage
.gitignore      project file
pyproject.toml  package metadata
```

## Check locally

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
python -m embedding_health --help
```
