# Produktidé 2027: "Analog-puck" (2026-10-02)

En fristående, batteridriven mottagarpuck. Analogt 5,8 GHz in, bild ut till XR-glasögon, en TV eller en skärm. Minimalt gränssnitt.

Status: idé. Inget beslutat, inga marknads- eller patentkontroller gjorda.

## Ursprunglig beskrivning

- Puck-format, gärna med HDMI-utgång och "modul-pins".
- Drivs av dubbla 18650/21700.
- Ett par knappar och en smal OLED-skärm (gärna svartvit).
- Har de utgångar som behövs för glasögonen eller för en fristående TV/skärm.

## Hur det passar ihop med det vi redan byggt

```
 [mottagare]  ──CVBS──►  dekoderkort (rev A)  ──BT.656──►  FPGA: mixer + bildbuffert + skalning  ──►  utgångar
  • 2× egna RX (mixning)                                    (M4 + M5-gatewaren)                        • HDMI 1080p60 (TV, glasögon via adapter)
  • eller modulfack för köpt modul                           + OLED/knappar via I2C                    • USB-C DP alt mode direkt till glasögonen (steg 2)
    (SteadyView X, RapidFire …)                                                                         • CVBS ut (vanliga goggles/skärmar)
```

Puckens elektronik är i stort sett "rev B" (`REV_A_KONCEPT.md`) plus batteri, laddning, kapsling och gränssnitt. Valet i går att göra rev A till ett separat dekoderkort håller: dekoderkortet sitter kvar oförändrat i pucken.

## Det som gör den intressant

- **Ett "modulfack"** för standardmoduler (Fat Shark-stil) gör att man kan välja mellan egen mixning (två RX på kortet) och en köpt modul. Samma puck täcker då båda vägarna i `research/ALTERNATIVA_VAGAR_2026-10-02.md`. Fackets stiftning och matning måste kontrolleras först.
- **Direkt USB-C till glasögonen**: pucken ger både DP alt mode och 5 V, så ingen adapter eller extra kabel behövs. Det kräver en HDMI→DP/USB-C-omvandlare och USB-C-logik (PD/alt mode). Delval ej gjort; Lontiums HDMI→DP/Type-C-kretsar är en kandidat att undersöka.
- **OLED + knappar** över samma I2C som dekodrarna redan använder: band/kanal, kanalscanning, RSSI/länkkvalitet per mottagare, mixläge (A/B/mix), batteri. FPGA:n har redan `i2c_master`. GW5A-25:s inbyggda ADC kan läsa RSSI och batterispänning.

## Grov strömbudget (att mäta, inte lova)

| Förbrukare | Uppskattning |
|---|---|
| 2 mottagare | ≈ 2 × 1–2 W (SpeedyBee ≈ 0,45 A @ 5 V) |
| FPGA + SDRAM | ≈ 0,5–1 W |
| 2× TVP5150AM1 | ≈ 0,3 W (datablad: 115 mW typ. styck) |
| HDMI/DP-omvandling | ≈ 0,3–0,5 W |
| XR-glasögon via USB-C | ≈ 1,5–2,5 W (om pucken matar dem) |
| **Summa** | **≈ 5–8 W** |

Två 18650 (2S, ≈ 22 Wh) räcker ungefär 3–4 h. Två 21700 (≈ 36 Wh) räcker ungefär 5–7 h. Laddning via USB-C PD, och ett skydds-/BMS-kort för 2S.

## Projektägarens svar 2026-10-02

1. **Bärsätt:** står på marken när man sitter; hänger i ett halsband eller sitter med clips när man står. **Inbyggd patchantenn i skalet + kontakt för lollipop.**
2. **Digitalt:** det vore fett att kunna plugga in digitala VRX-lösningar.
3. **Marknad:** projektägaren känner bara till markstationer som hör till ett visst digitalt system, och aldrig en portabel analog lösning som inte är en skärm. (Inte kontrollerat ännu.)
4. **Certifiering:** senare problem; det här kan vara en hobbyprototyp bara för projektägaren.

