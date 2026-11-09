#!/usr/bin/env python3
"""
Le pagine di sala di una mostra, tutte con la stessa grafica: una pagina A4
per artista con il titolo e le date della mostra, il nome, il testo critico
in italiano e, sotto, la didascalia di ogni opera esposta. È lo stesso
impianto delle pagine di I Luoghi dell'Anima, con i colori della mostra.

La grafica viene dalla scheda della mostra (testi-critici/mostre/<mostra>.json,
voce "grafica"): i colori della locandina e la fascia di decoro, una striscia
della locandina stessa che resta in locale in
testi-critici/mostre/catalogo/foto/. Senza fascia, il decoro si riduce al
filetto d'oro. Un carattere solo, il Cormorant Garamond.

Per ogni artista in "ordine" prende le opere della mostra e la presentazione
giusta: vedi critica.per_mostra.

Produce in testi-critici/mostre/<mostra>/: schede.pdf, una pagina per
artista, e in artisti/ lo stesso diviso in un PDF per artista.

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
A4 = (210 * mm, 297 * mm)


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
        self.riga = cfg.get("riga_sala", "")      # una riga uguale in ogni pagina, sopra il piede

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
            cv.line(w - larga, 10 * mm, w - larga, h - 10 * mm)

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
    return "  ·  ".join(str(o[k]) for k in ("serie", "anno", "tecnica", "misure", "provenienza") if o.get(k))


def pagina(cv, g: Grafica, scheda, lista):
    """A4, una pagina per artista: titolo e date della mostra, nome, testo
    critico in italiano e, sotto, la didascalia di ogni opera, in due colonne
    se le opere sono più d'una. Tutto si adatta finché sta in una pagina."""
    w, h = A4
    fascia = 38 * mm
    x = 20 * mm
    largo = w - fascia - x - 14 * mm
    giunto = 8 * mm
    colonne = 1 if len(lista) <= 1 else 2
    col = largo if colonne == 1 else (largo - giunto) / 2
    it = scheda.get("presentazione", {}).get("it", "")
    righe = [lista[i:i + colonne] for i in range(0, len(lista), colonne)]
    alto_utile = h - 20 * mm - 34 * mm - 30 * mm        # sotto l'intestazione, sopra il piede
    if g.riga:
        alto_utile -= 12 * mm

    def scheda_alta(o, s, k):
        a = c.misura(o["titolo"], s["titolo"], col)
        if dati_opera(o):
            a += c.misura(dati_opera(o), s["dati"], col)
        return a + 6 * mm * k + c.misura(o["didascalia"]["it"], s["dida"], col)

    for k in [1 - 0.025 * i for i in range(20)]:
        s = dict(
            nome=g.stile("n", fontName="Cormorant-Forte", fontSize=30 * k, leading=34 * k),
            it=g.stile("i", fontSize=12.5 * k, leading=17.5 * k, alignment=TA_JUSTIFY),
            titolo=g.stile("t", fontName="Cormorant-Corsivo", fontSize=15 * k, leading=18 * k),
            dati=g.stile("d", fontSize=9 * k, leading=11.5 * k, textColor=g.grigio),
            dida=g.stile("di", fontSize=11 * k, leading=15 * k, alignment=TA_JUSTIFY),
        )
        alto = c.misura(scheda["nome"], s["nome"], largo) + 13 * mm * k + c.misura(it, s["it"], largo) + 12 * mm * k
        alto += sum(max(scheda_alta(o, s, k) for o in r) + 8 * mm * k for r in righe)
        if alto <= alto_utile:
            break

    g.fondo(cv, A4, fascia)
    y = h - 20 * mm
    y = g.etichetta(cv, g.titolo, x, y, 9)
    y = c.scrivi(cv, g.date, g.stile("d", fontName="Cormorant-Corsivo", fontSize=11, leading=14,
                 textColor=g.accento), x, y - 1, largo) - 16 * mm
    y = c.scrivi(cv, scheda["nome"], s["nome"], x, y, largo)
    y -= 5 * mm * k
    g.filetto(cv, x, y, 22 * mm, 1)
    y -= 8 * mm * k
    if it:
        y = c.scrivi(cv, it, s["it"], x, y, largo) - 12 * mm * k
    for r in righe:
        fondo_riga = y
        for j, o in enumerate(r):
            xx = x + j * (col + giunto)
            yy = c.scrivi(cv, o["titolo"], s["titolo"], xx, y, col)
            if dati_opera(o):
                yy = c.scrivi(cv, dati_opera(o), s["dati"], xx, yy, col)
            yy -= 2.5 * mm * k
            g.filetto(cv, xx, yy, 10 * mm, 0.7)
            yy -= 3.5 * mm * k
            yy = c.scrivi(cv, o["didascalia"]["it"], s["dida"], xx, yy, col)
            fondo_riga = min(fondo_riga, yy)
        y = fondo_riga - 8 * mm * k
    # la riga comune a tutte le pagine della mostra
    if g.riga:
        c.scrivi(cv, g.riga, g.stile("r", fontName="Cormorant-Corsivo", fontSize=10, leading=13,
                 textColor=g.accento), x, 39 * mm, largo)
    # piede: marchio e indirizzo
    g.filetto(cv, x, 28 * mm, largo, 0.4)
    c.logo(cv, x, 24 * mm, 17 * mm)
    st = g.stile("p", fontSize=8, leading=10.5, textColor=g.grigio)
    c.scrivi(cv, "BE Art Gallery & Creative Lab<br/>Via San Pietro 24, Pistoia · beartgallery.eu",
             st, x + 21 * mm, 21.5 * mm, largo - 21 * mm)


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
        s = c.per_mostra(json.loads(f.read_text(encoding="utf-8")), mostra)
        lista = [o for o in s["opere"] if o.get("didascalia", {}).get("it")]
        if prova or lista:
            schede.append((s, lista))
    if prova:
        # le schede già in archivio, con le opere che hanno, solo per vedere la grafica
        schede = [(s, l or [o for o in s["opere"] if o.get("didascalia", {}).get("it")]) for s, l in schede]
    if not schede:
        print("Nessuna scheda pronta: niente da impaginare.")
        return

    suffisso = "-prova" if prova else ""
    p = uscita / f"schede{suffisso}.pdf"
    cv = Canvas(str(p), pagesize=A4)
    cv.setTitle(f"{cfg['titolo']} — artisti e opere")
    cv.setAuthor("BE Art Gallery & Creative Lab")
    n = 0
    for s, lista in schede:
        pagina(cv, g, s, lista)
        cv.showPage()
        n += len(lista)
    cv.save()
    # e un file per artista, da stampare o mandare uno per uno
    singole = uscita / f"artisti{suffisso}"
    singole.mkdir(exist_ok=True)
    for s, lista in schede:
        f = singole / f"{c.nome_file(s['nome'])}.pdf"
        cv = Canvas(str(f), pagesize=A4)
        cv.setTitle(f"{cfg['titolo']} — {s['nome']}")
        cv.setAuthor("BE Art Gallery & Creative Lab")
        pagina(cv, g, s, lista)
        cv.showPage()
        cv.save()
    print(f"\n{cfg['titolo']}: {len(schede)} pagine, {n} opere\n   {p.relative_to(c.RADICE)}")
    print(f"   {singole.relative_to(c.RADICE)}/  un PDF per artista\n")


if __name__ == "__main__":
    main()
