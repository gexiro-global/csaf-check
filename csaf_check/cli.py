"""Command line entry point for csaf-check."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from .validator import validate, validator_available


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csaf-check",
        description="Validate a CSAF 2.0 advisory against the strict schema.",
    )
    parser.add_argument("document", help="path to a CSAF JSON document, or '-' for stdin")
    parser.add_argument("--json", action="store_true", help="emit the raw result as JSON")
    parser.add_argument(
        "--require-validator",
        action="store_true",
        help="exit non-zero when the validator is unavailable instead of reporting UNKNOWN",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Exit codes: 0 valid | 1 invalid | 2 usage/parse error | 3 validator unavailable."""
    args = build_parser().parse_args(argv)

    try:
        if args.document == "-":
            document = json.load(sys.stdin)
        else:
            with open(args.document, "r", encoding="utf-8") as handle:
                document = json.load(handle)
    except OSError as exc:
        print(f"cannot read document: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"document is not valid JSON: {exc}", file=sys.stderr)
        return 2

    result = validate(document)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    elif not result.available:
        print("UNKNOWN - validator unavailable")
        print(f"  {result.note}")
    elif result.is_valid is None:
        print("UNKNOWN - validator returned no verdict")
        print(f"  {result.note}")
    elif result.is_valid:
        print("VALID - all mandatory CSAF 2.0 tests passed")
    else:
        print(f"INVALID - {len(result.errors)} mandatory test failure(s)")
        for err in result.errors:
            print(f"  - {err}")

    if not result.conclusive:
        return 3 if args.require_validator else 0
    return 0 if result.is_valid else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
