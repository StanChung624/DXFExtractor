import ezdxf

from dxf_extract import extract_from_doc


def test_single_insert() -> None:
    doc = ezdxf.new("R2010")
    block = doc.blocks.new("B")
    block.add_circle((0, 0), 1)
    doc.modelspace().add_blockref("B", (10, 0))

    out = extract_from_doc(doc)

    assert len(out.circles) == 1
    assert out.circles[0].center == (10.0, 0.0)


def test_nested_insert() -> None:
    doc = ezdxf.new("R2010")
    a = doc.blocks.new("A")
    a.add_circle((1, 0), 1)

    b = doc.blocks.new("B")
    b.add_blockref("A", (5, 0))

    doc.modelspace().add_blockref("B", (10, 0))

    out = extract_from_doc(doc)

    assert len(out.circles) == 1
    assert out.circles[0].center == (16.0, 0.0)
    assert out.circles[0].source is not None
    assert out.circles[0].source.block_path == ["B", "A"]


def test_missing_block_definition() -> None:
    doc = ezdxf.new("R2010")
    doc.modelspace().add_blockref("DOES_NOT_EXIST", (0, 0))

    out = extract_from_doc(doc)

    assert any(d.code == "MISSING_BLOCK_DEFINITION" for d in out.diagnostics)


def test_insert_array_rejected() -> None:
    doc = ezdxf.new("R2010")
    block = doc.blocks.new("ARR")
    block.add_circle((0, 0), 1)

    doc.modelspace().add_blockref(
        "ARR",
        (0, 0),
        dxfattribs={"row_count": 2, "column_count": 1, "row_spacing": 5.0},
    )

    out = extract_from_doc(doc)

    assert len(out.circles) == 0
    assert any(d.code == "UNSUPPORTED_INSERT_ARRAY" for d in out.diagnostics)
