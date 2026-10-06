# Dekoderkort — kopplingsrapport (genererad)

## C1 22u
_5 V bulk_

- 1 1: +5V
- 2 2: GND

## C10 0.1u
_PLL_AVDD A, C0G preferred_

- 1 1: PLL_AVDD_A
- 2 2: GND

## C11 4.7u
_PLL_AVDD A bulk after the ferrite (4.7-10 uF, damps the bead/0.1 uF LC)_

- 1 1: PLL_AVDD_A
- 2 2: GND

## C12 0.1u
_DVDD A_

- 1 1: +1V8_D
- 2 2: GND

## C13 0.1u
_IO_DVDD A (fig. 6-1 C10)_

- 1 1: +3V3
- 2 2: GND

## C14 1u
_REFP A_

- 1 1: REFP_A
- 2 2: GND

## C15 1u
_REFM A_

- 1 1: REFM_A
- 2 2: GND

## C16 1u
_REFP-REFM A_

- 1 1: REFP_A
- 2 2: REFM_A

## C17 10u
_receiver A supply_

- 1 1: +5V_RX_A
- 2 2: GND

## C18 1n C0G
_AAF capacitor (A), C0G/NP0_

- 1 1: CVBS_AAF_A
- 2 2: GND

## C19 0.1u
_AC coupling to AIP1A (A, fig. 6-1 C4/C5)_

- 1 1: CVBS_AAF_A
- 2 2: AIP1A_A

## C2 10u
_LDO in (>= 1 uF ceramic)_

- 1 1: +5V
- 2 2: GND

## C20 0.1u
_AIP1B unused (A): 0.1 uF to AGND per table 2-1_

- 1 1: AIP1B_A
- 2 2: GND

## C21 33p C0G
_CL1 A: 2*20 pF - ~5 pF stray; trim after measuring SCLK frequency_

- 1 1: XTAL1_A
- 2 2: GND

## C22 33p C0G
_CL2 A_

- 1 1: XTAL2_A
- 2 2: GND

## C23 0.1u
_CH_AVDD B_

- 1 1: AVDD_B
- 2 2: GND

## C24 1u
_CH_AVDD B (fig. 6-1 C3)_

- 1 1: AVDD_B
- 2 2: GND

## C25 0.1u
_PLL_AVDD B, C0G preferred_

- 1 1: PLL_AVDD_B
- 2 2: GND

## C26 4.7u
_PLL_AVDD B bulk after the ferrite (4.7-10 uF, damps the bead/0.1 uF LC)_

- 1 1: PLL_AVDD_B
- 2 2: GND

## C27 0.1u
_DVDD B_

- 1 1: +1V8_D
- 2 2: GND

## C28 0.1u
_IO_DVDD B (fig. 6-1 C10)_

- 1 1: +3V3
- 2 2: GND

## C29 1u
_REFP B_

- 1 1: REFP_B
- 2 2: GND

## C3 10u
_LDO out (>= 2.2 uF ceramic)_

- 1 1: +3V3
- 2 2: GND

## C30 1u
_REFM B_

- 1 1: REFM_B
- 2 2: GND

## C31 1u
_REFP-REFM B_

- 1 1: REFP_B
- 2 2: REFM_B

## C32 10u
_receiver B supply_

- 1 1: +5V_RX_B
- 2 2: GND

## C33 1n C0G
_AAF capacitor (B), C0G/NP0_

- 1 1: CVBS_AAF_B
- 2 2: GND

## C34 0.1u
_AC coupling to AIP1A (B, fig. 6-1 C4/C5)_

- 1 1: CVBS_AAF_B
- 2 2: AIP1A_B

## C35 0.1u
_AIP1B unused (B): 0.1 uF to AGND per table 2-1_

- 1 1: AIP1B_B
- 2 2: GND

## C36 33p C0G
_CL1 B: 2*20 pF - ~5 pF stray; trim after measuring SCLK frequency_

- 1 1: XTAL1_B
- 2 2: GND

## C37 33p C0G
_CL2 B_

- 1 1: XTAL2_B
- 2 2: GND

## C4 1u
_LDO in (X5R/X7R)_

- 1 1: +3V3
- 2 2: GND

## C5 10u
_LDO out (X5R/X7R, >= 1 uF)_

