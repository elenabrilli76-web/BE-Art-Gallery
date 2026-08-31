# Processo di creazione contenuti — BE Art Gallery

Questo è il processo definitivo. Vale per tutti e quattro i formati:
**reel, post, carosello, storia**.

I primi tre passi sono identici per tutti. Cambia solo il passo 4, la
produzione. Il passo 5, la pubblicazione, cambia solo nei dettagli.

---

## I 5 passi, sempre gli stessi

### Passo 1 — Decidi cosa pubblicare

Guarda il piano editoriale e scegli **un solo** contenuto.

Rispondi a tre domande, e sono le uniche tre che contano:

1. **Di quale evento parla?** (E.B.Art / ArtiAMO / I Luoghi dell'Anima / la galleria in generale)
2. **Cosa deve fare chi lo vede?** — una sola azione. Visitare, iscriversi, salvare la data.
3. **Dove va?** Instagram, Facebook, o entrambi.

> ⚠️ Se ti accorgi di volere due azioni diverse, sono **due contenuti**, non uno.

### Passo 2 — Prepara la cartella di lavoro

Sul computer, dentro il repository:

```
contenuti-social/in-lavorazione/
├── foto/          ← metti qui le foto scelte, rinominate 01.jpg, 02.jpg, 03.jpg…
└── brief.md       ← copia di BRIEF.md, compilato
```

**Le foto:**

- Prendile dal Drive e copiale in `foto/`
- **Rinominale in ordine numerico**: `01.jpg`, `02.jpg`, `03.jpg`… L'ordine dei
  nomi è l'ordine in cui appariranno
- Quante: reel 6–10 · carosello 3–8 · post 1 · storia 1

**Il brief:** copia `BRIEF.md`, rinominalo `brief.md`, compilalo. Ci mettiamo
due minuti e risparmia tre giri di correzioni.

### Passo 3 — Chiedi i testi a Claude

Apri la sessione **Creazione contenuti social** su [claude.ai/code](https://claude.ai/code)
e scrivi:

> Leggi `contenuti-social/in-lavorazione/brief.md` e scrivimi i testi.

Claude conosce già gli eventi, le date e le regole di tono: sono in `CLAUDE.md`.

Ti restituisce, salvato in `contenuti-social/in-lavorazione/testi.md`:

- La **caption** completa, nella lunghezza giusta per il canale
- Gli **hashtag**
- I **testi in sovrimpressione** (per reel, carosello e storia): cosa scrivere e in quale schermata
- La **prima riga**, che è quella che decide se il contenuto viene letto o saltato

Rileggi. Correggi. È più veloce correggere che spiegare da capo.

### Passo 4 — Produci

👉 **Qui le strade si dividono. Vai alla sezione del tuo formato, più sotto.**

### Passo 5 — Pubblica e archivia

1. Pubblica dal telefono (vedi la sezione del formato)
2. Sposta la cartella: da `in-lavorazione/` a `pubblicati/2026-09-15-nome-contenuto/`
3. Svuota `in-lavorazione/` per il contenuto successivo

L'archivio serve: fra due mesi vorrai sapere cosa avevi già scritto.

---

## Passo 4 per formato

### 🎬 REEL — video verticale

**Dove:** sul tuo computer, con lo script. Non serve Canva.

1. Scegli una musica, se la vuoi mettere tu. Altrimenti salta: è **meglio**
   aggiungerla dall'app Instagram al momento di pubblicare, perché i brani
   della libreria interna vengono distribuiti meglio
2. Apri il terminale nella cartella del repository
3. Lancia:

```bash
python3 reel/reel.py \
  --foto contenuti-social/in-lavorazione/foto \
  --out contenuti-social/in-lavorazione/reel.mp4 \
  --titolo "BE Art Gallery" \
  --sottotitolo "Pistoia · Creative Lab" \
  --finale "I Luoghi dell'Anima|Iscrizioni entro il 30 settembre"
```

4. Aspetta: circa 5 secondi di calcolo per ogni foto
5. Guarda il risultato. Non va bene? Cambia le foto o i testi e rilancia:
   costa mezzo minuto

**Se vuoi decidere i testi al secondo esatto** invece di titolo e finale
soltanto, usa un file di progetto: vedi `reel/progetto.esempio.json` e lancia
`python3 reel/reel.py --progetto progetto.json`.

**Cosa esce:** MP4 1080x1920, 9:16, H.264. Otto foto ≈ 21 secondi.

> Sotto i 30 secondi il reel viene guardato fino in fondo molto più spesso.

**Pubblicazione:** manda l'MP4 sul telefono (Drive, AirDrop o Telegram a te
stessa) → Instagram → **+** → Reel → scegli il video → aggiungi la musica
dalla libreria interna → incolla la caption → copertina: scegli un fotogramma
in cui **non** ci sia testo in sovrimpressione → Condividi.

---

### 🖼️ POST — foto singola

**Dove:** Canva. Cinque minuti.

1. Apri Canva → **Crea un design** → **Post Instagram**
2. Sulla sinistra, **Brand** → brand kit **BE Art Gallery**: colori e font
   sono già quelli giusti
3. Trascina dentro la foto
4. Imposta il formato **1080 x 1350** (verticale 4:5): occupa più spazio nel
   feed rispetto al quadrato, quindi si nota di più
5. Aggiungi il testo dal file `testi.md`
6. Scarica in **PNG**

**Pubblicazione:** Instagram → **+** → Post → caption da `testi.md` → Condividi.
Su Facebook lo stesso contenuto, ma con il **link diretto** dentro al testo.

---

### 📚 CAROSELLO — più immagini da sfogliare

**Dove:** Canva.

1. Canva → **Post Instagram**, formato **1080 x 1350**
2. Brand kit **BE Art Gallery**
3. Crea una pagina per ogni schermata. La struttura che funziona:

   | Pagina | Cosa ci va |
   |---|---|
   | 1 | **Il gancio.** Una frase che fa fermare il dito. È l'unica che quasi tutti vedono |
   | 2–7 | Una foto e un'idea per pagina. Mai due concetti nella stessa |
   | ultima | **La CTA.** Una sola azione, scritta grande |

4. Scarica in **PNG**: Canva produce un file numerato per pagina
5. Controlla che l'ordine dei file sia giusto **prima** di caricarli

**Quante pagine:** 4–8. Meno di 3 non è un carosello, più di 8 non arriva
in fondo quasi nessuno.

**Pubblicazione:** Instagram → **+** → Post → **seleziona più elementi** →
scegli le immagini **nell'ordine giusto** (l'ordine di selezione è l'ordine
finale) → caption → Condividi.