## Vad svaren betyder för designen

### Antenner = två mottagare = vår mixer

Patch (riktad) + lollipop (rundstrålande) är den klassiska diversity-kombinationen. Den passar exakt till två mottagare och radmixern (M4): patchen ger räckvidd framåt, lollipopen täcker när man vänder sig eller flyger nära.

- **Patchen pekar dit man tittar** när pucken hänger på bröstet, eftersom kroppen är bakom den. På marken behövs ett ställ eller ben som vinklar patchen mot flygområdet.
- **Polarisation:** patchen ska ha samma cirkulära polarisation som VTX-antennen (oftast RHCP) och lollipopen likaså, annars förloras mycket signal.
- **Patch i skalet:** antingen en färdig liten 5,8 GHz-patch (enklast) eller en egen PCB-patch. FR4 ger förluster vid 5,8 GHz och behöver mätas/trimmas. Kontakt för lollipop: SMA. Kontrollera SMA mot RP-SMA för de antenner projektägaren redan har.
- **RF-hygien:** mottagarna och antennerna ska hållas borta från FPGA, SDRAM, HDMI och switchade regulatorer, med skärmburk och separat jordad RF-del. Störningar från egen elektronik är den största risken med en puck där allt sitter ihop.

### Mottagare: RX5808 styrd av FPGA:n

RX5808-moduler (≈ 7,49 € hos Rotorama, SPI-styrda, analog RSSI-utgång) passar en puck bättre än goggle-moduler med eget gränssnitt. FPGA:n byter kanal via SPI (knappar + OLED) och läser RSSI. GW5A-25 har en inbyggd ADC; med GW2AR (Tang Nano 20K) behövs en extern ADC på I2C. Kontrollera att modulerna har "SPI-moden" (vissa säljs utan).

### "Plugga in digitalt": HDMI-in + matningsutgång

| Digital VRX | Bildutgång | Matning | Kommentar |
|---|---|---|---|
| Walksnail Avatar VRX | Mini-HDMI **1080p60** (även 720p100/60) | 7–25 V (2–6S), DC 5,5/2,1 | Kan gå rakt vidare till glasögonen |
| HDZero VRX | HDMI **720p60** | 7–26 V, **12 W** | 720p avvisas av XR-glasögonen → pucken måste skala till 1080p60 |
| DJI | ingen fristående VRX känd | — | utanför |

Konsekvenser:
- Pucken behöver ett **HDMI-in** och en **matningsutgång för den digitala mottagaren** (boost till t.ex. 12 V; ett 2S-batteri sjunker under 7 V när det är nästan tomt).
- **Enkel variant:** en passiv HDMI-omkopplare väljer analog bild (från FPGA:n) eller digital bild rakt igenom. Ingen extra latens, men ingen skalning eller OSD för den digitala bilden.
- **Smart variant:** FPGA:n tar emot HDMI själv. GW5A-25:s LVDS-mottagare klarar 1,6 Gbit/s enligt databladet, mot 1,485 som 1080p60 kräver. Då kan HDZero:s 720p skalas till 1080p60, och batteri och OSD läggas på. Det kostar viss latens (minst några rader, mer om bildfrekvenserna inte är låsta), och det är ett eget utvecklingssteg. Ytterligare ett skäl att GW5A-25 är intressant.
- **Strömmen:** HDZero VRX (12 W) mer än fördubblar puckens förbrukning. Med 2× 21700 (≈ 36 Wh) blir det ≈ 2–2,5 h med digital mottagare, ≈ 5–7 h analogt.

### Prototypväg (hobby, bara för projektägaren)

1. Dekoderkortet (rev A) + Tang Nano 20K + två RX5808 + patch/lollipop i en utskriven låda, matat från en USB-powerbank. Det ger ett första mått på räckvidd, mixning och egenstörningar.
2. Lägg till 2S-batteri med BMS och laddning, OLED och knappar.
3. HDMI-in (passiv omkopplare först, FPGA-mottagning senare om GW5A väljs).

## Marknadskoll (snabb, 2026-10-02 — inte heltäckande)

