# DONNE: Femminile Plurale — note di mostra

> Il file di lavoro della galleria per la collettiva: cosa sappiamo, le opere
> arrivate, le prime letture. I testi critici si scrivono solo per gli artisti
> che Elena indica. Materiali: Drive, cartella della mostra, una sottocartella
> per artista. Le immagini restano sul Drive.

## La mostra

| | |
|---|---|
| **Titolo** | DONNE: Femminile Plurale |
| **Tipo** | mostra collettiva |
| **Date** | 14 novembre – 13 dicembre 2026 |
| **Inaugurazione** | sabato 14 novembre 2026, ore 17:00 |
| **Claim** | «Infinite sfaccettature, un'unica grande forza.» |
| **Parole chiave** | identità · memoria · relazioni · autonomia · cura |
| **Highlight della mostra** | una collettiva di un mese dedicata all'immensa complessità del mondo femminile: infinite sfaccettature, un'unica grande forza |

## L'evento che la contiene

**Siamo Donne — oltre la violenza c'è di più.**
Arte, parola e presenza contro la violenza di genere: un progetto che parte
dall'arte e arriva alla parola, per aprire nel cuore storico di Pistoia uno
spazio di ascolto, consapevolezza e presenza.
Mostra · letture condivise · incontri editoriali.

| Data | Ora | Appuntamento |
|---|---|---|
| sab 14 nov | 17:00 | inaugurazione |
| sab 21 nov | 18:30 | Cristina Mensi |
| mer 25 nov | 21:30 | Violenze Anonime — è la Giornata internazionale contro la violenza sulle donne |
| sab 28 nov | 18:30 | Violenze Anonime |
| sab 5 dic | 18:30 | Serena Pisaneschi |
| dom 13 dic | 18:00 | chiusura |

