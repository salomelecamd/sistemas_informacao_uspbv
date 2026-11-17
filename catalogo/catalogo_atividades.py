# Catálogo de atividades da USP Baixo Vouga, por Programa.
# Fonte: Relatório de Atividades 2025 (abril de 2026). Rascunho para validação pelas equipas.
# Natureza: Operacional | Gestão do programa | Reunião | Formação | Administrativa
import json
import sys

AREAS = {
    "VE": "Vigilância e investigação epidemiológica",
    "PSPD": "Proteção da saúde e prevenção da doença",
    "PS": "Promoção da saúde",
    "AS": "Autoridade de Saúde",
    "FIQ": "Formação, investigação e qualidade",
    "OUT": "Outros programas e colaborações",
    "TR": "Transversal (todos os programas)",
}

# sigla, nome, área, equipa que valida, nota para a equipa
PROGRAMAS = [
    ("DNO", "Vigilância Epidemiológica de DNO", "VE", "Médicos de Saúde Pública / Autoridades de Saúde", ""),
    ("PNV", "PNV e vacinação sazonal", "PSPD", "Núcleo de Vacinação", ""),
    ("SI", "Sanidade Internacional (Porto de Aveiro e CVI)", "PSPD", "Equipa de Sanidade Marítima (TSA/AS)", ""),
    ("PVSA", "PVSA (Águas)", "PSPD", "Equipa Gestora do PVSA", ""),
    ("PVAL", "PVAL (Legionella)", "PSPD", "Equipa Gestora do PVSA", "O relatório refere que o PVAL passa a integrar o PVSA em 2026. Confirmar se na app fica como programa próprio ou como atividades do PVSA."),
    ("PVSEAS", "PVSEAS (Estabelecimentos de Apoio Social)", "PSPD", "Equipa Gestora do PVSEAS", ""),
    ("REVIVE", "REVIVE (Vigilância de Vetores)", "PSPD", "Equipa Gestora do REVIVE", ""),
    ("PRSS", "PRSS (Resposta Sazonal em Saúde)", "PSPD", "Grupo Operativo Local do PRSS", ""),
    ("PSAC", "PSAC (Segurança Alimentar em Cantinas)", "PSPD", "Equipa Gestora do PSAC", ""),
    ("PGRH", "PGRH (Resíduos Hospitalares)", "PSPD", "Equipa Gestora do PGRH", "As auditorias não avançaram em 2025 (passam para o Sistema de Gestão Ambiental da ULS). Confirmar se se mantêm na app."),
    ("RAST", "Rastreios (oncológicos e visuais)", "PSPD", "Equipa de Coordenação Local dos Rastreios (ECLR)", ""),
    ("PNT", "Programa Nacional para a Tuberculose", "PSPD", "Equipa Coordenadora do PNT", ""),
    ("PNSE", "Saúde Escolar (PNSE)", "PS", "Equipa Coordenadora da Saúde Escolar (ECSE)", ""),
    ("PNPSO", "Saúde Oral (PNPSO)", "PS", "Equipa Coordenadora do PNPSO", ""),
    ("PNISTVIH", "IST e Infeção por VIH (PNISTVIH)", "PS", "Equipa local do PNISTVIH", ""),
    ("AS", "Autoridade de Saúde", "AS", "Autoridades de Saúde / Conselho Técnico", "Atividades sem programa próprio. Os tipos de parecer e de vistoria seguem as categorias do Quadro 22."),
    ("FIQ", "Formação, Investigação e Qualidade", "FIQ", "Núcleo de Formação da USP BV", ""),
    ("OUT", "Outros programas e colaborações", "OUT", "Conselho Técnico", "Participação de profissionais da USP em comissões e equipas de outras entidades (capítulo 7)."),
    ("TR", "Transversal", "TR", "Conselho Técnico", "Atividades que podem ocorrer em qualquer programa. Na app ficam disponíveis em todos."),
]

O, G, R, F, A = "Operacional", "Gestão do programa", "Reunião", "Formação", "Administrativa"

