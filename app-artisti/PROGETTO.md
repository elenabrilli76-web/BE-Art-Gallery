# App per gli artisti — progetto

Lavoro parallelo ai contenuti social e ai testi critici: un'app per cellulare
dedicata agli artisti, costruita come una **community legata alla galleria**.

> Questo file è la prima stesura del progetto: cosa fa l'app, per chi, con
> quali strumenti e in che ordine. Le decisioni ancora aperte sono in fondo.
> Il codice dell'app **non** starà qui (vedi *Dove sta il codice*).

---

## L'idea in una riga

Lo spazio di via San Pietro, in tasca agli artisti: il posto dove la galleria
li seleziona, li segue, li mette in mostra e li fa parlare fra loro.

Non un social generico. Una **community curata**: è la galleria che accoglie,
come accoglie le opere sulle sue pareti. Coerente con il secondo pilastro della
visione — *un gruppo selezionato, seguito con cura, rappresentato con
professionalità*.

## Perché serve

Oggi il rapporto con gli artisti passa da WhatsApp, email, moduli e Drive.
Funziona, ma:

- le **iscrizioni alle collettive aperte** arrivano sparse, e raccoglierle
  (dati, foto delle opere, scadenze) è lavoro a mano
- gli artisti del gruppo **non hanno un posto comune** dove vedere il
  calendario, condividere il lavoro, sapere cosa succede
- i servizi della galleria (portfolio, sito, grafica, testi, social) **non
  hanno una vetrina** rivolta agli artisti
- i **testi critici** e i dati delle opere che produciamo già in questo
  repository restano in PDF, invece di diventare un profilo vivo

## Per chi

| Chi | Cosa ci fa |
|---|---|
| **Artisti del gruppo** (in curatela) | profilo completo, community, calendario, comunicazioni dalla galleria |
| **Artisti esterni** | si iscrivono a una collettiva aperta, caricano le opere, seguono la mostra |
| **La galleria** | seleziona, pubblica le call, gestisce le iscrizioni, modera, comunica |

Il pubblico (visitatori, collezionisti) **non** è il destinatario della prima
versione: per loro ci sono già il sito e Instagram. Si potrà aprire dopo.

## Cosa fa — prima versione

Poche funzioni, tutte legate alla galleria. Meglio cinque cose fatte bene che
venti abbozzate.

1. **Profilo d'artista** — biografia, testo critico, opere con didascalia.
   Il testo critico e i dati delle opere arrivano da `testi-critici/`, che li
   ha già in forma ordinata.
2. **Le call** — le collettive aperte con iscrizioni attive, in evidenza.
   Si compila l'iscrizione e si caricano le foto delle opere dall'app.
   La regola del calendario vale anche qui: **chiusa la scadenza, il bottone
   "iscriviti" sparisce** e la call diventa una mostra da visitare.
3. **Calendario** — mostre ed eventi della galleria, con le fasi
   (annuncio, inaugurazione, ultimi giorni). Per chi espone: date di
   consegna e ritiro opere.
4. **Bacheca della community** — gli artisti condividono lavori in corso,
   domande, notizie. Moderata dalla galleria; niente pubblico esterno.
5. **Comunicazioni** — notifiche dalla galleria: una call che apre, una
   scadenza vicina, l'allestimento confermato.

### Dopo, se la prima versione funziona

- **Servizi** — richiesta di portfolio, sito, grafica, testi direttamente
  dall'app («Raccontaci il tuo progetto»)
- **Messaggi diretti** fra artisti e con la galleria
- **Creative Lab** — iscrizione ai laboratori, quando partiranno
- **Profili pubblici** visibili dal sito `beartgallery.eu`
- **Vendita** — opere disponibili, richiesta di informazioni

## Come si costruisce — proposta

### Un'app web installabile, non (ancora) un'app da store

La proposta è partire con una **PWA**: un'app web che si installa sul
telefono dall'indirizzo, con l'icona sulla schermata come un'app vera,
notifiche comprese.

| | PWA | App nativa (App Store / Play Store) |
|---|---|---|
| Costi fissi | nessuno | 99 $/anno Apple + 25 $ una tantum Google |
| Pubblicazione | immediata | revisione degli store a ogni aggiornamento |
| Un solo codice per iPhone e Android | sì | sì, con gli strumenti giusti |
| Notifiche | sì (su iPhone dopo l'installazione) | sì |
| Presenza negli store | no | sì |

Per una community chiusa, dove gli artisti arrivano su invito o da un link
della galleria, gli store non servono all'inizio. Se servissero dopo, la
stessa app si impacchetta per gli store (Capacitor) senza riscriverla.

### Gli strumenti

- **Interfaccia**: React con TypeScript, lo stesso carattere del resto
  (Cormorant Garamond) e il linguaggio grafico della galleria — filetto oro,
  cartellino, arco
- **Dati, accessi e foto**: Supabase — database, login, archivio immagini,
  con server in Europa (serve per il GDPR). Il piano gratuito basta per
  partire
- **Pubblicazione**: un hosting statico (Vercel o Netlify), piano gratuito

### Dove sta il codice

In un **repository a parte**, `be-art-gallery-app`, **privato**.

- questo repository è pubblico e contiene strumenti e testi: l'app avrà
  configurazioni, chiavi e dati degli artisti che qui non vanno
  (vedi *Riservatezza* in `CLAUDE.md`)
- lavori separati, storie separate: un cambiamento all'app non deve
  passare in mezzo ai contenuti social

Qui resta solo questo documento di progetto, finché non si sposta.

### Riservatezza e regole

- dati personali degli artisti: solo nel database, mai nel codice
- consenso esplicito al trattamento dei dati all'iscrizione (GDPR)
- le opere caricate restano degli artisti: l'app le mostra, non le cede
- la bacheca è moderata: la galleria può nascondere un contenuto

## In che ordine

| Fase | Cosa | Risultato |
|---|---|---|
| **0 · Decidere** | rispondere alle domande qui sotto | il perimetro chiuso |
| **1 · Disegnare** | le schermate principali, nel linguaggio grafico della galleria | un prototipo da sfogliare sul telefono |
| **2 · Prima versione** | profilo, call con iscrizione, calendario | prova con il gruppo AMO.Art |
| **3 · Community** | bacheca e notifiche | apertura agli artisti delle collettive |
| **4 · Allargare** | servizi, messaggi, Creative Lab | — |

Un primo banco di prova naturale: la **prossima collettiva aperta**. Gestire
le iscrizioni dall'app invece che a mano è il vantaggio più concreto e
più facile da misurare.

## Decisioni aperte

- **Chi entra?** Solo su invito della galleria, o chiunque si iscrive a una
  collettiva aperta? O entrambi, con due livelli?
- **La bacheca**: tutti vedono tutto, o la galleria approva prima di
  pubblicare?
- **L'iscrizione alle collettive** si paga? Se sì, il pagamento passa
  dall'app (e allora servono Stripe e le sue regole) o resta fuori?
- **Il nome dell'app**: *BE Art Gallery*, *BE Artists*, *Creative Lab*…?
- **PWA o store** fin da subito?
- **Chi la usa dalla parte della galleria**: solo Elena, o anche altri?
