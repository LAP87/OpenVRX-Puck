# Rev A — underlag för layouten

Status 2026-10-13: underlag, ingen layout. Inget här är lagt ut, routat eller provat. Varje regel har ett skäl och en källa; det som är en egen bedömning står som bedömning. Referensbeteckningarna är netlistans (`out/dekoderkort_kopplingar.md`).

Källor (citeras, ingår inte i repot):

| Förkortning | Dokument |
|---|---|
| SLEA081 | TI, *TVP5150AM1 PCB Layout Guidelines*, juni 2010 |
| SLES209E | TI, TVP5150AM1-databladet, november 2007, reviderat oktober 2011 (tabell 2-1, avsnitt 3.16 och 3.18, termiska data, figur 6-1) |
| SLEU044 | TI, *TVP5150A Quick Start Guide*, oktober 2003 (ingångsdelare, antialiasfilter, kristall) |
| Sipeed | Tang Nano 20K: kortmåttet 22,55 × 54,04 mm ur Sipeeds wiki; stiftens funktioner ur Sipeeds schema rev 3921/3923 så som de används i `dekoderkort.py` och Core `gateware/BRINGUP.md` |

## 1. Kortet och Tang Nano 20K

**Montering som sandwich.** Tang-kortet ligger överst med komponentsidan upp, och dess hanstift går ner i två 1×20 hylslister på dekoderkortets ovansida: J2 under Tang-kortets J6 och J3 under J5, stift n mot stift n. Båda korten vänds åt samma håll, så hylslisternas läge sett ovanifrån är samma som Tang-kortets stift sett ovanifrån; ingen spegling. Läggs dekoderkortet i stället upp och ner ovanpå Tang-kortet måste fotavtrycket speglas.

| Mått | Värde | Källa |
|---|---|---|
| Tang Nano 20K | 22,55 × 54,04 mm | Sipeeds wiki |
| Stiftlister | 2 × 20 stift, delning 2,54 mm | Sipeed |
| Avstånd mellan raderna | 20,32 mm (0,8 tum) | ett KiCad-fotavtryck från en tredje part (DIP-40_TangNano20K); **inte kontrollerat mot Sipeeds måttritning** |
| Avstånd mellan korten | cirka 11 mm: hylslist 8,5 mm plus Tang-stiftlistens plast 2,5 mm | bedömning; beror på valda delar |

Innan kortet beställs: lägg Tang-kortets kontur och stiftlägen ur Sipeeds måttritning eller 3D-modell (nedladdningssidan "4_Dimensional_drawing") i layouten, och skriv ut kortet i skala 1:1 och tryck ett riktigt Tang-kort genom utskriften. Vilken ände stift 1 sitter i på J5 och J6 ska läsas av på kortet, inte antas.

**Förslag till yttermått: 66 × 58 mm**, Tang-kortet centrerat. Under Tang-kortet ryms hylslisterna och ledningarna dit; på varje långsida blir en remsa på cirka 21 mm kvar för en dekoder med sin ingång. Det är ett utgångsläge räknat på delarnas storlek (TQFP-32 med lödytor cirka 9 mm, seriemotstånd 2,5 mm, ingångskedja cirka 4 mm, JST PH 4-pol 4,8 mm djup), inte en provad placering. Längden ger 2 mm utanför Tang-kortet i varje ände; USB-C och HDMI sitter i Tang-kortets ändar ovanför, och deras kontaktdon når inte ner till dekoderkortet med 11 mm mellanrum (bedömning).

**Under Tang-kortet** ligger bara hylslisterna, ledningarna från seriemotstånden till hylslisterna, SCL, SDA och RESETB på väg mellan sidorna, I2C-pull-upparna R1–R3, lödbyglarna JP1 och JP2 och 5 V-kondensatorn C1. Inga testpunkter (de går inte att nå), inga värmekällor (luften står still mellan korten och FPGA:n värmer ovanifrån), inga analoga delar. Kontrollera Tang-kortets undersida i 3D-modellen innan något högt läggs där.

## 2. Lagerstack

**Fyra lager, 1,6 mm:** L1 delar och signaler, L2 obrutet jordplan, L3 matning (3,3 V, 1,8 V och 5 V som ytor), L4 långsamma signaler och jordyta. Ytterlager 35 µm (1 oz), innerlager 17,5 µm (0,5 oz).

