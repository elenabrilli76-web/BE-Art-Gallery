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

def carta(cv: Canvas) -> None:
    """Lo sfondo crema dei documenti singoli, su tutta la pagina."""
    c.fondo(cv, A4)


def piede(cv: Canvas, pagina: int) -> None:
    larghezza = A4[0]
    c.filetto(cv, M, M - 2 * mm, larghezza - 2 * M, 0.4)
    cv.setFont("Cormorant", 8)
    cv.setFillColor(c.GRIGIO)
    cv.drawString(M, M - 7 * mm, c.PIEDE)
    cv.drawRightString(larghezza - M, M - 7 * mm, str(pagina))


def testo_mostra(cv: Canvas, cfg: dict, pagina: int) -> int:
    """La presentazione della mostra: copertina, poi il testo che scorre sulle
    pagine che servono. Le voci {"titolo": ...} sono i titoletti dei paragrafi.
    Restituisce il numero dell'ultima pagina usata."""
    larghezza, altezza = A4
    utile = larghezza - 2 * M
    fondo = M + 6 * mm
    carta(cv)
    c.logo(cv, M, altezza - M, 34 * mm)
    y = altezza - M - 48 * mm
    y = c.scrivi(cv, cfg["titolo"], c.stile("t", fontName="Cormorant-Forte", fontSize=34, leading=38), M, y, utile)
    y = c.scrivi(cv, cfg["sottotitolo"], c.stile("s", fontName="Cormorant-Corsivo", fontSize=15,
                 leading=19, textColor=c.GRIGIO), M, y - 2, utile)
    y = c.scrivi(cv, cfg["luogo"], c.stile("l", fontSize=11, leading=14, textColor=c.GRIGIO), M, y - 1, utile)
    y -= 7 * mm
    c.filetto(cv, M, y, 24 * mm, 1.2)
    y -= 9 * mm

    corpo = c.stile("p", fontSize=12, leading=17, alignment=TA_JUSTIFY)
    titoletto = c.stile("h", fontName="Cormorant-Corsivo", fontSize=16, leading=20)
    voci = cfg["testo"]
    for i, voce in enumerate(voci):
        if isinstance(voce, dict):
            # Un titoletto non resta mai da solo in fondo alla pagina
            dopo = voci[i + 1] if i + 1 < len(voci) else ""
            serve = c.misura(voce["titolo"], titoletto, utile) + 6 * mm + 3 * corpo.leading
            if y - serve < fondo:
                piede(cv, pagina)
                cv.showPage()
                carta(cv)
                pagina += 1
                y = altezza - M
            y = c.scrivi(cv, voce["titolo"], titoletto, M, y - 3 * mm, utile) - 3 * mm
            continue
        par = c.Paragraph(voce.replace("'", "\u2019"), corpo)
        while True:
            _, alto = par.wrap(utile, 10_000)
            if y - alto >= fondo:
                par.drawOn(cv, M, y - alto)
                y -= alto + 4 * mm
                break
            pezzi = par.split(utile, y - fondo)
            if len(pezzi) == 2:
                _, h0 = pezzi[0].wrap(utile, 10_000)
                pezzi[0].drawOn(cv, M, y - h0)
                par = pezzi[1]
            piede(cv, pagina)
            cv.showPage()
            carta(cv)
            pagina += 1
            y = altezza - M
    piede(cv, pagina)
    return pagina


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
    n = testo_mostra(cv, cfg, 1)
    for scheda in schede:
        cv.showPage()
        carta(cv)
        n += 1
        pagina_artista(cv, scheda)
        piede(cv, n)
    cv.save()


# ----------------------------------------------------------------------------
# Word
# ----------------------------------------------------------------------------

def titoletto(doc, testo, livello, corpo, grassetto=False, corsivo=True):
    """Un titolo con lo stile Titolo di Word: compare nella struttura del
    documento e in Google Docs resta un titolo, non testo ingrandito."""
    par = doc.add_paragraph(style=f"Heading {livello}")
    par.paragraph_format.keep_with_next = True
    par.paragraph_format.space_before = Pt(12 if livello == 2 else 0)
    par.paragraph_format.space_after = Pt(4)
    r = par.add_run(testo.replace("'", "\u2019"))
    r.font.name = c.FONT_WORD
    r._element.rPr.rFonts.set(c.qn("w:eastAsia"), c.FONT_WORD)
    r.font.size = Pt(corpo)
    r.font.color.rgb = c._rgb(c.INCHIOSTRO)
    r.bold = grassetto
    r.italic = corsivo
    return par


