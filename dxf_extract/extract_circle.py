from __future__ import annotations

import math

from dxf_extract.config import ExtractionConfig
from dxf_extract.diagnostics import make_diagnostic
from dxf_extract.model import CircleGeometry, ExtractionResult
from dxf_extract.transforms import classify_xy_transform, normalize_zero, transform_point_2d
from dxf_extract.utils import entity_handle, source_trace


def process_circle(entity, ctx, out: ExtractionResult, cfg: ExtractionConfig) -> None:
    radius = float(entity.dxf.radius)
    if radius <= 0.0 or math.isnan(radius):
        out.diagnostics.append(
            make_diagnostic(
                "INVALID_CIRCLE_RADIUS",
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

    if analysis.kind not in {"rigid", "uniform_scale", "reflection_uniform_scale"}:
        out.diagnostics.append(
            make_diagnostic(
                "UNSUPPORTED_NONUNIFORM_SCALED_CIRCLE",
                handle=entity_handle(entity),
                dxftype=entity.dxftype(),
                block_path=ctx.block_path,
            )
        )
        return

    cx, cy, cz = transform_point_2d(ctx.transform, float(entity.dxf.center.x), float(entity.dxf.center.y), float(entity.dxf.center.z))
    if not math.isclose(cz, 0.0, abs_tol=cfg.abs_tol, rel_tol=cfg.rel_tol):
        out.diagnostics.append(
            make_diagnostic(
                "ENTITY_NOT_IN_XY_PLANE",
                handle=entity_handle(entity),
                dxftype=entity.dxftype(),
                block_path=ctx.block_path,
            )
        )
        return

    out.circles.append(
        CircleGeometry(
            center=(normalize_zero(cx, cfg), normalize_zero(cy, cfg)),
            radius=normalize_zero(radius * analysis.scale_x, cfg),
            source=source_trace(entity, layout=ctx.layout, block_path=ctx.block_path),
        )
    )
