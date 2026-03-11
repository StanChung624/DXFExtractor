import math

import ezdxf

from dxf_extract import ExtractionConfig, extract_from_doc


def test_direct_circle_modelspace() -> None:
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    msp.add_circle((1.0, 2.0), 3.0)

    out = extract_from_doc(doc)

    assert len(out.circles) == 1
    c = out.circles[0]
    assert c.center == (1.0, 2.0)
    assert c.radius == 3.0
    assert c.source is not None
    assert c.source.dxftype == "CIRCLE"
    assert c.source.block_path == []


def test_circle_through_insert_uniform_scale() -> None:
    doc = ezdxf.new("R2010")
    block = doc.blocks.new("B_CIRCLE")
    block.add_circle((1.0, 0.0), 2.0)
    doc.modelspace().add_blockref(
        "B_CIRCLE",
        (10.0, 5.0),
        dxfattribs={"xscale": 2.0, "yscale": 2.0, "rotation": 90.0},
    )

    out = extract_from_doc(doc)

    assert len(out.circles) == 1
    c = out.circles[0]
    assert math.isclose(c.radius, 4.0)
    assert c.source is not None
    assert c.source.block_path == ["B_CIRCLE"]


def test_nested_insert_non_uniform_circle_rejected() -> None:
    doc = ezdxf.new("R2010")
    inner = doc.blocks.new("INNER")
    inner.add_circle((0.0, 0.0), 1.0)

    outer = doc.blocks.new("OUTER")
    outer.add_blockref("INNER", (0.0, 0.0), dxfattribs={"xscale": 1.0, "yscale": 1.0})

    doc.modelspace().add_blockref("OUTER", (0.0, 0.0), dxfattribs={"xscale": 2.0, "yscale": 1.0})

    out = extract_from_doc(doc)

    assert len(out.circles) == 0
    assert any(d.code == "UNSUPPORTED_NONUNIFORM_SCALED_CIRCLE" for d in out.diagnostics)


def test_nested_insert_depth_rotation() -> None:
    doc = ezdxf.new("R2010")
    b1 = doc.blocks.new("B1")
    b1.add_circle((1.0, 0.0), 1.0)

    b2 = doc.blocks.new("B2")
    b2.add_blockref("B1", (0.0, 0.0), dxfattribs={"rotation": 90.0})

    doc.modelspace().add_blockref("B2", (0.0, 0.0), dxfattribs={"rotation": 90.0})

    out = extract_from_doc(doc)

    assert len(out.circles) == 1
    c = out.circles[0]
    assert c.source is not None
    assert c.source.block_path == ["B2", "B1"]


def test_invalid_circle_radius() -> None:
    doc = ezdxf.new("R2010")
    doc.modelspace().add_circle((0.0, 0.0), 0.0)

    out = extract_from_doc(doc)

    assert len(out.circles) == 0
    assert any(d.code == "INVALID_CIRCLE_RADIUS" for d in out.diagnostics)


def test_circle_out_of_xy_plane_rejected() -> None:
    doc = ezdxf.new("R2010")
    doc.modelspace().add_circle((0.0, 0.0, 1.0), 1.0)

    out = extract_from_doc(doc, ExtractionConfig(abs_tol=1e-12, rel_tol=1e-12))

    assert len(out.circles) == 0
    assert any(d.code == "ENTITY_NOT_IN_XY_PLANE" for d in out.diagnostics)
