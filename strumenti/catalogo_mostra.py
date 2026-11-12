#!/usr/bin/env python3
"""
Il catalogo di una mostra con la sua grafica (colori e fascia della
locandina, voce "grafica" nella scheda della mostra), in A4 o in A5, sempre in
multipli di 4 pagine: si stampa a fogli piegati e pinzati al centro.

    py strumenti\\catalogo_mostra.py donne-femminile-plurale          A4
    py strumenti\\catalogo_mostra.py donne-femminile-plurale --a5     A5

Legge la scheda della mostra (testo, ordine degli artisti), le schede degli
artisti (critica.per_mostra: presentazione e didascalie della mostra, tutte le
opere di un artista insieme, qualunque sia il foglio di sala) e il testo della
galleria (testi-critici/galleria.json). Le foto restano in locale, in
testi-critici/mostre/catalogo/foto/<mostra>/:

    locandina-mostra.jpg          la copertina ("grafica" → "locandina")
    locandina-evento.jpg          la pagina dell'evento che contiene la mostra
    <artista>/<opera>.jpg         una foto per opera, col nome di critica.nome_opera

Le pagine, in ordine: copertina, frontespizio, testo della mostra, gli
artisti (una pagina con presentazione e prime opere, poi le altre a gruppi),
l'elenco delle opere, l'evento, la galleria, le note, il retro nero col
marchio. Per arrivare al multiplo di 4 entrano, nell'ordine e solo se servono,
la pagina dell'evento, l'elenco delle opere e una pagina per le note; solo in
ultimo il testo della mostra si allarga su più pagine.

Produce in testi-critici/mostre/catalogo/:

- <mostra>-libro-A4.pdf (o -A5)        le pagine in ordine, per la tipografia
- <mostra>-libro-stampa-A3.pdf (o -A4) due pagine per foglio, nell'ordine di
                                       piegatura: fronte-retro sul lato corto,
                                       si piega a metà, si pinza
"""

import io
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

sys.path.insert(0, str(Path(__file__).resolve().parent))
import critica as c  # noqa: E402
import sala  # noqa: E402

MOSTRE = c.RADICE / "testi-critici" / "mostre"
CATALOGO = MOSTRE / "catalogo"
GALLERIA = c.RADICE / "testi-critici" / "galleria.json"
NERO = HexColor("#141312")
ROMANI = ["I", "II", "III", "IV", "V", "VI"]

FORMATI = {
    # pagina, margine interno, fascia sul lato esterno, stacco dalla fascia,
    # alto, basso, corpo, opere sulla prima pagina dell'artista e sulle seguenti
    "A4": dict(W=210 * mm, H=297 * mm, interno=20 * mm, fascia=16 * mm, stacco=13 * mm,
               alto=22 * mm, basso=26 * mm, k=1.0, prima=2, poi=4, stampa="A3"),
    "A5": dict(W=148 * mm, H=210 * mm, interno=13 * mm, fascia=10 * mm, stacco=9 * mm,
               alto=14 * mm, basso=19 * mm, k=0.8, prima=2, poi=4, stampa="A4"),
}


