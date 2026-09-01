#!/usr/bin/env python3
"""
Post, caroselli e storie per BE Art Gallery.

Da una cartella di foto produce i PNG pronti da caricare, alla misura giusta
per ogni formato, con i testi in sovrimpressione dove servono.
"""

from pathlib import Path

from grafica import (FORMATI, applica_logo, componi, fondo_pieno, impostazioni,
                     raccogli_foto, ritaglia)


def _sfondo(cartella: Path, indicazione, larghezza: int, altezza: int):
    """Una foto della cartella, oppure un fondo pieno se non ne è indicata una."""
    if not indicazione:
        return fondo_pieno(larghezza, altezza)
    percorso = cartella / indicazione if not Path(indicazione).is_absolute() else Path(indicazione)
    return ritaglia(percorso, larghezza, altezza)


def crea_post(cartella_foto: Path, destinazione: Path, spec: dict,
              cfg: dict) -> list[Path]:
    larghezza, altezza = FORMATI["post"]
    foto = spec.get("foto") or raccogli_foto(cartella_foto)[0].name
    immagine = componi(
        applica_logo(ritaglia(cartella_foto / foto, larghezza, altezza), cfg),
        spec.get("testi", []), cfg,
    )
    uscita = destinazione / "post.png"
    immagine.save(uscita)
    return [uscita]


def crea_storia(cartella_foto: Path, destinazione: Path, spec: dict,
                cfg: dict) -> list[Path]:
    larghezza, altezza = FORMATI["storia"]
    foto = spec.get("foto") or raccogli_foto(cartella_foto)[0].name
    immagine = componi(
        applica_logo(ritaglia(cartella_foto / foto, larghezza, altezza), cfg),
        spec.get("testi", []), cfg,
    )
    uscita = destinazione / "storia.png"
    immagine.save(uscita)
    return [uscita]


def crea_carosello(cartella_foto: Path, destinazione: Path, spec: dict,
                   cfg: dict) -> list[Path]:
    """
    Una pagina per foto, più l'eventuale schermata finale.

    Sulle foto non va testo se non richiesto: le immagini di un evento
    funzionano da sole, e una scritta sopra le fa somigliare a una locandina.
    """
    larghezza, altezza = FORMATI["carosello"]
    foto = raccogli_foto(cartella_foto, spec.get("ordine"))
    testi_per_pagina = {int(k): v for k, v in (spec.get("testi") or {}).items()}

    prodotte: list[Path] = []
    for numero, immagine in enumerate(foto, start=1):
        pagina = componi(
            applica_logo(ritaglia(immagine, larghezza, altezza), cfg),
            testi_per_pagina.get(numero, []), cfg,
        )
        uscita = destinazione / f"carosello_{numero:02d}.png"
        pagina.save(uscita)
        prodotte.append(uscita)

    finale = spec.get("finale")
    if finale:
        pagina = componi(
            applica_logo(_sfondo(cartella_foto, finale.get("sfondo"),
                                 larghezza, altezza), cfg),
            [{
                "righe": finale["righe"],
                "posizione": finale.get("posizione", "centro"),
                "enfasi": finale.get("enfasi", True),
            }],
            cfg,
        )
        uscita = destinazione / f"carosello_{len(foto) + 1:02d}.png"
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
