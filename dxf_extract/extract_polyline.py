from __future__ import annotations

import math

from dxf_extract.config import ExtractionConfig
from dxf_extract.diagnostics import make_diagnostic
from dxf_extract.model import ClosedPolylineGeometry, ExtractionResult, PolylineVertex
from dxf_extract.transforms import classify_xy_transform, normalize_zero, transform_point_2d
from dxf_extract.utils import entity_handle, sanitize, source_trace


def _bool_attr(value) -> bool:
    if callable(value):
        return bool(value())
    return bool(value)


def process_polyline(entity, ctx, out: ExtractionResult, cfg: ExtractionConfig) -> None:
    is_2d = _bool_attr(getattr(entity, "is_2d_polyline", False))
    is_3d = _bool_attr(getattr(entity, "is_3d_polyline", False))
    is_mesh = _bool_attr(getattr(entity, "is_polygon_mesh", False))
    is_face = _bool_attr(getattr(entity, "is_poly_face_mesh", False))

    if is_3d or is_mesh or is_face or not is_2d:
        out.diagnostics.append(
            make_diagnostic(
                "UNSUPPORTED_POLYLINE_MODE",
                handle=entity_handle(entity),
                dxftype=entity.dxftype(),
                block_path=ctx.block_path,
            )
        )
        return

    is_closed = _bool_attr(getattr(entity, "is_closed", False))
    if not is_closed:
        out.diagnostics.append(
            make_diagnostic(
                "MALFORMED_POLYLINE",
                message="Open POLYLINE skipped: closed flag required.",
                handle=entity_handle(entity),
                dxftype=entity.dxftype(),
                block_path=ctx.block_path,
            )
        )
        return

    try:
        ocs = entity.ocs()
        raw_vertices = list(entity.vertices)
    except Exception:
        out.diagnostics.append(
            make_diagnostic(
                "MALFORMED_POLYLINE",
                handle=entity_handle(entity),
                dxftype=entity.dxftype(),
                block_path=ctx.block_path,
            )
        )
        return

    if len(raw_vertices) < 2:
        out.diagnostics.append(
            make_diagnostic(
                "MALFORMED_POLYLINE",
                handle=entity_handle(entity),
                dxftype=entity.dxftype(),
                block_path=ctx.block_path,
            )
        )
        return

    analysis = classify_xy_transform(ctx.transform, cfg)
    if not analysis.preserves_xy_plane:
        out.diagnostics.append(
            make_diagnostic(
                "ENTITY_NOT_IN_XY_PLANE",
                handle=entity_handle(entity),
                dxftype=entity.dxftype(),
                block_path=ctx.block_path,
            )
        )
        return

    has_bulge = any(
        not math.isclose(float(getattr(v.dxf, "bulge", 0.0)), 0.0, abs_tol=cfg.abs_tol, rel_tol=cfg.rel_tol)
        for v in raw_vertices
    )
    if has_bulge:
        allowed = {"rigid", "uniform_scale"}
        if not cfg.allow_reflection_for_lines_only:
            allowed.add("reflection_uniform_scale")
        if analysis.kind not in allowed:
            out.diagnostics.append(
                make_diagnostic(
                    "UNSUPPORTED_TRANSFORMED_BULGE_POLYLINE",
                    handle=entity_handle(entity),
                    dxftype=entity.dxftype(),
                    block_path=ctx.block_path,
                )
            )
            return

    vertices: list[PolylineVertex] = []
    for v in raw_vertices:
        p = ocs.to_wcs(v.dxf.location)
        tx, ty, tz = transform_point_2d(ctx.transform, float(p.x), float(p.y), float(p.z))
        if not math.isclose(tz, 0.0, abs_tol=cfg.abs_tol, rel_tol=cfg.rel_tol):
            out.diagnostics.append(
                make_diagnostic(
                    "ENTITY_NOT_IN_XY_PLANE",
                    handle=entity_handle(entity),
                    dxftype=entity.dxftype(),
                    block_path=ctx.block_path,
                )
            )
            return

        b = float(getattr(v.dxf, "bulge", 0.0))
        if has_bulge and analysis.kind == "reflection_uniform_scale" and not cfg.allow_reflection_for_lines_only:
            b = -b

        vertices.append(
            PolylineVertex(
                x=sanitize(normalize_zero(tx, cfg), cfg),
                y=sanitize(normalize_zero(ty, cfg), cfg),
                bulge=sanitize(b, cfg),
            )
        )

    out.closed_polylines.append(
        ClosedPolylineGeometry(
            vertices=vertices,
            source=source_trace(entity, layout=ctx.layout, block_path=ctx.block_path),
        )
    )
