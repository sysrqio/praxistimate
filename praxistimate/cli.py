from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from praxistimate import __version__
from praxistimate.audit import (
    audit_manifest,
    build_report,
    bundled_rules_path,
    exit_code_for,
    format_markdown,
    format_text,
    load_manifest,
    load_rules,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="praxistimate")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    audit_p = sub.add_parser("audit", help="Audit practice manifest against TI/KZBV rules")
    audit_p.add_argument("--manifest", required=True, type=Path)
    audit_p.add_argument("--rules", type=Path, default=None)
    audit_p.add_argument("--output", choices=["text", "json", "markdown"], default="text")
    audit_p.add_argument("--out-file", type=Path, default=None)

    args = parser.parse_args(argv)
    if args.command != "audit":
        return 1

    try:
        manifest = load_manifest(args.manifest)
        rules_path = args.rules or bundled_rules_path()
        rules_doc = load_rules(rules_path)
        violations = audit_manifest(manifest, rules_doc)
        report = build_report(args.manifest, manifest, rules_doc, violations)

        if args.output == "json":
            body = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        elif args.output == "markdown":
            body = format_markdown(report)
        else:
            body = format_text(report)

        if args.out_file:
            args.out_file.write_text(body, encoding="utf-8")
        else:
            sys.stdout.write(body)
        return exit_code_for(violations)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
