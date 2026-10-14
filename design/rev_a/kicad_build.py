"""Build the rev A KiCad project: board file with the SKiDL netlist imported.

Night-pass task 18 (docs/NATTPASS_2026-10-13.md): design/rev_a/kicad/ with the
project file, the board file carrying all 126 parts with their footprints
(outside the board outline, in netlist/block order per LAYOUT.md), the outline
and the mounting holes, DRC rules (0,15/0,15 mm, via 0,3/0,6 mm) and the net
classes of LAYOUT.md section 4 (27M, CVBS, POWER). No routing.

The netlist names Package_QFP:TQFP-32_5x5mm_P0.5mm for the TVP5150AM1 PBS
package (32-TQFP, 5x5 mm, per TI's part page). KiCad's official library ships
that geometry only as LQFP-32_5x5mm_P0.5mm (NXP SOT401-1); this script copies
it into a local library kicad/footprints/Package_QFP.pretty under the
netlist's name so the netlist imports unmodified. Everything else resolves in
the official libraries.

Run:  python design/rev_a/kicad_build.py      (needs KiCad 9 with pcbnew)
"""
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE / 'kicad'
NETLIST = HERE / 'out' / 'dekoderkort.net'

BOARD_MM = (66.0, 58.0)          # LAYOUT.md: proposed outline
HOLE_EDGE_MM = 3.5               # M2 holes, 3,5 mm from the edges
HOLE_DRILL_MM = 2.2
NET_CLASSES = {                  # LAYOUT.md section 4
    '27M': 0.15,
    'CVBS': 0.15,
    'POWER': 0.30,
}


def parts_of_netlist():
    """[(ref, value, 'Lib:Footprint')] in netlist order."""
    text = NETLIST.read_text()
    comps = text[text.find('(components'):text.find('(nets')]
    pat = re.compile(r'\(comp\s+\(ref "([^"]+)"\)\s+\(value "([^"]*)"\)[\s\S]*?\(footprint "([^"]+)"\)')
    return pat.findall(comps)


def official_footprints():
    env = os.environ.get('KICAD9_FOOTPRINTS')
    if env:
        return Path(env)
    for cand in ('/usr/share/kicad/footprints', '/tmp/kicad-root/usr/share/kicad/footprints'):
        if Path(cand).is_dir():
            return Path(cand)
    sys.exit('KiCad footprint libraries not found; set KICAD9_FOOTPRINTS')


def provide_local_footprint(lib, name, official):
    """The netlist's TQFP-32_5x5 name does not exist upstream; alias the LQFP file."""
    dst_lib = PROJECT / 'footprints' / f'{lib}.pretty'
    dst_lib.mkdir(parents=True, exist_ok=True)
    dst = dst_lib / f'{name}.kicad_mod'
    if not dst.exists():
        src = official / f'{lib}.pretty' / f'LQFP-32_5x5mm_P0.5mm.kicad_mod'
        dst.write_text(src.read_text().replace('LQFP-32_5x5mm_P0.5mm', name))


