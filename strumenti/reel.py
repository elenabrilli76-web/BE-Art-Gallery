#!/usr/bin/env python3
"""
Generatore di reel per BE Art Gallery.

Prende una cartella di foto e produce un video verticale 1080x1920 pronto
per Instagram Reels / Stories, con movimento Ken Burns, transizioni in
dissolvenza, testi in sovrimpressione e musica di sottofondo.

Uso minimo:
    python3 reel.py --foto ./foto --out reel.mp4

Con testi e musica:
    python3 reel.py --foto ./foto --musica musica.mp3 \
        --titolo "BE Art Gallery" --sottotitolo "Pistoia" \
        --finale "I Luoghi dell'Anima|Iscrizioni entro il 30 settembre"

Con controllo completo (ordine foto, testo per scena):
    python3 reel.py --progetto progetto.json
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from grafica import impostazioni, raccogli_foto, ritaglia, strato_testo

# ----------------------------------------------------------------------------
# Impostazioni di base — modificabili da progetto.json
# ----------------------------------------------------------------------------

DEFAULT = {
    "larghezza": 1080,
    "altezza": 1920,
    "fps": 30,
    "durata_scena": 3.2,        # secondi per foto
    "durata_transizione": 0.6,  # dissolvenza incrociata fra due foto
    "zoom": 0.14,               # 0.14 = zoom del 14% nell'arco della scena
    "sovracampionamento": 2,    # la foto viene preparata a 2x prima dello zoom
    "crf": 20,
    "preset": "medium",         # codifica finale
    "preset_intermedio": "veryfast",
    "audio_bitrate": "192k",
    "fade_audio": 1.5,          # dissolvenza audio in chiusura
}

ESTENSIONI = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}


def trova_ffmpeg() -> str:
    """ffmpeg di sistema se c'è, altrimenti quello del pacchetto imageio-ffmpeg."""
    binario = shutil.which("ffmpeg")
    if binario:
        return binario
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit(
            "ffmpeg non trovato.\n"
            "Installalo con:  pip install imageio-ffmpeg\n"
            "oppure (Linux):  sudo apt install ffmpeg"
        )


def esegui(comando: list[str], descrizione: str) -> None:
    esito = subprocess.run(comando, capture_output=True, text=True)
    if esito.returncode != 0:
        coda = "\n".join(esito.stderr.strip().splitlines()[-15:])
        sys.exit(f"\nErrore durante: {descrizione}\n\n{coda}\n")


# ----------------------------------------------------------------------------
# Testi in sovrimpressione
# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Costruzione del video
# ----------------------------------------------------------------------------

def filtro_ken_burns(cfg: dict, durata: float, stile: int) -> str:
    """Movimento lento sull'immagine gia' preparata da prepara_immagine()."""
    larghezza, altezza, fps = cfg["larghezza"], cfg["altezza"], cfg["fps"]
    fotogrammi = max(int(round(durata * fps)), 1)
    zoom = cfg["zoom"]

    avanzamento = f"on/{fotogrammi}"
    if stile % 4 == 0:      # zoom in, centrato
        z = f"1+{zoom}*{avanzamento}"
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif stile % 4 == 1:    # zoom out, centrato
        z = f"{1 + zoom}-{zoom}*{avanzamento}"
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif stile % 4 == 2:    # zoom in con deriva verso destra
        z = f"1+{zoom}*{avanzamento}"
        x, y = f"(iw-iw/zoom)*({avanzamento})", "ih/2-(ih/zoom/2)"
    else:                   # zoom in con deriva verso l'alto
        z = f"1+{zoom}*{avanzamento}"
        x, y = "iw/2-(iw/zoom/2)", f"(ih-ih/zoom)*(1-{avanzamento})"

    return (
        f"zoompan=z='{z}':x='{x}':y='{y}':d={fotogrammi}:s={larghezza}x{altezza}:fps={fps},"
        f"setsar=1,format=yuv420p"
    )