| Produkt | Vad den är | Jämfört med pucken |
|---|---|---|
| Skyzone/Boscam **RC832** (klassisk) | Analog 48-kanalsmottagare, **en antenn**, AV ut (RCA/3,5 mm), ingen HDMI | **Föregångaren** enligt projektägaren: samma grundidé (fristående analog mottagare), men en antenn, ingen mixning, inget batteri, ingen digital bild ut |
| Skyzone **RC832-HD** (~80 USD) | Samma enkla mottagare + **mini-HDMI, uppskalad till 1080p eller 720p** (omkopplare), AV samtidigt, 6–24 V, ≤ 200 mA | Uppgiven latens **≈ 40 ms på HDMI mot ≈ 20 ms på AV** (Flying Tech); bildfrekvens på HDMI anges inte. Ingen diversity/mixning |
| **SteadyView X** + "ground station"-kort | Mixande modul; markstationskortet matas med 2–6S | Bara AV-ut (3,5 mm), ingen HDMI, ingen display/batteri i samma låda |
| **RXVID3V2** | Analog diversity-mottagare med inbyggd kortdistanssändare, 8–10 h batteri | Ingen HDMI; sänder vidare analogt i stället |
| Diversity-monitorer (RMRC 5802, Flysight Black Pearl) | Skärm + diversity + batteri | Det är skärmar, alltså precis det projektägaren menar att pucken inte är |
| **TBS Groundstation** (2018) | 2,4 GHz-mottagare med 4"-skärm, 3S | Fel band, ingen HDMI |
| **FuriousFPV Dock-King** (2018, ~88 USD) | Markstation för True-D-modulen: 2–4S extern LiPo, OLED (batteri/RSSI), 2× AV ut, HDMI via separat tillvalsmodul, OSD, Bluetooth, stativfäste | **Närmast pucken.** Skillnader: växlande diversity (inte mixning), extern batteri, gjord för stativ (inte bärbar), ingen inbyggd patch, inget känt om HDMI-formatet, inget HDMI-in för digitalt. Recensionen (Oscar Liang) såg liten förbättring jämfört med True-D-modulen ensam |

Slutsats så här långt: Dock-King (2018) visar att en analog markstation utan skärm har funnits — men inte som bärbar puck med mixning, 1080p60 till XR och HDMI-in. Delarna finns var för sig: HDMI-ut (RC832HD), mixning (SteadyView/RapidMix), batteri/markstation. Men **kombinationen bärbar puck + mixning + 1080p60 till XR-glasögon + HDMI-in för digitala mottagare** hittades inte. projektägarens intryck håller i den här snabba sökningen. En grundligare koll (AliExpress, Banggood, forum) behövs innan det kallas unikt.

Bonus: **RC832-HD kan vara det billigaste sättet att prova XR-glasögonen med analog bild** (väg A i en enda låda), *om* dess 1080p-läge är 60 Hz. Det måste bekräftas innan köp, t.ex. via manual eller en användare.

Latensjämförelse att ha i bakhuvudet: RC832-HD:s uppskalare lägger uppgivet ≈ 20 ms ovanpå AV-vägen. Vår FPGA-väg buffrar ≈ ett halvbildsintervall (16,7–20 ms) och skalar sedan på några rader. Båda ska mätas med `tests/latency/` innan något påstås.

## Modern komponentstack (jämfört med RC832-generationen)

RC832 är i grunden en enda analog mottagare med en AV-förstärkare (RC832-HD lägger till en uppskalare med ≈ 20 ms extra). Det som kan moderniseras i pucken sitter **efter** radion. Själva 5,8 GHz-mottagarchipet har ingen känd efterföljare: RX5808/RTC6715 är fortfarande standard 2025, och även mixande moduler bygger på analoga mottagardelar plus egen signalbehandling.

