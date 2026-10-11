#!/usr/bin/env python3
"""
Il catalogo di una mostra in formato libro A5: pagine in multipli di 4,
nessuna pagina con spazi vuoti, una miniatura per ogni opera degli artisti.

Legge testi-critici/mostre/<mostra>.json, le schede degli artisti e il testo
della galleria (testi-critici/galleria.json). Le foto restano in locale, in
testi-critici/mostre/catalogo/foto/:

    copertina.jpg                     la locandina
    <artista>/<opera>.jpg             già ritagliate sul quadro
    galleria/<foto>.jpg               l'allestimento, elencate in
                                      "foto_allestimento" nella scheda della mostra

Produce in testi-critici/mostre/catalogo/:

- <mostra>-libro-A5.pdf        pagine A5 in ordine: per la tipografia
- <mostra>-libro-stampa-A4.pdf due pagine per foglio A4 orizzontale, già
                               nell'ordine di piegatura: si stampa fronte-retro
                               girando sul lato corto, si piega a metà, si pinza

Come si riempiono le pagine:
- il testo della mostra e le collezioni private scorrono su un numero intero
  di pagine, con il carattere che si adatta finché le riempie;
- gli artisti (schede con "vive_e_lavora", o E.B.Art) hanno una pagina con
  presentazione e due opere, poi una pagina ogni quattro opere: le miniature
  si allargano fino a occupare lo spazio che resta;
- le foto dell'allestimento, a pagina piena, chiudono il libro e portano il
  numero di pagine al multiplo di 4.

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
W, H = 148 * mm, 210 * mm          # A5
M = 13 * mm                        # margine
ALTO = H - M
BASSO = M + 7 * mm                 # sopra il piede
UTILE = W - 2 * M
GIUNTO = 6 * mm
COLONNA = (UTILE - GIUNTO) / 2
NERO = HexColor("#141312")
PRIMA, POI = 2, 4                  # opere sulla pagina dell'artista, e sulle seguenti


def dati_opera(o: dict) -> str:
    return "  ·  ".join(str(o[k]) for k in ("anno", "tecnica", "misure", "provenienza") if o.get(k))


def opere(scheda: dict) -> list[dict]:
    return [o for o in scheda.get("opere", []) if o.get("didascalia", {}).get("it")]


def e_eb(scheda: dict) -> bool:
    return scheda["nome"].startswith("E.B.Art")


def con_miniature(scheda: dict) -> bool:
    return bool(scheda.get("vive_e_lavora")) or e_eb(scheda)


def pagine_artista(scheda: dict) -> list[list[dict]]:
    lista = opere(scheda)
    gruppi = [lista[:PRIMA]]
    for i in range(PRIMA, len(lista), POI):
        gruppi.append(lista[i:i + POI])
    return gruppi


# ----------------------------------------------------------------------------
# Elementi comuni
# ----------------------------------------------------------------------------

def carta(cv):
    c.fondo(cv, (W, H))


def piede(cv, n):
    """Il numero sul lato esterno: a destra le dispari, a sinistra le pari."""
    c.filetto(cv, M, M + 3 * mm, UTILE, 0.4)
    cv.setFont("Cormorant", 6.5)
    cv.setFillColor(c.GRIGIO)
    testo = "BE Art Gallery & Creative Lab  ·  beartgallery.eu"
    y = M - 1 * mm
    if n % 2:
        cv.drawString(M, y, testo)
        cv.drawRightString(W - M, y, str(n))
    else:
        cv.drawString(M, y, str(n))
        cv.drawRightString(W - M, y, testo)


def etichetta(cv, testo, y, x=M, colore=c.ORO, corpo=7.5):
    """Una riga in maiuscolo spaziato, come «ARTISTI IN MOSTRA» sulla locandina."""
    cv.setFont("Cormorant-Forte", corpo)
    cv.setFillColor(colore)
    t = cv.beginText(x, y - corpo)
    t.setCharSpace(corpo * 0.25)
    t.textOut(testo.upper())
    t.setCharSpace(0)          # la spaziatura resta sull'oggetto testo, non sul resto della pagina
    cv.drawText(t)
    return y - corpo * 1.6


def proporzione(file: Path) -> float:
    """Altezza su larghezza; 3/4 se la foto manca."""
    if not file.exists():
        return 0.75
    iw, ih = Image.open(file).size
    return ih / iw


def foto(cv, file: Path, x, y_alto, largo, alto):
    """Una foto centrata dentro un riquadro, senza deformarla. Se manca, un
    riquadro sottile ne tiene il posto."""
    if not file.exists():
        print(f"   ⚠ manca la foto {file.relative_to(c.RADICE)}")
        cv.setStrokeColor(c.GRIGIO)
        cv.setLineWidth(0.3)
        cv.rect(x, y_alto - alto, largo, alto)
        return
    iw, ih = Image.open(file).size
    s = min(largo / iw, alto / ih)
    w, h = iw * s, ih * s
    cv.drawImage(ImageReader(str(file)), x + (largo - w) / 2, y_alto - h, w, h)


def jpeg(im, lato):
    """Un'immagine già ritagliata, ricompressa in JPEG: passata così com'è,
    finirebbe nel PDF senza compressione e il file peserebbe dieci volte tanto."""
    import io
    im = im.copy()
    im.thumbnail((lato, lato))
    dati = io.BytesIO()
    im.save(dati, "JPEG", quality=85)
    dati.seek(0)
    return ImageReader(dati)


def ritaglia(cv, file, x, y, largo, alto):
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
    cv.drawImage(jpeg(im, 1800), x, y, largo, alto)


# ----------------------------------------------------------------------------
# Testo che scorre: la mostra, le collezioni, la galleria
# ----------------------------------------------------------------------------
# Un blocco è una tupla:
#   ("etichetta", testo)               maiuscolo spaziato oro
#   ("titolo", testo, stile)           resta attaccato a ciò che segue
#   ("par", testo, stile)              si spezza fra le pagine
#   ("filetto", lunghezza, spessore)
#   ("spazio", altezza)

def scorri(cv, blocchi, disegna, n0=0):
    """Posa i blocchi pagina dopo pagina. Restituisce (pagine, spazio rimasto)."""
    pagina, y = 1, ALTO

    def nuova():
        nonlocal pagina, y
        if disegna:
            piede(cv, n0 + pagina - 1)
            cv.showPage()
            carta(cv)
        pagina += 1
        y = ALTO

    if disegna:
        carta(cv)
    for i, b in enumerate(blocchi):
        tipo = b[0]
        if tipo == "spazio":
            if y < ALTO:
                y -= b[1]
        elif tipo == "filetto":
            if disegna:
                c.filetto(cv, M, y, b[1], b[2])
            y -= b[2]
        elif tipo == "etichetta":
            if y - 30 < BASSO:
                nuova()
            y = etichetta(cv, b[1], y) if disegna else y - 7.5 * 1.6
        elif tipo == "titolo":
            alto = c.misura(b[1], b[2], UTILE)
            # Un titolo non resta mai solo in fondo alla pagina: con sé porta
            # i titoli che lo seguono e almeno tre righe di testo
            seguito = 0
            righe = 0
            for x in blocchi[i + 1:]:
                if x[0] == "titolo":
                    seguito += c.misura(x[1], x[2], UTILE)
                elif x[0] == "par":
                    righe = 3 * x[2].leading
                    break
            if y - alto - seguito - righe - 6 * mm < BASSO:
                nuova()
            if disegna:
                c.scrivi(cv, b[1], b[2], M, y, UTILE)
            y -= alto
        elif tipo == "par":
            par = Paragraph(b[1].replace("'", "’"), b[2])
            while True:
                _, alto = par.wrap(UTILE, 10_000)
                if y - alto >= BASSO:
                    if disegna:
                        par.drawOn(cv, M, y - alto)
                    y -= alto
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


def adatta(componi, pagine, minimo=0.5, massimo=1.6):
    """Il fattore di scala più grande con cui i blocchi stanno in `pagine`."""
    basso, alto = minimo, massimo
    for _ in range(28):
        k = (basso + alto) / 2
        if scorri(None, componi(k), False)[0] <= pagine:
            basso = k
        else:
            alto = k
    return basso


def pagine_servono(componi, k):
    """Quante pagine servono con il carattere a scala k."""
    return scorri(None, componi(k), False)[0]


def blocchi_mostra(cfg):
    def componi(k):
        corpo = c.stile("p", fontSize=10 * k, leading=14 * k, alignment=TA_JUSTIFY)
        tit = c.stile("h", fontName="Cormorant-Corsivo", fontSize=13 * k, leading=16 * k)
        b = [("etichetta", cfg["titolo"]), ("spazio", 3 * mm)]
        for voce in cfg["testo"]:
            if isinstance(voce, dict):
                b += [("spazio", 4 * mm * k), ("titolo", voce["titolo"], tit), ("spazio", 1.5 * mm * k)]
            else:
                b += [("par", voce, corpo), ("spazio", 3 * mm * k)]
        return b
    return componi


def blocchi_collezioni(schede):
    def componi(k):
        nome = c.stile("n", fontName="Cormorant-Forte", fontSize=16 * k, leading=19 * k)
        sotto = c.stile("st", fontName="Cormorant-Corsivo", fontSize=10 * k, leading=13 * k, textColor=c.GRIGIO)
        testo = c.stile("tx", fontSize=9.5 * k, leading=13 * k, alignment=TA_JUSTIFY)
        s = stili_scheda(k)
        b = [("etichetta", "Dalle collezioni private"), ("spazio", 3 * mm)]
        for i, sc in enumerate(schede):
            if i:
                b.append(("spazio", 6 * mm * k))
            b += [("titolo", sc["nome"], nome), ("titolo", c.sottotitolo(sc), sotto), ("spazio", 2.5 * mm * k),
                  ("filetto", 14 * mm, 0.8), ("spazio", 3 * mm * k)]
            if sc.get("presentazione", {}).get("it"):
                b.append(("par", sc["presentazione"]["it"], testo))
            for o in opere(sc):
                b.append(("titolo", o["titolo"], s["titolo"]))
                if dati_opera(o):
                    b.append(("titolo", dati_opera(o), s["dati"]))
                b += [("spazio", 2 * mm * k), ("par", o["didascalia"]["it"], s["dida"])]
        return b
    return componi


def blocchi_galleria(gal):
    def componi(k):
        testo = c.stile("tx", fontSize=9.5 * k, leading=13.2 * k, alignment=TA_JUSTIFY)
        b = [("etichetta", "La galleria"), ("spazio", 2 * mm),
             ("titolo", gal["titolo"], c.stile("t", fontName="Cormorant-Forte", fontSize=18 * k, leading=21 * k)),
             ("titolo", gal["sottotitolo"], c.stile("s", fontName="Cormorant-Corsivo", fontSize=10.5 * k,
                                                     leading=13 * k, textColor=c.GRIGIO)),
             ("spazio", 3 * mm * k), ("filetto", 18 * mm, 1), ("spazio", 4 * mm * k)]
        for p in gal["testo"]:
            b += [("par", p, testo), ("spazio", 2.5 * mm * k)]
        tit = c.stile("pt", fontName="Cormorant-Corsivo", fontSize=11 * k, leading=13.5 * k)
        des = c.stile("pd", fontSize=8.8 * k, leading=11.5 * k, textColor=c.GRIGIO)
        romani = ["I", "II", "III", "IV", "V", "VI"]
        b.append(("spazio", 1.5 * mm * k))
        for n, (t, d) in enumerate(gal["pilastri"]):
            b += [("titolo", f'<font color="#C9A227">{romani[n]}</font>  {t}', tit), ("par", d, des),
                  ("spazio", 2 * mm * k)]
        b += [("spazio", 3 * mm * k), ("par", f"«{gal['chiusura']}»",
              c.stile("ch", fontName="Cormorant-Corsivo", fontSize=12.5 * k, leading=16 * k, alignment=TA_CENTER))]
        return b
    return componi


# ----------------------------------------------------------------------------
# Le pagine
# ----------------------------------------------------------------------------

def copertina(cv, cfg, cartella):
    """La locandina a tutta pagina; sotto, il nero della sua fascia."""
    file = cartella / "foto" / "copertina.jpg"
    if not file.exists():
        carta(cv)
        c.scrivi(cv, cfg["titolo"], c.stile("t", fontName="Cormorant-Forte", fontSize=32, leading=36),
                 M, H / 2, UTILE)
        print("   ⚠ manca la copertina: foto/copertina.jpg")
        return
    im = Image.open(file).convert("RGB")
    iw, ih = im.size
    fondo = im.resize((1, 1), box=(0, ih - 5, iw, ih)).getpixel((0, 0))
    cv.setFillColorRGB(*(v / 255 for v in fondo))
    cv.rect(0, 0, W, H, stroke=0, fill=1)
    h = W * ih / iw
    if h > H:
        w = H * iw / ih
        cv.drawImage(jpeg(im, 2000), (W - w) / 2, 0, w, H)
    else:
        cv.drawImage(jpeg(im, 2000), 0, H - h, W, h)


def frontespizio(cv, cfg, schede):
    carta(cv)
    c.logo(cv, M, ALTO, 26 * mm)
    y = ALTO - 36 * mm
    y = c.scrivi(cv, cfg["titolo"], c.stile("t", fontName="Cormorant-Forte", fontSize=30, leading=33), M, y, UTILE)
    y = c.scrivi(cv, cfg["sottotitolo"], c.stile("s", fontName="Cormorant-Corsivo", fontSize=13, leading=17,
                 textColor=c.GRIGIO), M, y - 3, UTILE)
    y = c.scrivi(cv, cfg["luogo"], c.stile("l", fontSize=9.5, leading=12, textColor=c.GRIGIO), M, y - 1, UTILE)
    y -= 7 * mm
    c.filetto(cv, M, y, 18 * mm, 1)
    y -= 9 * mm
    y = etichetta(cv, "Artisti in mostra", y, corpo=8.5)
    nome = c.stile("n", fontSize=14, leading=19)
    for s in schede:
        if con_miniature(s) and not e_eb(s):
            y = c.scrivi(cv, s["nome"], nome, M, y, UTILE)
    if any(e_eb(s) for s in schede):
        y = c.scrivi(cv, "E.B.Art", nome, M, y, UTILE)
    if cfg.get("collezioni"):
        y -= 5 * mm
        c.filetto(cv, M, y, 18 * mm, 0.6)
        y -= 4 * mm
        c.scrivi(cv, cfg["collezioni"], c.stile("c", fontName="Cormorant-Corsivo", fontSize=12.5, leading=16,
                 textColor=c.ORO), M, y, UTILE)
    if cfg.get("orari"):
        c.scrivi(cv, cfg["orari"], c.stile("o", fontSize=9, leading=12, textColor=c.GRIGIO), M, BASSO + 12, UTILE)


def stili_scheda(k):
    return dict(
        titolo=c.stile("ti", fontName="Cormorant-Corsivo", fontSize=11.5 * k, leading=14 * k),
        dati=c.stile("da", fontSize=7.5 * k, leading=9.5 * k, textColor=c.GRIGIO),
        dida=c.stile("di", fontSize=8.8 * k, leading=11.6 * k, alignment=TA_JUSTIFY),
    )


def testo_scheda(cv, o, s, x, y, largo, k, disegna=True):
    """Titolo, dati, filetto, didascalia. Restituisce l'altezza usata."""
    y0 = y
    f = c.scrivi if disegna else (lambda cv_, t, st, xx, yy, l: yy - c.misura(t, st, l))
    y = f(cv, o["titolo"], s["titolo"], x, y, largo)
    if dati_opera(o):
        y = f(cv, dati_opera(o), s["dati"], x, y, largo)
    y -= 2 * mm * k
    if disegna:
        c.filetto(cv, x, y, 8 * mm, 0.6)
    y -= 3 * mm * k
    y = f(cv, o["didascalia"]["it"], s["dida"], x, y, largo)
    return y0 - y


