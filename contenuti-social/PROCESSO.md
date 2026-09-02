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
| `testi.md` | la caption, in italiano e inglese, più gli hashtag |
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

**Due modi di trovarceli, ed è bene sapere quale sta succedendo.**

| Se le foto sono | I file finiti arrivano |
|---|---|
| sul tuo computer, nella cartella `foto\` | dal comando del passo 3 |
| solo da me — perché li ho composti io | con un **Pull origin**: la cartella `pronti` viaggia su GitHub |

Se dopo un Pull la cartella ti sembra ancora vuota, chiudila e riaprila:
Esplora risorse a volte non si accorge dei file nuovi.

### Se pubblichi dal telefono

Instagram si pubblica dal telefono, non dal PC, e i file mandati in chat non
sempre si scaricano — dipende dall'app che stai usando per aprire la chat.
**La via che funziona sempre è GitHub.** Ogni file di `pronti\` ha un indirizzo
fisso, fatto così:

```
https://raw.githubusercontent.com/elenabrilli76-web/BE-Art-Gallery/be-art-gallery-creazione-contenuti/contenuti-social/in-lavorazione/pronti/NOME-DEL-FILE
```

Ti mando sempre questi link già pronti, uno per immagine, quando finisco un
contenuto. Tu:

1. apri il link **nel browser del telefono** (Safari o Chrome — non dentro
   un'altra app, altrimenti il tenere premuto spesso non funziona)
2. tieni il dito premuto sull'immagine a schermo intero → **Salva immagine**
3. ripeti per ogni file, nell'ordine numerato

Salvate così finiscono nel Rullino, pronte per essere caricate su Instagram.

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
- **Hashtag:** nel **primo commento**, non nella caption. I primi sono sempre
  quelli della galleria
- **Reel:** la musica aggiungila dall'app. I brani della libreria interna di
  Instagram vengono distribuiti meglio di un audio già montato nel video

Su **Facebook** non si riscrive niente: è una ripubblicazione dello stesso
contenuto, con lo stesso testo. Per questo la caption è una sola, pensata per
reggere su entrambi.

**Il logo della galleria c'è già** su ogni immagine e su tutta la durata dei
video: non devi aggiungerlo.

**Ogni contenuto esce diverso dal precedente.** I reel hanno cinque stili di
montaggio, post e caroselli quattro impaginazioni: le sceglie Claude in base a
cosa racconti, tu non devi indicarle.

**Le caption sono sempre in italiano e inglese.** Sulle immagini e nei video
invece l'inglese compare solo dove è breve abbastanza da non soffocare la foto:
se ne occupa il comando, non è una scelta da fare ogni volta.

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

## Il carosello attuale — I Luoghi dell'Anima

I sei link pronti da aprire dal telefono, nell'ordine di pubblicazione:

1. https://raw.githubusercontent.com/elenabrilli76-web/BE-Art-Gallery/be-art-gallery-creazione-contenuti/contenuti-social/in-lavorazione/pronti/carosello_01.png
2. https://raw.githubusercontent.com/elenabrilli76-web/BE-Art-Gallery/be-art-gallery-creazione-contenuti/contenuti-social/in-lavorazione/pronti/carosello_02.png
3. https://raw.githubusercontent.com/elenabrilli76-web/BE-Art-Gallery/be-art-gallery-creazione-contenuti/contenuti-social/in-lavorazione/pronti/carosello_03.png
4. https://raw.githubusercontent.com/elenabrilli76-web/BE-Art-Gallery/be-art-gallery-creazione-contenuti/contenuti-social/in-lavorazione/pronti/carosello_04.png
5. https://raw.githubusercontent.com/elenabrilli76-web/BE-Art-Gallery/be-art-gallery-creazione-contenuti/contenuti-social/in-lavorazione/pronti/carosello_05.png
6. https://raw.githubusercontent.com/elenabrilli76-web/BE-Art-Gallery/be-art-gallery-creazione-contenuti/contenuti-social/in-lavorazione/pronti/carosello_06.png

Questi link cambiano contenuto ogni volta che il file viene rifatto: restano
validi finché non chiedi un nuovo carosello, poi questa sezione si aggiorna
con i link del prossimo.
