#!/usr/bin/env python3
"""
I materiali di sala di una mostra, tutti con la stessa grafica: il pannello
A5 con la presentazione di ogni artista e il cartellino A6 di ogni opera.

La grafica viene dalla scheda della mostra (testi-critici/mostre/<mostra>.json,
voce "grafica"): i colori della locandina e la fascia di decoro, una striscia
della locandina stessa che resta in locale in
testi-critici/mostre/catalogo/foto/. Senza fascia, il decoro si riduce al
filetto d'oro. Un carattere solo, il Cormorant Garamond.

Per ogni artista in "ordine" prende le opere della mostra: quelle con
"mostra": "<mostra>" nella scheda, o tutte se nessuna opera lo indica.

Produce in testi-critici/mostre/<mostra>/:

- pannelli.pdf     un pannello A5 per artista, in ordine
- cartellini.pdf   un cartellino A6 per opera, in ordine
- cartellini-A4.pdf  gli stessi, quattro per foglio A4, da stampare e tagliare

    py strumenti\\sala.py donne-femminile-plurale
    py strumenti\\sala.py donne-femminile-plurale --prova    una pagina di esempio
"""

import json
import sys
from pathlib import Path

from PIL import Image
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

sys.path.insert(0, str(Path(__file__).resolve().parent))
import critica as c  # noqa: E402

MOSTRE = c.RADICE / "testi-critici" / "mostre"
FOTO = MOSTRE / "catalogo" / "foto"
A5 = (148 * mm, 210 * mm)
A6 = (105 * mm, 148 * mm)


class Grafica:
    def __init__(self, cfg):
        g = cfg.get("grafica", {})
        self.carta = HexColor(g.get("carta", "#FAF7F0"))
        self.inchiostro = HexColor(g.get("inchiostro", "#1E1B18"))
        self.accento = HexColor(g.get("accento", "#6B645B"))
        self.oro = HexColor(g.get("oro", "#C9A227"))
        self.grigio = HexColor(g.get("grigio", "#6B645B"))
        f = FOTO / g["fascia"] if g.get("fascia") else None
        self.fascia = Image.open(f).convert("RGB") if f and f.exists() else None
        if f and not self.fascia:
            print(f"   ⚠ manca la fascia di decoro: {f.relative_to(c.RADICE)}")
        self.titolo = cfg["titolo"]
        self.date = cfg.get("sottotitolo", "")

    def stile(self, nome, **k):
        k.setdefault("textColor", self.inchiostro)
        return c.stile(nome, **k)

    def fondo(self, cv, formato, larga):
        """Carta e, sul lato destro, la fascia di veli della locandina."""
        w, h = formato
        cv.setFillColor(self.carta)
        cv.rect(0, 0, w, h, stroke=0, fill=1)
        if self.fascia:
            im = self.fascia
            iw, ih = im.size
            r = h / larga
            if ih / iw > r:                          # più alta: si taglia sopra e sotto
                nh = iw * r
                im = im.crop((0, (ih - nh) / 2, iw, (ih + nh) / 2))
            else:
                nw = ih / r
                im = im.crop((iw - nw, 0, iw, ih))   # più larga: si tiene il bordo destro
            cv.drawImage(ImageReader(im), w - larga, 0, larga, h)
        else:
            cv.setStrokeColor(self.oro)
            cv.setLineWidth(0.8)
            cv.line(w - larga, 8 * mm, w - larga, h - 8 * mm)

    def etichetta(self, cv, testo, x, y, corpo, colore=None):
        cv.setFont("Cormorant-Forte", corpo)
        cv.setFillColor(colore or self.oro)
        t = cv.beginText(x, y - corpo)
        t.setCharSpace(corpo * 0.22)
        t.textOut(testo.upper())
        t.setCharSpace(0)
        cv.drawText(t)
        return y - corpo * 1.5

    def filetto(self, cv, x, y, lungo, spessore=0.8):
        cv.setStrokeColor(self.oro)
        cv.setLineWidth(spessore)
        cv.line(x, y, x + lungo, y)


def dati_opera(o: dict) -> str:
    return "  ·  ".join(str(o[k]) for k in ("anno", "tecnica", "misure", "provenienza") if o.get(k))


