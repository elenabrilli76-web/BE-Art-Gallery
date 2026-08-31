# BE Art Gallery — contesto per Claude Code

Chi apre una sessione su questo repository legge prima questo file.
Serve a non dover rispiegare ogni volta com'è fatto il lavoro.

## Chi siamo

**BE Art Gallery & Creative Lab** — Pistoia. Galleria d'arte in un palazzo
storico del XIII secolo, su tre livelli comunicanti, di fronte a San Pier
Maggiore. Mostre personali e collettive, più servizi agli artisti.

## Dove stanno le cose

| Cosa | Dove |
|---|---|
| Foto, logo, depliant, biglietti, video | **Google Drive**, cartella `BE Art Gallery` |
| Grafica di marca (colori, font, logo) | **Canva**, brand kit `BE Art Gallery` |
| Codice del sito | repository `be-art-gallery-site` |
| Strumenti e processo | **questo repository** |

Le sottocartelle del Drive che servono più spesso: `Galleria-foto allestita 1`,
`Galleria-foto allestita 2`, `Galleria-foto vuota`, `Logo`,
`Materiale Grafico_Social`, `Depliant`, `Biglietto da Visita`.

> I materiali **non** stanno su GitHub: sono file pesanti e si sfogliano
> meglio dal Drive. Qui ci sono solo gli strumenti e i testi.

## Gli eventi

| Evento | Date | CTA |
|---|---|---|
| **Mostra personale E.B.Art** (Elena Brilli) | 29 ago – 6 set 2026 | vieni a visitare |
| **ArtiAMO** — collettiva AMO.Art, su invito | 12 – 27 set 2026 | vieni a visitare — **mai** "iscriviti" |
| **I Luoghi dell'Anima** — collettiva aperta | 10 – 25 ott 2026 · iscrizioni entro il **30 settembre** | iscriviti / partecipa come artista |

## Regole di tono, non negoziabili

- **Una sola CTA per contenuto.** Mai due link o due azioni diverse.
- **ArtiAMO è su invito**: il messaggio è sempre "vieni a visitare", mai "iscriviti".
- **I Luoghi dell'Anima** è l'unico evento con CTA di iscrizione, ed è la
  priorità di comunicazione fino al 30 settembre.
- **Instagram**: testo breve, gancio forte in apertura. I link stanno solo in
  bio o negli sticker delle Stories.
- **Facebook**: tono più disteso, dettagli pratici (date, orari, come
  iscriversi), e il link va direttamente nel post.
- Ogni contenuto Instagram viene ripubblicato su Facebook nella stessa
  settimana, con in più il link diretto.

## Come si lavora

Il processo completo è in [`contenuti-social/PROCESSO.md`](contenuti-social/PROCESSO.md).
In breve: si compila un brief, si mettono le foto in una cartella, Claude
scrive i testi, poi il reel si genera con lo script e post/caroselli/storie
si fanno in Canva sul brand kit.

## Lo strumento

```bash
pip install -r reel/requirements.txt
python3 reel/reel.py --foto ./contenuti-social/in-lavorazione/foto --out reel.mp4
```

Istruzioni complete: [`reel/README.md`](reel/README.md).

## Nota sulla riservatezza

Questo repository è **pubblico**. Non vanno messi qui: token di accesso a
Meta o ad altri servizi, indirizzi email di contatti, la rubrica, dati degli
artisti iscritti. Se serve tenerci materiale riservato, va reso privato prima.