def testata(cv, scheda, k, disegna=True):
    """Nome, sottotitolo, filetto, presentazione. Restituisce la y sotto."""
    nome = c.stile("n", fontName="Cormorant-Forte", fontSize=21 * k, leading=24 * k)
    sotto = c.stile("st", fontName="Cormorant-Corsivo", fontSize=11 * k, leading=13.5 * k, textColor=c.GRIGIO)
    testo = c.stile("tx", fontSize=10 * k, leading=13.6 * k, alignment=TA_JUSTIFY)
    f = c.scrivi if disegna else (lambda cv_, t, s, x, yy, l: yy - c.misura(t, s, l))
    y = f(cv, scheda["nome"], nome, M, ALTO, UTILE)
    if c.sottotitolo(scheda):
        y = f(cv, c.sottotitolo(scheda), sotto, M, y - 1, UTILE)
    y -= 4 * mm * k
    if disegna:
        c.filetto(cv, M, y, 18 * mm, 1)
    y -= 6 * mm * k
    if scheda.get("presentazione", {}).get("it"):
        y = f(cv, scheda["presentazione"]["it"], testo, M, y, UTILE)
    return y - 6 * mm * k


def testata_seguito(cv, scheda, disegna=True):
    """Sulle pagine che continuano un artista: il nome, piccolo, e il filetto."""
    st = c.stile("ns", fontName="Cormorant-Corsivo", fontSize=11, leading=13.5, textColor=c.GRIGIO)
    y = c.scrivi(cv, scheda["nome"], st, M, ALTO, UTILE) if disegna else ALTO - c.misura(scheda["nome"], st, UTILE)
    y -= 2.5 * mm
    if disegna:
        c.filetto(cv, M, y, 18 * mm, 0.6)
    return y - 6 * mm