# (programa, tipo de atividade, natureza, quem, indicador/unidade, fonte)
ATIVIDADES = [
    # DNO - Quadro 1, p. 10
    ("DNO", "Validação de notificação SINAVE / inquérito epidemiológico", O, "MSP/AS", "N.º de IE validados", "Quadro 1, p. 10"),
    ("DNO", "Inquérito ambiental", O, "MSP/AS + TSA", "N.º de IA realizados", "Quadro 1, p. 10"),
    ("DNO", "Gestão de contactos e medidas de controlo", O, "MSP/AS", "N.º de casos com medidas", "Objetivos específicos, p. 9"),
    ("DNO", "Investigação e seguimento de surto", O, "MSP/AS + TSA", "N.º de surtos investigados", "Objetivos específicos, p. 9"),
    ("DNO", "Análise de dados e informação semestral", G, "Equipa", "Realizado (sim/não)", "Quadro 1, p. 10"),
    ("DNO", "Relatório anual de avaliação", G, "Equipa", "Realizado (sim/não)", "Quadro 1, p. 10"),
    # PNV - Quadro 2, p. 18-19
    ("PNV", "Ato de vacinação (PNV)", O, "Equipas das UF / USP", "N.º de vacinas administradas", "Enquadramento, p. 16"),
    ("PNV", "Gestão de stocks de vacinas", O, "Equipas das UF", "Realizado", "Quadro 2, p. 18"),
    ("PNV", "Manutenção da rede de frio", O, "Equipas das UF", "Realizado", "Quadro 2, p. 18"),
    ("PNV", "Monitorização de coberturas vacinais", G, "Núcleo de Vacinação", "Avaliação anual e semestral", "Quadro 2, p. 18"),
    ("PNV", "Convocatória de utentes", O, "Equipas das UF", "N.º de convocatórias", "Quadro 2, p. 18"),
    ("PNV", "Formação interna em vacinação", F, "Núcleo de Vacinação", "N.º de ações", "Quadro 2, p. 18"),
    ("PNV", "Curso de Vacinação (anual)", F, "Núcleo de Vacinação", "Realizado (sim/não)", "Quadro 2, p. 18"),
    ("PNV", "Vacinação sazonal (gripe/COVID-19) em ERPI e similares", O, "USP BV", "N.º de ERPI vacinados", "Quadro 2, p. 18"),
    ("PNV", "Vacinação BCG em grupos de risco", O, "USP BV", "N.º de utentes vacinados", "Quadro 2, p. 19"),
    ("PNV", "Atualização do cadastro vacinal (semestral)", G, "Equipas das UF", "Realizado", "Objetivos específicos, p. 17"),
    # Sanidade Internacional - Quadro 3, p. 22
    ("SI", "Concessão de livre prática", O, "TSA", "N.º de livres práticas", "Quadro 3, p. 22"),
    ("SI", "Desembaraço sanitário", O, "TSA", "N.º de desembaraços", "Quadro 3, p. 22"),
    ("SI", "Vistoria a navio (certificado sanitário)", O, "TSA", "N.º de vistorias", "Quadro 3, p. 22"),
    ("SI", "Emissão de certificado sanitário de navio", A, "TSA", "N.º de certificados", "Quadro 3, p. 22"),
    ("SI", "Emissão de fatura na JUL", A, "TSA", "N.º de faturas", "Quadro 3, p. 22"),
    ("SI", "Prorrogação de certificado", A, "TSA", "N.º de prorrogações", "Quadro 3, p. 22"),
    ("SI", "Vistoria bienal às instalações do Porto de Aveiro", O, "TSA/AS", "N.º de vistorias", "Quadro 3, p. 22"),
    ("SI", "Vacinação internacional (CVI)", O, "USP BV", "N.º de consultas/vacinas", "Objetivos gerais, p. 21"),
    # PVSA - Quadro 5, p. 26-27
    ("PVSA", "Reunião anual com os profissionais do programa", R, "Equipa Gestora + USP-SL", "N.º de reuniões", "Quadro 5, p. 26"),
    ("PVSA", "Elaboração/revisão de procedimentos", G, "Equipa Gestora", "Realizado (sim/não)", "Quadro 5, p. 26"),
    ("PVSA", "Programação de colheitas", G, "TSA", "Programação por USP-SL", "Quadro 5, p. 26"),
    ("PVSA", "Colheita - água para consumo humano", O, "TSA", "N.º de colheitas", "Quadro 5, p. 26; Quadro 6"),
    ("PVSA", "Colheita - piscinas", O, "TSA", "N.º de colheitas", "Quadro 5, p. 26; Quadro 7"),
    ("PVSA", "Colheita - águas minerais naturais / termas", O, "TSA", "N.º de colheitas", "Quadro 5, p. 26"),
    ("PVSA", "Colheita - água de nascente (oficina de engarrafamento)", O, "TSA", "N.º de colheitas", "Quadro 5, p. 26"),
    ("PVSA", "Colheita - zonas balneares", O, "TSA", "N.º de colheitas", "Quadro 5, p. 26; Quadro 8"),
    ("PVSA", "Vistoria / visita técnica (SA, piscinas, termas, OE, ZB)", O, "TSA/AS", "N.º de vistorias", "Enquadramento, p. 24"),
    ("PVSA", "Atualização de cadastro (SA, piscinas, OE, ZB, termas)", O, "TSA", "Cadastro atualizado", "Objetivos específicos, p. 25"),
    ("PVSA", "Registo de resultados analíticos", A, "TSA", "N.º de boletins registados", "Quadro 5, p. 27"),
    ("PVSA", "Gestão de incumprimento analítico", O, "TSA/AS", "N.º de incumprimentos comunicados", "Quadro 5, p. 27"),
    ("PVSA", "Promoção da saúde em piscinas e zonas balneares", O, "TSA", "N.º de ações", "Enquadramento, p. 24"),
    # PVAL - Quadro 12, p. 45-46
    ("PVAL", "Atualização de cadastro de estabelecimentos com risco de Legionella", O, "TSA/MSP/TSS", "Concelhos com cadastro atualizado", "Quadro 12, p. 45"),
    ("PVAL", "Identificação de equipamentos geradores de aerossóis", O, "TSA/MSP/TSS", "N.º de estabelecimentos caracterizados", "Quadro 12, p. 45"),
    ("PVAL", "Verificação do Plano de Prevenção e Controlo (Lei 52/2018)", O, "TSA/MSP/TSS", "N.º de planos recebidos", "Quadro 12, p. 45"),
    ("PVAL", "Georreferenciação de estabelecimentos", G, "Equipa Gestora", "Realizado (sim/não)", "Quadro 12, p. 46"),
    ("PVAL", "Calendarização anual de colheitas de Legionella", G, "Equipa Gestora", "Realizado (sim/não)", "Quadro 12, p. 46"),
    ("PVAL", "Colheita - Legionella", O, "TSA", "N.º de colheitas", "Quadro 5, p. 27"),
    ("PVAL", "Investigação ambiental de caso de Doença dos Legionários", O, "MSP + TSA/TSS", "N.º de casos investigados", "Quadro 12, p. 46"),
    # PVSEAS - Quadro 9, p. 33-34
    ("PVSEAS", "Atualização do cadastro de EAS", O, "TSA/MSP/TSS/EEEC", "Concelhos com cadastro atualizado", "Quadro 9, p. 33"),
    ("PVSEAS", "Vistoria a EAS (1.ª vistoria)", O, "TSA/MSP/TSS/EEEC", "N.º de EAS vistoriados", "Quadro 9, p. 33"),
    ("PVSEAS", "Vistoria a ERPI (1.ª vistoria, inclui vertente clínica e PBCI)", O, "TSA/MSP/TSS/EEEC", "N.º de ERPI vistoriadas", "Quadro 9, p. 33; Enquadramento, p. 31"),
    ("PVSEAS", "Relatório de vistoria", A, "Quem fez a vistoria", "N.º de relatórios", "Quadro 9, p. 33"),
    ("PVSEAS", "Comunicação de resultados / audiência prévia", A, "TSA/MSP/EEEC/TSS/AT", "N.º de comunicações", "Quadro 9, p. 33-34"),
    ("PVSEAS", "Vistoria de verificação (2.ª vistoria)", O, "TSA/MSP/TSS/EEEC", "N.º de 2.as vistorias", "Quadro 9, p. 34"),
    ("PVSEAS", "Análise de dados, avaliação e revisão de procedimentos", G, "Equipa Gestora", "Realizado (sim/não)", "Quadro 9, p. 34"),
    # REVIVE - Quadro 10, p. 37-38
    ("REVIVE", "Armadilhas CDC - culicídeos", O, "TSA", "N.º de armadilhas", "Quadro 10, p. 37"),
    ("REVIVE", "Armadilhas BG - Porto de Aveiro (Aedes albopictus)", O, "TSA", "N.º de armadilhas", "Quadro 10, p. 37"),
    ("REVIVE", "Rede de ovitraps - Porto de Aveiro", O, "TSA", "N.º de redes", "Quadro 10, p. 37"),
    ("REVIVE", "Saída de campo - captura de mosquitos imaturos", O, "TSA", "N.º de saídas", "Quadro 10, p. 37"),
    ("REVIVE", "Armadilhas CDC - flebótomos", O, "TSA", "N.º de armadilhas", "Quadro 10, p. 37"),
    ("REVIVE", "Saída de campo - captura de carraças", O, "TSA", "N.º de saídas", "Quadro 10, p. 37"),
    ("REVIVE", "Sessão em escola - literacia sobre vetores", O, "TSA e EEEC/SP", "N.º de alunos abrangidos", "Quadro 10, p. 38"),
    # PRSS - Quadro 11, p. 41-42
    ("PRSS", "Elaboração do Plano de Contingência (verão/inverno)", G, "Profissionais no GOL", "Plano elaborado", "Quadro 11, p. 41"),
    ("PRSS", "Divulgação do Plano de Contingência", G, "GOL da ULS", "Plano divulgado", "Quadro 11, p. 41"),
    ("PRSS", "Comunicação de alerta (calor/frio) às instituições", O, "Autoridades de Saúde Locais", "N.º de alertas", "Quadro 11, p. 41"),
    ("PRSS", "Reunião do Grupo Operativo Local (GOL)", R, "Profissionais no GOL", "N.º de reuniões", "Discussão, p. 42"),
    ("PRSS", "Reunião de acompanhamento com DGS/DE-SNS", R, "Profissionais no GOL", "N.º de reuniões", "Discussão, p. 42"),
    ("PRSS", "Relatório semanal da resposta sazonal", A, "Profissionais no GOL", "N.º de relatórios", "Discussão, p. 42"),
    # PSAC - Quadro 13, p. 49-51
    ("PSAC", "Reunião com os profissionais do programa", R, "Equipa Gestora", "N.º de reuniões", "Quadro 13, p. 49"),
    ("PSAC", "Levantamento de recursos materiais", G, "USP-SL", "Realizado (sim/não)", "Quadro 13, p. 49"),
    ("PSAC", "Atualização do cadastro de cantinas", O, "USP-SL", "N.º de cantinas atualizadas", "Quadro 13, p. 49"),
    ("PSAC", "Seleção de cantinas para vigilância microbiológica", G, "Equipa Gestora + USP-SL", "Lista enviada", "Quadro 13, p. 49"),
    ("PSAC", "Revisão da ficha de diagnóstico", G, "Equipa Gestora", "Realizado (sim/não)", "Quadro 13, p. 49"),
    ("PSAC", "Vistoria a cantina (ficha de diagnóstico)", O, "USP-SL", "N.º de cantinas vistoriadas", "Quadro 13, p. 50"),
    ("PSAC", "Notificação de deficiências na cantina", A, "USP-SL", "N.º de notificações", "Quadro 13, p. 50"),
    ("PSAC", "Programação de colheitas em cantinas", G, "TSA", "Realizado (sim/não)", "Quadro 13, p. 51"),
    ("PSAC", "Colheita em cantina (alimentos, superfícies, mãos)", O, "USP-SL", "N.º de colheitas", "Quadro 13, p. 51; Quadro 14"),
    ("PSAC", "Notificação de resultados não satisfatórios", A, "USP-SL", "N.º de relatórios de recomendações", "Quadro 13, p. 51"),
    ("PSAC", "Formação de manipuladores de alimentos", F, "USP-SL", "N.º de ações", "Enquadramento, p. 48"),
    ("PSAC", "Avaliação do programa (relatório/infografia)", G, "Equipa Gestora", "Realizado (sim/não)", "Quadro 13, p. 51"),
    # PGRH - Quadro 15, p. 54
    ("PGRH", "Divulgação de procedimentos de gestão de RH", G, "Equipa Gestora", "Informação divulgada", "Quadro 15, p. 54"),
    ("PGRH", "Auditoria aos procedimentos numa UF", O, "Equipa Gestora + USP-SL", "N.º de UF auditadas", "Quadro 15, p. 54"),
    ("PGRH", "Relatório de auditoria", A, "Equipa Gestora + USP-SL", "N.º de relatórios", "Quadro 15, p. 54"),
    ("PGRH", "Tratamento de dados de produção e custos de RH", G, "Equipa Gestora", "Informação divulgada", "Quadro 15, p. 54"),
    # Rastreios - Quadro 17, p. 59-60
    ("RAST", "Reunião ECLR com Direção Clínica / serviços hospitalares", R, "ECLR", "N.º de reuniões", "Quadro 17, p. 59"),
    ("RAST", "Reunião formativa sobre RCCR", F, "ECLR", "N.º de formações", "Quadro 17, p. 59"),
    ("RAST", "Entrega de material RCCR às UF", O, "ECLR", "N.º de UF", "Quadro 17, p. 59"),
    ("RAST", "Apoio às UF (dificuldades e necessidades)", O, "ECLR", "N.º de respostas", "Quadro 17, p. 59"),
    ("RAST", "Monitorização de convites e rastreados (RCM, RCCU, RCCR)", G, "ECLR", "N.º de UF monitorizadas", "Quadro 17, p. 59-60"),
    ("RAST", "Reunião formativa sobre RSVI", F, "ECLR + Equipa Regional", "N.º de reuniões", "Quadro 17, p. 60"),
    ("RAST", "Rastreio de Saúde Visual Infantil (RSVI)", O, "Enfermeiros de SP", "N.º de crianças rastreadas", "Discussão, p. 61"),
    ("RAST", "Validação de resultados do RSVI", O, "Enfermeiros de SP", "N.º de resultados validados", "Discussão, p. 61"),
    ("RAST", "Relatório de monitorização (semestral/anual)", G, "ECLR", "Realizado (sim/não)", "Quadro 17, p. 60"),
    ("RAST", "Rastreio da Retinopatia Diabética", O, "ECLR", "N.º de rastreados", "Discussão, p. 61 (suspenso)"),
    # PNT - Quadro 18, p. 66
    ("PNT", "Formação sobre tuberculose (médicos e enfermeiros)", F, "Equipa Coordenadora", "N.º de ações", "Quadro 18, p. 66"),
    ("PNT", "Inquérito epidemiológico de caso de tuberculose", O, "Equipa Coordenadora", "N.º de IE", "Quadro 18, p. 66"),
    ("PNT", "Identificação de grupos de risco", G, "Equipa Coordenadora", "Realizado (sim/não)", "Quadro 18, p. 66"),
    ("PNT", "Elaboração da lista de contactos de risco", O, "Equipa Coordenadora", "N.º de listas", "Quadro 18, p. 66"),
    ("PNT", "Rastreio de contactos de risco", O, "Equipa Coordenadora", "N.º de contactos rastreados", "Quadro 18, p. 66"),
    ("PNT", "Rastreio de grupo de risco", O, "Equipa Coordenadora", "N.º de rastreios", "Quadro 18, p. 66"),
    ("PNT", "Reunião com CRC-B / serviços de internamento", R, "Equipa Coordenadora", "N.º de reuniões", "Estratégias, p. 65"),
    # PNSE - Quadro 19, p. 70-72
    ("PNSE", "Reunião da ECSE com as ELSE", R, "ECSE", "N.º de reuniões", "Quadro 19, p. 70"),
    ("PNSE", "Reunião ELSE com Agrupamento/PES", R, "ELSE", "N.º de reuniões", "Quadro 19, p. 70"),
    ("PNSE", "Sessão de educação para a saúde (projeto PES)", O, "ELSE", "N.º de sessões / alunos abrangidos", "Quadro 19, p. 70"),
    ("PNSE", "Campanha / material de literacia em saúde", O, "ECSE/ELSE", "N.º de campanhas", "Quadro 19, p. 71"),
    ("PNSE", "Vistoria de avaliação de risco do ambiente escolar", O, "ELSE", "N.º de EEE avaliados", "Quadro 19, p. 71"),
    ("PNSE", "Avaliação de acidente escolar", O, "ELSE", "N.º de acidentes avaliados", "Quadro 19, p. 71"),
    ("PNSE", "Formação em primeiros socorros / SBV nas escolas", F, "ELSE/Parceiros", "N.º de formandos", "Quadro 19, p. 71"),
    ("PNSE", "Plano de Saúde Individual (NSE)", O, "ELSE/Parceiros", "N.º de PSI elaborados", "Quadro 19, p. 71"),
    ("PNSE", "Formação de profissionais de saúde em Saúde Escolar", F, "ECSE", "N.º de ações", "Quadro 19, p. 71"),
    ("PNSE", "Formação de professores (Centros de Formação)", F, "ECSE", "N.º de formações", "Quadro 19, p. 71-72"),
    ("PNSE", "Parceria / protocolo com instituição científica", R, "ECSE", "N.º de parcerias", "Quadro 19, p. 72"),
    # PNPSO - Quadro 20, p. 76-77
    ("PNPSO", "Consulta de medicina dentária / higiene oral", O, "Médicos dentistas / Higienistas orais", "N.º de consultas", "Discussão, p. 78"),
    ("PNPSO", "Ação de promoção da saúde oral", O, "Médicos, enfermeiros, higienistas, dentistas", "N.º de ações", "Quadro 20, p. 76"),
    ("PNPSO", "Aplicação de verniz de flúor (pré-escolar)", O, "Higienistas orais", "N.º de crianças", "Quadro 20, p. 76"),
    ("PNPSO", "Kits de escovagem - formação e distribuição", O, "ELSE / Higienistas orais", "N.º de crianças", "Quadro 20, p. 77"),
    ("PNPSO", "Emissão / promoção do cheque-dentista", A, "Equipa Coordenadora", "N.º de cheques / envios", "Quadro 20, p. 76-77"),
    ("PNPSO", "Reunião da ECSE (elo de ligação do PNPSO)", R, "Elo de ligação", "N.º de reuniões", "Quadro 20, p. 76"),
    ("PNPSO", "Elaboração de procedimento, guia ou material informativo", G, "Equipa Coordenadora", "Documento elaborado", "Quadro 20, p. 76-77"),
    ("PNPSO", "Formação PNPSO a médicos e enfermeiros da USP", F, "Equipa Coordenadora", "Realizado (sim/não)", "Quadro 20, p. 77"),
    # PNISTVIH - Quadro 21, p. 82-84
    ("PNISTVIH", "Monitorização de testes IST/VIH, PrEP e casos", G, "Equipa local", "Dados compilados", "Quadro 21, p. 82"),
    ("PNISTVIH", "Distribuição de preservativos", O, "Equipa local", "N.º de preservativos", "Quadro 21, p. 83"),
    ("PNISTVIH", "Campanha de informação (redes sociais / rádio)", O, "Equipa local", "N.º de campanhas", "Quadro 21, p. 83"),
    ("PNISTVIH", "Evento de sensibilização em local público", O, "Equipa local", "N.º de eventos", "Quadro 21, p. 83"),
    ("PNISTVIH", "Implementação de ponto de testagem", G, "Equipa local + Direção Clínica", "N.º de pontos", "Quadro 21, p. 83"),
    ("PNISTVIH", "Dia de teste comunitário", O, "Equipa local + ONG", "N.º de testes", "Quadro 21, p. 83"),
    ("PNISTVIH", "Reunião / parceria com ONG", R, "Equipa local + ONG", "N.º de reuniões", "Quadro 21, p. 83"),
    ("PNISTVIH", "Sessão em escola - afetos e sexualidade", O, "ELSE", "N.º de alunos", "Quadro 21, p. 83"),
    ("PNISTVIH", "Intervenção em contexto universitário", O, "Equipa local + UA", "N.º de ações", "Quadro 21, p. 83"),
    ("PNISTVIH", "Reunião sobre adesão ao tratamento", R, "Equipa local + Doenças Infeciosas", "N.º de reuniões", "Quadro 21, p. 84"),
    ("PNISTVIH", "Vacinação mpox (consulta e inoculação)", O, "Enfermeiros USP", "N.º de consultas / inoculações", "Quadro 21, p. 84"),
    # Autoridade de Saúde - Quadro 22, p. 88-90
    ("AS", "Avaliação médica para a condução / atestado", O, "Autoridade de Saúde", "N.º de atestados", "Quadro 22, p. 88"),
    ("AS", "Avaliação de saúde mental (pedido / mandado de condução)", O, "Autoridade de Saúde", "N.º de pedidos / mandados", "Quadro 22, p. 88"),
    ("AS", "Verificação de óbito", O, "Autoridade de Saúde", "N.º de óbitos verificados", "Quadro 22, p. 88"),
    ("AS", "Atestado de trasladação / remoção", A, "Autoridade de Saúde", "N.º de atestados", "Quadro 22, p. 88"),
    ("AS", "Parecer - estabelecimento industrial", O, "Autoridade de Saúde", "N.º de pareceres", "Quadro 22, p. 88"),
    ("AS", "Parecer - estabelecimento de saúde", O, "Autoridade de Saúde", "N.º de pareceres", "Quadro 22, p. 88"),
    ("AS", "Parecer - estabelecimento de educação e ensino", O, "Autoridade de Saúde", "N.º de pareceres", "Quadro 22, p. 88"),
    ("AS", "Parecer - estabelecimento de apoio social", O, "Autoridade de Saúde", "N.º de pareceres", "Quadro 22, p. 88"),
    ("AS", "Parecer - agropecuária (REAP/NREAP)", O, "Autoridade de Saúde", "N.º de pareceres", "Quadro 22, p. 89"),
    ("AS", "Parecer - avaliação de impacte ambiental", O, "Autoridade de Saúde", "N.º de pareceres", "Quadro 22, p. 89"),
    ("AS", "Parecer - outro", O, "Autoridade de Saúde", "N.º de pareceres", "Quadro 22, p. 89"),
    ("AS", "Vistoria - estabelecimento industrial (entidade coordenadora)", O, "AS / TSA", "N.º de vistorias", "Quadro 22, p. 89"),
    ("AS", "Vistoria - agropecuária", O, "AS / TSA", "N.º de vistorias", "Quadro 22, p. 89"),
    ("AS", "Vistoria - EAS (fora do PVSEAS)", O, "AS / TSA", "N.º de vistorias", "Quadro 22, p. 89"),
    ("AS", "Vistoria - estabelecimento de educação e ensino", O, "AS / TSA", "N.º de vistorias", "Quadro 22, p. 89"),
    ("AS", "Vistoria - cantina (fora do PSAC)", O, "AS / TSA", "N.º de vistorias", "Quadro 22, p. 89"),
    ("AS", "Vistoria - estabelecimento privado de saúde", O, "AS / TSA", "N.º de vistorias", "Quadro 22, p. 89"),
    ("AS", "Vistoria conjunta com a ASAE", O, "AS / TSA", "N.º de vistorias", "Quadro 22, p. 89"),
    ("AS", "Vistoria - evento (feira, festa, festival, campo de férias)", O, "AS / TSA", "N.º de vistorias", "Quadro 22, p. 89"),
    ("AS", "Vistoria - praia ou parque aquático (fora do PVSA)", O, "AS / TSA", "N.º de vistorias", "Quadro 22, p. 89"),
    ("AS", "Vistoria - habitabilidade (pedido do Ministério Público)", O, "AS / TSA", "N.º de vistorias", "Quadro 22, p. 90"),
    ("AS", "Visita técnica - avaliação de impacte ambiental", O, "AS / TSA", "N.º de visitas", "Quadro 22, p. 90"),
    ("AS", "Vistoria - outra (fontanários, acampamentos, espaços de jogo)", O, "AS / TSA", "N.º de vistorias", "Quadro 22, p. 90"),
    ("AS", "Reunião - Conselho Municipal de Educação", R, "Autoridade de Saúde", "N.º de reuniões", "Quadro 22, p. 90"),
    ("AS", "Reunião - Conselho Municipal de Segurança", R, "Autoridade de Saúde", "N.º de reuniões", "Quadro 22, p. 90"),
    ("AS", "Reunião - Comissão Municipal de Proteção Civil", R, "Autoridade de Saúde", "N.º de reuniões", "Quadro 22, p. 90"),
    ("AS", "Reunião - outra entidade (rede social, ONG, EAS)", R, "Autoridade de Saúde", "N.º de reuniões", "Quadro 22, p. 90"),
    ("AS", "Atividade formativa para serviços da ULSRA", F, "Autoridade de Saúde", "N.º de atividades", "Quadro 22, p. 90"),
    ("AS", "Atividade formativa para entidades externas", F, "Autoridade de Saúde", "N.º de atividades", "Quadro 22, p. 90"),
    # Formação, Investigação e Qualidade - Quadro 23, p. 93
    ("FIQ", "Elaboração do caderno de formação", G, "Núcleo de Formação", "Elaborado (sim/não)", "Quadro 23, p. 93"),
    ("FIQ", "Ação de formação interna (como formador)", F, "Núcleo e formadores", "N.º de ações", "Quadro 23, p. 93"),
    ("FIQ", "Frequência de formação externa", F, "Profissionais da USP", "N.º de ações frequentadas", "Discussão, p. 94"),
    ("FIQ", "Avaliação da formação", G, "Núcleo de Formação", "N.º de cursos avaliados", "Quadro 23, p. 93"),
    ("FIQ", "Partilha de formação em reunião da USP", R, "Profissionais da USP", "N.º de partilhas", "Quadro 23, p. 93"),
    ("FIQ", "Orientação de estágio", F, "Profissionais da USP", "N.º de estagiários", "Introdução, p. 8"),
    ("FIQ", "Projeto de investigação ou de melhoria da qualidade", G, "Profissionais da USP", "N.º de projetos", "Introdução, p. 8"),
    # Outros programas e colaborações - capítulo 7, p. 95
    ("OUT", "Comissão Municipal de Saúde", R, "Profissionais da USP", "N.º de reuniões", "Cap. 7, p. 95"),
    ("OUT", "Comissão Sub-Regional de Proteção Civil", R, "Profissionais da USP", "N.º de reuniões", "Cap. 7, p. 95"),
    ("OUT", "PPCIRA (Unidade Local)", R, "Profissionais da USP", "N.º de reuniões", "Cap. 7, p. 95"),
    ("OUT", "Programa Nacional da Diabetes (equipa local)", R, "Profissionais da USP", "N.º de reuniões", "Cap. 7, p. 95"),
    ("OUT", "Projeto IMPULSO (ponto focal)", R, "Profissionais da USP", "N.º de reuniões", "Cap. 7, p. 95"),
    ("OUT", "Comissão de Qualidade e Segurança da ULSRA", R, "Profissionais da USP", "N.º de reuniões", "Cap. 7, p. 95"),
    ("OUT", "Colaboração com a DGS (CESP, Alimentação Saudável)", R, "Profissionais da USP", "N.º de reuniões", "Cap. 7, p. 95"),
    ("OUT", "Comissão de Ética (CAC Egas Moniz)", R, "Profissionais da USP", "N.º de reuniões", "Cap. 7, p. 95"),
    ("OUT", "Prevenção da Violência no Setor da Saúde", R, "Profissionais da USP", "N.º de reuniões", "Cap. 7, p. 95"),
    ("OUT", "Estratificação pelo Risco da ULSRA (interlocutor)", R, "Profissionais da USP", "N.º de reuniões", "Cap. 7, p. 95"),
    ("OUT", "Gabinete de Investigação da ULSRA", R, "Profissionais da USP", "N.º de reuniões", "Cap. 7, p. 95"),
    # Transversal (já usadas na app)
    ("TR", "Reunião de coordenação / Conselho Geral da USP", R, "Todos", "N.º de reuniões", "App atual"),
    ("TR", "Reunião institucional", R, "Todos", "N.º de reuniões", "App atual"),
    ("TR", "Atividade formativa", F, "Todos", "N.º de atividades", "App atual"),
    ("TR", "Apoio administrativo", A, "Todos", "Horas", "App atual"),
    ("TR", "Atendimento ao público", O, "Todos", "N.º de atendimentos", "App atual"),
    ("TR", "Gestão de processos", A, "Todos", "Horas", "App atual"),
    ("TR", "Visita aos polos", O, "Coordenação", "N.º de visitas", "App atual"),
    ("TR", "Relatório de gestão / atividades", G, "Todos", "Realizado (sim/não)", "App atual"),
]


def linhas():
    prog = {p[0]: p for p in PROGRAMAS}
    out = []
    for i, (sig, tipo, nat, quem, ind, fonte) in enumerate(ATIVIDADES, start=1):
        p = prog[sig]
        out.append({
            "ordem": i, "area": AREAS[p[2]], "programa_sigla": sig, "programa": p[1],
            "tipo_atividade": tipo, "natureza": nat, "quem": quem, "indicador": ind,
            "fonte": fonte, "equipa_validacao": p[3],
        })
    return out


if __name__ == "__main__":
    dados = {"programas": [dict(sigla=s, nome=n, area=AREAS[a], equipa=e, nota=t) for s, n, a, e, t in PROGRAMAS],
             "atividades": linhas()}
    with open(sys.argv[1], "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)
    print(len(dados["programas"]), "programas;", len(dados["atividades"]), "atividades")