| Block | RC832-eran | Pucken (förslag) | Vad det ger |
|---|---|---|---|
| Mottagare | 1× modul, en antenn | 2× RX5808 (RTC6715), patch + lollipop | Diversity med riktad + rundstrålande antenn |
| Signalbehandling | ingen (växling i bästa fall) | **FPGA-mixer rad för rad** (M4, simulerad) + 2× TVP5150AM1 | Mixning som i SteadyView/RapidMix/Fusion, men egen och justerbar |
| Bild ut | AV; HDMI via uppskalare (≈ 40 ms) | **1080p60 direkt från FPGA** (GW5A-25, 2 Gbit/s serialiserare) eller ADV7513; ≈ ett halvbildsintervall buffert | Glasögon/TV utan extra box; latens att mäta |
| Digital in | — | **HDMI-in** (passiv omkopplare, senare FPGA-mottagning) + 12 V ut för digital VRX | Walksnail 1080p rakt igenom, HDZero 720p uppskalad |
| Kanalval | knappar på mottagaren | Knappar + OLED, **inbyggd ExpressLRS VRX Backpack** (ESP32, styr RX5808 via SPI) | Radion ställer in puckens kanal automatiskt när VTX:en byter |
| Konfiguration | — | ESP32: Bluetooth/wifi-sida i mobilen | Inställningar utan meny på en liten OLED |
| Ström | extern 7–24 V | 2S 18650/21700 + **USB-C PD-laddare med buck-boost** (TI BQ25792: dokumenterad, I2C, 1–4S; eller Injoinic IP2368: 100 W åt båda hållen) | Ladda från vilken USB-C-laddare som helst; IP2368 kan även *ge* ström (powerbank för glasögon/telefon) |
| Batteriinfo | — | Bränslemätare / FPGA-ADC (GW5A-25) | Kvarvarande tid på OLED |
| Inspelning (senare) | extern DVR | SD-kort från FPGA (rå/enkel komprimering) eller DVR-utgång | — |

Kandidaterna ovan är sökträffar 2026-10-02 och inte valda: datablad, tillgänglighet och pris kontrolleras innan något ritas. Enklast i prototypen är färdiga moduler: RX5808 med SPI-mod, ett ESP32-C3-kort som backpack, en färdig 2S USB-C-laddmodul.

## Dubbelriktad USB-C PD 3.0 (projektägarens favoritfunktion)

En USB-C-port som både laddar pucken och kan **ge** ström. Det kan Injoinic **IP2368** (datablad v1.35/v1.40):
- **PD 2.0/3.0 åt båda hållen** + QC2.0/QC3.0/QC3+, FCP, AFC, SCP, Apple. Ut och in 5/9/12/15/20 V, upp till **100 W**. PPS bara i kundanpassade versioner.
- 2–6 celler i serie (väljs med motstånd), NTC-temperaturvakt, I2C, batteriindikering med LED.
- Färdiga moduler finns ("IP2368 2–5S 100 W bidirectional"). En sådan räcker i prototypen.

Vad det ger pucken:
- **Ladda** med vilken USB-C PD-laddare som helst, snabbt (2S 21700 ≈ 36 Wh).
- **Mata ut**: XR-glasögon, telefon, en digital VRX via PD-trigger (12 V) eller laddning av radion i fält. Pucken blir en powerbank.
- Med I2C kan FPGA:n läsa laddstatus och visa den på OLED:n.

Att tänka på: XR-glasögonen vill ha DisplayPort alt mode *och* ström på samma USB-C. Det kräver en egen port med DP-omvandlare (se "utgångar"), inte laddporten. Laddporten ger ström till annat. TI BQ25792 + separat PD-kontroller är ett alternativ med fullt TI-datablad, men det blir fler chip.

## Egenstörning (EMI): mät först, rita skal sedan

projektägaren frågade 2026-10-03 om skalet. Svar: inget skal ritas förrän egenstörningen är uppmätt. Placeringen av delarna i skalet följer av mätningen, inte tvärtom.

### Var våra klockor hamnar i 5,8 GHz (räknat)

Övertoner inom ±9 MHz från svenska kanaler (5725–5875 MHz):

