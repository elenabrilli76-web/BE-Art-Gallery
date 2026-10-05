#!/usr/bin/env python3
"""
I PDF dei testi critici d'artista.

Legge la scheda di un artista, testi-critici/artisti/<nome-cognome>/scheda.json,
e produce nella sua cartella pdf/:

- presentazione.pdf — la sintesi critica in A5, da consegnare all'artista e da
  stampare per la sala
- una didascalia in A6 per ogni opera analizzata, da mettere accanto al quadro

    py strumenti\\critica.py nome-cognome      un artista
    py strumenti\\critica.py                   tutti

La scheda la scrive Claude: qui non c'è niente da comporre a mano.
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

CARTELLA = Path(__file__).resolve().parent
RADICE = CARTELLA.parent
ARTISTI = RADICE / "testi-critici" / "artisti"
FONT = CARTELLA / "marchio" / "font"
LOGO = CARTELLA / "marchio" / "logo-nero.png"   # il marchio chiaro vuole il suo fondo nero

A5 = (148 * mm, 210 * mm)
A6_ORIZZONTALE = (148 * mm, 105 * mm)

CARTA = HexColor("#FAF7F0")
INCHIOSTRO = HexColor("#1E1B18")
GRIGIO = HexColor("#6B645B")
ORO = HexColor("#C9A227")   # l'oro antico del logo, lo stesso dei social

# Le soglie della procedura: oltre, il testo non sta più nel suo formato
LIMITI = {"presentazione": (500, 600), "didascalia": (150, 300)}

PIEDE = "BE Art Gallery & Creative Lab  ·  Pistoia  ·  beartgallery.eu"

# Un carattere solo, quello delle locandine, nei suoi pesi
for nome, file in {
    "Cormorant": "CormorantGaramond-Regular.ttf",
    "Cormorant-Forte": "CormorantGaramond-SemiBold.ttf",
    "Cormorant-Corsivo": "CormorantGaramond-Italic.ttf",
}.items():
    pdfmetrics.registerFont(TTFont(nome, str(FONT / file)))


def stile(nome, **opzioni) -> ParagraphStyle:
    base = dict(fontName="Cormorant", fontSize=11.5, leading=15.5,
                textColor=INCHIOSTRO, alignment=TA_LEFT)
    base.update(opzioni)
    return ParagraphStyle(nome, **base)


def nome_file(testo: str) -> str:
    """«Il colore come linguaggio» → il-colore-come-linguaggio"""
    piano = unicodedata.normalize("NFKD", testo).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", piano.lower()).strip("-") or "opera"


def controlla(etichetta: str, testo: str, tipo: str) -> None:
    minimo, massimo = LIMITI[tipo]
    n = len(testo)
    if not minimo <= n <= massimo:
        print(f"   ⚠ {etichetta}: {n} caratteri, la procedura ne vuole {minimo}–{massimo}")


def scrivi(c: Canvas, testo: str, st: ParagraphStyle, x: float, y: float, larghezza: float) -> float:
    """Posa un paragrafo con il bordo superiore in y; restituisce dove finisce."""
    # Apostrofi tipografici: quello dritto della tastiera sulla carta si nota
    testo = testo.replace("'", "\u2019").replace("\n", "<br/>")
    p = Paragraph(testo, st)
    _, altezza = p.wrap(larghezza, 10_000)
    p.drawOn(c, x, y - altezza)
    return y - altezza


def fondo(c: Canvas, formato) -> None:
    c.setFillColor(CARTA)
    c.rect(0, 0, *formato, stroke=0, fill=1)


def filetto(c: Canvas, x: float, y: float, lunghezza: float, spessore=0.6) -> None:
    c.setStrokeColor(ORO)
    c.setLineWidth(spessore)
    c.line(x, y, x + lunghezza, y)


def logo(c: Canvas, x: float, y_alto: float, larghezza: float) -> None:
    altezza = larghezza * 616 / 888
    c.drawImage(str(LOGO), x, y_alto - altezza, larghezza, altezza, mask="auto")


def piede(c: Canvas, larghezza_pagina: float, margine: float, base: float, corpo=7.5) -> None:
    filetto(c, margine, base + 9, larghezza_pagina - 2 * margine, 0.4)
    c.setFont("Cormorant", corpo)
    c.setFillColor(GRIGIO)
    c.drawCentredString(larghezza_pagina / 2, base, PIEDE)


def presentazione(scheda: dict, uscita: Path) -> Path:
    testi = scheda["presentazione"]
    controlla("presentazione (it)", testi["it"], "presentazione")

    larghezza, altezza = A5
    m = 16 * mm
    utile = larghezza - 2 * m
    file = uscita / "presentazione.pdf"
    c = Canvas(str(file), pagesize=A5)
    c.setTitle(f"{scheda['nome']} — testo critico")
    c.setAuthor("BE Art Gallery & Creative Lab")
    fondo(c, A5)

    logo(c, m, altezza - m, 24 * mm)
    y = altezza - m - 30 * mm

    y = scrivi(c, scheda["nome"], stile("nome", fontName="Cormorant-Forte",
               fontSize=25, leading=28), m, y, utile)
    if scheda.get("vive_e_lavora"):
        y = scrivi(c, f"vive e lavora a {scheda['vive_e_lavora']}",
                   stile("luogo", fontName="Cormorant-Corsivo", fontSize=11,
                         leading=14, textColor=GRIGIO), m, y - 2, utile)
    y -= 5 * mm
    filetto(c, m, y, 18 * mm, 1)
    y -= 6 * mm

    corpo = stile("it", fontSize=12, leading=16.5, alignment=TA_JUSTIFY)
    y = scrivi(c, testi["it"], corpo, m, y, utile)

    if testi.get("en"):
        y -= 6 * mm
        filetto(c, m, y, 8 * mm, 0.6)
        y -= 5 * mm
        scrivi(c, testi["en"], stile("en", fontName="Cormorant-Corsivo",
               fontSize=10.5, leading=14, textColor=GRIGIO,
               alignment=TA_JUSTIFY), m, y, utile)

    piede(c, larghezza, m, m)
    c.save()
    return file


def didascalia(scheda: dict, opera: dict, uscita: Path) -> Path:
    testi = opera["didascalia"]
    controlla(f"didascalia «{opera['titolo']}» (it)", testi["it"], "didascalia")

    larghezza, altezza = A6_ORIZZONTALE
    m = 11 * mm
    utile = larghezza - 2 * m
    file = uscita / f"opera-{nome_file(opera['titolo'])}.pdf"
    c = Canvas(str(file), pagesize=A6_ORIZZONTALE)
    c.setTitle(f"{scheda['nome']} — {opera['titolo']}")
    c.setAuthor("BE Art Gallery & Creative Lab")
    fondo(c, A6_ORIZZONTALE)

    # Il cartellino da mostra: chi, cosa, come — poi la lettura
    logo(c, larghezza - m - 15 * mm, altezza - m + 2 * mm, 15 * mm)
    y = altezza - m
    y = scrivi(c, scheda["nome"], stile("artista", fontName="Cormorant-Forte",
               fontSize=11, leading=13), m, y, utile - 18 * mm)
    y = scrivi(c, opera["titolo"], stile("titolo", fontName="Cormorant-Corsivo",
               fontSize=16, leading=19), m, y - 1, utile - 18 * mm)
    dati = "  ·  ".join(str(opera[k]) for k in ("anno", "tecnica", "misure") if opera.get(k))
    if dati:
        y = scrivi(c, dati, stile("dati", fontSize=9, leading=11.5,
                   textColor=GRIGIO), m, y - 1, utile)
    y -= 3.5 * mm
    filetto(c, m, y, 12 * mm, 0.8)
    y -= 3.5 * mm

    y = scrivi(c, testi["it"], stile("dit", fontSize=10.5, leading=13.5,
               alignment=TA_JUSTIFY), m, y, utile)
    if testi.get("en"):
        scrivi(c, testi["en"], stile("den", fontName="Cormorant-Corsivo",
               fontSize=9, leading=11.5, textColor=GRIGIO,
               alignment=TA_JUSTIFY), m, y - 2.5 * mm, utile)

    piede(c, larghezza, m, 7 * mm, corpo=6.5)
    c.save()
    return file


def artista(cartella: Path) -> list[Path]:
    scheda = json.loads((cartella / "scheda.json").read_text(encoding="utf-8"))
    uscita = cartella / "pdf"
    uscita.mkdir(exist_ok=True)
    print(f"\n{scheda['nome']}")
    prodotti = []
    if scheda.get("presentazione", {}).get("it"):
        prodotti.append(presentazione(scheda, uscita))
    for opera in scheda.get("opere", []):
        if opera.get("didascalia", {}).get("it"):
            prodotti.append(didascalia(scheda, opera, uscita))
    for file in prodotti:
        print(f"   {file.relative_to(RADICE)}")
    return prodotti


def main() -> None:
    if len(sys.argv) > 1:
        cartelle = [ARTISTI / sys.argv[1]]
        if not (cartelle[0] / "scheda.json").exists():
            print(f"\nNon trovo testi-critici/artisti/{sys.argv[1]}/scheda.json\n")
            raise SystemExit(1)
    else:
        # Le cartelle che iniziano con _ sono modelli, non artisti
        cartelle = sorted(p.parent for p in ARTISTI.glob("*/scheda.json")
                          if not p.parent.name.startswith("_"))
    for cartella in cartelle:
        artista(cartella)
    print()


if __name__ == "__main__":
    main()
