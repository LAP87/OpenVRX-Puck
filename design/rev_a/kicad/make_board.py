#!/usr/bin/env python3
"""Make the KiCad 9 project for rev A from the SKiDL netlist (hub night pass 2026-10-13, task 18).

Run with KiCad's own python (the pcbnew module), not the project venv:

    python3 design/rev_a/kicad/make_board.py            # -> design/rev_a/kicad/dekoderkort.kicad_{pcb,pro}

What it does, and nothing more:
  * reads design/rev_a/out/dekoderkort.net (every part with its footprint, every net with its pins);
  * a 66 x 58 mm outline, the four M2 holes 3.5 mm from the corners, and the two 1x20 headers J2/J3
    where the Tang Nano 20K's J6/J5 land when the Tang sits centred (row spacing 20.32 mm, see
    LAYOUT.md section 1: not checked against Sipeed's drawing; pin 1 end assumed at the top);
  * every other part outside the outline, in rows by block in the order of LAYOUT.md section 3,
    with the block name beside the row (Cmts.User);
  * all nets, every pad assigned, no tracks;
  * 4 copper layers, the manufacturing minimums of LAYOUT.md section 4 (0.15/0.15 mm, via 0.6/0.3)
    and the net classes 27M, CVBS, POWER5, POWER as pattern assignments in the project file.
The placement inside the outline and all routing is a human's job in Pcbnew; LAYOUT.md says how.
tests/test_kicad_project.py checks the board file against the netlist without needing pcbnew.
"""
import json
import re
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
NETLIST = HERE.parent / 'out' / 'dekoderkort.net'
PCB = HERE / 'dekoderkort.kicad_pcb'
PRO = HERE / 'dekoderkort.kicad_pro'
FP_DIRS = [Path('/usr/share/kicad/footprints'), Path('C:/Program Files/KiCad/9.0/share/kicad/footprints')]

BOARD_W, BOARD_H = 66.0, 58.0            # LAYOUT.md section 1
HOLE_IN = 3.5                             # section 7
TANG_W, TANG_H = 22.55, 54.04             # Sipeed, via LAYOUT.md
ROW_PITCH = 20.32                         # between J2 and J3, not checked against Sipeed's drawing
PIN_PITCH = 2.54

# LAYOUT.md section 3, in its order. Parts not listed here land in "Övrigt" and are reported.
BLOCKS = [
    ('Ingång A: kontakt, första ESD, delare, andra ESD, AAF, koppling', 'J4 D1 TP1 R4 R5 D2 L1 C18 C19 C20'),
    ('Mottagare A: PTC, 5 V, RSSI-pull-down', 'F1 C17 R36'),
    ('Dekoder A: TVP, kristall, referenser, matning, seriemotstånd, styrstift, testpunkter',
     'U4 Y1 C21 C22 R6 C14 C15 C16 FB1 C8 C9 FB2 C10 C11 C12 C13 R9 R10 R11 R12 R13 R14 R15 R16 R19 R7 R8 R17 R18 '
     'TP2 TP3 TP4 TP5 TP6 TP7'),
    ('Ingång B', 'J5 D3 TP8 R20 R21 D4 L2 C33 C34 C35'),
    ('Mottagare B', 'F2 C32 R38'),
    ('Dekoder B', 'U5 Y2 C36 C37 R22 C29 C30 C31 FB3 C23 C24 FB4 C25 C26 C27 C28 R25 R26 R27 R28 R29 R30 R31 R32 R35 '
     'R23 R24 R33 R34 TP9 TP10 TP11 TP12 TP13 TP14'),
    ('Matning: 3,3 V, 1,8 V digital, 1,8 V analog, 5 V in', 'U1 C2 C3 U2 C4 C5 U3 C6 C7 J1 C1 JP2'),
    ('Under Tang-kortet: I2C-pull-ups, JP1', 'R1 R2 R3 JP1'),
    ('RSSI: ADC, RC-filter, testpunkter', 'U6 R37 C38 R39 C39 C40 TP15 TP16'),
]