| Klocka | Träffar |
|---|---|
| 27 MHz (kort, TVP SCLK), 14,318 MHz (TVP-kristall) | något nära **alla** kanaler (övertonsavstånd 27/14 MHz). Det är den 200:e+ övertonen, alltså svag, men går inte att undvika med kanalval |
| SDRAM 64,8 MHz | A3/B6/F6 (90× = 5832), A6/B3/F2/R4 (89× = 5767,2) |
| Pixel 720p 74,25 MHz | **F4** och A5/B4 (78× = 5791,5), A1/B8/F7 (79× = 5865,8) |
| Pixel 1080p 148,5 MHz | **F4** och A5/B4 (39× = 5791,5) |
| TMDS-bitklockor (742,5 / 1485 MHz) | inga svenska kanaler |

**F4 5800 (standardkanalen) ligger 8,5 MHz från pixelklockans överton.** Det kan synas som ett svagt mönster vid svag signal. Mät det. Om det stör: välj en annan standardkanal, eller flytta SDRAM-klockan (den är fri att välja), eller sprid HDMI-kabeln bort från antennerna. TMDS-kabeln och HDMI-kontakten är troligen den starkaste strålaren.

### Var våra klockor hamnar i mottagarens mellanfrekvens (räknat)

RTC6715 blandar ner till 479–480 MHz och filtrerar där (filtret sitter på RX5808-modulen; dess bredd står inte i något datablad vi har, filterklassen har 20–24 MHz). De här övertonerna ligger i det bandet på **varje** kanal och är mycket lägre övertoner än de i tabellen ovan (18:e mot 215:e), alltså starkare vid källan:

| Överton | Frekvens | Avstånd från mellanfrekvensen |
|---|---|---|
| 18 × 27 MHz (TVP SCLK, kortets oscillator) = 36 × 13,5 MHz (BT.656-data) | 486,0 MHz | +6 till +7 MHz |
| 34 × 14,318 MHz (TVP-kristallen) | 486,8 MHz | +7 till +8 MHz |
| 33 × 14,318 MHz = 35 × 13,5 MHz | 472,5 MHz | −6,5 till −7,5 MHz |
| SDRAM 64,8 MHz, pixel 74,25 MHz | inga inom ±20 MHz | |

TMDS-data är dessutom bredbandigt mellan bitklockans multiplar, inte bara spikar. Verkan är inte mätt: en störning här syns inte som mönster utan som kortare räckvidd, så den måste mätas vid svag signal. Underlag och åtgärder: navets `research/RF_DIVERSITY_OCH_EGENSTORNING_2026-10-05.md`, avsnitt 4.

### Inbyggt mätinstrument

FPGA:n mäter redan "snö" per bildrad (HF-energin i `bt656_rx`, samma mått som mixern använder). Med en VTX på fast avstånd (eller med dämpare) och en stillastående kamera blir det ett jämförbart störmått:
1. Allt på, mät snö-nivå och hur ofta mixern byter/blandar.
2. Slå av HDMI-utgången (mixer och SDRAM igång): skillnaden = HDMI:s bidrag.
3. Byt kanal: F4 mot t.ex. A8 eller R7. Skillnaden visar övertonstreffar.
4. Flytta mottagarna 5 / 10 / 20 cm bort; lägg på en skärmburk (koppartejp/bleckburk) över digitaldelen.
5. Dekoderkortets matning av och på, FPGA:n igång: skillnaden = bidraget från 27 och 14,318 MHz, det som hamnar i mellanfrekvensbandet. (Reset räcker inte som "av": om kristalloscillatorn går under reset är inte kontrollerat.)
6. Gör mätningarna vid svag signal, helst kabelbundet (VTX i skärmad låda → dämpare → delare → båda mottagarna, strax över tröskeln). Vid stark signal syns inte en störning i mellanfrekvensbandet.

(Verktyg finns sedan 2026-10-03: mätarsidan på OLED:n/OSD:n och mätloggen över USB, `gateware/tools/snowlog.py` med `--label` per testvillkor och `--summary`. Se `gateware/README.md`, avsnittet M6.)

### Testrigg i stället för skal (steg 1)