def opere_in_mostra(scheda, mostra):
    tutte = [o for o in scheda.get("opere", []) if o.get("didascalia", {}).get("it")]
    if any("mostra" in o for o in tutte):
        return [o for o in tutte if o.get("mostra") == mostra]
    return tutte


def pannello(cv, g: Grafica, scheda):
    """A5: intestazione della mostra, nome, presentazione italiana e inglese,
    piede con il marchio della galleria. Il carattere cala se il testo non ci sta."""
    w, h = A5
    fascia = 30 * mm
    x, largo = 14 * mm, w - fascia - 14 * mm - 9 * mm
    it = scheda.get("presentazione", {}).get("it", "")
    en = scheda.get("presentazione", {}).get("en", "")
    piede = 30 * mm
    for k in [1 - 0.03 * i for i in range(12)]:
        s = dict(
            nome=g.stile("n", fontName="Cormorant-Forte", fontSize=25 * k, leading=28 * k),
            sotto=g.stile("s", fontName="Cormorant-Corsivo", fontSize=12 * k, leading=15 * k, textColor=g.accento),
            it=g.stile("i", fontSize=11 * k, leading=15.4 * k, alignment=TA_JUSTIFY),
            en=g.stile("e", fontName="Cormorant-Corsivo", fontSize=9 * k, leading=12.2 * k,
                       alignment=TA_JUSTIFY, textColor=g.grigio),
        )
        alto = (c.misura(scheda["nome"], s["nome"], largo) + c.misura(c.sottotitolo(scheda) or " ", s["sotto"], largo)
                + 14 * mm + c.misura(it, s["it"], largo) + (c.misura(en, s["en"], largo) + 6 * mm if en else 0))
        if alto <= h - 34 * mm - piede:
            break
    g.fondo(cv, A5, fascia)
    y = h - 14 * mm
    y = g.etichetta(cv, g.titolo, x, y, 7.5)
    y = c.scrivi(cv, g.date, g.stile("d", fontName="Cormorant-Corsivo", fontSize=8.5, leading=11,
                 textColor=g.accento), x, y - 1, largo) - 12 * mm
    y = c.scrivi(cv, scheda["nome"], s["nome"], x, y, largo)
    if c.sottotitolo(scheda):
        y = c.scrivi(cv, c.sottotitolo(scheda), s["sotto"], x, y - 1, largo)
    y -= 5 * mm
    g.filetto(cv, x, y, 18 * mm, 1)
    y -= 7 * mm
    y = c.scrivi(cv, it, s["it"], x, y, largo)
    if en:
        y -= 5 * mm
        c.scrivi(cv, en, s["en"], x, y, largo)
    # piede: marchio e indirizzo
    g.filetto(cv, x, 24 * mm, largo, 0.4)
    c.logo(cv, x, 21 * mm, 15 * mm)
    st = g.stile("p", fontSize=7, leading=9, textColor=g.grigio)
    c.scrivi(cv, "BE Art Gallery & Creative Lab<br/>Via San Pietro 24, Pistoia · beartgallery.eu",
             st, x + 18 * mm, 19.5 * mm, largo - 18 * mm)