- 1 1: +1V8_D
- 2 2: GND

## C6 1u
_LDO in (X5R/X7R)_

- 1 1: +3V3
- 2 2: GND

## C7 10u
_LDO out (X5R/X7R, >= 1 uF)_

- 1 1: +1V8_A
- 2 2: GND

## C8 0.1u
_CH_AVDD A_

- 1 1: AVDD_A
- 2 2: GND

## C9 1u
_CH_AVDD A (fig. 6-1 C3)_

- 1 1: AVDD_A
- 2 2: GND

## D1 ESD9B5.0ST5G
_LCSC C111566, bidirectional 5 V, ~15 pF (pole ~280 MHz at ~37 ohm: no effect on video); bidirectional because AC-coupled receiver outputs swing below 0 V (fig. 6-1 note G)_

- 1 K: CVBS_A
- 2 A: GND

## D2 ESD9B5.0ST5G
_LCSC C111566, bidirectional 5 V, ~15 pF (pole ~280 MHz at ~37 ohm: no effect on video); bidirectional because AC-coupled receiver outputs swing below 0 V (fig. 6-1 note G)_

- 1 K: CVBS_B
- 2 A: GND

## F1 0.75A hold PTC
_Resettable fuse for receiver A supply, >= 0.75 A HOLD current (SpeedyBee draws ~0.45 A at 5 V); check that the chosen series is available in 1206, else change footprint_

- 1 1: +5V
- 2 2: +5V_RX_A

## F2 0.75A hold PTC
_Resettable fuse for receiver B supply, >= 0.75 A HOLD current (SpeedyBee draws ~0.45 A at 5 V); check that the chosen series is available in 1206, else change footprint_

- 1 1: +5V
- 2 2: +5V_RX_B

## FB1 BLM18KG601SN1D
_ferrite bead 600 ohm @ 100 MHz, >= 200 mA_

- 1 1: +1V8_A
- 2 2: AVDD_A

## FB2 BLM18KG601SN1D
_ferrite bead 600 ohm @ 100 MHz, >= 200 mA_

- 1 1: +1V8_A
- 2 2: PLL_AVDD_A

## FB3 BLM18KG601SN1D
_ferrite bead 600 ohm @ 100 MHz, >= 200 mA_

- 1 1: +1V8_A
- 2 2: AVDD_B

## FB4 BLM18KG601SN1D
_ferrite bead 600 ohm @ 100 MHz, >= 200 mA_

- 1 1: +1V8_A
- 2 2: PLL_AVDD_B

## J1 PWR_IN
_Optional 5 V input if not powered from header J5-1_

- 1 1: +5V
- 2 2: GND

## J2 PinHeader_1x20
_Mirror of Tang Nano 20K J6: connect pin n to J6-n_

- 1 1: TVPA_D6
- 2 2: TVPA_D7
- 3 3: I2C_SCL
- 4 4: I2C_SDA_A
- 5 5: TVPA_SCLK
- 6 6: __NOCONNECT
- 7 7: __NOCONNECT
- 8 8: TVPA_D0
- 9 9: TVPA_D1
- 10 10: __NOCONNECT
- 11 11: TVPA_D2
- 12 12: TVPA_D3
- 13 13: TVPA_D4
- 14 14: TVPA_D5
- 15 15: __NOCONNECT
- 16 16: __NOCONNECT
- 17 17: __NOCONNECT
- 18 18: TVP_RESETB
- 19 19: __NOCONNECT
- 20 20: GND

## J3 PinHeader_1x20
_Mirror of Tang Nano 20K J5: connect pin n to J5-n_

- 1 1: +5V_TANG
- 2 2: GND
- 3 3: TVPB_D0
- 4 4: TVPB_SCLK
- 5 5: TVPB_D1
- 6 6: TVPB_D2
- 7 7: __NOCONNECT
- 8 8: __NOCONNECT
- 9 9: I2C_SDA_B
- 10 10: TVPB_D3
- 11 11: __NOCONNECT
- 12 12: TVPB_D4
- 13 13: TVPB_D5
- 14 14: TVPB_D6
- 15 15: GND
- 16 16: __NOCONNECT
- 17 17: TVPB_D7
- 18 18: __NOCONNECT
- 19 19: __NOCONNECT
- 20 20: __NOCONNECT