En platt utskriven platta (eller plywood) med tre zoner och flyttbara fästen:
- **RF-zon:** 2× RX5808 + patch + SMA för lollipop, i ena änden, med eget LDO-matat 5 V.
- **Digital zon:** Tang Nano 20K + dekoderkort, med plats för en skärmburk.
- **Kraft och gränssnitt:** batteri/laddare, OLED, knappar, HDMI-uttag så långt från RF-zonen som möjligt.

Kablarna mellan RF och dekoderkort görs långa nog att avståndet kan varieras (videon tål 30 cm utan problem).

### När skalet ritas (råd)

- **projektägarens val: mycket tunn seg, slagtålig och reptålig resin.** Bra; tänk på: plast framför patchen förstimmer den. **Resin (SLA)** allmänt: plast framför patchen förstimmer den (εr ≈ 3–4). Håll radomen tunn (≈ 1–2 mm) och jämntjock, utan färg eller metall. Vanlig resin är spröd för något som hänger i halsband/clips; seg resin ("tough") eller FDM i PETG/ASA för prototyper.
- **Skärmning:** separat kammare för digitaldelen, invändigt koppartejp eller ledande färg, jordad till kortets jordplan. Inget ledande över patchen eller lollipop-kontakten.
- **Värme:** FPGA + LDO:er ≈ 1–2 W i en sluten låda behöver ventilation eller en kylplatta mot skalet. Battericellerna ska inte ligga mot de varma delarna.
- **Antenner:** patchen i fronten (pekar framåt när pucken hänger på bröstet), SMA-uttaget för lollipop upptill.

### Jordning i ett slutet, batteridrivet skal (projektägarens fråga 2026-10-03)

"Jord" för skärmning betyder **kretsens egen referens** (0 V / jordplanet på kretskortet, batteriets minus), inte jord i marken. En batteridriven puck svävar fritt, och det gör inget: skärmen fungerar ändå så länge den sitter ihop med kretsens jordplan med **låg impedans**. Då kan bruset från den digitala delen inte ta sig ut till antennerna.

Så gör man i praktiken:
- **Skärmburk på kortet** (bäst): plåtburk eller klämfäste som löds direkt mot jordplanet runt FPGA, SDRAM och HDMI. Färdiga burkar och klämmor finns att köpa. I prototypen: koppartejp format som en låda, lödd mot jordplanet i flera punkter längs kanten.
- **Skärmning i skalet**: ledande färg (nickel/koppar) eller koppartejp på insidan av den digitala kammaren. Kontakt mot kortets jord via **metallskruvar genom pläterade monteringshål**, fjäderkontakter eller ledande packning. En enda tunn tråd räcker inte: vid höga frekvenser är tråden en spole och skärmen blir en antenn i stället.
- **Många kontaktpunkter**, inte en. Avståndet mellan dem och längden på springor i skärmen ska vara små mot våglängden. Vid 5,8 GHz är λ ≈ 52 mm, så springor och hål bör vara under ≈ 5 mm (λ/10). Skarvar i koppartejp ska överlappa.
- **Allt som går ut genom skärmen** är en möjlig antenn: matning, knappar, OLED-kabel och HDMI. Filtrera vid genomföringen (ferrit + kondensator mot jord) och jorda HDMI-kontaktens skal mot samma jordplan.
- **Antennerna**: SMA-kontaktens yttre del och patchens jordplan kopplas till samma jord, men på RF-sidan. Ingen ledande färg över patchen eller lollipop-kontakten.
- **Vid laddning via USB-C** binds kretsens jord till laddarens jord. Det är normalt och påverkar inte skärmningen.

### Standardväg för prototypen: två SMA-kontakter, skruva på antennerna (projektägaren 2026-10-03)