class Libro:
    def __init__(self, cfg, formato, cartella):
        self.cfg = cfg
        self.f = FORMATI[formato]
        self.W, self.H = self.f["W"], self.f["H"]
        self.K = self.f["k"]
        self.g = sala.Grafica(cfg)
        self.cartella = cartella
        self._fasce = {}

    # ------------------------------------------------------------------ pagina

    def x(self, n):
        """Margine sinistro e larghezza utile: la fascia sta sul lato esterno,
        a destra sulle pagine dispari, a sinistra sulle pari."""
        f = self.f
        largo = self.W - f["interno"] - f["fascia"] - f["stacco"]
        return (f["interno"] if n % 2 else f["fascia"] + f["stacco"]), largo

    @property
    def cima(self):
        return self.H - self.f["alto"]

    @property
    def fondo_testo(self):
        return self.f["basso"] + 4 * mm * self.K

    def fascia(self, destra):
        """La striscia della locandina, ritagliata una volta sola per lato e
        salvata in JPEG: così nel PDF c'è un'immagine sola, ripetuta."""
        if destra not in self._fasce:
            self._fasce[destra] = None
            if self.g.fascia:
                im = self.g.fascia
                iw, ih = im.size
                r = self.H / self.f["fascia"]
                if ih / iw > r:
                    nh = iw * r
                    im = im.crop((0, (ih - nh) / 2, iw, (ih + nh) / 2))
                else:
                    nw = ih / r
                    im = im.crop((iw - nw, 0, iw, ih))
                if not destra:
                    im = ImageOps.mirror(im)
                b = io.BytesIO()
                im.save(b, "JPEG", quality=88)
                b.seek(0)
                self._fasce[destra] = ImageReader(b)
        return self._fasce[destra]

    def carta(self, cv, n):
        cv.setFillColor(self.g.carta)
        cv.rect(0, 0, self.W, self.H, stroke=0, fill=1)
        f = self.fascia(bool(n % 2))
        larga = self.f["fascia"]
        if f:
            cv.drawImage(f, self.W - larga if n % 2 else 0, 0, larga, self.H)

    def piede(self, cv, n):
        x, largo = self.x(n)
        y = self.f["basso"] - 6 * mm * self.K
        self.g.filetto(cv, x, y + 4 * mm * self.K, largo, 0.4)
        cv.setFont("Cormorant", 7.5 * self.K)
        cv.setFillColor(self.g.grigio)
        testo = f"{self.cfg['titolo']}  ·  BE Art Gallery & Creative Lab"
        if n % 2:
            cv.drawString(x, y, testo)
            cv.drawRightString(x + largo, y, str(n))
        else:
            cv.drawString(x, y, str(n))
            cv.drawRightString(x + largo, y, testo)

    def st(self, nome, corpo, interlinea, **k):
        k.setdefault("textColor", self.g.inchiostro)
        return c.stile(nome, fontSize=corpo * self.K, leading=interlinea * self.K, **k)

    def etichetta(self, cv, testo, x, y, corpo=8.5):
        return self.g.etichetta(cv, testo, x, y, corpo * self.K)

    # ------------------------------------------------------------------ immagini

    @staticmethod
    def jpeg(file, lato=1400):
        im = ImageOps.exif_transpose(Image.open(file)).convert("RGB")
        im.thumbnail((lato, lato))
        b = io.BytesIO()
        im.save(b, "JPEG", quality=86)
        b.seek(0)
        return ImageReader(b), im.size

    def pagina_intera(self, cv, file):
        """Un'immagine a pagina piena, tagliata appena ai bordi se serve."""
        im = ImageOps.exif_transpose(Image.open(file)).convert("RGB")
        iw, ih = im.size
        if iw / ih > self.W / self.H:
            nw = ih * self.W / self.H
            im = im.crop((round((iw - nw) / 2), 0, round((iw + nw) / 2), ih))
        else:
            nh = iw * self.H / self.W
            im = im.crop((0, round((ih - nh) / 2), iw, round((ih + nh) / 2)))
        im.thumbnail((2400, 2400))
        b = io.BytesIO()
        im.save(b, "JPEG", quality=88)
        b.seek(0)
        cv.drawImage(ImageReader(b), 0, 0, self.W, self.H)

    def foto(self, cv, file, x, y_alto, largo, alto):
        """Una foto centrata nel riquadro, senza deformarla; se manca, un
        riquadro sottile ne tiene il posto."""
        if not file.exists():
            print(f"   ⚠ manca la foto {file.relative_to(c.RADICE)}")
            cv.setStrokeColor(self.g.grigio)
            cv.setLineWidth(0.3)
            cv.rect(x, y_alto - alto, largo, alto)
            return
        r, (iw, ih) = self.jpeg(file)
        s = min(largo / iw, alto / ih)
        w, h = iw * s, ih * s
        cv.drawImage(r, x + (largo - w) / 2, y_alto - h, w, h)

    @staticmethod
    def proporzione(file):
        if not file.exists():
            return 1.3
        im = ImageOps.exif_transpose(Image.open(file))
        return im.size[1] / im.size[0]

    # ------------------------------------------------------------------ testo che scorre

    def scorri(self, cv, voci, k, n0, disegna):
        """Il testo della mostra, coi titoletti, da pagina n0 in avanti.
        Restituisce quante pagine ha usato."""
        corpo = self.st("p", 11 * k, 15.5 * k, alignment=TA_JUSTIFY)
        tit = self.st("h", 15 * k, 18.5 * k, fontName="Cormorant-Corsivo", textColor=self.g.accento)
        n = n0
        x, largo = self.x(n)

        def apri():
            nonlocal x, largo
            x, largo = self.x(n)
            if disegna:
                self.carta(cv, n)
            return self.cima

        def chiudi():
            nonlocal n
            if disegna:
                self.piede(cv, n)
                cv.showPage()
            n += 1

        y = apri()
        y = self.etichetta(cv, self.cfg["titolo"], x, y) if disegna else y - 8.5 * self.K * 1.5
        y -= 4 * mm * self.K
        for i, v in enumerate(voci):
            if isinstance(v, dict):
                serve = c.misura(v["titolo"], tit, largo) + 5 * mm * k + 3 * corpo.leading
                if y - serve < self.fondo_testo:
                    chiudi()
                    y = apri()
                elif y < self.cima - 20 * mm * self.K:
                    y -= 4 * mm * k
                if disegna:
                    c.scrivi(cv, v["titolo"], tit, x, y, largo)
                y -= c.misura(v["titolo"], tit, largo) + 1.5 * mm * k
                continue
            par = Paragraph(v.replace("'", "’"), corpo)
            while True:
                _, alto = par.wrap(largo, 10_000)
                if y - alto >= self.fondo_testo:
                    if disegna:
                        par.drawOn(cv, x, y - alto)
                    y -= alto + 3 * mm * k
                    break
                pezzi = par.split(largo, y - self.fondo_testo)
                if len(pezzi) == 2:
                    _, h0 = pezzi[0].wrap(largo, 10_000)
                    if disegna:
                        pezzi[0].drawOn(cv, x, y - h0)
                    par = pezzi[1]
                chiudi()
                y = apri()
        chiudi()
        return n - n0

    def adatta(self, pagine):
        """Il corpo più grande con cui il testo della mostra sta in `pagine`."""
        basso, alto = 0.6, 1.6
        for _ in range(24):
            k = (basso + alto) / 2
            if self.scorri(None, self.cfg["testo"], k, 3, False) <= pagine:
                basso = k
            else:
                alto = k
        return basso

    # ------------------------------------------------------------------ le pagine

    def copertina(self, cv):
        f = sala.FOTO / self.cfg.get("grafica", {}).get("locandina", "")
        if f.is_file():
            self.pagina_intera(cv, f)
        else:
            print("   ⚠ manca la locandina per la copertina")
            self.carta(cv, 1)
            c.scrivi(cv, self.cfg["titolo"], self.st("t", 34, 38, fontName="Cormorant-Forte"),
                     *self.x(1)[:1], self.H / 2, self.x(1)[1])
        cv.showPage()

    def frontespizio(self, cv, nomi, n=2):
        self.carta(cv, n)
        x, largo = self.x(n)
        K = self.K
        c.logo(cv, x, self.cima, 26 * mm * K)
        y = self.cima - 34 * mm * K
        y = c.scrivi(cv, self.cfg["titolo"], self.st("t", 30, 33, fontName="Cormorant-Forte"), x, y, largo)
        y = c.scrivi(cv, self.cfg["sottotitolo"], self.st("s", 13, 17, fontName="Cormorant-Corsivo",
                     textColor=self.g.accento), x, y - 2, largo)
        y = c.scrivi(cv, self.cfg["luogo"], self.st("l", 10, 13, textColor=self.g.grigio), x, y - 1, largo)
        y -= 6 * mm * K
        self.g.filetto(cv, x, y, 20 * mm * K, 1)
        y -= 7 * mm * K
        if self.cfg.get("claim"):
            y = c.scrivi(cv, f"«{self.cfg['claim']}»", self.st("c", 14, 18, fontName="Cormorant-Corsivo",
                         textColor=self.g.oro), x, y, largo) - 3 * mm * K
        if self.cfg.get("parole"):
            y = c.scrivi(cv, "  ·  ".join(self.cfg["parole"]), self.st("w", 10, 13, textColor=self.g.grigio),
                         x, y, largo)
        y -= 12 * mm * K
        y = self.etichetta(cv, "Artisti in mostra", x, y) - 1.5 * mm * K
        nome = self.st("n", 13, 17.5)
        for s in nomi:
            y = c.scrivi(cv, s, nome, x, y, largo)
        basso = self.f["basso"] + 2 * mm
        if self.cfg.get("riga_presentazione"):
            basso = c.scrivi(cv, self.cfg["riga_presentazione"], self.st("r", 9.5, 12.5, fontName="Cormorant-Corsivo",
                             textColor=self.g.accento), x, basso + 12 * mm * K, largo)
        if self.cfg.get("orari"):
            c.scrivi(cv, self.cfg["orari"], self.st("o", 9.5, 12.5, textColor=self.g.grigio), x,
                     self.f["basso"] + 22 * mm * K, largo)
        self.piede(cv, n)
        cv.showPage()

    def stili_opera(self, k):
        return dict(
            titolo=self.st("ti", 12.5 * k, 15 * k, fontName="Cormorant-Corsivo"),
            dati=self.st("da", 8 * k, 10.5 * k, textColor=self.g.grigio),
            dida=self.st("di", 9.6 * k, 12.8 * k, alignment=TA_JUSTIFY),
        )

    def testo_opera(self, cv, o, s, x, y, largo, k, disegna=True):
        y0 = y
        f = c.scrivi if disegna else (lambda cv_, t, st, xx, yy, ll: yy - c.misura(t, st, ll))
        y = f(cv, o["titolo"], s["titolo"], x, y, largo)
        if sala.dati_opera(o):
            y = f(cv, sala.dati_opera(o), s["dati"], x, y, largo)
        y -= 2 * mm * k * self.K
        if disegna:
            self.g.filetto(cv, x, y, 9 * mm * self.K, 0.6)
        y -= 3 * mm * k * self.K
        y = f(cv, o["didascalia"]["it"], s["dida"], x, y, largo)
        return y0 - y

    def testata(self, cv, scheda, x, largo, k, disegna=True):
        nome = self.st("n", 24 * k, 27 * k, fontName="Cormorant-Forte")
        sotto = self.st("st", 12 * k, 15 * k, fontName="Cormorant-Corsivo", textColor=self.g.accento)
        testo = self.st("tx", 11 * k, 15 * k, alignment=TA_JUSTIFY)
        f = c.scrivi if disegna else (lambda cv_, t, s, xx, yy, ll: yy - c.misura(t, s, ll))
        y = f(cv, scheda["nome"], nome, x, self.cima, largo)
        if scheda.get("sottotitolo"):                  # non la città: solo il nome vero, per E.B.Art
            y = f(cv, scheda["sottotitolo"], sotto, x, y - 1, largo)
        y -= 4 * mm * k * self.K
        if disegna:
            self.g.filetto(cv, x, y, 20 * mm * self.K, 1)
        y -= 6 * mm * k * self.K
        if scheda.get("presentazione", {}).get("it"):
            y = f(cv, scheda["presentazione"]["it"], testo, x, y, largo)
        return y - 7 * mm * k * self.K

    def testata_seguito(self, cv, scheda, x, largo, disegna=True):
        st = self.st("ns", 12, 15, fontName="Cormorant-Corsivo", textColor=self.g.accento)
        y = c.scrivi(cv, scheda["nome"], st, x, self.cima, largo) if disegna \
            else self.cima - c.misura(scheda["nome"], st, largo)
        y -= 2.5 * mm * self.K
        if disegna:
            self.g.filetto(cv, x, y, 20 * mm * self.K, 0.6)
        return y - 7 * mm * self.K

    def pagina_opere(self, cv, scheda, lista, n, prima):
        """Le opere in righe da due, ognuna con la sua foto sopra. Le foto
        crescono finché la pagina è piena; il carattere cala solo se
        altrimenti resterebbero troppo piccole."""
        self.carta(cv, n)
        x0, largo_pag = self.x(n)
        giunto = 8 * mm * self.K
        file = [self.cartella / scheda["_cartella"] / f"{c.nome_opera(o)}.jpg" for o in lista]
        colonne = 1 if len(lista) == 1 else 2
        col = largo_pag if colonne == 1 else (largo_pag - giunto) / 2
        righe = [list(range(i, min(i + colonne, len(lista)))) for i in range(0, len(lista), colonne)]
        passo, stacco = 7 * mm * self.K, 3.5 * mm * self.K
        basso = self.fondo_testo

        for k in [1 - 0.025 * i for i in range(16)]:
            s = self.stili_opera(k)
            y = self.testata(cv, scheda, x0, largo_pag, k, False) if prima \
                else self.testata_seguito(cv, scheda, x0, largo_pag, False)
            testi = [max(self.testo_opera(cv, lista[i], s, 0, 0, col, k, False) for i in r) for r in righe]
            spazio = y - basso - sum(testi) - (stacco + passo) * len(righe) + passo
            if spazio / len(righe) >= 45 * mm * self.K:
                break

        y = self.testata(cv, scheda, x0, largo_pag, k) if prima else self.testata_seguito(cv, scheda, x0, largo_pag)
        # una sola opera: la foto non occupa più di metà della larghezza in più
        massimo = col if colonne == 2 else col * 0.85
        voluti = [max(massimo * self.proporzione(file[i]) for i in r) for r in righe]
        scala = min(1, spazio / sum(voluti))
        alti = [v * scala for v in voluti]
        extra = max(0, spazio - sum(alti)) / (len(righe) + 1)
        y -= extra
        for r, t, af in zip(righe, testi, alti):
            for j, i in enumerate(r):
                xx = x0 + j * (col + giunto)
                self.foto(cv, file[i], xx, y, col, af)
                self.testo_opera(cv, lista[i], s, xx, y - af - stacco, col, k)
            y -= af + stacco + t + passo + extra
        self.piede(cv, n)
        cv.showPage()

    def pagina_evento(self, cv, n):
        """La locandina dell'evento che contiene la mostra, entro i margini,
        con la sua riga sotto."""
        f = sala.FOTO / Path(self.cfg["grafica"]["locandina"]).parent / "locandina-evento.jpg"
        self.carta(cv, n)
        x, largo = self.x(n)
        st = self.st("ev", 10.5, 14, fontName="Cormorant-Corsivo", textColor=self.g.accento, alignment=TA_CENTER)
        riga = self.cfg.get("riga_presentazione", "")
        h_riga = c.misura(riga, st, largo) if riga else 0
        y_alto = self.cima
        alto = y_alto - self.fondo_testo - h_riga - 6 * mm * self.K
        self.foto(cv, f, x, y_alto, largo, alto)
        if riga:
            c.scrivi(cv, riga, st, x, self.fondo_testo + h_riga, largo)
        self.piede(cv, n)
        cv.showPage()

    def galleria(self, cv, gal, n, disegna=True, k=1.0):
        """Chi siamo: testo, i quattro pilastri, la frase di casa. Il corpo
        si adatta finché sta nella pagina."""
        x, largo = self.x(n)
        if disegna:
            for k in [1.15 - 0.02 * i for i in range(40)]:
                if self.galleria(None, gal, n, False, k) >= self.fondo_testo:
                    break
            self.carta(cv, n)
        f = c.scrivi if disegna else (lambda cv_, t, s, xx, yy, ll: yy - c.misura(t, s, ll))
        y = self.etichetta(cv, "La galleria", x, self.cima) if disegna else self.cima - 8.5 * self.K * 1.5
        y = f(cv, gal["titolo"], self.st("t", 20 * k, 23 * k, fontName="Cormorant-Forte"), x, y - 2 * mm, largo)
        y = f(cv, gal["sottotitolo"], self.st("s", 11.5 * k, 14.5 * k, fontName="Cormorant-Corsivo",
              textColor=self.g.accento), x, y, largo)
        y -= 4 * mm * k
        if disegna:
            self.g.filetto(cv, x, y, 20 * mm * self.K, 1)
        y -= 5 * mm * k
        testo = self.st("tx", 10.5 * k, 14.5 * k, alignment=TA_JUSTIFY)
        for p in gal["testo"]:
            y = f(cv, p, testo, x, y, largo) - 3 * mm * k
        tit = self.st("pt", 12 * k, 15 * k, fontName="Cormorant-Corsivo")
        des = self.st("pd", 9.8 * k, 13 * k, textColor=self.g.grigio)
        oro = self.g.oro.hexval()[2:]
        y -= 2 * mm * k
        for i, (t, d) in enumerate(gal["pilastri"]):
            y = f(cv, f'<font color="#{oro}">{ROMANI[i]}</font>  {t}', tit, x, y, largo)
            y = f(cv, d, des, x, y, largo) - 2.5 * mm * k
        y -= 4 * mm * k
        y = f(cv, f"«{gal['chiusura']}»", self.st("ch", 13.5 * k, 17 * k, fontName="Cormorant-Corsivo",
              textColor=self.g.oro, alignment=TA_CENTER), x, y, largo)
        if disegna:
            self.piede(cv, n)
            cv.showPage()
        return y

    def elenco(self, cv, schede, n, disegna=True, k=1.0):
        """Le opere in mostra, artista per artista, su due colonne: titolo e
        tecnica. Il corpo si adatta finché l'elenco sta nella pagina."""
        x0, largo = self.x(n)
        if disegna:
            for k in [1.1 - 0.02 * i for i in range(40)]:
                if self.elenco(None, schede, n, False, k):
                    break
            self.carta(cv, n)
        giunto = 7 * mm * self.K
        col = (largo - giunto) / 2
        nome = self.st("en", 10.5 * k, 13 * k, fontName="Cormorant-Corsivo", textColor=self.g.accento)
        opera = self.st("eo", 8.6 * k, 10.6 * k)
        grigio = self.g.grigio.hexval()[2:]
        cima = (self.etichetta(cv, "Le opere in mostra", x0, self.cima) if disegna
                else self.cima - 8.5 * self.K * 1.5) - 3 * mm * self.K
        y, colonna = cima, 0
        for s in schede:
            righe = [(s["nome"], nome)]
            for o in s["opere"]:
                if o.get("didascalia", {}).get("it"):
                    t = o["titolo"] + (f' <font color="#{grigio}">· {o["tecnica"]}</font>' if o.get("tecnica") else "")
                    righe.append((t, opera))
            alto = sum(c.misura(t, st, col) for t, st in righe) + 2.5 * mm * k
            if y - alto < self.fondo_testo:
                colonna += 1
                y = cima
                if colonna == 2:
                    return False
            if disegna:
                xx = x0 + colonna * (col + giunto)
                yy = y
                for t, st in righe:
                    yy = c.scrivi(cv, t, st, xx, yy, col)
            y -= alto
        if disegna:
            self.piede(cv, n)
            cv.showPage()
        return True

    def note(self, cv, n):
        self.carta(cv, n)
        x, largo = self.x(n)
        y = self.etichetta(cv, "Note", x, self.cima) - 8 * mm * self.K
        cv.setStrokeColor(self.g.grigio)
        cv.setLineWidth(0.25)
        while y > self.fondo_testo + 4 * mm:
            cv.line(x, y, x + largo, y)
            y -= 9 * mm * self.K
        self.piede(cv, n)
        cv.showPage()

    def retro(self, cv, gal):
        W, H, K = self.W, self.H, self.K
        cv.setFillColor(NERO)
        cv.rect(0, 0, W, H, stroke=0, fill=1)
        larga = 60 * mm * K
        top = H * 0.64
        c.logo(cv, (W - larga) / 2, top, larga)
        y = top - larga * 616 / 888 - 9 * mm * K
        m = 20 * mm * K
        carta = HexColor("#F2E5D5")
        y = c.scrivi(cv, gal["titolo"], self.st("r1", 14, 18, fontName="Cormorant-Forte", alignment=TA_CENTER,
                     textColor=carta), m, y, W - 2 * m) - 2 * mm
        for riga in gal["contatti"]:
            y = c.scrivi(cv, riga, self.st("r2", 10, 14, alignment=TA_CENTER, textColor=carta), m, y, W - 2 * m)
        y -= 7 * mm * K
        self.g.filetto(cv, W / 2 - 10 * mm * K, y, 20 * mm * K, 0.8)
        y -= 7 * mm * K
        c.scrivi(cv, f"«{gal['chiusura']}»", self.st("r3", 12, 15, fontName="Cormorant-Corsivo",
                 alignment=TA_CENTER, textColor=self.g.oro), m, y, W - 2 * m)
        c.scrivi(cv, f"{self.cfg['titolo']}  ·  {self.cfg['sottotitolo']}",
                 self.st("r4", 8, 11, alignment=TA_CENTER, textColor=HexColor("#8A8378")), m, m, W - 2 * m)
        cv.showPage()

    # ------------------------------------------------------------------ il libro

    def gruppi(self, scheda):
        lista = [o for o in scheda["opere"] if o.get("didascalia", {}).get("it")]
        p, q = self.f["prima"], self.f["poi"]
        return [lista[:p]] + [lista[i:i + q] for i in range(p, len(lista), q)]

    def componi(self, cv, schede, gal):
        p_testo = self.scorri(None, self.cfg["testo"], 1.0, 3, False)
        p_artisti = sum(len(self.gruppi(s)) for s in schede)
        evento = (sala.FOTO / Path(self.cfg["grafica"]["locandina"]).parent / "locandina-evento.jpg").is_file()
        fisse = 1 + 1 + p_testo + p_artisti + 1 + 1               # copertina, frontespizio, galleria, retro
        manca = (-fisse) % 4
        p_evento = 1 if evento and manca else 0
        manca -= p_evento
        p_elenco = 1 if manca else 0                               # poi l'elenco delle opere
        manca -= p_elenco
        p_note = min(manca, 1)                                     # poi una pagina per le note
        manca -= p_note
        p_testo += manca                                           # solo in ultimo il testo si allarga
        k = self.adatta(p_testo)

        self.copertina(cv)
        self.frontespizio(cv, [s["nome"] for s in schede])
        n = 3
        usate = self.scorri(cv, self.cfg["testo"], k, n, True)
        n += usate
        for _ in range(p_testo - usate):       # non dovrebbe servire: il corpo è scelto perché il testo le riempia
            self.note(cv, n)
            n += 1
        for s in schede:
            for i, gruppo in enumerate(self.gruppi(s)):
                self.pagina_opere(cv, s, gruppo, n, i == 0)
                n += 1
        if p_elenco:
            self.elenco(cv, schede, n)
            n += 1
        if p_evento:
            self.pagina_evento(cv, n)
            n += 1
        self.galleria(cv, gal, n)
        n += 1
        for _ in range(p_note):
            self.note(cv, n)
            n += 1
        self.retro(cv, gal)
        if n % 4:
            print(f"   ⚠ {n} pagine: non è un multiplo di 4")
        print(f"   testo della mostra: {p_testo} pagine, corpo {11 * k * self.K:.1f} pt")
        return n