# LAYOUT.md section 4; widths in mm. Clearance for 27M is two widths, for CVBS 8-10 widths.
NET_CLASSES = [
    dict(name='Default', clearance=0.15, track_width=0.15, via_diameter=0.6, via_drill=0.3),
    dict(name='27M', clearance=0.7, track_width=0.35, via_diameter=0.6, via_drill=0.3),
    dict(name='CVBS', clearance=1.2, track_width=0.15, via_diameter=0.6, via_drill=0.3),
    dict(name='POWER5', clearance=0.2, track_width=0.8, via_diameter=0.8, via_drill=0.4),
    dict(name='POWER', clearance=0.2, track_width=0.5, via_diameter=0.6, via_drill=0.3),
]
NET_PATTERNS = [
    ('27M', 'TVPA_*'), ('27M', 'TVPB_*'), ('27M', 'A_YOUT*'), ('27M', 'A_SCLK_U'), ('27M', 'B_YOUT*'), ('27M', 'B_SCLK_U'),
    ('CVBS', 'CVBS_*'), ('CVBS', 'AIP1A_*'),
    ('POWER5', '+5V'), ('POWER5', '+5V_TANG'), ('POWER5', '+5V_RX_*'),
    ('POWER', '+3V3'), ('POWER', '+1V8*'), ('POWER', 'AVDD_*'), ('POWER', 'PLL_AVDD_*'),
]


def mm(x):
    return pcbnew.FromMM(x)


