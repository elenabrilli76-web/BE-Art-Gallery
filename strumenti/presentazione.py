#!/usr/bin/env python3
"""
La presentazione di una mostra, con la stessa grafica delle pagine di sala
(strumenti/sala.py):

- presentazione.pdf   in copertina la locandina ("grafica" → "locandina"),
                      poi il testo della mostra ("testo" nella scheda della
                      mostra, con i titoletti {"titolo": ...}) che scorre su
                      più pagine A4, poi una pagina per artista con la
                      presentazione e TUTTE le didascalie insieme, anche
                      quando in sala le opere sono divise in più fogli
- pannello-sala.pdf   la versione breve in due facciate A4 da appendere in
                      sala ("pannello" nella scheda: una lista di paragrafi
                      per facciata), con l'elenco degli artisti in fondo

    py strumenti\\presentazione.py donne-femminile-plurale
"""

import json
import sys
from pathlib import Path

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

sys.path.insert(0, str(Path(__file__).resolve().parent))
import critica as c  # noqa: E402
import sala  # noqa: E402

A4 = sala.A4
W, H = A4
FASCIA = 38 * mm
X = 20 * mm
LARGO = W - FASCIA - X - 14 * mm
BASSO = 32 * mm
PER_PAGINA = 8


def piede(cv, g, n=None):
    g.filetto(cv, X, 28 * mm, LARGO, 0.4)
    c.logo(cv, X, 24 * mm, 17 * mm)
    st = g.stile("p", fontSize=8, leading=10.5, textColor=g.grigio)
    c.scrivi(cv, "BE Art Gallery & Creative Lab<br/>Via San Pietro 24, Pistoia · beartgallery.eu",
             st, X + 21 * mm, 21.5 * mm, LARGO - 21 * mm)
    if n:
        cv.setFont("Cormorant", 9)
        cv.setFillColor(g.grigio)
        cv.drawRightString(X + LARGO, 21 * mm, str(n))


def intestazione(cv, g, cfg, grande=True):
    """Titolo e date della mostra, e sotto il claim. Restituisce la y sotto."""
    y = H - 20 * mm
    if grande:
        y = c.scrivi(cv, cfg["titolo"], g.stile("t", fontName="Cormorant-Forte", fontSize=32, leading=36),
                     X, y - 6 * mm, LARGO)
        y = c.scrivi(cv, cfg["sottotitolo"], g.stile("s", fontName="Cormorant-Corsivo", fontSize=14, leading=18,
                     textColor=g.accento), X, y - 2, LARGO)
        y = c.scrivi(cv, cfg["luogo"], g.stile("l", fontSize=10.5, leading=13, textColor=g.grigio), X, y - 1, LARGO)
        y -= 6 * mm
        g.filetto(cv, X, y, 22 * mm, 1)
        y -= 7 * mm
        if cfg.get("claim"):
            y = c.scrivi(cv, f"«{cfg['claim']}»", g.stile("c", fontName="Cormorant-Corsivo", fontSize=15,
                         leading=19, textColor=g.oro), X, y, LARGO) - 8 * mm
        return y
    y = g.etichetta(cv, cfg["titolo"], X, y, 9)
    return c.scrivi(cv, cfg["sottotitolo"], g.stile("d", fontName="Cormorant-Corsivo", fontSize=11, leading=14,
                    textColor=g.accento), X, y - 1, LARGO) - 10 * mm


def copertina(cv, g, cfg):
    """La locandina della mostra a pagina piena: riempie l'A4 in altezza e
    perde solo una sottile striscia ai lati. Senza locandina, niente copertina."""
    f = sala.FOTO / cfg.get("grafica", {}).get("locandina", "")
    if not f.is_file():
        return False
    from PIL import Image
    from reportlab.lib.utils import ImageReader
    im = Image.open(f).convert("RGB")
    iw, ih = im.size
    if iw / ih > W / H:                        # più larga dell'A4: si taglia ai lati
        nw = ih * W / H
        im = im.crop((round((iw - nw) / 2), 0, round((iw + nw) / 2), ih))
    else:
        nh = iw * H / W
        im = im.crop((0, round((ih - nh) / 2), iw, round((ih + nh) / 2)))
    cv.drawImage(ImageReader(im), 0, 0, W, H)
    cv.showPage()
    return True


def testo_mostra(cv, g, cfg, n):
    """Il testo lungo che scorre sulle pagine; i titoletti non restano mai
    soli in fondo. Restituisce il numero della prossima pagina."""
    corpo = g.stile("p", fontSize=11.5, leading=16.5, alignment=TA_JUSTIFY)
    tit = g.stile("h", fontName="Cormorant-Corsivo", fontSize=16, leading=20, textColor=g.accento)
    g.fondo(cv, A4, FASCIA)
    y = intestazione(cv, g, cfg)

    def nuova():
        nonlocal y, n
        piede(cv, g, n)
        cv.showPage()
        n += 1
        g.fondo(cv, A4, FASCIA)
        y = intestazione(cv, g, cfg, grande=False)

    voci = cfg["testo"]
    for i, v in enumerate(voci):
        if isinstance(v, dict):
            seguito = voci[i + 1] if i + 1 < len(voci) and isinstance(voci[i + 1], str) else ""
            serve = c.misura(v["titolo"], tit, LARGO) + 6 * mm + 3 * corpo.leading
            if y - serve < BASSO:
                nuova()
            y = c.scrivi(cv, v["titolo"], tit, X, y - 3 * mm, LARGO) - 2 * mm
            continue
        par = Paragraph(v.replace("'", "’"), corpo)
        while True:
            _, alto = par.wrap(LARGO, 10_000)
            if y - alto >= BASSO:
                par.drawOn(cv, X, y - alto)
                y -= alto + 3.5 * mm
                break
            pezzi = par.split(LARGO, y - BASSO)
            if len(pezzi) == 2:
                _, h0 = pezzi[0].wrap(LARGO, 10_000)
                pezzi[0].drawOn(cv, X, y - h0)
                par = pezzi[1]
            nuova()
    piede(cv, g, n)
    cv.showPage()
    return n + 1


