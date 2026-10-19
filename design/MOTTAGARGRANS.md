# Gränsen mot mottagardelen

Vad videokärnan (dekoderkortet rev A och Core-gatewaren) kräver av en mottagarmodul, så att RF-delen kan bytas utan att resten görs om. Rådet 2026-10-19 (navets `docs/design/2026-10-19/COUNCIL.md`, P3) bad om just den här gränsen. Allt nedan är läst ur `design/rev_a/dekoderkort.py`, Core `gateware/README.md` och `gateware/boards/m4_dual_mix.cst`; inget är mätt. Där ett värde inte står i våra egna filer står "okänt".

Två gränser finns, och de är olika:

- **A. CVBS före dekodern.** Det rev A har: mottagarkontakten `VIDEO_IN_A` / `VIDEO_IN_B`. En modul som lämnar analog video passar här (RX5808, varje annan analog mottagare, C5VRX som gör CVBS ur ESP32-C5:ans radio).
- **B. BT.656 efter dekodern.** Det Tang Nano 20K får på J6/J5: en digital ström per kanal. En modul med egen videoavkodning (en SDR-väg med FM-demodulering och digital PAL/NTSC-avkodning) skulle lämna detta och hoppa över TVP5150AM1.

## A. CVBS-gränsen: kontakten `VIDEO_IN_x` (JST PH 2,0 mm, 4 stift)

| Stift | Signal | Rev A, så som det är ritat | Krav på en annan modul |
|---|---|---|---|
| 1 | +5 V ut | från kortets 5 V genom en återställbar säkring med minst 0,75 A hållström per mottagare, 10 µF vid kontakten. RX5808-modulen antas dra omkring 0,45 A (not i schemat, ett modulblad; inte mätt) | matas med 5 V, högst omkring 0,6 A i drift (säkringens hållström sjunker med temperaturen, se noten i schemat); egen matning annars |
| 2 | GND | gemensam jord | gemensam jord; kontakten får inte sättas i med modulen matad från en annan jord (klampens begränsning, nedan) |
| 3 | CVBS | ESD-klamp 5 V bidirektionell vid kontakten → 37,4 Ω serie + 37,4 Ω shunt (75 Ω-terminering, nivån halveras) → valfri andra klamp 3,3 V → antialiasfilter 0,47 µH / 1 nF (platt till 4,2 MHz, −1 dB vid 6 MHz; 0 Ω i L-läget kopplar bort det) → 0,1 µF → `AIP1A` på TVP5150AM1 | standard-CVBS: 1 V topp-till-topp i 75 Ω, negativ synk, PAL eller NTSC (dekodern växlar själv, 28h = 00; SECAM maskad). Modulen ska tåla 75 Ω last. Likspänningsnivån spelar ingen roll (AC-koppling), men svängning under 0 V förekommer och klamparna är därför bidirektionella. Starkare video än 1 V: byt delaren till 47/27 Ω (noterat i schemat); nivån som når dekodern får inte överstiga ingångens 2,0 V |
| 4 | RSSI | 100 kΩ till jord, 10 kΩ / 0,1 µF RC-filter, in på ADS1115 (±4,096 V, en avläsning per fält per mottagare, AIN0 = A, AIN1 = B) | en likspänning 0–3,3 V som stiger monotont med mottagen signal. Skalan är egal: menyns CAL mäter min och max per mottagare och räknar om till 0–100 (`rssi_adc.v`, minst 400 koder ≈ 50 mV spann för att räknas som kalibrerad). Utgången ska klara 100 kΩ last och RC-filtrets 10 kΩ. Saknas RSSI: lämna stiftet öppet; kärnan visar `?` och mixern använder inget RSSI-villkor |