def crea_scena(ffmpeg: str, foto: Path, destinazione: Path, cfg: dict,
               durata: float, stile: int, lavoro: Path) -> None:
    # zoompan si muove in modo fluido solo se il fotogramma in ingresso e'
    # piu' grande dell'uscita: la foto viene portata a 2x una volta sola.
    fattore = cfg["sovracampionamento"]
    pronta = lavoro / f"pronta_{destinazione.stem}.jpg"
    ritaglia(foto, cfg["larghezza"] * fattore, cfg["altezza"] * fattore).save(
        pronta, quality=95, subsampling=0)
    # Un solo fotogramma in ingresso: e' zoompan, con d=<fotogrammi>, a generare
    # tutta la scena. Passandogli un flusso in loop produrrebbe invece
    # <fotogrammi> uscite per ogni ingresso, cioe' una scena lunghissima e ferma.
    esegui([
        ffmpeg, "-y", "-loglevel", "error",
        "-i", str(pronta),
        "-vf", filtro_ken_burns(cfg, durata, stile),
        "-c:v", "libx264", "-preset", cfg["preset_intermedio"], "-crf", str(cfg["crf"]),
        "-pix_fmt", "yuv420p", str(destinazione),
    ], f"creazione scena da {foto.name}")


def unisci_scene(ffmpeg: str, scene: list[Path], destinazione: Path,
                 cfg: dict, durata_scena: float) -> float:
    """Concatena le scene con dissolvenza incrociata. Restituisce la durata finale."""
    transizione = cfg["durata_transizione"]

    if len(scene) == 1:
        shutil.copy(scene[0], destinazione)
        return durata_scena

    ingressi: list[str] = []
    for scena in scene:
        ingressi += ["-i", str(scena)]

    catena: list[str] = []
    corrente = "[0:v]"
    # Ogni xfade accorcia il risultato di 'transizione' secondi
    accumulata = durata_scena
    for indice in range(1, len(scene)):
        offset = accumulata - transizione
        etichetta = f"[v{indice}]"
        catena.append(
            f"{corrente}[{indice}:v]xfade=transition=fade:"
            f"duration={transizione}:offset={offset:.3f}{etichetta}"
        )
        corrente = etichetta
        accumulata = offset + durata_scena

    esegui([
        ffmpeg, "-y", "-loglevel", "error", *ingressi,
        "-filter_complex", ";".join(catena),
        "-map", corrente,
        "-c:v", "libx264", "-preset", cfg["preset_intermedio"], "-crf", str(cfg["crf"]),
        "-pix_fmt", "yuv420p", str(destinazione),
    ], "unione delle scene")

    return accumulata


def applica_testi(ffmpeg: str, video: Path, testi: list[dict], destinazione: Path,
                  cfg: dict, cartella: Path) -> None:
    if not testi:
        shutil.copy(video, destinazione)
        return

    ingressi = ["-i", str(video)]
    catena: list[str] = []
    corrente = "[0:v]"
    dissolvenza = 0.5

    for indice, testo in enumerate(testi, start=1):
        png = cartella / f"testo_{indice}.png"
        strato_testo(
            testo["righe"], cfg["larghezza"], cfg["altezza"], cfg,
            posizione=testo.get("posizione", "basso"),
            enfasi=testo.get("enfasi", False),
        ).save(png)
        inizio, fine = float(testo["inizio"]), float(testo["fine"])
        durata = max(fine - inizio, dissolvenza * 2 + 0.1)
        ingressi += ["-loop", "1", "-t", f"{durata:.3f}", "-i", str(png)]

        catena.append(
            f"[{indice}:v]format=rgba,"
            f"fade=t=in:st=0:d={dissolvenza}:alpha=1,"
            f"fade=t=out:st={durata - dissolvenza:.3f}:d={dissolvenza}:alpha=1,"
            f"setpts=PTS+{inizio}/TB[t{indice}]"
        )
        etichetta = f"[o{indice}]"
        catena.append(
            f"{corrente}[t{indice}]overlay=0:0:"
            f"enable='between(t,{inizio},{inizio + durata:.3f})'{etichetta}"
        )
        corrente = etichetta

    esegui([
        ffmpeg, "-y", "-loglevel", "error", *ingressi,
        "-filter_complex", ";".join(catena),
        "-map", corrente,
        "-c:v", "libx264", "-preset", cfg["preset"], "-crf", str(cfg["crf"]),
        "-pix_fmt", "yuv420p", str(destinazione),
    ], "sovrimpressione dei testi")


