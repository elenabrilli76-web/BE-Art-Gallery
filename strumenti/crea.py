#!/usr/bin/env python3
"""
Un comando solo, per tutti i contenuti di BE Art Gallery.

Legge contenuti-social/in-lavorazione/contenuto.json, guarda quali formati sono
richiesti e produce tutto dentro in-lavorazione/pronti: il reel come MP4, post,
caroselli e storie come PNG. Da lì si passano sul telefono e si pubblicano.

    py strumenti\\crea.py

Il file contenuto.json lo scrive Claude a partire dal brief: non c'è niente da
comporre a mano.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

CARTELLA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARTELLA))

import immagini  # noqa: E402  (importato dopo l'aggiunta al percorso di ricerca)

RADICE = CARTELLA.parent
LAVORO = RADICE / "contenuti-social" / "in-lavorazione"
PREDEFINITO = LAVORO / "contenuto.json"


def fine(messaggio: str) -> None:
    print(f"\n{messaggio}\n", flush=True)
    raise SystemExit(1)


def genera_reel(spec: dict, cartella_foto: Path, destinazione: Path) -> list[Path]:
    """Delega a reel.py, che ha la sua catena ffmpeg."""
    uscita = destinazione / "reel.mp4"
    progetto = {
        "foto": str(cartella_foto),
        "out": str(uscita),
        "impostazioni": spec.get("impostazioni", {}),
    }
    for chiave in ("ordine", "testi", "musica", "stile"):
        if spec.get(chiave):
            progetto[chiave] = spec[chiave]

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                     encoding="utf-8") as f:
        json.dump(progetto, f, ensure_ascii=False)
        temporaneo = f.name

    esito = subprocess.run(
        [sys.executable, str(CARTELLA / "reel.py"), "--progetto", temporaneo]
    )
    Path(temporaneo).unlink(missing_ok=True)
    if esito.returncode != 0:
        fine("Il reel non è stato prodotto: vedi l'errore qui sopra.")
    return [uscita]


def main() -> None:
    percorso = Path(sys.argv[1]) if len(sys.argv) > 1 else PREDEFINITO
    if not percorso.exists():
        fine(
            f"Non trovo {percorso}.\n"
            "È il file che descrive il contenuto da produrre: chiedilo a Claude\n"
            "insieme ai testi, e salvalo in contenuti-social/in-lavorazione/."
        )

    contenuto = json.loads(percorso.read_text(encoding="utf-8"))
    cartella_foto = Path(contenuto.get("foto") or LAVORO / "foto")
    destinazione = Path(contenuto.get("out") or LAVORO / "pronti")

    if not cartella_foto.is_dir():
        fine(f"Non trovo la cartella delle foto: {cartella_foto}")
    if not any(f for f in cartella_foto.iterdir() if f.name != ".gitkeep"):
        fine(
            f"La cartella {cartella_foto} è vuota.\n"
            "Mettici le foto, rinominate 01.jpg, 02.jpg, 03.jpg…"
        )

    destinazione.mkdir(parents=True, exist_ok=True)
    extra = contenuto.get("impostazioni")

    richiesti = [f for f in ("post", "carosello", "storia", "reel") if f in contenuto]
    if not richiesti:
        fine("In contenuto.json non è richiesto nessun formato.")

    print(f"Contenuto: {contenuto.get('nome', percorso.stem)}", flush=True)
    print(f"Formati:   {', '.join(richiesti)}\n", flush=True)

    prodotti: list[Path] = []
    for formato in richiesti:
        print(f"— {formato}", flush=True)
        if formato == "reel":
            prodotti += genera_reel(contenuto["reel"], cartella_foto, destinazione)
        else:
            try:
                prodotti += immagini.crea(
                    formato, cartella_foto, destinazione, contenuto[formato], extra
                )
            except FileNotFoundError as errore:
                fine(str(errore))

    print(f"\nFatto. {len(prodotti)} file in {destinazione}:\n", flush=True)
    for file in prodotti:
        peso = file.stat().st_size / 1_000_000
        print(f"  {file.name}  ({peso:.1f} MB)", flush=True)
    print("\nPassali sul telefono e pubblica.\n", flush=True)


if __name__ == "__main__":
    main()