Enklast och mest flexibelt, och samma sätt som goggles och mottagarmoduler använder:
- **Två SMA-genomföringar i skalet:** en framåt för patchen, en uppåt för lollipop. Kontakterna sitter i skalet (inte i kortkanten), med kort pigtail-koax in till varje RX5808, så att skalet tar kraften när pucken hänger.
- **Valfria antenner:** patch, helical, lollipop; RHCP eller LHCP efter VTX-antennerna. Kontrollera SMA mot RP-SMA. Ingen VNA eller trimning behövs, och en trasig antenn byts.
- **Snyggare:** en **ficka i skalets front** där en kompakt platt patch (t.ex. TrueRC X²-AIR, Lumenier AXII Patch) ligger nästan i nivå med skalet. Den ser inbyggd ut men går att skruva loss.
- **EMI:** genomföringskontakternas hölje jordas mot skärmen/jordplanet. Kontakten är ett av hålen i skärmningen.

Den inbyggda luft-patchen nedan är en senare uppgradering för en snyggare puck.

### Möjlig väg: skärmens lock som patchantennens jordplan (projektägaren 2026-10-03)

Idén är att den inbyggda skärmningen också gör nytta som antenn, med flit. Mobiltelefoner gör samma sak med metallramen. **Grundregel: antennens insida måste vara tyst.** Den digitala skärmburken får aldrig själv vara antennen, för då kopplar FPGA-bruset rakt in i den.

**Vägen som rekommenderas:** locket på den digitala kammaren (koppartejp/plåt, jordat mot kortets jordplan) blir **jordplan för en luft-patch** som sitter utanpå, under den tunna resin-radomen. En patch strålar främst bort från sitt jordplan, så locket skärmar patchen från bruset under samtidigt som det är en del av antennen.

Byggsätt (startpunkt, inte färdig konstruktion):
- **Patch:** kopparplåt (≈ 0,2–0,3 mm) på utskrivna distanser över locket, luft emellan. Uppskattad sida vid 5,8 GHz (Hammerstad, luft, kvadratisk):

  | Höjd över jordplanet | Patchens sida | Jordplan minst |
  |---|---|---|
  | 2 mm | ≈ 23,1 mm | ≈ 47 mm |
  | 3 mm | ≈ 21,8 mm | ≈ 58 mm |
  | 4 mm | ≈ 20,6 mm | ≈ 69 mm |

  Högre ger större bandbredd men kräver större jordplan; 3 mm är en rimlig början. Radomen framför sänker resonansen något, så patchen blir lite mindre än tabellen.
- **Cirkulär polarisation (RHCP):** två motstående hörn avfasade (storleken trimmas, i storleksordningen 10–15 % av sidan). Vilket hörnpar som fasas avgör RHCP eller LHCP; det ska matcha VTX-antennerna.
- **Matning:** koaxialprob genom locket till patchen, förskjuten från mitten tills impedansen blir 50 Ω (bestäms med VNA). Kort koax till RX5808, som sitter i en **egen** liten RF-burk.
- **Lollipop:** SMA-uttaget upptill, kopplat till den andra RX5808. Patch + lollipop = mixerns två kanaler.

**Avancerad variant (senare):** en slits ≈ λ/2 (≈ 26 mm) i en *egen* RF-kammare (cavity-backed slot, korsade slitsar för cirkulär polarisation). Kräver att kammaren bara innehåller antennmatningen. Ledande färg som antennyta: silverfärg, inte nickel (för stora förluster vid 5,8 GHz).

**Krävs:** en VNA som når 6 GHz för att trimma resonans, impedans och polarisation, *med radomen på*. NanoVNA-familjen har modeller upp till ≈ 6 GHz (t.ex. LiteVNA); pris och modell kontrolleras vid köp. Utan VNA går det bara att jämföra grovt mot en köpt patch med snö-mätaren.

Testordning: (1) köpt patch i testriggen som referens, (2) egen luft-patch på ett löst jordplan, trimmad med VNA, (3) samma patch på skärmlocket i riggen, jämförd med snö-mätaren mot (1).

## Öppna frågor innan något ritas

