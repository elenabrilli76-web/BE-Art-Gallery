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
                   "velatura": False,
                   # Sulla carta si torna al carattere della locandina: il
                   # bastone serve sopra le fotografie, non qui
                   "font_testo": cfg["font_forte"]})
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
    # Sulla fotografia il marchio prende il proprio fondo nero: sopra una
    # parete di sasso la versione trasparente si confonde con il muro
    foto_con_marchio = applica_logo(_immagine(foto, larghezza, alta),
                                    {**cfg, "logo_variante": "nero",
                                     "logo_velatura": False})
    pagina.paste(foto_con_marchio, (0, 0))

    # In fondo alla fascia sta il nome della galleria: il testo si compone
    # sopra quella riga, non sull'intera fascia, o le due cose si toccano
    riga = int(fascia * 0.16)
    scritta = fascia - riga - int(altezza * 0.078)
    banda = Image.new("RGB", (larghezza, scritta), AVORIO)
    # Il tetto del 28%, pensato per non coprire una foto, qui non ha senso:
    # questa fascia esiste apposta per il testo
    banda = componi(banda, [dict(t, posizione="centro") for t in testi],
                    {**_su_fondo_chiaro(cfg), "blocco_massimo": 0.86})
    filetto(pagina, alta + riga, 0.14, ORO_SCURO)
    pagina.paste(banda, (0, alta + riga + int(altezza * 0.014)))
    marchio_scritto(pagina, cfg, corpo=0.026, colore=ORO_SCURO)
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
    # Anche sul nero il testo è quello della locandina: il bastone resta per
    # le scritte sopra le fotografie
    _striscia_testo(pagina, riga + int(altezza * 0.03), testi,
                    {**cfg, "velatura": False, "font_testo": cfg["font_forte"]})
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
           numero: int = 0, **opzioni) -> Image.Image:
    if nome not in IMPAGINAZIONI:
        raise SystemExit(
            f"Impaginazione '{nome}' sconosciuta. Disponibili: {', '.join(IMPAGINAZIONI)}"
        )
    disegna = IMPAGINAZIONI[nome]
    accettate = disegna.__code__.co_varnames[:disegna.__code__.co_argcount]
    ammesse = {k: v for k, v in opzioni.items() if k in accettate}
    return disegna(foto, testi, cfg, misura, numero, **ammesse)


# ----------------------------------------------------------------------------
# Il manifesto: fondo a strati, per i contenuti senza foto
# ----------------------------------------------------------------------------

# Il sistema tipografico è quello delle locandine: un solo carattere, il
# Cormorant Garamond, che cambia peso e taglio invece di cambiare famiglia.
# Sulla copertina de "I Luoghi dell'Anima" non compare un solo bastone: titolo
# tondo, sottotitolo corsivo oro, data tonda, firma tonda spaziata. Qui si
# ripete la stessa scala, così una pagina generata e una locandina stanno
# nello stesso carosello senza che si veda la cucitura.
RUOLI = {
    # ruolo:        (font,          corpo,  colore,        interlinea, spazio dopo, spaziatura)
    "etichetta":    ("font_serif",   0.034, onde.ORO,        1.5,  0.034, 0.16),
    "titolo":       ("font_titolo",  0.118, onde.INCHIOSTRO, 1.02, 0.020, 0.0),
    "sottotitolo":  ("font_corsivo", 0.048, onde.ORO,        1.25, 0.018, 0.0),
    "data":         ("font_serif",   0.058, onde.INCHIOSTRO, 1.2,  0.026, 0.03),
    "corpo":        ("font_forte",   0.042, "#3A322C",       1.42, 0.020, 0.0),
    "evidenza":     ("font_forte",   0.072, onde.INCHIOSTRO, 1.12, 0.020, 0.0),
}


def _scrivi_spaziato(penna, x: float, y: float, testo: str, font,
                     colore, spaziatura: float) -> None:
    """Scrive lettera per lettera quando serve allargare la spaziatura."""
    if not spaziatura:
        penna.text((x, y), testo, font=font, fill=colore)
        return
    for carattere in testo:
        penna.text((x, y), carattere, font=font, fill=colore)
        x += font.getlength(carattere) + spaziatura


def _larghezza_spaziata(testo: str, font, spaziatura: float) -> float:
    if not spaziatura:
        return font.getlength(testo)
    return sum(font.getlength(c) + spaziatura for c in testo) - spaziatura


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
        nome, quota, colore, interlinea, dopo, traccia = RUOLI[ruolo]
        font = _carica_font(cfg[nome], int(larghezza * quota), nome)
        spaziatura = font.size * traccia
        testo = voce["testo"].upper() if ruolo == "etichetta" else voce["testo"]
        for pezzo in _manda_a_capo(testo, font, utile - spaziatura * len(testo)):
            preparate.append({"testo": pezzo, "font": font, "colore": colore,
                              "spaziatura": spaziatura,
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

    preparate = _misura_blocco(testi, larghezza, cfg)
    blocco = sum(v["altezza"] for v in preparate)

    # La carta libera deve bastare al testo: se il blocco è più alto della
    # fascia chiara, l'orizzonte scende invece di lasciare che le ultime righe
    # finiscano sopra gli strati di colore, dove non si leggono più
    cima = int(altezza * 0.115)
    # Gli strati non cominciano netti sull'orizzonte: le creste salgono
    # sopra di esso, e il respiro tiene il testo fuori dalle onde
    respiro = int(altezza * 0.095)
    servono = (cima + blocco + respiro) / altezza
    orizzonte = min(max(orizzonte, servono), 0.80)

    pagina = onde.fondo(larghezza, altezza, orizzonte=orizzonte, seme=seme)

    zona = altezza * orizzonte - respiro
    y = max(int((cima + zona) / 2 - blocco / 2), cima)

    penna = ImageDraw.Draw(pagina)
    for voce in preparate:
        if voce.get("filetto"):
            _riga_oro(pagina, y + voce["altezza"] // 2, 0.30)
        else:
            spaziatura = voce.get("spaziatura", 0)
            larga = _larghezza_spaziata(voce["testo"], voce["font"], spaziatura)
            x = (larghezza - larga) / 2
            _scrivi_spaziato(penna, x, y, voce["testo"], voce["font"],
                             voce["colore"], spaziatura)
        y += voce["altezza"]

    return _firma(pagina, cfg)


def marchio_scritto(pagina: Image.Image, cfg: dict, y: int | None = None,
                    corpo: float = 0.032, colore: str = onde.ORO) -> None:
    """
    Il nome della galleria come sta in fondo alle locandine: tondo, spaziato,
    oro. È la costante che tiene insieme una pagina generata e una stampata.
    """
    from grafica import _carica_font
    penna = ImageDraw.Draw(pagina)
    font = _carica_font(cfg["font_serif"], int(pagina.width * corpo), "font_serif")
    testo = "BE Art Gallery  ·  Pistoia"
    spaziatura = pagina.width * 0.006
    larghezza_testo = _larghezza_spaziata(testo, font, spaziatura)
    x = (pagina.width - larghezza_testo) / 2
    if y is None:
        y = pagina.height - int(pagina.height * 0.058)
    _scrivi_spaziato(penna, x, y, testo, font, colore, spaziatura)


def _firma(pagina: Image.Image, cfg: dict) -> Image.Image:
    """Il nome della galleria in fondo, e il marchio in alto a sinistra."""
    marchio_scritto(pagina, cfg)
    return applica_logo(pagina, {**cfg, "logo_larghezza": 0.155,
                                 "logo_variante": "nero",
                                 "logo_velatura": False})


IMPAGINAZIONI["manifesto"] = manifesto
