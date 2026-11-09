#!/usr/bin/env python3
"""
Impagina portfolio e brochure dei Servizi per l'Arte.

Legge servizi-per-l-arte/progetti/<progetto>/impaginazione.json e produce,
nella cartella materiali/ del progetto (che non va su GitHub):

- portfolio.pdf   A4 verticale, una pagina dopo l'altra
- brochure.pdf    pieghevole a tre ante su A4 orizzontale: esterno e interno

Le foto si cercano in materiali/foto/, con la stessa struttura della cartella
del Drive: il JSON dice, per ogni codice d'opera, il percorso del file
(es. "104": "SERPENTINO/WhatsApp Image ... 12.08.00 4.jpeg"). Quando arrivano
le foto definitive basta sostituire i file, o aggiornare i percorsi, e rilanciare.
Una foto che manca lascia un riquadro vuoto col suo codice: la pagina si vede lo stesso.

    py strumenti\\servizi.py sauro-calamai
    py strumenti\\servizi.py sauro-calamai brochure      solo la brochure

Nei testi del JSON: <i>corsivo</i>; [fra quadre] diventa grigio, per i dati
ancora da completare.
"""

import io
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

sys.path.insert(0, str(Path(__file__).resolve().parent))
import critica as c  # noqa: E402  — carattere, colori e funzioni comuni

PROGETTI = c.RADICE / "servizi-per-l-arte" / "progetti"
LOGO_CHIARO = c.CARTELLA / "marchio" / "logo.png"   # chiaro su trasparente: vuole un fondo scuro

A4 = (210 * mm, 297 * mm)
A4_ORIZZONTALE = (297 * mm, 210 * mm)
SCURO = c.INCHIOSTRO
ROMANI = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI"}


# ----------------------------------------------------------------------------
# Testo
# ----------------------------------------------------------------------------

def markup(testo: str) -> str:
    testo = testo.replace("'", "’").replace("\n", "<br/>")
    return re.sub(r"\[([^\]]+)\]", r'<font color="#9A9288">[\1]</font>', testo)


def st(k, **o):
    """Uno stile alla scala k: 1 per l'A4, meno per le ante della brochure."""
    corpo = o.pop("corpo", 11.5) * k
    base = dict(fontName="Cormorant", fontSize=corpo, leading=corpo * 1.38,
                textColor=c.INCHIOSTRO, alignment=TA_LEFT)
    base.update(o)
    from reportlab.lib.styles import ParagraphStyle
    return ParagraphStyle("s", **base)


def par(cv, testo, stile, x, y, largo, disegna=True):
    p = Paragraph(markup(testo), stile)
    _, h = p.wrap(largo, 10_000)
    if disegna:
        p.drawOn(cv, x, y - h)
    return y - h


def etichetta(cv, testo, x, y, k, colore=c.ORO, centro=None, disegna=True):
    corpo = 8 * k
    if disegna:
        cv.setFont("Cormorant-Forte", corpo)
        cv.setFillColor(colore)
        spazio = corpo * 0.25
        t = testo.upper()
        if centro is not None:
            larghezza = cv.stringWidth(t, "Cormorant-Forte", corpo) + spazio * (len(t) - 1)
            x = centro - larghezza / 2
        o = cv.beginText(x, y - corpo)
        o.setCharSpace(spazio)
        o.textOut(t)
        o.setCharSpace(0)
        cv.drawText(o)
    return y - corpo * 2


# ----------------------------------------------------------------------------
# Foto
# ----------------------------------------------------------------------------