def pagina_opere(cv, scheda, lista, cartella, prima):
    """Le schede in righe da due, ciascuna con la sua miniatura sopra. Le
    miniature crescono finché la pagina è piena; il carattere cala solo se
    altrimenti resterebbero troppo piccole."""
    file = [cartella / "foto" / scheda["_cartella"] / f"{c.nome_opera(o)}.jpg" for o in lista]
    colonne = 1 if len(lista) == 1 else 2
    largo = UTILE if colonne == 1 else COLONNA
    righe = [list(range(i, min(i + colonne, len(lista)))) for i in range(0, len(lista), colonne)]
    passo, stacco = 6 * mm, 3 * mm

    for k in [1 - 0.025 * i for i in range(15)]:
        s = stili_scheda(k)
        y = testata(cv, scheda, k, False) if prima else testata_seguito(cv, scheda, False)
        testi = [max(testo_scheda(cv, lista[i], s, 0, 0, largo, k, False) for i in r) for r in righe]
        spazio = y - BASSO - sum(testi) - (stacco + passo) * len(righe) + passo
        if spazio / len(righe) >= 34 * mm:
            break

    y = testata(cv, scheda, k) if prima else testata_seguito(cv, scheda)
    # Ogni riga riceve altezza in proporzione alle sue foto; quello che le foto,
    # già larghe quanto la colonna, non possono usare va fra le righe
    voluti = [max(largo * proporzione(file[i]) for i in r) for r in righe]
    scala = min(1, spazio / sum(voluti))
    alti = [v * scala for v in voluti]
    avanzo = max(0, spazio - sum(alti))
    extra = avanzo / (len(righe) + 1)
    y -= extra
    for r, t, af in zip(righe, testi, alti):
        for j, i in enumerate(r):
            x = M + j * (COLONNA + GIUNTO)
            hf = min(af, largo * proporzione(file[i]))
            foto(cv, file[i], x, y - (af - hf), largo, hf)       # le foto di una riga poggiano sulla stessa linea
            testo_scheda(cv, lista[i], s, x, y - af - stacco, largo, k)
        y -= af + stacco + t + passo + extra