I due concept grafici (locandina della mostra e dell'evento) condividono il
profilo femminile fra veli d'acquerello e fili d'oro: terracotta, rosa,
salvia e blu polvere.

---

## Grafica di sala — approvata da Elena il 6 novembre 2026

Una pagina A4 per artista, prodotta con `py strumenti\sala.py donne-femminile-plurale`
in `testi-critici/mostre/donne-femminile-plurale/schede.pdf`. Stesso impianto
delle pagine finali di *I Luoghi dell'Anima*, con i colori della locandina.

- in alto: **DONNE: FEMMINILE PLURALE** in maiuscoletto oro, sotto «Mostra
  collettiva · 14 novembre – 13 dicembre 2026» in corsivo terracotta
- il **nome dell'artista**, senza città, e il filetto d'oro
- il **testo critico solo in italiano**
- sotto, nella stessa pagina, la **didascalia di ogni opera** (titolo, dati,
  testo), su due colonne se le opere sono più d'una
- piede con marchio e indirizzo della galleria; a destra la fascia di veli
  della locandina (`catalogo/foto/donne-femminile-plurale/fascia.jpg`, in locale)
- colori: carta `#F2E5D5`, inchiostro `#212B2D`, terracotta `#8C3A1E`,
  oro `#A8844A`, grigio `#6E6560`; carattere Cormorant Garamond
- **niente cartellino A6 e niente inglese** per questa mostra
- **una scheda separata per ogni artista**: un PDF ciascuno in
  `donne-femminile-plurale/artisti/` (decisione di Elena, 9 novembre 2026)

**Fogli di sala divisi, catalogo unito** (Elena, 10 novembre): quando le opere
di un artista stanno in punti diversi della galleria, i fogli di sala si
dividono (campo `"foglio"`; per ora Massai: quadri, omaggio a Picasso, scultura; E.B.Art: i cinque ritratti insieme, Holy Mother of Gaza e J'accuse insieme, le altre una per foglio; Mazzanti: Fuga da Kandahar, L'agguato e Com'eri vestita? insieme, Basta e Attesa insieme, Ecce domina a sé; Santi: Mater e La sposa appesa insieme, Hotel, Relic e Sirene ciascuna a sé). Nella
presentazione generale e nel catalogo finale invece le opere di ogni artista
stanno **tutte insieme**, in una sola sezione.

**Presentazione e pannello di sala** (Elena, 12 novembre) — `py strumenti\presentazione.py`:
- `presentazione.pdf`: in copertina la locandina a pagina piena, poi il testo
  della mostra, poi una pagina per artista con tutte le didascalie insieme
- `pannello-sala.pdf`: **il testo della mostra per intero**, non riassunto, su
  **due facciate** da appendere in sala: due colonne, fascia stretta, in fondo
  gli artisti in mostra e la riga di *Siamo Donne*. Si può stampare anche in A3

## Artisti e opere arrivate

Stato al 6 novembre 2026. Nessun testo ancora scritto: si aspetta l'indicazione
di Elena su per chi procedere.

| Artista | Opere | Dati forniti | Note |
|---|---|---|---|
| **Patrizia Vangelisti** — Lucca, già in archivio | trittico «Lasciar andare»: *Circe*, *Calipso* (tecnica mista su tela — acrilico, pastelli a olio, grafite — 60 × 60 cm, 2026); *Geisha* (scultura di oggetti di recupero, cartapesta e acrilico, h 36,5 cm, Ø 16 cm, 2026) | completi | ha mandato una descrizione delle opere: archetipi dell'Odissea, donne che trattengono e lasciano andare; la Geisha fa da legame fra i due dipinti |
| **Catia Massai** — Prato, già in archivio | *Due sguardi* (grafite su carta, 33 × 48, cornice 40 × 50) · *Marie-Thérèse – omaggio a Picasso* (acrilico su tela, 40 × 50) · *Sensualità* (matite su cartoncino nero, 22 × 33, cornice 30 × 40) · *La ragazza con la pistola* (acrilico su tela, 40 × 60) · un rilievo con la scritta «NO!» | titoli e misure delle prime quattro | il rilievo «NO!» (busto, pizzo bianco, cuore rosso, su tavola) non è nell'elenco: titolo, tecnica e misure da chiedere. *Due sguardi* riporta a mano un brano di Oriana Fallaci («Essere donna è così affascinante…», da *Lettera a un bambino mai nato*) |
| **Maria Cristina Andreini** — Prato, già in archivio | *Ragazza con velo azzurro* (olio su tela, 21 × 30) · *Ragazza occhi verdi* (30 × 20) · *Ragazza con copricapo viola* (30 × 40) · *Giovane donna occhi grigi* (30 × 40) | misure del dipinto e con cornice | l'abbinamento foto–titolo è dedotto da soggetto e proporzioni: da confermare. Nota sua: «gli occhi delle donne parlano… basta saper leggere» |
| **Maria Maselli** | quadrittico *Femmes au marché*: *Esmeralda*, *Il flauto magico* (olio su tela, 30 × 40); *Il cesto di fiori*, *Il cesto di pere* (35 × 45) | completi | vendibili insieme o singolarmente; i titoli citano lirica e letteratura (Mozart, Victor Hugo). Città e anni: si lasciano fuori (Elena, 9 novembre). Le opere le porta Cristina Andreini |
| **Donatella Bucchieri** | *Petali di coraggio* · *Oltre il genere: Noi* · *Ecosistema interiore* | titoli | ha mandato un commento alle opere. Tecnica a colore versato (pouring) per due tele; *Noi* con foglia d'oro e mandala. Misure, anno e città da chiedere |
| **Gabriella Lo Cascio** | *Sono circondata di Rosso* (olio) | titolo, tecnica, misure | una sola opera |
| **Grazia Barbieri** | *Caterina* | solo titolo | una sola opera; tecnica, misure e anno da chiedere |

Per Vangelisti, Massai e Andreini le presentazioni in archivio nascono dalle
opere di *I Luoghi dell'Anima* e raccontano un'altra parte del loro lavoro:
con le opere nuove vanno riviste, non solo completate.

---

## Poetiche in memoria

Il materiale per il testo di presentazione della mostra, che si scrive alla
fine, quando tutti gli artisti sono analizzati. Per ciascuno: la poetica in
una riga, cosa porta in mostra, con chi dialoga. I testi completi sono nelle
cartelle `testi-critici/artisti/…`; le pagine di sala in
`testi-critici/mostre/donne-femminile-plurale/schede.pdf`.

| Artista | Stato |
|---|---|
| Patrizia Vangelisti | analizzata il 9 novembre — presentazione v2 e 3 didascalie |
| Maria Maselli | analizzata il 9 novembre — presentazione e 4 didascalie |
| Maria Cristina Andreini | analizzata il 9 novembre — presentazione v2 e 4 didascalie |
| Donatella Bucchieri | analizzata il 9 novembre — presentazione e 3 didascalie |
| Catia Massai | analizzata il 9 novembre — presentazione v2 e 6 didascalie |
| Federica Barletta | analizzata il 9 novembre — presentazione provvisoria (un'opera) e 1 didascalia |
| Roberta Grillanda | analizzata il 9 novembre — presentazione provvisoria (un'opera) e 1 didascalia |
| Manuela Romanelli | analizzata il 9 novembre — presentazione provvisoria (due opere) e 2 didascalie |
| Sipontina Paloscia | analizzata il 9 novembre — presentazione provvisoria (due opere) e 2 didascalie |
| Gabriella Lo Cascio | analizzata il 9 novembre — presentazione provvisoria (un'opera) e 1 didascalia |
| Grazia Barbieri | analizzata l'11 novembre — presentazione e 1 didascalia |
| Enzo Mazzanti | analizzato l'11 novembre — presentazione v2 e 5 didascalie |
| Marco Santi | analizzato l'11 novembre — presentazione e 5 didascalie |
| Innocenzo Melani | due stampe (cartella «extra»), 12 novembre — presentazione e 2 didascalie, titoli proposti |
| E.B.Art | 12 novembre — presentazione e 14 didascalie, *Rosaspina* compresa |

Serena D'Onofrio non è in mostra (Elena, 12 novembre): gli artisti sono 15.

### Patrizia Vangelisti — ricomporre, lasciar andare

- **Poetica**: costruisce per incastri — due nature in un volto, cocci in una
  figura — e ne fa il racconto di un passaggio emotivo. Qui il passaggio è il
  distacco: trattenere e lasciar andare.
- **In mostra**: il trittico «Lasciar andare», in quest'ordine — *Circe*
  (metà leone, metà donna), *Geisha* al centro (scultura di cocci ricomposti
  sotto la cartapesta), *Calipso* (profilo sereno e sguardo teso, il cigno
  che si piega).
- **Parole chiave della mostra che tocca**: autonomia, relazioni, cura.
- **Dialoga con**: Maselli per il mito e la letteratura come specchio (Odissea
  da una parte, Hugo e Mozart dall'altra); con la ferita che si ricompone
  (Bucchieri, i tagli d'oro di *Noi*).
- **Frase da tenere**: la ricomposizione come gesto di cura.

### Maria Maselli — la donna del mercato come protagonista

- **Poetica**: porta la quotidianità femminile nel linguaggio della pittura
  antica — fondi scuri, velature, natura morta — e dà a figure popolari la
  dignità della scena teatrale. Dentro la posa, ognuna si prende un momento
  interiore.
- **In mostra**: il quadrittico *Femmes au marché* — *Il cesto di pere*,
  *Il cesto di fiori*, *Il flauto magico*, *Esmeralda*.
- **Parole chiave**: identità, memoria (la tradizione pittorica), cura.
- **Dialoga con**: Barbieri (realismo di tradizione, la posa come potere);
  Andreini (lo sguardo che si sottrae o che interroga); Vangelisti (figure
  letterarie e mitiche).
- **Frase da tenere**: la scena quotidiana si fa teatro, e ogni donna ne è la
  protagonista; *Il cesto di fiori* «non si lascia guardare, interroga».

### Maria Cristina Andreini — lo sguardo che parla

- **Poetica**: racconta la donna per sottrazione — o nasconde il volto e lascia
  parlare il corpo, o copre la bocca e lascia parlare gli occhi. Un'emozione da
  leggere, mai dichiarata.
- **In mostra**: quattro ritratti ravvicinati di ragazze velate — *Ragazza con
  velo azzurro*, *Ragazza occhi verdi*, *Ragazza con copricapo viola*,
  *Giovane donna occhi grigi*.
- **Parole chiave**: identità, autonomia.
- **Dialoga con**: è il cuore del tema dello sguardo, che attraversa tutta la
  mostra (Barbieri, il volto di *Noi* di Bucchieri); *Ragazza occhi
  verdi*, con la mano alzata e la bocca coperta, è l'immagine più vicina al
  senso dell'evento: un silenzio imposto che lo sguardo rifiuta.
- **Frase da tenere**: gli occhi delle donne parlano, basta saper leggere
  (dalla nota dell'artista).

### Donatella Bucchieri — la ferita che fiorisce

- **Poetica**: lascia che il colore versato trovi da sé la sua forma — cellule,
  venature, correnti — e accanto dipinge il volto, attraversato da fratture
  d'oro. Sempre la stessa idea: ciò che è ferito o caotico si trasforma e
  fiorisce.
- **In mostra**: *Petali di coraggio* (rosso che esplode dal nero, piccolo
  formato), *Oltre il genere: Noi* (volto androgino su turchese, oro e
  mandala, una parte che manca), *Ecosistema interiore* (verdi fluidi, il
  paesaggio della mente).
- **Parole chiave**: identità, cura, autonomia.
- **Dialoga con**: Vangelisti (la ricomposizione: i cocci della *Geisha*, le
  fratture d'oro di *Noi*); Andreini (lo sguardo frontale che segue chi
  passa); Lo Cascio (il rosso). È l'unica voce astratta finora: allarga il
  «plurale» dei linguaggi.
- **Frase da tenere**: la ferita diventa forza; il «Noi» che completa la parte
  mancante del volto — chi guarda è chiamato dentro l'opera.

### Catia Massai — citare per dire di sé

- **Poetica**: cambia linguaggio a seconda di ciò che deve dire e usa i
  modelli (Picasso, Oriana Fallaci, il pop) come voci con cui dialogare. Il
  filo è il corpo femminile e la libertà di decidere di sé.
- **In mostra**: *Due sguardi* (nudo a grafite con le parole di Fallaci),
  *Marie-Thérèse – omaggio a Picasso*, *Sensualità* (matite su nero, datata
  8 marzo 2026), *La ragazza con la pistola* (pop anni Sessanta), *NO!*
  (piccola scultura in terracotta con applicazioni: busto con pizzo, cuore
  rosso e la scritta a mano).
- **Parole chiave**: identità, autonomia.
- **Dialoga con**: Maselli e Vangelisti (le donne dei racconti: qui Picasso e
  Fallaci); Andreini (il corpo e lo sguardo come linguaggio); è la voce più
  diretta sul tema della violenza.
- **Frase da tenere**: il NO! scritto a mano — il rifiuto più semplice, quello
  che ogni violenza finge di non sentire.

### Federica Barletta — le madri antiche e il posto vuoto

- **Poetica**: scene oniriche con la forza del rito; figure femminili arcaiche,
  simili alle Veneri preistoriche, potenti e giudicanti, insieme grembo e
  minaccia. Interroga l'origine dell'identità femminile: potenza generativa,
  giudizio, rinascita. (Provvisoria: un'opera sola.)
- **In mostra**: *Concistoro delle madri* — otto madri gravide attorno a una
  tavola in una stanza rosso sangue, una porta aperta sulla luce, una sedia
  vuota per chi guarda.
- **Parole chiave**: identità, memoria, relazioni, cura.
- **Dialoga con**: Vangelisti e Maselli (archetipo e mito); Bucchieri
  (trasformazione, rinascita); Bucchieri ancora, per il «Noi» che chiama chi
  guarda dentro l'opera — qui la sedia vuota.
- **Filo nuovo**: il **giudizio fra donne**, quando si fa proprio lo sguardo
  degli altri; e il suo rovescio, la sorellanza. Delicato: con misura.
- **Frase da tenere**: una sedia resta vuota, ed è per chi guarda.

### Roberta Grillanda — un occhio, tutte le donne

- **Poetica**: ingrandisce un dettaglio fino a farlo paesaggio; l'acquerello
  sciolto in velature e fermato da linee sottili. (Provvisoria: un'opera.)
- **In mostra**: *Gli occhi delle donne* (2026, acquerello) — un solo occhio
  che riempie il foglio: sopracciglio come montagne, iride come mare, ombra
  come campagna. Dal cartoncino dell'artista: «tutte assieme unite
  combatteremo per la nostra libertà».
- **Parole chiave**: identità, autonomia, relazioni.
- **Dialoga con**: Andreini e la nota «gli occhi delle donne parlano» — lo
  stesso titolo, quasi; Bucchieri (*Noi*). È l'immagine più
  vicina al claim: il plurale in un solo sguardo.
- **Frase da tenere**: lo sguardo di una diventa lo sguardo di tutte.

### Manuela Romanelli — la casa che non protegge

- **Poetica**: interni domestici in blu, viola e rosso, dove la donna sta ai
  margini, in controluce, più spenta degli oggetti che la circondano. Una
  tensione taciuta. (Provvisoria: due opere, nessun testo dell'artista.)
- **In mostra**: *Controluce* (la donna in grigi e blu sul bordo di una
  poltrona rossa, lo sguardo in allarme), *Controluce 2* (divano blu vuoto,
  porta rossa, oltre la soglia una donna in sottoveste piegata, di spalle).
- **Parole chiave**: relazioni, cura (mancata), identità.
- **Dialoga con**: Barletta (la stanza rossa), Andreini e Grillanda (lo
  sguardo), Lo Cascio (il rosso che avvolge).
- **Per il tema**: la voce più trattenuta — la casa come luogo dove la
  violenza accade, senza mostrarla. L'aggancio è nei colori: «i colori di un
  livido».
- **Frase da tenere**: la casa, che dovrebbe essere riparo.

### Sipontina Paloscia — non mi faccio cancellare

- **Poetica**: figure in grigio e colore riservato al segno; l'oggetto
  quotidiano e la scritta a mano come voce. Identità e autonomia dette in prima
  persona, senza chiedere permesso. (Provvisoria: due opere.)
- **In mostra**: *Scarpe rosse* (2014, olio) — la donna in grigi e blu, una
  rosa e le scarpe rosse; *Nessuno mi può comandare* (2021, tecnica mista) —
  rotelle di correttore incollate attorno a un volto, e le scritte «io sono
  viva», «non mi faccio cancellare», «decido da sola».
- **Parole chiave**: identità, autonomia.
- **Dialoga con**: Massai (*NO!*, la parola scritta sul corpo), Andreini
  (*Ragazza occhi verdi*), Romanelli (la figura spenta di colore).
- **Per il tema**: le scarpe rosse sono il simbolo del 25 novembre; qui
  ai piedi di una donna viva. È la voce più esplicita, con *NO!*.
- **Frase da tenere**: l'oggetto che cancella diventa il modo per restare.

### Gabriella Lo Cascio — il rosso che avvolge

- **Poetica**: gesto e colore prima del disegno; pennellate d'olio a vortice,
  un rosso quasi unico, il volto in pochi segni. (Provvisoria: un'opera.)
- **In mostra**: *Sono circondata di rosso* (olio) — la donna a
  occhi chiusi, capo chino, avvolta da un vortice rosso.
- **Parole chiave**: identità, relazioni.
- **Dialoga con**: Romanelli (la donna chiusa nello spazio colorato),
  Barletta (la stanza rossa), Paloscia e Massai (il rosso come segno).
- **Per il tema**: opera aperta — il rosso può essere passione o assedio,
  abbraccio o prigione. Non va chiusa in una lettura sola.
- **Frase da tenere**: passione che scalda o qualcosa che stringe.

### Grazia Barbieri — la regina che vince la partita

- **Poetica**: realismo al limite dell'iperrealismo, impianto del ritratto
  antico, volti e gesti di oggi; spesso nomi di donne del mito e della storia.
  Lo sguardo è sempre diretto.
- **In mostra**: *Caterina* — Caterina Sforza con corona e velluto blu, una
  donna di oggi; sotto la sua mano il re degli scacchi è caduto.
- **Parole chiave**: identità, autonomia, memoria.
- **Dialoga con**: Maselli (il ritratto antico), Vangelisti e Massai (le
  donne della storia e del mito), Andreini e Grillanda (lo sguardo).
- **Per il tema**: la partita vinta — il potere che passa di mano.
- **Frase da tenere**: la partita l'ha vinta lei.

### Enzo Mazzanti — dipingere per prendere posizione

- **Poetica**: gesto espressionista, materiali poveri (lamiera ossidata, una
  finestra vera), il rosso come segno. Dal viandante solitario alla
  denuncia: la stessa attenzione per chi resta solo. L'unica voce maschile
  della mostra.
- **In mostra**: *Basta* (donna velata, la mano rossa e la scritta),
  *L'agguato* (su lamiera: la donna bianca di spalle, l'ombra nera
  dell'uomo), *Attesa* (dipinta dentro una finestra; la
  storia vera della donna del Galleno che aspettò tutta la vita il
  fidanzato partito per la guerra), *Com'eri vestita?* (la donna che torna a
  casa dopo la violenza, scalza, con le scarpe rosse in mano), *Fuga da Kandahar* (la ragazza dal velo rosso davanti al deserto al tramonto, 2021), *Ecce domina* (l'Ecce homo volto al femminile: la donna senza volto davanti a una croce di luce).
- **Parole chiave**: relazioni, memoria, autonomia.
- **Dialoga con**: Paloscia (le scarpe rosse), Andreini (la mano alzata),
  Romanelli (la casa e la soglia), Massai (la parola scritta: *NO!* e *BASTA*).
- **Per il tema**: la voce più esplicita, con Massai e Paloscia.
- **Frase da tenere**: il quadro rimanda la domanda a chi la pone.

### Marco Santi — sacro e profano

- **Poetica**: realismo levigato, quasi fotografico, caricato di simboli; il
  sacro (pala, reliquia, Madonna) riportato al corpo femminile, con ironia.
- **In mostra**: *Mater* (la madre come Madonna del parto laica), *La sposa
  appesa* (la sposa che precipita), *Hotel* (la signora anni Venti in
  pelliccia), *Relic* (il perizoma-reliquiario), *Sirene* (due donne nella
  vasca: la sorellanza).
- **Parole chiave**: identità, relazioni, cura.
- **Dialoga con**: Barletta (le madri, il giudizio / qui la sorellanza),
  Barbieri (il ritratto in posa), Mazzanti (l'altra voce maschile).
- **Frase da tenere**: le sirene non sono più una trappola per marinai, ma
  un patto di sorellanza.

### Innocenzo Melani — l'attesa romantica (stampe)

- Due stampe d'arte, non originali: donne in bianco con cappello di paglia e
  fiori, accanto a una gondola, a spatola in rosa e azzurri. Firma «ML».
- Il registro più lieve della mostra: la donna dell'attesa e del ricordo,
  un'immagine ideale che fa da contrappunto alle voci di denuncia.
- **Dialoga con**: *Attesa* di Mazzanti (la stessa attesa, rovesciata in
  dolore), Maselli e Santi (la donna in posa).

### E.B.Art — il metamorfismo emotivo

- **Poetica**: la stessa emozione che cambia forma — linea nera, oro,
  pattern, tela stropicciata. Al centro sempre una donna, fragile e indomita.
- **In mostra**: cinque ritratti (*Madama*, *Gold Butterflies and me*,
  *Flower in the hair*, *Belle époque*, *Mother in war*); il dittico di
  denuncia (*Holy Mother of Gaza*, *J'accuse*); e *Nonostante*, *Notte nel
  deserto*, *Red passion*, *Resilienza*, *Turning page*, *I can hardly
  express*, *Rosaspina*.
- **Per il tema**: la denuncia (Gaza, Afghanistan, Ucraina) e la resistenza
  (*Nonostante*, *Resilienza*, *Turning page*).
- **Frase da tenere**: e, nonostante tutto, resiste.
- La galleria ne parla in terza persona, come di ogni artista.

## Il tono e i riferimenti — per il testo di mostra e le prossime schede

**Il tono** (Elena, 11 novembre): evocativo, non descrittivo. Chi legge ha
l'opera davanti; il testo gli dà un appiglio e una risonanza, non un
inventario. Modello: la didascalia di *Com'eri vestita?* di Mazzanti. Le
didascalie già scritte restano come sono.

**È critica d'arte da galleria, non un libro di scuola** (Elena, 11
novembre): niente spiegazioni, date e nozioni messe in fila. I riferimenti
si evocano come fa un critico che li dà per condivisi con chi legge — un
nome, un'immagine — e il testo resta asciutto, colto, emotivo.

**I riferimenti**: pittori, stili e poetiche note con cui le opere
dialogano — da usare nel testo della mostra, uno o due per volta, e nelle
schede dei prossimi artisti. Mai come etichetta, sempre come risonanza.

| Artista | Riferimenti possibili |
|---|---|
| Vangelisti | il mito omerico riletto al femminile, da Madeline Miller (*Circe*) a Margaret Atwood (*Il canto di Penelope*); i volti doppi del surrealismo; il riuso e l'assemblaggio (Louise Nevelson) |
| Maselli | la pittura di genere del Seicento, le popolane di Caravaggio e Murillo; Vermeer per la luce raccolta |
| Andreini | il ritratto «parlante» per sguardi, fino alla *Ragazza afghana* di Steve McCurry |
| Bucchieri | il kintsugi, l'arte di riparare con l'oro; l'action painting e il dripping (Pollock), qui reso fluido |
| Massai | Picasso e Marie-Thérèse (*Il sogno*, 1932); Oriana Fallaci; la Pop Art e il cinema anni Sessanta; per *NO!* la scultura come corpo-messaggio (Louise Bourgeois) |
| Barletta | le Veneri paleolitiche (Willendorf); la «grande madre» di Marija Gimbutas; il surrealismo onirico (Leonora Carrington, Remedios Varo); l'Ultima Cena rovesciata al femminile |
| Grillanda | il dettaglio ingrandito di Georgia O'Keeffe; l'occhio-paesaggio del surrealismo (Magritte, *Il falso specchio*) |
| Romanelli | le stanze di Edward Hopper e di Vilhelm Hammershøi: donne sole in interni silenziosi |
| Lo Cascio | l'espressionismo del colore (i Fauves, Munch per l'emozione che avvolge la figura) |
| Paloscia | le *Zapatos Rojos* di Elina Chauvet, origine del simbolo delle scarpe rosse; la parola scritta nell'arte femminista (Barbara Kruger) |
| Barbieri | il ritratto rinascimentale di corte; Caterina Sforza; l'iperrealismo; Artemisia Gentileschi per le eroine (Giuditta) che ricorrono nel suo lavoro |
| Santi | la Madonna del parto di Piero; le bagnanti di Degas; il sacro-profano di Pierre et Gilles |
| Mazzanti | i materiali poveri dell'Arte povera e di Burri (la lamiera ossidata); il manifesto di denuncia; *What Were You Wearing?*, la mostra che raccoglie gli abiti delle sopravvissute |

## Il tema trasversale: la violenza contro le donne

Indicazione di Elena (9 novembre): la violenza contro le donne attraversa
diverse opere ed è il tema che lega la mostra all'evento *Siamo Donne —
oltre la violenza c'è di più* e al **25 novembre, Giornata internazionale per
l'eliminazione della violenza contro le donne**. Nel testo di mostra va
detto con misura: le opere non illustrano la violenza, rispondono.

Appunto di lavoro per il testo della mostra — **non** da mostrare come elenco:

| Opera | Artista | Come lo porta |
|---|---|---|
| *NO!* | Massai | il rifiuto scritto sul corpo esposto; i segni rossi sul ventre — l'opera manifesto del tema |
| *Ragazza occhi verdi* | Andreini | la bocca coperta, la mano alzata: un silenzio imposto che lo sguardo rifiuta |
| *Petali di coraggio* | Bucchieri | il piccolo formato di chi si è sentita ferita e rimpicciolita, e rifiorisce |
| *Oltre il genere: Noi* | Bucchieri | le fratture del pregiudizio rese d'oro: la ferita che diventa forza |
| *Due sguardi* | Massai | le parole di Fallaci: battersi perché un'intelligenza sia ascoltata |
| *La ragazza con la pistola* | Massai | la difesa, con ironia: i ruoli rovesciati |
| il trittico «Lasciar andare» | Vangelisti | la relazione senza possesso: Circe non cerca sottomissione, Calipso rinuncia a trattenere |
| *Controluce*, *Controluce 2* | Romanelli | la casa che non protegge, la donna ai margini; blu, viola e rosso come un livido |
| *Scarpe rosse* | Paloscia | il simbolo delle donne uccise, ai piedi di una donna viva |
| *Nessuno mi può comandare* | Paloscia | la risposta in prima persona: non mi faccio cancellare |
| *Basta*, *L'agguato*, *Com'eri vestita?*, *Attesa* | Mazzanti | la denuncia diretta; la minaccia che segue; la domanda rivolta alle vittime; l'attesa di una vita |
| *Il cesto di fiori* | Maselli | lo sguardo che non si lascia guardare, ma interroga |

**Dove sta il tema — decisioni di Elena del 9 novembre.**
- le **presentazioni degli artisti non si toccano**: sono riutilizzabili e
  per alcune ricerche la violenza non è il centro
- **nessuna opera va distinta dalle altre** come «opera sul tema»: sarebbe
  divisivo. Le didascalie descrivono ciascuna la sua opera e restano come sono;
  la tabella qui sopra è solo un appunto di lavoro per il testo della mostra,
  non un elenco da mostrare
- il tema sta nel **testo di presentazione della mostra**, che dice che queste
  opere, accostate, rispondono alla violenza senza illustrarla, e lega la
  mostra al 25 novembre e a *Siamo Donne*
- e nelle **due pagine di presentazione della mostra** che vanno in sala:
  lì il testo, e lì anche la riga «Siamo Donne — oltre la violenza c'è di
  più · 25 novembre, Giornata internazionale per l'eliminazione della violenza
  contro le donne» (voce `riga_presentazione` nella scheda della mostra).
  **Non** nelle schede dei singoli artisti (Elena, 9 novembre).

**L'arco del racconto**: dalla ferita (*NO!*, *Petali di coraggio*) alla
risposta — lo sguardo che non si abbassa, il corpo che si riprende, la
relazione libera — fino alla forza plurale del claim: «Infinite
sfaccettature, un'unica grande forza». È anche il senso del titolo
dell'evento: oltre la violenza c'è di più.

### Primi fili, dopo cinque artisti

- **Il velo e lo sguardo**: Andreini (il velo copre la bocca, restano gli
  occhi), Maselli (il velo scivola, lo sguardo si abbassa o sfida),
  Vangelisti (il volto doppio). Il vedere e l'essere viste.
- **Le donne dei racconti**: Circe e Calipso, Esmeralda, il Flauto magico.
  Figure di mito, romanzo e teatro come specchi per quelle di oggi.
- **Trattenere e lasciar andare**: il distacco consapevole di Vangelisti, il
  momento tutto per sé delle donne di Maselli, il rifiuto silenzioso di
  *Ragazza occhi verdi*. Autonomia dentro le relazioni.
- **Cinque linguaggi, un'attenzione**: simbolico e materico (Vangelisti),
  tradizione accademica (Maselli), realismo intimo (Andreini), colore fluido
  e ritratto (Bucchieri), citazione e pop (Massai). Il «plurale» del titolo è anche nei modi di
  dipingere.
- **La ferita e la ricomposizione**: i cocci della *Geisha*, le fratture d'oro
  di *Noi*, i *Petali di coraggio* che fioriscono dal nero. È il filo più
  vicino al senso dell'evento: oltre la violenza c'è di più.

## Prime letture per il filo conduttore

Appunti, da verificare quando si scrivono i testi.

- **Lo sguardo.** Quasi ogni opera si regge su uno sguardo: gli occhi che
  parlano sopra il velo di Andreini, lo
  sguardo fermo di *Caterina*, la donna del *Cesto di fiori* che non si
  lascia guardare ma interroga, il volto di *Noi* che segue chi passa.
- **Il velo e la maschera.** Veli che coprono la bocca (Andreini), veli che
  scivolano (Maselli), volti doppi o divisi (Circe e Calipso di Vangelisti,
  *Due sguardi* di Massai).
- **Mito, archetipo, citazione.** Circe e Calipso, la Geisha; Esmeralda e il
  Flauto magico; Marie-Thérèse di Picasso; la regina di *Caterina*. Le donne
  della storia e del racconto come specchi per quelle di oggi.
- **La ferita e la ricomposizione.** Le fratture d'oro di *Noi*, i cocci
  riuniti della *Geisha*, *Petali di coraggio* che fiorisce dal nero, il
  «NO!» scritto sopra un corpo esposto. È il filo più vicino al senso
  dell'evento: oltre la violenza c'è di più.
- **Il rosso.** *Sono circondata di Rosso*, *Petali di coraggio*, il cuore
  del rilievo di Massai: il colore del 25 novembre, fra passione e pericolo.
- **Femminile plurale anche nei linguaggi.** Realismo da tradizione antica
  (Barbieri, Maselli), figurazione realista (Andreini), pittura a colore
  versato (Bucchieri), gesto espressionista (Lo Cascio), omaggio e pop
  (Massai), mito e assemblaggio (Vangelisti).
- **Lasciar andare.** Il titolo del trittico di Vangelisti tiene insieme
  autonomia e relazioni, due delle cinque parole chiave della mostra.
