#!/usr/bin/env python3
"""
Il catalogo di una mostra in formato libro: pagine in multipli di 4, nessuna
pagina con spazi vuoti, una miniatura per ogni opera degli artisti.

Legge testi-critici/mostre/<mostra>.json, le schede degli artisti e il testo
della galleria (testi-critici/galleria.json). Le foto restano in locale, in
testi-critici/mostre/catalogo/foto/:

    copertina.jpg                     la locandina
    <artista>/<opera>.jpg             già ritagliate sul quadro
    galleria/*.jpg                    la galleria allestita per la mostra

Produce in testi-critici/mostre/catalogo/:

- <mostra>-libro.pdf          A4, pagine in ordine: per la tipografia
- <mostra>-libro-A3.pdf       due pagine per foglio A3, già nell'ordine di
                              piegatura: si stampa fronte-retro (lato corto),
                              si piega a metà e si pinza

Le schede con "vive_e_lavora" o un nome che comincia per E.B.Art hanno una
pagina ciascuna, con le miniature; le collezioni private si raccolgono in
una pagina sola, con il carattere che si adatta fino a riempirla.

    py strumenti\\libro.py i-luoghi-dell-anima
"""

import json
import sys
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

sys.path.insert(0, str(Path(__file__).resolve().parent))
import critica as c  # noqa: E402

MOSTRE = c.RADICE / "testi-critici" / "mostre"
GALLERIA = c.RADICE / "testi-critici" / "galleria.json"
W, H = 210 * mm, 297 * mm
M = 18 * mm                     # margine
BASSO = M + 8 * mm              # sopra il piede
UTILE = W - 2 * M
GIUNTO = 8 * mm
COLONNA = (UTILE - GIUNTO) / 2
NERO = HexColor("#141312")


def dati_opera(o: dict) -> str:
    return "  ·  ".join(str(o[k]) for k in ("anno", "tecnica", "misure", "provenienza") if o.get(k))


def opere(scheda: dict) -> list[dict]:
    return [o for o in scheda.get("opere", []) if o.get("didascalia", {}).get("it")]


def con_miniature(scheda: dict) -> bool:
    return bool(scheda.get("vive_e_lavora")) or scheda["nome"].startswith("E.B.Art")


# ----------------------------------------------------------------------------
# Elementi comuni
# ----------------------------------------------------------------------------

def carta(cv):
    c.fondo(cv, (W, H))


def piede(cv, n):
    """Il numero di pagina sul lato esterno: a destra le dispari, a sinistra le pari."""
    c.filetto(cv, M, M + 3 * mm, UTILE, 0.4)
    cv.setFont("Cormorant", 8)
    cv.setFillColor(c.GRIGIO)
    if n % 2:
        cv.drawString(M, M - 2 * mm, c.PIEDE)
        cv.drawRightString(W - M, M - 2 * mm, str(n))
    else:
        cv.drawString(M, M - 2 * mm, str(n))
        cv.drawRightString(W - M, M - 2 * mm, c.PIEDE)


def etichetta(cv, testo, y, x=M, colore=c.ORO, corpo=9):
    """Una riga in maiuscolo spaziato, come «ARTISTI IN MOSTRA» sulla locandina."""
    cv.setFont("Cormorant-Forte", corpo)
    cv.setFillColor(colore)
    t = cv.beginText(x, y - corpo)
    t.setCharSpace(corpo * 0.25)
    t.textOut(testo.upper())
    t.setCharSpace(0)          # la spaziatura resta sull'oggetto testo, non sul resto della pagina
    cv.drawText(t)
    return y - corpo * 1.6


def foto(cv, file: Path, x, y_alto, largo, alto, allinea="centro"):
    """Una foto dentro un riquadro, senza deformarla. Restituisce (larghezza, altezza)
    effettive. Se la foto manca, un riquadro sottile ne tiene il posto."""
    if not file.exists():
        print(f"   ⚠ manca la foto {file.relative_to(c.RADICE)}")
        cv.setStrokeColor(c.GRIGIO)
        cv.setLineWidth(0.3)
        cv.rect(x, y_alto - alto, largo, alto)
        return largo, alto
    iw, ih = Image.open(file).size
    s = min(largo / iw, alto / ih)
    w, h = iw * s, ih * s
    dx = (largo - w) / 2 if allinea == "centro" else 0
    cv.drawImage(ImageReader(str(file)), x + dx, y_alto - h, w, h)
    return w, h


