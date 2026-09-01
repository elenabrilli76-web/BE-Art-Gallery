# Strumenti

Producono i contenuti social di BE Art Gallery a partire da una cartella di
foto e video: reel, post, caroselli e storie, tutti con la stessa faccia.

## Installazione, una volta sola

```
py -m pip install -r strumenti\requirements.txt
```

`imageio-ffmpeg` porta con sé ffmpeg, che serve solo ai reel. Se sul computer
c'è già ffmpeg, viene usato quello.

## Uso

```
py strumenti\crea.py
```

Legge `contenuti-social/in-lavorazione/contenuto.json`, produce quello che vi
è richiesto e lo salva in `contenuti-social/in-lavorazione/pronti/`.

Il file `contenuto.json` lo scrive Claude a partire da quello che chiedi: non
va composto a mano. Per usarne un altro:

```
py strumenti\crea.py percorso\del\file.json
```

## Com'è fatto

| File | Cosa fa |
|---|---|
| `crea.py` | l'unico da lanciare: legge il file e smista ai due generatori |
| `immagini.py` | post, caroselli e storie → PNG |
| `reel.py` | il video → MP4, con ffmpeg |
| `grafica.py` | ritaglio delle foto e composizione dei testi, comuni a tutti |

I colori e i font stanno in un posto solo, `grafica.py`, così un contenuto
prodotto oggi e uno prodotto fra un mese hanno lo stesso aspetto.

## Le impaginazioni di post, caroselli e storie

Come per i reel, servono a non pubblicare sempre la stessa pagina. Non sono
decorazioni intercambiabili: nascono dal linguaggio grafico già definito per la
galleria — il filetto oro che accompagna i titoli come la cornice di un quadro,
il cartellino da mostra, il ritaglio ad arco che richiama gli archi in mattoni.
Si indicano con `"impaginazione"`.

| Impaginazione | Com'è fatta | Quando |
|---|---|---|
| **pieno** | foto a tutto campo, testo sulla velatura | la più diretta: eventi, persone, atmosfera |
| **cartellino** | foto sopra, fascia avorio sotto con filetto e testo in inchiostro | quando la parola conta quanto l'immagine: annunci, titoli di mostra |
| **cornice** | fondo nero, immagine rientrata, filetto e testo sotto | una singola opera, che vuole aria attorno |
| **arco** | ritaglio ad arco su fondo avorio | lo spazio, l'architettura, il richiamo al palazzo |

**Un'impaginazione per contenuto, non per pagina.** Dentro un carosello la
coerenza tiene insieme il racconto: la varietà sta fra un contenuto e il
successivo. Le pagine senza testo tornano automaticamente a `pieno`, perché una
fascia vuota sembra un errore di stampa.

Con `"numerazione": true` le pagine di un carosello portano il numero romano in
alto a destra, come il cartellino di sala.

## Gli stili di montaggio

Non sono effetti diversi per il gusto di variare: ogni stile corrisponde a un
modo di raccontare, e cambia insieme ritmo, transizione e ampiezza del
movimento. Si indica con `"stile"` dentro `reel`.

| Stile | Per cosa | Come si comporta |
|---|---|---|
| **serata** | un evento, con le persone dentro | ritmo medio, dissolvenza, alterna fermo e movimento |
| **camminata** | lo spazio, i tre livelli | scene lunghe, movimento ampio e lento, dissolvenze morbide |
| **opera** | una sola opera guardata da vicino | zoom deciso, passaggi molto morbidi |
| **urgenza** | ultimi giorni, scadenze | **stacco netto**, nessuna dissolvenza, ritmo serrato |
| **rassegna** | più opere una dopo l'altra | scorrimento laterale, come sfogliando |

Le singole voci di `impostazioni` sovrascrivono lo stile, se serve una
correzione puntuale.

## Il marchio

Il logo della galleria viene messo **da solo** in alto a sinistra, su ogni
immagine e per tutta la durata dei video, con sotto una velatura sfumata che lo
tiene leggibile anche sulle foto chiare — il logo ha un'aureola scura attorno
al monogramma e senza fondo si sporca.

Il file è `marchio/logo.png`. Si può regolarne la misura con
`"logo_larghezza"` (quota della larghezza dell'immagine, predefinito `0.24`)
oppure toglierlo con `"logo": false`, ma toglierlo non è previsto dalle regole
di comunicazione: la galleria è il soggetto di ogni contenuto.

## Il formato di `contenuto.json`

Serve solo se qualcosa va storto e vuoi capire cosa.

```json
{
  "nome": "inaugurazione-ebart",
  "carosello": {
    "ordine": ["01.jpg", "02.jpg", "03.jpg"],
    "finale": {
      "righe": ["E.B.Art", "fino al 6 settembre"],
      "sfondo": "04.jpg"
    }
  },
  "storia": {
    "foto": "01.jpg",
    "testi": [
      { "righe": ["Ultimi giorni"], "en": "Last days",
        "posizione": "basso", "enfasi": true }
    ]
  },
  "reel": {
    "stile": "serata",
    "testi": [
      { "righe": ["BE Art Gallery", "Pistoia"],
        "inizio": 0.4, "fine": 3.4, "posizione": "centro", "enfasi": true }
    ],
    "impostazioni": { "durata_scena": 3.2 }
  }
}
```

- I formati presenti nel file sono quelli che vengono prodotti: se manca
  `post`, il post non si fa
- `posizione` può essere `alto`, `centro` o `basso`
- `en` è la traduzione inglese della riga, e viene aggiunta **solo se ci sta**:
  deve stare su una riga sola e il blocco non deve superare il 28% dell'altezza
  (`blocco_massimo`). Altrimenti resta il solo italiano e il comando lo dice.
  Sulle caption invece l'inglese è sempre obbligatorio — quelle le scrive Claude
  in `testi.md`, non passano da qui
- `enfasi` usa il corpo grande e l'oro sulla prima riga
- Le foto si indicano per nome, e stanno tutte in `in-lavorazione/foto/`
- Senza `ordine` vengono presi in ordine alfabetico

### Video nei reel

Nella scaletta di un reel possono entrare anche gli spezzoni video: in un
contenuto d'evento il movimento racconta più di una foto ferma. Una voce di
`ordine` può quindi essere un oggetto invece di un nome:

```json
"ordine": [
  "01.jpg",
  { "file": "VID_20260829.mp4", "durata": 4.0, "da": 12.5 },
  "02.jpg"
]
```

- `durata` quanti secondi dura la scena
- `da` da che secondo del video parte — serve a prendere il momento buono
  invece dell'inizio

Sugli spezzoni video non viene applicato nessun movimento: l'inquadratura si
muove già, e uno zoom sopra renderebbe la scena confusa. L'audio viene
scartato, perché la musica si mette dall'app al momento di pubblicare.

Post, caroselli e storie ignorano i video anche se stanno nella stessa cartella.

## Il reel da solo

`reel.py` funziona anche per conto suo, se serve una prova veloce:

```
py strumenti\reel.py --foto contenuti-social\in-lavorazione\foto --out prova.mp4 --titolo "BE Art Gallery"
```

Il comando va **su una riga sola**: la barra rovesciata a fine riga degli
esempi per Mac e Linux non funziona nel Prompt dei comandi di Windows.

## Musica

Meglio non montarla nel video: aggiungila dall'app Instagram al momento di
pubblicare, perché i brani della libreria interna vengono distribuiti meglio.
Se serve comunque, si indica con `"musica"` dentro `reel` in `contenuto.json`.
