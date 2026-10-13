# Rev A — dekoderkort (2× TVP5150AM1)

Status 2026-10-05: **schema som kod, ERC rent, ingen layout, inget hårdvaruprov.** RESETB ligger på J6-18; genererade utdata och Core-submodulen ska följa samma version. Det här är ett konstruktionsunderlag, inte ett tillverkningsgodkännande.

Varför ett dekoderkort och inte hela goggle-elektroniken: se [navets vägval](https://github.com/LAP87/OpenVRX/blob/main/research/ALTERNATIVA_VAGAR_2026-10-02.md). Dekoderdelen är gemensam för vägar med egen mixning. Kopplingen är avsedd för Tang Nano 20K rev 3923 och andra FPGA-kort via korta ledningar; faktisk funktion och signalintegritet är ännu inte provade.

## Vad kortet gör

```
mottagare A ─ CVBS ─┐ ESD → 2×37,4 Ω (75 Ω term., ÷2) → [AAF-plats] → 0,1 µF → TVP5150AM1 #A ─ BT.656 + SCLK ─┐
mottagare B ─ CVBS ─┘                    (samma)                              TVP5150AM1 #B ─ BT.656 + SCLK ─┤
                                         egen 14,31818 MHz-kristall per dekoder                              ├─ 2× 1×20 stiftlist
5 V (från Tang J5-1 via lödbygel, eller egen kontakt) → 3,3 V LDO → 2× 1,8 V LDO (digital / analog via ferrit) ┘   = Tang Nano 20K J6 / J5
```

- **Stiftlisterna är numrerade som Tang Nano 20K:s J6 och J5.** Stift n till stift n ger signalplanen för M3/M4/M6 (`../../core/gateware/boards/`). Skriptet kontrollerar hela dekoderkartan för varje topp, både stiftnummer och RESETB/SPI-funktion; kortrevision och kabeldragning kontrolleras på bänken.
- Mottagarkontakterna (JST-PH 4-pol: +5 V, GND, CVBS, RSSI; till 2026-10-13 3-pol utan RSSI) matar varsin mottagare via en PTC-säkring med minst 0,75 A *hold*-ström (inte trip). Mottagaren drar ca 0,45 A; en 0,5 A-del klarar enligt Bourns MF-NSMF-kurvan bara ca 0,44 A vid 40 °C och 0,35 A vid 60 °C. Serien och 1206-footprinten är ännu inte kontrollerade.
- I2C: gemensam SCL och separat SDA per dekoder är standardkopplingen: JP1 öppen, båda YOUT7/I2CSEL-strappade till 7-bitarsadress 5Ch (8-bitars skrivadress B8h). De nuvarande M3/M4/M6-bitströmmarna använder `SPLIT_SDA=1` och adresserna 5Ch/5Ch. Att stänga JP1 och strappa B till 5Dh (BAh) stöds inte av dessa bitströmmar; det kräver en separat verifierad tvåadresskonfiguration. Adressbytet ensamt räcker inte.
- **Två ESD-klampar per videoingång** (2026-10-13, Puck #3, ägarens beslut A): ESD9B5.0 vid kontakten som förut, och en ESD9B3.3 efter spänningsdelaren vid dekoderns ingångsnät. Den första klampar vid 12,5–15 V för en 8 kV-puls och delaren halverar, så 6–7 V skulle nå kopplingskondensatorn framför en ingång som tål 2,0 V; den andra tar större delen av energin intill dekodern och halverar toppen igen. Det är inte ett fullständigt skydd: TI:s referenskoppling har ingen klamp här, och resten av pulsen tas av AAF-spolen och dekoderns egna dioder. Omonterad (DNP) går den att jämföra på bänken. ~15 pF vid ett 18-ohmsnät påverkar inte videon.
- RESETB från FPGA:n på J6-18 (Tang-stift 18, som också driver kortets lysdiod 3). Lysdiodens 510 Ω mot 3,3 V innebär att RESETB inte hålls låg före FPGA-konfiguration. TVP-utgångarna är odefinierade tills en resetpuls har givits; nuvarande `tvp_ctrl` väntar 20 ms efter konfiguration, håller RESETB låg i 2 ms och lämnar sedan YOUT avstängda tills register 03h skrivs. Se [Core bring-up, avsnitt 5](../../core/gateware/BRINGUP.md#5-delade-stift-på-tang-nano-20k-rev-3923). Tidigare låg RESETB på J6-10 (stift 25), som ligger i HDMI-banken och är skärmens CEC-ledning (Puck issue #1, Core issue #6).
- RSSI från båda mottagarna till en I2C-ADC på dekoder A:s buss, se "RSSI" nedan.
- Testpunkter: CVBS, RSSI, SCLK och de separata synksignalerna (HSYNC/VSYNC/AVID/FID) per dekoder. Dessutom en jordpad vid vardera stiftlist (TP för GND), nära SCLK-stiftet: en mätprobs jordfjäder eller en kort returtråd där ger liten slinga när 27 MHz-klockan mäts.

## RSSI (tillagt 2026-10-13)

Ägarens beslut 2026-10-13 (navets `docs/BESLUT_2026-10-12.md`, punkt 7): en I2C-ADC på rev A. Tang Nano 20K har ingen ADC, och mixern ser i dag fading först när raderna redan är förstörda. Lärdomarna från rx5808-pro-diversity och FENIX står i navets `research/RX5808_PRO_DIVERSITY_2026-10-13.md`.

```
mottagare A, stift 4 ─┬─ 100 kΩ ─ GND        ┌─ AIN0
                      └─ 10 kΩ ─┬────────────┤
                                 0,1 µF      │  ADS1115 (48h) ── SDA_A, SCL (dekoder A:s buss)
mottagare B, stift 4  (samma) ───────────────┴─ AIN1         AIN2/AIN3 till GND, ALERT/RDY öppen
```

- **Krets:** TI ADS1115IDGSR, 16 bitar, 8–860 SPS, VSSOP-10. Den har fyra ingångar; två används. Stiftning, adress och regler för oanvända stift är kontrollerade mot TI SBAS444E (tabell 4-1, tabell 7-2, avsnitt 9.1.4). Databladet ingår inte i repot.
- **Adress 48h** (ADDR till GND). Bussarna har redan dekodrarna på 5Ch eller 5Dh och OLED:en på 3Ch; ADS1115 kan bara ha 48h–4Bh, så ingen strappning krockar. `rssi_checks` i skriptet kontrollerar det.
- **Matning 3,3 V**, som I2C-pull-upparna, med 0,1 µF vid VDD. Ingångarna tål GND − 0,3 V till VDD + 0,3 V.
- **Filtret:** 100 kΩ pull-down vid kontakten ger 0 V utan mottagare (samma värde som FENIX). 10 kΩ och 0,1 µF ger τ = 1 ms: en fading syns inom samma fält, och radfrekvensens rippel (15,7 kHz) dämpas cirka 40 dB. 10 kΩ begränsar också strömmen in i ADC:ns skyddsdioder till under 0,2 mA om RSSI skulle nå 5 V.
- **Fälttakt räcker nu.** Core läser båda kanalerna en gång per fält (50–60 Hz; uppgift 14 i navets arbetsplan). Det räcker för tidig varning till mixern, kanalscanning och loggen. Vid 475 SPS tar två omvandlingar cirka 4 ms av fältets 17–20 ms.
- **Radtakt är rev B.** RSSI för varje rad, som FENIX använder för antennbyte, kräver minst 15–30 kSPS. Det betyder en SPI-ADC eller en FPGA med inbyggd ADC, inte en I2C-krets.
- **Kalibrering:** inga två RX5808 har samma RSSI-omfång. Core sparar min och max per mottagare (uppgift 14 och 15). Testpunkten på RSSI-nätet gör det möjligt att jämföra ADC-värdet med en multimeter.
- **Inte kontrollerat:** RSSI-stiftets spänningsomfång och utgångsimpedans hos de mottagare som ska användas, och om de har ett RSSI-stift som går att nå. Mät det innan ADC:ns mätområde väljs i Core.

## Filer

| Fil | Innehåll |
|---|---|
| `dekoderkort.py` | Schemat (SKiDL). Kör: `.venv/bin/python design/rev_a/dekoderkort.py` |
| `out/dekoderkort.net` | KiCad-netlista (importera i Pcbnew när footprints är kontrollerade) |
| `out/dekoderkort_bom.csv` | Stycklista grupperad per värde/footprint |
| `out/dekoderkort_kopplingar.md` | Läsbar lista: varje dels stift → nät |
| `review/` | Underlag för extern granskning (databladsutdrag + uppdrag) |
| `LAYOUT.md` | Underlag för layouten: mått och sandwich mot Tang Nano 20K, lagerstack, placering per block, ledningsregler, jord, värme, mekanik (2026-10-13) |

## Kontroller som körs varje gång

1. **SKiDL ERC**: inga fel och inga varningar (medvetet oanslutna stift är markerade NC).
2. **Databladsregler** (`design_checks`): RSSI-ADC:n på dekoder A:s buss med en ledig adress, 3,3 V och filter plus pull-down på varje RSSI-ingång (`rssi_checks`, med negativa kontroller i testet: fel SDA, 5 V, ombytta ingångar, adresskrock, ingen pull-down, ingen filterkondensator); alla 32 TVP-stift anslutna, rätt matning per stift (IO_DVDD 3,3 V, DVDD 1,8 V digital, CH_AVDD/PLL_AVDD 1,8 V bakom egna ferriter), ingen 3,3 V/5 V-del på XTAL1-näten, exakt en pull-up per I2C-linje.
3. **Mot gateware**: varje dekodersignal på stiftlisterna jämförs separat med FPGA-stiften i `m3_probe.cst`, `m4_dual_mix.cst` och `m6_puck_proto.cst`. Saknade, dubbla eller kolliderande relevanta stiftbegränsningar avvisas. Core kräver dessutom entydig direkt RESETB/SPI-tilldelning till LED3/4/5 i M3/M4/M6. Negativa kontroller lämnar RESETB oansluten, byter D0/D1 på M3/M6, flyttar båda klockor och alla I2C-signaler på varje topp, tar bort/dubblerar stiftbegränsningar och tar bort kontraktskontrollen. Alla avvisas. En äldre Core utan kontraktet kan inte godkännas genom enbart stiftnummer.

Vid regel- eller ERC-fel avslutas scriptet före netlista/BOM/kopplingsrapport skrivs över. Del- och nättaggar är stabila mellan körningar; netlistans genereringsdatum kan ändras. Regression: `.venv/bin/python -m pytest -q tests` från Pucks rot.

Utdata: 126 delar, 87 anslutna nät (124 före den andra ESD-klampen 2026-10-13; 114 och 83 före RSSI). Två körningar gav samma innehåll när genereringsdatumet normaliserades. Netlisteloggen har separata varningar om saknade KiCad-footprintbibliotek och den tomma rot-tagg som KiCad kräver; inga slumpmässiga del-/nättaggar genereras. ERC-resultatet verifierar därför inte footprints eller layout.

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
| RSSI-ADC | TI **ADS1115IDGSR**, VSSOP-10 | — | Två av fyra ingångar, 48h, 3,3 V. Se "RSSI". |
| TVP5150AM1 | TVP5150AM1**I**PBSR (industriklass, −40…85 °C) | — | Bytt från handelsklassen PBSR (0…70 °C) i Puck #3: kortet sitter i ett slutet hus bredvid två mottagare och ett FPGA-kort. C10013 gäller handelsklassen och är inte kontrollerat för I-klassen; leverantör och lagerstatus okontrollerade. |

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

## Ingångsdelaren, alternativ för starka videonivåer

2 × 37,4 Ω (figur 6-1) är kvar. Om en mottagare ger för hög videonivå kan 47 Ω i serie och 27 Ω mot jord användas (TI SLEU044) på samma 0402-platser. Summan är 74 Ω, en fortfarande rimlig 75 Ω-avslutning, men delningen går från 0,50 till 0,36 (−8,8 dB mot −6 dB). Källimpedansen in i antialiasfiltret sjunker från ca 28 till ca 22 Ω, så filtret bör räknas om om det monteras. Inget av detta är provat.

## PLL-matningen

Varje dekoders PLL_AVDD ligger bakom en egen ferrit och hade bara 0,1 µF efter den. Pärlan är induktiv långt under sina 100 MHz och en liten keramikkondensator har nästan ingen ESR, så de bildar en svagt dämpad LC. Därför finns nu även 4,7 µF efter pärlan (4–10 µF duger), med 0,1 µF kvar vid stiftet. Värdet är en bedömning, inte uppmätt eller simulerat.

## Livscykel

Grundkontrollen är från 2026-10-04. Industrivarianten TVP5150AM1IPBSR kontrollerades hos TI 2026-10-06 och är Active: [LIFECYCLE.md](LIFECYCLE.md). Leverantör och småvolymstillgång för den är fortfarande okontrollerade; hela BOM:en ska kontrolleras igen före kortbeställning.

## Kontroller (tillägg)

- Regulatorernas in- och utgångar kontrolleras mot rätt matningsnät. Provat med en avsiktligt felvänd 3,3 V-regulator, och kontrollen slår larm. (Kontrollen gäller näten; att stiftnumren i deldefinitionen följer databladet är kontrollerat manuellt mot DS37274 och AP2112-databladet.)

## Öppna punkter

- PTC:n är bytt till minst 0,75 A hold (Puck #2); serie, footprint och verkligt strömdrag mot temperatur återstår att kontrollera. ESD-kedja behöver granskas före layout (Puck #2–#3).
- LCSC-nummer för kristall och spole, PTC-säkring och kontaktvarianter.
- Layout: underlaget står i [LAYOUT.md](LAYOUT.md). Måtten för att sätta kortet direkt på Tang Nano 20K (båda stiftlisterna) är inte kontrollerade mot Sipeeds måttritning, och en sandwich kräver kontakter för OLED och RX5808-SPI som schemat saknar (LAYOUT.md, avsnitt 7).
- KiCad är inte installerat på datorn; netlistan har inte importerats ännu.
