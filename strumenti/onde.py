#!/usr/bin/env python3
"""
Il fondo a strati di BE Art Gallery.

Bande di colore che attraversano la pagina come strati di roccia, separate da
un filo d'oro, su carta avorio. È il linguaggio della locandina de "I Luoghi
dell'Anima", e serve ai contenuti che non hanno una foto da mostrare:
annunci, iscrizioni, scadenze, informazioni pratiche.

Il fondo si genera, non si ritaglia da un file: cambiando `seme` e `orizzonte`
ogni pagina è diversa dalla precedente pur restando della stessa famiglia.
"""

import math
import random

from PIL import Image, ImageColor, ImageDraw, ImageFilter

CARTA = "#F2EAD9"
INCHIOSTRO = "#241F1C"
ORO = "#D6B24C"
ORO_CHIARO = "#E3CB84"

# I colori degli strati, nell'ordine in cui si sovrappongono dall'alto in basso
STRATI = [
    "#E7D9BE",  # crema
    "#D9C39E",  # sabbia
    "#CE8B7A",  # rosa antico
    "#B0604A",  # terracotta
    "#2A2A2D",  # antracite
    "#C97F6B",  # rosa caldo
    "#4E2B44",  # prugna
    "#B0604A",  # terracotta
    "#2A2A2D",  # antracite
]


def _curva(larghezza: int, base: float, ampiezza: float, casuale: random.Random,
           passo: int = 6) -> list[tuple[int, float]]:
    """Una linea ondulata: somma di tre sinusoidi, così non si ripete a occhio."""
    onde = [(casuale.uniform(0.6, 1.4), casuale.uniform(0, math.tau),
             casuale.uniform(0.35, 1.0)) for _ in range(3)]
    punti = []
    for x in range(0, larghezza + passo, passo):
        t = x / larghezza
        y = base
        for frequenza, fase, peso in onde:
            y += ampiezza * peso * math.sin(math.tau * frequenza * t + fase)
        punti.append((x, y))
    return punti


def _foglia_oro(tela: Image.Image, punti, spessore_massimo: float,
                casuale: random.Random) -> None:
    """
    Foglia d'oro lungo il bordo di uno strato.

    Non una toppa piena — quella si leggeva come un blocco col bordo
    frastagliato — ma un bagliore che segue l'onda e sfuma, con sopra un
    pulviscolo di scaglie. Lo spessore resta dentro la striscia visibile della
    banda, altrimenti la banda successiva ne taglia via metà.
    """
    strato = Image.new("RGBA", tela.size, (0, 0, 0, 0))
    penna = ImageDraw.Draw(strato)

    for _ in range(casuale.randint(1, 2)):
        inizio = casuale.randrange(0, max(len(punti) - 40, 1))
        tratto = punti[inizio:inizio + casuale.randint(30, 70)]
        if len(tratto) < 6:
            continue
        fascia = spessore_massimo * casuale.uniform(0.3, 0.55)
        penna.line([(x, y + fascia * 0.45) for x, y in tratto],
                   fill=(214, 178, 76, 150), width=max(int(fascia), 3), joint="curve")
        for _ in range(casuale.randint(30, 70)):
            x, y = casuale.choice(tratto)
            raggio = casuale.uniform(1.0, 3.2)
            scarto = casuale.uniform(0, fascia)
            penna.ellipse([x - raggio, y + scarto - raggio,
                           x + raggio, y + scarto + raggio],
                          fill=(232, 203, 118, casuale.randint(110, 220)))

    tela.paste(Image.alpha_composite(
        tela.convert("RGBA"), strato.filter(ImageFilter.GaussianBlur(3.5))
    ).convert("RGB"), (0, 0))


