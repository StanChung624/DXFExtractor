from __future__ import annotations

import ezdxf

from typing import Callable

from dxf_extract.config import ExtractionConfig
from dxf_extract.model import ExtractionResult
from dxf_extract.transforms import identity_matrix
from dxf_extract.traverse import VisitContext, visit_entity


def extract_geometry(path: str,
                    config: ExtractionConfig | None = None,
                    log_callback:Callable[[str], None] | None = None) -> ExtractionResult:
    """Load a DXF file and return extracted circles, closed polylines, and diagnostics."""
    cfg = config or ExtractionConfig()
    if log_callback:
        log_callback("💿 loading DXF file...")
    doc = ezdxf.readfile(path)
    return extract_from_doc(doc, cfg, log_callback=log_callback)


def extract_from_doc(doc, config: ExtractionConfig | None = None,log_callback:Callable[[str], None] | None = None) -> ExtractionResult:
    cfg = config or ExtractionConfig()
    if log_callback:
        log_callback("📁 extracting file with config:\n"+str(cfg))
    return extract_from_modelspace(doc.modelspace(), doc, cfg, log_callback=log_callback)


def extract_from_modelspace(msp, doc, config: ExtractionConfig | None = None, log_callback:Callable[[str], None] | None = None) -> ExtractionResult:
    cfg = config or ExtractionConfig()
    out = ExtractionResult()
    root = VisitContext(
        transform=identity_matrix(),
        layout=getattr(msp, "name", "Model") or "Model",
        block_path=[],
        depth=0,
        active_blocks=[],
    )
    if log_callback:
        log_callback("⌛️ collecting entities...")
    for entity in msp:
        visit_entity(entity, doc, root, out, cfg)

    return out
