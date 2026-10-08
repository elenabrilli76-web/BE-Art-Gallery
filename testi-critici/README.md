# Testi critici d'artista

Una cartella per artista, con nome e cognome. Dentro, sempre le stesse cose:

```
testi-critici/artisti/nome-cognome/
├── analisi.md                     il file per la galleria: note e testi, con i conteggi
├── scheda.json                    i testi definitivi, da cui nasce tutto il resto
├── pdf/                           per la stampa
│   ├── presentazione.pdf          A5 · la sintesi da consegnare all'artista
│   └── opera-titolo-opera.pdf     A6 · una didascalia per ogni opera analizzata
├── png/                           le stesse pagine in immagine, a 300 dpi:
│                                  per WhatsApp, email, social, o la tipografia
└── word/                          le stesse pagine in Word, da ritoccare e stampare
```

> **I file Word sono in Garamond**, che c'è già su ogni PC con Office: si
> aprono così come sono, senza installare niente. PDF e PNG restano nel
> Cormorant delle locandine, che sta dentro il file.

## Le due modalità

| Chiedi | Ricevi |
|---|---|
| **la presentazione di un artista** — da 3 a 5 opere | il testo critico di 500–600 caratteri, in A5, da consegnare e da stampare per la sala |
| **l'analisi di una singola opera** — una foto | una didascalia di 150–300 caratteri, in A6, da mettere accanto al quadro |

Si possono chiedere insieme o in momenti diversi: le didascalie si aggiungono
nella stessa cartella dell'artista, e la presentazione già scritta resta coerente
con le opere che arrivano dopo.

## Come scaricarli

Dopo un **Pull origin**, stanno nelle cartelle `pdf/`, `png/` e `word/` dell'artista. Da
telefono: su GitHub si apre il file e si usa il pulsante di download.

Se si ritocca un testo a mano dentro `scheda.json`, PDF, PNG e Word si rifanno con:

```
py strumenti\critica.py nome-cognome
```

## Il catalogo della mostra

Tutte le schede di una mostra in un documento solo, A4, stampabile, solo in
italiano: una pagina con il testo della mostra, poi una pagina per artista
con presentazione e didascalie.

```
testi-critici/mostre/catalogo/i-luoghi-dell-anima.pdf
testi-critici/mostre/catalogo/i-luoghi-dell-anima.docx
```

Il testo della mostra e l'ordine degli artisti stanno in
`testi-critici/mostre/i-luoghi-dell-anima.json`. Si rifà con:

```
py strumenti\catalogo.py i-luoghi-dell-anima
```

👉 Il metodo di analisi e le regole di scrittura: [`PROCEDURA.md`](PROCEDURA.md)