def proporzione(file: Path) -> float:
    """Altezza su larghezza; 3/4 se la foto manca."""
    if not file.exists():
        return 0.75
    iw, ih = Image.open(file).size
    return ih / iw


# ----------------------------------------------------------------------------
# Le pagine
# ----------------------------------------------------------------------------

def copertina(cv, cfg, cartella):
    """La locandina a tutta larghezza; sotto, il nero della sua fascia col logo."""
    file = cartella / "foto" / "copertina.jpg"
    if not file.exists():
        carta(cv)
        c.scrivi(cv, cfg["titolo"], c.stile("t", fontName="Cormorant-Forte", fontSize=40, leading=44),
                 M, H / 2, UTILE)
        print("   ⚠ manca la copertina: foto/copertina.jpg")
        return
    im = Image.open(file).convert("RGB")
    iw, ih = im.size
    fondo = im.resize((1, 1), box=(0, ih - 5, iw, ih)).getpixel((0, 0))
    cv.setFillColorRGB(*(v / 255 for v in fondo))
    cv.rect(0, 0, W, H, stroke=0, fill=1)
    h = W * ih / iw
    if h > H:                                   # più alta della pagina: si adatta in altezza
        w = H * iw / ih
        cv.drawImage(ImageReader(im), (W - w) / 2, 0, w, H)
    else:
        cv.drawImage(ImageReader(im), 0, H - h, W, h)


def frontespizio(cv, cfg, schede):
    carta(cv)
    c.logo(cv, M, H - M, 34 * mm)
    y = H - M - 60 * mm
    y = c.scrivi(cv, cfg["titolo"], c.stile("t", fontName="Cormorant-Forte", fontSize=46, leading=50), M, y, UTILE)
    y = c.scrivi(cv, cfg["sottotitolo"], c.stile("s", fontName="Cormorant-Corsivo", fontSize=18, leading=23,
                 textColor=c.GRIGIO), M, y - 4, UTILE)
    y = c.scrivi(cv, cfg["luogo"], c.stile("l", fontSize=12.5, leading=16, textColor=c.GRIGIO), M, y - 2, UTILE)
    y -= 9 * mm
    c.filetto(cv, M, y, 24 * mm, 1.2)
    y -= 12 * mm
    y = etichetta(cv, "Artisti in mostra", y, corpo=11)
    nome = c.stile("n", fontSize=19, leading=26)
    for s in schede:
        if con_miniature(s) and not s["nome"].startswith("E.B.Art"):
            y = c.scrivi(cv, s["nome"], nome, M, y, UTILE)
    if any(s["nome"].startswith("E.B.Art") for s in schede):
        y = c.scrivi(cv, "E.B.Art", nome, M, y, UTILE)
    if cfg.get("collezioni"):
        y -= 6 * mm
        c.filetto(cv, M, y, 24 * mm, 0.6)
        y -= 5 * mm
        y = c.scrivi(cv, cfg["collezioni"], c.stile("c", fontName="Cormorant-Corsivo", fontSize=16, leading=20,
                     textColor=c.ORO), M, y, UTILE)
    if cfg.get("orari"):
        c.scrivi(cv, cfg["orari"], c.stile("o", fontSize=12, leading=15, textColor=c.GRIGIO), M, BASSO + 15, UTILE)


def scorri(cv, voci, k, disegna, n0, titolo=""):
    """Il testo della mostra che scorre sulle pagine. Restituisce quante pagine
    servono e quanto spazio resta sull'ultima."""
    corpo = c.stile("p", fontSize=12 * k, leading=17 * k, alignment=TA_JUSTIFY)
    tit = c.stile("h", fontName="Cormorant-Corsivo", fontSize=16 * k, leading=20 * k)
    pagina, y = 1, H - M

    def nuova():
        nonlocal pagina, y
        if disegna:
            piede(cv, n0 + pagina - 1)
            cv.showPage()
            carta(cv)
        pagina += 1
        y = H - M

    if disegna:
        carta(cv)
        y = etichetta(cv, titolo, y) - 4 * mm
    else:
        y -= 9 * 1.6 + 4 * mm
    for i, voce in enumerate(voci):
        if isinstance(voce, dict):
            serve = c.misura(voce["titolo"], tit, UTILE) + 6 * mm * k + 3 * corpo.leading
            if y - serve < BASSO:
                nuova()
            if disegna:
                c.scrivi(cv, voce["titolo"], tit, M, y - 3 * mm * k, UTILE)
            y -= c.misura(voce["titolo"], tit, UTILE) + 6 * mm * k
            continue
        par = Paragraph(voce.replace("'", "’"), corpo)
        while True:
            _, alto = par.wrap(UTILE, 10_000)
            if y - alto >= BASSO:
                if disegna:
                    par.drawOn(cv, M, y - alto)
                y -= alto + 4 * mm * k
                break
            pezzi = par.split(UTILE, y - BASSO)
            if len(pezzi) == 2:
                _, h0 = pezzi[0].wrap(UTILE, 10_000)
                if disegna:
                    pezzi[0].drawOn(cv, M, y - h0)
                par = pezzi[1]
            nuova()
    if disegna:
        piede(cv, n0 + pagina - 1)
    return pagina, y - BASSO


