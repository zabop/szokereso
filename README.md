# Szókereső
---
## Kliens-specifikus szókereső

Ez alapján a szótár alapján dolgozunk:  `/mnt/volume/jupyter/szokereso/negyedikfeladatUjraHat/vip_szotar_1.5.xlsx`
Minden "kliens" egy worksheet a szótárban. Minden kliens számára az adott worksheeten szereplő kifejezéseket keressük.
Az egy worksheeten belül, egy sorban található kifejezések egyenértékűek, ezeket hívom ekvivalencia-oszályoknak.
Bármelyik elemét megtaláljuk egy ekvivalencia-osztálynak egy szövegen belül, az ekvivalencia-osztály nevét mentjük el, ami az első elem a sorban.

Kétórénként vannak bejövő fájlok. (Path bele van írva a scriptbe). Ezek nagyrésze olyan sorokat tartalmaz, amik már egy korábbi fájlban szerepeltek.

Először tehát az inputok duplikált-szűrése történik. A szűrt outputra eresszük rá az alább részletezett `szokereso_core.py`-t.

### Szókereső script

Ennek legfejlettebb verziója itt található:
`/mnt/volume/jupyter/szokereso/negyedikfeladatUjraNyolc/szokereso_core.py`

Sok függvényt használ ebből a fájlból:
`/mnt/volume/jupyter/szokereso/negyedikfeladatUjraNyolc/szokereso_functions.py`

### Adatok napi aggregálása

Ez az, hogy megszámoljuk, egy nap alatt melyik entitás hányszor jelent meg. Ennek legfejlettebb verziója, amire épül a heti aggregáló:

    /mnt/volume/jupyter/szokereso/negyedikfeladatUjraNyolc/extended_dailyaggreg_outputsTwo.py
    
**Fejlődési lehetőség**: meg lehetne csinálni, hogy ez is szinten a `szokereso_functions.py`-ból hívja be a függvényeket, erre már nem volt időm.

### Adatok heti aggregála

Egy adott héten hányszor jelenik meg egy entitás. A napi aggregálóra épül (így ha az elhasal ez is, de egyszerűbb sokkal a kód).
Legfejlettebb verzió:
    
    /mnt/volume/jupyter/szokereso/negyedikfeladatUjraNyolc/weeklyaggreg_from_dailyaggreg_dbcompatible_output.py

Ha egy új direcory-ban indítjuk el, figyeljünk, hogy a napi aggregálás output már kész legyen, különben (mivel arra épül), nem fog rendesen működni.

**Fejlődési lehetőség**: ha `szokereso_functions.py`-ból hívná be a függvényeket, jobb lenne.

### Cooccurence mátrix

Nem automatikus az outputgyártás. Eddigi legfejlettebb verzió:

    /mnt/volume/jupyter/szokereso/ujfajlnezoHet/Cooc.ipynb

---

## Sokszótáras szókereső

Ez a kód nagyban hasonlít a kliens-specifikus szókeresésre. Most több szótárat használunk, de az eredményt nem bontjuk kliensekre. Futási időn nagyban gyorsít (egy-két nagyságrendet kb), hogy szűrünk duplikáltakra. Nagyot lassít az, hogy ekvivalencia-osztályokat használunk ('MSZP', 'Magyar Szocialista Párt', 'Szocik' - bármelyiket találjuk, mindig csak az ekvivalencia-osztály nevét, vagyis ebben a példában: MSZP jegyezzük fel az output csv-be). Valószínűleg lehet javítani sokat az algoritmuson, amivel csinálom. (Először minden névre külön keres, utána cseréljük le a neveket annak az ekvivalencia-osztálynak a nevére ahova tartoznak: ez valószínűleg nem túl computing power optimális, de egyszerű volt megírni & szerintem karbantartani. 

Eddigi legjelettebb verzió:

    /mnt/volume/jupyter/szokereso/ujfajlnezoNyolc/nagyszokereso_duplikalt_szuressel_ekvivalenciaosztalyokkal.py
    
Ez használja ezt:

    /mnt/volume/jupyter/szokereso/ujfajlnezoNyolc/szokereso_functions.py

Ez a fálj (és a többi `szokereso_functions.py`) heavily kommentelt, szerintem elég jól le lett írva, melyik függvény mit csinál. A `core` scriptek kommenteltsége nem jó, de gyakran kódból is egyértelmű szerintem, hogy mi történik (főleg, ha értjük hogy melyik függvény mit csinál, ahhoz ott van a kommentelt `szokereso_functions.py`).

**Fejlődési lehetőség**: lehetne egyesíteni ezt a `szokereso_functions.py`-t a fentebb említett `/mnt/volume/jupyter/szokereso/negyedikfeladatUjraNyolc/`-ban lévő `szokereso_functions.py`-jal. Ez a kettő nagyon hasonló.

---

Figyeljünk, hogy ne nevezzünk el fájlokat úgy, hogy azokban számok megjelennek, kivéve a dátum. Ha egyéb számok is vannak, az összezavarhatja az olyan függvényeket, amelyek a fájl nevéből következteti ki, mikori a fájl. (Tehát pl ne legyen olyan path egy fájlhoz hogy `/mappam/kliens2/futas4/fajl.valami`. A napi heti aggregáló annyira kis számításigényű, hogy mikor újraindítjuk, újrakezdi csinálni őket Július 1 -től (vagy amennyi bele van íva). A heti talán minden héten legyártja a pár ábrát. Mivel ez csak pár perc futás, nem láttam értelmét ezen javítani. Néha van olyan, hogy változók neveiben a Momentum, vagy arra utaló kifejezés szerepel, pl preMomFile, postMomFileSzokereso, postMomFileSzurt, postMomFileErrorlog. Ezek abból az időszakból maradványok, amikor csak a Momentumra írtuk a kódot. Később, mikor a többi kliensre kiterjesztettük, nem változtattam, így kicsit félrevezető lett a nevezéktan pár helyen. Ha kérdésünk van, Stackoverflow a barátunk, különösen, ha jól feltett kérdésünk van. Ha kevésbé jól megfogalmazott, akkor https://chat.stackoverflow.com/rooms/6/python -t tudom ajánlani. Munkaügyben feltett kérdés / bounty-k az elmúlt időszakból:

https://stackoverflow.com/questions/63598670/cooccurence-matrix-from-pandas-dataframe
https://stackoverflow.com/questions/63594550/apply-to-every-column-of-every-dataframe-of-an-excelfile-pandas
https://stackoverflow.com/questions/63583502/removing-duplicates-from-pandas-rows
https://stackoverflow.com/questions/63548321/pandas-dataframe-rows-to-dict-of-lists-using-first-value-of-each-row-as-key
https://stackoverflow.com/questions/63526631/create-as-many-columns-as-necessary-use-them-to-place-output-of-apply-in-a
https://stackoverflow.com/questions/63247382/how-to-count-the-number-of-rows-containing-both-a-value-in-a-set-of-columns-and
https://stackoverflow.com/questions/63237043/how-to-get-columns-containing-names-of-pre-defined-equivalence-classes-of-values
https://stackoverflow.com/questions/62943622/how-to-improve-accuracy-of-model-for-categorical-non-binary-foreign-language-s
https://stackoverflow.com/questions/60816403/get-week-number-with-week-start-day-different-than-monday-python


