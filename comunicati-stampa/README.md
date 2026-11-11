# Comunicati stampa

Il ramo di lavoro dei **comunicati alla stampa locale**: annunci di mostre ed
eventi da mandare alle redazioni di Pistoia, distinti dai contenuti social.

| File | Cosa contiene |
|---|---|
| [`testate.md`](testate.md) | le redazioni a cui scrivere, con indirizzo e carattere |
| [`modello.md`](modello.md) | la struttura della mail e del comunicato, già nella voce della galleria |
| `archivio/AAAA-MM-evento.md` | un file per comunicato: testo inviato, data, a chi |
| `archivio/locandine/AAAA-MM-evento/` | le locandine dell'evento, pronte da allegare — sono pubbliche, possono stare qui |
| [`leggi-sito.js`](leggi-sito.js) | legge la pagina eventi del sito e tutte le pagine evento collegate |
| [`pdf.py`](pdf.py) | fa il PDF del comunicato da allegare: `py comunicati-stampa\pdf.py 2026-11-nome-evento` |

## Da dove vengono le informazioni

**Tutte le informazioni sugli eventi si prendono da
[beartgallery.eu/eventi](https://www.beartgallery.eu/eventi)** e dalle pagine
evento collegate. È la fonte fissa: titoli, date, orari, programma, stato delle
iscrizioni. Non si chiedono a Elena, e non si prendono da `CLAUDE.md`, che può
essere rimasto indietro.

Il sito si costruisce con JavaScript: una richiesta semplice della pagina
restituisce solo il titolo. Claude lo legge con il browser:

```
node comunicati-stampa/leggi-sito.js
```

Se il sito e una mail o un appunto dicono cose diverse, vale il sito — e si
segnala la differenza a Elena, perché una delle due va corretta.

**I materiali da allegare** — foto delle opere, locandina, PDF — li dà Elena di
volta in volta. Non stanno sul sito né qui.

## Come si lavora

1. **Elena dice di quale evento si parla.** Claude legge tutto il resto dal sito:
   titolo, tipo, date, inaugurazione, programma, orari. Chiede solo quello che
   il sito non dice.
2. **Claude scrive** il comunicato in `archivio/AAAA-MM-nome-evento.md`, seguendo
   [`modello.md`](modello.md): oggetto, testo della mail, comunicato completo.
3. **Elena dà i materiali da allegare**, controlla e invia dalla mail della galleria, con le foto in allegato.
4. Nel file si segna **quando** è partito e **a chi**: serve per il richiamo e
   per la volta dopo.

> Claude prepara la **bozza in Gmail**, nell'account della galleria, con
> destinatari in Ccn, testo nel corpo e PDF del comunicato già allegato.
> Elena aggiunge foto e locandina, rilegge e invia: l'invio lo fa sempre lei.

> ⚠️ **I link nelle bozze.** Il collegamento con cui Claude crea le bozze
> riscrive ogni indirizzo web facendolo passare da google.com
> (`https://www.google.com/url?q=…`). Per questo la bozza si scrive in HTML,
> con il testo del link pulito; ma il collegamento sotto resta quello di Google.
> **Prima di inviare**, in Gmail si cancellano e si riscrivono a mano i link
> (`www.beartgallery.eu` e la pagina dell'evento): Gmail li ricrea puliti.
> Succede con qualunque formato, anche scrivendo l'indirizzo senza `https://`:
> è un passaggio da fare ogni volta, ed è l'unico. Le email restano pulite.

## Cosa si allega

| Allegato | Chi lo fa | Note |
|---|---|---|
| **il comunicato in PDF** | Claude, con `pdf.py` | una pagina, con logo e carattere della galleria |
| **la locandina in JPG** | Elena, una volta: poi sta in `archivio/locandine/` | anche il PDF va bene, ma molti siti pubblicano solo immagini |
| **2–3 foto delle opere** | Elena | nominate `cognome-titolo.jpg`, sotto i 3 MB l'una; meglio una verticale e una orizzontale |
| *una foto della galleria allestita* | Elena, dal Drive | se c'è: dice ai giornali dove siamo meglio di qualunque frase |

In tutto **sotto i 10 MB**: tante redazioni respingono le mail più pesanti.
Niente cartelle compresse e niente link a WeTransfer al primo invio: i
giornalisti aprono quello che hanno davanti.

## I tempi

| Quando | Cosa |
|---|---|
| **10–14 giorni prima** | il comunicato completo, con foto |
| **2–3 giorni prima** | un richiamo breve, solo a chi non l'ha pubblicato |
| **la sera dell'inaugurazione o il giorno dopo** | 2–3 foto della serata, con una riga di testo — a La Nazione anche su WhatsApp |

Per una **collettiva aperta** si manda un comunicato in più, all'apertura delle
iscrizioni: è l'unico momento in cui la stampa porta artisti, non visitatori.

## Le regole

Il comunicato **non** è un post. Della sezione Voce di `CLAUDE.md` valgono il
lessico, la concretezza e il divieto di superlativi; **non** valgono il "tu",
gli hashtag e l'inglese.

- **Terza persona.** Il comunicato parla *della* galleria («BE Art Gallery
  presenta…»), perché il giornalista deve poterlo riprendere così com'è. La mail
  di accompagnamento invece è nostra: "noi".
- **Solo italiano.** Sono testate locali.
- **Le cinque W nel primo paragrafo.** Chi, cosa, dove, quando, perché. Chi legge
  solo quello deve avere tutto quello che serve per scrivere la notizia.
- **Il testo nel corpo della mail**, non solo in allegato: le redazioni copiano
  e incollano, e un allegato non aperto è un comunicato non letto.
- **Niente aggettivi da ente.** Non «appuntamento culturale di rilievo», non
  «evento imperdibile»: si dice cosa si vede e dove, e il resto lo decide la
  redazione.
- **Orari veri**, quelli del sito: non un orario inventato.
- **Ingresso, prezzi, quote** solo se confermati.
- **Le foto**: 2–3, orizzontali e verticali, sotto i 3 MB l'una, rinominate
  `cognome-titolo-opera.jpg`. Si indica il credito da citare
  («courtesy l'artista e BE Art Gallery»), non «libere da diritti»: i diritti
  delle opere sono degli artisti.
- **San Pier Maggiore** una volta sola, per dire dove siamo.
- **Una notizia per comunicato.** Due mostre, due comunicati.