class Foto:
    def __init__(self, cartella: Path, mappa: dict):
        self.cartella, self.mappa, self.cache = cartella, mappa, {}
        self.mancanti = set()

    def file(self, codice):
        rel = self.mappa.get(codice)
        return self.cartella / rel if rel else None

    def immagine(self, codice):
        if codice not in self.cache:
            f = self.file(codice)
            if not f or not f.exists():
                self.mancanti.add(codice)
                self.cache[codice] = None
            else:
                self.cache[codice] = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        return self.cache[codice]

    def proporzione(self, codice):
        im = self.immagine(codice)
        return im.height / im.width if im else 0.75

    def posa(self, cv, codice, x, y, largo, alto, taglia=False, lato=1800, in_alto=False):
        """Dentro il riquadro con il bordo basso in y. Senza taglio la foto
        si centra intera; con il taglio riempie il riquadro come una finestra."""
        im = self.immagine(codice)
        if im is None:
            cv.setStrokeColor(c.GRIGIO)
            cv.setLineWidth(0.4)
            cv.rect(x, y, largo, alto)
            cv.setFont("Cormorant", 10)
            cv.setFillColor(c.GRIGIO)
            cv.drawCentredString(x + largo / 2, y + alto / 2, f"manca la foto {codice}")
            return x, y, largo, alto
        iw, ih = im.size
        if taglia:
            r = alto / largo
            if ih / iw > r:
                nh = iw * r
                im = im.crop((0, (ih - nh) / 2, iw, (ih + nh) / 2))
            else:
                nw = ih / r
                im = im.crop(((iw - nw) / 2, 0, (iw + nw) / 2, ih))
            w, h, px, py = largo, alto, x, y
        else:
            s = min(largo / iw, alto / ih)
            w, h = iw * s, ih * s
            px, py = x + (largo - w) / 2, (y + alto - h) if in_alto else y + (alto - h) / 2
        im = im.copy()
        im.thumbnail((lato, lato))
        dati = io.BytesIO()
        im.save(dati, "JPEG", quality=85)
        dati.seek(0)
        cv.drawImage(ImageReader(dati), px, py, w, h)
        return px, py, w, h


def didascalia(cv, righe, x, y, largo, k, disegna=True, chiaro=False):
    """La prima riga in corsivo, le altre piccole e grigie."""
    for i, r in enumerate(righe):
        s = (st(k, corpo=10.5, fontName="Cormorant-Corsivo", alignment=TA_CENTER,
                textColor=c.CARTA if chiaro else c.INCHIOSTRO) if i == 0
             else st(k, corpo=8.5, textColor=HexColor("#D9D3C7") if chiaro else c.GRIGIO, alignment=TA_CENTER))
        y = par(cv, r, s, x, y, largo, disegna)
    return y


