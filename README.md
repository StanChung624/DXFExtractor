# DXFExtractor

`DXFExtractor` is a Python library for extracting normalized 2D geometry from customer DXF files using `ezdxf`.

It focuses on robust CAD ingestion for:
- direct entities in modelspace
- entities inside block definitions referenced by `INSERT` (including nested inserts)

## Version

- Extraction spec version: **v1.0**
- Project/package version: **0.1.0**
- Python: **3.11+**

## Supported DXF Entities (v1.0)

The extractor currently supports:
- `CIRCLE`
- `LWPOLYLINE` (closed only)
- classic `POLYLINE` (2D + closed only)
- `INSERT` (recursive block-reference traversal)

## Geometry Output

The library returns:
- circles
- closed 2D polylines (with bulge values preserved)
- structured diagnostics

All output coordinates are normalized to world coordinates (WCS XY).

## Transform Rules

`INSERT` transforms are resolved recursively and composed through the full block path.

Accepted transform behavior in v1.0:
- translation
- XY rotation
- uniform scale
- non-uniform scale only where geometry remains valid for this output model

Important policy:
- non-uniformly scaled circles are rejected (`UNSUPPORTED_NONUNIFORM_SCALED_CIRCLE`)
- bulged polylines under unsupported transforms are rejected (`UNSUPPORTED_TRANSFORMED_BULGE_POLYLINE`)

## Out of Scope (v1.0)

Examples of unsupported categories:
- `ARC`, `ELLIPSE`, `SPLINE`, `HATCH`
- text/dimensions/leaders
- 3D solids/surfaces/meshes
- xrefs as extracted geometry
- entity reconstruction from separate primitives

Unsupported or malformed content is reported in diagnostics instead of silently dropped.

## Public API

- `extract_geometry(path: str, config: ExtractionConfig | None = None) -> ExtractionResult`
- `extract_from_doc(doc, config: ExtractionConfig | None = None) -> ExtractionResult`
- `extract_from_modelspace(msp, doc, config: ExtractionConfig | None = None) -> ExtractionResult`

## Quick Start

Install dependencies:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .[dev]
```

Run tests:

```bash
.venv/bin/python -m pytest -q
```

Run extractor script (included):

```bash
.venv/bin/python extract_supported_entities.py "your_file.DXF" -o extraction_result.json
```

## Result Schema (summary)

`ExtractionResult` contains:
- `circles: List[CircleGeometry]`
- `closed_polylines: List[ClosedPolylineGeometry]`
- `diagnostics: List[Diagnostic]`

Each geometry also includes source trace metadata (`handle`, `dxftype`, `layout`, `block_path`) for debugging.
