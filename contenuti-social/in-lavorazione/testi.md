# Testi — Inaugurazione E.B.Art, invito a visitare

**Formato:** carosello · **Canali:** Instagram + Facebook
**CTA unica:** vieni a visitare, entro il 6 settembre

---

## Instagram — caption

> Sabato sera abbiamo aperto le porte per la prima volta.
>
> Le opere di Elena Brilli sono appese alle pareti in sasso di un palazzo del
> centro storico, distribuite su tre livelli comunicanti. Il colore contro la
> pietra: è esattamente il contrasto per cui abbiamo scelto questo spazio.
>
> Chi non c'era fa ancora in tempo. La personale di E.B.Art resta visitabile
> fino a domenica 6 settembre, su appuntamento: scrivici un messaggio e ti
> apriamo.
>
> Via San Pietro 24, Pistoia — di fronte a San Pier Maggiore.

**Prima riga alternativa**, se vuoi un attacco più asciutto:

> Restano sei giorni per vedere le opere di Elena Brilli sulle nostre pareti in sasso.

---

## Facebook — stesso contenuto, con i dettagli pratici

> Sabato sera abbiamo aperto le porte per la prima volta, e la galleria si è
> riempita. Grazie a tutti quelli che sono passati.
>
> Le opere di Elena Brilli — E.B.Art — sono appese alle pareti in sasso di un
> palazzo storico nel centro di Pistoia, su tre livelli comunicanti: il piano
> d'ingresso a doppio volume, il ballatoio in ferro e cotto, e la sala voltata.
> Il colore contro la pietra è il contrasto per cui abbiamo scelto questo spazio.
>
> **La mostra resta visitabile fino a domenica 6 settembre**, su appuntamento.
> Per venire basta un messaggio: 377 573 5187, anche su WhatsApp.
>
> BE Art Gallery & Creative Lab
> Via San Pietro 24, Pistoia — di fronte alla Chiesa di San Pier Maggiore
> beartgallery.eu

---

## Testi in sovrimpressione

**Nessuno sulle foto della serata.** Le immagini di un evento funzionano da sole:
le facce, la luce, le persone davanti alle opere. Un testo sopra le indebolisce
e le fa sembrare una locandina.

L'unica eccezione è **l'ultima immagine del carosello**, che chiude con
l'informazione pratica:

> **E.B.Art**
> fino al 6 settembre
> Via San Pietro 24, Pistoia
> su appuntamento — 377 573 5187

Non devi farla: la produce il comando, su fondo scuro, come ultima pagina.

---

## Quali foto scegliere

Da 5 a 7, in quest'ordine:

1. **La sala piena.** Una veduta larga con le persone dentro. È l'immagine che
   dice "è successo qualcosa" — la sola che quasi tutti vedranno
2. **Persone davanti a un'opera**, di spalle o di tre quarti: si guarda dove
   guardano loro
3. **Un'opera intera**, ben illuminata, sulla parete in sasso
4. **Elena che parla con qualcuno.** L'artista al lavoro, non in posa
5. **Un dettaglio**: le mani, un bicchiere, la scala, la luce sulle travi
6. *(facoltativa)* **Il ballatoio o la sala voltata**, per far capire i tre livelli

La schermata finale con date e indirizzo si aggiunge da sola, in coda.

Da evitare: foto mosse o troppo scure, persone col bicchiere davanti alla
faccia, e due inquadrature quasi identiche di seguito.

---

## Hashtag

Da provare — questo set va affinato guardando cosa porta visite davvero:

`#beartgallery #pistoia #artecontemporanea #galleriadarte #ebart #elenabrilli`
`#arteastratta #toscana #mostradarte #pistoiacittà #vernissage #artegiovane`

Su Instagram vanno nel primo commento, non nella caption: il testo resta pulito.
Su Facebook servono a poco, tienine due o tre al massimo.

---

## Note

- **Una sola CTA:** venire a visitare. Non nominare "I Luoghi dell'Anima" né le
  iscrizioni di ottobre: sono un altro contenuto, e due richieste nello stesso
  post se ne annullano una
- Su Instagram i link non sono cliccabili: per questo la CTA è il messaggio
  diretto, non il sito
- Parla la galleria: Elena Brilli è nominata in terza persona, come qualunque
  altro artista in mostra

---

## Come produrlo

Metti le foto in `contenuti-social\in-lavorazione\foto\`, rinominate
`01.jpg`, `02.jpg`, `03.jpg`… nell'ordine in cui vuoi che appaiano. Poi:

```
py strumenti\crea.py
```

Escono in `in-lavorazione\pronti\`:

- `carosello_01.png` … e in coda la schermata con date e indirizzo
- `storia.png`, per rilanciare il carosello fra le storie

Il numero di foto non è fissato: il comando usa quelle che trova.