def word(cfg: dict, schede: list[dict], file: Path) -> None:
    doc = c._documento(A4, 20, f"{cfg['titolo']} — catalogo")
    # Il colore di pagina crema: Word lo mostra e lo stampa se nelle opzioni
    # di stampa è attivo «Stampa colori e immagini di sfondo»
    sfondo = c.OxmlElement("w:background")
    sfondo.set(c.qn("w:color"), c.CARTA.hexval()[2:].upper())
    doc.element.insert(0, sfondo)
    mostra = c.OxmlElement("w:displayBackgroundShape")
    doc.settings.element.insert(0, mostra)
    p = lambda *a, **k: c._paragrafo(doc, *a, **k)  # noqa: E731

    doc.add_paragraph().add_run().add_picture(str(c.LOGO), width=Mm(34))
    p(dopo=30)
    p(cfg["titolo"], corpo=34, grassetto=True)
    p(cfg["sottotitolo"], corpo=15, colore=c.GRIGIO, corsivo=True)
    c._filetto(p(cfg["luogo"], corpo=11, colore=c.GRIGIO, dopo=18))
    for voce in cfg["testo"]:
        if isinstance(voce, dict):
            titoletto(doc, voce["titolo"], livello=2, corpo=15)
        else:
            p(voce, corpo=12, giustificato=True, interlinea=17, dopo=9)

    for scheda in schede:
        doc.paragraphs[-1].add_run().add_break(WD_BREAK.PAGE)
        titoletto(doc, scheda["nome"], livello=1, corpo=24, grassetto=True, corsivo=False)
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
    print(f"\n{cfg['titolo']}: testo della mostra e {len(schede)} schede")
    for f in (f"{mostra}.pdf", f"{mostra}.docx"):
        print(f"   testi-critici/mostre/catalogo/{f}")
    print()


if __name__ == "__main__":
    main()


# ----------------------------------------------------------------------------
# HTML per Google Docs: Drive lo converte in un documento modificabile
# ----------------------------------------------------------------------------

LOGO_PUBBLICO = ("https://raw.githubusercontent.com/elenabrilli76-web/BE-Art-Gallery/"
                 "be-art-gallery-creazione-contenuti/strumenti/marchio/logo-nero.png")


def html(cfg: dict, schede: list[dict]) -> str:
    """Google Docs, importando, rispetta caratteri e corsivi definiti a classi,
    ma non i colori dei bordi né page-break sui titoli: quelli vanno in linea,
    e il salto di pagina è un <br> dedicato."""
    from html import escape

    def e(t):
        return escape(t.replace("'", "\u2019"))

    stile = """<style>@page{size:21cm 29.7cm;margin:2cm}
body,p,h1,h2,td{font-family:Garamond,serif;color:#1E1B18}
p{font-size:12pt;line-height:1.4;text-align:justify;margin:0 0 8pt 0}
h1{font-size:24pt;font-weight:bold;margin:0 0 2pt 0}
h2{font-size:15pt;font-style:italic;font-weight:normal;margin:14pt 0 4pt 0}
.s{font-size:12pt;font-style:italic;color:#6B645B;margin:0}
.l{font-size:11pt;color:#6B645B}
.pr{font-size:11.5pt;margin-bottom:14pt}
.t{font-size:13pt;font-style:italic;margin:0;text-align:left}
.d{font-size:8.5pt;color:#6B645B;margin:0 0 5pt 0;text-align:left}
.c{font-size:10pt}
td{vertical-align:top;padding:0 10pt 12pt 0;border:none}
table{border-collapse:collapse;width:100%;border:none}
</style>"""
    oro = ' style="border-bottom:1.5pt solid #C9A227;padding-bottom:6pt;margin-bottom:12pt"'
    oro_d = ' style="border-bottom:1pt solid #C9A227;padding-bottom:4pt"'
    salto = '<br style="page-break-before:always;clear:both">'
    out = [f'<html><head><meta charset="utf-8">{stile}</head><body style="background-color:#FAF7F0">']
    out.append(f'<p><img src="{LOGO_PUBBLICO}" width="160"></p>')
    out.append(f'<h1 style="font-size:32pt;margin-top:24pt">{e(cfg["titolo"])}</h1>')
    out.append(f'<p class="s">{e(cfg["sottotitolo"])}</p>')
    out.append(f'<p class="l"{oro}>{e(cfg["luogo"])}</p>')
    for voce in cfg["testo"]:
        out.append(f'<h2>{e(voce["titolo"])}</h2>' if isinstance(voce, dict) else f'<p>{e(voce)}</p>')
    for s in schede:
        out.append(salto)
        out.append(f'<h1>{e(s["nome"])}</h1>')
        out.append(f'<p class="s"{oro}>{e(c.sottotitolo(s)) or "&nbsp;"}</p>')
        if s.get("presentazione", {}).get("it"):
            out.append(f'<p class="pr">{e(s["presentazione"]["it"])}</p>')
        opere = [o for o in s.get("opere", []) if o.get("didascalia", {}).get("it")]
        if not opere:
            continue
        col = 1 if len(opere) == 1 else COLONNE
        out.append("<table>")
        for i in range(0, len(opere), col):
            celle = "".join(f'<td width="{100 // col}%"><p class="t">{e(o["titolo"])}</p>'
                            f'<p class="d"{oro_d}>{e(dati_opera(o)) or "&nbsp;"}</p>'
                            f'<p class="c">{e(o["didascalia"]["it"])}</p></td>' for o in opere[i:i + col])
            out.append(f"<tr>{celle}</tr>")
        out.append("</table>")
    out.append("</body></html>")
    return "\n".join(out)
