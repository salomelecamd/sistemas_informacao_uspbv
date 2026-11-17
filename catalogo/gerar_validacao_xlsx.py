# Gera o Excel de validação do catálogo de atividades: uma folha de instruções e uma folha por equipa.
# Uso: python gerar_validacao_xlsx.py catalogo_atividades_v2.json saida.xlsx
import json
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

d = json.load(open(sys.argv[1], encoding="utf-8"))
OUT = sys.argv[2]

# Equipa que valida -> nome curto da folha (máx. 31 caracteres)
FOLHAS = {
    "Médicos de Saúde Pública / Autoridades de Saúde": "Vigilância Epidemiológica",
    "Núcleo de Vacinação": "Núcleo de Vacinação",
    "Equipa de Sanidade Marítima (TSA/AS)": "Sanidade Marítima",
    "Equipa Gestora do PVSA": "Equipa PVSA e PVAL",
    "Equipa Gestora do PVSEAS": "Equipa PVSEAS",
    "Equipa Gestora do REVIVE": "Equipa REVIVE",
    "Grupo Operativo Local do PRSS": "GOL PRSS",
    "Equipa Gestora do PSAC": "Equipa PSAC",
    "Equipa Gestora do PGRH": "Equipa PGRH",
    "Equipa de Coordenação Local dos Rastreios (ECLR)": "Rastreios (ECLR)",
    "Equipa Coordenadora do PNT": "Tuberculose (PNT)",
    "Equipa Coordenadora da Saúde Escolar (ECSE)": "Saúde Escolar (ECSE)",
    "Equipa Coordenadora do PNPSO": "Saúde Oral (PNPSO)",
    "Equipa local do PNISTVIH": "IST e VIH (PNISTVIH)",
    "Autoridades de Saúde / Conselho Técnico": "Autoridade de Saúde",
    "Núcleo de Formação da USP BV": "Formação e Qualidade",
    "Conselho Técnico": "Conselho Técnico",
}
OPCOES = ["Validado", "Alterar", "Remover", "Nova"]
LINHAS_NOVAS = 5

AZUL = "1F4E79"
CINZA = "F2F2F2"
fino = Side(style="thin", color="BFBFBF")
borda = Border(left=fino, right=fino, top=fino, bottom=fino)
cab_font = Font(bold=True, color="FFFFFF")
cab_fill = PatternFill("solid", fgColor=AZUL)
prog_fill = PatternFill("solid", fgColor="DDEBF7")
nova_fill = PatternFill("solid", fgColor=CINZA)
wrap = Alignment(wrap_text=True, vertical="top")

# Equipas pela ordem do catálogo
equipas = []
for a in d["atividades"]:
    if a["equipa_validacao"] not in equipas:
        equipas.append(a["equipa_validacao"])

wb = Workbook()
ins = wb.active
ins.title = "Instruções"
ins.column_dimensions["A"].width = 34
ins.column_dimensions["B"].width = 52
ins.column_dimensions["C"].width = 12
ins["A1"] = "Validação do catálogo de atividades da USP Baixo Vouga"
ins["A1"].font = Font(bold=True, size=14, color=AZUL)
texto = [
    "Este ficheiro lista os tipos de atividade que aparecem na aplicação do Calendário Partilhado, por programa.",
    "Cada equipa valida a sua folha (separadores em baixo). Pode haver várias pessoas a editar ao mesmo tempo.",
    "1. Na coluna Validação escolha: Validado, Alterar ou Remover.",
    "2. Em Alterar, escreva na coluna Proposta / observações o nome correto.",
    "3. Atividades em falta: use as linhas cinzentas no fim de cada programa, com Validação = Nova.",
    "4. O nome do tipo de atividade é o que aparece na aplicação: curto e reconhecível por quem regista.",
    "As atividades da folha Conselho Técnico (Transversal) ficam disponíveis em todos os programas.",
]
for i, t in enumerate(texto, start=3):
    ins.cell(row=i, column=1, value=t).alignment = Alignment(wrap_text=False)
r0 = len(texto) + 4
for c, h in enumerate(["Folha", "Programas", "Atividades"], start=1):
    cel = ins.cell(row=r0, column=c, value=h)
    cel.font, cel.fill, cel.border = cab_font, cab_fill, borda

r = r0 + 1
for eq in equipas:
    rows = [a for a in d["atividades"] if a["equipa_validacao"] == eq]
    progs = []
    for a in rows:
        if a["programa"] not in progs:
            progs.append(a["programa"])
    nome = FOLHAS[eq]
    cel = ins.cell(row=r, column=1, value=nome)
    cel.hyperlink = "#'%s'!A1" % nome
    cel.font = Font(color="0563C1", underline="single")
    ins.cell(row=r, column=2, value="; ".join(progs))
    ins.cell(row=r, column=3, value=len(rows))
    for c in range(1, 4):
        ins.cell(row=r, column=c).border = borda
        ins.cell(row=r, column=c).alignment = wrap
    r += 1

    ws = wb.create_sheet(nome)
    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 62
    ws.column_dimensions["C"].width = 14
    ws.column_dimensions["D"].width = 60
    ws["A1"] = nome
    ws["A1"].font = Font(bold=True, size=14, color=AZUL)
    ws["A2"] = "Valida: " + eq
    ws["A2"].font = Font(italic=True, color="595959")
    hdr = 4
    for c, h in enumerate(["Nº", "Tipo de atividade", "Validação", "Proposta / observações"], start=1):
        cel = ws.cell(row=hdr, column=c, value=h)
        cel.font, cel.fill, cel.border = cab_font, cab_fill, borda
    ws.freeze_panes = ws.cell(row=hdr + 1, column=1)
    dv = DataValidation(type="list", formula1='"%s"' % ",".join(OPCOES), allow_blank=True,
                        showErrorMessage=True, errorTitle="Validação", error="Escolha uma opção da lista.")
    ws.add_data_validation(dv)

    lin = hdr + 1
    for prog in progs:
        ws.merge_cells(start_row=lin, start_column=1, end_row=lin, end_column=4)
        cel = ws.cell(row=lin, column=1, value=prog)
        cel.font, cel.fill = Font(bold=True, color=AZUL), prog_fill
        for c in range(1, 5):
            ws.cell(row=lin, column=c).border = borda
        lin += 1
        for a in [x for x in rows if x["programa"] == prog]:
            vals = [a["ordem"], a["tipo_atividade"], None, None]
            for c, v in enumerate(vals, start=1):
                cel = ws.cell(row=lin, column=c, value=v)
                cel.border, cel.alignment = borda, wrap
            dv.add(ws.cell(row=lin, column=3))
            lin += 1
        for _ in range(LINHAS_NOVAS):
            for c in range(1, 5):
                cel = ws.cell(row=lin, column=c)
                cel.border, cel.fill, cel.alignment = borda, nova_fill, wrap
            ws.cell(row=lin, column=1, value="nova")
            ws.cell(row=lin, column=1).font = Font(italic=True, color="808080")
            dv.add(ws.cell(row=lin, column=3))
            lin += 1
        lin += 1

wb.active = 0
wb.save(OUT)
print(OUT, len(equipas), "folhas de equipa")