def pagina_foto(cv, file, didascalia):
    """Una foto dell'allestimento a pagina piena, entro i margini."""
    carta(cv)
    st = c.stile("fd", fontName="Cormorant-Corsivo", fontSize=8.5, leading=11, textColor=c.GRIGIO)
    alto_dida = c.misura(didascalia, st, UTILE) + 3 * mm
    ritaglia(cv, file, M, BASSO + alto_dida, UTILE, ALTO - BASSO - alto_dida)
    c.scrivi(cv, didascalia, st, M, BASSO + alto_dida - 2 * mm, UTILE)


def retro(cv, cfg, gal):
    cv.setFillColor(NERO)
    cv.rect(0, 0, W, H, stroke=0, fill=1)
    larga = 52 * mm
    top = H * 0.64
    c.logo(cv, (W - larga) / 2, top, larga)
    y = top - larga * 616 / 888 - 8 * mm
    centro = dict(alignment=TA_CENTER, textColor=c.CARTA)
    y = c.scrivi(cv, gal["titolo"], c.stile("r1", fontName="Cormorant-Forte", fontSize=13, leading=17, **centro),
                 M, y, UTILE) - 2 * mm
    for riga in gal["contatti"]:
        y = c.scrivi(cv, riga, c.stile("r2", fontSize=9.5, leading=13.5, **centro), M, y, UTILE)
    y -= 6 * mm
    c.filetto(cv, W / 2 - 9 * mm, y, 18 * mm, 0.8)
    y -= 6 * mm
    c.scrivi(cv, f"«{gal['chiusura']}»", c.stile("r3", fontName="Cormorant-Corsivo", fontSize=11, leading=14,
             alignment=TA_CENTER, textColor=c.ORO), M, y, UTILE)
    c.scrivi(cv, f"{cfg['titolo']}  ·  {cfg['sottotitolo']}", c.stile("r4", fontSize=7.5, leading=10,
             alignment=TA_CENTER, textColor=HexColor("#8A8378")), M, M + 5 * mm, UTILE)


