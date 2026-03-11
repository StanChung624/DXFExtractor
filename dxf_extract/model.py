from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional

Vec2 = tuple[float, float]


@dataclass(slots=True)
class SourceTrace:
    handle: Optional[str]
    dxftype: str
    layout: str
    block_path: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CircleGeometry:
    kind: Literal["circle"] = "circle"
    center: Vec2 = (0.0, 0.0)
    radius: float = 0.0
    source: Optional[SourceTrace] = None


@dataclass(slots=True)
class PolylineVertex:
    x: float
    y: float
    bulge: float = 0.0


@dataclass(slots=True)
class ClosedPolylineGeometry:
    kind: Literal["closed_polyline"] = "closed_polyline"
    vertices: list[PolylineVertex] = field(default_factory=list)
    source: Optional[SourceTrace] = None


@dataclass(slots=True)
class Diagnostic:
    severity: Literal["info", "warning", "error"] = "warning"
    code: str = ""
    message: str = ""
    handle: Optional[str] = None
    dxftype: Optional[str] = None
    block_path: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ExtractionResult:
    circles: list[CircleGeometry] = field(default_factory=list)
    closed_polylines: list[ClosedPolylineGeometry] = field(default_factory=list)
    diagnostics: list[Diagnostic] = field(default_factory=list)
