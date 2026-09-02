#!/usr/bin/env python3
"""
Le impaginazioni di post, caroselli e storie.

Non sono decorazioni intercambiabili: nascono dal linguaggio grafico già
definito per la galleria — il filetto oro che accompagna i titoli come la
cornice di un quadro, il cartellino da mostra, il ritaglio ad arco che richiama
gli archi in mattoni, i numeri romani da segnaletica museale.

Si sceglie un'impaginazione per contenuto, non per pagina: dentro un carosello
la coerenza tiene, la varietà sta fra un contenuto e il successivo.
"""

from pathlib import Path

from PIL import Image, ImageDraw

import onde

from grafica import applica_logo, componi, fondo_pieno, ritaglia

# Fondi e inchiostri delle impaginazioni su fondo pieno
AVORIO = "#F2EAD9"      # la carta: la stessa del fondo a strati
NERO_CALDO = "#14110F"
INCHIOSTRO = "#241F1C"
ORO_SCURO = "#9A7620"   # l'oro leggibile su fondo chiaro

ROMANI = ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
          "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX"]


def _su_fondo_chiaro(cfg: dict) -> dict:
    """Gli stessi testi, con i colori che reggono sull'avorio."""
    chiaro = dict(cfg)
    chiaro.update({"colore_testo": INCHIOSTRO, "colore_accento": ORO_SCURO,
                   "velatura": False})
    return chiaro


def _striscia_testo(pagina: Image.Image, da: int, testi: list[dict],
                    cfg_testo: dict) -> None:
    """
    Scrive i testi nella fascia sotto l'immagine, non sopra di essa.

    Lasciare che il testo si posizioni "in basso" sulla pagina intera lo faceva
    ricadere sull'immagine quando questa era alta: qui la zona di scrittura è
    esplicita e la sovrapposizione non può accadere.
    """
    if not testi:
        return
    striscia = pagina.crop((0, da, pagina.width, pagina.height))
    striscia = componi(striscia, [dict(t, posizione="centro") for t in testi],
                       {**cfg_testo, "blocco_massimo": 0.7})
    pagina.paste(striscia, (0, da))


def filetto(tela: Image.Image, y: int, larghezza_filetto: float, colore: str) -> None:
    """La linea d'oro sotto o sopra un titolo: richiama la cornice di un quadro."""
    penna = ImageDraw.Draw(tela)
    meta = int(tela.width * larghezza_filetto / 2)
    centro = tela.width // 2
    spessore = max(int(tela.width * 0.0022), 2)
    penna.rectangle([centro - meta, y, centro + meta, y + spessore], fill=colore)


def _numero(tela: Image.Image, indice: int, cfg: dict, colore: str) -> None:
    """Il numero romano in alto a destra, come il cartellino di sala."""
    if not indice or indice >= len(ROMANI):
        return
    from grafica import _carica_font
    font = _carica_font(cfg["font_titolo"], int(tela.width * 0.038), "font_titolo")
    penna = ImageDraw.Draw(tela)
    testo = ROMANI[indice]
    x = tela.width - int(tela.width * 0.075) - font.getlength(testo)
    penna.text((x, int(tela.width * 0.062)), testo, font=font, fill=colore)


# ----------------------------------------------------------------------------
# Le impaginazioni
# ----------------------------------------------------------------------------

def pieno(foto, testi: list[dict], cfg: dict, misura, numero: int = 0) -> Image.Image:
    """Foto a tutto campo, testo in basso sulla velatura. La più diretta."""
    larghezza, altezza = misura
    pagina = applica_logo(_immagine(foto, larghezza, altezza), cfg)
    _numero(pagina, numero, cfg, cfg["colore_accento"])
    return componi(pagina, testi, cfg)


def cartellino(foto, testi: list[dict], cfg: dict, misura, numero: int = 0) -> Image.Image:
    """
    Il cartellino da mostra: la foto sopra, sotto una fascia avorio con il
    filetto oro e il testo in inchiostro. Il contrario del testo sulla foto —
    qui l'immagine resta intatta e la parola ha il suo spazio.
    """
    if not testi:
        # Una fascia avorio senza niente dentro sembra un errore di stampa:
        # sulle pagine senza testo si lascia parlare la foto
        return pieno(foto, testi, cfg, misura, numero)

    larghezza, altezza = misura
    fascia = int(altezza * (0.30 if altezza / larghezza < 1.4 else 0.24))
    alta = altezza - fascia

    pagina = Image.new("RGB", (larghezza, altezza), AVORIO)
    pagina.paste(applica_logo(_immagine(foto, larghezza, alta), cfg), (0, 0))

    banda = Image.new("RGB", (larghezza, fascia), AVORIO)
    filetto(banda, int(fascia * 0.16), 0.14, ORO_SCURO)
    # La fascia è tutta a disposizione del testo: qui il tetto del 28%, pensato
    # per non coprire una foto, non ha senso
    banda = componi(banda, [dict(t, posizione="centro") for t in testi],
                    {**_su_fondo_chiaro(cfg), "blocco_massimo": 0.75})
    pagina.paste(banda, (0, alta))
    _numero(pagina, numero, cfg, cfg["colore_accento"])
    return pagina


