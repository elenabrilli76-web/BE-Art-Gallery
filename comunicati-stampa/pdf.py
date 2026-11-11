"""Il PDF del comunicato stampa, da allegare alla mail.

    py comunicati-stampa\\pdf.py 2026-11-siamo-donne

Legge il blocco «## Comunicato» di comunicati-stampa/archivio/<nome>.md e salva
comunicati-stampa/archivio/pdf/<nome>.pdf (la cartella pdf/ non va su GitHub).

Dentro il blocco:
    # TITOLO          il titolo grande
    ## riga           sottotitolo; se viene dopo il testo, un'intestazione di sezione
    · voce            una voce d'elenco
    ---               il filetto oro; il paragrafo dopo è la nota sulla galleria
    riga vuota        separa i paragrafi
"""

import re
import sys
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (HRFlowable, Image, Paragraph, SimpleDocTemplate,
                                Spacer)
from xml.sax.saxutils import escape

QUI = Path(__file__).resolve().parent
MARCHIO = QUI.parent / "strumenti" / "marchio"
LOGO = MARCHIO / "logo-nero.png"

INCHIOSTRO = HexColor("#1E1B18")
GRIGIO = HexColor("#6B645B")
ORO = HexColor("#C9A227")

for nome, file in [("Cormorant", "Regular"), ("Cormorant-Bold", "Bold"),
                   ("Cormorant-SemiBold", "SemiBold"), ("Cormorant-Italic", "Italic")]:
    pdfmetrics.registerFont(TTFont(nome, str(MARCHIO / "font" / f"CormorantGaramond-{file}.ttf")))


def stile(nome, **kw):
    base = dict(fontName="Cormorant", fontSize=11, leading=13.8, textColor=INCHIOSTRO)
    base.update(kw)
    return ParagraphStyle(nome, **base)


def stili(scala: float = 1.0) -> dict:
    """Gli stili, ridotti di `scala` quando il testo non sta in una pagina."""
    return {k: ParagraphStyle(k, parent=v, fontSize=v.fontSize * scala, leading=v.leading * scala,
                              spaceBefore=v.spaceBefore * scala, spaceAfter=v.spaceAfter * scala)
            for k, v in BASE.items()}


BASE = {
    "etichetta": stile("etichetta", fontName="Cormorant-SemiBold", fontSize=10, textColor=ORO),
    "data": stile("data", fontSize=10, textColor=GRIGIO, spaceAfter=10),
    "titolo": stile("titolo", fontName="Cormorant-Bold", fontSize=22, leading=25, spaceAfter=4),
    "sotto": stile("sotto", fontName="Cormorant-Italic", fontSize=13, leading=17, textColor=GRIGIO),
    "sezione": stile("sezione", fontName="Cormorant-SemiBold", fontSize=11, textColor=ORO,
                     spaceBefore=8, spaceAfter=4),
    "testo": stile("testo", alignment=TA_JUSTIFY, spaceAfter=8),
    "voce": stile("voce", leftIndent=12, bulletIndent=0, spaceAfter=3),
    "info": stile("info", spaceAfter=1),
    "nota": stile("nota", fontName="Cormorant-Italic", fontSize=10, leading=12.5,
                  textColor=GRIGIO, alignment=TA_JUSTIFY),
}


def blocco_comunicato(md: str) -> list[str]:
    m = re.search(r"^## Comunicato\s*\n+```[^\n]*\n(.*?)\n```", md, re.S | re.M)
    if not m:
        sys.exit("Nel file manca il blocco «## Comunicato» fra ```.")
    return m.group(1).split("\n")


def corsivo_titoli(t: str) -> str:
    t = re.sub(r"«([^»]+)»", r"«<font name='Cormorant-Italic'>\1</font>»", escape(t))
    # gli indirizzi del sito diventano link cliccabili nel PDF
    return re.sub(r"\b(www\.beartgallery\.eu[^\s·<]*)", r"<a href='https://\1'>\1</a>", t)


def costruisci(righe: list[str], S: dict) -> list:
    out = [Image(str(LOGO), width=18 * mm, height=18 * mm * _rapporto(), hAlign="LEFT"),
           Spacer(1, 3 * mm)]
    paragrafo, iniziato, nota = [], False, False

    def chiudi():
        nonlocal paragrafo
        if paragrafo:
            stile_p = S["nota"] if nota else (S["info"] if len(paragrafo) > 1 else S["testo"])
            for i, r in enumerate(paragrafo):
                out.append(Paragraph(corsivo_titoli(r), stile_p))
            if len(paragrafo) > 1:
                out.append(Spacer(1, 6))
        paragrafo = []

    for i, r in enumerate(righe):
        r = r.rstrip()
        if i == 0:
            out.append(Paragraph(escape(r).upper(), S["etichetta"]))
        elif i == 1:
            out.append(Paragraph(escape(r), S["data"]))
        elif r.startswith("# "):
            out.append(Paragraph(escape(r[2:]), S["titolo"]))
        elif r.startswith("## "):
            chiudi()
            out.append(Paragraph(corsivo_titoli(r[3:]), S["sezione"] if iniziato else S["sotto"]))
        elif r.startswith("· "):
            chiudi()
            out.append(Paragraph(corsivo_titoli(r[2:]), S["voce"], bulletText="·"))
        elif r == "---":
            chiudi()
            out.append(Spacer(1, 6))
            out.append(HRFlowable(width="25%", thickness=0.8, color=ORO, hAlign="LEFT", spaceAfter=8))
            nota = True
        elif r == "":
            chiudi()
            if out and isinstance(out[-1], Paragraph) and out[-1].style is S["voce"]:
                out.append(Spacer(1, 6))
            if not iniziato and len(out) > 4:
                out.append(Spacer(1, 6))
                out.append(HRFlowable(width="100%", thickness=0.5, color=ORO, spaceAfter=10))
                iniziato = True
        else:
            paragrafo.append(r)
    chiudi()
    return out


def _rapporto() -> float:
    from reportlab.lib.utils import ImageReader
    w, h = ImageReader(str(LOGO)).getSize()
    return h / w


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    nome = sys.argv[1].removesuffix(".md")
    sorgente = QUI / "archivio" / f"{nome}.md"
    uscita = QUI / "archivio" / "pdf" / f"{nome}.pdf"
    uscita.parent.mkdir(exist_ok=True)
    righe = blocco_comunicato(sorgente.read_text(encoding="utf-8"))
    # un comunicato sta in una pagina: se non ci sta, il carattere scende un poco
    for scala in (1.0, 0.97, 0.94, 0.91, 0.88):
        doc = SimpleDocTemplate(str(uscita), pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm,
                                topMargin=12 * mm, bottomMargin=12 * mm,
                                title="Comunicato stampa", author="BE Art Gallery")
        doc.build(costruisci(righe, stili(scala)))
        if doc.page == 1:
            break
    else:
        print("Attenzione: il comunicato non sta in una pagina, conviene accorciarlo.")
    print(f"Salvato: {uscita}")


if __name__ == "__main__":
    main()