def pannello(cv, g, cfg, nomi):
    """Due facciate, carattere grande, da leggere in piedi davanti al muro."""
    pagine = cfg["pannello"]

    def entra(k):
        corpo = g.stile("p", fontSize=15 * k, leading=22 * k, alignment=TA_JUSTIFY)
        for p, paragrafi in enumerate(pagine):
            alto = sum(c.misura(t, corpo, LARGO) + 6 * mm for t in paragrafi)
            disponibile = H - (115 * mm if p == 0 else 50 * mm) - (75 * mm if p == len(pagine) - 1 else 40 * mm)
            if alto > disponibile:
                return False
        return True

    k = next(k for k in [1.5 - 0.03 * i for i in range(30)] if entra(k))   # lo stesso corpo su ogni facciata
    corpo = g.stile("p", fontSize=15 * k, leading=22 * k, alignment=TA_JUSTIFY)
    for p, paragrafi in enumerate(pagine):
        g.fondo(cv, A4, FASCIA)
        y = intestazione(cv, g, cfg, grande=(p == 0))
        for i, t in enumerate(paragrafi):
            ultimo = p == len(pagine) - 1 and i == len(paragrafi) - 1
            st = g.stile("cl", fontName="Cormorant-Corsivo", fontSize=17, leading=22, textColor=g.oro) if ultimo \
                else corpo
            y = c.scrivi(cv, t, st, X, y, LARGO) - 6 * mm
        if p == len(pagine) - 1:
            y -= 4 * mm
            y = g.etichetta(cv, "Artisti in mostra", X, y, 8.5) - 1 * mm
            c.scrivi(cv, "  ·  ".join(nomi), g.stile("n", fontSize=11, leading=16), X, y, LARGO)
            if cfg.get("riga_presentazione"):
                c.scrivi(cv, cfg["riga_presentazione"], g.stile("r", fontName="Cormorant-Corsivo", fontSize=10,
                         leading=13, textColor=g.accento), X, 40 * mm, LARGO)
        piede(cv, g)
        cv.showPage()


def main() -> None:
    mostra = sys.argv[1] if len(sys.argv) > 1 else "donne-femminile-plurale"
    cfg = json.loads((sala.MOSTRE / f"{mostra}.json").read_text(encoding="utf-8"))
    g = sala.Grafica(cfg)
    uscita = sala.MOSTRE / mostra
    uscita.mkdir(exist_ok=True)

    schede = []
    for nome in cfg["ordine"]:
        f = c.ARTISTI / nome / "scheda.json"
        if not f.exists():
            print(f"   · {nome}: scheda non ancora scritta")
            continue
        s = c.per_mostra(json.loads(f.read_text(encoding="utf-8")), mostra)
        lista = [o for o in s["opere"] if o.get("didascalia", {}).get("it")]
        if lista:
            schede.append((s, lista))

    p = uscita / "presentazione.pdf"
    cv = Canvas(str(p), pagesize=A4)
    cv.setTitle(f"{cfg['titolo']} — presentazione")
    cv.setAuthor("BE Art Gallery & Creative Lab")
    copertina(cv, g, cfg)
    n = testo_mostra(cv, g, cfg, 1)
    for s, lista in schede:
        # tutte le opere insieme, qualunque sia il foglio di sala; oltre le sei
        # didascalie l'artista continua sulla pagina dopo, perché il carattere
        # resti leggibile
        pagine = -(-len(lista) // PER_PAGINA)
        passo = -(-len(lista) // pagine)          # pagine riempite in modo uniforme
        for i in range(0, len(lista), passo):
            parte = s if i == 0 else {**s, "presentazione": {}}
            sala.pagina(cv, g, parte, lista[i:i + passo])
            cv.showPage()
            n += 1
    cv.save()

    q = uscita / "pannello-sala.pdf"
    cv = Canvas(str(q), pagesize=A4)
    cv.setTitle(f"{cfg['titolo']} — pannello di sala")
    cv.setAuthor("BE Art Gallery & Creative Lab")
    pannello(cv, g, cfg, [s["nome"] for s, _ in schede])
    cv.save()
    print(f"\n{cfg['titolo']}: {n - 1} pagine di presentazione, {len(schede)} artisti")
    for f in (p, q):
        print(f"   {f.relative_to(c.RADICE)}")
    print()


if __name__ == "__main__":
    main()
