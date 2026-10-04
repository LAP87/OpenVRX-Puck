# Rev A: komponenternas livscykel

Kontrollerad 2026-10-04 mot tillverkarnas sidor, Digi-Key och LCSC. Gör om kontrollen innan kort beställs.

| Del | Tillverkare | Status | Anmärkning |
|---|---|---|---|
| TVP5150AM1PBSR (U4, U5) | Texas Instruments | **Active**, med förbehåll | TI: "does not have ongoing design support from TI for new projects". Ingen PCN eller sista-köpdatum hittad. Kretsen hela rev A vilar på. |
| AP7361C-33E-13 (U1) | Diodes Inc. | Active | |
| AP2112K-1.8TRG1 (U2, U3) | Diodes Inc. | Active | Pinkompatibla kopior finns från andra tillverkare; behövs inte nu. |
| ESD9B5.0ST5G (D1, D2) | onsemi | Active | SZ-varianten (fordonsklassad) är också Active. |
| BLM18KG601SN1D (FB1–FB4) | Murata | Active | BOM:en saknade förpackningssuffixet `D`; rättat. |
| X32251431818MSB4SI (Y1, Y2) | YXC | Säljs (YXC publicerar ingen livscykel) | ±10 ppm vid 25 °C, ±20 ppm över −40…85 °C; TVP kräver ±50 ppm. Likvärdig YXC-del finns om den tar slut. LCSC-numret var inte ifyllt; rättat. |

Övrigt är generiska delar (motstånd, kondensatorer, PTC-säkringar, 0,47 µH-spolar, stiftlister, JST PH) som finns från många tillverkare.

## Risk: TVP5150AM1

Statusen är Active, men TI utvecklar inget nytt för kretsen. Det brukar komma före NRND och sista köp. Åtgärder:

- Köp några kretsar extra när den första kortomgången beställs.
- Bevaka TI:s produktsida och PCN-flöde för TVP5150AM1.
- Reserv: ADV7180 (Analog Devices) är en kandidat. Den kräver ny design, med annan stiftning och andra register, och dess egen livscykel är inte kontrollerad här. Se OpenVRX-navet, `research/DEKODRAR_KUNSKAPSUNDERLAG_2026-09-30.md`. Gatewarens BT.656-väg fungerar oförändrad. Det som behöver bytas är I2C-uppstarten (`tvp_ctrl.v`) och kortet.

Källor: [TI TVP5150AM1](https://www.ti.com/product/TVP5150AM1), [Digi-Key TVP5150AM1PBSR](https://www.digikey.com/en/products/detail/texas-instruments/TVP5150AM1PBSR/657835), [Digi-Key AP7361C-33E-13](https://www.digikey.com/en/products/detail/diodes-incorporated/AP7361C-33E-13/5638317), [Digi-Key AP2112K-1.8TRG1](https://www.digikey.com/en/products/detail/diodes-incorporated/AP2112K-1-8TRG1/4470745), [onsemi ESD9B](https://www.onsemi.com/products/discrete-power-modules/esd-protection-diodes/esd9b), [Digi-Key BLM18KG601SN1D](https://www.digikey.com/en/products/detail/murata-electronics/BLM18KG601SN1D/1982766), [YXC YSX321SL](https://www.yxcxtal.com/product/ysx321sl.html).
