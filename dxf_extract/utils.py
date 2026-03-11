from __future__ import annotations

from dxf_extract.config import ExtractionConfig
from dxf_extract.model import SourceTrace


def entity_handle(entity) -> str | None:
    return getattr(getattr(entity, "dxf", object()), "handle", None)


def source_trace(entity, *, layout: str, block_path: list[str]) -> SourceTrace:
    return SourceTrace(
        handle=entity_handle(entity),
        dxftype=entity.dxftype(),
        layout=layout,
        block_path=list(block_path),
    )


def is_close(a: float, b: float, cfg: ExtractionConfig) -> bool:
    return abs(a - b) <= max(cfg.abs_tol, cfg.rel_tol * max(abs(a), abs(b)))


def sanitize(value: float, cfg: ExtractionConfig) -> float:
    if abs(value) <= cfg.abs_tol:
        return 0.0
    if value == -0.0:
        return 0.0
    return float(value)
