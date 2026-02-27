#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(prog="glyphser-conformance")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("run", help="Run conformance suite (stub)")
    sub.add_parser("verify", help="Verify results (stub)")
    sub.add_parser("report", help="Generate report (stub)")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return 2

    print(f"Glyphser conformance: {args.command} (STUB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
