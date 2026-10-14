# OpenVRX-Puck

> Part of the [OpenVRX](https://github.com/LAP87/OpenVRX) family.

A portable analog FPV ground station without a screen: two 5.8 GHz receivers
on the same channel, two video decoders, an FPGA that keeps the cleaner signal
line by line, and HDMI out to goggles, XR glasses or a TV. Battery powered,
two buttons and a small OLED. It stands on the ground when you sit, or hangs
from a lanyard or clip when you stand. SMA connectors for screw-on patch and
omni antennas.

**Status: planned / early design.** The first board, rev A, is a decoder
board (2x TVP5150AM1 to pin headers) that plugs into a Tang Nano 20K running
[OpenVRX-Core](https://github.com/LAP87/OpenVRX-Core)'s `m6_puck_proto`. Its
schematic exists as a script (SKiDL), passes ERC and is checked against the
gateware pin plan and shared RESETB/SPI roles. It has a KiCad 9 project
(design/rev_a/kicad/, board file with all 126 parts, outline, holes and net
classes; no routing) but no layout yet, and no hardware has been tested.

## Why

A display-less puck separates the receiver from the display. Per-line
selection and blending are implemented in Core; real RF improvement and
camera-to-display latency remain unmeasured. The current output is 720p,
so compatibility with a chosen display must be checked before an XR build.

## Specifications (targets, not measured)

| | |
|---|---|
| Receivers | 2x RX5808 (SPI mod), tuned together over SPI; 48 channels |
| Antennas | 2x SMA bulkhead (patch + omni); shield-lid air patch as a later option |
| Decoders | 2x TVP5150AM1 (rev A board) |
| FPGA | Tang Nano 20K (GW2AR-18) for the prototype |
| Output | HDMI 720p (buffered, or genlocked low-latency) |
| RSSI | both receivers to an ADS1115 I2C ADC on the rev A board, read once per field |
| UI | 2 buttons, 0.91" 128x32 OLED, on-screen menu, USB-UART measurement log |
| Power | 2S 21700 Li-ion; USB-C PD in/out via IP2368 (planned) |
| Enclosure | thin tough resin, internal shield can grounded to circuit ground |

## Constraints

- Hobby prototype first, built from modules where possible.
- Receivers and FPGA stay as plug-in modules until the rest works.
- Self-interference matters: the gateware's snow meter and UART log exist to
  measure it (HDMI on/off, channel, shielding).

## Repository

| Path | What |
|---|---|
| `core/` | [OpenVRX-Core](https://github.com/LAP87/OpenVRX-Core) as a git submodule, pinned to a tested version |
| `design/rev_a/` | Decoder board schematic script, generated netlist/BOM/connection list, design notes |
| `design/PUCK_2027_KONCEPT.md` | Product concept: outputs, power, enclosure, EMI, antennas (Swedish) |
| `design/REV_A_KONCEPT.md` | Earlier integrated-board concept, now rev B (Swedish) |

## Pinned Core

The `core/` submodule pins `072dbdef3afe53384be19008768661bad20524d6`.
The suite is 757 tests, green on Core `main` `2b67dea` (both Core READMEs name the
commit of the suite and of every build). Core `main` since the previous pin
`46a1e4f` adds work-plan tasks 4-15 (VINTERP, AVI-infoframe, LOW row placement,
RSSI reading/calibration/mixer health, SCAN and settings in flash) and the night-pass
tasks 16-20 (campaign reruns, BRINGUP, status lines).

Vertical interpolation remains off, the transmitter defaults to DVI, and the
varying LOW line stays after vsync. VINTERP=1 with HDMI=1 has not been built in
this review. SDRAM pin timing and HDMI compatibility remain unmeasured on hardware.

```sh
git clone --recurse-submodules https://github.com/LAP87/OpenVRX-Puck
pip install skidl==2.3.0 pytest==9.1.1
python -m pytest -q tests
python design/rev_a/dekoderkort.py     # ERC, design rules, Core pin and signal-role checks
```

The schematic was generated with AI assistance from the datasheets
and reviewed by the project owner and one external model. The plan is to
redraw it in KiCad by hand before layout, which is also its most useful review.

## License

[CERN-OHL-S-2.0](https://ohwr.org/cern_ohl_s_v2.txt), see [LICENSE](LICENSE).
