#!/usr/bin/env python3
"""
Le richieste per ricostruire il catalogo dentro un Google Doc esistente.

Il Google Doc si aggiorna con le API di Docs (documents.batchUpdate): questo
script legge le stesse schede del catalogo e scrive in un file JSON la lista
di richieste — svuota il documento e lo riscrive con A4, sfondo crema, logo,
titoli, filetti oro e una pagina per artista. A mandarle è Claude, con il
connettore Google Docs.

    python strumenti/gdoc.py <fine-del-body> <revisionId> > richieste.json
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalogo as k  # noqa: E402
import critica as c  # noqa: E402


def rgb(colore):
    h = colore.hexval()[2:]
    return {"color": {"rgbColor": {"red": round(int(h[0:2], 16) / 255, 3),
                                   "green": round(int(h[2:4], 16) / 255, 3),
                                   "blue": round(int(h[4:6], 16) / 255, 3)}}}


PT = lambda n: {"magnitude": n, "unit": "PT"}  # noqa: E731
ORO, GRIGIO, NERO, CARTA = rgb(c.ORO), rgb(c.GRIGIO), rgb(c.INCHIOSTRO), rgb(c.CARTA)
NESSUN_BORDO = {"width": PT(0), "padding": PT(0), "dashStyle": "SOLID", "color": CARTA}
CELLA_SENZA_BORDO = {"width": PT(0), "dashStyle": "SOLID", "color": CARTA}   # le celle non hanno padding sul bordo


BASE_P = {"namedStyleType": "NORMAL_TEXT", "alignment": "JUSTIFIED", "lineSpacing": 140,
          "spaceAbove": PT(0), "spaceBelow": PT(8), "pageBreakBefore": False,
          "keepWithNext": False, "borderBottom": NESSUN_BORDO}
BASE_T = {"weightedFontFamily": {"fontFamily": "EB Garamond", "weight": 400},
          "fontSize": PT(12), "foregroundColor": NERO, "bold": False, "italic": False}


class Doc:
    """Ogni paragrafo nuovo eredita lo stile del paragrafo vuoto in fondo al
    documento: lo si imposta una volta sul corpo del testo, e per ogni
    paragrafo si mandano solo le differenze. Così le richieste restano corte."""

    def __init__(self):
        self.r = []
        self.pos = 1

    def _par(self, a, b, **p):
        if p:
            self.r.append({"updateParagraphStyle": {"range": {"startIndex": a, "endIndex": b},
                                                    "paragraphStyle": p, "fields": ",".join(p)}})

    def _txt(self, a, b, **t):
        if t and b > a:
            self.r.append({"updateTextStyle": {"range": {"startIndex": a, "endIndex": b},
                                               "textStyle": t, "fields": ",".join(t)}})

    def base(self):
        """Lo stile di partenza sul paragrafo vuoto finale."""
        self._par(1, 2, **BASE_P)
        self._txt(1, 2, **BASE_T)

    def paragrafo(self, testo, par=None, txt=None):
        testo = testo.replace("'", "\u2019")
        a = self.pos
        self.r.append({"insertText": {"location": {"index": a}, "text": testo + "\n"}})
        self._par(a, a + len(testo) + 1, **(par or {}))
        self._txt(a, a + len(testo), **(txt or {}))
        self.pos += len(testo) + 1

    def logo(self, url, larghezza):
        self.r.append({"insertText": {"location": {"index": self.pos}, "text": "\n"}})
        self.r.append({"insertInlineImage": {"location": {"index": self.pos}, "uri": url,
                                             "objectSize": {"width": PT(larghezza)}}})
        self._par(self.pos, self.pos + 2, alignment="START", spaceBelow=PT(30))
        self.pos += 2

    def tabella(self, schede, colonne):
        righe = [schede[i:i + colonne] for i in range(0, len(schede), colonne)]
        R, C = len(righe), colonne
        i = self.pos - 1
        self.r.append({"insertTable": {"location": {"index": i}, "rows": R, "columns": C}})
        celle = []
        for r, riga in enumerate(righe):
            for col in range(C):
                o = riga[col] if col < len(riga) else None
                parti = [] if o is None else [o["titolo"], k.dati_opera(o) or " ", o["didascalia"]["it"]]
                celle.append((i + 4 + r * (2 * C + 1) + 2 * col, [x.replace("'", "\u2019") for x in parti]))
        for base, parti in reversed(celle):
            if parti:
                self.r.append({"insertText": {"location": {"index": base}, "text": "\n".join(parti)}})
        sp = 0
        for base, parti in celle:
            if not parti:
                continue
            p = base + sp
            lung = len("\n".join(parti))
            # Nelle celle Google non accetta pageBreakBefore
            cella = {kk: v for kk, v in BASE_P.items() if kk != "pageBreakBefore"}
            self._par(p, p + lung + 1, **{**cella, "lineSpacing": 125, "spaceBelow": PT(0)})
            self._txt(p, p + lung, **{**BASE_T, "fontSize": PT(10)})
            t, d, _ = (len(x) + 1 for x in parti)
            self._par(p, p + t, alignment="START")
            self._txt(p, p + t - 1, fontSize=PT(13), italic=True)
            self._par(p + t, p + t + d, alignment="START", spaceBelow=PT(5),
                      borderBottom={"width": PT(0.75), "padding": PT(3), "dashStyle": "SOLID", "color": ORO})
            self._txt(p + t, p + t + d - 1, fontSize=PT(8.5), foregroundColor=GRIGIO)
            sp += lung
        nb = CELLA_SENZA_BORDO
        self.r.append({"updateTableCellStyle": {
            "tableRange": {"tableCellLocation": {"tableStartLocation": {"index": i + 1},
                                                 "rowIndex": 0, "columnIndex": 0},
                           "rowSpan": R, "columnSpan": C},
            "tableCellStyle": {"borderTop": nb, "borderBottom": nb, "borderLeft": nb, "borderRight": nb,
                               "paddingTop": PT(0), "paddingBottom": PT(12),
                               "paddingLeft": PT(0), "paddingRight": PT(12)},
            "fields": "borderTop,borderBottom,borderLeft,borderRight,paddingTop,paddingBottom,paddingLeft,paddingRight"}})
        self.pos = i + 3 + R * (2 * C + 1) + sp


def richieste(fine_body: int) -> list:
    cfg = json.loads((k.MOSTRE / "i-luoghi-dell-anima.json").read_text(encoding="utf-8"))
    schede = [json.loads((c.ARTISTI / n / "scheda.json").read_text(encoding="utf-8")) for n in cfg["ordine"]]
    d = Doc()
    if fine_body - 1 > 1:
        d.r.append({"deleteContentRange": {"range": {"startIndex": 1, "endIndex": fine_body - 1}}})
    d.r.append({"updateDocumentStyle": {"documentStyle": {
        "pageSize": {"width": PT(595.28), "height": PT(841.89)},
        "marginTop": PT(56.7), "marginBottom": PT(56.7), "marginLeft": PT(56.7), "marginRight": PT(56.7),
        "background": {"color": CARTA}},
        "fields": "pageSize,marginTop,marginBottom,marginLeft,marginRight,background"}})
    d.base()
    ORO_F = {"width": PT(1.5), "padding": PT(5), "dashStyle": "SOLID", "color": ORO}
    d.logo(k.LOGO_PUBBLICO, 120)
    d.paragrafo(cfg["titolo"], {"namedStyleType": "TITLE", "alignment": "START", "spaceBelow": PT(2)},
                {"fontSize": PT(34), "bold": True})
    d.paragrafo(cfg["sottotitolo"], {"alignment": "START", "spaceBelow": PT(0)},
                {"fontSize": PT(15), "italic": True, "foregroundColor": GRIGIO})
    d.paragrafo(cfg["luogo"], {"alignment": "START", "spaceBelow": PT(16), "borderBottom": ORO_F},
                {"fontSize": PT(11), "foregroundColor": GRIGIO})
    for voce in cfg["testo"]:
        if isinstance(voce, dict):
            d.paragrafo(voce["titolo"], {"namedStyleType": "HEADING_2", "alignment": "START",
                                         "spaceAbove": PT(12), "spaceBelow": PT(4), "keepWithNext": True},
                        {"fontSize": PT(15), "italic": True})
        else:
            d.paragrafo(voce)
    for s in schede:
        d.paragrafo(s["nome"], {"namedStyleType": "HEADING_1", "alignment": "START", "spaceBelow": PT(2),
                                "pageBreakBefore": True, "keepWithNext": True},
                    {"fontSize": PT(24), "bold": True})
        d.paragrafo(c.sottotitolo(s) or " ", {"alignment": "START", "spaceBelow": PT(14), "borderBottom": ORO_F},
                    {"fontSize": PT(12), "italic": True, "foregroundColor": GRIGIO})
        if s.get("presentazione", {}).get("it"):
            # stile completo: senza tabella prima, il paragrafo erediterebbe quello del sottotitolo
            d.paragrafo(s["presentazione"]["it"],
                        {"alignment": "JUSTIFIED", "spaceBelow": PT(14), "borderBottom": NESSUN_BORDO},
                        {"fontSize": PT(11.5), "italic": False, "foregroundColor": NERO})
        opere = [o for o in s.get("opere", []) if o.get("didascalia", {}).get("it")]
        if opere:
            d.tabella(opere, 1 if len(opere) == 1 else k.COLONNE)
    return d.r


if __name__ == "__main__":
    print(json.dumps({"requests": richieste(int(sys.argv[1])),
                      "writeControl": {"requiredRevisionId": sys.argv[2]}}, ensure_ascii=False))
