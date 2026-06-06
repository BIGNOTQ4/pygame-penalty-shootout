# Tizenegyes játék

Egy grafikus focis tizenegyesrúgó játék Pythonban, Pygame használatával. A játékos csapatot, nehézséget és lövéstípust választ, egérrel céloz, lövéserőt időzít, majd megpróbál gólt lőni a vetődő kapus mellett.

## Funkciók

- 900x600-as Pygame ablak
- Modern, paneles UI gombokkal, hover effektekkel és jól olvasható szövegekkel
- Magyar ékezetes felület, például ő és ű karakterekkel
- Kezdőmenü nehézségi szint választással
- Könnyű, normál és nehéz játékmód
- Csapatválasztás legalább 5 különböző mezszínnel
- Lövéstípusok: erős lövés, helyezett lövés, panenka
- A lövéstípus befolyásolja a sebességet, pontosságot és védési esélyt
- Egeres célzás
- Mozgó lövéserő csík
- 10 lövéses játékmenet
- Játék vége képernyő végső összesítéssel és értékeléssel
- High score mentés és betöltés `save_data.json` fájlból
- Gól, védés és mellé lövés logika
- Pontszámok: gólok, védések, mellé lövések, összes lövés, pontosság
- Szebb focipálya és részletesebb kapuháló
- Egyszerű játékosfigura rúgó animációval
- Látványosabb kapusvetődés
- Labdaanimáció és forgáseffekt
- Generált hangok lövéshez, gólhoz, védéshez és mellé lövéshez
- Gólnál villanás, képernyőrázkódás és részecskeeffekt
- Moduláris, többfájlos `src` projektstruktúra

## Irányítás

- Egér mozgatása: célzás
- SPACE: lövés
- Bal egérgomb: lövés vagy menüválasztás
- 1: könnyű nehézség
- 2: normál nehézség
- 3: nehéz nehézség
- ENTER: meccs indítása a főmenüből
- R: újrakezdés
- ESC: kilépés

## Telepítés

1. Hozz létre egy virtuális környezetet:

```powershell
python -m venv .venv
```

2. Aktiváld a virtuális környezetet Windows PowerShellben:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Telepítsd a függőségeket:

```powershell
pip install -r requirements.txt
```

## Futtatás

```powershell
python main.py
```

## Használt technológiák

- Python
- Pygame

## Projektstruktúra

```text
Foca_game/
|-- main.py
|-- requirements.txt
|-- README.md
|-- .gitignore
|-- save_data.json
`-- src/
    |-- __init__.py
    |-- game.py
    |-- menu.py
    |-- ui.py
    |-- sounds.py
    |-- save_manager.py
    |-- player.py
    |-- goalkeeper.py
    `-- settings.py
```

## Modulok szerepe

- `main.py`: csak a belépési pont, létrehozza és elindítja a játékot
- `src/game.py`: fő játékmenet, fő ciklus, állapotkezelés és lövéslogika
- `src/menu.py`: főmenü és játék vége képernyő
- `src/ui.py`: UI segédek, gombok, panelek, szöveg és fontbetöltés
- `src/sounds.py`: kódból generált hanghatások
- `src/save_manager.py`: high score mentése és betöltése
- `src/player.py`: játékosfigura rajzolása és rúgó animációja
- `src/goalkeeper.py`: kapuslogika és kapus rajzolása
- `src/settings.py`: konstansok, színek, csapatok és lövéstípusok

## Jövőbeli fejlesztési ötletek

- Saját kép- és hangfájlok használata
- Kapus és játékos sprite-ok
- Bajnokság vagy karrier mód
- Részletesebb toplista több mentett eredménnyel
- Többfajta stadion vagy pálya
- Mobilisabb kapus AI
- Nehézségi szintek finomhangolása
- Teljes képernyős mód
