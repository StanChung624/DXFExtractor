from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from ezdxf.math import Matrix44, Vec3

from dxf_extract.config import ExtractionConfig

TransformClass = Literal[
    "rigid",
    "uniform_scale",
    "reflection_uniform_scale",
    "nonuniform_scale",
    "unsupported",
]


@dataclass(slots=True)
class XYTransformAnalysis:
    kind: TransformClass
    scale_x: float
    scale_y: float
    determinant: float
    preserves_xy_plane: bool


def identity_matrix() -> Matrix44:
    return Matrix44()


def compose(parent: Matrix44, child: Matrix44) -> Matrix44:
    return parent @ child


def transform_point_2d(matrix: Matrix44, x: float, y: float, z: float = 0.0) -> tuple[float, float, float]:
    p = matrix.transform(Vec3(x, y, z))
    return (float(p.x), float(p.y), float(p.z))


def _len2(x: float, y: float) -> float:
    return math.sqrt(x * x + y * y)


def _is_close(a: float, b: float, cfg: ExtractionConfig) -> bool:
    return math.isclose(a, b, abs_tol=cfg.abs_tol, rel_tol=cfg.rel_tol)


def classify_xy_transform(matrix: Matrix44, cfg: ExtractionConfig) -> XYTransformAnalysis:
    o = matrix.transform(Vec3(0.0, 0.0, 0.0))
    ex = matrix.transform(Vec3(1.0, 0.0, 0.0))
    ey = matrix.transform(Vec3(0.0, 1.0, 0.0))
    ez = matrix.transform(Vec3(0.0, 0.0, 1.0))

    vx = (ex.x - o.x, ex.y - o.y, ex.z - o.z)
    vy = (ey.x - o.x, ey.y - o.y, ey.z - o.z)
    vz = (ez.x - o.x, ez.y - o.y, ez.z - o.z)

    preserves_xy = (
        _is_close(o.z, 0.0, cfg)
        and _is_close(vx[2], 0.0, cfg)
        and _is_close(vy[2], 0.0, cfg)
        and _is_close(vz[0], 0.0, cfg)
        and _is_close(vz[1], 0.0, cfg)
    )
    if not preserves_xy:
        return XYTransformAnalysis(
            kind="unsupported",
            scale_x=0.0,
            scale_y=0.0,
            determinant=0.0,
            preserves_xy_plane=False,
        )

    sx = _len2(vx[0], vx[1])
    sy = _len2(vy[0], vy[1])
    dot = vx[0] * vy[0] + vx[1] * vy[1]
    det = vx[0] * vy[1] - vx[1] * vy[0]

    if _is_close(sx, 0.0, cfg) or _is_close(sy, 0.0, cfg):
        kind: TransformClass = "unsupported"
    elif _is_close(dot, 0.0, cfg):
        if _is_close(sx, sy, cfg):
            if _is_close(sx, 1.0, cfg):
                kind = "rigid" if det >= 0.0 else "reflection_uniform_scale"
            else:
                kind = "uniform_scale" if det >= 0.0 else "reflection_uniform_scale"
        else:
            kind = "nonuniform_scale"
    else:
        kind = "unsupported"

    return XYTransformAnalysis(
        kind=kind,
        scale_x=sx,
        scale_y=sy,
        determinant=det,
        preserves_xy_plane=True,
    )


def normalize_zero(v: float, cfg: ExtractionConfig) -> float:
    if abs(v) <= cfg.abs_tol:
        return 0.0
    return v


def transform_preserves_xy(matrix: Matrix44, cfg: ExtractionConfig) -> bool:
    return classify_xy_transform(matrix, cfg).preserves_xy_plane
