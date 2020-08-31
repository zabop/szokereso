# Szókereső
---
## Kliens-specifikus szókereső

Ez alapján a szótár alapján dolgozunk:  `/mnt/volume/jupyter/szokereso/negyedikfeladatUjraHat/vip_szotar_1.5.xlsx`
Minden "kliens" egy worksheet a szótárban. Minden kliens számára az adott worksheeten szereplő kifejezéseket keressük.
Az egy worksheeten belül, egy sorban található kifejezések egyenértékűek, ezeket hívom ekvivalencia-oszályoknak.
Bármelyik elemét megtaláljuk egy ekvivalencia-osztálynak egy szövegen belül, az ekvivalencia-osztály nevét mentjük el, ami az első elem a sorban.

Kétórénként vannak bejövő fájlok. (Path bele van írva a scriptbe, nem kell vele törődni). Ezek nagyrésze olyan sorokat tartalmaz, amik már egy korábbi fájlban szerepeltek.

Először tehát az inputok duplikált-szűrése történik. A szűrt outputra eresszük rá az alább részletezett `szokereso_core.py`-t.

### Szókereső script

Ennek legfejlettebb verziója itt található:
`/mnt/volume/jupyter/szokereso/negyedikfeladatUjraNyolc/szokereso_core.py`

Sok függvényt használ ebből a fájlból:
`/mnt/volume/jupyter/szokereso/negyedikfeladatUjraNyolc/szokereso_functions.py`

### Adatok napi aggregálása

Ez az, hogy megszámoljuk, egy nap alatt melyik entitás hányszor jelent meg. Ennek legfejlettebb verziója:

    /mnt/volume/jupyter/szokereso/negyedikfeladatUjraNyolc/dailyAggregPlotsImproved_dbcompatible.py

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