**Kanalstyrning** går inte genom dekoderkortet: RX5808-modulernas SPI-stift (CLK = Tang J5-18, DATA = J6-17, SEL = J6-16, 3,3 V-logik) kopplas direkt från Tang-kortet till båda modulerna parallellt (Core `gateware/README.md`, M6). Ramen är 25 bitar LSB först (adress 1, skrivbit, 20 bitars syntesord ur `vtx_channels.vh`); båda mottagarna får alltid samma kanal, 0,5 s efter start, vid kanalbyte och varannan sekund så länge ingen dekoder är låst (`rx5808_tune.v`). En annan modul måste antingen ta samma ram (RTC6715-registret) eller få en egen styrmodul i gatewaren; menyn lämnar bara kanalindex 0–47 och `chan_step`. Modulens status (lås, nivå) läses inte av kärnan; lås kommer från dekodern (TVP 88h/89h över I2C), nivå från RSSI-stiftet.

**Vad kärnan antar om bilden:** två oberoende videoströmmar från två antenner. En färdig diversitymodul med en enda redan vald CVBS-utgång kan matas in på en kanal, men då finns inget för radmixern att välja mellan. Radmixern parar rader på radnummer inom 15,8 µs och väljer per rad på HF-energi; den förutsätter att båda strömmarna kommer från samma sändare.

**Okänt och att mäta på bänken:** RX5808-modulens verkliga videonivå och utimpedans, dess RSSI-spann och strömförbrukning; om 75 Ω-termineringen och delaren ger rätt nivå i dekodern (`MATPROTOKOLL.md` blad om videonivå); klamparnas verkan vid ESD-puls (räkneexemplet i schemat är ett överslag).

## B. BT.656-gränsen: J6/J5 mot Tang Nano 20K

Per kanal: 8 databitar YCbCr 4:2:2 med inbäddade SAV/EAV-koder, en 27 MHz-klocka (`SCLK`, på FPGA:ns dedikerade klockingångar 77/80), 3,3 V LVCMOS, plus I2C till dekodern (SCL delad, en SDA per dekoder eftersom båda TVP har samma adress) och `RESETB`. Stiftplanen är Core `gateware/boards/m4_dual_mix.cst`; dekoderkortets J6/J5 speglar Tang-kortets så att en 1:1-kabel ger den.

Krav på en modul som lämnar denna gräns i stället för CVBS:

| | Krav | Varför |
|---|---|---|
| Ström | BT.656 8 bitar, 27 MHz, SAV/EAV med rätt paritet, F/V/H-bitar; 720 aktiva ord per rad; radnumren startar om vid vertikal släckning (två tidkoder med V = 1), inte vid F-biten | `bt656_rx.v` räknar rader så; mixern parar på radnumret |
| Fält | 242–244 (NTSC) eller 286–288 (PAL) aktiva rader per fält; ett avklippt fält tolereras (störningskampanjen), men inte godtyckliga geometrier | fältminnet och genlocken (`fb_backend.v`, `genlock_timing.v`) är simulerade för dessa |
| Lås och närvaro | kärnan tar `dec_present` och `dec_locked` ur TVP-pollningen (88h/89h). En modul utan TVP måste ge motsvarande två signaler per kanal, annars räknas kanalen som låst eller saknad beroende på hur toppen kopplas | menyn, mixerns "bad"-markering och RX5808-omskrivningen använder dem |
| Filtervalet | menyposten `FILT` skriver TV/VCR till TVP (02h). Utan TVP är posten verkningslös | bara dokumentation |
| Klocka | 27 MHz per kanal, oberoende av varandra; kärnan korsar domänerna i FIFO:er | `chan_capture.v`, `async_fifo.v` |

Det här är gränsen en SDR-väg (AD9361-kort, FM-demodulering och videoavkodning i mjukvara eller FPGA) skulle behöva nå för att använda radmixern och resten av kedjan. Den är inte byggd; inget här är provat.

## Vad som inte bestäms här

Ingen universalkontakt, ingen ny stycklista, inga nivåer på gissning (rådets avgränsning). Första riktiga modulen som provas mot gräns A utöver RX5808 bör vara C5VRX (lämnar CVBS); en SDR-väg mot gräns B är en egen uppgift när ett behov finns.