def testo_mostra(cv, cfg, pagine, n0):
    """Il carattere più grande con cui il testo sta esattamente nelle pagine date."""
    basso, alto = 0.6, 1.6
    for _ in range(30):
        k = (basso + alto) / 2
        if scorri(None, cfg["testo"], k, False, n0)[0] <= pagine:
            basso = k
        else:
            alto = k
    scorri(cv, cfg["testo"], basso, True, n0, cfg["titolo"])
    return basso


def testata(cv, scheda, k, disegna=True):
    """Nome, sottotitolo, filetto, presentazione. Restituisce la y sotto."""
    nome = c.stile("n", fontName="Cormorant-Forte", fontSize=28 * k, leading=32 * k)
    sotto = c.stile("st", fontName="Cormorant-Corsivo", fontSize=14 * k, leading=17 * k, textColor=c.GRIGIO)
    testo = c.stile("tx", fontSize=12.5 * k, leading=17 * k, alignment=TA_JUSTIFY)
    y = H - M
    f = c.scrivi if disegna else (lambda cv_, t, s, x, yy, l: yy - c.misura(t, s, l))
    y = f(cv, scheda["nome"], nome, M, y, UTILE)
    if c.sottotitolo(scheda):
        y = f(cv, c.sottotitolo(scheda), sotto, M, y - 1, UTILE)
    y -= 5 * mm * k
    if disegna:
        c.filetto(cv, M, y, 22 * mm, 1)
    y -= 7 * mm * k
    if scheda.get("presentazione", {}).get("it"):
        y = f(cv, scheda["presentazione"]["it"], testo, M, y, UTILE)
    return y - 8 * mm * k


def stili_scheda(k):
    return dict(
        titolo=c.stile("ti", fontName="Cormorant-Corsivo", fontSize=14 * k, leading=17 * k),
        dati=c.stile("da", fontSize=9 * k, leading=11.5 * k, textColor=c.GRIGIO),
        dida=c.stile("di", fontSize=10.5 * k, leading=14 * k, alignment=TA_JUSTIFY),
    )


def testo_scheda(cv, o, s, x, y, largo, k, disegna=True):
    """Titolo, dati, filetto, didascalia. Restituisce l'altezza usata."""
    y0 = y
    f = c.scrivi if disegna else (lambda cv_, t, st, xx, yy, l: yy - c.misura(t, st, l))
    y = f(cv, o["titolo"], s["titolo"], x, y, largo)
    if dati_opera(o):
        y = f(cv, dati_opera(o), s["dati"], x, y, largo)
    y -= 2.5 * mm * k
    if disegna:
        c.filetto(cv, x, y, 10 * mm, 0.7)
    y -= 3.5 * mm * k
    y = f(cv, o["didascalia"]["it"], s["dida"], x, y, largo)
    return y0 - y


