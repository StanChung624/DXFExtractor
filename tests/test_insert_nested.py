import ezdxf

from dxf_extract import ExtractionConfig, extract_from_doc


def test_recursion_depth_exceeded() -> None:
    doc = ezdxf.new("R2010")
    c = doc.blocks.new("C")
    c.add_circle((0, 0), 1)

    b = doc.blocks.new("B")
    b.add_blockref("C", (0, 0))

    a = doc.blocks.new("A")
    a.add_blockref("B", (0, 0))

    doc.modelspace().add_blockref("A", (0, 0))

    out = extract_from_doc(doc, ExtractionConfig(max_insert_depth=2))

    assert len(out.circles) == 0
    assert any(d.code == "MAX_INSERT_DEPTH_EXCEEDED" for d in out.diagnostics)


def test_block_reference_cycle_protection() -> None:
    doc = ezdxf.new("R2010")

    a = doc.blocks.new("A")
    b = doc.blocks.new("B")
    a.add_blockref("B", (0, 0))
    b.add_blockref("A", (0, 0))

    doc.modelspace().add_blockref("A", (0, 0))

    out = extract_from_doc(doc)

    assert any(d.code == "BLOCK_REFERENCE_CYCLE" for d in out.diagnostics)
