from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExtractionConfig:
    abs_tol: float = 1e-9
    rel_tol: float = 1e-9
    max_insert_depth: int = 16
    allow_reflection_for_lines_only: bool = True
