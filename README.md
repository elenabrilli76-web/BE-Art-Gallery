# BE Art Gallery — contenuti social

Gli **strumenti e il processo** per produrre i contenuti social della galleria.
I materiali — foto, video, logo — restano nell'archivio: qui c'è solo ciò che
serve a trasformarli in contenuti pubblicabili.

## Il giro, in quattro mosse

```
1. metti le foto in contenuti-social\in-lavorazione\foto\
2. dici a Claude cosa vuoi
3. py strumenti\crea.py
4. scarichi da pronti\ e pubblichi
```

Vale per reel, post, caroselli e storie: cambia solo cosa chiedi al passo 2.

👉 Il processo completo: **[`contenuti-social/PROCESSO.md`](contenuti-social/PROCESSO.md)**

## Cosa c'è

| Cartella | Cosa contiene |
|---|---|
| [`contenuti-social/`](contenuti-social/) | il processo, lo spazio di lavoro, l'archivio dei contenuti usciti |
| [`strumenti/`](strumenti/) | i generatori di reel, post, caroselli e storie |

E [`CLAUDE.md`](CLAUDE.md), che dà il contesto a chi apre una sessione di
Claude Code su questo repository: chi siamo, come parliamo, come funzionano
gli eventi.

## Installazione, una volta sola

```
py -m pip install -r strumenti\requirements.txt
```
