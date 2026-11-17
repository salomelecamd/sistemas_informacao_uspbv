import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.worksheet.datavalidation import DataValidation

OUT = sys.argv[1]

UNIDADES = ["Estarreja", "Vagos", "Albergaria-A-Velha", "Oliveira do Bairro", "Anadia", "CVI", "Sede USP", "Aveiro",
            "Coordenação USP", "Equipa Gestora PVSA", "EGQ", "Equipa Gestora PNV e VS"]
PROGRAMAS = ["PNV e vacinação sazonal", "PVSA (Águas)", "Autoridade de Saúde", "Sem programa específico"]
TIPOS = ["Ato de vacinação (PNV)", "Vacinação sazonal em EAS", "Gestão de stocks/rede de frio", "Convocatória de utentes",
         "Monitorização de coberturas", "Colheita - consumo humano", "Colheita - piscinas", "Colheita - zonas balneares",
         "Colheita - mineral/nascente", "Inspeção/vistoria (PVSA)", "Avaliação médica/atestado (condução)",
         "Avaliação de saúde mental (mandado/internamento)", "Verificação de óbito", "Emissão de parecer",
         "Vistoria/inspeção (Autoridade de Saúde)", "Reunião institucional", "Atividade formativa",
         "Reunião de coordenação", "Apoio administrativo", "Atendimento ao público", "Gestão de processos",
         "Visita domiciliária", "Rastreio", "Sensibilização/Educação para a saúde", "Inquérito epidemiológico",
         "Vigilância epidemiológica", "Consulta de SP", "Vacinação (fora do PNV)", "Inspeção sanitária",
         "Colheita de amostras", "Vistoria", "Fiscalização", "Relatório de gestão", "Visita aos polos"]
CONCELHOS = ["Águeda", "Albergaria-A-Velha", "Anadia", "Aveiro", "Estarreja", "Ílhavo", "Murtosa", "Oliveira do Bairro",
             "Sever do Vouga", "Vagos", "Fora área abrangência DSP"]
COLS = ["Data", "Hora", "Duração (min)", "Unidade", "Programa", "Tipo de atividade", "Participantes (emails)",
        "Eu participo", "Concelho", "Local", "Observações"]
WID = [12, 8, 13, 22, 24, 38, 48, 12, 22, 26, 36]

wb = Workbook()
ws = wb.active
ws.title = "Planificação"
for i, (c, w) in enumerate(zip(COLS, WID), start=1):
    ws.cell(row=1, column=i, value=c)
    ws.column_dimensions[ws.cell(row=1, column=i).column_letter].width = w
N = 400
for r in range(2, N + 2):
    ws.cell(row=r, column=1).number_format = "dd/mm/yyyy"
    ws.cell(row=r, column=2).number_format = "@"
    ws.cell(row=r, column=7).number_format = "@"
tab = Table(displayName="Atividades", ref="A1:K2")
tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
ws.add_table(tab)
ws.freeze_panes = "A2"

ls = wb.create_sheet("Listas")
for col, (titulo, vals) in enumerate([("Unidade", UNIDADES), ("Programa", PROGRAMAS), ("Tipo de atividade", TIPOS),
                                       ("Concelho", CONCELHOS), ("Sim/Não", ["Sim", "Não"])], start=1):
    ls.cell(row=1, column=col, value=titulo).font = Font(bold=True)
    for i, v in enumerate(vals, start=2):
        ls.cell(row=i, column=col, value=v)
    ls.column_dimensions[ls.cell(row=1, column=col).column_letter].width = 40


def lista(col_letter, n, alvo, titulo, msg):
    dv = DataValidation(type="list", formula1="=Listas!$%s$2:$%s$%d" % (col_letter, col_letter, n + 1),
                        allow_blank=True, showErrorMessage=True, errorTitle=titulo,
                        error="Escolha um valor da lista.", promptTitle=titulo, prompt=msg, showInputMessage=True)
    dv.add("%s2:%s%d" % (alvo, alvo, N + 1))
    ws.add_data_validation(dv)


