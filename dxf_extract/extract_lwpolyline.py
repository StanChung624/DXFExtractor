from __future__ import annotations

import math

from dxf_extract.config import ExtractionConfig
from dxf_extract.diagnostics import make_diagnostic
from dxf_extract.model import ClosedPolylineGeometry, ExtractionResult, PolylineVertex
from dxf_extract.transforms import classify_xy_transform, normalize_zero, transform_point_2d
from dxf_extract.utils import entity_handle, sanitize, source_trace


def _is_closed(entity) -> bool:
    closed = getattr(entity, "closed", None)
    if closed is not None:
        return bool(closed)
    is_closed = getattr(entity, "is_closed", None)
    if callable(is_closed):
        return bool(is_closed())
    return bool(is_closed)


def process_lwpolyline(entity, ctx, out: ExtractionResult, cfg: ExtractionConfig) -> None:
    if not _is_closed(entity):
        out.diagnostics.append(
            make_diagnostic(
                "MALFORMED_POLYLINE",
                message="Open LWPOLYLINE skipped: closed flag required.",
                handle=entity_handle(entity),
                dxftype=entity.dxftype(),
                block_path=ctx.block_path,
            )
        )
        return

    try:
        points = list(entity.get_points("xyb"))
        ocs = entity.ocs()
        elevation = float(getattr(entity.dxf, "elevation", 0.0) or 0.0)
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

    if len(points) < 2:
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

    has_bulge = any(not math.isclose(float(p[2]), 0.0, abs_tol=cfg.abs_tol, rel_tol=cfg.rel_tol) for p in points)
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
    for x, y, bulge in points:
        w = ocs.to_wcs((float(x), float(y), elevation))
        tx, ty, tz = transform_point_2d(ctx.transform, float(w.x), float(w.y), float(w.z))
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

        b = float(bulge)
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
