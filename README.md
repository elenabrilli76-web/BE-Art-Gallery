# BE Art Gallery — strumenti per i contenuti social

Questo repository contiene **gli strumenti**, non i materiali.

Foto, video, logo e depliant restano su Google Drive: sono file pesanti, si
sfogliano meglio da lì e GitHub non è fatto per conservarli.

## Cosa c'è

- **[`reel/`](reel/)** — generatore di reel: da una cartella di foto produce un
  video verticale 1080x1920 pronto per Instagram, con movimento sulle immagini,
  dissolvenze, testi in sovrimpressione e musica.

## Come si usa, in breve

```bash
pip install -r reel/requirements.txt
python3 reel/reel.py --foto ./foto --out reel.mp4 --titolo "BE Art Gallery"
```

Le istruzioni complete sono in [`reel/README.md`](reel/README.md).
