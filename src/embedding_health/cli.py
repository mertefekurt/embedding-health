from __future__ import annotations

import argparse
import sys
from pathlib import Path

from embedding_health import __version__
from embedding_health.checks import (
    check_embeddings,
    findings_to_json,
    findings_to_markdown,
    has_failure,
)
from embedding_health.io import read_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="embedding-health",
        description="Check embedding JSONL files for vector quality problems.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="JSONL file with embedding or vector fields",
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--similarity-threshold", type=float, default=0.999)
    parser.add_argument("--fail-on", choices=("low", "medium", "high"), default="high")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.input is None:
        parser.print_help()
        return 0
    try:
        records = read_jsonl(args.input)
        findings = check_embeddings(records, similarity_threshold=args.similarity_threshold)
    except (OSError, ValueError) as exc:
        print(f"embedding-health: error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(findings_to_json(findings), end="")
    else:
        print(findings_to_markdown(findings), end="")
    return 2 if has_failure(findings, args.fail_on) else 0