def gruppo(cv, F, opere, x, y_basso, largo, alto, k, in_alto=False, chiaro=False):
    """Da una a quattro foto nel riquadro, ognuna con la sua didascalia. Con
    in_alto le foto stanno subito sotto il testo, invece che centrate nel vuoto."""
    n = len(opere)
    if not n:
        return
    gap = 6 * mm * k
    alto_dida = max(didascalia(cv, o.get("dida", []), 0, 0, largo, k, False) * -1 for o in opere) + 3 * k
    verticali = all(F.proporzione(o["foto"]) > 1.05 for o in opere)
    alta = alto > largo * 1.25
    if n == 1:
        celle = [(x, y_basso, largo, alto)]
    elif n == 2 and verticali and not alta:
        w = (largo - gap) / 2
        celle = [(x, y_basso, w, alto), (x + w + gap, y_basso, w, alto)]
    elif n == 2:
        h = (alto - gap) / 2
        celle = [(x, y_basso + h + gap, largo, h), (x, y_basso, largo, h)]
    elif n == 3 and alto > largo * 2:
        h = (alto - 2 * gap) / 3
        celle = [(x, y_basso + (2 - i) * (h + gap), largo, h) for i in range(3)]
    elif n == 3:
        h = (alto - gap) / 2
        w = (largo - gap) / 2
        celle = [(x, y_basso + h + gap, largo, h), (x, y_basso, w, h), (x + w + gap, y_basso, w, h)]
    else:
        h = (alto - gap) / 2
        w = (largo - gap) / 2
        celle = [(x + (i % 2) * (w + gap), y_basso + (1 - i // 2) * (h + gap), w, h) for i in range(4)]
    for o, (cx, cy, cw, ch) in zip(opere, celle):
        hd = alto_dida if o.get("dida") else 0
        _, py, _, ph = F.posa(cv, o["foto"], cx, cy + hd, cw, ch - hd, in_alto=in_alto)
        if o.get("dida"):
            didascalia(cv, o["dida"], cx, py - 2 * k, cw, k, chiaro=chiaro)


# ----------------------------------------------------------------------------
# Fondo a gradiente con venature
# ----------------------------------------------------------------------------

def fondo_venato(larghezza, altezza, da, a, venature=7, seme=7, dpi=150):
    """Un gradiente diagonale fra due colori — il verde del serpentino e il bruno
    del legno — attraversato da venature bianche, come quelle della pietra e del
    marmo. Il seme fisso fa uscire sempre lo stesso fondo."""
    import math
    import random
    from PIL import ImageChops, ImageDraw, ImageFilter
    W, H = int(larghezza / 72 * dpi), int(altezza / 72 * dpi)
    c1 = [int(da[i:i + 2], 16) for i in (1, 3, 5)]
    c2 = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    # il gradiente, calcolato piccolo e poi ingrandito: è liscio comunque
    g = Image.new("RGB", (256, 256))
    px = g.load()
    for y in range(256):
        for x in range(256):
            t = min(1, max(0, (x / 255 * 0.65 + (1 - y / 255) * 0.35)))
            px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    im = g.resize((W, H), Image.BICUBIC)
    rnd = random.Random(seme)
    # Le venature del serpentino non sono linee nette: sono fasce chiare e
    # nuvolose, fitte di puntini verdi e bianchi, con qualche filo più luminoso
    fasce = Image.new("L", (W, H), 0)
    fili = Image.new("L", (W, H), 0)
    df, dl = ImageDraw.Draw(fasce), ImageDraw.Draw(fili)

    def vena(x, y, ang, passi, largo, ramo=0):
        punti = [(x, y)]
        for _ in range(passi):
            ang += rnd.uniform(-0.14, 0.14)
            x += math.cos(ang) * W / 80
            y += math.sin(ang) * W / 80
            punti.append((x, y))
            if ramo < 2 and rnd.random() < 0.035:
                vena(x, y, ang + rnd.choice((-1, 1)) * rnd.uniform(0.3, 0.8),
                     rnd.randint(15, 50), largo * 0.55, ramo + 1)
        df.line(punti, fill=int(rnd.uniform(150, 230)), width=max(2, int(largo)), joint="curve")
        if rnd.random() < 0.7:
            sfasato = [(px_ + rnd.uniform(-largo, largo) * 0.25, py_) for px_, py_ in punti]
            dl.line(sfasato, fill=int(rnd.uniform(140, 220)), width=max(1, int(W / 900)), joint="curve")

    for _ in range(venature):
        vena(-W * 0.05, rnd.uniform(-0.1, 1.1) * H, rnd.uniform(-0.6, 0.6),
             rnd.randint(80, 140), rnd.uniform(W / 70, W / 28))
    fasce = fasce.filter(ImageFilter.GaussianBlur(W / 110))
    # la grana: puntini chiari sparsi, più fitti dentro le fasce
    grana = Image.effect_noise((W, H), 90).point(lambda v: 255 if v > 205 else 0)
    grana = grana.filter(ImageFilter.GaussianBlur(W / 1400))
    nuvola = ImageChops.multiply(fasce, grana.point(lambda v: 90 + v * 0.65))
    luce = ImageChops.lighter(nuvola, fili.filter(ImageFilter.GaussianBlur(W / 1800)))
    luce = ImageChops.lighter(luce, grana.point(lambda v: v * 0.10))   # un velo di grana ovunque
    verde_chiaro = Image.new("RGB", (W, H), (214, 226, 210))
    im = Image.composite(verde_chiaro, im, luce.point(lambda v: int(v * 0.62)))
    dati = io.BytesIO()
    im.save(dati, "JPEG", quality=88)
    dati.seek(0)
    return ImageReader(dati)


# ----------------------------------------------------------------------------
# Blocchi di testo che scendono dall'alto
# ----------------------------------------------------------------------------

def blocchi(cv, lista, x, y, largo, k, chiaro=False, disegna=True):
    inchiostro = c.CARTA if chiaro else c.INCHIOSTRO
    for b in lista:
        if "etichetta" in b:
            y = etichetta(cv, b["etichetta"], x, y, k, disegna=disegna)
        elif "titolo" in b:
            y = par(cv, b["titolo"], st(k, corpo=26, leading=29 * k, textColor=inchiostro), x, y, largo, disegna)
            y -= 4 * mm * k
            if disegna:
                c.filetto(cv, x, y, 18 * mm * k, 0.6)
            y -= 6 * mm * k
        elif "sottotitolo" in b:
            y = par(cv, b["sottotitolo"], st(k, corpo=14, fontName="Cormorant-Corsivo", textColor=c.ORO), x, y, largo, disegna)
            y -= 4 * mm * k
        elif "par" in b:
            y = par(cv, b["par"], st(k, textColor=inchiostro), x, y, largo, disegna)
            y -= 3.2 * mm * k
        elif "citazione" in b:
            y = par(cv, "«" + b["citazione"] + "»",
                    st(k, corpo=13.5, fontName="Cormorant-Corsivo", textColor=inchiostro), x, y, largo, disegna)
            if b.get("firma"):
                y -= 2 * mm * k
                y = par(cv, "— " + b["firma"], st(k, corpo=10, textColor=c.GRIGIO), x, y, largo, disegna)
            y -= 5 * mm * k
        elif "righe" in b:
            col = 26 * mm * k
            for a, t in b["righe"]:
                y2 = par(cv, t, st(k, corpo=10.5, textColor=inchiostro), x + col, y, largo - col, disegna)
                par(cv, a, st(k, corpo=10.5, fontName="Cormorant-Forte", textColor=c.ORO), x, y, col, disegna)
                y = y2 - 1.6 * mm * k
            y -= 3 * mm * k
        elif "spazio" in b:
            y -= b["spazio"] * mm * k
    return y


def adatta(cv, lista, x, y, largo, alto_max, k, chiaro=False):
    """Scala il testo finché non entra nell'altezza data; restituisce la scala."""
    s = k
    while s > 0.6 * k and y - blocchi(cv, lista, x, y, largo, s, chiaro, False) > alto_max:
        s *= 0.96
    return s


# ----------------------------------------------------------------------------
# Le pagine
# ----------------------------------------------------------------------------

class Riquadro:
    """Una pagina, o un'anta della brochure: dove disegnare e a che scala."""
    def __init__(self, x, y, w, h, k, margine):
        self.x, self.y, self.w, self.h, self.k, self.m = x, y, w, h, k, margine

    @property
    def utile(self):
        return self.w - 2 * self.m


def fondo(cv, R, colore):
    cv.setFillColor(colore)
    cv.rect(R.x, R.y, R.w, R.h, stroke=0, fill=1)


def piede(cv, R, n, testo, chiaro=False):
    if n is None:
        return
    y = R.y + R.m * 0.55
    c.filetto(cv, R.x + R.m, y + 9, R.utile, 0.4)
    cv.setFont("Cormorant", 8)
    cv.setFillColor(HexColor("#CFC8BA") if chiaro else c.GRIGIO)
    if n % 2:
        cv.drawString(R.x + R.m, y, testo)
        cv.drawRightString(R.x + R.w - R.m, y, str(n))
    else:
        cv.drawString(R.x + R.m, y, str(n))
        cv.drawRightString(R.x + R.w - R.m, y, testo)


def p_copertina(cv, R, p, F):
    banda = R.h * 0.30
    if p.get("trasparente"):
        # sul fondo venato: la foto incorniciata dai margini, niente nero
        F.posa(cv, p["foto"], R.x + R.m, R.y + banda, R.utile, R.h - banda - R.m, taglia=True)
    else:
        fondo(cv, R, SCURO)
        F.posa(cv, p["foto"], R.x, R.y + banda, R.w, R.h - banda, taglia=True)
    k = R.k
    y = R.y + banda - R.m * 0.9
    y = par(cv, p["titolo"], st(k, corpo=40, leading=44 * k, textColor=c.CARTA), R.x + R.m, y, R.utile)
    y -= 3 * mm * k
    c.filetto(cv, R.x + R.m, y, 24 * mm * k, 0.8)
    y -= 6 * mm * k
    y = par(cv, p.get("sottotitolo", ""), st(k, corpo=17, fontName="Cormorant-Corsivo", textColor=c.ORO), R.x + R.m, y, R.utile)
    if p.get("riga"):
        y -= 4 * mm * k
        etichetta(cv, p["riga"], R.x + R.m, y, k, colore=c.CARTA)


def p_testo(cv, R, p, F):
    chiaro = bool(p.get("trasparente"))
    if not chiaro:
        fondo(cv, R, c.CARTA)
    alto = R.y + R.h - R.m
    basso = R.y + R.m + 8 * mm * R.k
    foto = p.get("foto", [])
    spazio_foto = (alto - basso) * p.get("quota_foto", 0.45) if foto else 0
    k = adatta(cv, p.get("blocchi", []), R.x + R.m, alto, R.utile, alto - basso - spazio_foto,
               R.k * p.get("scala", 1), chiaro)
    y = blocchi(cv, p.get("blocchi", []), R.x + R.m, alto, R.utile, k, chiaro)
    if foto:
        gruppo(cv, F, foto, R.x + R.m, basso, R.utile, y - basso - 4 * mm * R.k, R.k, in_alto=True, chiaro=chiaro)


def p_citazione(cv, R, p, F):
    if not p.get("trasparente"):
        fondo(cv, R, c.CARTA)
    k = R.k
    largo = R.utile * 0.8
    x = R.x + (R.w - largo) / 2
    lista = [{"citazione": p["citazione"], "firma": p.get("firma")}]
    chiaro = bool(p.get("trasparente"))
    h = R.y + R.h - blocchi(cv, lista, x, R.y + R.h, largo, k, chiaro, disegna=False)
    blocchi(cv, lista, x, R.y + (R.h + h) / 2, largo, k, chiaro)


def p_foto(cv, R, p, F):
    """Un'opera a pagina: la foto più grande che ci sta, la didascalia sotto."""
    chiaro = bool(p.get("trasparente"))
    if not chiaro:
        fondo(cv, R, c.CARTA)
    k = R.k
    alto = R.y + R.h - R.m
    basso = R.y + R.m + 8 * mm * k
    nota = p.get("nota")
    y_nota = basso
    if nota:
        h = R.y + R.h - par(cv, nota, st(k), 0, R.y + R.h, R.utile * 0.8, False)
        y_nota = basso + h + 6 * mm * k
        par(cv, nota, st(k, textColor=c.CARTA if chiaro else c.INCHIOSTRO),
            R.x + R.m + R.utile * 0.1, y_nota - 6 * mm * k, R.utile * 0.8)
    gruppo(cv, F, [p], R.x + R.m, y_nota, R.utile, alto - y_nota, k, chiaro=chiaro)


def p_gruppo(cv, R, p, F):
    p_testo(cv, R, {**p, "quota_foto": p.get("quota_foto", 0.8)}, F)


def p_piena(cv, R, p, F):
    fondo(cv, R, SCURO)
    F.posa(cv, p["foto"], R.x, R.y, R.w, R.h, taglia=True)


def p_sezione(cv, R, p, F):
    """L'apertura di sezione: fondo scuro, un dettaglio in alto, il numero romano."""
    if not p.get("trasparente"):
        fondo(cv, R, SCURO)
    k = R.k
    meta = R.h * 0.52
    F.posa(cv, p["foto"], R.x, R.y + R.h - meta, R.w, meta, taglia=True)
    y = R.y + R.h - meta - R.m
    if p.get("numero"):
        y = par(cv, ROMANI.get(p["numero"], str(p["numero"])), st(k, corpo=30, textColor=c.ORO), R.x + R.m, y, R.utile)
        y -= 2 * mm * k
    if p.get("etichetta"):
        y = etichetta(cv, p["etichetta"], R.x + R.m, y, k)
    y = par(cv, p["titolo"], st(k, corpo=30, leading=34 * k, textColor=c.CARTA), R.x + R.m, y, R.utile)
    y -= 4 * mm * k
    c.filetto(cv, R.x + R.m, y, 18 * mm * k, 0.6)
    y -= 7 * mm * k
    if p.get("testo"):
        par(cv, p["testo"], st(k, textColor=c.CARTA), R.x + R.m, y, R.utile * 0.85)


def p_retro(cv, R, p, F):
    if not p.get("trasparente"):
        fondo(cv, R, SCURO)
    k = R.k
    y = R.y + R.h - R.m * 2
    lista = p.get("blocchi", [])
    blocchi(cv, lista, R.x + R.m, y, R.utile, k, chiaro=True)
    if p.get("logo"):
        lw = R.utile * 0.5
        lh = lw * 616 / 888
        cv.drawImage(str(LOGO_CHIARO), R.x + (R.w - lw) / 2, R.y + R.m, lw, lh, mask="auto")


def p_bianca(cv, R, p, F):
    if not p.get("trasparente"):
        fondo(cv, R, c.CARTA)


TIPI = {"copertina": p_copertina, "testo": p_testo, "citazione": p_citazione, "foto": p_foto,
        "gruppo": p_gruppo, "piena": p_piena, "sezione": p_sezione, "retro": p_retro, "bianca": p_bianca}
SENZA_PIEDE = {"copertina", "piena", "sezione", "retro", "bianca"}


def bozza(cv, R, testo):
    cv.setFont("Cormorant-Forte", 7.5)
    cv.setFillColor(HexColor("#B04A3A"))
    cv.drawRightString(R.x + R.w - 6 * mm, R.y + R.h - 6 * mm, testo.upper())


# ----------------------------------------------------------------------------
# I due prodotti
# ----------------------------------------------------------------------------

def portfolio(cfg, F, uscita: Path):
    pag = cfg["portfolio"]["pagine"]
    if len(pag) % 4:
        print(f"   ⚠ il portfolio ha {len(pag)} pagine: per la rilegatura serve un multiplo di 4")
    cv = Canvas(str(uscita), pagesize=A4)
    cv.setTitle(cfg["portfolio"].get("titolo", "Portfolio"))
    venato = cfg["portfolio"].get("fondo_venato", {})
    fondi = {}
    for n, p in enumerate(pag, 1):
        R = Riquadro(0, 0, *A4, 1, 18 * mm)
        tipi = venato.get("tipi", [])
        if "tutte" in tipi or p["tipo"] in tipi:
            # i fondi girano su pochi semi: le venature cambiano da una pagina
            # all'altra, ma il PDF riusa le stesse immagini e resta leggero
            seme = venato.get("seme", 7) + n % venato.get("varianti", 6)
            if seme not in fondi:
                fondi[seme] = fondo_venato(*A4, venato["da"], venato["a"], venato.get("venature", 5), seme)
            cv.drawImage(fondi[seme], 0, 0, *A4)
            p = {**p, "trasparente": True}
        TIPI[p["tipo"]](cv, R, p, F)
        if p["tipo"] not in SENZA_PIEDE:
            piede(cv, R, n, cfg["portfolio"].get("piede", ""), bool(p.get("trasparente")))
        if cfg.get("bozza"):
            bozza(cv, R, cfg["bozza"])
        cv.showPage()
    cv.save()
    return len(pag)


def brochure(cfg, F, uscita: Path):
    """Due facciate A4 orizzontali, tre ante ciascuna. L'anta che si ripiega
    dentro è 2 mm più stretta, come vuole la piega a portafoglio."""
    b = cfg["brochure"]
    W, H = A4_ORIZZONTALE
    larghe = [(W + 2 * mm) / 3] * 3
    cv = Canvas(str(uscita), pagesize=A4_ORIZZONTALE)
    cv.setTitle(b.get("titolo", "Brochure"))
    for lato in ("esterno", "interno"):
        ante = b[lato]
        # esterno: aletta (stretta) · retro · copertina — interno: tre ante, l'ultima stretta
        w = [larghe[0] - 2 * mm, larghe[1], larghe[2]] if lato == "esterno" else [larghe[0], larghe[1], larghe[2] - 2 * mm]
        venato = b.get("fondo_venato", {})
        if lato in venato.get("lati", []):
            cv.drawImage(fondo_venato(W, H, venato["da"], venato["a"], venato.get("venature", 7),
                                      venato.get("seme", 7)), 0, 0, W, H)
        x = 0
        for anta, wi in zip(ante, w):
            anta = {**anta, "trasparente": lato in venato.get("lati", [])}
            R = Riquadro(x, 0, wi, H, b.get("scala", 0.82), 9 * mm)
            TIPI[anta["tipo"]](cv, R, anta, F)
            x += wi
        cv.setStrokeColor(HexColor("#D8D2C4"))
        cv.setLineWidth(0.3)
        cv.setDash(2, 3)
        xx = 0
        for wi in w[:-1]:
            xx += wi
            cv.line(xx, 0, xx, H)
        cv.setDash()
        if cfg.get("bozza"):
            bozza(cv, Riquadro(0, 0, W, H, 1, 0), cfg["bozza"] + f" · {lato}")
        cv.showPage()
    cv.save()


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    progetto = PROGETTI / sys.argv[1]
    cosa = sys.argv[2:] or ["portfolio", "brochure"]
    cfg = json.loads((progetto / "impaginazione.json").read_text(encoding="utf-8"))
    materiali = progetto / "materiali"
    F = Foto(materiali / "foto", cfg["foto"])
    if "portfolio" in cosa:
        n = portfolio(cfg, F, materiali / "portfolio.pdf")
        print(f"✓ materiali/portfolio.pdf — {n} pagine")
    if "brochure" in cosa:
        brochure(cfg, F, materiali / "brochure.pdf")
        print("✓ materiali/brochure.pdf — esterno e interno")
    if F.mancanti:
        print(f"   ⚠ foto non trovate in materiali/foto: {', '.join(sorted(F.mancanti))}")


if __name__ == "__main__":
    main()