def cartellino(cv, g: Grafica, scheda, o):
    """A6: artista, titolo, dati, didascalia italiana e inglese."""
    w, h = A6
    fascia = 17 * mm
    x, largo = 10 * mm, w - fascia - 10 * mm - 6 * mm
    it = o["didascalia"]["it"]
    en = o["didascalia"].get("en", "")
    for k in [1 - 0.03 * i for i in range(14)]:
        s = dict(
            titolo=g.stile("t", fontName="Cormorant-Corsivo", fontSize=17 * k, leading=19.5 * k),
            dati=g.stile("d", fontSize=7.8 * k, leading=10 * k, textColor=g.grigio),
            it=g.stile("i", fontSize=9.6 * k, leading=13.2 * k, alignment=TA_JUSTIFY),
            en=g.stile("e", fontName="Cormorant-Corsivo", fontSize=8 * k, leading=10.6 * k,
                       alignment=TA_JUSTIFY, textColor=g.grigio),
        )
        alto = (c.misura(o["titolo"], s["titolo"], largo) + (c.misura(dati_opera(o), s["dati"], largo) if dati_opera(o) else 0)
                + 10 * mm + c.misura(it, s["it"], largo) + (c.misura(en, s["en"], largo) + 4 * mm if en else 0))
        if alto <= h - 30 * mm - 14 * mm:
            break
    g.fondo(cv, A6, fascia)
    y = h - 10 * mm
    y = g.etichetta(cv, scheda["nome"], x, y, 7, g.accento) - 6 * mm
    y = c.scrivi(cv, o["titolo"], s["titolo"], x, y, largo)
    if dati_opera(o):
        y = c.scrivi(cv, dati_opera(o), s["dati"], x, y - 1, largo)
    y -= 3.5 * mm
    g.filetto(cv, x, y, 12 * mm, 0.8)
    y -= 5 * mm
    y = c.scrivi(cv, it, s["it"], x, y, largo)
    if en:
        y -= 3.5 * mm
        c.scrivi(cv, en, s["en"], x, y, largo)
    g.filetto(cv, x, 14 * mm, largo, 0.4)
    g.etichetta(cv, g.titolo, x, 12.5 * mm, 5.5)
    c.scrivi(cv, "BE Art Gallery & Creative Lab · Pistoia", g.stile("p", fontSize=6.5, leading=8, textColor=g.grigio),
             x, 8.5 * mm, largo)


def quattro_per_foglio(sorgente: Path, uscita: Path) -> None:
    """I cartellini A6 quattro per foglio A4, con i segni di taglio al centro."""
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(str(sorgente))
    nuovo = pdfium.PdfDocument.new()
    W, H = 210 * mm, 297 * mm
    posti = [(0, H / 2), (W / 2, H / 2), (0, 0), (W / 2, 0)]
    for inizio in range(0, len(doc), 4):
        foglio = nuovo.new_page(W, H)
        for (px, py), i in zip(posti, range(inizio, min(inizio + 4, len(doc)))):
            ogg = doc.page_as_xobject(i, nuovo).as_pageobject()
            ogg.transform(pdfium.PdfMatrix().translate(px, py))
            foglio.insert_obj(ogg)
        foglio.gen_content()
    nuovo.save(str(uscita))


def main() -> None:
    argomenti = [a for a in sys.argv[1:] if not a.startswith("--")]
    mostra = argomenti[0] if argomenti else "donne-femminile-plurale"
    prova = "--prova" in sys.argv
    cfg = json.loads((MOSTRE / f"{mostra}.json").read_text(encoding="utf-8"))
    g = Grafica(cfg)
    uscita = MOSTRE / mostra
    uscita.mkdir(exist_ok=True)

    schede = []
    for nome in cfg["ordine"]:
        f = c.ARTISTI / nome / "scheda.json"
        if not f.exists():
            print(f"   · {nome}: scheda non ancora scritta")
            continue
        s = json.loads(f.read_text(encoding="utf-8"))
        lista = opere_in_mostra(s, mostra)
        if prova or lista:
            schede.append((s, lista))
    if prova:
        schede = schede[:1]
        if schede and not schede[0][1]:
            schede[0] = (schede[0][0], [o for o in schede[0][0]["opere"] if o.get("didascalia", {}).get("it")][:1])
    if not schede:
        print("Nessuna scheda pronta: niente da impaginare.")
        return

    suffisso = "-prova" if prova else ""
    p = uscita / f"pannelli{suffisso}.pdf"
    cv = Canvas(str(p), pagesize=A5)
    cv.setTitle(f"{cfg['titolo']} — pannelli")
    for s, _ in schede:
        pannello(cv, g, s)
        cv.showPage()
    cv.save()

    q = uscita / f"cartellini{suffisso}.pdf"
    cv = Canvas(str(q), pagesize=A6)
    cv.setTitle(f"{cfg['titolo']} — cartellini")
    n = 0
    for s, lista in schede:
        for o in lista:
            cartellino(cv, g, s, o)
            cv.showPage()
            n += 1
    cv.save()
    a4 = uscita / f"cartellini-A4{suffisso}.pdf"
    quattro_per_foglio(q, a4)
    print(f"\n{cfg['titolo']}: {len(schede)} pannelli, {n} cartellini")
    for f in (p, q, a4):
        print(f"   {f.relative_to(c.RADICE)}")
    print()


if __name__ == "__main__":
    main()
