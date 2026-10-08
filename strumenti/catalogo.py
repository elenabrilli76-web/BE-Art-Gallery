#!/usr/bin/env python3
"""
Il catalogo di una mostra in un documento solo, da stampare.

Legge testi-critici/mostre/<mostra>.json — il testo della mostra e l'ordine
degli artisti — e per ogni artista la sua scheda.json. Produce, nella cartella
testi-critici/mostre/catalogo/:

- <mostra>.pdf  — A4, una pagina per la mostra e una per ogni artista
- <mostra>.docx — lo stesso, in Word, da ritoccare

Solo italiano: l'inglese resta nelle schede dei singoli artisti. Fondo bianco
per la stampa; l'oro e i grigi sono quelli della galleria.

    py strumenti\\catalogo.py i-luoghi-dell-anima
"""

import json
import sys
from pathlib import Path

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_BREAK
from docx.shared import Mm, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import critica as c  # noqa: E402  (stessi caratteri, colori e funzioni dei PDF singoli)

MOSTRE = c.RADICE / "testi-critici" / "mostre"
A4 = (210 * mm, 297 * mm)
M = 20 * mm                     # margine
COLONNE = 2                     # le schede delle opere, affiancate
GIUNTO = 8 * mm                 # spazio fra le colonne


def dati_opera(opera: dict) -> str:
    return "  ·  ".join(str(opera[k]) for k in ("anno", "tecnica", "misure", "provenienza") if opera.get(k))


# ----------------------------------------------------------------------------
# PDF
# ----------------------------------------------------------------------------

def piede(cv: Canvas, pagina: int) -> None:
    larghezza = A4[0]
    c.filetto(cv, M, M - 2 * mm, larghezza - 2 * M, 0.4)
    cv.setFont("Cormorant", 8)
    cv.setFillColor(c.GRIGIO)
    cv.drawString(M, M - 7 * mm, c.PIEDE)
    cv.drawRightString(larghezza - M, M - 7 * mm, str(pagina))


def pagina_mostra(cv: Canvas, cfg: dict) -> None:
    larghezza, altezza = A4
    utile = larghezza - 2 * M
    c.logo(cv, M, altezza - M, 34 * mm)
    y = altezza - M - 48 * mm
    y = c.scrivi(cv, cfg["titolo"], c.stile("t", fontName="Cormorant-Forte", fontSize=34, leading=38), M, y, utile)
    y = c.scrivi(cv, cfg["sottotitolo"], c.stile("s", fontName="Cormorant-Corsivo", fontSize=15,
                 leading=19, textColor=c.GRIGIO), M, y - 2, utile)
    y = c.scrivi(cv, cfg["luogo"], c.stile("l", fontSize=11, leading=14, textColor=c.GRIGIO), M, y - 1, utile)
    y -= 7 * mm
    c.filetto(cv, M, y, 24 * mm, 1.2)
    y -= 9 * mm
    # Il testo si adatta allo spazio, come nelle presentazioni singole
    for k in (1, 0.95, 0.9, 0.85, 0.8):
        st = c.stile("p", fontSize=12.5 * k, leading=17.5 * k, alignment=TA_JUSTIFY)
        alto = sum(c.misura(p, st, utile) + 4 * mm * k for p in cfg["testo"])
        if y - alto >= M + 4 * mm:
            break
    for p in cfg["testo"]:
        y = c.scrivi(cv, p, st, M, y, utile) - 4 * mm * k


def pagina_artista(cv: Canvas, scheda: dict) -> None:
    larghezza, altezza = A4
    utile = larghezza - 2 * M
    colonna = (utile - GIUNTO * (COLONNE - 1)) / COLONNE
    presentazione = scheda.get("presentazione", {}).get("it")
    opere = [o for o in scheda.get("opere", []) if o.get("didascalia", {}).get("it")]

    def stili(k):
        return dict(
            nome=c.stile("n", fontName="Cormorant-Forte", fontSize=26 * k, leading=30 * k),
            sotto=c.stile("st", fontName="Cormorant-Corsivo", fontSize=13 * k, leading=16 * k, textColor=c.GRIGIO),
            testo=c.stile("tx", fontSize=12 * k, leading=16.5 * k, alignment=TA_JUSTIFY),
            titolo=c.stile("ti", fontName="Cormorant-Corsivo", fontSize=14 * k, leading=17 * k),
            dati=c.stile("da", fontSize=9 * k, leading=11.5 * k, textColor=c.GRIGIO),
            dida=c.stile("di", fontSize=10.5 * k, leading=14 * k, alignment=TA_JUSTIFY),
        )

    def scheda_alta(o, s, k, largo):
        h = c.misura(o["titolo"], s["titolo"], largo)
        if dati_opera(o):
            h += c.misura(dati_opera(o), s["dati"], largo)
        return h + 6 * mm * k + c.misura(o["didascalia"]["it"], s["dida"], largo)

    def righe(lista):
        return [lista[i:i + COLONNE] for i in range(0, len(lista), COLONNE)]

    def larghezza_schede(n):
        return utile if n == 1 else colonna

    # Tutto su una pagina: si cerca la misura più grande che ci sta
    alto_utile = altezza - 2 * M - 6 * mm
    for k in (1, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65):
        s = stili(k)
        h = c.misura(scheda["nome"], s["nome"], utile) + 14 * mm * k
        if c.sottotitolo(scheda):
            h += c.misura(c.sottotitolo(scheda), s["sotto"], utile)
        if presentazione:
            h += c.misura(presentazione, s["testo"], utile) + 10 * mm * k
        largo = larghezza_schede(len(opere))
        for riga in righe(opere):
            h += max(scheda_alta(o, s, k, largo) for o in riga) + 8 * mm * k
        if h <= alto_utile:
            break

    y = altezza - M
    y = c.scrivi(cv, scheda["nome"], s["nome"], M, y, utile)
    if c.sottotitolo(scheda):
        y = c.scrivi(cv, c.sottotitolo(scheda), s["sotto"], M, y - 1, utile)
    y -= 5 * mm * k
    c.filetto(cv, M, y, 22 * mm, 1)
    y -= 8 * mm * k
    if presentazione:
        y = c.scrivi(cv, presentazione, s["testo"], M, y, utile) - 10 * mm * k

    largo = larghezza_schede(len(opere))
    for riga in righe(opere):
        fondo_riga = y
        for i, o in enumerate(riga):
            x = M + i * (colonna + GIUNTO)
            yy = c.scrivi(cv, o["titolo"], s["titolo"], x, y, largo)
            if dati_opera(o):
                yy = c.scrivi(cv, dati_opera(o), s["dati"], x, yy, largo)
            yy -= 2.5 * mm * k
            c.filetto(cv, x, yy, 10 * mm, 0.7)
            yy -= 3.5 * mm * k
            yy = c.scrivi(cv, o["didascalia"]["it"], s["dida"], x, yy, largo)
            fondo_riga = min(fondo_riga, yy)
        y = fondo_riga - 8 * mm * k


