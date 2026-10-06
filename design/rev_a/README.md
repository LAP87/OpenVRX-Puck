# Rev A — dekoderkort (2× TVP5150AM1)

Status 2026-10-02: **schema som kod klart, ERC rent, inga komponenter valda till fullo, ingen layout, inget beställt.**

Varför ett dekoderkort och inte hela goggle-elektroniken: se `../../research/ALTERNATIVA_VAGAR_2026-10-02.md`. Dekoderdelen är gemensam för alla vägar med egen mixning. FPGA (GW2AR-18 eller GW5A-25) och HDMI-lösning (LT8618SX, ADV7513 eller direkt TMDS) väljs först när de är provade på devkort. Det här kortet fungerar med Tang Nano 20K i dag och med andra FPGA-kort via sladdar.

## Vad kortet gör

```
mottagare A ─ CVBS ─┐ ESD → 2×37,4 Ω (75 Ω term., ÷2) → [AAF-plats] → 0,1 µF → TVP5150AM1 #A ─ BT.656 + SCLK ─┐
mottagare B ─ CVBS ─┘                    (samma)                              TVP5150AM1 #B ─ BT.656 + SCLK ─┤
                                         egen 14,31818 MHz-kristall per dekoder                              ├─ 2× 1×20 stiftlist
5 V (från Tang J5-1 via lödbygel, eller egen kontakt) → 3,3 V LDO → 2× 1,8 V LDO (digital / analog via ferrit) ┘   = Tang Nano 20K J6 / J5
```