def cornice(foto, testi: list[dict], cfg: dict, misura, numero: int = 0) -> Image.Image:
    """
    La stampa incorniciata: fondo nero caldo, immagine rientrata, filetto e
    testo sotto. Il logo è disegnato per il nero, e qui sta a casa sua.
    """
    larghezza, altezza = misura
    margine = int(larghezza * 0.085)
    largo = larghezza - 2 * margine
    alto = int(altezza * 0.50)
    cima = int(altezza * 0.095)

    pagina = fondo_pieno(larghezza, altezza, NERO_CALDO)
    pagina.paste(_immagine(foto, largo, alto), (margine, cima))
    riga = cima + alto + int(altezza * 0.042)
    filetto(pagina, riga, 0.14, cfg["colore_accento"])

    pagina = applica_logo(pagina, {**cfg, "logo_larghezza": 0.20,
                                   "logo_velatura": False})
    _numero(pagina, numero, cfg, cfg["colore_accento"])
    _striscia_testo(pagina, riga + int(altezza * 0.03), testi,
                    {**cfg, "velatura": False})
    return pagina


def arco(foto, testi: list[dict], cfg: dict, misura, numero: int = 0) -> Image.Image:
    """
    Il ritaglio ad arco su fondo avorio: richiama gli archi in mattoni della
    galleria. Il logo va dentro l'immagine, dove la velatura lo tiene pulito.
    """
    larghezza, altezza = misura
    margine = int(larghezza * 0.095)
    largo = larghezza - 2 * margine
    alto = int(altezza * 0.47)
    cima = int(altezza * 0.135)

    immagine = _immagine(foto, largo, alto)

    maschera = Image.new("L", (largo, alto), 0)
    penna = ImageDraw.Draw(maschera)
    penna.pieslice([0, 0, largo, largo], 180, 360, fill=255)
    penna.rectangle([0, largo // 2, largo, alto], fill=255)

    pagina = Image.new("RGB", (larghezza, altezza), AVORIO)
    pagina.paste(immagine, (margine, cima), maschera)
    riga = cima + alto + int(altezza * 0.042)
    filetto(pagina, riga, 0.14, ORO_SCURO)

    # Il marchio sta sull'avorio, non dentro l'arco: la curva lo taglierebbe.
    # Sul chiaro serve la versione con il proprio fondo nero, che sull'avorio
    # diventa una piccola targa invece di una scritta che si perde
    pagina = applica_logo(pagina, {**cfg, "logo_larghezza": 0.20,
                                   "logo_variante": "nero",
                                   "logo_velatura": False})
    _numero(pagina, numero, cfg, ORO_SCURO)
    _striscia_testo(pagina, riga + int(altezza * 0.03), testi,
                    _su_fondo_chiaro(cfg))
    return pagina


IMPAGINAZIONI = {
    "pieno": pieno,
    "cartellino": cartellino,
    "cornice": cornice,
    "arco": arco,
}


def _immagine(foto, larghezza: int, altezza: int) -> Image.Image:
    """La foto ritagliata alla misura, o un fondo pieno se non ce n'è una."""
    if foto is None:
        return fondo_pieno(larghezza, altezza, NERO_CALDO)
    if isinstance(foto, Image.Image):
        return foto.resize((larghezza, altezza), Image.LANCZOS)
    return ritaglia(Path(foto), larghezza, altezza)


def pagina(nome: str, foto, testi: list[dict], cfg: dict, misura,
           numero: int = 0) -> Image.Image:
    if nome not in IMPAGINAZIONI:
        raise SystemExit(
            f"Impaginazione '{nome}' sconosciuta. Disponibili: {', '.join(IMPAGINAZIONI)}"
        )
    return IMPAGINAZIONI[nome](foto, testi, cfg, misura, numero)


# ----------------------------------------------------------------------------
# Il manifesto: fondo a strati, per i contenuti senza foto
# ----------------------------------------------------------------------------

RUOLI = {
    # ruolo:        (font,          corpo,  colore,        interlinea, spazio dopo)
    "etichetta":    ("font_testo",  0.030, onde.ORO,        1.5,  0.034),
    "titolo":       ("font_titolo", 0.115, onde.INCHIOSTRO, 0.98, 0.020),
    "sottotitolo":  ("font_corsivo", 0.046, onde.ORO,       1.25, 0.018),
    "data":         ("font_serif",  0.055, onde.INCHIOSTRO, 1.2,  0.026),
    "corpo":        ("font_testo",  0.035, "#3A322C",       1.55, 0.020),
    "evidenza":     ("font_titolo", 0.070, onde.INCHIOSTRO, 1.1,  0.020),
}


def _riga_oro(tela: Image.Image, y: int, larghezza_riga: float) -> None:
    """Il filetto con il piccolo rombo al centro, come sulla locandina."""
    penna = ImageDraw.Draw(tela)
    meta = int(tela.width * larghezza_riga / 2)
    centro = tela.width // 2
    spessore = max(int(tela.width * 0.0015), 1)
    penna.rectangle([centro - meta, y, centro - 18, y + spessore], fill=onde.ORO)
    penna.rectangle([centro + 18, y, centro + meta, y + spessore], fill=onde.ORO)
    lato = max(int(tela.width * 0.007), 4)
    penna.polygon([(centro, y - lato + spessore // 2), (centro + lato, y + spessore // 2),
                   (centro, y + lato + spessore // 2), (centro - lato, y + spessore // 2)],
                  fill=onde.ORO)


def _misura_blocco(righe: list[dict], larghezza: int, cfg: dict) -> list[dict]:
    """Prepara ogni riga con il suo font e la sua altezza, andando a capo."""
    from grafica import _carica_font, _manda_a_capo
    margine = int(larghezza * 0.10)
    utile = larghezza - 2 * margine
    preparate = []
    for voce in righe:
        if voce.get("ruolo") == "filetto":
            preparate.append({"filetto": True, "altezza": int(larghezza * 0.075)})
            continue
        ruolo = voce.get("ruolo", "corpo")
        nome, quota, colore, interlinea, dopo = RUOLI[ruolo]
        font = _carica_font(cfg[nome], int(larghezza * quota), nome)
        for pezzo in _manda_a_capo(voce["testo"], font, utile):
            preparate.append({"testo": pezzo, "font": font, "colore": colore,
                              "altezza": int(font.size * interlinea)})
        preparate[-1]["altezza"] += int(larghezza * dopo)
    return preparate


def manifesto(foto, testi: list[dict], cfg: dict, misura, numero: int = 0,
              orizzonte: float = 0.46, seme: int = 0) -> Image.Image:
    """
    Una pagina senza fotografia: gli strati di colore sotto, la carta libera
    sopra per il testo. È il linguaggio della locandina, e serve agli annunci
    dove non c'è ancora niente da fotografare.
    """
    larghezza, altezza = misura
    pagina = onde.fondo(larghezza, altezza, orizzonte=orizzonte, seme=seme)

    preparate = _misura_blocco(testi, larghezza, cfg)
    blocco = sum(v["altezza"] for v in preparate)
    y = int(altezza * orizzonte * 0.5 - blocco / 2) + int(altezza * 0.03)
    y = max(y, int(altezza * 0.09))

    penna = ImageDraw.Draw(pagina)
    for voce in preparate:
        if voce.get("filetto"):
            _riga_oro(pagina, y + voce["altezza"] // 2, 0.30)
        else:
            x = (larghezza - voce["font"].getlength(voce["testo"])) / 2
            penna.text((x, y), voce["testo"], font=voce["font"], fill=voce["colore"])
        y += voce["altezza"]

    return _firma(pagina, cfg)


def _firma(pagina: Image.Image, cfg: dict) -> Image.Image:
    """Il nome della galleria in fondo, e il marchio in alto a sinistra."""
    from grafica import _carica_font
    penna = ImageDraw.Draw(pagina)
    font = _carica_font(cfg["font_serif"], int(pagina.width * 0.032), "font_serif")
    testo = "BE ART GALLERY  ·  PISTOIA"
    spaziatura = pagina.width * 0.004
    larghezza_testo = sum(font.getlength(c) + spaziatura for c in testo) - spaziatura
    x = (pagina.width - larghezza_testo) / 2
    y = pagina.height - int(pagina.height * 0.058)
    for carattere in testo:
        penna.text((x, y), carattere, font=font, fill=onde.ORO)
        x += font.getlength(carattere) + spaziatura
    return applica_logo(pagina, {**cfg, "logo_larghezza": 0.155,
                                 "logo_variante": "nero",
                                 "logo_velatura": False})


IMPAGINAZIONI["manifesto"] = manifesto
