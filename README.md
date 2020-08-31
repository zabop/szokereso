# Szókereső
---
## Kliens-specifikus szókereső

Ez alapján a szótár alapján dolgozunk:  `/mnt/volume/jupyter/szokereso/negyedikfeladatUjraHat/vip_szotar_1.5.xlsx`
Minden "kliens" egy worksheet a szótárban. Minden kliens számára az adott worksheeten szereplő kifejezéseket keressük.
Az egy worksheeten belül, egy sorban található kifejezések egyenértékűek, ezeket hívom ekvivalencia-oszályoknak.
Bármelyik elemét megtaláljuk egy ekvivalencia-osztálynak egy szövegen belül, az ekvivalencia-osztály nevét mentjük el, ami az első elem a sorban.

### Szókereső script

Ennek legfejlettebb verziója itt található:
`/mnt/volume/jupyter/szokereso/negyedikfeladatUjraNyolc/szokereso_core.py`

Sok függvényt használ ebből a fájlból:
`/mnt/volume/jupyter/szokereso/negyedikfeladatUjraNyolc/szokereso_functions.py`

### Adatok napi aggregálása

Ez az, hogy megszámoljuk, egy nap alatt melyik entitás hányszor jelent meg. Ennek legfejlettebb verziója:
`/mnt/volume/jupyter/szokereso/negyedikfeladatUjraNyolc/dailyAggregPlotsImproved_dbcompatible.py`

### Adatok heti aggregála
Egy adott héten hányszor jelenik meg egy entitás. A napi aggregálóra épül (így ha az elhasal ez is, de egyszerűbb sokkal a kód).
Legfejlettebb verzió:
`/mnt/volume/jupyter/szokereso/negyedikfeladatUjraNyolc/weeklyaggreg_from_dailyaggreg_dbcompatible_output.py`

### Cooccurence mátrix

---
