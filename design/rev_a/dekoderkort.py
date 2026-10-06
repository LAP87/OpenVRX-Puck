#!/usr/bin/env python3
"""Rev A — dual TVP5150AM1 decoder board (schematic as code, SKiDL).

    .venv/bin/python design/rev_a/dekoderkort.py      # -> design/rev_a/out/

Two CVBS inputs (from two 5.8 GHz receivers) -> 2x TVP5150AM1 -> two 1x20
headers numbered like the Tang Nano 20K's J6 and J5, so a 1:1 ribbon/Dupont
cable gives exactly the M4 pin plan (OpenVRX-Core: gateware/boards/m4_dual_mix.cst). Any
other FPGA board can use the same signals. No FPGA and no HDMI on this board:
those choices stay open (research/ALTERNATIVA_VAGAR_2026-10-02.md).

Every connection follows TI SLES209E (TVP5150AM1): terminal table 2-1, reset
section 3.18, clock section 3.16 (XTAL1 is a 1.8 V input, abs. max 2.3 V —
hence a crystal per decoder, never a 3.3 V oscillator), application example
figure 6-1 (2 x 37.4 ohm divider/termination, 0.1 uF coupling, REFP/REFM 1 uF,
10 k pull-down on INTREQ/GPCL/VBLK, PDN high, I2CSEL pull).

Outputs: KiCad netlist (importable into Pcbnew once footprints are
assigned/checked), BOM CSV, ERC log, connection report. Values marked TBD
need a part choice; LCSC numbers are only given where checked.
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

import skidl
import builtins

from skidl import ERC, POWER, SKIDL, Net, Part, Pin, generate_netlist

NC = builtins.NC          # SKiDL keeps its no-connect net in builtins

OUT = Path(__file__).resolve().parent / 'out'
T = Pin.types

FP_0402R = 'Resistor_SMD:R_0402_1005Metric'
FP_0402C = 'Capacitor_SMD:C_0402_1005Metric'
FP_0603C = 'Capacitor_SMD:C_0603_1608Metric'
FP_0805C = 'Capacitor_SMD:C_0805_2012Metric'
FP_0603L = 'Inductor_SMD:L_0603_1608Metric'


# ---------------------------------------------------------------- part helpers
def two_pin(prefix, value, fp, note=''):
    p = Part(tool=SKIDL, name=prefix, ref_prefix=prefix, value=value, footprint=fp,
             pins=[Pin(num=1, name='1', func=T.PASSIVE), Pin(num=2, name='2', func=T.PASSIVE)])
    p.fields['note'] = note
    return p


def R(value, a, b, note='', fp=FP_0402R):
    p = two_pin('R', value, fp, note)
    p[1] += a
    p[2] += b
    return p


def C(value, a, b, note='', fp=FP_0402C):
    p = two_pin('C', value, fp, note)
    p[1] += a
    p[2] += b
    return p


def FB(a, b, note='ferrite bead 600 ohm @ 100 MHz, >= 200 mA'):
    p = two_pin('FB', 'BLM18KG601SN1D', FP_0603L, note)
    p[1] += a
    p[2] += b
    return p


def tvp5150am1():
    """TI TVP5150AM1, 32-TQFP (PBS), pinout from SLES209E table 2-1."""
    pins = [
        (1, 'AIP1A', T.INPUT), (2, 'AIP1B', T.INPUT), (3, 'PLL_AGND', T.PWRIN), (4, 'PLL_AVDD', T.PWRIN),
        (5, 'XTAL1', T.INPUT), (6, 'XTAL2', T.OUTPUT), (7, 'AGND', T.PWRIN), (8, 'RESETB', T.INPUT),
        (9, 'SCLK', T.OUTPUT), (10, 'IO_DVDD', T.PWRIN), (11, 'YOUT7_I2CSEL', T.BIDIR), (12, 'YOUT6', T.TRISTATE),
        (13, 'YOUT5', T.TRISTATE), (14, 'YOUT4', T.TRISTATE), (15, 'YOUT3', T.TRISTATE), (16, 'YOUT2', T.TRISTATE),
        (17, 'YOUT1', T.TRISTATE), (18, 'YOUT0', T.TRISTATE), (19, 'DGND', T.PWRIN), (20, 'DVDD', T.PWRIN),
        (21, 'SCL', T.BIDIR), (22, 'SDA', T.BIDIR), (23, 'FID_GLCO', T.OUTPUT), (24, 'VSYNC_PALI', T.OUTPUT),
        (25, 'HSYNC', T.OUTPUT), (26, 'AVID', T.OUTPUT), (27, 'INTREQ_GPCL_VBLK', T.OUTPUT), (28, 'PDN', T.INPUT),
        (29, 'REFP', T.PASSIVE), (30, 'REFM', T.PASSIVE), (31, 'CH_AGND', T.PWRIN), (32, 'CH_AVDD', T.PWRIN),
    ]
    # Industrial grade (-40..85 C) instead of the commercial TVP5150AM1PBSR (0..70 C): the board sits in a
    # closed housing next to two receivers and an FPGA board, where 70 C is not a comfortable ceiling.
    # Same die, same 32-TQFP pinout; only the temperature screening and the ordering code differ (Puck #3).
    p = Part(tool=SKIDL, name='TVP5150AM1PBS', ref_prefix='U', value='TVP5150AM1IPBSR',
             footprint='Package_QFP:TQFP-32_5x5mm_P0.5mm',
             pins=[Pin(num=n, name=nm, func=f) for n, nm, f in pins])
    p.fields['note'] = ('TI TVP5150AM1IPBSR, industrial grade -40..85 C; LCSC C10013 is the commercial-grade code '
                        'and has NOT been checked for this grade (Other Suppliers, per design/REV_A_KONCEPT.md)')
    return p


def ldo_ap7361c_sot223(value, note):
    """Diodes AP7361C fixed, SOT-223 (E): 1 = IN, 2 = GND (tab), 3 = OUT (DS37274 rev 5 pin table).
    NOT the AMS1117 order (1 = GND, 2 = OUT, 3 = IN). Stable with >= 2.2 uF ceramic on OUT,
    >= 1 uF on IN; theta-JA 110 C/W."""
    p = Part(tool=SKIDL, name='LDO_AP7361C', ref_prefix='U', value=value,
             footprint='Package_TO_SOT_SMD:SOT-223-3_TabPin2',
             pins=[Pin(num=1, name='VIN', func=T.PWRIN), Pin(num=2, name='GND', func=T.PWRIN),
                   Pin(num=3, name='VOUT', func=T.PWROUT)])
    p.fields['note'] = note
    return p


def ldo_ap2112k(value, note):
    """Diodes AP2112K, SOT-23-5: 1 = VIN, 2 = GND, 3 = EN (high = on), 4 = NC, 5 = VOUT (AP2112 datasheet).
    1 uF X5R/X7R ceramic on IN and OUT is enough for stability."""
    p = Part(tool=SKIDL, name='LDO_AP2112K', ref_prefix='U', value=value,
             footprint='Package_TO_SOT_SMD:SOT-23-5',
             pins=[Pin(num=1, name='VIN', func=T.PWRIN), Pin(num=2, name='GND', func=T.PWRIN),
                   Pin(num=3, name='EN', func=T.INPUT), Pin(num=4, name='NC', func=T.NOCONNECT),
                   Pin(num=5, name='VOUT', func=T.PWROUT)])
    p.fields['note'] = note
    return p


def header_1x20(ref_note):
    p = Part(tool=SKIDL, name='CONN_1x20', ref_prefix='J', value='PinHeader_1x20',
             footprint='Connector_PinHeader_2.54mm:PinHeader_1x20_P2.54mm_Vertical',
             pins=[Pin(num=i, name=str(i), func=T.PASSIVE) for i in range(1, 21)])
    p.fields['note'] = ref_note
    return p


def conn(n, name, fp, note):
    p = Part(tool=SKIDL, name=name, ref_prefix='J', value=name, footprint=fp,
             pins=[Pin(num=i, name=str(i), func=T.PASSIVE) for i in range(1, n + 1)])
    p.fields['note'] = note
    return p


# ---------------------------------------------------------------- nets
def power_net(name):
    n = Net(name)
    n.drive = POWER
    return n


GND = power_net('GND')
AGND = GND        # one ground plane; analog return kept local in layout (see notes)
V5 = power_net('+5V')
V3 = Net('+3V3')
V18D = Net('+1V8_D')
V18A = Net('+1V8_A')
SCL = Net('I2C_SCL')
RESETB = Net('TVP_RESETB')


def build():
    # ---- power: 5 V from the FPGA board header (J5-1) or the aux connector
    j_pwr = conn(2, 'PWR_IN', 'Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical',
                 'Optional 5 V input if not powered from header J5-1')
    j_pwr[1] += V5
    j_pwr[2] += GND
    C('22u', V5, GND, '5 V bulk', FP_0805C)

    u3 = ldo_ap7361c_sot223('AP7361C-33E-13',
                            'LCSC C500795. 5 V -> 3.3 V for TVP IO_DVDD, pull-ups and both 1.8 V LDOs '
                            '(~170 mA: 0.29 W, +32 C at 110 C/W)')
    u3['VIN'] += V5
    u3['GND'] += GND
    u3['VOUT'] += V3
    C('10u', V5, GND, 'LDO in (>= 1 uF ceramic)', FP_0805C)
    C('10u', V3, GND, 'LDO out (>= 2.2 uF ceramic)', FP_0805C)
    V3.drive = POWER

    for rail, label, load in ((V18D, 'digital (2x DVDD)', '~66 mA'), (V18A, 'analog (2x CH_AVDD + PLL_AVDD)', '~78 mA')):
        u = ldo_ap2112k('AP2112K-1.8TRG1', f'LCSC C176944. 3.3 V -> 1.8 V {label}, {load} max (0.12 W)')
        u['VIN'] += V3
        u['EN'] += V3                          # always on
        u['GND'] += GND
        u['VOUT'] += rail
        C('1u', V3, GND, 'LDO in (X5R/X7R)', FP_0603C)
        C('10u', rail, GND, 'LDO out (X5R/X7R, >= 1 uF)', FP_0805C)
        rail.drive = POWER

    # ---- shared I2C clock and reset from the FPGA
    R('4.7k', SCL, V3, 'I2C SCL pull-up')
    # RESETB comes from Tang pin 18 (J6-18), which also drives the board's LED3 through 510 ohm to 3.3 V,
    # so a pull-down here cannot hold it low before configuration (OpenVRX-Puck issue #1). Not needed:
    # the TVP's outputs stay disabled after power-on until register 03h is written, and the FPGA pulses
    # RESETB before initialising. (Pin 25 = J6-10 was used before: it is in the HDMI bank and is the CEC line.)

    # ---- FPGA headers, numbered like Tang Nano 20K J6 / J5 (v3921 schematic)
    j6 = header_1x20('Mirror of Tang Nano 20K J6: connect pin n to J6-n')
    j5 = header_1x20('Mirror of Tang Nano 20K J5: connect pin n to J5-n')

    sda = [Net('I2C_SDA_A'), Net('I2C_SDA_B')]
    for s in sda:
        R('4.7k', s, V3, 'I2C SDA pull-up')
    jp = two_pin('JP', 'SolderJumper_2_Open', 'Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm',
                 'Close to join SDA_A/SDA_B into one bus (then set decoder B to BAh, see R I2CSEL)')
    jp[1] += sda[0]
    jp[2] += sda[1]

    # decoder A on J6, decoder B on J5 (OpenVRX-Core: gateware/boards/m4_dual_mix.cst)
    hdr = {
        'A': dict(j=j6, sclk=5, d=[8, 9, 11, 12, 13, 14, 1, 2], sda=4),
        'B': dict(j=j5, sclk=4, d=[3, 5, 6, 10, 12, 13, 14, 17], sda=9),
    }
    j6[3] += SCL
    j6[18] += RESETB
    j6[20] += GND
    # 5 V from the Tang Nano 20K (its USB) through a solder jumper. Open JP2 when this board is
    # fed from J1 instead — e.g. when the two receivers (~0.45 A each) would overload the
    # FPGA board's USB port — so the two 5 V sources never back-feed each other.
    v5_tang = Net('+5V_TANG')
    j5[1] += v5_tang
    jp2 = two_pin('JP', 'SolderJumper_2_Bridged', 'Jumper:SolderJumper-2_P1.3mm_Bridged_RoundedPad1.0x1.5mm',
                  '5 V from Tang Nano 20K J5-1 (closed by default); open when powering from J1')
    jp2[1] += v5_tang
    jp2[2] += V5
    j5[2] += GND
    j5[15] += GND
    # deliberately unconnected: J6-6/7/15 are LED pins on the Tang Nano 20K, J6-10 is pin 25 (HDMI CEC),
    # J6-16/17 carry the RX5808 SPI SEL/DATA (wired straight to the receivers), J6-19 / J5-16 are the
    # Tang's 3.3 V outputs (this board makes its own 3.3 V), J5-7/8/11 are FPGA configuration pins,
    # J5-18..20 unused (J5-18 is the RX5808 SPI clock)
    for n in (6, 7, 10, 15, 16, 17, 19):
        j6[n] += NC
    for n in (7, 8, 11, 16, 18, 19, 20):
        j5[n] += NC

    for idx, ch in enumerate(('A', 'B')):
        h = hdr[ch]
        u = tvp5150am1()
        u.fields['note'] += f'; decoder {ch}'

        # supplies (each pin: 0.1 uF at the pin; analog pins behind a ferrite)
        avdd = Net(f'AVDD_{ch}')
        pavdd = Net(f'PLL_AVDD_{ch}')
        FB(V18A, avdd)
        FB(V18A, pavdd)
        avdd.drive = POWER
        pavdd.drive = POWER
        u['CH_AVDD'] += avdd
        u['PLL_AVDD'] += pavdd
        u['DVDD'] += V18D
        u['IO_DVDD'] += V3
        for g in ('CH_AGND', 'PLL_AGND', 'AGND', 'DGND'):
            u[g] += GND
        C('0.1u', avdd, GND, f'CH_AVDD {ch}')
        C('1u', avdd, GND, f'CH_AVDD {ch} (fig. 6-1 C3)', FP_0603C)
        C('0.1u', pavdd, GND, f'PLL_AVDD {ch}, C0G preferred')
        # A ferrite followed only by 0.1 uF is a lightly damped LC: the bead is inductive well below its
        # 100 MHz rating and the small ceramic has almost no ESR, so it can ring and peak (Puck #3).
        # A larger capacitor after the bead lowers the filter's characteristic impedance and keeps the
        # supply node stiff at the PLL's loop frequencies. The 0.1 uF stays for the high frequencies.
        C('4.7u', pavdd, GND, f'PLL_AVDD {ch} bulk after the ferrite (4.7-10 uF, damps the bead/0.1 uF LC)', FP_0603C)
        C('0.1u', V18D, GND, f'DVDD {ch}')
        C('0.1u', V3, GND, f'IO_DVDD {ch} (fig. 6-1 C10)')

        # references (fig. 6-1 C1, C2 and REFP-REFM)
        refp, refm = Net(f'REFP_{ch}'), Net(f'REFM_{ch}')
        u['REFP'] += refp
        u['REFM'] += refm
        C('1u', refp, GND, f'REFP {ch}', FP_0603C)
        C('1u', refm, GND, f'REFM {ch}', FP_0603C)
        C('1u', refp, refm, f'REFP-REFM {ch}', FP_0603C)

        # video input: connector -> ESD -> 37.4 + 37.4 ohm (75 ohm termination, /2) -> AAF footprint -> 0.1 uF
        jin = conn(3, f'VIDEO_IN_{ch}', 'Connector_JST:JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical',
                   f'Receiver {ch}: 1 = +5 V out (fused), 2 = GND, 3 = CVBS')
        cvbs = Net(f'CVBS_{ch}')
        mid = Net(f'CVBS_DIV_{ch}')
        aaf = Net(f'CVBS_AAF_{ch}')
        ain = Net(f'AIP1A_{ch}')
        v5rx = Net(f'+5V_RX_{ch}')
        jin[1] += v5rx
        jin[2] += GND
        jin[3] += cvbs
        # Hold current, not trip: the receiver draws ~0.45 A. A 0.5 A hold part is derated to ~0.44 A at 40 C
        # and ~0.35 A at 60 C (Bourns MF-NSMF curves, as cited in the review of #2), which is below the load.
        # 0.75 A hold scales to roughly 0.66 A / 0.53 A on the same curve (estimate, not read from a datasheet).
        f = two_pin('F', '0.75A hold PTC', 'Fuse:Fuse_1206_3216Metric',
                    f'Resettable fuse for receiver {ch} supply, >= 0.75 A HOLD current (SpeedyBee draws ~0.45 A at 5 V); '
                    'check that the chosen series is available in 1206, else change footprint')
        f[1] += V5
        f[2] += v5rx
        v5rx.drive = POWER
        C('10u', v5rx, GND, f'receiver {ch} supply', FP_0805C)
        esd = Part(tool=SKIDL, name='ESD', ref_prefix='D', value='ESD9B5.0ST5G',
                   footprint='Diode_SMD:D_SOD-923',
                   pins=[Pin(num=1, name='K', func=T.PASSIVE), Pin(num=2, name='A', func=T.PASSIVE)])
        esd.fields['note'] = ('LCSC C111566, bidirectional 5 V, ~15 pF (pole ~280 MHz at ~37 ohm: no effect on video); '
                              'bidirectional because AC-coupled receiver outputs swing below 0 V (fig. 6-1 note G)')
        esd['K'] += cvbs
        esd['A'] += GND
        # Kept at 37.4/37.4 ohm (fig. 6-1). Alternative for hot video levels (receiver output that clips the
        # TVP5150's input range): 47 ohm series / 27 ohm shunt, from TI SLEU044. That is 74 ohm in total, still a
        # fair 75 ohm termination, but the gain drops from 0.50 to 0.36. The AAF source impedance then falls from
        # ~28 to ~22 ohm, so recheck the 0.47 uH / 1 nF filter if it is fitted. Same 0402 positions, no re-layout.
        R('37.4', cvbs, mid, f'fig. 6-1 R1/R5: series half of the 2x37.4 ohm termination ({ch}); 47 ohm = hot-video alternative (SLEU044)')
        R('37.4', mid, GND, f'fig. 6-1 R2/R6: shunt half ({ch}); 27 ohm = hot-video alternative (SLEU044)')
        # anti-aliasing filter (fig. 6-1 note F), 2nd-order LC from the ~28 ohm Thevenin source of the
        # divider: f0 7.3 MHz, Q 0.77 -> flat to 4.2 MHz, -1 dB @ 6 MHz, -10.6 dB @ 13.5 MHz, -22.6 dB @ 27 MHz
        # (design/rev_a/README.md). A 0 ohm in the L position bypasses it.
        aafl = two_pin('L', '0.47uH', FP_0603L,
                       f'AAF inductor ({ch}): 0603, SRF > 100 MHz, DCR < 0.5 ohm; or 0 ohm to bypass')
        aafl[1] += mid
        aafl[2] += aaf
        C('1n C0G', aaf, GND, f'AAF capacitor ({ch}), C0G/NP0', FP_0402C)
        C('0.1u', aaf, ain, f'AC coupling to AIP1A ({ch}, fig. 6-1 C4/C5)')
        u['AIP1A'] += ain
        tp = Part(tool=SKIDL, name='TP', ref_prefix='TP', value='TestPoint',
                  footprint='TestPoint:TestPoint_Pad_D1.0mm', pins=[Pin(num=1, name='1', func=T.PASSIVE)])
        tp[1] += cvbs
        # unused second input: 0.1 uF to ground (table 2-1)
        ain_b = Net(f'AIP1B_{ch}')
        u['AIP1B'] += ain_b
        C('0.1u', ain_b, GND, f'AIP1B unused ({ch}): 0.1 uF to AGND per table 2-1')

        # clock: own crystal per decoder (XTAL1 abs. max 2.3 V)
        x1, x2 = Net(f'XTAL1_{ch}'), Net(f'XTAL2_{ch}')
        u['XTAL1'] += x1
        u['XTAL2'] += x2
        y = Part(tool=SKIDL, name='XTAL', ref_prefix='Y', value='X32251431818MSB4SI',
                 footprint='Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm',
                 pins=[Pin(num=1, name='1', func=T.PASSIVE), Pin(num=2, name='GND', func=T.PASSIVE),
                       Pin(num=3, name='3', func=T.PASSIVE), Pin(num=4, name='GND2', func=T.PASSIVE)])
        y.fields['note'] = ('YXC 14.31818 MHz, CL 20 pF, +-10 ppm at 25 C / +-20 ppm over -40..85 C, SMD3225-4P '
                            '(TVP needs +-50 ppm); LCSC C34748. CL1 = CL2 = 2*CL - Cstray = 40 - ~5 -> 33 pF (section 3.16)')
        y[1] += x1
        y[3] += x2
        y[2] += GND
        y[4] += GND
        C('33p C0G', x1, GND, f'CL1 {ch}: 2*20 pF - ~5 pF stray; trim after measuring SCLK frequency')
        C('33p C0G', x2, GND, f'CL2 {ch}')
        R('100k', x1, x2, f'parallel resistor across crystal ({ch}, fig. 6-1 note E)')

        # control pins
        u['RESETB'] += RESETB
        pdn = Net(f'PDN_{ch}')
        u['PDN'] += pdn
        R('10k', pdn, V3, f'PDN high = always on ({ch}, fig. 6-1 note C)')
        intreq = Net(f'INTREQ_{ch}')
        u['INTREQ_GPCL_VBLK'] += intreq
        R('10k', intreq, GND, f'pin 27 must not float; 10 k pull-down while the output is disabled ({ch}, note H)')
        for nm in ('FID_GLCO', 'VSYNC_PALI', 'HSYNC', 'AVID'):
            n = Net(f'{nm}_{ch}')
            u[nm] += n
            t = Part(tool=SKIDL, name='TP', ref_prefix='TP', value='TestPoint',
                     footprint='TestPoint:TestPoint_Pad_D1.0mm', pins=[Pin(num=1, name='1', func=T.PASSIVE)])
            t[1] += n       # discrete syncs reachable for M1s/M2s-style capture if ever needed

        # I2C
        u['SCL'] += SCL
        u['SDA'] += sda[idx]
        j = h['j']
        j[h['sda']] += sda[idx]

        # data + clock outputs: 33 ohm series resistors at the TVP (cable drive)
        yout = ['YOUT0', 'YOUT1', 'YOUT2', 'YOUT3', 'YOUT4', 'YOUT5', 'YOUT6', 'YOUT7_I2CSEL']
        for bit, nm in enumerate(yout):
            near, far = Net(f'{ch}_{nm}_U'), Net(f'TVP{ch}_D{bit}')
            u[nm] += near
            R('33', near, far, f'series termination {ch} D{bit}')
            j[h['d'][bit]] += far
        # I2CSEL (sampled at reset): 10 k pull-down -> B8h on both (M4 uses split SDA);
        # alternative pull-up footprint for BAh when sharing one SDA line
        R('10k', Net.get(f'{ch}_YOUT7_I2CSEL_U'), GND, f'I2CSEL low = B8h ({ch})')
        R('DNP 10k', Net.get(f'{ch}_YOUT7_I2CSEL_U'), V3, f'fit instead of the pull-down for BAh ({ch})')
        sclk_u, sclk = Net(f'{ch}_SCLK_U'), Net(f'TVP{ch}_SCLK')
        u['SCLK'] += sclk_u
        R('33', sclk_u, sclk, f'series termination {ch} SCLK')
        j[h['sclk']] += sclk
        tps = Part(tool=SKIDL, name='TP', ref_prefix='TP', value='TestPoint',
                   footprint='TestPoint:TestPoint_Pad_D1.0mm', pins=[Pin(num=1, name='1', func=T.PASSIVE)])
        tps[1] += sclk
        # Ground pad beside this header, close to the 27 MHz SCLK pin (Puck #3): a scope ground spring or a
        # short return wire here keeps the probe loop small. Without it the nearest ground to measure SCLK
        # against is a header pin or the far connector, and the long ground lead shows ringing that is not there.
        tpg = Part(tool=SKIDL, name='TP', ref_prefix='TP', value='TestPoint_GND',
                   footprint='TestPoint:TestPoint_Pad_D1.0mm', pins=[Pin(num=1, name='1', func=T.PASSIVE)])
        tpg.fields['note'] = f'GND pad next to header {j.ref} (SCLK {ch}): probe ground for the 27 MHz clock'
        tpg[1] += GND

    for k in range(4):
        Part(tool=SKIDL, name='MH', ref_prefix='H', value='MountingHole_M2', footprint='MountingHole:MountingHole_2.2mm_M2',
             pins=[])


# ---------------------------------------------------------------- checks + outputs
# Tang Nano 20K header position -> FPGA pin (Sipeed v3921 page 2; unchanged positions on 3923).
# M3/M4/M6 require revision 3923 because earlier BL616 connections conflict with these signals.
TANG_J6 = {1: 73, 2: 74, 3: 75, 4: 85, 5: 77, 6: 15, 7: 16, 8: 27, 9: 28, 10: 25, 11: 26, 12: 29, 13: 30, 14: 31,
           15: 17, 16: 20, 17: 19, 18: 18}
TANG_J5 = {3: 76, 4: 80, 5: 42, 6: 41, 7: 56, 8: 54, 9: 51, 10: 48, 11: 55, 12: 49, 13: 86, 14: 79, 17: 72, 18: 71,
           19: 53, 20: 52}
# board net -> port name in gateware/boards/m4_dual_mix.cst (RESETB is the tvp_resetb port on pin 18, the LED3 pin)
NET_TO_PORT = {'TVPA_SCLK': 'tvpa_sclk', 'TVPB_SCLK': 'tvpb_sclk', 'I2C_SCL': 'i2c_scl', 'I2C_SDA_A': 'i2c_sda_a',
               'I2C_SDA_B': 'i2c_sda_b', 'TVP_RESETB': 'tvp_resetb',
               **{f'TVP{c}_D{i}': f'tvp{c.lower()}_d[{i}]' for c in 'AB' for i in range(8)}}


def check_against_gateware(circuit, gw=None):
    """Header pin n on this board must carry the signal the M4 bitstream expects on J6-n / J5-n."""
    import re
    root = Path(__file__).resolve().parents[2]
    gw = Path(gw) if gw is not None else root / 'core' / 'gateware'
    if not gw.exists():
        gw = root / 'gateware'                       # original single-tree layout
    cst = (gw / 'boards' / 'tangnano20k.cst').read_text() + (gw / 'boards' / 'm4_dual_mix.cst').read_text()
    port_pin = {m[0]: int(m[1]) for m in re.findall(r'IO_LOC\s+"([^"]+)"\s+(\d+);', cst)}
    problems, seen = [], set()
    contract = gw / 'tools' / 'board_contract.py'
    if not contract.is_file():
        problems.append('pinned Core lacks the shared-output contract; update the core submodule')
    else:
        import importlib.util
        spec = importlib.util.spec_from_file_location('board_contract', contract)
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        board = (gw / 'boards' / 'tangnano20k.cst').read_text()
        for top in ('m3_probe', 'm4_dual_mix', 'm6_puck_proto'):
            problems += checker.shared_output_problems((gw / 'top' / f'{top}.v').read_text(), top,
                                                       board + (gw / 'boards' / f'{top}.cst').read_text())
    for part in circuit.parts:
        if part.name != 'CONN_1x20':
            continue
        table = TANG_J6 if 'J6' in part.fields['note'] else TANG_J5
        for pin in part.pins:
            net = pin.net.name if pin.net is not None else None
            if net in NET_TO_PORT:
                port = NET_TO_PORT[net]
                seen.add(port)
                want = port_pin.get(port)
                got = table.get(int(pin.num))
                if want != got:
                    problems.append(f'{net} on header pin {pin.num} = FPGA pin {got}, M4 expects {want}')
    missing = set(NET_TO_PORT.values()) - seen
    if missing:
        problems.append(f'signals not on any header: {sorted(missing)}')
    return problems


def design_checks(circuit):
    """Rules from the datasheet that ERC cannot know, plus the gateware pin plan."""
    problems = check_against_gateware(circuit)
    nets = {n.name: n for n in circuit.nets}
    for ch in 'AB':
        x1 = nets[f'XTAL1_{ch}']
        names = {p.part.value for p in x1.pins}
        if any('3.3' in str(v) for v in names):
            problems.append(f'XTAL1_{ch} touches a 3.3 V part')
        for p in x1.pins:
            for other in p.part.pins:
                if other.net is not None and other.net.name in ('+3V3', '+5V') and p.part.ref.startswith(('Y', 'C')):
                    problems.append(f'XTAL1_{ch} part {p.part.ref} connects to {other.net.name}')
    for part in circuit.parts:
        if part.name == 'TVP5150AM1PBS':
            for pin in part.pins:
                if pin.net is None or not pin.net.name:
                    problems.append(f'{part.ref} pin {pin.num} {pin.name} unconnected')
            supply = {pin.name: pin.net.name for pin in part.pins}
            if supply['IO_DVDD'] != '+3V3' or supply['DVDD'] != '+1V8_D':
                problems.append(f'{part.ref} supply mapping wrong: {supply}')
            if not supply['CH_AVDD'].startswith('AVDD_') or not supply['PLL_AVDD'].startswith('PLL_AVDD_'):
                problems.append(f'{part.ref} analog supplies not behind ferrites')
    # regulators: input from the higher rail, output on the lower one (catches swapped pinouts)
    want = {'+3V3': '+5V', '+1V8_D': '+3V3', '+1V8_A': '+3V3'}
    for part in circuit.parts:
        if part.name.startswith('LDO'):
            pins = {pin.name: (pin.net.name if pin.net is not None else None) for pin in part.pins}
            if want.get(pins['VOUT']) != pins['VIN'] or pins['GND'] != 'GND':
                problems.append(f'{part.ref} {part.value}: VIN={pins["VIN"]} VOUT={pins["VOUT"]} GND={pins["GND"]}')
    # every I2C line has exactly one pull-up
    for nm in ('I2C_SCL', 'I2C_SDA_A', 'I2C_SDA_B'):
        pulls = [p.part for p in nets[nm].pins if p.part.ref.startswith('R')
                 and any(o.net is not None and o.net.name == '+3V3' for o in p.part.pins)]
        if len(pulls) != 1:
            problems.append(f'{nm} has {len(pulls)} pull-ups')
    return problems


def write_reports(circuit):
    OUT.mkdir(parents=True, exist_ok=True)
    # BOM grouped by value + footprint
    groups = defaultdict(list)
    for p in circuit.parts:
        if not p.pins and p.name == 'MH':
            key = (p.name, p.value, p.footprint, '')
        else:
            key = (p.name, str(p.value), p.footprint, p.fields.get('note', '') if p.name not in ('R', 'C') else '')
        groups[key].append(p.ref)
    with (OUT / 'dekoderkort_bom.csv').open('w', newline='') as fh:
        w = csv.writer(fh, lineterminator='\n')
        w.writerow(['qty', 'refs', 'part', 'value', 'footprint', 'note'])
        for (name, value, fp, note), refs in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
            w.writerow([len(refs), ' '.join(sorted(refs, key=lambda r: (r.rstrip('0123456789'), int(''.join(c for c in r if c.isdigit()) or 0)))),
                        name, value, fp, note])
    # human-readable connection report
    lines = ['# Dekoderkort — kopplingsrapport (genererad)', '']
    for p in sorted(circuit.parts, key=lambda p: p.ref):
        if not p.pins:
            continue
        lines.append(f'## {p.ref} {p.value}')
        if p.fields.get('note'):
            lines.append(f'_{p.fields["note"]}_')
        lines.append('')
        for pin in p.pins:
            lines.append(f'- {pin.num} {pin.name}: {pin.net.name if pin.net is not None else "—"}')
        lines.append('')
    (OUT / 'dekoderkort_kopplingar.md').write_text('\n'.join(lines))


def main():
    build()
    import builtins
    circuit = builtins.default_circuit
    problems = design_checks(circuit)
    if problems:
        print('DESIGN CHECK FAILED:\n  ' + '\n  '.join(problems))
        return 1                         # do not replace accepted outputs with a mismatched design
    OUT.mkdir(parents=True, exist_ok=True)
    ERC()
    from skidl.logger import erc_logger
    if erc_logger.error.count or erc_logger.warning.count:
        print('ERC failed; outputs were not regenerated')
        return 1
    # Stable identifiers make schematic changes reviewable instead of random tag churn.
    # KiCad requires an empty root hierarchy. SKiDL warns about its empty tag;
    # leave it empty rather than changing the generated hierarchy.
    for part in circuit.parts:
        part.tag = part.ref
    for net in circuit.nets:
        net.tag = net.name
    generate_netlist(file_=str(OUT / 'dekoderkort.net'), track_src=False, track_abs_path=False)
    write_reports(circuit)
    print(f'{len(circuit.parts)} parts, {len([n for n in circuit.nets if n.pins])} nets -> {OUT}')
    print('design checks passed')
    return 0


if __name__ == '__main__':
    sys.exit(main())
