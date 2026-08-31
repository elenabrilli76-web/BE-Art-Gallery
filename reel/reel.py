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

from PIL import Image, ImageDraw, ImageFont, ImageOps

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
    "colore_testo": "#FFFFFF",
    "colore_accento": "#C9A227",
    "font_titolo": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "font_testo": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
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

def _carica_font(percorso: str, dimensione: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(percorso, dimensione)
    except OSError:
        return ImageFont.load_default(dimensione)


def _manda_a_capo(testo: str, font: ImageFont.FreeTypeFont,
                  larghezza_utile: float) -> list[str]:
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


def _adatta_font(testo: str, font: ImageFont.FreeTypeFont, larghezza_utile: float,
                 percorso: str) -> ImageFont.FreeTypeFont:
    """Rimpicciolisce il font finche' la parola piu' lunga ci sta in larghezza."""
    parole = testo.split() or [testo]
    dimensione = font.size
    while dimensione > 24:
        candidato = _carica_font(percorso, dimensione)
        if max(candidato.getlength(p) for p in parole) <= larghezza_utile:
            return candidato
        dimensione -= 4
    return _carica_font(percorso, dimensione)


def disegna_testo(righe: list[str], destinazione: Path, cfg: dict,
                  posizione: str = "basso", enfasi: bool = False) -> None:
    """Crea un PNG trasparente con il testo e una velatura che lo rende leggibile."""
    larghezza, altezza = cfg["larghezza"], cfg["altezza"]
    tela = Image.new("RGBA", (larghezza, altezza), (0, 0, 0, 0))

    corpo = 64 if not enfasi else 82
    font_principale = _carica_font(cfg["font_titolo"], corpo)
    font_secondario = _carica_font(cfg["font_testo"], int(corpo * 0.62))

    # Manda a capo misurando il testo davvero, non stimando la larghezza media
    # di un carattere: con un serif in grassetto la stima sbaglia di molto e
    # spezza i titoli a meta' senza motivo.
    margine = int(larghezza * 0.09)
    utile = larghezza - 2 * margine
    spezzate: list[tuple[str, ImageFont.FreeTypeFont, int]] = []
    for indice, riga in enumerate(righe):
        font = font_principale if indice == 0 else font_secondario
        font = _adatta_font(riga, font, utile,
                            cfg["font_titolo"] if indice == 0 else cfg["font_testo"])
        for pezzo in _manda_a_capo(riga, font, utile):
            spezzate.append((pezzo, font, indice))

    interlinea = 1.28
    altezze = [int(font.size * interlinea) for _, font, _ in spezzate]
    blocco = sum(altezze)

    if posizione == "basso":
        partenza = altezza - int(altezza * 0.16) - blocco
    elif posizione == "alto":
        partenza = int(altezza * 0.14)
    else:
        partenza = (altezza - blocco) // 2

    # Velatura sfumata dietro al testo: senza, il bianco sparisce sulle foto chiare
    velatura = Image.new("RGBA", (larghezza, altezza), (0, 0, 0, 0))
    pennello = ImageDraw.Draw(velatura)
    alto_velatura = max(partenza - int(altezza * 0.10), 0)
    basso_velatura = min(partenza + blocco + int(altezza * 0.10), altezza)
    estensione = max(basso_velatura - alto_velatura, 1)
    for y in range(alto_velatura, basso_velatura):
        avanzamento = (y - alto_velatura) / estensione
        if posizione == "basso":
            opacita = int(165 * min(avanzamento * 1.8, 1.0))
        elif posizione == "alto":
            opacita = int(165 * min((1 - avanzamento) * 1.8, 1.0))
        else:
            opacita = int(150 * (1 - abs(avanzamento - 0.5) * 2) ** 0.5)
        pennello.line([(0, y), (larghezza, y)], fill=(0, 0, 0, opacita))
    tela = Image.alpha_composite(tela, velatura)

    penna = ImageDraw.Draw(tela)
    y = partenza
    for testo, font, riga_originale in spezzate:
        colore = cfg["colore_accento"] if (enfasi and riga_originale == 0) else cfg["colore_testo"]
        x = (larghezza - font.getlength(testo)) / 2
        penna.text((x + 2, y + 3), testo, font=font, fill=(0, 0, 0, 130))  # ombra
        penna.text((x, y), testo, font=font, fill=colore)
        y += int(font.size * interlinea)

    tela.save(destinazione)


# ----------------------------------------------------------------------------
# Costruzione del video
# ----------------------------------------------------------------------------

def prepara_immagine(foto: Path, destinazione: Path, cfg: dict) -> None:
    """
    Ritaglia e ridimensiona la foto una volta sola, con Pillow.

    Serve perche' zoompan, per muoversi in modo fluido, ha bisogno di un
    fotogramma piu' grande dell'uscita finale. Farlo fare a ffmpeg con il
    filtro scale significherebbe rifare il ridimensionamento a ogni singolo
    fotogramma della scena: qui invece si fa una volta e basta.
    """
    fattore = cfg["sovracampionamento"]
    obiettivo_w = cfg["larghezza"] * fattore
    obiettivo_h = cfg["altezza"] * fattore

    with Image.open(foto) as immagine:
        immagine = ImageOps.exif_transpose(immagine).convert("RGB")

        # Riempie il formato verticale senza deformare: ritaglia l'eccedenza
        scala = max(obiettivo_w / immagine.width, obiettivo_h / immagine.height)
        intermedia = immagine.resize(
            (max(int(immagine.width * scala + 0.5), obiettivo_w),
             max(int(immagine.height * scala + 0.5), obiettivo_h)),
            Image.LANCZOS,
        )
        sinistra = (intermedia.width - obiettivo_w) // 2
        alto = (intermedia.height - obiettivo_h) // 2
        ritagliata = intermedia.crop(
            (sinistra, alto, sinistra + obiettivo_w, alto + obiettivo_h)
        )
        ritagliata.save(destinazione, quality=95, subsampling=0)


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
    pronta = lavoro / f"pronta_{destinazione.stem}.jpg"
    prepara_immagine(foto, pronta, cfg)
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
        disegna_testo(
            testo["righe"], png, cfg,
            posizione=testo.get("posizione", "basso"),
            enfasi=testo.get("enfasi", False),
        )
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

def raccogli_foto(cartella: Path, ordine: list[str] | None) -> list[Path]:
    if ordine:
        foto = [cartella / nome for nome in ordine]
        mancanti = [str(f) for f in foto if not f.exists()]
        if mancanti:
            sys.exit("Foto non trovate:\n  " + "\n  ".join(mancanti))
        return foto

    foto = sorted(f for f in cartella.iterdir() if f.suffix.lower() in ESTENSIONI)
    if not foto:
        sys.exit(f"Nessuna immagine trovata in {cartella}")
    return foto


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

    cfg = dict(DEFAULT)
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
