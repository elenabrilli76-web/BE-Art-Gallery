# Generatore di reel — BE Art Gallery

Prende una cartella di foto e produce un video verticale **1080x1920** pronto
da caricare su Instagram Reels, Stories o Facebook: movimento lento sulle
immagini (effetto Ken Burns), dissolvenze fra una foto e l'altra, testi in
sovrimpressione e musica di sottofondo.

Il video è composto **solo** dalle foto che gli dai in ingresso: non inventa
nulla e non aggiunge immagini generate.

## Installazione (una volta sola)

```bash
pip install Pillow imageio-ffmpeg
```

`imageio-ffmpeg` porta con sé ffmpeg, quindi non serve installarlo a parte.
Se sul computer c'è già ffmpeg, lo script usa quello.

## Uso

Il caso più semplice — una cartella di foto, un video in uscita:

```bash
python3 reel.py --foto ./foto --out reel.mp4
```

Con titolo di apertura, chiusura e musica:

```bash
python3 reel.py --foto ./foto --out reel.mp4 --musica ./musica.mp3 \
  --titolo "BE Art Gallery" \
  --sottotitolo "Pistoia · Creative Lab" \
  --finale "I Luoghi dell'Anima|Iscrizioni entro il 30 settembre"
```

Le righe del `--finale` si separano con `|`. La prima riga viene scritta nel
colore d'accento, le successive in bianco.

### Opzioni

| Opzione | Cosa fa | Predefinito |
|---|---|---|
| `--foto` | cartella con le immagini | — |
| `--out` | file video da produrre | `reel.mp4` |
| `--musica` | traccia audio (mp3, m4a, wav) | nessuna |
| `--titolo` | testo grande di apertura | nessuno |
| `--sottotitolo` | riga sotto il titolo | nessuno |
| `--finale` | chiusura, righe separate da `\|` | nessuna |
| `--durata-scena` | secondi per foto | `3.2` |
| `--max-foto` | quante foto usare al massimo | `10` |
| `--progetto` | file JSON con la configurazione completa | — |

Senza `--progetto` le foto vengono prese **in ordine alfabetico**. Se arrivano
da un telefono i nomi contengono già data e ora, quindi l'ordine è cronologico.

## Controllo completo: `progetto.json`

Per decidere l'ordine delle foto e piazzare i testi al secondo esatto:

```bash
python3 reel.py --progetto progetto.json
```

Vedi `progetto.esempio.json`. Le posizioni possibili per un testo sono
`alto`, `centro` e `basso`; `enfasi: true` usa il corpo grande e il colore
d'accento sulla prima riga.

## Durata del video

Con i valori predefiniti: `numero_foto x 3.2 - (numero_foto - 1) x 0.6` secondi.
Otto foto fanno circa **21 secondi**, dieci circa **27**. Instagram accetta
Reels fino a 90 secondi, ma sotto i 30 il video viene guardato fino in fondo
molto più spesso.

## Tempi di elaborazione

Circa **5 secondi di calcolo per ogni foto**, più una passata finale. Sei foto
richiedono circa mezzo minuto su una macchina modesta.

## Musica

Usa solo tracce per cui hai i diritti, oppure la libreria audio interna di
Instagram (in quel caso genera il video **senza** `--musica` e aggiungi la
musica dall'app al momento di pubblicare: è anche il modo in cui il brano
viene distribuito meglio dall'algoritmo).