def imponi(sorgente: Path, uscita: Path, pagine: int, W, H) -> None:
    """Due pagine per facciata, nell'ordine della piegatura: con 32 pagine il
    primo foglio porta 32|1 davanti e 2|31 dietro."""
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(str(sorgente))
    nuovo = pdfium.PdfDocument.new()
    for f in range(pagine // 4):
        for sinistra, destra in ((pagine - 2 * f, 1 + 2 * f), (2 + 2 * f, pagine - 1 - 2 * f)):
            foglio = nuovo.new_page(2 * W, H)
            for lato, numero in ((0, sinistra), (1, destra)):
                oggetto = doc.page_as_xobject(numero - 1, nuovo).as_pageobject()
                oggetto.transform(pdfium.PdfMatrix().translate(lato * W, 0))
                foglio.insert_obj(oggetto)
            foglio.gen_content()
    nuovo.save(str(uscita))


def main() -> None:
    argomenti = [a for a in sys.argv[1:] if not a.startswith("--")]
    mostra = argomenti[0] if argomenti else "donne-femminile-plurale"
    formato = "A5" if "--a5" in sys.argv else "A4"
    cfg = json.loads((MOSTRE / f"{mostra}.json").read_text(encoding="utf-8"))
    gal = json.loads(GALLERIA.read_text(encoding="utf-8"))
    schede = []
    for nome in cfg["ordine"]:
        f = c.ARTISTI / nome / "scheda.json"
        if not f.exists():
            print(f"   · {nome}: scheda non ancora scritta")
            continue
        s = c.per_mostra(json.loads(f.read_text(encoding="utf-8")), mostra)
        s["_cartella"] = nome
        schede.append(s)
    libro = Libro(cfg, formato, sala.FOTO / mostra)
    file = CATALOGO / f"{mostra}-libro-{formato}.pdf"
    cv = Canvas(str(file), pagesize=(libro.W, libro.H))
    cv.setTitle(f"{cfg['titolo']} — catalogo")
    cv.setAuthor("BE Art Gallery & Creative Lab")
    pagine = libro.componi(cv, schede, gal)
    cv.save()
    stampa = CATALOGO / f"{mostra}-libro-stampa-{libro.f['stampa']}.pdf"
    imponi(file, stampa, pagine, libro.W, libro.H)
    print(f"\n{cfg['titolo']}: catalogo {formato}, {pagine} pagine, "
          f"{pagine // 4} fogli {libro.f['stampa']} fronte-retro")
    for f in (file, stampa):
        print(f"   {f.relative_to(c.RADICE)}")
    print()


if __name__ == "__main__":
    main()