| Skäl | Källa |
|---|---|
| Alla 27 MHz-ledningar på L1 får ett obrutet referensplan direkt under sig utan vior; på två lager måste korsningar gå på undersidan och skär då jordplanet | SLEA081: snabba signaler över hela plan, inte över delningar |
| TI rekommenderar 50 Ω på kortet och nära 75 Ω för CVBS; med cirka 0,2 mm till L2 blir det 0,35 mm (50 Ω) och 0,15 mm (75 Ω), på två lager 3 respektive 1,3 mm | SLEA081; bredderna räknade med IPC-2141-formeln och εr 4,4, kontrollera mot leverantörens stack |
| TVP:ns θJA är 91,1 °C/W på ett JEDEC-kort med inre plan och 125,3 °C/W utan; med 185 mW blir det +17 respektive +23 °C | SLES209E, termiska data; SLEA081 (185 mW) |
| Strömmarna är små (högst cirka 1,1 A på 5 V), så 1 oz räcker | avsnitt 4, Matning |

Två lager går att göra men kräver nästan hel jord på undersidan och fler bryggor; skälet att ändå välja det vore pris, inte funktion.

## 3. Placering per block

Varje dekoder i sin remsa utanför Tang-kortet: A på J6-sidan (J2), B på J5-sidan (J3). TVP:n vänds så att sidan med stift 9–16 (SCLK, IO_DVDD, YOUT7–YOUT2) pekar mot hylslisten, med YOUT1 och YOUT0 (stift 17–18) på sidan intill, och hörnet mellan stift 1 och 32 (analog ingång, PLL, kristall, referenser på stift 1–7 och 29–32) pekar utåt mot kortkanten och ingångskontakten.

**Varför TVP:n vid sin stiftlist:** TVP:ns data- och klockutgångar är specade för högst 10 pF last (SLEA081) och driver 2 mA (SCLK 4 mA; SLES209E). Ledningen på dekoderkortet, hylslisten, Tang-kortets ledning och FPGA:ns ingång delar på de 10 pF. Dekoder A:s datastift ligger på J6-1 till J6-14, B:s på J5-3 till J5-17 (`dekoderkort.py`), så TVP:n ska sitta mitt för sin del av raden, inte vid kortets ände.