def pagina_artista(cv, scheda, cartella):
    """Le miniature riempiono lo spazio che resta: sopra al testo con una o due
    righe di schede, accanto con tre o più."""
    lista = opere(scheda)
    file = [cartella / "foto" / Path(scheda["_cartella"]) / f"{c.nome_opera(o)}.jpg" for o in lista]
    n = len(lista)
    colonne = 1 if n == 1 else 2
    righe = [list(range(i, min(i + colonne, n))) for i in range(0, n, colonne)]
    accanto = len(righe) >= 3
    largo = UTILE if colonne == 1 else COLONNA
    passo = 7 * mm             # fra le righe
    stacco = 4 * mm            # fra foto e testo

    for k in [1 - 0.025 * i for i in range(17)]:
        s = stili_scheda(k)
        y = testata(cv, scheda, k, disegna=False)
        spazio = y - BASSO - passo * (len(righe) - 1)
        if accanto:
            alto_riga = spazio / len(righe)
            larga_foto = COLONNA * 0.5
            testo_largo = COLONNA - larga_foto - stacco
            if all(testo_scheda(cv, lista[i], s, 0, 0, testo_largo, k, False) <= alto_riga for r in righe for i in r):
                break
        else:
            testi = [max(testo_scheda(cv, lista[i], s, 0, 0, largo, k, False) for i in r) for r in righe]
            alto_foto = (spazio - sum(testi) - stacco * len(righe)) / len(righe)
            if alto_foto >= 35 * mm:
                break

    y = testata(cv, scheda, k)
    if accanto:
        for r in righe:
            for j, i in enumerate(r):
                x = M + j * (COLONNA + GIUNTO)
                w, _ = foto(cv, file[i], x, y, larga_foto, alto_riga, allinea="sinistra")
                testo_scheda(cv, lista[i], s, x + w + stacco, y, COLONNA - w - stacco, k)
            y -= alto_riga + passo
        return
    # Le foto sono larghe al massimo quanto la colonna: se avanza altezza, la
    # si distribuisce fra le righe invece di lasciarla in fondo
    alti = []
    for r, t in zip(righe, testi):
        alti.append(min(alto_foto, max(largo / 1 * proporzione(file[i]) for i in r)))
    if colonne == 1:
        alti = [min(alto_foto, 150 * mm)]
    avanzo = (y - BASSO) - sum(alti) - sum(testi) - stacco * len(righe) - passo * (len(righe) - 1)
    extra = max(0, avanzo) / (len(righe) + 1)
    y -= extra
    for r, t, af in zip(righe, testi, alti):
        for j, i in enumerate(r):
            x = M + j * (COLONNA + GIUNTO)
            iw = largo if colonne == 2 else UTILE
            # le foto di una riga poggiano sulla stessa linea
            hf = min(af, iw * proporzione(file[i]))
            foto(cv, file[i], x, y - (af - hf), iw, hf)
            testo_scheda(cv, lista[i], s, x, y - af - stacco, largo, k)
        y -= af + stacco + t + passo + extra


def pagina_collezioni(cv, schede):
    """Le collezioni private tutte in una pagina: il carattere cresce o cala
    finché il testo la riempie."""
    def componi(k, disegna):
        nome = c.stile("n", fontName="Cormorant-Forte", fontSize=20 * k, leading=24 * k)
        sotto = c.stile("st", fontName="Cormorant-Corsivo", fontSize=12 * k, leading=15 * k, textColor=c.GRIGIO)
        testo = c.stile("tx", fontSize=11.5 * k, leading=15.5 * k, alignment=TA_JUSTIFY)
        f = c.scrivi if disegna else (lambda cv_, t, st, x, yy, l: yy - c.misura(t, st, l))
        y = H - M
        if disegna:
            y = etichetta(cv, "Dalle collezioni private", y)
        else:
            y -= 9 * 1.6
        y -= 4 * mm
        for i, s in enumerate(schede):
            if i:
                y -= 7 * mm * k
            y = f(cv, s["nome"], nome, M, y, UTILE)
            y = f(cv, c.sottotitolo(s), sotto, M, y, UTILE)
            y -= 3 * mm * k
            if disegna:
                c.filetto(cv, M, y, 16 * mm, 0.8)
            y -= 4 * mm * k
            if s.get("presentazione", {}).get("it"):
                y = f(cv, s["presentazione"]["it"], testo, M, y, UTILE)
            for o in opere(s):
                y -= testo_scheda(cv, o, stili_scheda(k), M, y, UTILE, k, disegna)
        return y - BASSO

    basso, alto = 0.6, 1.6
    for _ in range(30):
        k = (basso + alto) / 2
        if componi(k, False) >= 0:
            basso = k
        else:
            alto = k
    carta(cv)
    componi(basso, True)


