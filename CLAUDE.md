# BE Art Gallery — contesto per Claude Code

Chi apre una sessione su questo repository legge prima questo file.
Serve a non dover rispiegare ogni volta chi siamo, come parliamo e come si lavora.

Il file è diviso in **tre sezioni**, che si completano via via:

| Sezione | Cosa contiene | Stato |
|---|---|---|
| **1 · Contesto** | dove stanno le cose, come funzionano gli eventi, come si lavora | completa |
| **2 · Chi siamo** | identità, spazio, storia, visione, servizi | prima stesura, dal sito |
| **3 · Voce** | tono, lessico, regole per canale | prima stesura, dal sito |

> Le sezioni 2 e 3 nascono dai testi già approvati del sito `beartgallery.eu`
> e dalle note di progetto. Vanno arricchite con quello che il sito non dice:
> il modo di parlare vero, gli esempi che funzionano, quelli che non funzionano.

---

# 1 · CONTESTO

## Cos'è questo repository

Gli **strumenti e il processo** per produrre i contenuti social della galleria.
Non i materiali: quelli stanno sul Drive.

| Cosa | Dove |
|---|---|
| Foto, logo, depliant, biglietti, video | **Google Drive**, cartella `BE Art Gallery` |
| Codice del sito | repository `be-art-gallery-site` |
| Strumenti, processo e testi | **questo repository** |

Le sottocartelle del Drive che servono più spesso: `Galleria-foto allestita 1`,
`Galleria-foto allestita 2`, `Galleria-foto vuota`, `Logo`,
`Materiale Grafico_Social`, `Depliant`, `Biglietto da Visita`.

> I materiali **non** stanno su GitHub: sono file pesanti e si sfogliano
> meglio dal Drive.

## Gli eventi

Il calendario cambia in continuazione. Quello che **non** cambia è che la CTA
di un contenuto discende dal **tipo** di evento, non dal suo nome.

| Tipo | Chi partecipa | CTA |
|---|---|---|
| **Personale** | un artista, scelto dalla galleria | vieni a visitare |
| **Collettiva su invito** | artisti invitati, chiusa | vieni a visitare — **mai** "iscriviti" |
| **Collettiva aperta** | qualsiasi artista, con iscrizione e scadenza | **iscriviti** fino alla scadenza, poi vieni a visitare |
| **Presentazione, convegno, incontro** | pubblico | vieni · prenota il posto |
| **Performance, evento culturale** | pubblico | vieni a visitare |
| **Evento esclusivo o privato** | su invito | non si comunica prima; semmai un racconto dopo |

### La regola che si sbaglia più spesso

Su una **collettiva aperta**, quando le iscrizioni si chiudono **la CTA cambia**:
da "iscriviti" a "vieni a vedere". È il passaggio che sfugge più facilmente,
perché il contenuto sembra ancora attuale ma sta chiedendo una cosa impossibile.

Finché una collettiva aperta ha le iscrizioni ancora aperte, **è la priorità di
comunicazione**: è l'unico tipo di evento con una scadenza vera, e ogni settimana
persa sono iscrizioni perse.

### Le fasi di ogni mostra

Tutte le mostre attraversano le stesse fasi. Vale per quelle di oggi e per quelle
che verranno:

1. **Annuncio** — cos'è, quando, di chi
2. **Iscrizioni** *(solo collettive aperte)* — dettagli pratici, poi urgenza verso la scadenza
3. **Countdown** — verso l'inaugurazione, sempre più fitto
4. **Inaugurazione** — storie durante, post il giorno dopo
5. **Mostra in corso** — a rotazione: una singola opera, un artista, l'atmosfera
6. **Ultimi giorni** — «prima che chiuda»
7. **Chiusura** — ringraziamento e accenno alla prossima

Le fasi di due mostre diverse **si sovrappongono**: mentre una è in corso, quella
dopo è già in countdown o in raccolta iscrizioni. È normale, e va gestito
alternando i contenuti — non affastellandoli nello stesso post.

### Calendario in corso

> ⚠️ Questa tabella invecchia. Va aggiornata quando un evento finisce o se ne
> aggiunge uno. Le regole qui sopra invece restano valide sempre.

