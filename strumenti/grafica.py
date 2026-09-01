#!/usr/bin/env python3
"""
Pezzi comuni a tutti i contenuti di BE Art Gallery.

Qui stanno il ritaglio delle foto e la composizione dei testi: li usano sia il
generatore di reel sia quello di post, caroselli e storie, così un contenuto
prodotto oggi e uno prodotto fra un mese hanno la stessa faccia.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

LOGO = Path(__file__).resolve().parent / "marchio" / "logo.png"

# ----------------------------------------------------------------------------
# Impostazioni di marca — valgono per ogni formato
# ----------------------------------------------------------------------------

MARCHIO = {
    "logo": True,               # il marchio sta su ogni contenuto
    "logo_larghezza": 0.24,     # quota della larghezza dell'immagine
    "logo_opacita": 0.92,
    "colore_testo": "#FFFFFF",
    "colore_accento": "#C9A227",   # l'oro antico del logo
    "font_titolo": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "font_testo": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
}

# Su Windows i font di sistema stanno altrove: si cercano lì se i primi mancano
FONT_ALTERNATIVI = {
    "font_titolo": ["C:/Windows/Fonts/georgiab.ttf", "C:/Windows/Fonts/timesbd.ttf",
                    "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"],
    "font_testo": ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
                   "/System/Library/Fonts/Supplemental/Arial.ttf"],
}

FORMATI = {
    "post":      (1080, 1350),   # verticale 4:5, occupa più feed del quadrato
    "carosello": (1080, 1350),
    "storia":    (1080, 1920),
    "reel":      (1080, 1920),
}

ESTENSIONI = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
ESTENSIONI_VIDEO = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"}


def e_video(percorso: Path) -> bool:
    return percorso.suffix.lower() in ESTENSIONI_VIDEO


def impostazioni(extra: dict | None = None) -> dict:
    cfg = dict(MARCHIO)
    if extra:
        cfg.update(extra)
    return cfg


def raccogli_foto(cartella: Path, ordine: list[str] | None = None,
                  includi_video: bool = False) -> list[Path]:
    """
    I file della cartella, nell'ordine indicato o in ordine alfabetico.

    I video entrano solo dove servono, cioè nei reel: un post o un carosello
    li ignora anche se stanno nella stessa cartella.
    """
    if ordine:
        media = [cartella / nome for nome in ordine]
        mancanti = [f.name for f in media if not f.exists()]
        if mancanti:
            raise FileNotFoundError(
                "Questi file non sono in " + str(cartella) + ":\n  " + "\n  ".join(mancanti)
            )
        return media

    ammesse = ESTENSIONI | (ESTENSIONI_VIDEO if includi_video else set())
    media = sorted(f for f in cartella.iterdir() if f.suffix.lower() in ammesse)
    if not media:
        raise FileNotFoundError(f"Nessun file utilizzabile in {cartella}")
    return media


# ----------------------------------------------------------------------------
# Immagini
# ----------------------------------------------------------------------------

def ritaglia(foto: Path, larghezza: int, altezza: int) -> Image.Image:
    """
    Porta la foto alla misura richiesta riempiendola tutta, senza deformarla:
    ridimensiona quanto basta a coprire e taglia l'eccedenza dal centro.
    """
    with Image.open(foto) as immagine:
        immagine = ImageOps.exif_transpose(immagine).convert("RGB")
        scala = max(larghezza / immagine.width, altezza / immagine.height)
        intermedia = immagine.resize(
            (max(int(immagine.width * scala + 0.5), larghezza),
             max(int(immagine.height * scala + 0.5), altezza)),
            Image.LANCZOS,
        )

    sinistra = (intermedia.width - larghezza) // 2
    alto = (intermedia.height - altezza) // 2
    return intermedia.crop((sinistra, alto, sinistra + larghezza, alto + altezza))


def fondo_pieno(larghezza: int, altezza: int, colore: str = "#1A1613") -> Image.Image:
    return Image.new("RGB", (larghezza, altezza), colore)


# ----------------------------------------------------------------------------
# Testi
# ----------------------------------------------------------------------------

def _carica_font(percorso: str, dimensione: int, ruolo: str = "font_testo"):
    for candidato in [percorso, *FONT_ALTERNATIVI.get(ruolo, [])]:
        try:
            return ImageFont.truetype(candidato, dimensione)
        except OSError:
            continue
    return ImageFont.load_default(dimensione)


def _manda_a_capo(testo: str, font, larghezza_utile: float) -> list[str]:
    """Va a capo fra le parole, misurando ogni riga con il font vero."""
    parole = testo.split()
    if not parole:
        return [""]
    righe, corrente = [], parole[0]
    for parola in parole[1:]:
        tentativo = f"{corrente} {parola}"
        if font.getlength(tentativo) <= larghezza_utile:
            corrente = tentativo
        else:
            righe.append(corrente)
            corrente = parola
    righe.append(corrente)
    return righe


def _adatta_font(testo: str, dimensione: int, percorso: str, ruolo: str,
                 larghezza_utile: float):
    """Rimpicciolisce il font finché la parola più lunga ci sta in larghezza."""
    parole = testo.split() or [testo]
    while dimensione > 22:
        candidato = _carica_font(percorso, dimensione, ruolo)
        if max(candidato.getlength(p) for p in parole) <= larghezza_utile:
            return candidato
        dimensione -= 4
    return _carica_font(percorso, dimensione, ruolo)


def strato_testo(righe: list[str], larghezza: int, altezza: int, cfg: dict,
                 posizione: str = "basso", enfasi: bool = False,
                 corpo: int | None = None) -> Image.Image:
    """
    Compone i testi su uno strato trasparente della misura richiesta.

    Sotto al testo passa una velatura sfumata: senza, il bianco sparisce sulle
    foto chiare e il contenuto diventa illeggibile proprio sulle immagini
    migliori.
    """
    tela = Image.new("RGBA", (larghezza, altezza), (0, 0, 0, 0))

    base = corpo or int(larghezza * (0.076 if enfasi else 0.059))
    margine = int(larghezza * 0.09)
    utile = larghezza - 2 * margine

    spezzate: list[tuple[str, object, int]] = []
    for indice, riga in enumerate(righe):
        principale = indice == 0
        ruolo = "font_titolo" if principale else "font_testo"
        font = _adatta_font(riga, base if principale else int(base * 0.62),
                            cfg[ruolo], ruolo, utile)
        for pezzo in _manda_a_capo(riga, font, utile):
            spezzate.append((pezzo, font, indice))

    interlinea = 1.3
    blocco = sum(int(f.size * interlinea) for _, f, _ in spezzate)

    # Nelle storie i bordi sono coperti dall'interfaccia di Instagram
    respiro = 0.18 if altezza > larghezza * 1.6 else 0.13
    if posizione == "basso":
        partenza = altezza - int(altezza * respiro) - blocco
    elif posizione == "alto":
        partenza = int(altezza * respiro)
    else:
        partenza = (altezza - blocco) // 2

    velatura = Image.new("RGBA", (larghezza, altezza), (0, 0, 0, 0))
    pennello = ImageDraw.Draw(velatura)
    cima = max(partenza - int(altezza * 0.11), 0)
    fondo = min(partenza + blocco + int(altezza * 0.11), altezza)
    estensione = max(fondo - cima, 1)
    for y in range(cima, fondo):
        avanzamento = (y - cima) / estensione
        if posizione == "basso":
            opacita = int(205 * min(avanzamento * 1.7, 1.0))
        elif posizione == "alto":
            opacita = int(205 * min((1 - avanzamento) * 1.7, 1.0))
        else:
            opacita = int(190 * (1 - abs(avanzamento - 0.5) * 2) ** 0.5)
        pennello.line([(0, y), (larghezza, y)], fill=(0, 0, 0, opacita))
    tela = Image.alpha_composite(tela, velatura)

    penna = ImageDraw.Draw(tela)
    y = partenza
    for testo, font, riga_originale in spezzate:
        colore = cfg["colore_accento"] if (enfasi and riga_originale == 0) else cfg["colore_testo"]
        x = (larghezza - font.getlength(testo)) / 2
        penna.text((x + 2, y + 3), testo, font=font, fill=(0, 0, 0, 130))
        penna.text((x, y), testo, font=font, fill=colore)
        y += int(font.size * interlinea)

    return tela


def componi(sfondo: Image.Image, testi: list[dict], cfg: dict) -> Image.Image:
    """Sovrappone i blocchi di testo allo sfondo e restituisce l'immagine finita."""
    risultato = sfondo.convert("RGBA")
    for testo in testi:
        strato = strato_testo(
            testo["righe"], risultato.width, risultato.height, cfg,
            posizione=testo.get("posizione", "basso"),
            enfasi=testo.get("enfasi", False),
            corpo=testo.get("corpo"),
        )
        risultato = Image.alpha_composite(risultato, strato)
    return risultato.convert("RGB")


