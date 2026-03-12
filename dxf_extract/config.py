from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExtractionConfig:
    abs_tol: float = 1e-9
    rel_tol: float = 1e-9
    max_insert_depth: int = 16
    allow_reflection_for_lines_only: bool = True

    def __str__(self) -> str:
        return f"\tExtractionConfig(abs_tol={self.abs_tol},\n\trel_tol={self.rel_tol},\n\tmax_insert_depth={self.max_insert_depth},\n\tallow_reflection_for_lines_only={self.allow_reflection_for_lines_only})"
