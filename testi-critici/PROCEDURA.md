# Testi critici d'artista — procedura

Testi brevi di presentazione critica per un singolo artista, da usare in una
personale o dentro una collettiva: pannello in sala, scheda A5, catalogo,
pagina del sito. Sono testi **riutilizzabili**: non nominano mostre, date o
luoghi espositivi, così lo stesso testo segue l'artista da una mostra all'altra.

> Non sono contenuti social. Le regole della sezione **Voce** di `CLAUDE.md`
> (il "noi" della galleria, nome, sito, hashtag) qui **non** valgono: il
> soggetto è l'artista, e chi scrive è lo sguardo critico, in terza persona.

---

## Cosa serve

| | |
|---|---|
| **Nome dell'artista** | come vuole comparire |
| **Contesto geografico** | dove vive e lavora — entra nel testo solo se si vede nelle opere |
| **Immagini delle opere** | **minimo 3–5**, rappresentative; meglio se di periodi o serie diverse |

**Nessuna dichiarazione di poetica.** La poetica si ricava dalle opere: è il
lavoro che fa Claude. Se l'artista ne ha una, la si legge dopo, per verifica,
non prima.

### Come far arrivare le immagini

- **allegate in chat**, direttamente nella conversazione con Claude, oppure
- **una cartella sul Drive** (`BE Art Gallery` → una sottocartella per artista),
  indicando a Claude il nome della cartella

Le immagini **non** si caricano su GitHub: il repository è pubblico e le opere
appartengono agli artisti. Qui resta solo il testo.

Se possibile, per ogni opera: titolo, anno, tecnica, misure. Non sono
obbligatori, ma evitano di dover indovinare la tecnica da una fotografia.

---

## Metodo di analisi

Cinque passaggi, nell'ordine. Ogni affermazione del testo finale deve poter
essere indicata con il dito su almeno un'opera.

### 1 · Analisi formale
- tecniche e materiali
- composizione e struttura
- colore e luce
- gestione dello spazio, superficie, formato

### 2 · Estrazione della poetica
- **osservazione sistematica**: cosa si ripete fra le opere — colori, soggetti,
  modi di comporre, gesti
- **interpretazione dall'evidenza**: collegare le scelte formali a possibili
  significati; cercare le tensioni interne (pieno/vuoto, controllo/gesto,
  figura/dissoluzione…)
- **sintesi**: un'ipotesi interpretativa coerente, **verificata su più opere**,
  che resta aperta e non attribuisce intenzioni che le opere non mostrano

### 3 · Linguaggio visivo
- segni e simboli ricorrenti
- stile personale distintivo
- elementi iconografici caratteristici
- relazione fra forma e contenuto

### 4 · Contestualizzazione
- tendenze contemporanee con cui la ricerca dialoga
- **uno, al massimo due** riferimenti ad altri artisti o movimenti: per
  orientare, mai per sminuire né per nobilitare per contagio
- dialogo fra tradizione e innovazione
- il contesto locale solo se è costitutivo delle opere

### 5 · Tematiche
- contenuti ricorrenti dedotti dalle opere
- messaggi impliciti nelle scelte visive
- approccio concettuale che emerge
- relazione con il presente

---

## Il testo

**Lunghezza: 500–600 caratteri, spazi inclusi.** È il formato A5.

| Parte | Caratteri | Cosa fa |
|---|---|---|
| **Apertura** | 100–150 | una frase d'impatto che dica l'essenza della ricerca, come emerge dalle opere |
| **Corpo** | 300–350 | linguaggio visivo, temi dedotti, un elemento tecnico significativo, **un** riferimento contestuale |
| **Chiusura** | 100–150 | cosa rende la proposta riconoscibile e perché conta oggi |

Schema di partenza — da usare come ossatura, non da riempire a stampo:

```
[ARTISTA] sviluppa una ricerca che [CARATTERISTICA DISTINTIVA].
Le sue opere [DESCRIZIONE TECNICA/FORMALE] rivelano [TEMA DEDOTTO],
attraverso [METODO OSSERVATO]. Il dialogo tra [ELEMENTO A] e [ELEMENTO B]
genera [EFFETTO VISIBILE], in sintonia con [RIFERIMENTO CONTEMPORANEO].
La sua pratica [CONCLUSIONE SULLA RICONOSCIBILITÀ].
```

### Come si scrive

- **Chiaro ma non banale.** Niente gergo accademico, niente tecnicismi che
  chiedono un glossario.
- **Verbi attivi**: l'artista costruisce, sottrae, stratifica, interroga.
- **Aggettivi pochi e precisi.** Uno che descrive vale più di tre che lodano.
- **Oggettivo, con spunti interpretativi**: prima ciò che si vede, poi ciò che
  significa. Equilibrio fra le due cose.
- **Nessun giudizio di valore assoluto.** Niente "straordinario", "unico",
  "geniale": la sezione Voce di `CLAUDE.md` vale anche qui.

### Cosa non entra

- mostre specifiche, date, luoghi espositivi
- confronti che sminuiscono l'artista o un altro
- intenzioni non verificabili guardando le opere
- biografia: titoli di studio e premi stanno in una scheda a parte

---

## Checklist prima di consegnare

- [ ] Sta in piedi da solo, senza riferimenti a un contesto espositivo?
- [ ] Lo capisce chi entra in galleria per caso?
- [ ] Dà qualcosa anche a un collezionista o a un addetto ai lavori?
- [ ] È fra 500 e 600 caratteri, spazi inclusi?
- [ ] Coglie ciò che distingue **questo** artista da un altro?
- [ ] Si può riusare in una personale come in una collettiva?
- [ ] Ogni interpretazione è sostenuta da ciò che si vede nelle opere?

---

## Cosa consegna Claude

Un file per artista in [`artisti/`](artisti/), sul modello di
[`artisti/MODELLO.md`](artisti/MODELLO.md), con dentro:

1. **le note di analisi**, opera per opera e poi per sintesi — servono a
   verificare il testo e a riscriverlo in futuro senza ricominciare da zero
2. **il testo critico in italiano**, con il conteggio dei caratteri
3. **la traduzione inglese**, con il suo conteggio — la galleria riceve
   visitatori stranieri; l'inglese può sforare di poco, l'italiano no
4. **una variante breve** (circa 250 caratteri) per didascalie e pannelli
   di collettiva, dove lo spazio per ogni artista è minore

Il nome del file è `nome-cognome.md`, minuscolo, con i trattini.
