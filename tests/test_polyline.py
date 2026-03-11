import ezdxf

from dxf_extract import extract_from_doc


def test_closed_2d_polyline() -> None:
    doc = ezdxf.new("R2010")
    doc.modelspace().add_polyline2d([(0, 0), (1, 0), (1, 1)], dxfattribs={"closed": True})

    out = extract_from_doc(doc)

    assert len(out.closed_polylines) == 1
    assert len(out.closed_polylines[0].vertices) == 3


def test_open_2d_polyline_skipped() -> None:
    doc = ezdxf.new("R2010")
    doc.modelspace().add_polyline2d([(0, 0), (1, 0), (1, 1)], dxfattribs={"closed": False})

    out = extract_from_doc(doc)

    assert len(out.closed_polylines) == 0
    assert any(d.code == "MALFORMED_POLYLINE" for d in out.diagnostics)


def test_3d_polyline_rejected() -> None:
    doc = ezdxf.new("R2010")
    doc.modelspace().add_polyline3d([(0, 0, 0), (1, 0, 1), (1, 1, 0)])

    out = extract_from_doc(doc)

    assert len(out.closed_polylines) == 0
    assert any(d.code == "UNSUPPORTED_POLYLINE_MODE" for d in out.diagnostics)