1. Finns det redan portabla analoga puckar med HDMI/USB-C ut, mixning och batteri? Snabbkollen ovan hittade ingen; grundligare koll återstår.
2. Var hamnar latensen hela vägen till glasögonen? Mätriggen finns (`tests/latency/`).
3. Modulfack eller egna mottagare? projektägaren är osäker. Förslaget är två RX5808 på kortet (passar patch + lollipop och mixern) plus HDMI-in för digitalt; ett modulfack för köpta analoga moduler är ett möjligt tillägg.
4. ~~Bärsätt~~ besvarat: både på marken och hängande (halsband/clips).
5. Certifiering (CE/RED, batterier, transport): senare, gäller bara om det blir en produkt.
6. Egenstörning: hur mycket stör FPGA/HDMI/regulatorer mottagarna när allt sitter i samma låda? Mäts i prototypsteg 1.
7. Antenner: prototypen kör två SMA-genomföringar med påskruvade antenner (beslut 2026-10-03). Inbyggd luft-patch på skärmlocket är en senare uppgradering och kräver VNA (≈ 6 GHz).

## Källor (2026-10-02)

- Moderna delar: [ExpressLRS VRx Backpack (wiki)](https://github.com/ExpressLRS/ExpressLRS/wiki/VRx-Backpack), [Backpack-installation](https://www.expresslrs.org/hardware/backpack/backpack-vrx-setup/), [BQ25792-datablad](https://download.mikroe.com/documents/datasheets/BQ25792_datasheet.pdf), [IP2368-laddare (Xtronic)](https://xtronic.org/circuit/battery-charger/ip2368-lithium-battery-charger-3s-6s-pd-100w/), [IP2368-datablad v1.35 (ChipSourceTek)](https://www.chipsourcetek.com/DataSheet/IP2368_v1.35.pdf), [IP2368 v1.40 (Injoinic)](https://energo-shop.com/content/files/ip2368-datasheet-8175550.pdf), [IP2368-modul (Amazon)](https://www.amazon.com/PIEXANGH-Bidirectional-Discharge-Discharging-Institution/dp/B0HBQ1TFG3), [RX5808/FS5808M](https://fpvspeed.com/product/showproduct.php?id=252)

- Marknad: [RC832-HD (Flying Tech)](https://www.flyingtech.co.uk/product/skyzone-rc832-hd-48ch-5-8ghz-fpv-video-receiver-with-hdmi-output/), [RC832HD (Pyrodrone)](https://pyrodrone.com/products/rc832hd-5-8ghz-48ch-fpv-hd-receiver-with-1080p-hdmi-a-v-output), [RC832HD (Rotorama)](https://www.rotorama.com/product/readytosky-rc-hd-receiver-with-2dbi-antenna), [SteadyView X V3.3 (Rotorama)](https://www.rotorama.com/product/skyzone-steadyview), [RXVID3V2](https://d3.xlrs.eu/product/rxvid3v2-analog-diversity-video-receiver-with-internal-short-range-transmitter-5-8ghz/), [RMRC 5802](https://www.readymaderc.com/products/details/5802-5_8GHz-40-channel-7-inch-diversity-receiver-fpv-monitor-with-dvr), [TBS Groundstation (Oscar Liang)](https://oscarliang.com/tbs-groundstation/), [IntoFPV: analoga HDMI-mottagare](https://intofpv.com/t-are-there-any-good-analog-hdmi-video-receivers), [Dock-King (Oscar Liang)](https://oscarliang.com/furiousfpv-dockking-ground-station/), [Dock-King (FPV24)](https://www.fpv24.com/en/furious-fpv/furiousfpv-dock-king-ground-station)

- Walksnail Avatar VRX: [Caddx produktsida](https://www.caddxfpv.com/products/walksnail-avatar-fpv-vrx), [Caddx genomgång](https://www.caddxfpv.com/blogs/news/walksnail-avatar-vrx-hdmi-digital-fpv-receiver)
- HDZero VRX: [Oscar Liang recension](https://oscarliang.com/hdzero-vrx-2022/), [HDZero produktsida](https://www.hd-zero.com/product-page/hdzero-vrx)
- RX5808: [Rotorama](https://www.rotorama.com/product/rx5808-prijimac-modul), [Buzz Hobbies (SPI-mod)](https://buzzfpv.com.au/products/rx-5808-receiver-module-spi-mod)
