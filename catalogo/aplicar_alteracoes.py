# Aplica ao catálogo local as alterações feitas na lista catalogo_atividades (19/10/2026)
# e calcula a nova ordem. Os Id do SharePoint 1..182 correspondem à ordem original.
import json

d = json.load(open("catalogo_atividades.json", encoding="utf-8"))
progs = {p["sigla"]: p for p in d["programas"]}

APAGADOS = {3, 7, 13, 24, 35, 37, 66, 68, 69, 71, 72, 83, 92, 94, 95, 96, 109, 113, 121, 126, 160, 163}

# Id -> (tipo, natureza, quem, indicador), como estão agora na lista
EDITADOS = {
    5: ("Análise de dados e elaboração informação (semestral)", "Gestão do programa", "Equipa", "Realizado (sim/não)"),
    6: ("Avaliação anual e elaboração do respetivo relatório", "Gestão do programa", "Equipa", "Realizado (sim/não)"),
    17: ("Concessão de Livre prática", "Operacional", "TSA", "N.º de livres práticas"),
    19: ("Vistoria para emissão de certificado", "Operacional", "TSA", "N.º de vistorias"),
    20: ("Emissão de certificado", "Administrativa", "TSA", "N.º de certificados"),
    25: ("Reunião anual com os profissionais envolvidos no programa", "Reunião", "Equipa Gestora + USP-SL", "N.º de reuniões"),
    33: ("Vistoria / vertente tecnológica", "Operacional", "TSA/AS", "N.º de vistorias"),
    34: ("Atualização de cadastro", "Operacional", "TSA", "Cadastro atualizado"),
    38: ("Atualização de cadastro", "Operacional", "TSA/MSP/TSS", "Concelhos com cadastro atualizado"),
    45: ("Atualização do cadastro", "Operacional", "TSA/MSP/TSS/EEEC", "Concelhos com cadastro atualizado"),
    47: ("Vistoria a ERPI (1.ª vistoria)", "Operacional", "TSA/MSP/TSS/EEEC", "N.º de ERPI vistoriadas"),
    49: ("Comunicação do resultado da vistoria", "Administrativa", "TSA/MSP/EEEC/TSS/AT", "N.º de comunicações"),
    67: ("Atualização do cadastro", "Operacional", "USP-SL", "N.º de cantinas atualizadas"),
    70: ("Vistoria a cantina", "Operacional", "USP-SL", "N.º de cantinas vistoriadas"),
    91: ("Realização de formação sobre tuberculose", "Formação", "Equipa Coordenadora", "N.º de ações"),
    98: ("Reunião da ECSE com ELSE", "Reunião", "ECSE", "N.º de reuniões"),
    107: ("Elaboração de proposta de formação", "Formação", "ECSE", "N.º de formações"),
    116: ("Formação PNPSO a médicos e enfermeiros", "Formação", "Equipa Coordenadora", "Realizado (sim/não)"),
    124: ("Sessão em escola", "Operacional", "ELSE", "N.º de alunos"),
    128: ("Avaliação médica para a condução / Emissão de atestados", "Operacional", "Autoridade de Saúde", "N.º de atestados"),
    129: ("Avaliação de saúde mental/psiquiátrica", "Operacional", "Autoridade de Saúde", "N.º de pedidos / mandados"),
    131: ("Emissão de atestados de trasladação", "Administrativa", "Autoridade de Saúde", "N.º de atestados"),
    139: ("Vistoria - estabelecimento industrial", "Operacional", "AS / TSA", "N.º de vistorias"),
}

# Novos (Id -> sigla): "Reunião equipa gestora" em cada programa
NOVOS = {183: "PVSEAS", 184: "PNV", 185: "PVSA", 186: "DNO", 187: "PRSS", 188: "PNSE", 189: "PVAL",
         190: "PSAC", 191: "PGRH", 192: "PNT", 193: "PNISTVIH"}

linhas = []
for a in d["atividades"]:
    i = a["ordem"]
    if i in APAGADOS:
        continue
    a = dict(a, sp_id=i)
    if i in EDITADOS:
        a["tipo_atividade"], a["natureza"], a["quem"], a["indicador"] = EDITADOS[i]
    linhas.append(a)

# Cada reunião nova fica no fim do bloco do seu programa
for sp_id, sig in NOVOS.items():
    p = progs[sig]
    linhas.append({"ordem": max(x["ordem"] for x in linhas if x["programa_sigla"] == sig) + 0.5, "sp_id": sp_id,
                   "area": next(x["area"] for x in linhas if x["programa_sigla"] == sig),
                   "programa_sigla": sig, "programa": p["nome"], "tipo_atividade": "Reunião equipa gestora",
                   "natureza": "Reunião", "quem": "Equipa Gestora", "indicador": "N.º de reuniões",
                   "fonte": "Proposta da coordenação", "equipa_validacao": p["equipa"], "novo": True})

linhas.sort(key=lambda x: x["ordem"])
for n, a in enumerate(linhas, start=1):
    a["ordem"] = n

d["atividades"] = linhas
json.dump(d, open("catalogo_atividades_v2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# Atualizações para o SharePoint: [id, ordem] para todos; campos completos para os novos e títulos sem espaços
upd = [[a["sp_id"], a["ordem"]] for a in linhas]
novos = [[a["sp_id"], a["area"], a["natureza"], a["quem"], a["indicador"], a["fonte"], a["equipa_validacao"], a["programa_sigla"]]
         for a in linhas if a.get("novo")]
json.dump({"ordem": upd, "novos": novos}, open("sp_updates.json", "w"), ensure_ascii=True, separators=(",", ":"))
print(len(linhas), "linhas")