def build():
    import pcbnew
    from pcbnew import VECTOR2I, FromMM

    PROJECT.mkdir(exist_ok=True)
    official = official_footprints()
    parts = parts_of_netlist()
    assert len(parts) == 126, f'expected 126 components, netlist has {len(parts)}'
    for _, _, fp in parts:
        lib, name = fp.split(':')
        if not (official / f'{lib}.pretty' / f'{name}.kicad_mod').exists():
            provide_local_footprint(lib, name, official)

    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)                  # LAYOUT.md: four layers

    # outline: 66 x 58 mm rectangle on Edge_Cuts
    w, h = FromMM(BOARD_MM[0]), FromMM(BOARD_MM[1])
    for a, b in (((0, 0), (w, 0)), ((w, 0), (w, h)), ((w, h), (0, h)), ((0, h), (0, 0))):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(VECTOR2I(*a))
        seg.SetEnd(VECTOR2I(*b))
        seg.SetLayer(pcbnew.Edge_Cuts)
        board.Add(seg)

    # mounting holes: four M2, 3,5 mm from the edges (LAYOUT.md section 6)
    for xm, ym in ((HOLE_EDGE_MM, HOLE_EDGE_MM),
                   (BOARD_MM[0] - HOLE_EDGE_MM, HOLE_EDGE_MM),
                   (BOARD_MM[0] - HOLE_EDGE_MM, BOARD_MM[1] - HOLE_EDGE_MM),
                   (HOLE_EDGE_MM, BOARD_MM[1] - HOLE_EDGE_MM)):
        fp = pcbnew.FOOTPRINT(board)
        pad = pcbnew.PAD(fp)
        pad.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        pad.SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
        pad.SetLayerSet(pcbnew.LSET.AllCuMask())
        pad.SetPosition(VECTOR2I(FromMM(xm), FromMM(ym)))
        pad.SetSize(VECTOR2I(FromMM(HOLE_DRILL_MM), FromMM(HOLE_DRILL_MM)))
        pad.SetDrillShape(pcbnew.PAD_SHAPE_CIRCLE)
        pad.SetDrillSize(VECTOR2I(FromMM(HOLE_DRILL_MM), FromMM(HOLE_DRILL_MM)))
        fp.Add(pad)
        board.Add(fp)

    # net classes: LAYOUT.md section 4; the default carries the 0,15 mm rule
    settings = board.GetDesignSettings().m_NetSettings
    default = settings.GetDefaultNetclass()
    default.SetClearance(FromMM(0.15))
    default.SetTrackWidth(FromMM(0.15))
    default.SetViaDiameter(FromMM(0.6))
    default.SetViaDrill(FromMM(0.3))
    for cls, width in NET_CLASSES.items():
        nc = pcbnew.NETCLASS(cls)
        nc.SetClearance(FromMM(0.15))
        nc.SetTrackWidth(FromMM(width))
        nc.SetViaDiameter(FromMM(0.6))
        nc.SetViaDrill(FromMM(0.3))
        settings.SetNetclass(cls, nc)

    # DRC minimums (0,15/0,15, via 0,3/0,6)
    ds = board.GetDesignSettings()
    ds.m_MinClearance = FromMM(0.15)
    ds.m_TrackMinWidth = FromMM(0.15)
    ds.m_ViasMinSize = FromMM(0.6)
    ds.m_ViasMinDrill = FromMM(0.3)

    # every part with its footprint, outside the outline in netlist (block) order
    io = pcbnew.PCB_IO_KICAD_SEXPR()
    col_x, y = FromMM(-90.0), FromMM(-70.0)
    n_in_col = 0
    for ref, value, fp_name in parts:
        lib, name = fp_name.split(':')
        official_file = official / f'{lib}.pretty' / f'{name}.kicad_mod'
        lib_path = str(official / f'{lib}.pretty') if official_file.exists() \
            else str(PROJECT / 'footprints' / f'{lib}.pretty')
        f = io.FootprintLoad(lib_path, name)
        f.SetReference(ref)
        f.SetValue(value)
        f.SetPosition(VECTOR2I(col_x, y))
        board.Add(f)
        n_in_col += 1
        y += FromMM(10.0)
        if n_in_col == 14:
            n_in_col = 0
            col_x += FromMM(15.0)
            y = FromMM(-70.0)

    out = PROJECT / 'dekoderkort.kicad_pcb'
    pcbnew.SaveBoard(str(out), board)

    # the project file: KiCad 9 keeps net classes and DRC minimums here; SaveBoard
    # writes a minimal one, so the rules of LAYOUT.md section 4 are merged in
    import json
    pro_path = PROJECT / 'dekoderkort.kicad_pro'
    pro = json.loads(pro_path.read_text()) if pro_path.exists() else {}
    pro.setdefault('meta', {})['filename'] = 'dekoderkort.kicad_pro'
    pro['boards'] = ['dekoderkort.kicad_pcb']
    pro.setdefault('board', {}).setdefault('design_settings', {})
    pro['board']['design_settings']['rules'] = {
        'min_clearance': 0.15, 'min_track_width': 0.15,
        'min_via_diameter': 0.6, 'min_via_drill': 0.3,
        'min_hole_to_hole': 0.25, 'min_hole_clearance': 0.25,
    }
    pro['board']['design_settings']['rule_severities'] = {
        'connection_width': 'warning', 'copper_sliver': 'warning',
        'silk_over_copper': 'warning', 'silk_overlap': 'warning',
    }
    classes = pro.setdefault('net_settings', {}).setdefault('classes', [])
    by_name = {c.get('name'): c for c in classes}
    for name, width in [('Default', 0.15), *NET_CLASSES.items()]:
        c = by_name.get(name)
        if c is None:
            c = {'bus_width': 12, 'clearance': 0.15, 'diff_pair_gap': 0.25,
                 'diff_pair_via_gap': 0.25, 'diff_pair_width': 0.2, 'line_style': 0,
                 'microvia_diameter': 0.3, 'microvia_drill': 0.1, 'name': name,
                 'pcb_color': 'rgba(0, 0, 0, 0.000)', 'priority': 2147483647 if name == 'Default' else 0,
                 'schematic_color': 'rgba(0, 0, 0, 0.000)', 'track_width': width,
                 'via_diameter': 0.6, 'via_drill': 0.3, 'wire_width': 6}
            classes.append(c)
        else:
            c['clearance'] = 0.15
            c['track_width'] = width
            c['via_diameter'] = 0.6
            c['via_drill'] = 0.3
    pro_path.write_text(json.dumps(pro, indent=2) + '\n')
    print(f'{out}: {len(parts)} footprints, outline {BOARD_MM[0]}x{BOARD_MM[1]} mm, '
          f'{len(NET_CLASSES)} net classes')
    return 0


if __name__ == '__main__':
    sys.exit(build())