| Block | Delar (A / B) | Regel | Skäl och källa |
|---|---|---|---|
| Ingång och första ESD | J4, D1, TP1 / J5, D3, TP8 | D1 direkt vid kontaktens CVBS-stift, med kort väg och egen via till jordplanet | ESD-pulsen ska till jord innan den går vidare; SLES209E figur 6-1 not G (ESD rekommenderas på ingången) |
| Delare och andra ESD | R4, R5, D2 / R20, R21, D4 | Delaren intill D1, D2 vid delarens mittpunkt | Termineringen ska sitta där kabeln slutar; SLEU044 (delaren), README (andra klampen efter delaren) |
| Antialiasfilter | L1, C18 / L2, C33 | Mellan delaren och kopplingskondensatorn, C18 mot jord tätt vid L1 | SLES209E figur 6-1 not F; filtret räknat i README |
| Kopplingskondensator | C19 / C34 | Intill stift 1 (AIP1A), ledningen efter den kortare än några mm | Noden efter kondensatorn har ingen DC-väg utom TVP:ns ingång och är känsligast för störning; SLEA081 (TVP:n så nära ingången som möjligt) |
| Oanvänd ingång | C20 / C35 | Vid stift 2 | SLES209E tabell 2-1 |
| Kristall | Y1, C21, C22, R6 / Y2, C36, C37, R22 | Vid stift 5–6, ledningarna några mm; urtag i jordplan och jordytor runt kretsen | SLEA081 (avstånd och urtag); SLES209E 3.16 och SLEU044 (lastkondensatorerna mot den jord kristallen ser) |
| Referenser | C14, C15, C16 / C29, C30, C31 | Vid stift 29–30, C16/C31 direkt mellan REFP och REFM | SLES209E tabell 2-1 och figur 6-1 |
| Analog matning | FB1, C8, C9; FB2, C10, C11 / FB3, C23, C24; FB4, C25, C26 | Ferriten nära stiftet, 0,1 µF vid stiftet (stift 32 respektive 4), 1 µF och 4,7 µF strax efter ferriten | SLEA081 (avkoppling vid stiften); README "PLL-matningen" |
| Digital matning | C12, C13 / C27, C28 | 0,1 µF vid stift 20 (DVDD) och 10 (IO_DVDD) | SLEA081; SLES209E figur 6-1 |
| Seriemotstånd | R9–R16, R19 / R25–R32, R35 | Inom 2–3 mm från TVP-stiften, i en rad mot hylslisten | Serietermineringen verkar vid källan; SLEA081 (22 eller 33 Ω) |
| Styrstift | R7, R8, R17, R18 / R23, R24, R33, R34 | Vid stift 28, 27 och 11 | SLES209E figur 6-1 not C, H; I2CSEL |
| Synkutgångar | TP2–TP5 / TP9–TP12 | Testpunkter vid stift 23–26, på kortets utsida | Nås med kortet monterat |
| 3,3 V | U1, C2, C3 | I en remsa, inte under Tang-kortet, med en kopparyta på fliken | Avsnitt 6 |
| 1,8 V | U2 (digital), C4, C5; U3 (analog), C6, C7 | Nära den dekoder som ligger närmast; U3:s utgång till båda dekodrarnas ferriter som egen ledning eller yta på L3 | Den analoga 1,8 V ska bara gå till CH_AVDD och PLL_AVDD (schemat) |
| Mottagarnas 5 V | F1, C17 / F2, C32 | PTC och kondensator vid respektive ingångskontakt | Matningen till mottagaren går den kortaste vägen; avsnitt 6 om värme |
| RSSI | U6, R37, C38, R39, C39, C40 | ADC:n på A-sidan nära J6-3/J6-4 (SCL, SDA_A); 10 kΩ och 0,1 µF vid ADC:ns ingång, så den filtrerade noden blir kort | RC-filtret dämpar det som plockas upp på vägen; README "RSSI" |
| RSSI-pull-down | R36 / R38 | Vid kontaktens stift 4 | Ger 0 V utan mottagare (README) |
| RSSI-testpunkter | TP15, TP16 | På kortets utsida | Multimeterjämförelse (README) |
| SCLK-testpunkter | TP6 + TP7 / TP13 + TP14 | Signalpunkt och jordpunkt högst 5 mm isär, utanför Tang-kortets skugga, så nära hylslisten det går | En kort jordfjäder ger liten slinga när 27 MHz mäts (README) |
| Matningsingång | J1, C1, JP2 | J1 vid kortkanten; JP2 och C1 vid J3-1 (+5V_TANG) | Kort väg för upp till cirka 1,1 A (avsnitt 4) |

## 4. Ledningsregler