| Evento | Tipo | Date |
|---|---|---|
| **E.B.Art** — Elena Brilli | personale | 29 ago – 6 set 2026 · inaugurazione sab 29/8 h 17 |
| **ArtiAMO** — gruppo AMO.Art | collettiva su invito | 12 – 27 set 2026 · inaugurazione sab 12/9 h 17 |
| **I Luoghi dell'Anima** | collettiva aperta | 10 – 25 ott 2026 · iscrizioni entro il **30 settembre** · consegna opere 7-8/10 |

## Come si lavora

Il processo completo è in [`contenuti-social/PROCESSO.md`](contenuti-social/PROCESSO.md).
In breve: le foto vanno in una cartella, Elena dice cosa vuole, Claude scrive
i testi e il file `contenuto.json`, un comando produce tutto.

```
py strumenti\\crea.py
```

Il comando legge `contenuti-social/in-lavorazione/contenuto.json` e salva reel,
post, caroselli e storie in `in-lavorazione/pronti/`, pronti da pubblicare.

**Quando arriva una richiesta di contenuto**, Claude scrive due file in
`contenuti-social/in-lavorazione/`: `testi.md` con le caption e `contenuto.json`
con le istruzioni per il comando. Le foto restano sul computer di Elena: Claude
non le vede, quindi l'ordine si indica per nome di file.

Nei reel la scaletta può contenere anche spezzoni video, con la durata e il
secondo da cui partire: vedi [`strumenti/README.md`](strumenti/README.md).

Istruzioni complete: [`strumenti/README.md`](strumenti/README.md).

## Riservatezza

Questo repository è **pubblico**. Non vanno messi qui: token di accesso a Meta
o ad altri servizi, la rubrica contatti, dati e indirizzi degli artisti iscritti.
Indirizzo, telefono ed email della galleria si possono scrivere: sono già
pubblicati sul sito.

---

# 2 · CHI SIAMO

## In una riga

**BE Art Gallery & Creative Lab** — galleria d'arte contemporanea e laboratorio
creativo nel centro storico di Pistoia, dove la materia antica di un palazzo
esalta l'arte contemporanea.

## Lo spazio

Settanta metri quadrati su **tre livelli comunicanti**, in un palazzo storico di
via San Pietro 24, **di fronte alla Chiesa di San Pier Maggiore** — romanico
pistoiese, origini longobarde attorno al 748 d.C.

Non è il solito *white cube* asettico. Volte, travi in legno scuro, pareti in
sasso e mattoni, pavimenti in cotto, ringhiere in ferro. Le opere non sono
semplicemente appese: dialogano con l'architettura.

| Livello | Cos'è |
|---|---|
| **Piano d'ingresso** | il doppio volume con la grande parete a vista, la scala in pietra, le lampade sospese |
| **Livello superiore** | il ballatoio affacciato sul vuoto centrale, ringhiera in ferro e cotto: raccolto, per opere di piccolo e medio formato |
| **Sala voltata** | il più suggestivo, quasi ipogeo: installazioni, proiezioni, esposizioni immersive |

## Da dove veniamo

La galleria nasce da **oltre cinque anni di lavoro nel mondo dell'arte**: mostre,
eventi culturali, rassegne con partecipazione da tutta Italia e dall'estero, e la
direzione di un gruppo di **oltre quindici artisti**.

Da lì la convinzione che ha portato a via San Pietro: *l'arte merita una cornice
all'altezza del suo ruolo*.

## La filosofia

L'arte contemporanea, astratta e materica trova la sua massima espressione nel
**dialogo con la storia**. Non l'asetticità della galleria convenzionale, ma un
contrasto vibrante: l'antico e il moderno che si esaltano a vicenda.

Il palazzo non è uno sfondo neutro. È un interlocutore.

## La visione — quattro pilastri

1. **Esporre e valorizzare** — ogni artista ha diritto a uno spazio degno del proprio lavoro
2. **Comunità di artisti** — un gruppo selezionato, seguito con cura, rappresentato con professionalità
3. **Creative Lab** — i laboratori creativi, come le antiche botteghe: si impara facendo
4. **Volano di bellezza** — la galleria come motore culturale per Pistoia e la Toscana

## Cosa offriamo agli artisti

Portfolio d'artista · siti web personali · grafica e identità visiva ·
organizzazione di mostre ed eventi · testi e copywriting · social media e
comunicazione.

L'obiettivo dichiarato è uno solo: **esporre, essere visti, vendere.**

## Dati pratici