def _pennellate(tela: Image.Image, punti, spessore: float, colore: str,
                casuale: random.Random) -> None:
    """
    Solchi appena più chiari dentro la campitura, che seguono l'onda.

    Servono a far sembrare la banda materia stesa a mano invece che un
    riempimento uniforme.
    """
    strato = Image.new("RGBA", tela.size, (0, 0, 0, 0))
    penna = ImageDraw.Draw(strato)
    rosso, verde, blu = ImageColor.getrgb(colore)
    for _ in range(casuale.randint(3, 6)):
        scarto = spessore * casuale.uniform(0.15, 0.85)
        chiaro = casuale.random() < 0.5
        delta = 26 if chiaro else -20
        tinta = (max(0, min(255, rosso + delta)), max(0, min(255, verde + delta)),
                 max(0, min(255, blu + delta)), casuale.randint(40, 90))
        penna.line([(x, y + scarto) for x, y in punti], fill=tinta,
                   width=casuale.randint(3, 9), joint="curve")
    strato = strato.filter(ImageFilter.GaussianBlur(3))
    tela.paste(Image.alpha_composite(tela.convert("RGBA"), strato).convert("RGB"), (0, 0))


def _grana(immagine: Image.Image) -> Image.Image:
    """Una grana appena percettibile: senza, le campiture sembrano di plastica."""
    rumore = Image.effect_noise(immagine.size, 14).convert("L")
    rumore = rumore.filter(ImageFilter.GaussianBlur(0.4))
    return Image.blend(immagine, Image.merge("RGB", (rumore, rumore, rumore)), 0.05)


def fondo(larghezza: int, altezza: int, orizzonte: float = 0.46,
          seme: int = 0, quanti: int | None = None,
          foglia: bool = False) -> Image.Image:
    """
    La pagina a strati.

    `orizzonte` è dove cominciano le bande, in quota dell'altezza: più è in
    basso, più carta resta libera per il testo.

    La foglia d'oro resta spenta: generata al computer si legge come una
    barretta invece che come doratura, e un dettaglio che sembra un difetto è
    peggio di un dettaglio assente. Il filo d'oro lungo ogni bordo e la
    pennellata dentro le campiture bastano a dare la materia.
    """
    casuale = random.Random(seme)
    tela = Image.new("RGB", (larghezza, altezza), CARTA)
    penna = ImageDraw.Draw(tela)

    partenza = altezza * orizzonte
    colori = STRATI[:quanti] if quanti else STRATI
    passo = (altezza - partenza) / (len(colori) + 1.2)

    # Prima tutte le bande: ognuna riempie fino in fondo ed è la successiva a
    # coprirla, e da questa sovrapposizione nasce l'effetto degli strati
    curve = []
    for indice, colore in enumerate(colori):
        base = partenza + passo * indice
        punti = _curva(larghezza, base, altezza * casuale.uniform(0.028, 0.055), casuale)
        penna.polygon([*punti, (larghezza, altezza), (0, altezza)], fill=colore)
        curve.append((punti, colore))

    # Poi le rifiniture, dall'alto in basso, ciascuna dentro la striscia che
    # resta visibile della propria banda
    filo = max(int(larghezza * 0.004), 3)
    for indice, (punti, colore) in enumerate(curve):
        visibile = passo if indice < len(curve) - 1 else altezza * 0.06
        _pennellate(tela, punti, visibile, colore, casuale)
        if foglia and casuale.random() < 0.6:
            _foglia_oro(tela, punti, visibile, casuale)
        ImageDraw.Draw(tela).line(punti, fill=ORO, width=filo, joint="curve")

    # Il bordo di schiuma chiara in fondo, come sulla locandina. Tenuto alto e
    # poco mosso: è lì che va la firma della galleria, e su una banda scura non
    # si leggerebbe
    punti = _curva(larghezza, altezza * 0.925, altezza * 0.012, casuale)
    ImageDraw.Draw(tela).polygon([*punti, (larghezza, altezza), (0, altezza)], fill=CARTA)
    ImageDraw.Draw(tela).line(punti, fill=ORO, width=max(filo - 1, 2), joint="curve")

    return _grana(tela)
