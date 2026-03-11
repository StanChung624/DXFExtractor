import ezdxf

from dxf_extract import extract_from_doc


def test_unsupported_entity_type() -> None:
    doc = ezdxf.new("R2010")
    doc.modelspace().add_arc((0, 0), radius=1, start_angle=0, end_angle=90)

    out = extract_from_doc(doc)

    assert any(d.code == "UNSUPPORTED_ENTITY_TYPE" for d in out.diagnostics)


def test_malformed_entity_does_not_stop_extraction() -> None:
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (1, 0), (1, 1)], dxfattribs={"closed": False})
    msp.add_circle((2, 2), 1)

    out = extract_from_doc(doc)

    assert any(d.code == "MALFORMED_POLYLINE" for d in out.diagnostics)
    assert len(out.circles) == 1