# ----------------------------------------------------------------------------
# Il libro
# ----------------------------------------------------------------------------

def libro(cv, cfg, schede, gal, cartella):
    """Conta le pagine, sceglie quante darne al testo e alle foto perché il
    totale sia un multiplo di 4, poi disegna. Restituisce il numero di pagine."""
    artisti = [s for s in schede if con_miniature(s) and not e_eb(s)]
    collezioni = [s for s in schede if not con_miniature(s)]
    eb = [s for s in schede if e_eb(s)]
    mostra = blocchi_mostra(cfg)
    raccolte = blocchi_collezioni(collezioni)
    galleria = blocchi_galleria(gal)
    p_testo = pagine_servono(mostra, 1.0)
    p_coll = pagine_servono(raccolte, 0.95) if collezioni else 0
    p_artisti = sum(len(pagine_artista(s)) for s in artisti + eb)
    fisse = 1 + 1 + p_testo + p_artisti + p_coll + 1 + 1        # copertina, frontespizio, galleria, retro
    foto_all = [cartella / "foto" / "galleria" / f for f in cfg.get("foto_allestimento", [])]
    foto_all = [f for f in foto_all if f.exists()]
    p_foto = (-fisse) % 4
    if p_foto == 0 and len(foto_all) >= 4:
        p_foto = 4
    if p_foto > len(foto_all):
        # Meno foto che pagine da riempire: il testo della mostra prende le pagine in più
        p_testo += p_foto - len(foto_all)
        p_foto = len(foto_all)

    n = 1
    copertina(cv, cfg, cartella)
    cv.showPage()
    n += 1
    frontespizio(cv, cfg, schede)
    piede(cv, n)
    cv.showPage()
    n += 1
    n += scorri(cv, mostra(adatta(mostra, p_testo)), True, n)[0]
    cv.showPage()
    for s in artisti:
        for i, gruppo in enumerate(pagine_artista(s)):
            carta(cv)
            pagina_opere(cv, s, gruppo, cartella, prima=(i == 0))
            piede(cv, n)
            cv.showPage()
            n += 1
    if collezioni:
        n += scorri(cv, raccolte(adatta(raccolte, p_coll)), True, n)[0]
        cv.showPage()
    for s in eb:
        for i, gruppo in enumerate(pagine_artista(s)):
            carta(cv)
            pagina_opere(cv, s, gruppo, cartella, prima=(i == 0))
            piede(cv, n)
            cv.showPage()
            n += 1
    n += scorri(cv, galleria(adatta(galleria, 1)), True, n)[0]
    cv.showPage()
    for f in foto_all[:p_foto]:
        pagina_foto(cv, f, f"{cfg['titolo']} — l'allestimento in via San Pietro")
        piede(cv, n)
        cv.showPage()
        n += 1
    retro(cv, cfg, gal)
    cv.showPage()
    if n % 4:
        print(f"   ⚠ {n} pagine: non è un multiplo di 4")
    return n


def imponi(sorgente: Path, uscita: Path, pagine: int) -> None:
    """Fogli A4 orizzontali, due pagine A5 per facciata, nell'ordine della
    piegatura: con 20 pagine il primo foglio porta 20|1 davanti e 2|19 dietro."""
    import pypdfium2 as pdfium
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
    file = cartella / f"{mostra}-libro-A5.pdf"
    cv = Canvas(str(file), pagesize=(W, H))
    cv.setTitle(f"{cfg['titolo']} — catalogo")
    cv.setAuthor("BE Art Gallery & Creative Lab")
    pagine = libro(cv, cfg, schede, gal, cartella)
    cv.save()
    stampa = cartella / f"{mostra}-libro-stampa-A4.pdf"
    imponi(file, stampa, pagine)
    print(f"\n{cfg['titolo']}: {pagine} pagine A5, {pagine // 4} fogli A4 fronte-retro")
    for f in (file, stampa):
        print(f"   {f.relative_to(c.RADICE)}")
    print()


if __name__ == "__main__":
    main()
