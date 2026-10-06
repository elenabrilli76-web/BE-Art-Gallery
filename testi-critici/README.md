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

> **Per i file Word**: perché si vedano con il carattere della galleria, il
> Cormorant Garamond va installato sul PC, una volta sola. Si apre
> `strumenti\marchio\font\`, si selezionano i file `CormorantGaramond-…`,
> tasto destro → **Installa**. Senza, Word usa un carattere sostitutivo: il
> testo resta giusto, cambia solo l'aspetto.

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

👉 Il metodo di analisi e le regole di scrittura: [`PROCEDURA.md`](PROCEDURA.md)