- **Indirizzo** — Via San Pietro 24, 51100 Pistoia
- **Telefono / WhatsApp** — +39 377 573 5187
- **Email** — beartgallery.eu@gmail.com
- **Sito** — beartgallery.eu
- **Orari** — su appuntamento e in occasione di mostre ed eventi

## Da completare

- I nomi degli artisti in curatela, quando la selezione è chiusa
- La storia di Elena Brilli / E.B.Art come artista, per i contenuti che la riguardano
- Cosa diventerà il Creative Lab in concreto: quali laboratori, per chi, quando

---

# 3 · VOCE DI BE ART GALLERY

## Chi parla

Parla **la galleria**. Sempre "noi", mai "io".

> «Abbiamo scelto di rispettare l'anima di un palazzo storico.»
> «Selezioniamo lavori capaci di dialogare con lo spazio.»

Questo vale **anche quando la mostra è di Elena Brilli**: in quel caso la galleria
parla dell'artista in terza persona, come farebbe con qualunque altro. È la stessa
distanza curatoriale che rende credibile la selezione — una galleria che si
autocelebra in prima persona vale meno di una galleria che presenta.

Non significa essere impersonali: "noi" è un noi che ha gusti, sceglie e prende
posizione.

## L'essenza

Tre aggettivi: **materico, colto, accogliente.**

Elegante ma diretto, mai pomposo. **Parla d'arte con concretezza toscana.**

Se una frase suona come il comunicato stampa di un ente, è sbagliata. Se suona
come qualcuno che conosce l'arte e ti sta spiegando una cosa a cui tiene,
è giusta.

## Come parliamo

- **Concreti prima che evocativi.** "Settanta metri quadrati su tre livelli"
  vale più di "uno spazio suggestivo".
- **Il contrasto è il nostro tema.** Antico e contemporaneo, materia e segno,
  pietra e colore. Torna in quasi tutto quello che scriviamo — ma va mostrato,
  non annunciato.
- **Mai superlativi vuoti.** Niente "straordinario", "imperdibile", "unico nel
  suo genere".
- **Mai CTA generiche.** «Raccontaci il tuo progetto», non «Scopri di più».
- **A chi legge diamo del tu**, con rispetto.

## Il lessico

| Diciamo | Non diciamo |
|---|---|
| il fascino antico, la materia, il palazzo | location, venue, spazio polifunzionale |
| opere, lavori, ricerca | pezzi, creazioni |
| mostra, personale, collettiva, vernissage | esposizione evento |
| vieni a visitare, passa a trovarci | non mancare, ti aspettiamo (da solo) |
| Raccontaci il tuo progetto | Scopri di più, Clicca qui, Get started |

**Frasi di casa**, già usate e approvate:

> «L'arte contemporanea trova la sua materia.»
> «La materia è la cornice, l'arte è la protagonista.»
> «Ogni appuntamento cambia il volto dello spazio.»
> «Dove la storia esalta il contemporaneo.»

## Regole per canale

|  | Instagram | Facebook |
|---|---|---|
| **Ruolo** | richiamo, atmosfera, riconoscibilità | dettagli pratici e link |
| **Testo** | breve, gancio forte in apertura | più disteso: date, orari, come iscriversi |
| **Link** | solo in bio o negli sticker delle Stories | direttamente nel post |

Ogni contenuto Instagram viene ripubblicato su Facebook nella stessa settimana,
con in più il link diretto.

## Regole non negoziabili

- **Una sola CTA per contenuto.** Mai due link o due azioni diverse. Se ne
  servono due, sono due contenuti.
- **La CTA discende dal tipo di evento**, non dal suo nome: vedi la tabella
  nella sezione Contesto. Un evento su invito non chiede mai un'iscrizione.
- **Quando le iscrizioni chiudono, la CTA cambia.** Da "iscriviti" a "vieni a
  vedere", lo stesso giorno.
- **San Pier Maggiore si cita con misura.** È un dettaglio prezioso, non
  l'argomento principale: la protagonista è l'arte.
- **Niente prezzi o quote nei post** finché non sono confermati.

## Da completare

- Esempi di caption **davvero pubblicate** che hanno funzionato, e di caption
  che non hanno funzionato: sono la guida migliore
- Il set di hashtag di riferimento, una volta trovato quello giusto
- Il tono per il Creative Lab, quando partirà: rivolgersi a famiglie e bambini
  richiede un registro diverso da quello per collezionisti e artisti
