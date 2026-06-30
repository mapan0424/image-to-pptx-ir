"""Command line interface for PPTX-IR."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from . import __version__
from .preview import write_svg
from .validator import detect_kind, validate_document


def _load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError("file not found: {}".format(path))
    except json.JSONDecodeError as exc:
        raise ValueError("invalid JSON at line {}, column {}: {}".format(exc.lineno, exc.colno, exc.msg))


def _validate(args: argparse.Namespace) -> int:
    try:
        document = _load(args.input)
    except ValueError as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 2
    result = validate_document(document, args.kind)
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        status = "PASS" if result.valid else "FAIL"
        print("{} {} — {} error(s), {} warning(s)".format(status, args.input, len(result.errors), len(result.warnings)))
        for issue in result.issues:
            print("  {} {} {}: {}".format(issue.severity.upper(), issue.code, issue.path, issue.message))
    return 1 if result.errors or (args.strict and result.warnings) else 0


def _inspect(args: argparse.Namespace) -> int:
    try:
        document = _load(args.input)
    except ValueError as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 2
    kind = detect_kind(document)
    if kind == "render":
        elements = document.get("elements", [])
        counts: Dict[str, int] = {}
        for element in elements:
            key = str(element.get("type", "unknown")) if isinstance(element, dict) else "invalid"
            counts[key] = counts.get(key, 0) + 1
        print(json.dumps({
            "kind": kind,
            "canvas": document.get("canvas"),
            "elementCount": len(elements),
            "elementTypes": counts,
            "layerCount": len(document.get("layerRules", {})),
        }, ensure_ascii=False, indent=2))
    elif kind == "semantic":
        print(json.dumps({
            "kind": kind,
            "title": document.get("title"),
            "regionCount": len(document.get("regions", [])),
        }, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"kind": "unknown"}, indent=2))
        return 1
    return 0


def _preview(args: argparse.Namespace) -> int:
    try:
        document = _load(args.input)
    except ValueError as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 2
    result = validate_document(document, "render")
    if result.errors:
        print("error: preview refused because the IR has {} validation error(s)".format(len(result.errors)), file=sys.stderr)
        return 1
    write_svg(document, args.output, args.input.name)
    print("Wrote {}".format(args.output))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pptx-ir", description="Validate and preview Image-to-PPTX IR documents.")
    parser.add_argument("--version", action="version", version="%(prog)s " + __version__)
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="Run schema-inspired and semantic checks.")
    validate.add_argument("input", type=Path)
    validate.add_argument("--kind", choices=("auto", "semantic", "render"), default="auto")
    validate.add_argument("--strict", action="store_true", help="Treat warnings as a failing exit status.")
    validate.add_argument("--json", action="store_true", help="Emit a machine-readable report.")
    validate.set_defaults(handler=_validate)

    inspect = commands.add_parser("inspect", help="Print a compact document inventory.")
    inspect.add_argument("input", type=Path)
    inspect.set_defaults(handler=_inspect)

    preview = commands.add_parser("preview", help="Create a deterministic SVG diagnostic preview.")
    preview.add_argument("input", type=Path)
    preview.add_argument("output", type=Path)
    preview.set_defaults(handler=_preview)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
