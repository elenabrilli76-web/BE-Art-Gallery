# Processo di creazione contenuti — BE Art Gallery

Vale per tutti e quattro i formati: **reel, post, carosello, storia.**
Il giro è sempre lo stesso, cambia solo cosa chiedi.

```
1. metti le foto nella cartella
2. dici a Claude cosa vuoi
3. lanci un comando
4. scarichi e pubblichi
```

---

## Passo 1 — Le foto nella cartella

```
contenuti-social\in-lavorazione\foto\
```

Prendile dal tuo archivio e copiale lì, **rinominate `01.jpg`, `02.jpg`,
`03.jpg`…** L'ordine dei nomi è l'ordine in cui appariranno.

Quante: reel 6–10 · carosello 4–8 · post 1 · storia 1. Se ne metti di più non
è un problema: si sceglie dopo quali usare.

**Nella stessa cartella puoi mettere anche i video.** Entrano nei reel, dove
il movimento racconta più di una foto ferma; post, caroselli e storie li
ignorano.

> È sempre questa cartella, per qualunque formato. Non ce ne sono altre.

## Passo 2 — Dici a Claude cosa vuoi

Nella sessione **Creazione contenuti social**, scrivi in parole tue. Non serve
un modulo: serve che si capiscano tre cose.

1. **Che formato** — reel, post, carosello, storia. Anche più di uno insieme
2. **Di quale evento parla** e **cosa deve fare chi lo vede** — una sola azione
3. **Cosa deve venir fuori**, due righe con parole tue: l'idea, il tono

Esempio, ed è già abbastanza:

> «Un carosello con le foto dell'inaugurazione, per invitare a visitare la
> mostra prima che chiuda il 6 settembre. Ho messo 7 foto nella cartella.»

Se vuoi qualcosa di più strutturato c'è [`BRIEF.md`](BRIEF.md) da compilare,
ma è facoltativo.

### Cosa ricevi

Due file, che trovi in `in-lavorazione\` dopo un **Pull origin**:

| File | Cosa contiene |
|---|---|
| `testi.md` | caption per Instagram e Facebook, hashtag, note |
| `contenuto.json` | le istruzioni per il comando del passo 3 |

`testi.md` lo leggi tu. `contenuto.json` non devi aprirlo né capirlo: serve al
comando.

## Passo 3 — Un comando

Da GitHub Desktop: menu **Repository** → **Open in Command Prompt**. Poi:

```
py strumenti\crea.py
```

Basta questo, per qualunque formato. Il comando legge `contenuto.json`, guarda
cosa è stato chiesto e produce tutto.

Vedrai scorrere i formati, e alla fine l'elenco dei file prodotti.

**Quanto ci mette:** le immagini sono immediate, il reel circa 5 secondi per
foto. Un contenuto completo sta sotto il minuto.

## Passo 4 — Scarichi e pubblichi

Tutto quello che è stato prodotto è qui:

```
contenuti-social\in-lavorazione\pronti\
```

| File | Cos'è | Dove va |
|---|---|---|
| `post.png` | 1080×1350 | Instagram → **+** → Post |
| `carosello_01.png`, `02`, `03`… | 1080×1350, in ordine | Instagram → **+** → Post → *seleziona più elementi* |
| `storia.png` | 1080×1920 | Instagram → la tua foto profilo |
| `reel.mp4` | 1080×1920, H.264 | Instagram → **+** → Reel |

Passa i file sul telefono — Drive, oppure mandateli su WhatsApp da sola, che è
più rapido. Poi pubblica, con la caption che trovi in `testi.md`.

**Tre cose da ricordare al momento di pubblicare:**

- **Carosello:** l'ordine in cui tocchi le immagini è l'ordine finale. Toccale
  seguendo la numerazione dei file
- **Hashtag:** su Instagram vanno nel **primo commento**, non nella caption
- **Reel:** la musica aggiungila dall'app. I brani della libreria interna di
  Instagram vengono distribuiti meglio di un audio già montato nel video

Su **Facebook** ripubblichi lo stesso contenuto nella stessa settimana, con il
testo più lungo che trovi in `testi.md`: lì il link e il numero di telefono si
possono mettere direttamente, su Instagram no.

## Passo 5 — Archivi

Sposta il contenuto di `in-lavorazione\` in:

```
contenuti-social\pubblicati\2026-09-15-nome-contenuto\
```

Poi svuota `in-lavorazione\` e sei pronta per il prossimo.

Serve davvero: fra due mesi vorrai sapere cosa avevi già scritto e quali foto
avevi già usato.

---

## Le misure, per riferimento

| | Misura | Quante immagini |
|---|---|---|
| **Post** | 1080 × 1350 (verticale 4:5) | 1 |
| **Carosello** | 1080 × 1350 | 4–8 |
| **Storia** | 1080 × 1920 | 1 |
| **Reel** | 1080 × 1920 | 6–10 fra foto e spezzoni video → ~20 secondi |

Il verticale 4:5 occupa più spazio nel feed del quadrato, quindi si nota di più.
Un reel sotto i 30 secondi viene guardato fino in fondo molto più spesso.

## Domande che tornano

**Le foto vanno ritoccate prima?** No. Vengono ritagliate in verticale in
automatico, senza deformarle. Serve solo che siano a fuoco e ben esposte.

**Posso chiedere più formati insieme?** Sì, ed è il modo normale di lavorare:
un carosello per il feed e una storia con lo stesso contenuto si producono in
un colpo solo.

**Il risultato non mi convince, cosa cambio?** In quest'ordine: le foto — è
quasi sempre quello. Poi i testi. Poi, per il reel, il ritmo. Dillo a Claude e
rifai il comando: costa meno di un minuto.

**Devo aprire `contenuto.json`?** No. Se qualcosa non va, dillo a Claude e te
lo riscrive.
