# Testi critici d'artista

Una cartella per artista, con nome e cognome. Dentro, sempre le stesse cose:

```
testi-critici/artisti/nome-cognome/
├── analisi.md                     il file per la galleria: note e testi, con i conteggi
├── scheda.json                    i testi definitivi, da cui nascono i PDF
└── pdf/
    ├── presentazione.pdf          A5 · la sintesi da consegnare all'artista
    └── opera-titolo-opera.pdf     A6 · una didascalia per ogni opera analizzata
```

## Le due modalità

| Chiedi | Ricevi |
|---|---|
| **la presentazione di un artista** — da 3 a 5 opere | il testo critico di 500–600 caratteri, in A5, da consegnare e da stampare per la sala |
| **l'analisi di una singola opera** — una foto | una didascalia di 150–300 caratteri, in A6, da mettere accanto al quadro |

Si possono chiedere insieme o in momenti diversi: le didascalie si aggiungono
nella stessa cartella dell'artista, e la presentazione già scritta resta coerente
con le opere che arrivano dopo.

## Come scaricare i PDF

Dopo un **Pull origin**, i PDF stanno nella cartella `pdf/` dell'artista. Da
telefono: su GitHub si apre il file e si usa il pulsante di download.

Se si ritocca un testo a mano dentro `scheda.json`, i PDF si rifanno con:

```
py strumenti\critica.py nome-cognome
```

👉 Il metodo di analisi e le regole di scrittura: [`PROCEDURA.md`](PROCEDURA.md)