# ----------------------------------------------------------------------------
# Marchio
# ----------------------------------------------------------------------------

def strato_logo(larghezza: int, altezza: int, cfg: dict) -> Image.Image | None:
    """
    Il marchio in alto a sinistra, su una velatura appena accennata.

    Il logo è pensato per fondi scuri — ha un'aureola nera attorno al
    monogramma — quindi sulle foto chiare, senza velatura, si sporca. La
    sfumatura in alto lo tiene leggibile su qualunque immagine e non ruba
    spazio ai testi, che stanno in basso.
    """
    if not cfg.get("logo", True) or not LOGO.exists():
        return None

    strato = Image.new("RGBA", (larghezza, altezza), (0, 0, 0, 0))
    pennello = ImageDraw.Draw(strato)
    fascia = int(altezza * 0.17)
    for y in range(fascia):
        pennello.line([(0, y), (larghezza, y)],
                      fill=(0, 0, 0, int(185 * (1 - y / fascia) ** 1.25)))

    with Image.open(LOGO) as marchio:
        marchio = marchio.convert("RGBA")
        largo = int(larghezza * cfg.get("logo_larghezza", 0.30))
        marchio = marchio.resize(
            (largo, max(int(largo * marchio.height / marchio.width), 1)), Image.LANCZOS)

    opacita = cfg.get("logo_opacita", 0.92)
    if opacita < 1:
        marchio.putalpha(marchio.getchannel("A").point(lambda v: int(v * opacita)))

    margine = int(larghezza * 0.05)
    strato.paste(marchio, (margine, margine), marchio)
    return strato


def applica_logo(immagine: Image.Image, cfg: dict) -> Image.Image:
    strato = strato_logo(immagine.width, immagine.height, cfg)
    if strato is None:
        return immagine
    return Image.alpha_composite(immagine.convert("RGBA"), strato).convert("RGB")