lista("A", len(UNIDADES), "D", "Unidade", "Unidade cujo calendário recebe o evento.")
lista("B", len(PROGRAMAS), "E", "Programa", "Escolha o programa.")
lista("C", len(TIPOS), "F", "Tipo de atividade", "Escolha o tipo de atividade.")
lista("D", len(CONCELHOS), "I", "Concelho", "Opcional.")
lista("E", 2, "H", "Eu participo", "Sim se quem envia o ficheiro também participa. Vazio = Sim.")
dv = DataValidation(type="date", operator="greaterThan", formula1="DATE(2025,1,1)", showErrorMessage=True,
                    errorTitle="Data", error="Escreva uma data (dd/mm/aaaa).", promptTitle="Data",
                    prompt="dd/mm/aaaa — uma linha por data.", showInputMessage=True)
dv.add("A2:A%d" % (N + 1)); ws.add_data_validation(dv)
dv = DataValidation(type="whole", operator="between", formula1="5", formula2="720", showErrorMessage=True,
                    errorTitle="Duração", error="Minutos entre 5 e 720.", promptTitle="Duração (min)",
                    prompt="Em minutos. Vazio = 60.", showInputMessage=True)
dv.add("C2:C%d" % (N + 1)); ws.add_data_validation(dv)
dv = DataValidation(type="custom", formula1='AND(LEN(B2)=5,MID(B2,3,1)=":")', allow_blank=True, showErrorMessage=True,
                    errorTitle="Hora", error="Escreva a hora como hh:mm, por exemplo 09:30.", promptTitle="Hora",
                    prompt="hh:mm, por exemplo 09:30.", showInputMessage=True)
dv.add("B2:B%d" % (N + 1)); ws.add_data_validation(dv)
dv = DataValidation(type="custom", formula1="TRUE", allow_blank=True, promptTitle="Participantes",
                    prompt="Emails institucionais separados por ; (sem contar consigo).", showInputMessage=True)
dv.add("G2:G%d" % (N + 1)); ws.add_data_validation(dv)

ins = wb.create_sheet("Instruções", 0)
ins.column_dimensions["A"].width = 120
linhas = [
    ("Planificação anual — importação para o Calendário Partilhado USP", True),
    ("", False),
    ("1. Preencha a folha «Planificação»: uma linha por atividade (uma colheita mensal = 12 linhas).", False),
    ("2. Obrigatório: Data, Hora (hh:mm), Unidade, Programa e Tipo de atividade. Duração vazia = 60 min.", False),
    ("3. Participantes: emails institucionais separados por ; — não precisa de se incluir a si.", False),
    ("4. «Eu participo»: Não se só está a organizar/registar. Vazio = Sim.", False),
    ("5. Guarde o ficheiro e carregue-o na biblioteca «Planificação anual» do site do piloto (botão na app).", False),
    ("6. Recebe um email com o resumo (atividades válidas e linhas com erro) e um botão Aprovar / Rejeitar.", False),
    ("7. Só depois de Aprovar as atividades são criadas na app e os convites enviados pelo calendário da Unidade.", False),
    ("", False),
    ("Notas: só são importadas datas futuras. Carregar o mesmo ficheiro outra vez não duplica atividades.", False),
    ("Não mude o nome das colunas nem da tabela «Atividades».", False),
]
for i, (t, b) in enumerate(linhas, start=1):
    c = ins.cell(row=i, column=1, value=t)
    c.font = Font(bold=b, size=14 if b else 11)
    c.alignment = Alignment(wrap_text=True)
ins.cell(row=14, column=1, value="Exemplo de linha:").font = Font(bold=True)
ins.cell(row=15, column=1, value="03/11/2026 | 09:30 | 90 | Vagos | PVSA (Águas) | Colheita - consumo humano | "
                                 "nome.apelido@ulsra.min-saude.pt; outro.nome@ulsra.min-saude.pt | Sim | Vagos | ETAR Vagos | ")
wb.active = 1
wb.save(OUT)
print(OUT)
