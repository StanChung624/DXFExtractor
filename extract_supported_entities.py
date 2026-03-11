#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from dxf_extract import ExtractionConfig, extract_geometry


def _find_default_dxf(cwd: Path) -> Path | None:
    for p in sorted(cwd.iterdir()):
        if p.is_file() and p.suffix.lower() == ".dxf":
            return p
    return None


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract supported DXF entities (CIRCLE + closed 2D polylines)."
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="Path to input DXF. If omitted, the first .dxf file in cwd is used.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("extraction_result.json"),
        help="Path for output JSON (default: extraction_result.json).",
    )
    parser.add_argument("--abs-tol", type=float, default=1e-9)
    parser.add_argument("--rel-tol", type=float, default=1e-9)
    parser.add_argument("--max-insert-depth", type=int, default=16)
    parser.add_argument(
        "--allow-reflection-for-lines-only",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="If true, reflected bulged polylines are rejected; linear-only reflections remain allowed.",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    input_path: Path | None = args.input
    if input_path is None:
        input_path = _find_default_dxf(Path.cwd())
        if input_path is None:
            parser.error("No input DXF provided and no .dxf file found in current directory.")

    input_path = input_path.resolve()
    if not input_path.exists() or not input_path.is_file():
        parser.error(f"Input file not found: {input_path}")

    cfg = ExtractionConfig(
        abs_tol=args.abs_tol,
        rel_tol=args.rel_tol,
        max_insert_depth=args.max_insert_depth,
        allow_reflection_for_lines_only=args.allow_reflection_for_lines_only,
    )

    result = extract_geometry(str(input_path), cfg)
    payload = asdict(result)

    out_path: Path = args.output.resolve()
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"Input: {input_path}")
    print(f"Circles: {len(result.circles)}")
    print(f"Closed polylines: {len(result.closed_polylines)}")
    print(f"Diagnostics: {len(result.diagnostics)}")
    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
