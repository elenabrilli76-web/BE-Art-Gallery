#!/usr/bin/env python3
"""
Post, caroselli e storie per BE Art Gallery.

Da una cartella di foto produce i PNG pronti da caricare, alla misura giusta
per ogni formato, nell'impaginazione scelta per quel contenuto.
"""

from pathlib import Path

import impaginazione
from grafica import FORMATI, impostazioni, raccogli_foto, ritaglia

PREDEFINITE = {"post": "pieno", "carosello": "pieno", "storia": "pieno"}


def _foto(cartella: Path, indicazione):
    """Il percorso di una foto della cartella, o niente per un fondo pieno."""
    if not indicazione:
        return None
    percorso = Path(indicazione)
    return percorso if percorso.is_absolute() else cartella / indicazione


def crea_post(cartella_foto: Path, destinazione: Path, spec: dict,
              cfg: dict) -> list[Path]:
    misura = FORMATI["post"]
    foto = spec.get("foto") or raccogli_foto(cartella_foto)[0].name
    pagina = impaginazione.pagina(
        spec.get("impaginazione", PREDEFINITE["post"]),
        _foto(cartella_foto, foto), spec.get("testi", []), cfg, misura,
    )
    uscita = destinazione / "post.png"
    pagina.save(uscita)
    return [uscita]


def crea_storia(cartella_foto: Path, destinazione: Path, spec: dict,
                cfg: dict) -> list[Path]:
    misura = FORMATI["storia"]
    foto = spec.get("foto") or raccogli_foto(cartella_foto)[0].name
    pagina = impaginazione.pagina(
        spec.get("impaginazione", PREDEFINITE["storia"]),
        _foto(cartella_foto, foto), spec.get("testi", []), cfg, misura,
    )
    uscita = destinazione / "storia.png"
    pagina.save(uscita)
    return [uscita]


def crea_carosello(cartella_foto: Path, destinazione: Path, spec: dict,
                   cfg: dict) -> list[Path]:
    """
    Una pagina per foto, più l'eventuale schermata finale.

    L'impaginazione è la stessa per tutte le pagine: dentro un carosello la
    coerenza tiene insieme il racconto, e la varietà sta fra un contenuto e il
    successivo. Sulle foto non va testo se non richiesto — le immagini di un
    evento funzionano da sole, e una scritta sopra le fa somigliare a una
    locandina.
    """
    misura = FORMATI["carosello"]
    nome = spec.get("impaginazione", PREDEFINITE["carosello"])

    if spec.get("pagine"):
        return _carosello_a_pagine(cartella_foto, destinazione, spec, cfg,
                                   misura, nome)

    foto = raccogli_foto(cartella_foto, spec.get("ordine"))
    testi_per_pagina = {int(k): v for k, v in (spec.get("testi") or {}).items()}
    numerata = spec.get("numerazione", False)

    prodotte: list[Path] = []
    for numero, immagine in enumerate(foto, start=1):
        pagina = impaginazione.pagina(
            nome, immagine, testi_per_pagina.get(numero, []), cfg, misura,
            numero=numero if numerata else 0,
        )
        uscita = destinazione / f"carosello_{numero:02d}.png"
        pagina.save(uscita)
        prodotte.append(uscita)

    finale = spec.get("finale")
    if finale:
        # La chiusura ha la sua impaginazione: le informazioni pratiche vogliono
        # un fondo pulito. Senza una foto indicata è un fondo scuro pieno con il
        # testo al centro; con una foto sotto conviene la cornice
        predefinita = "cornice" if finale.get("sfondo") else "pieno"
        pagina = impaginazione.pagina(
            finale.get("impaginazione", predefinita),
            _foto(cartella_foto, finale.get("sfondo")),
            [{"righe": finale["righe"],
              "posizione": finale.get("posizione", "centro"),
              "enfasi": finale.get("enfasi", True)}],
            cfg, misura,
        )
        uscita = destinazione / f"carosello_{len(foto) + 1:02d}.png"
        pagina.save(uscita)
        prodotte.append(uscita)

    return prodotte


def _carosello_a_pagine(cartella_foto: Path, destinazione: Path, spec: dict,
                        cfg: dict, misura, predefinita: str) -> list[Path]:
    """
    Il carosello scritto pagina per pagina, quando il racconto non è "una foto
    dopo l'altra" ma un'alternanza fra locandina e fotografia — è la forma che
    serve agli annunci: si apre con il manifesto, si entra nello spazio con due
    scatti, si chiude con la chiamata.

    Ogni pagina dichiara la sua impaginazione, la sua foto (o nessuna) e i suoi
    testi: `righe` con i ruoli tipografici per le pagine di sola carta,
    `testi` per quelle costruite sopra una fotografia.
    """
    numerata = spec.get("numerazione", False)
    prodotte: list[Path] = []
    for numero, voce in enumerate(spec["pagine"], start=1):
        immagine = _foto(cartella_foto, voce.get("foto"))
        if voce.get("pronta"):
            # Una pagina già impaginata altrove — una locandina, per esempio:
            # si porta dentro com'è, riportata alla misura del carosello
            pagina = ritaglia(_foto(cartella_foto, voce["pronta"]), *misura)
        else:
            testi = voce.get("righe") or voce.get("testi") or []
            pagina = impaginazione.pagina(
                voce.get("impaginazione", predefinita), immagine, testi, cfg,
                misura, numero=numero if numerata else 0,
                orizzonte=voce.get("orizzonte", 0.46), seme=voce.get("seme", 0),
            )
        uscita = destinazione / f"carosello_{numero:02d}.png"
        pagina.save(uscita)
        prodotte.append(uscita)
    return prodotte


COSTRUTTORI = {
    "post": crea_post,
    "storia": crea_storia,
    "carosello": crea_carosello,
}


def crea(formato: str, cartella_foto: Path, destinazione: Path, spec: dict,
         extra: dict | None = None) -> list[Path]:
    destinazione.mkdir(parents=True, exist_ok=True)
    return COSTRUTTORI[formato](cartella_foto, destinazione, spec, impostazioni(extra))