- **Stiftlisterna är numrerade som Tang Nano 20K:s J6 och J5.** Koppla stift n till stift n (flatkabel eller dupont), så får du exakt M4-bitströmmens stift (`gateware/boards/m4_dual_mix.cst`). Skriptet kontrollerar det automatiskt.
- Mottagarkontakterna (JST-PH 3-pol: +5 V, GND, CVBS) matar varsin mottagare via en 0,5 A PTC-säkring.
- I2C: gemensam SCL, en SDA per dekoder (båda på B8h, som M4 förväntar sig). Med lödbygel JP1 och en flyttad pull-up kan de i stället dela en buss (B8h + BAh).
- RESETB från FPGA:n på J6-18 (Tang-stift 18, som också driver kortets lysdiod 3). Ingen pull-down: lysdiodens 510 Ω mot 3,3 V skulle vinna ändå, och dekoderns utgångar är avstängda efter start tills register 03h skrivs. Tidigare låg RESETB på J6-10 (stift 25), som ligger i HDMI-banken och är skärmens CEC-ledning (Puck issue #1, Core issue #6).
- Testpunkter: CVBS, SCLK och de separata synksignalerna (HSYNC/VSYNC/AVID/FID) per dekoder.

## Filer

| Fil | Innehåll |
|---|---|
| `dekoderkort.py` | Schemat (SKiDL). Kör: `.venv/bin/python design/rev_a/dekoderkort.py` |
| `out/dekoderkort.net` | KiCad-netlista (importera i Pcbnew när footprints är kontrollerade) |
| `out/dekoderkort_bom.csv` | Stycklista grupperad per värde/footprint |
| `out/dekoderkort_kopplingar.md` | Läsbar lista: varje dels stift → nät |
| `review/` | Underlag för extern granskning (databladsutdrag + uppdrag) |

## Kontroller som körs varje gång

1. **SKiDL ERC**: inga fel och inga varningar (medvetet oanslutna stift är markerade NC).
2. **Databladsregler** (`design_checks`): alla 32 TVP-stift anslutna, rätt matning per stift (IO_DVDD 3,3 V, DVDD 1,8 V digital, CH_AVDD/PLL_AVDD 1,8 V bakom egna ferriter), ingen 3,3 V/5 V-del på XTAL1-näten, exakt en pull-up per I2C-linje.
3. **Mot gateware**: varje signal på stiftlisterna jämförs med FPGA-stiften i `m4_dual_mix.cst` via Tang Nano 20K:s stiftlistetabell. Kontrollen är provad genom att byta plats på två datastift — då fallerar den med rätt meddelande.

## Granskning

- Extern granskning via A0 (DeepSeek V4 Pro) gick inte: **A0-kvoten var slut** (`quota_exhausted` i ledgern 2026-10-02). Efter projektägarens godkännande kördes granskningen i stället med **Nemotron 3 Ultra (gratis, OpenCode Zen)**. Körningen gjordes i en isolerad mapp med bara de tre filerna i `review/`, i läsläge (agent `plan`). Resultat: `review/review_nemotron3ultra_opencode.md`.
  - **Inga fel.** Alla 32 stift, matningar, kristallkrets, ingångskedja och styrstift fick OK.
  - Varningar, alla redan öppna punkter: antialiasfiltret (nu en platshållare, 0 Ω + ej monterad C; TI: "highly recommended"), ESD-diodens modell och kristallens lastkondensatorer.
  - Not om stift 27: 10 k pull-down gäller så länge INTREQ är avstängt. Vår `tvp_ctrl` skriver 03h = 0Dh (bit 5 = 0, avstängt), så det stämmer. Skulle INTREQ användas som aktivt låg interrupt krävs pull-up i stället (figur 6-1 not I).
  - Modellens svar är obekräftad text. Varje punkt ovan är kontrollerad mot databladsutdraget av mig.
- Egen genomgång mot SLES209E tabell 2-1, avsnitt 3.16/3.18 och figur 6-1: inga avvikelser. Saker att bevaka vid komponentval:
  - **XTAL1 tål max 2,3 V** (absoluta maxvärden), VIH = 0,7 × PLL_AVDD. Därför en kristall per dekoder. Idén i `../REV_A_KONCEPT.md` med en gemensam oscillator fungerar bara med en **1,8 V**-oscillator, aldrig med en vanlig på 3,3 V.
  - ~~AMS1117 kräver ESR~~ → bytt till LDO:er som är stabila med keramiska kondensatorer (se Komponentval).
  - Kristallens lastkondensatorer: CL1 = CL2 = 2·CL − C_stray (TI 3.16) → 33 pF för vald kristall (CL 20 pF).
  - TVP:ns utgångar driver bara 2 mA (SCLK 4 mA). Kabeln till FPGA-kortet ska därför vara kort, och 33 Ω-serieresistorerna sitter vid TVP:n.

## Komponentval (2026-10-02)

| Funktion | Del | LCSC | Varför |
|---|---|---|---|
| 5 V → 3,3 V | Diodes **AP7361C-33E-13**, SOT-223 | C500795 | Stabil med keramiska kondensatorer (≥ 2,2 µF). 0,29 W vid ~170 mA ger +32 °C (θJA 110 °C/W). **Stiftning 1 = IN, 2 = GND, 3 = OUT**, inte AMS1117-ordningen. |
| 3,3 V → 1,8 V ×2 (digital / analog) | Diodes **AP2112K-1.8TRG1**, SOT-23-5 | C176944 | 1 µF keramisk räcker. 0,12 W styck. Stiftning 1 = VIN, 2 = GND, 3 = EN (till VIN), 5 = VOUT. |
| ESD på videoingångarna | onsemi **ESD9B5.0ST5G**, SOD-923, bidirektionell | C111566 | AC-kopplade mottagarutgångar går under 0 V. ~15 pF ger en pol vid ~280 MHz, ingen påverkan på video. |
| Antialiasfilter | **0,47 µH** (0603, SRF > 100 MHz) i serie + **1 nF C0G** mot jord | att välja | Se nedan. |
| Kristall | YXC **X32251431818MSB4SI**, 14,31818 MHz, CL 20 pF, ±10 ppm (±20 ppm över −40…85 °C), SMD3225 | C34748 | TVP kräver ±50 ppm. |
| Lastkondensatorer | **33 pF C0G** ×2 per kristall | basic | CL1 = CL2 = 2·20 pF − ~5 pF strökapacitans ≈ 35 pF. Trimmas efter uppmätt SCLK om det behövs. |
| TVP5150AM1 | TVP5150AM1PBSR | C10013 | "Other Suppliers"; hur JLC hanterar dem är okontrollerat. |

Alternativ som noterats: LCSC har en 14,31818 MHz-oscillator för **1,8 V** (C16851, CTS, ±25 ppm). Den gör en gemensam klocka till båda XTAL1 säker, om det någon gång behövs.

Datablad för LDO:erna: se tillverkarnas webbplatser (Diodes Inc.); de ingår inte i repot.

### Antialiasfiltret, räknat

Mottagarens utgång (75 Ω) och spänningsdelaren 2 × 37,4 Ω ger filtret en källa på ≈ 28 Ω. En LC på 0,47 µH / 1 nF (andra ordningen) ger f0 7,3 MHz och Q 0,77:

| Frekvens | Dämpning |
|---|---|
| 4,2 MHz (lumabandbredd) | 0,0 dB |
| 6 MHz | −1,0 dB |
| 13,5 MHz (halva samplingstakten 27 MHz) | −10,6 dB |
| 27 MHz | −22,6 dB |

Färgbärvågen (3,58/4,43 MHz) påverkas inte. En mottagare med nästan 0 Ω utgång ger högst +2,1 dB överslängning, mot 0,1 dB med 75 Ω. Ett 0 Ω-motstånd på spolens plats kopplar förbi filtret.

## Livscykel

Alla delar med tillverkarnummer kontrollerades 2026-10-04: [LIFECYCLE.md](LIFECYCLE.md). Alla är aktiva. Risken är TVP5150AM1, som TI inte längre utvecklar något nytt för.

## Kontroller (tillägg)

- Regulatorernas in- och utgångar kontrolleras mot rätt matningsnät. Provat med en avsiktligt felvänd 3,3 V-regulator, och kontrollen slår larm. (Kontrollen gäller näten; att stiftnumren i deldefinitionen följer databladet är kontrollerat manuellt mot DS37274 och AP2112-databladet.)

## Öppna punkter

- LCSC-nummer för kristall och spole, PTC-säkring och kontaktvarianter.
- Layout: analog jord och retur nära ingången, kristall och REFP/REFM tätt intill respektive TVP, 0,1 µF vid varje matningsstift. Mekaniskt mått för att sätta kortet direkt på Tang Nano 20K som en "sköld" (båda stiftlisterna) är inte kontrollerat — därför sladdar i rev A.
- KiCad är inte installerat på datorn; netlistan har inte importerats ännu.
