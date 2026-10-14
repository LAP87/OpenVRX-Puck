"""Pin numbers alone cannot establish that the pinned Core drives RESETB."""
import builtins
import importlib.util
from pathlib import Path
import shutil
import re
import json
import sys

import pytest
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
    assert len(circuit.parts) == 126    # 2026-10-13: a second ESD clamp per input after the divider
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


def test_rssi_adc_and_negative_controls():
    """The RSSI ADC on decoder A's bus with a free address, and each receiver's RSSI through the
    pull-down and the RC filter. Each fault below must be reported by rssi_checks."""
    builtins.default_circuit.reset()
    spec = importlib.util.spec_from_file_location('dekoderkort_rssi', ROOT / 'design/rev_a/dekoderkort.py')
    schema = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(schema)
    schema.build()
    circuit = builtins.default_circuit
    assert not schema.rssi_checks(circuit)
    nets = {n.name: n for n in circuit.nets}
    adc = [p for p in circuit.parts if p.name == 'ADS1115'][0]
    assert adc['ADDR'].net.name == 'GND' and schema.ADS1115_ADDR['GND'] == 0x48

    def moved(pin, to):
        old = pin.net
        pin.disconnect()
        nets[to] += pin
        problems = schema.rssi_checks(circuit)
        pin.disconnect()
        old += pin
        assert not schema.rssi_checks(circuit)
        return problems

    assert any('decoder A bus' in p for p in moved(adc['SDA'], 'I2C_SDA_B'))
    assert any('supply' in p for p in moved(adc['VDD'], '+5V'))
    assert any('AIN0' in p for p in moved(adc['AIN0'], 'RSSI_ADC_B'))
    # an address another device on the bus uses
    schema.BUS_ADDRESSES[0x48] = 'test device'
    assert any('collides' in p for p in schema.rssi_checks(circuit))
    del schema.BUS_ADDRESSES[0x48]
    # no pull-down on RSSI B, and the filter capacitor missing on RSSI A
    pull = [p.part for p in nets['RSSI_B'].pins if p.part.ref.startswith('R') and p.part.value == '100k'][0]
    assert any('RSSI_B pull-down' in p for p in moved(pull[2], 'RSSI_B'))
    cap = [p.part for p in nets['RSSI_ADC_A'].pins if p.part.ref.startswith('C')][0]
    gnd_pin = [p for p in cap.pins if p.net.name == 'GND'][0]
    assert any('RSSI_ADC_A filter' in p for p in moved(gnd_pin, 'RSSI_ADC_A'))


def test_kicad_board_matches_netlist():
    """Night-pass task 18: the board file in design/rev_a/kicad/ carries exactly the
    netlist's component references (all 126, none extra, none missing), the 66x58 mm
    outline, the four M2 holes and the three net classes of LAYOUT.md. Skipped
    without KiCad (the board is generated by design/rev_a/kicad_build.py)."""
    import re
    pcb_path = ROOT / 'design/rev_a/kicad/dekoderkort.kicad_pcb'
    try:
        import pcbnew  # noqa: F401
    except ImportError:
        try:
            sys.path.insert(0, '/usr/lib/python3/dist-packages')
            import pcbnew  # noqa: F401
        except ImportError:
            pytest.skip('KiCad pcbnew not available')
            return
    board = pcbnew.LoadBoard(str(pcb_path))
    refs = sorted(f.GetReference() for f in board.GetFootprints() if f.GetReference())
    net = (ROOT / 'design/rev_a/out/dekoderkort.net').read_text()
    comps = net[net.find('(components'):net.find('(nets')]
    netlist_refs = sorted(set(re.findall(r'\(ref "([^"]+)"\)', comps)))
    assert len(netlist_refs) == 126, f'netlist has {len(netlist_refs)} components'
    assert refs == netlist_refs, (sorted(set(netlist_refs) ^ set(refs)))[:8]
    assert board.GetCopperLayerCount() == 4, 'LAYOUT.md: four layers'
    # outline and holes from the board file, net classes and DRC minimums from the
    # project file (KiCad 9 keeps them there)
    text = pcb_path.read_text()
    assert text.count('(layer "Edge.Cuts")') >= 4, 'the rectangular outline'
    assert text.count('np_thru_hole') >= 4, 'four M2 holes'
    pro = json.loads((pcb_path.parent / 'dekoderkort.kicad_pro').read_text())
    names = [c['name'] for c in pro['net_settings']['classes']]
    assert {'27M', 'CVBS', 'POWER'} <= set(names), names
    rules = pro['board']['design_settings']['rules']
    assert rules['min_clearance'] == 0.15 and rules['min_track_width'] == 0.15
    assert rules['min_via_diameter'] == 0.6 and rules['min_via_drill'] == 0.3
    widths = {c['name']: c['track_width'] for c in pro['net_settings']['classes']}
    assert widths['POWER'] == 0.3 and widths['27M'] == widths['CVBS'] == 0.15
