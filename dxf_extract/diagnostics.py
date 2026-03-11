from __future__ import annotations

from dxf_extract.model import Diagnostic

_MESSAGES: dict[str, str] = {
    "UNSUPPORTED_ENTITY_TYPE": "Entity type is not supported in extraction v1.",
    "UNSUPPORTED_POLYLINE_MODE": "Only closed 2D classic POLYLINE entities are supported.",
    "ENTITY_NOT_IN_XY_PLANE": "Entity is not representable in the XY plane.",
    "UNSUPPORTED_NONUNIFORM_SCALED_CIRCLE": "Circle transformed by non-uniform/sheared transform is unsupported.",
    "UNSUPPORTED_TRANSFORMED_BULGE_POLYLINE": "Bulged polyline transformed by unsupported transform.",
    "MISSING_BLOCK_DEFINITION": "Referenced block definition was not found.",
    "MAX_INSERT_DEPTH_EXCEEDED": "Maximum insert recursion depth exceeded.",
    "BLOCK_REFERENCE_CYCLE": "Detected recursive block reference cycle.",
    "INVALID_CIRCLE_RADIUS": "Circle radius must be positive.",
    "MALFORMED_POLYLINE": "Polyline data is malformed and could not be extracted.",
    "UNSUPPORTED_INSERT_ARRAY": "INSERT arrays are unsupported in extraction v1.",
    "UNSUPPORTED_XREF": "XREF block references are unsupported in extraction v1.",
    "UNSUPPORTED_3D_ENTITY": "3D entities are unsupported in extraction v1.",
}


def make_diagnostic(
    code: str,
    *,
    severity: str = "warning",
    message: str | None = None,
    handle: str | None = None,
    dxftype: str | None = None,
    block_path: list[str] | None = None,
) -> Diagnostic:
    return Diagnostic(
        severity=severity,  # type: ignore[arg-type]
        code=code,
        message=message or _MESSAGES.get(code, code),
        handle=handle,
        dxftype=dxftype,
        block_path=list(block_path or []),
    )


def diagnostic_message(code: str) -> str:
    return _MESSAGES.get(code, code)
