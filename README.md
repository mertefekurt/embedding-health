# Embedding Health

Check embedding JSONL files for vector quality and retrieval-risk issues. The repository is intentionally plain: a small command, a visible rule surface, and enough examples to make the behavior inspectable.

![Embedding Health cover](assets/readme-cover.svg)

## Where it fits

- for model evaluation, traces, retrieval, and prompt review
- quick local checks without a service dependency
- review notes that should stay easy to reproduce

## Run it

```bash
git clone https://github.com/mertefekurt/embedding-health.git
cd embedding-health
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
embedding-health examples/embeddings.jsonl
```

## Project map

```text
.github/        CI workflow
examples/       sample inputs
src/            package source
tests/          test coverage
.gitignore      project file
pyproject.toml  package metadata
```