## J4 VIDEO_IN_A
_Receiver A: 1 = +5 V out (fused), 2 = GND, 3 = CVBS_

- 1 1: +5V_RX_A
- 2 2: GND
- 3 3: CVBS_A

## J5 VIDEO_IN_B
_Receiver B: 1 = +5 V out (fused), 2 = GND, 3 = CVBS_

- 1 1: +5V_RX_B
- 2 2: GND
- 3 3: CVBS_B

## JP1 SolderJumper_2_Open
_Close to join SDA_A/SDA_B into one bus (then set decoder B to BAh, see R I2CSEL)_

- 1 1: I2C_SDA_A
- 2 2: I2C_SDA_B

## JP2 SolderJumper_2_Bridged
_5 V from Tang Nano 20K J5-1 (closed by default); open when powering from J1_

- 1 1: +5V_TANG
- 2 2: +5V

## L1 0.47uH
_AAF inductor (A): 0603, SRF > 100 MHz, DCR < 0.5 ohm; or 0 ohm to bypass_

- 1 1: CVBS_DIV_A
- 2 2: CVBS_AAF_A

## L2 0.47uH
_AAF inductor (B): 0603, SRF > 100 MHz, DCR < 0.5 ohm; or 0 ohm to bypass_

- 1 1: CVBS_DIV_B
- 2 2: CVBS_AAF_B

## R1 4.7k
_I2C SCL pull-up_

- 1 1: I2C_SCL
- 2 2: +3V3

## R10 33
_series termination A D1_

- 1 1: A_YOUT1_U
- 2 2: TVPA_D1

## R11 33
_series termination A D2_

- 1 1: A_YOUT2_U
- 2 2: TVPA_D2

## R12 33
_series termination A D3_

- 1 1: A_YOUT3_U
- 2 2: TVPA_D3

## R13 33
_series termination A D4_

- 1 1: A_YOUT4_U
- 2 2: TVPA_D4

## R14 33
_series termination A D5_

- 1 1: A_YOUT5_U
- 2 2: TVPA_D5

## R15 33
_series termination A D6_

- 1 1: A_YOUT6_U
- 2 2: TVPA_D6

## R16 33
_series termination A D7_

- 1 1: A_YOUT7_I2CSEL_U
- 2 2: TVPA_D7

## R17 10k
_I2CSEL low = B8h (A)_

- 1 1: A_YOUT7_I2CSEL_U
- 2 2: GND

## R18 DNP 10k
_fit instead of the pull-down for BAh (A)_

- 1 1: A_YOUT7_I2CSEL_U
- 2 2: +3V3

## R19 33
_series termination A SCLK_

- 1 1: A_SCLK_U
- 2 2: TVPA_SCLK

## R2 4.7k
_I2C SDA pull-up_

- 1 1: I2C_SDA_A
- 2 2: +3V3

## R20 37.4
_fig. 6-1 R1/R5: series half of the 2x37.4 ohm termination (B); 47 ohm = hot-video alternative (SLEU044)_

- 1 1: CVBS_B
- 2 2: CVBS_DIV_B

## R21 37.4
_fig. 6-1 R2/R6: shunt half (B); 27 ohm = hot-video alternative (SLEU044)_

- 1 1: CVBS_DIV_B
- 2 2: GND

## R22 100k
_parallel resistor across crystal (B, fig. 6-1 note E)_

- 1 1: XTAL1_B
- 2 2: XTAL2_B

## R23 10k
_PDN high = always on (B, fig. 6-1 note C)_

- 1 1: PDN_B
- 2 2: +3V3

## R24 10k
_pin 27 must not float; 10 k pull-down while the output is disabled (B, note H)_

- 1 1: INTREQ_B
- 2 2: GND

## R25 33
_series termination B D0_

- 1 1: B_YOUT0_U
- 2 2: TVPB_D0

## R26 33
_series termination B D1_

- 1 1: B_YOUT1_U
- 2 2: TVPB_D1

## R27 33
_series termination B D2_

- 1 1: B_YOUT2_U
- 2 2: TVPB_D2

## R28 33
_series termination B D3_

- 1 1: B_YOUT3_U
- 2 2: TVPB_D3

## R29 33
_series termination B D4_

