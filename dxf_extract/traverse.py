from __future__ import annotations

from dataclasses import dataclass

from ezdxf.math import Matrix44

from dxf_extract.config import ExtractionConfig
from dxf_extract.diagnostics import make_diagnostic
from dxf_extract.extract_circle import process_circle
from dxf_extract.extract_insert import process_insert
from dxf_extract.extract_lwpolyline import process_lwpolyline
from dxf_extract.extract_polyline import process_polyline
from dxf_extract.model import ExtractionResult
from dxf_extract.utils import entity_handle


@dataclass(slots=True)
class VisitContext:
    transform: Matrix44
    layout: str
    block_path: list[str]
    depth: int
    active_blocks: list[str]

    def child(self, *, transform: Matrix44, block_name: str) -> "VisitContext":
        return VisitContext(
            transform=transform,
            layout=self.layout,
            block_path=self.block_path + [block_name],
            depth=self.depth + 1,
            active_blocks=self.active_blocks + [block_name],
        )


_3D_TYPES = {
    "3DFACE",
    "3DSOLID",
    "BODY",
    "MESH",
    "REGION",
    "SURFACE",
}


def visit_entity(entity, doc, ctx: VisitContext, out: ExtractionResult, cfg: ExtractionConfig) -> None:
    t = entity.dxftype()
    if t == "CIRCLE":
        process_circle(entity, ctx, out, cfg)
    elif t == "LWPOLYLINE":
        process_lwpolyline(entity, ctx, out, cfg)
    elif t == "POLYLINE":
        process_polyline(entity, ctx, out, cfg)
    elif t == "INSERT":
        process_insert(entity, doc, ctx, out, cfg, visit_entity)
    elif t in _3D_TYPES:
        out.diagnostics.append(
            make_diagnostic(
                "UNSUPPORTED_3D_ENTITY",
                handle=entity_handle(entity),
                dxftype=t,
                block_path=ctx.block_path,
            )
        )
    else:
        out.diagnostics.append(
            make_diagnostic(
                "UNSUPPORTED_ENTITY_TYPE",
                handle=entity_handle(entity),
                dxftype=t,
                block_path=ctx.block_path,
            )
        )