def applica_musica(ffmpeg: str, video: Path, musica: Path, destinazione: Path,
                   cfg: dict, durata: float) -> None:
    if not musica:
        shutil.copy(video, destinazione)
        return

    fade = cfg["fade_audio"]
    esegui([
        ffmpeg, "-y", "-loglevel", "error",
        "-i", str(video), "-i", str(musica),
        "-filter_complex",
        f"[1:a]afade=t=in:st=0:d=1,"
        f"afade=t=out:st={max(durata - fade, 0):.3f}:d={fade},"
        f"atrim=0:{durata:.3f}[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", cfg["audio_bitrate"],
        "-shortest", str(destinazione),
    ], "aggiunta della musica")


# ----------------------------------------------------------------------------

def testi_automatici(titolo: str | None, sottotitolo: str | None,
                     finale: str | None, durata: float) -> list[dict]:
    """Apertura sulla prima scena, chiamata all'azione sull'ultima."""
    testi = []
    if titolo or sottotitolo:
        righe = [r for r in (titolo, sottotitolo) if r]
        testi.append({"righe": righe, "inizio": 0.4, "fine": 3.6,
                      "posizione": "centro", "enfasi": True})
    if finale:
        testi.append({"righe": finale.split("|"),
                      "inizio": max(durata - 3.8, 0.5), "fine": durata - 0.3,
                      "posizione": "basso", "enfasi": True})
    return testi


def main() -> None:
    p = argparse.ArgumentParser(description="Genera un reel verticale dalle foto della galleria.")
    p.add_argument("--foto", type=Path, help="cartella con le foto")
    p.add_argument("--out", type=Path, default=Path("reel.mp4"), help="file video da produrre")
    p.add_argument("--musica", type=Path, help="traccia audio (mp3/m4a/wav)")
    p.add_argument("--titolo", help="testo grande di apertura")
    p.add_argument("--sottotitolo", help="riga sotto il titolo")
    p.add_argument("--finale", help="chiusura, righe separate da |")
    p.add_argument("--durata-scena", type=float, help="secondi per foto")
    p.add_argument("--max-foto", type=int, default=10, help="quante foto usare al massimo")
    p.add_argument("--progetto", type=Path, help="file JSON con la configurazione completa")
    args = p.parse_args()

    cfg = impostazioni(DEFAULT)
    progetto: dict = {}
    if args.progetto:
        progetto = json.loads(args.progetto.read_text(encoding="utf-8"))
        cfg.update(progetto.get("impostazioni", {}))

    cartella_foto = Path(progetto.get("foto", args.foto or ""))
    if not cartella_foto or not cartella_foto.is_dir():
        sys.exit("Indica una cartella di foto valida con --foto (o nel file di progetto).")

    if args.durata_scena:
        cfg["durata_scena"] = args.durata_scena
    durata_scena = cfg["durata_scena"]

    foto = raccogli_foto(cartella_foto, progetto.get("ordine"))[: args.max_foto]
    musica = Path(progetto["musica"]) if progetto.get("musica") else args.musica
    destinazione = Path(progetto.get("out", args.out))

    ffmpeg = trova_ffmpeg()
    print(f"ffmpeg: {ffmpeg}", flush=True)
    print(f"Foto:   {len(foto)}", flush=True)

    with tempfile.TemporaryDirectory() as tmp:
        lavoro = Path(tmp)

        scene = []
        for indice, immagine in enumerate(foto):
            scena = lavoro / f"scena_{indice:03d}.mp4"
            print(f"  [{indice + 1}/{len(foto)}] {immagine.name}", flush=True)
            crea_scena(ffmpeg, immagine, scena, cfg, durata_scena, indice, lavoro)
            scene.append(scena)

        print("Unione delle scene...", flush=True)
        montato = lavoro / "montato.mp4"
        durata = unisci_scene(ffmpeg, scene, montato, cfg, durata_scena)

        testi = progetto.get("testi") or testi_automatici(
            args.titolo, args.sottotitolo, args.finale, durata
        )
        if testi:
            print(f"Testi in sovrimpressione: {len(testi)}", flush=True)
        con_testi = lavoro / "con_testi.mp4"
        applica_testi(ffmpeg, montato, testi, con_testi, cfg, lavoro)

        if musica:
            print(f"Musica: {musica}", flush=True)
        destinazione.parent.mkdir(parents=True, exist_ok=True)
        applica_musica(ffmpeg, con_testi, musica, destinazione, cfg, durata)

    peso = destinazione.stat().st_size / 1_000_000
    print(f"\nFatto: {destinazione}  —  {durata:.1f}s, {peso:.1f} MB, "
          f"{cfg['larghezza']}x{cfg['altezza']}")


if __name__ == "__main__":
    main()