def pagina_galleria(cv, gal, cartella):
    carta(cv)
    y = etichetta(cv, "La galleria", H - M) - 3 * mm
    y = c.scrivi(cv, gal["titolo"], c.stile("t", fontName="Cormorant-Forte", fontSize=24, leading=28), M, y, UTILE)
    y = c.scrivi(cv, gal["sottotitolo"], c.stile("s", fontName="Cormorant-Corsivo", fontSize=13, leading=16,
                 textColor=c.GRIGIO), M, y - 1, UTILE)
    y -= 5 * mm
    c.filetto(cv, M, y, 22 * mm, 1)
    y -= 7 * mm
    testo = c.stile("tx", fontSize=11.5, leading=15.5, alignment=TA_JUSTIFY)
    for p in gal["testo"]:
        y = c.scrivi(cv, p, testo, M, y, UTILE) - 3 * mm
    y -= 2 * mm
    romani = ["I", "II", "III", "IV", "V", "VI"]
    colonna = (UTILE - GIUNTO) / 2
    tit = c.stile("pt", fontName="Cormorant-Corsivo", fontSize=13, leading=16)
    des = c.stile("pd", fontSize=10.5, leading=13.5, textColor=c.GRIGIO)
    for r in range(0, len(gal["pilastri"]), 2):
        fondo_riga = y
        for j, (titolo, descr) in enumerate(gal["pilastri"][r:r + 2]):
            x = M + j * (colonna + GIUNTO)
            yy = c.scrivi(cv, f'<font color="#C9A227">{romani[r + j]}</font>  {titolo}', tit, x, y, colonna)
            yy = c.scrivi(cv, descr, des, x, yy, colonna)
            fondo_riga = min(fondo_riga, yy)
        y = fondo_riga - 3 * mm
    y -= 3 * mm
    chiusura = c.stile("ch", fontName="Cormorant-Corsivo", fontSize=15, leading=19, alignment=TA_CENTER)
    alto_chiusura = c.misura(f"«{gal['chiusura']}»", chiusura, UTILE) + 8 * mm
    # Le foto della galleria allestita riempiono lo spazio fra testo e chiusura
    elenco = [cartella / "foto" / "galleria" / f for f in gal.get("foto", [])]
    elenco = [f for f in elenco if f.exists()]
    spazio = y - BASSO - alto_chiusura
    if elenco and spazio > 30 * mm:
        n = len(elenco)
        larga = (UTILE - 4 * mm * (n - 1)) / n
        for i, f in enumerate(elenco):
            _ritaglia(cv, f, M + i * (larga + 4 * mm), y - spazio, larga, spazio)
        y -= spazio + 6 * mm
    else:
        y = BASSO + alto_chiusura - 4 * mm
    c.scrivi(cv, f"«{gal['chiusura']}»", chiusura, M, y, UTILE)


def _ritaglia(cv, file, x, y, largo, alto):
    """Riempie il riquadro tagliando la foto al centro, come una finestra."""
    im = Image.open(file).convert("RGB")
    iw, ih = im.size
    r = alto / largo
    if ih / iw > r:
        nh = iw * r
        im = im.crop((0, (ih - nh) / 2, iw, (ih + nh) / 2))
    else:
        nw = ih / r
        im = im.crop(((iw - nw) / 2, 0, (iw + nw) / 2, ih))
    cv.drawImage(ImageReader(im), x, y, largo, alto)


def retro(cv, cfg, gal):
    cv.setFillColor(NERO)
    cv.rect(0, 0, W, H, stroke=0, fill=1)
    larga = 70 * mm
    c.logo(cv, (W - larga) / 2, H * 0.62, larga)
    y = H * 0.62 - larga * 616 / 888 - 10 * mm
    chiaro = c.CARTA
    centro = dict(alignment=TA_CENTER, textColor=chiaro)
    y = c.scrivi(cv, gal["titolo"], c.stile("r1", fontName="Cormorant-Forte", fontSize=17, leading=22, **centro),
                 M, y, UTILE) - 3 * mm
    for riga in gal["contatti"]:
        y = c.scrivi(cv, riga, c.stile("r2", fontSize=12, leading=17, **centro), M, y, UTILE)
    y -= 8 * mm
    c.filetto(cv, W / 2 - 12 * mm, y, 24 * mm, 0.8)
    y -= 8 * mm
    c.scrivi(cv, f"«{gal['chiusura']}»", c.stile("r3", fontName="Cormorant-Corsivo", fontSize=14, leading=18,
             alignment=TA_CENTER, textColor=c.ORO), M, y, UTILE)
    piede_retro = f"{cfg['titolo']}  ·  {cfg['sottotitolo']}"
    c.scrivi(cv, piede_retro, c.stile("r4", fontSize=9, leading=12, alignment=TA_CENTER,
             textColor=HexColor("#8A8378")), M, M + 6 * mm, UTILE)


