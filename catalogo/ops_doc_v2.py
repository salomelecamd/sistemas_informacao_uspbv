# Gera as operações para substituir, no documento de validação, o parágrafo inicial e a tabela
# de cada programa alterado, a partir do catálogo v2.
import json
import sys

d = json.load(open("catalogo_atividades_v2.json", encoding="utf-8"))
ENUM = "8795b51f-ab5f"
S = "m4vwjh0z50t."
# sigla: (id do parágrafo, hash, id da tabela, hash, rev da escrita)
BLOCOS = {
    "DNO": (1339, "40f8caee", 1418, "83703951", 3),
    "PNV": (2226, "4408673b", 2278, "084f6c96", 4),
    "SI": (3531, "74437fa2", 3599, "a4429645", 4),
    "PVSA": (4514, "d74b2609", 4569, "77d44f6d", 5),
    "PVAL": (6156, "8dcaac85", 6348, "6c0cf1b3", 5),
    "PVSEAS": (7402, "4f81d0fd", 7458, "c00ba138", 6),
    "PRSS": (9385, "4e2f329d", 9446, "9cc39c65", 6),
    "PSAC": (10317, "13fc673a", 10372, "64db9698", 7),
    "PGRH": (11925, "4428f464", 12098, "d43e80a2", 7),
    "RAST": (12715, "6ecc1377", 12796, "9bb90003", 7),
    "PNT": (14057, "405fa5bb", 14115, "ddb01585", 8),
    "PNSE": (15063, "6a312fb7", 15139, "350b2062", 8),
    "PNPSO": (16470, "ca0494a4", 16530, "9d9ff9cd", 8),
    "PNISTVIH": (17703, "fad1af38", 17760, "531186ae", 8),
    "AS": (19149, "b11dc042", 19323, "eb841dce", 9),
    "FIQ": (22908, "eb34c880", 22968, "3a41ed84", 10),
    "REVIVE": (8479, "98319d6e", 8535, "a5f1e32a", 6),
    "OUT": (23923, "33a8d6b1", 24066, "8378a2ad", 10),
    "TR": (25405, "92675af5", 25539, "e91c0d0e", 10),
}

ops = {}
for p in d["programas"]:
    sig = p["sigla"]
    if sig not in BLOCOS:
        continue
    pid, ph, tid, th, rev = BLOCOS[sig]
    rows = [a for a in d["atividades"] if a["programa_sigla"] == sig]
    lead = "%d tipos de atividade. **Valida:** %s." % (len(rows), p["equipa"])
    if p["nota"]:
        lead += " " + p["nota"]
    t = "| # | Tipo de atividade | Natureza | Quem | Indicador | Fonte | Validação | Observações |\n| --- | --- | --- | --- | --- | --- | --- | --- |\n"
    blocks = {}
    for j, a in enumerate(rows, 1):
        k = "%s_v2_%d" % (sig.lower(), j)
        blocks[k] = {"type": "dropdown", "enum": ENUM, "index": 0}
        t += "| %d | %s | %s | %s | %s | %s | <?claude block %s?> |  |\n" % (
            a["ordem"], a["tipo_atividade"], a["natureza"], a["quem"], a["indicador"], a["fonte"], k)
    ops[sig] = [
        {"op": "replace", "target": {"kind": "blocks", "ids": [S + str(pid)]}, "ifHash": ph, "ifRev": rev,
         "with": {"from": {"kind": "inline", "content": lead}, "as": "markdown"}},
        {"op": "replace", "target": {"kind": "blocks", "ids": [S + str(tid)]}, "ifHash": th, "ifRev": rev,
         "with": {"from": {"kind": "inline", "content": t.rstrip()}, "as": "markdown", "blocks": blocks}},
    ]

json.dump(ops, open("ops_doc_v2.json", "w"), ensure_ascii=True)
if len(sys.argv) > 1:
    print(json.dumps({"ops": [o for s in sys.argv[1:] for o in ops[s]]}, ensure_ascii=True))
