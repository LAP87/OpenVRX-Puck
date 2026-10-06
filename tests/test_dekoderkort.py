"""Pin numbers alone cannot establish that the pinned Core drives RESETB."""
import builtins
import importlib.util
from pathlib import Path
import shutil
import re
import skidl  # Creates default_circuit before the fixture resets it.

ROOT = Path(__file__).resolve().parents[1]
GW = ROOT / 'core/gateware'


def test_schema_gateware_contract_and_negative_controls(tmp_path):
    # The module creates power/I2C nets at import. Reset before importing it,
    # so the fixture retains those nets in the circuit being checked.
    builtins.default_circuit.reset()
    spec = importlib.util.spec_from_file_location('dekoderkort', ROOT / 'design/rev_a/dekoderkort.py')
    schema = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(schema)
    schema.build()
    circuit = builtins.default_circuit
    assert not schema.design_checks(circuit)
    assert len(circuit.parts) == 112
    isolated = tmp_path / 'gateware'
    for directory in ('boards', 'top', 'tools'):
        (isolated / directory).mkdir(parents=True)
    for rel in ('boards/tangnano20k.cst', 'boards/m3_probe.cst', 'boards/m4_dual_mix.cst', 'boards/m6_puck_proto.cst',
                'tools/board_contract.py', 'top/m3_probe.v', 'top/m4_dual_mix.v', 'top/m6_puck_proto.v'):
        shutil.copy2(GW / rel, isolated / rel)
    assert not schema.check_against_gateware(circuit, isolated)
    top = isolated / 'top/m4_dual_mix.v'
    good = top.read_text()
    assert '.tvp_resetb(tvp_resetb)' in good
    top.write_text(good.replace('.tvp_resetb(tvp_resetb)', '.tvp_resetb()'))     # reset left unconnected
    assert any('tvp_resetb' in p for p in schema.check_against_gateware(circuit, isolated))
    top.write_text(good)
    cst = isolated / 'boards/m4_dual_mix.cst'
    before = cst.read_text()
    after = re.sub(r'("tvpa_sclk"\s+)77;', r'\g<1>80;', before)
    assert after != before
    cst.write_text(after)
    assert any('TVPA_SCLK' in p for p in schema.check_against_gateware(circuit, isolated))
    (isolated / 'tools/board_contract.py').unlink()
    assert any('lacks' in p for p in schema.check_against_gateware(circuit, isolated))