- 1 1: B_YOUT4_U
- 2 2: TVPB_D4

## R3 4.7k
_I2C SDA pull-up_

- 1 1: I2C_SDA_B
- 2 2: +3V3

## R30 33
_series termination B D5_

- 1 1: B_YOUT5_U
- 2 2: TVPB_D5

## R31 33
_series termination B D6_

- 1 1: B_YOUT6_U
- 2 2: TVPB_D6

## R32 33
_series termination B D7_

- 1 1: B_YOUT7_I2CSEL_U
- 2 2: TVPB_D7

## R33 10k
_I2CSEL low = B8h (B)_

- 1 1: B_YOUT7_I2CSEL_U
- 2 2: GND

## R34 DNP 10k
_fit instead of the pull-down for BAh (B)_

- 1 1: B_YOUT7_I2CSEL_U
- 2 2: +3V3

## R35 33
_series termination B SCLK_

- 1 1: B_SCLK_U
- 2 2: TVPB_SCLK

## R4 37.4
_fig. 6-1 R1/R5: series half of the 2x37.4 ohm termination (A); 47 ohm = hot-video alternative (SLEU044)_

- 1 1: CVBS_A
- 2 2: CVBS_DIV_A

## R5 37.4
_fig. 6-1 R2/R6: shunt half (A); 27 ohm = hot-video alternative (SLEU044)_

- 1 1: CVBS_DIV_A
- 2 2: GND

## R6 100k
_parallel resistor across crystal (A, fig. 6-1 note E)_

- 1 1: XTAL1_A
- 2 2: XTAL2_A

## R7 10k
_PDN high = always on (A, fig. 6-1 note C)_

- 1 1: PDN_A
- 2 2: +3V3

## R8 10k
_pin 27 must not float; 10 k pull-down while the output is disabled (A, note H)_

- 1 1: INTREQ_A
- 2 2: GND

## R9 33
_series termination A D0_

- 1 1: A_YOUT0_U
- 2 2: TVPA_D0

## TP1 TestPoint

- 1 1: CVBS_A

## TP10 TestPoint

- 1 1: VSYNC_PALI_B

## TP11 TestPoint

- 1 1: HSYNC_B

## TP12 TestPoint

- 1 1: AVID_B

## TP13 TestPoint

- 1 1: TVPB_SCLK

## TP14 TestPoint_GND
_GND pad next to header J3 (SCLK B): probe ground for the 27 MHz clock_

- 1 1: GND

## TP2 TestPoint

- 1 1: FID_GLCO_A

## TP3 TestPoint

- 1 1: VSYNC_PALI_A

## TP4 TestPoint

- 1 1: HSYNC_A

## TP5 TestPoint

- 1 1: AVID_A

## TP6 TestPoint

- 1 1: TVPA_SCLK

## TP7 TestPoint_GND
_GND pad next to header J2 (SCLK A): probe ground for the 27 MHz clock_

- 1 1: GND

## TP8 TestPoint

- 1 1: CVBS_B

## TP9 TestPoint

- 1 1: FID_GLCO_B

## U1 AP7361C-33E-13
_LCSC C500795. 5 V -> 3.3 V for TVP IO_DVDD, pull-ups and both 1.8 V LDOs (~170 mA: 0.29 W, +32 C at 110 C/W)_

- 1 VIN: +5V
- 2 GND: GND
- 3 VOUT: +3V3

## U2 AP2112K-1.8TRG1
_LCSC C176944. 3.3 V -> 1.8 V digital (2x DVDD), ~66 mA max (0.12 W)_

- 1 VIN: +3V3
- 2 GND: GND
- 3 EN: +3V3
- 4 NC: —
- 5 VOUT: +1V8_D

## U3 AP2112K-1.8TRG1
_LCSC C176944. 3.3 V -> 1.8 V analog (2x CH_AVDD + PLL_AVDD), ~78 mA max (0.12 W)_

- 1 VIN: +3V3
- 2 GND: GND
- 3 EN: +3V3
- 4 NC: —
- 5 VOUT: +1V8_A

## U4 TVP5150AM1IPBSR
_TI TVP5150AM1IPBSR, industrial grade -40..85 C; LCSC C10013 is the commercial-grade code and has NOT been checked for this grade (Other Suppliers, per design/REV_A_KONCEPT.md); decoder A_