def v(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def parse_netlist(path):
    """Parts {ref: (value, lib, name)} and nets {name: [(ref, pin)]} from the KiCad netlist (S-expression)."""
    text = path.read_text(encoding='utf-8')
    parts = {}
    for m in re.finditer(r'\(comp\s*\(ref "([^"]+)"\)\s*\(value "([^"]*)"\)(.*?)\n\s*\(fields', text, re.S):
        ref, value, rest = m.group(1), m.group(2), m.group(3)
        fp = re.search(r'\(footprint "([^"]+)"\)', rest)
        if not fp:
            raise SystemExit(f'{ref}: no footprint in the netlist')
        lib, name = fp.group(1).split(':', 1)
        parts[ref] = (value, lib, name)
    nets = {}
    nets_text = text[text.index('\n  (nets'):]
    for m in re.finditer(r'\(net\s*\(code \d+\)\s*\(name "([^"]+)"\)(.*?)(?=\n\s*\(net\s*\(code|\Z)', nets_text, re.S):
        nodes = re.findall(r'\(node\s*\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', m.group(2))
        nets[m.group(1)] = nodes
    return parts, nets


def load_footprint(lib, name):
    for d in FP_DIRS:
        p = d / f'{lib}.pretty'
        if p.is_dir():
            fp = pcbnew.FootprintLoad(str(p), name)
            if fp is not None:
                return fp
    raise SystemExit(f'footprint {lib}:{name} not found under {FP_DIRS}')


def outline(board):
    pts = [(0, 0), (BOARD_W, 0), (BOARD_W, BOARD_H), (0, BOARD_H)]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(v(x0, y0))
        s.SetEnd(v(x1, y1))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(mm(0.1))
        board.Add(s)
    # the Tang Nano 20K's outline, centred, on a comment layer: what sits under it (LAYOUT.md section 1)
    cx, cy = BOARD_W / 2, BOARD_H / 2
    tp = [(cx - TANG_W / 2, cy - TANG_H / 2), (cx + TANG_W / 2, cy - TANG_H / 2),
          (cx + TANG_W / 2, cy + TANG_H / 2), (cx - TANG_W / 2, cy + TANG_H / 2)]
    for (x0, y0), (x1, y1) in zip(tp, tp[1:] + tp[:1]):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(v(x0, y0))
        s.SetEnd(v(x1, y1))
        s.SetLayer(pcbnew.Cmts_User)
        s.SetWidth(mm(0.1))
        board.Add(s)
    label(board, 'Tang Nano 20K ovanpå (kontur, LAYOUT.md 1; stift 1-änden antagen)', cx, cy, 1.0)


def label(board, text, x, y, size=1.5):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(text)
    t.SetPosition(v(x, y))
    t.SetLayer(pcbnew.Cmts_User)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    board.Add(t)


def extent(fp):
    """The footprint's front courtyard box (falls back to the body box), in board units."""
    try:
        poly = fp.GetCourtyard(pcbnew.F_CrtYd)
        if poly.OutlineCount() > 0:
            return poly.BBox()
    except Exception:
        pass
    return fp.GetBoundingBox(False, False)


def fixed_positions():
    """Holes and headers: real positions. Header pin 1 at the top end (to be read on the board)."""
    cx, cy = BOARD_W / 2, BOARD_H / 2
    y1 = cy - 19 * PIN_PITCH / 2
    pos = {
        'H1': (HOLE_IN, HOLE_IN), 'H2': (BOARD_W - HOLE_IN, HOLE_IN),
        'H3': (HOLE_IN, BOARD_H - HOLE_IN), 'H4': (BOARD_W - HOLE_IN, BOARD_H - HOLE_IN),
        'J2': (cx - ROW_PITCH / 2, y1),            # under the Tang's J6 (decoder A side)
        'J3': (cx + ROW_PITCH / 2, y1),            # under the Tang's J5 (decoder B side)
    }
    return pos


def main():
    parts, nets = parse_netlist(NETLIST)
    board = pcbnew.BOARD()
    board.SetFileName(str(PCB))
    ds = board.GetDesignSettings()
    ds.SetCopperLayerCount(4)
    ds.m_MinClearance = mm(0.15)
    ds.m_TrackMinWidth = mm(0.15)
    ds.m_ViasMinSize = mm(0.6)
    ds.m_MinThroughDrill = mm(0.3)
    outline(board)

    netinfo = {}
    for name in nets:
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netinfo[name] = ni
    pad_net = {(ref, pin): name for name, nodes in nets.items() for ref, pin in nodes}

    fixed = fixed_positions()
    placed = {}
    footprints = {}
    for ref, (value, lib, name) in sorted(parts.items()):
        fp = load_footprint(lib, name)
        fp.SetFPID(pcbnew.LIB_ID(lib, name))     # keep the library nickname in the board file
        fp.SetReference(ref)
        fp.SetValue(value)
        footprints[ref] = fp
        board.Add(fp)
        for pad in fp.Pads():
            key = (ref, pad.GetNumber())
            if key in pad_net:
                pad.SetNet(netinfo[pad_net[key]])
        if ref in fixed:
            fp.SetPosition(v(*fixed[ref]))
            placed[ref] = 'fast'

    # rows outside the outline, one per block, in LAYOUT.md order; the rest in a last row
    listed = set()
    rows = [(title, refs.split()) for title, refs in BLOCKS]
    for _, refs in rows:
        listed.update(refs)
    rest = sorted(r for r in parts if r not in listed and r not in fixed)
    if rest:
        rows.append(('Övrigt (inte i LAYOUT.md avsnitt 3)', rest))
        print('not in a block:', ' '.join(rest))
    y = 4.0
    for title, refs in rows:
        x = BOARD_W + 10.0
        label(board, title, x, y - 3.0, 1.2)
        row_h = 0.0
        for ref in refs:
            if ref not in footprints:
                print(f'LAYOUT.md names {ref}, which is not in the netlist')
                continue
            fp = footprints[ref]
            fp.SetPosition(v(x, y))
            bb = extent(fp)                       # courtyard, so that DRC sees no overlap in the rows
            fp.Move(pcbnew.VECTOR2I(mm(x) - bb.GetLeft(), mm(y) - bb.GetTop()))
            w, h = pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight())
            x += w + 2.0
            row_h = max(row_h, h)
            placed[ref] = title
        y += row_h + 6.0

    pcbnew.SaveBoard(str(PCB), board)
    PRO.write_text(json.dumps({
        'meta': {'filename': PRO.name, 'version': 1},
        'board': {'design_settings': {'rules': {
            'min_clearance': 0.15, 'min_track_width': 0.15, 'min_via_diameter': 0.6,
            'min_through_hole_diameter': 0.3, 'min_copper_edge_clearance': 0.3, 'min_hole_clearance': 0.25}}},
        'net_settings': {
            'classes': [dict(c, bus_width=12, diff_pair_gap=0.25, diff_pair_via_gap=0.25, diff_pair_width=0.2,
                             line_style=0, microvia_diameter=0.3, microvia_drill=0.1, pcb_color='rgba(0, 0, 0, 0.000)',
                             schematic_color='rgba(0, 0, 0, 0.000)', wire_width=6) for c in NET_CLASSES],
            'meta': {'version': 4},
            'netclass_patterns': [{'netclass': nc, 'pattern': pat} for nc, pat in NET_PATTERNS],
        },
        'pcbnew': {'page_layout_descr_file': ''},
        'sheets': [], 'text_variables': {},
    }, indent=2) + '\n', encoding='utf-8')
    missing = [r for r in parts if r not in placed]
    print(f'{len(parts)} parts, {len(nets)} nets -> {PCB.name}, {PRO.name}; fixed: {sum(1 for p in placed.values() if p == "fast")}, '
          f'in rows: {sum(1 for p in placed.values() if p != "fast")}, unplaced: {missing}')
    return 0 if not missing else 1


if __name__ == '__main__':
    sys.exit(main())