def pdf(cfg: dict, schede: list[dict], file: Path) -> None:
    cv = Canvas(str(file), pagesize=A4)
    cv.setTitle(f"{cfg['titolo']} — catalogo")
    cv.setAuthor("BE Art Gallery & Creative Lab")
    pagina_mostra(cv, cfg)
    piede(cv, 1)
    for n, scheda in enumerate(schede, start=2):
        cv.showPage()
        pagina_artista(cv, scheda)
        piede(cv, n)
    cv.save()


# ----------------------------------------------------------------------------
# Word
# ----------------------------------------------------------------------------

def word(cfg: dict, schede: list[dict], file: Path) -> None:
    doc = c._documento(A4, 20, f"{cfg['titolo']} — catalogo")
    p = lambda *a, **k: c._paragrafo(doc, *a, **k)  # noqa: E731

    doc.add_paragraph().add_run().add_picture(str(c.LOGO), width=Mm(34))
    p(dopo=30)
    p(cfg["titolo"], corpo=34, grassetto=True)
    p(cfg["sottotitolo"], corpo=15, colore=c.GRIGIO, corsivo=True)
    c._filetto(p(cfg["luogo"], corpo=11, colore=c.GRIGIO, dopo=18))
    for testo in cfg["testo"]:
        p(testo, corpo=12, giustificato=True, interlinea=17, dopo=9)

    for scheda in schede:
        doc.paragraphs[-1].add_run().add_break(WD_BREAK.PAGE)
        p(scheda["nome"], corpo=24, grassetto=True)
        ultimo = p(c.sottotitolo(scheda), corpo=12, colore=c.GRIGIO, corsivo=True, dopo=12)
        c._filetto(ultimo)
        if scheda.get("presentazione", {}).get("it"):
            p(scheda["presentazione"]["it"], corpo=11.5, giustificato=True, interlinea=15.5, dopo=14)
        opere = [o for o in scheda.get("opere", []) if o.get("didascalia", {}).get("it")]
        if not opere:
            continue
        colonne = 1 if len(opere) == 1 else COLONNE
        tabella = doc.add_table(rows=0, cols=colonne)
        tabella.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i in range(0, len(opere), colonne):
            celle = tabella.add_row().cells
            for cella, o in zip(celle, opere[i:i + colonne]):
                cella.paragraphs[0].text = ""
                def q(testo, **k):
                    par = cella.add_paragraph()
                    r = par.add_run(testo.replace("'", "’"))
                    r.font.name = c.FONT_WORD
                    r.font.size = Pt(k.get("corpo", 10))
                    r.font.color.rgb = c._rgb(k.get("colore", c.INCHIOSTRO))
                    r.italic = k.get("corsivo", False)
                    par.paragraph_format.space_after = Pt(k.get("dopo", 0))
                    if k.get("giustificato"):
                        par.alignment = 3
                    return par
                q(o["titolo"], corpo=13, corsivo=True)
                c._filetto(q(dati_opera(o) or " ", corpo=8.5, colore=c.GRIGIO, dopo=6))
                q(o["didascalia"]["it"], corpo=10, giustificato=True, dopo=12)
        p("")
    doc.save(file)


def main() -> None:
    mostra = sys.argv[1] if len(sys.argv) > 1 else "i-luoghi-dell-anima"
    cfg = json.loads((MOSTRE / f"{mostra}.json").read_text(encoding="utf-8"))
    schede = [json.loads((c.ARTISTI / nome / "scheda.json").read_text(encoding="utf-8"))
              for nome in cfg["ordine"]]
    uscita = MOSTRE / "catalogo"
    uscita.mkdir(exist_ok=True)
    pdf(cfg, schede, uscita / f"{mostra}.pdf")
    word(cfg, schede, uscita / f"{mostra}.docx")
    print(f"\n{cfg['titolo']}: {len(schede) + 1} pagine")
    for f in (f"{mostra}.pdf", f"{mostra}.docx"):
        print(f"   testi-critici/mostre/catalogo/{f}")
    print()


if __name__ == "__main__":
    main()
