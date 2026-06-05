# Tizenegyesrugo jatek

Egy egyszeru, grafikus focis tizenegyesrugo jatek Pythonban, Pygame hasznalataval. A jatekos egerrel celoz, loveserot idozit, majd megprobal golt loni a veletlenszeruen vetodo kapus mellett.

## Funkciok

- 900x600-as Pygame ablak
- Kezdomenu nehezsegi szint valasztassal
- Konnyu, normal es nehez jatekmod
- Egeres celzas
- Mozgo lovesero csik
- 10 loveses jatekmenet
- Jatek vege kepernyo vegso osszesitessel
- Gol, vedes es melle loves logika
- Pontszamok: golok, vedesek, melle lovesek, osszes loves
- Szebb focipalya es reszletesebb kapuhalo
- Egyszeru jatekosfigura rugo animacioval
- Latvanyosabb kapusvetodes
- Labdaanimacio es forgaseffekt
- Hangok loveshez, golhoz, vedeshez es melle loveshez
- Golnal villanas, kepernyorazkodas es reszecskeeffekt

## Iranyitas

- Eger mozgatasa: celzas
- SPACE: loves
- Bal egergomb: loves vagy menuvalasztas
- 1: konnyu nehezseg
- 2: normal nehezseg
- 3: nehez nehezseg
- R: ujrakezdes
- ESC: kilepes

## Telepites

1. Hozz letre egy virtualis kornyezetet:

```powershell
python -m venv .venv
```

2. Aktivald a virtualis kornyezetet Windows PowerShellben:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Telepitsd a fuggosegeket:

```powershell
pip install -r requirements.txt
```

## Futtatas

```powershell
python main.py
```

## Hasznalt technologiak

- Python
- Pygame

## Projektstruktura

```text
Foca_game/
|-- main.py
|-- requirements.txt
|-- README.md
`-- .gitignore
```

## Jovobeli fejlesztesi otletek

- Sajat kep- es hangfajlok hasznalata
- Kapus es jatekos sprite-ok
- Bajnoksag vagy karrier mod
- Toplista
- Tobbfajta stadion vagy palya
- Mobilisabb kapus AI
- Nehezsegi szintek finomhangolasa
- Teljes kepernyos mod