| Signaler | Regel | Skäl | Källa |
|---|---|---|---|
| 27 MHz: TVPA_D0–D7, TVPA_SCLK, TVPB_D0–D7, TVPB_SCLK (och ledningarna mellan TVP och seriemotstånd) | På L1 hela vägen, inga vior | En via byter referensplan och lämnar en stubbe; med fyra lager har L1 ett obrutet L2 under sig | SLEA081 (över hela plan, inte över delningar) |
| | 0,35 mm (50 Ω mot L2), avstånd minst två bredder mellan ledningar | TI:s rekommendation för kortets impedans; avståndet är bedömning | SLEA081 |
| | Så korta som möjligt, sikta på under 25 mm från TVP-stift till hylslist | Lasten är högst 10 pF totalt; 25 mm är cirka 3 pF på kortet, resten tas av hylslist, Tang-kortet och FPGA:n | SLEA081 (10 pF); kapacitansen bedömning |
| | Varje dekoders data inom ±10 mm från sin SCLK | Vid 37 ns period är skillnaden betydelselös (60 ps per cm); regeln håller samplingspunkten oberoende av routningen | bedömning |
| | Seriemotstånden inom 2–3 mm från TVP:n | Serieterminering verkar vid källan | SLEA081 (22 eller 33 Ω) |
| Returvägen för 27 MHz | Ingen ledning eller urtag i L2 mellan TVP:n och hylslisten; vior till L2 vid varje GND-stift i hylslisterna (J2-20, J3-2, J3-15) | Tang-kortet har bara tre jordstift i stiftlisterna. B:s datastift ligger intill J5-2 och J5-15, men A:s ligger på J6-1 till J6-14 och J6-20 är upp till 48 mm bort, så A:s returström går en lång väg | stiftkartan i `dekoderkort.py` |
| CVBS: CVBS_A/B, CVBS_DIV, CVBS_AAF, AIP1A | Kort, cirka 0,15 mm (75 Ω mot L2) | TI vill ha CVBS nära 75 Ω; på några centimeter vid 5 MHz spelar impedansen liten roll, terminering vid kontakten är det som räknas | SLEA081; SLEU044 |
| | Avstånd minst 8–10 ledningsbredder till varandra och till andra ledningar, jordyta med vior på båda sidor | Överhörning mellan de två videoingångarna och från digitalt | SLEA081 |
| | Över jord, aldrig korsad av en 27 MHz-ledning på annat lager | Samma skäl | SLEA081 |
| Kristall: XTAL1/XTAL2 | Några mm, inga andra ledningar närmare än 8–10 bredder, urtag i L2 och jordytor runt kretsen | Liten frekvensavvikelse ger förlorad färg | SLEA081; SLEU044 |
| I2C: I2C_SCL, I2C_SDA_A, I2C_SDA_B | Ledningarna tillsammans, minst tio bredder till andra ledningar | | SLEA081 |
| RESETB (TVP_RESETB) | Från J2-18 till stift 8 på båda; inte förbi ingångar eller kristaller | Ett störpulståg på RESETB startar om dekodern | SLES209E 3.18 |
| RSSI | Långsam (τ = 1 ms), men bort från CVBS och kristall | Ingen ström att tala om; inget skäl att ta plats nära analog video | README "RSSI" |
| 5 V från J3-1 genom JP2 | Minst 0,8 mm eller yta | Upp till cirka 1,1 A (två mottagare à 0,45 A och kortet); IPC-2221 ger 0,35 mm för +10 °C med 35 µm, 0,8 mm ger cirka 20 mV fall på 30 mm | README (mottagarnas ström); IPC-2221 |
| +5V_RX_A/B (efter PTC) | Minst 0,5 mm | 0,45 A per mottagare | README |
| +3V3, +1V8_D, +1V8_A, AVDD, PLL_AVDD | 0,3 mm eller ytor på L3 | Under 0,2 A | SLEA081 (strömmarna per matning) |
| Avkoppling | Kondensatorn vid stiftet, via till L2 direkt vid kondensatorns jordyta | | SLEA081 |

Nätklasser för KiCad (uppgift 18 i navets nattpass): **27M** (TVPx_D0–D7, TVPx_SCLK och deras `_U`-nät före seriemotstånden), **CVBS** (CVBS_x, CVBS_DIV_x, CVBS_AAF_x, AIP1A_x), **POWER** (+5V, +5V_TANG, +5V_RX_x, +3V3, +1V8_D, +1V8_A, AVDD_x, PLL_AVDD_x). Reglerna ovan ryms inom vanliga tillverkningsgränser (ledning och avstånd 0,15 mm, via 0,3/0,6 mm).

## 5. Jordstrategi

**Ett obrutet jordplan på L2, inte delat i analog och digital jord.** Analog och digital ström hålls isär genom placeringen: det analoga hörnet av varje TVP, kristallen, referenserna och ingångskedjan ligger mot kortkanten, och ingen digital returström har anledning att gå där, eftersom 27 MHz-ledningarna går från TVP:ns andra sidor in mot hylslisten.

Skäl:
1. TI föredrar delad jord men kräver den inte (SLEA081). Utan delning ska ändå ett urtag göras runt kristallkretsen (SLEA081, figur 1).
2. Schemat har ett enda GND-nät. En delning kräver nettie-delar i schemat.
3. Mottagarkontakten (J4, J5) har ett jordstift för både mottagarens 5 V-retur (cirka 0,45 A) och videons retur. På en analog ö går matningsreturen genom ön till mötespunkten; på den digitala sidan korsar videoreturen delningen. Båda är sämre än ett helt plan.
4. Två dekodrar ger två analoga öar och två mötespunkter, inte en.

Mottagarens matningsretur går genom planet från ingångskontakten till Tang-kortets jordstift. Lägg ingångskontakten och PTC:n så att den vägen inte går rakt under TVP:ns analoga hörn (bedömning).