---

### 📱 STORIA — verticale, sparisce in 24 ore

**Dove:** Canva, oppure direttamente dal telefono se è una cosa veloce.

1. Canva → **Crea un design** → **La tua storia** (1080 x 1920)
2. Brand kit **BE Art Gallery**
3. Foto a tutto schermo, testo grande e poco
4. **Lascia liberi i bordi**: circa il 15% in alto e il 15% in basso, altrimenti
   il testo finisce sotto il nome del profilo o sotto la barra delle risposte
5. Scarica in **PNG** (o **MP4** se hai messo animazioni)

**Pubblicazione:** Instagram → la tua foto profilo → carica → **aggiungi lo
sticker del link** se serve mandare al sito → Condividi.

> Le Stories sono l'unico posto, oltre alla bio, dove su Instagram puoi mettere
> un link cliccabile. Per la spinta iscrizioni servono a questo.

---

## Riepilogo: cosa fai e dove

| | Reel | Post | Carosello | Storia |
|---|---|---|---|---|
| **Misura** | 1080x1920 | 1080x1350 | 1080x1350 | 1080x1920 |
| **Quante foto** | 6–10 | 1 | 3–8 | 1 |
| **Si produce con** | lo script | Canva | Canva | Canva |
| **Serve il computer?** | sì | no | no | no |
| **Tempo** | ~10 min | ~5 min | ~15 min | ~5 min |
| **Link cliccabile** | no | no | no | **sì** |

## Riepilogo: gli strumenti

| Strumento | A cosa serve |
|---|---|
| **Google Drive** | archivio delle foto e dei materiali |
| **Claude Code** | testi, caption, hashtag, generazione del reel |
| **Canva** (brand kit BE Art Gallery) | post, caroselli, storie |
| **Instagram / Facebook** | pubblicazione, a mano dal telefono |

---

## Domande frequenti

**Posso saltare il brief?** Sì, ma poi i testi arrivano generici e ci metti
più tempo a correggerli che a compilarlo.

**Le foto devono essere ritoccate prima?** No. Lo script ritaglia in verticale
da solo, Canva pure. Serve solo che siano a fuoco e ben esposte.

**Il reel viene male, cosa cambio?** In ordine: le foto (è quasi sempre quello),
poi la durata delle scene (`--durata-scena 2.6` per un ritmo più veloce), poi i testi.

**Posso pubblicare lo stesso contenuto su Instagram e Facebook?** Sì, ed è
previsto dal piano. Ma su Facebook il testo va allungato e ci va il **link
diretto**, che su Instagram non sarebbe cliccabile.