# ----------------------------------------------------------------------------
# Il libro
# ----------------------------------------------------------------------------

def disegna_pagine(cv, cfg, schede, gal, cartella):
    """Disegna tutte le pagine; restituisce quante sono."""
    artisti = [s for s in schede if con_miniature(s) and not s["nome"].startswith("E.B.Art")]
    collezioni = [s for s in schede if not con_miniature(s)]
    eb = [s for s in schede if s["nome"].startswith("E.B.Art")]
    fisse = 2 + len(artisti) + (1 if collezioni else 0) + len(eb) + 2   # copertina, frontespizio, galleria, retro
    pagine_testo = 2
    while (fisse + pagine_testo) % 4:
        pagine_testo += 1

    n = 1
    copertina(cv, cfg, cartella)
    cv.showPage()
    n += 1
    frontespizio(cv, cfg, schede)
    piede(cv, n)
    cv.showPage()
    n += 1
    testo_mostra(cv, cfg, pagine_testo, n)
    cv.showPage()
    n += pagine_testo
    for s in artisti:
        carta(cv)
        pagina_artista(cv, s, cartella)
        piede(cv, n)
        cv.showPage()
        n += 1
    if collezioni:
        pagina_collezioni(cv, collezioni)
        piede(cv, n)
        cv.showPage()
        n += 1
    for s in eb:
        carta(cv)
        pagina_artista(cv, s, cartella)
        piede(cv, n)
        cv.showPage()
        n += 1
    pagina_galleria(cv, gal, cartella)
    piede(cv, n)
    cv.showPage()
    n += 1
    retro(cv, cfg, gal)
    cv.showPage()
    return n


def imponi(sorgente: Path, uscita: Path, pagine: int) -> None:
    """Fogli A3 orizzontali, due pagine per facciata, nell'ordine della piegatura:
    con 16 pagine il primo foglio porta 16|1 davanti e 2|15 dietro, e così via."""
    import pypdfium2 as pdfium
    import pypdfium2.raw as pdfium_c
    doc = pdfium.PdfDocument(str(sorgente))
    nuovo = pdfium.PdfDocument.new()
    for f in range(pagine // 4):
        for sinistra, destra in ((pagine - 2 * f, 1 + 2 * f), (2 + 2 * f, pagine - 1 - 2 * f)):
            foglio = nuovo.new_page(2 * W, H)
            for lato, numero in ((0, sinistra), (1, destra)):
                forma = doc.page_as_xobject(numero - 1, nuovo)
                oggetto = forma.as_pageobject()
                oggetto.transform(pdfium.PdfMatrix().translate(lato * W, 0))
                foglio.insert_obj(oggetto)
            foglio.gen_content()
    nuovo.save(str(uscita))


def main() -> None:
    mostra = sys.argv[1] if len(sys.argv) > 1 else "i-luoghi-dell-anima"
    cfg = json.loads((MOSTRE / f"{mostra}.json").read_text(encoding="utf-8"))
    gal = json.loads(GALLERIA.read_text(encoding="utf-8"))
    schede = []
    for nome in cfg["ordine"]:
        s = json.loads((c.ARTISTI / nome / "scheda.json").read_text(encoding="utf-8"))
        s["_cartella"] = nome
        schede.append(s)
    cartella = MOSTRE / "catalogo"
    file = cartella / f"{mostra}-libro.pdf"
    cv = Canvas(str(file), pagesize=(W, H))
    cv.setTitle(f"{cfg['titolo']} — catalogo")
    cv.setAuthor("BE Art Gallery & Creative Lab")
    pagine = disegna_pagine(cv, cfg, schede, gal, cartella)
    cv.save()
    a3 = cartella / f"{mostra}-libro-A3.pdf"
    imponi(file, a3, pagine)
    print(f"\n{cfg['titolo']}: {pagine} pagine")
    for f in (file, a3):
        print(f"   {f.relative_to(c.RADICE)}")
    print()


if __name__ == "__main__":
    main()
