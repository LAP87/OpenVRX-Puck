"""The KiCad board for rev A (design/rev_a/kicad/, made by make_board.py) matches the netlist.

Plain text checks, so they run without pcbnew: every part of the netlist is on the board with the
same footprint, no extra parts, every net of the netlist exists on the board, and the project file
has the net classes of LAYOUT.md section 4. A negative control removes a part from a copy of the
board text and expects the check to fail.
"""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1] / 'design' / 'rev_a'
NETLIST = ROOT / 'out' / 'dekoderkort.net'
PCB = ROOT / 'kicad' / 'dekoderkort.kicad_pcb'
PRO = ROOT / 'kicad' / 'dekoderkort.kicad_pro'


def netlist_parts_and_nets():
    text = NETLIST.read_text(encoding='utf-8')
    parts = {}
    for m in re.finditer(r'\(comp\s*\(ref "([^"]+)"\)\s*\(value "[^"]*"\)(.*?)\n\s*\(fields', text, re.S):
        parts[m.group(1)] = re.search(r'\(footprint "([^"]+)"\)', m.group(2)).group(1)
    nets = set(re.findall(r'\(net\s*\(code \d+\)\s*\(name "([^"]+)"\)', text[text.index('\n  (nets'):]))
    return parts, nets


def board_parts_and_nets(text):
    parts = {}
    for m in re.finditer(r'\(footprint "([^"]+)"(.*?)\(property "Reference" "([^"]+)"', text, re.S):
        parts[m.group(3)] = m.group(1)
    nets = set(re.findall(r'\n\t\(net \d+ "([^"]+)"\)', text))
    return parts, nets


def problems(pcb_text):
    want_parts, want_nets = netlist_parts_and_nets()
    got_parts, got_nets = board_parts_and_nets(pcb_text)
    out = []
    for ref, fp in want_parts.items():
        if ref not in got_parts:
            out.append(f'{ref} missing on the board')
        elif got_parts[ref] != fp:
            out.append(f'{ref}: board footprint {got_parts[ref]}, netlist {fp}')
    out += [f'{ref} on the board but not in the netlist' for ref in got_parts if ref not in want_parts]
    out += [f'net {n} missing on the board' for n in sorted(want_nets - got_nets)]
    return out


def test_board_matches_netlist():
    assert PCB.exists(), 'run design/rev_a/kicad/make_board.py with KiCad\'s python'
    assert problems(PCB.read_text(encoding='utf-8')) == []


def test_project_has_the_net_classes():
    pro = json.loads(PRO.read_text(encoding='utf-8'))
    names = {c['name'] for c in pro['net_settings']['classes']}
    assert {'Default', '27M', 'CVBS', 'POWER5', 'POWER'} <= names
    patterns = {(p['netclass'], p['pattern']) for p in pro['net_settings']['netclass_patterns']}
    assert ('27M', 'TVPA_*') in patterns and ('CVBS', 'CVBS_*') in patterns and ('POWER5', '+5V') in patterns
    rules = pro['board']['design_settings']['rules']
    assert rules['min_track_width'] == 0.15 and rules['min_clearance'] == 0.15 and rules['min_via_diameter'] == 0.6


def test_check_is_tested():
    """Negative control: a board copy without U4 (decoder A) fails the check."""
    text = PCB.read_text(encoding='utf-8')
    start = text.index('(property "Reference" "U4"')
    fp_start = text.rindex('(footprint "', 0, start)
    broken = text[:fp_start] + text[fp_start:].replace('(property "Reference" "U4"', '(property "Reference" "U99"', 1)
    found = problems(broken)
    assert any(p.startswith('U4 missing') for p in found) and any('U99' in p for p in found), found
