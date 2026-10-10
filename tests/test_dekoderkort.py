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
    assert len(circuit.parts) == 114
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


def test_all_supported_tops_check_decoder_and_board_pin_maps(tmp_path):
    builtins.default_circuit.reset()
    spec = importlib.util.spec_from_file_location('dekoderkort_all_tops', ROOT / 'design/rev_a/dekoderkort.py')
    schema = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(schema)
    schema.build()
    circuit = builtins.default_circuit

    isolated = tmp_path / 'gateware'
    for directory in ('boards', 'top', 'tools'):
        (isolated / directory).mkdir(parents=True)
    for rel in ('boards/tangnano20k.cst', 'boards/m3_probe.cst', 'boards/m4_dual_mix.cst', 'boards/m6_puck_proto.cst',
                'tools/board_contract.py', 'top/m3_probe.v', 'top/m4_dual_mix.v', 'top/m6_puck_proto.v'):
        shutil.copy2(GW / rel, isolated / rel)
    assert not schema.check_against_gateware(circuit, isolated)

    # D0/D1 swaps on M3 and M6 used to escape a guard built from M4 constraints alone.
    for top in ('m3_probe', 'm6_puck_proto'):
        path = isolated / 'boards' / f'{top}.cst'
        original = path.read_text()
        swapped = original.replace('IO_LOC  "tvpa_d[0]" 27;', 'IO_LOC  "tvpa_d[0]" 28;')
        swapped = swapped.replace('IO_LOC  "tvpa_d[1]" 28;', 'IO_LOC  "tvpa_d[1]" 27;')
        assert swapped != original
        path.write_text(swapped)
        problems = schema.check_against_gateware(circuit, isolated)
        assert any(top in p and 'tvpa_d[0]' in p for p in problems), problems
        path.write_text(original)

    # Move decoder clocks and each I2C line, one fault at a time in every supported top.
    moves = (('tvpa_sclk', 77, 14), ('tvpb_sclk', 80, 13), ('i2c_scl', 75, 12),
             ('i2c_sda_a', 85, 11), ('i2c_sda_b', 51, 10))
    for top in schema.SUPPORTED_TOPS:
        path = isolated / 'boards' / f'{top}.cst'
        original = path.read_text()
        for port, pin, moved_pin in moves:
            old = f'IO_LOC  "{port}" {pin};'
            new = f'IO_LOC  "{port}" {moved_pin};'
            assert original.count(old) == 1, (top, old)
            path.write_text(original.replace(old, new))
            problems = schema.check_against_gateware(circuit, isolated)
            assert any(top in p and port in p for p in problems), (top, port, problems)
            path.write_text(original)

    # A missing mapping or repeated IO_LOC must be reported, not hidden by a dictionary overwrite.
    path = isolated / 'boards' / 'm4_dual_mix.cst'
    original = path.read_text()
    without_sda = original.replace('IO_LOC  "i2c_sda_a" 85;\n', '')
    assert without_sda != original
    path.write_text(without_sda)
    problems = schema.check_against_gateware(circuit, isolated)
    assert any('m4_dual_mix' in p and 'i2c_sda_a' in p and 'missing' in p for p in problems), problems
    duplicate = original + '\nIO_LOC  "tvpb_d[0]" 76;\n'
    path.write_text(duplicate)
    problems = schema.check_against_gateware(circuit, isolated)
    assert any('m4_dual_mix' in p and 'tvpb_d[0]' in p and 'duplicate' in p for p in problems), problems
    path.write_text(original)