**Om en delning ändå väljs:** en analog ö per dekoder under stift 1–7 och 29–32 med ingångskedjan, referenserna och kristallen, ihop med den digitala jorden på ett enda ställe under kretsen mellan stift 7–8 och 28–29 (SLEA081 figur 1), två nettie-delar i schemat, och mottagarkontakten med skilda stift för matningsretur och videoretur (5-polig kontakt). Det är en schemaändring.

## 6. Termik

| Del | Effekt | Följd | Källa |
|---|---|---|---|
| U4, U5 (TVP5150AM1) | högst 185 mW var | +17 °C med inre plan, +23 °C utan; TJ högst 105 °C ger högst 88 respektive 82 °C omgivning | SLEA081; SLES209E termiska data |
| U1 (AP7361C, 5 → 3,3 V) | cirka 0,31 W (TVP-kretsarnas I/O 16 mA plus båda 1,8 V-regulatorerna, cirka 180 mA) | +34 °C vid 110 °C/W; fliken (stift 2, GND) på en kopparyta med vior till L2 sänker det | README "Komponentval"; strömmarna ur SLEA081 |
| U2 (AP2112K, digital 1,8 V) | 2 × 33,5 mA → 0,10 W | | SLEA081 |
| U3 (AP2112K, analog 1,8 V) | 2 × (39,2 + 7,9) mA = 94 mA → 0,14 W | Delens anteckning i schemat säger 78 mA; PLL_AVDD (FB2, FB4) matas också härifrån | SLEA081 |
| F1, F2 (PTC) | | Hållströmmen sjunker med temperaturen; med 0,45 A last och 0,75 A hållström vid rumstemperatur krymper marginalen nära varma delar. Minst 10 mm från U1, inte under Tang-kortet, vid kortkanten | README (Bourns MF-NSMF-kurvan) |

Kristallerna klarar ±20 ppm över −40…85 °C och TVP:n kräver ±50 ppm (README), så U1:s värme spelar ingen roll för dem; avståndet till kristallen är en störningsfråga.

## 7. Mekanik

- **Hål:** fyra M2 (H1–H4, 2,2 mm) i hörnen, 3,5 mm från kanterna, utanför Tang-kortets kontur så att skruvarna nås med Tang-kortet på plats. Inga ledningar inom cirka 2,5 mm från hålets centrum (skruvskalle). Tang-kortet hålls av stiftlisterna; kontrollera om det har egna hål.
- **Knappar:** S1 (OK) och S2 (NEXT) sitter på Tang-kortet och nås ovanifrån i sandwichen. Håll ingen av dem nere vid start (Core `BRINGUP.md`).
- **OLED:** sitter i dag på J6-3/J6-4 (SCL, SDA_A) och 3,3 V via sladdar till Tang-kortets stift. I sandwichen är de stiften inne i hylslisten. Dekoderkortet behöver en 4-polig kontakt för OLED:en (3,3 V, GND, SCL, SDA_A); det är en schemaändring.
- **RX5808-styrningen:** SPI CLK på J5-18, DATA på J6-17 och SEL på J6-16 är oanslutna på dekoderkortet ("wired straight to the receivers" i `dekoderkort.py`). I sandwichen går de inte att nå. De behöver dras till en kontakt, eller till mottagarkontakterna; schemaändring.
- **Kapsling:** öppningar för Tang-kortets USB-C och HDMI i ändarna, de två ingångskontakterna på långsidorna, J1 om den används, och knapparna och lysdioderna ovanpå. Höjden är dekoderkortet, cirka 11 mm, Tang-kortet och dess högsta del. Luft ska kunna röra sig mellan korten.

## 8. Öppet

- Raderna 20,32 mm isär och stift 1:s läge på J5/J6 är inte kontrollerade mot Sipeeds måttritning eller ett riktigt kort.
- Tang-kortets delar på undersidan och deras höjd.
- Kontakt för OLED och för RX5808-SPI (schemaändring, avsnitt 7).
- Den analoga 1,8 V-regulatorns ström i schemats anteckning (78 mA mot 94 mA, avsnitt 6).
- Kapacitiv avkoppling från Tang-kortets 3,3 V-stift (J6-19, J5-16) till jord vid hylslisten skulle ge 27 MHz-returen fler vägar än tre jordstift; stiften är oanslutna i schemat i dag (bedömning, schemaändring).
- Impedansbredderna är räknade med en formel, inte med leverantörens stack.
