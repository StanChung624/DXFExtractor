from __future__ import annotations

from dxf_extract.config import ExtractionConfig
from dxf_extract.diagnostics import make_diagnostic
from dxf_extract.model import ExtractionResult
from dxf_extract.transforms import compose
from dxf_extract.utils import entity_handle


def _is_insert_array(insert) -> bool:
    mcount = getattr(insert, "mcount", 1)
    if isinstance(mcount, int) and mcount > 1:
        return True
    row_count = int(getattr(insert.dxf, "row_count", 1) or 1)
    column_count = int(getattr(insert.dxf, "column_count", 1) or 1)
    return row_count > 1 or column_count > 1


def process_insert(insert, doc, ctx, out: ExtractionResult, cfg: ExtractionConfig, visit_entity) -> None:
    if ctx.depth >= cfg.max_insert_depth:
        out.diagnostics.append(
            make_diagnostic(
                "MAX_INSERT_DEPTH_EXCEEDED",
                handle=entity_handle(insert),
                dxftype=insert.dxftype(),
                block_path=ctx.block_path,
            )
        )
        return

    if _is_insert_array(insert):
        out.diagnostics.append(
            make_diagnostic(
                "UNSUPPORTED_INSERT_ARRAY",
                handle=entity_handle(insert),
                dxftype=insert.dxftype(),
                block_path=ctx.block_path,
            )
        )
        return

    block_name = str(insert.dxf.name)
    if block_name in ctx.active_blocks:
        out.diagnostics.append(
            make_diagnostic(
                "BLOCK_REFERENCE_CYCLE",
                handle=entity_handle(insert),
                dxftype=insert.dxftype(),
                block_path=ctx.block_path + [block_name],
            )
        )
        return

    try:
        block = doc.blocks.get(block_name)
    except Exception:
        block = None

    if block is None:
        out.diagnostics.append(
            make_diagnostic(
                "MISSING_BLOCK_DEFINITION",
                handle=entity_handle(insert),
                dxftype=insert.dxftype(),
                block_path=ctx.block_path + [block_name],
            )
        )
        return

    if bool(getattr(block, "is_xref", False)):
        out.diagnostics.append(
            make_diagnostic(
                "UNSUPPORTED_XREF",
                handle=entity_handle(insert),
                dxftype=insert.dxftype(),
                block_path=ctx.block_path + [block_name],
            )
        )
        return

    child_transform = compose(ctx.transform, insert.matrix44())
    child_ctx = ctx.child(
        transform=child_transform,
        block_name=block_name,
    )

    for child in block:
        visit_entity(child, doc, child_ctx, out, cfg)
