import ezdxf

from dxf_extract import extract_from_doc


def test_direct_closed_lwpolyline_without_bulges() -> None:
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (10, 0), (10, 5)], dxfattribs={"closed": True})

    out = extract_from_doc(doc)

    assert len(out.closed_polylines) == 1
    poly = out.closed_polylines[0]
    assert len(poly.vertices) == 3
    assert all(v.bulge == 0.0 for v in poly.vertices)


def test_direct_open_lwpolyline_skipped() -> None:
    doc = ezdxf.new("R2010")
    doc.modelspace().add_lwpolyline([(0, 0), (1, 0), (1, 1)], dxfattribs={"closed": False})

    out = extract_from_doc(doc)

    assert len(out.closed_polylines) == 0
    assert any(d.code == "MALFORMED_POLYLINE" for d in out.diagnostics)


def test_closed_bulged_lwpolyline() -> None:
    doc = ezdxf.new("R2010")
    doc.modelspace().add_lwpolyline(
        [(0, 0, 1.0), (1, 0, 0.0), (1, 1, 0.0)],
        format="xyb",
        dxfattribs={"closed": True},
    )

    out = extract_from_doc(doc)

    assert len(out.closed_polylines) == 1
    assert out.closed_polylines[0].vertices[0].bulge == 1.0


def test_bulged_lwpolyline_through_uniform_insert() -> None:
    doc = ezdxf.new("R2010")
    block = doc.blocks.new("B_LW")
    block.add_lwpolyline(
        [(0, 0, 0.5), (2, 0, 0.0), (2, 2, 0.0)],
        format="xyb",
        dxfattribs={"closed": True},
    )
    doc.modelspace().add_blockref("B_LW", (10, 10), dxfattribs={"xscale": 2.0, "yscale": 2.0})

    out = extract_from_doc(doc)

    assert len(out.closed_polylines) == 1
    assert out.closed_polylines[0].source is not None
    assert out.closed_polylines[0].source.block_path == ["B_LW"]


def test_bulged_lwpolyline_through_nonuniform_insert_rejected() -> None:
    doc = ezdxf.new("R2010")
    block = doc.blocks.new("B_LW")
    block.add_lwpolyline(
        [(0, 0, 0.5), (2, 0, 0.0), (2, 2, 0.0)],
        format="xyb",
        dxfattribs={"closed": True},
    )
    doc.modelspace().add_blockref("B_LW", (0, 0), dxfattribs={"xscale": 2.0, "yscale": 1.0})

    out = extract_from_doc(doc)

    assert len(out.closed_polylines) == 0
    assert any(d.code == "UNSUPPORTED_TRANSFORMED_BULGE_POLYLINE" for d in out.diagnostics)