- 1 AIP1A: AIP1A_A
- 2 AIP1B: AIP1B_A
- 3 PLL_AGND: GND
- 4 PLL_AVDD: PLL_AVDD_A
- 5 XTAL1: XTAL1_A
- 6 XTAL2: XTAL2_A
- 7 AGND: GND
- 8 RESETB: TVP_RESETB
- 9 SCLK: A_SCLK_U
- 10 IO_DVDD: +3V3
- 11 YOUT7_I2CSEL: A_YOUT7_I2CSEL_U
- 12 YOUT6: A_YOUT6_U
- 13 YOUT5: A_YOUT5_U
- 14 YOUT4: A_YOUT4_U
- 15 YOUT3: A_YOUT3_U
- 16 YOUT2: A_YOUT2_U
- 17 YOUT1: A_YOUT1_U
- 18 YOUT0: A_YOUT0_U
- 19 DGND: GND
- 20 DVDD: +1V8_D
- 21 SCL: I2C_SCL
- 22 SDA: I2C_SDA_A
- 23 FID_GLCO: FID_GLCO_A
- 24 VSYNC_PALI: VSYNC_PALI_A
- 25 HSYNC: HSYNC_A
- 26 AVID: AVID_A
- 27 INTREQ_GPCL_VBLK: INTREQ_A
- 28 PDN: PDN_A
- 29 REFP: REFP_A
- 30 REFM: REFM_A
- 31 CH_AGND: GND
- 32 CH_AVDD: AVDD_A

## U5 TVP5150AM1IPBSR
_TI TVP5150AM1IPBSR, industrial grade -40..85 C; LCSC C10013 is the commercial-grade code and has NOT been checked for this grade (Other Suppliers, per design/REV_A_KONCEPT.md); decoder B_

- 1 AIP1A: AIP1A_B
- 2 AIP1B: AIP1B_B
- 3 PLL_AGND: GND
- 4 PLL_AVDD: PLL_AVDD_B
- 5 XTAL1: XTAL1_B
- 6 XTAL2: XTAL2_B
- 7 AGND: GND
- 8 RESETB: TVP_RESETB
- 9 SCLK: B_SCLK_U
- 10 IO_DVDD: +3V3
- 11 YOUT7_I2CSEL: B_YOUT7_I2CSEL_U
- 12 YOUT6: B_YOUT6_U
- 13 YOUT5: B_YOUT5_U
- 14 YOUT4: B_YOUT4_U
- 15 YOUT3: B_YOUT3_U
- 16 YOUT2: B_YOUT2_U
- 17 YOUT1: B_YOUT1_U
- 18 YOUT0: B_YOUT0_U
- 19 DGND: GND
- 20 DVDD: +1V8_D
- 21 SCL: I2C_SCL
- 22 SDA: I2C_SDA_B
- 23 FID_GLCO: FID_GLCO_B
- 24 VSYNC_PALI: VSYNC_PALI_B
- 25 HSYNC: HSYNC_B
- 26 AVID: AVID_B
- 27 INTREQ_GPCL_VBLK: INTREQ_B
- 28 PDN: PDN_B
- 29 REFP: REFP_B
- 30 REFM: REFM_B
- 31 CH_AGND: GND
- 32 CH_AVDD: AVDD_B

## Y1 X32251431818MSB4SI
_YXC 14.31818 MHz, CL 20 pF, +-10 ppm at 25 C / +-20 ppm over -40..85 C, SMD3225-4P (TVP needs +-50 ppm); LCSC C34748. CL1 = CL2 = 2*CL - Cstray = 40 - ~5 -> 33 pF (section 3.16)_

- 1 1: XTAL1_A
- 2 GND: GND
- 3 3: XTAL2_A
- 4 GND2: GND

## Y2 X32251431818MSB4SI
_YXC 14.31818 MHz, CL 20 pF, +-10 ppm at 25 C / +-20 ppm over -40..85 C, SMD3225-4P (TVP needs +-50 ppm); LCSC C34748. CL1 = CL2 = 2*CL - Cstray = 40 - ~5 -> 33 pF (section 3.16)_

- 1 1: XTAL1_B
- 2 GND: GND
- 3 3: XTAL2_B
- 4 GND2: GND
