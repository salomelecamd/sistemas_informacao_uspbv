import json, uuid, zipfile, os, sys, datetime

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

SITE = "https://snspt.sharepoint.com/sites/USPBaixoVouga-piloto_calendario_partilhado"
L_ATIV = "a6676e1a-3536-4ead-a52d-7ac9b95c6989"
L_PERF = "21e9bfd8-642f-47b9-905f-0e806fc415ac"
L_PLAN = "32523316-3300-4d5c-9a5a-e723e0887abe"
DRIVE = "b!QEPVNqzAMUOrE8INQX0FKfV6_3VCfN5GnQAQDOEa2y0WM1IyADNcTZpa5yPgiHq-"
EXCEL_SOURCE = "sites/snspt.sharepoint.com:/sites/USPBaixoVouga-piloto_calendario_partilhado:"
APP_URL = ("https://apps.powerapps.com/play/e/Default-22c84608-f01d-46c5-8024-63cc962e5f51/"
           "a/50d606a5-77cc-4e8b-a6ee-1ebd49de9840?tenantId=22c84608-f01d-46c5-8024-63cc962e5f51")
APIS = {"shared_sharepointonline": "SharePoint", "shared_office365": "Office 365 Outlook",
        "shared_excelonlinebusiness": "Excel Online (Business)"}
ICON = {"shared_sharepointonline": "https://connectoricons-prod.azureedge.net/releases/v1.0.1676/1.0.1676.3617/sharepointonline/icon.png",
        "shared_office365": "https://connectoricons-prod.azureedge.net/releases/v1.0.1682/1.0.1682.3647/office365/icon.png",
        "shared_excelonlinebusiness": "https://connectoricons-prod.azureedge.net/releases/v1.0.1680/1.0.1680.3632/excelonlinebusiness/icon.png"}

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


def conn(api, op, params, run_after=None, kind="OpenApiConnection"):
    return {"type": kind, "runAfter": run_after or {},
            "inputs": {"host": {"apiId": "/providers/Microsoft.PowerApps/apis/" + api, "connectionName": api,
                                "operationId": op},
                       "parameters": params, "authentication": "@parameters('$authentication')"}}


def sp(op, params, ra=None):
    return conn("shared_sharepointonline", op, params, ra)


def ol(op, params, ra=None, kind="OpenApiConnection"):
    return conn("shared_office365", op, params, ra, kind)


def rest(method, uri, body=None, ra=None, extra=None):
    h = {"Accept": "application/json;odata=nometadata", "Content-Type": "application/json;odata=nometadata"}
    if extra:
        h.update(extra)
    p = {"dataset": SITE, "parameters/method": method, "parameters/uri": uri, "parameters/headers": h}
    if body is not None:
        p["parameters/body"] = body
    return sp("HttpRequest", p, ra)


def compose(v, ra=None):
    return {"type": "Compose", "inputs": v, "runAfter": ra or {}}


def after(*names):
    return {n: ["Succeeded"] for n in names}


def cond(expr, yes, no=None, ra=None):
    return {"type": "If", "expression": expr, "actions": yes, "else": {"actions": no or {}}, "runAfter": ra or {}}


def append(var, value, ra=None):
    return {"type": "AppendToArrayVariable", "inputs": {"name": var, "value": value}, "runAfter": ra or {}}


TR = "triggerOutputs()?['body/{}']"
AUTOR = "toLower(triggerOutputs()?['body/Author/Email'])"
NOME_FICH = "triggerOutputs()?['body/{FilenameWithExtension}']"

# ---------------------------------------------------------------- linha a linha
L = "items('Para_cada_linha')"
F = lambda c: "%s?['%s']" % (L, c)
TXT = lambda c: "trim(string(coalesce(%s, '')))" % F(c)

linha = {}
linha["Data_txt"] = compose("@{if(contains(%s, '/'), concat(split(%s, '/')[2], '-', if(equals(length(split(%s, '/')[1]), 1), '0', ''), split(%s, '/')[1], '-', if(equals(length(split(%s, '/')[0]), 1), '0', ''), split(%s, '/')[0]), if(greaterOrEquals(length(%s), 10), substring(%s, 0, 10), %s))}"
                            % ((TXT("Data"),) * 9))
H = TXT("Hora")
linha["Hora_txt"] = compose("@{if(contains(%s, 'T'), substring(concat(split(%s, 'T')[1], '00000'), 0, 5), if(equals(length(%s), 4), concat('0', %s), if(greaterOrEquals(length(%s), 5), substring(%s, 0, 5), %s)))}"
                            % ((H,) * 7), after("Data_txt"))
linha["Emails"] = {"type": "Select", "runAfter": after("Hora_txt"),
                   "inputs": {"from": "@split(replace(replace(string(coalesce(%s, '')), ',', ';'), ' ', ''), ';')" % F("Participantes (emails)"),
                              "select": "@toLower(trim(item()))"}}
linha["Emails_preenchidos"] = {"type": "Query", "runAfter": after("Emails"),
                               "inputs": {"from": "@body('Emails')",
                                          "where": "@and(not(empty(item())), not(equals(first(split(item(), '@')), first(split(%s, '@')))))" % AUTOR}}
linha["Desconhecidos"] = {"type": "Query", "runAfter": after("Emails_preenchidos"),
                          "inputs": {"from": "@body('Emails_preenchidos')",
                                     "where": "@not(contains(body('Locais_perfis'), first(split(item(), '@'))))"}}
P = "toLower(%s)" % TXT("Eu participo")
linha["Participa"] = compose("@not(or(equals(%s, 'não'), equals(%s, 'nao'), equals(%s, 'n'), equals(%s, 'no')))" % (P, P, P, P),
                             after("Desconhecidos"))
D, HH = "outputs('Data_txt')", "outputs('Hora_txt')"
ok_data = "and(equals(length(%s), 10), isInt(substring(%s, 0, 4)), isInt(substring(%s, 5, 2)), isInt(substring(%s, 8, 2)))" % (D, D, D, D)
ok_hora = "and(equals(length(%s), 5), equals(substring(%s, 2, 1), ':'), isInt(substring(%s, 0, 2)), isInt(substring(%s, 3, 2)), less(int(if(isInt(substring(%s, 0, 2)), substring(%s, 0, 2), '99')), 24), less(int(if(isInt(substring(%s, 3, 2)), substring(%s, 3, 2), '99')), 60))" % ((HH,) * 8)
linha["Chave"] = compose("@{toLower(concat(%s, '|', %s, '|', %s, '|', %s, '|', %s))}" % (D, HH, TXT("Unidade"), TXT("Tipo de atividade"), AUTOR),
                         after("Participa"))
linha["Ja_existe"] = sp("GetItems", {"dataset": SITE, "table": L_ATIV,
                                     "$filter": "chave_importacao eq '@{replace(outputs('Chave'), '''', '''''')}'", "$top": 1},
                        after("Chave"))
linha["Erros_linha"] = compose(
    "@{concat("
    "if(%s, '', 'data inválida; '), "
    "if(%s, '', 'hora inválida (use hh:mm); '), "
    "if(contains(outputs('Lista_unidades'), %s), '', 'unidade desconhecida; '), "
    "if(contains(outputs('Lista_programas'), %s), '', 'programa desconhecido; '), "
    "if(contains(outputs('Lista_tipos'), %s), '', 'tipo de atividade desconhecido; '), "
    "if(empty(body('Desconhecidos')), '', concat('emails sem perfil: ', join(body('Desconhecidos'), ', '), '; ')), "
    "if(and(not(outputs('Participa')), empty(body('Emails_preenchidos'))), 'indique participantes (Eu participo = Não); ', ''), "
    "if(empty(outputs('Ja_existe')?['body/value']), '', 'já importada anteriormente; '))}"
    % (ok_data, ok_hora, TXT("Unidade"), TXT("Programa"), TXT("Tipo de atividade")), after("Ja_existe"))
DESC = "concat(outputs('Data_txt'), ' ', outputs('Hora_txt'), ' — ', %s, ' (', %s, ')')" % (TXT("Tipo de atividade"), TXT("Unidade"))
QUANDO = "convertToUtc(concat(outputs('Data_txt'), 'T', outputs('Hora_txt'), ':00'), 'GMT Standard Time')"
valida = {
    "Quando": compose("@{%s}" % QUANDO),
    "Futura": cond({"greater": ["@ticks(outputs('Quando'))", "@ticks(utcNow())"]},
                   {"Juntar_valida": append("Validas", {
                       "chave": "@outputs('Chave')", "quando": "@outputs('Quando')",
                       "duracao": "@int(if(isInt(%s), %s, '60'))" % (TXT("Duração (min)"), TXT("Duração (min)")),
                       "unidade": "@{%s}" % TXT("Unidade"), "programa": "@{%s}" % TXT("Programa"),
                       "tipo": "@{%s}" % TXT("Tipo de atividade"),
                       "concelho": "@if(contains(outputs('Lista_concelhos'), %s), %s, null)" % (TXT("Concelho"), TXT("Concelho")),
                       "local": "@{%s}" % TXT("Local"), "obs": "@{%s}" % TXT("Observações"),
                       "emails": "@body('Emails_preenchidos')", "participa": "@outputs('Participa')"})},
                   {"Juntar_passada": append("Erros", "@{%s}: data já passou" % DESC)}, after("Quando")),
}
linha["Valida"] = cond({"equals": ["@outputs('Erros_linha')", ""]}, valida,
                       {"Juntar_erro": append("Erros", "@{%s}: @{outputs('Erros_linha')}" % DESC)}, after("Erros_linha"))

# ---------------------------------------------------------------- criacao
C = "items('Criar_atividades')"
PERF_DE = lambda local: {"type": "Query", "runAfter": {}, "inputs": {"from": "@body('Perfis')?['value']",
                                                   "where": "@equals(first(split(toLower(coalesce(item()?['Email'], '')), '@')), %s)" % local}}
POLO = "if(equals(first(%s)?['Polo_x002f_Servi_x00e7_oUSP']?[0], 'Coordenação'), 'Coordenação USP', coalesce(first(%s)?['Polo_x002f_Servi_x00e7_oUSP']?[0], %s?['unidade']))"


def item_body(prof_id, cat, polo, registante, participa, chave):
    return {"Title": "@{outputs('Grupo')}", "data_hora": "@{%s?['quando']}" % C, "polo_servi_x00e7_o": polo,
            "profissionalId": prof_id, "categoria_profissional": cat, "programa": "@{%s?['programa']}" % C,
            "tipo_atividade": "@{%s?['tipo']}" % C, "concelho": "@%s?['concelho']" % C, "local": "@{%s?['local']}" % C,
            "duracao_minutos": "@%s?['duracao']" % C, "observacoes": "@{%s?['obs']}" % C, "estado": "Planeado",
            "registante": registante, "participa": participa, "n_adiamentos": 0, "chave_importacao": chave}


outro = {
    "Perfil_outro": PERF_DE("first(split(items('Para_cada_participante'), '@'))"),
    "Corpo_outro": compose(item_body("@first(body('Perfil_outro'))?['NomeId']",
                                     "@first(body('Perfil_outro'))?['CategoriaProfissional']",
                                     "@" + POLO % ("body('Perfil_outro')", "body('Perfil_outro')", C),
                                     False, True, None), after("Perfil_outro")),
    "Criar_outro": rest("POST", "_api/web/lists(guid'%s')/items" % L_ATIV, "@{string(outputs('Corpo_outro'))}",
                        after("Corpo_outro")),
}
criar = {
    "Grupo": compose("@{guid()}"),
    "Para_cada_participante": {"type": "Foreach", "foreach": "@%s?['emails']" % C, "runAfter": after("Grupo"),
                               "runtimeConfiguration": {"concurrency": {"repetitions": 1}}, "actions": outro},
    "Corpo_registante": compose(item_body("@body('Eu_sharepoint')?['Id']",
                                          "@first(body('Perfil_autor'))?['CategoriaProfissional']",
                                          "@{%s?['unidade']}" % C, True, "@%s?['participa']" % C,
                                          "@{%s?['chave']}" % C), after("Para_cada_participante")),
    "Criar_registante": rest("POST", "_api/web/lists(guid'%s')/items" % L_ATIV, "@{string(outputs('Corpo_registante'))}",
                             after("Corpo_registante")),
}


def marcar_ficheiro(texto, ra):
    return rest("POST", "_api/web/lists(guid'%s')/items(@{triggerOutputs()?['body/ID']})" % L_PLAN,
                "@{string(setProperty(json('{}'), 'resultado_importacao', %s))}" % texto, ra,
                {"IF-MATCH": "*", "X-HTTP-Method": "MERGE"})


def email(assunto, corpo, ra):
    return ol("SendEmailV2", {"emailMessage/To": "@{%s}" % AUTOR, "emailMessage/Subject": assunto,
                              "emailMessage/Body": corpo, "emailMessage/Importance": "Normal"}, ra)


ERROS_HTML = "@{if(empty(variables('Erros')), '<p>Sem linhas com erro.</p>', concat('<p><b>Linhas não importadas (' , length(variables('Erros')), '):</b></p><ul><li>', join(variables('Erros'), '</li><li>'), '</li></ul>'))}"
RODAPE = "<p style=\"color:#666;font-size:12px\">Ficheiro: @{%s}. Mensagem automática do Calendário Partilhado USP.</p>" % NOME_FICH

aprovado = {
    "Criar_atividades": {"type": "Foreach", "foreach": "@variables('Validas')", "runAfter": {},
                         "runtimeConfiguration": {"concurrency": {"repetitions": 1}}, "actions": criar},
    "Email_concluido": email("Planificação importada: @{length(variables('Validas'))} atividade(s) criada(s)",
                             "<p>As atividades aprovadas foram criadas na app. Os eventos e convites são enviados "
                             "pelos calendários das Unidades nos próximos minutos.</p>" + ERROS_HTML +
                             "<p><a href=\"%s\">Abrir a app</a></p>" % APP_URL + RODAPE, after("Criar_atividades")),
}
rejeitado = {
    "Email_rejeitado": email("Importação cancelada", "<p>Rejeitou a importação. Nada foi criado.</p>" + RODAPE, {}),
}
com_validas = {
    "Tabela": {"type": "Table", "runAfter": {}, "inputs": {"from": "@variables('Validas')", "format": "HTML", "columns": [
        {"header": "Data", "value": "@formatDateTime(convertFromUtc(item()?['quando'], 'GMT Standard Time'), 'dd/MM/yyyy HH:mm')"},
        {"header": "Duração", "value": "@{item()?['duracao']} min"},
        {"header": "Tipo", "value": "@item()?['tipo']"},
        {"header": "Unidade", "value": "@item()?['unidade']"},
        {"header": "Participantes", "value": "@join(item()?['emails'], ', ')"},
        {"header": "Eu participo", "value": "@if(item()?['participa'], 'Sim', 'Não')"}]}},
    "Pedir_aprovacao": ol("SendApprovalMail", {
        "approvalEmailSubscription/Message/To": "@{%s}" % AUTOR,
        "approvalEmailSubscription/Message/Subject": "Aprovar importação: @{length(variables('Validas'))} atividade(s) da planificação",
        "approvalEmailSubscription/Message/Options": "Aprovar, Rejeitar",
        "approvalEmailSubscription/Message/Body": "<p>O ficheiro <b>@{%s}</b> tem <b>@{length(variables('Validas'))}</b> atividade(s) "
                                     "válida(s), listadas abaixo. Se aprovar, são criadas na app como <b>Planeado</b> e os "
                                     "participantes recebem o convite do calendário da Unidade.</p>@{body('Tabela')}" % NOME_FICH
                                     + ERROS_HTML,
        "approvalEmailSubscription/Message/Importance": "Normal",
        "approvalEmailSubscription/Message/HideHTMLMessage": False}, after("Tabela"), "OpenApiConnectionWebhook"),
    "Decisao": cond({"equals": ["@body('Pedir_aprovacao')?['SelectedOption']", "Aprovar"]}, aprovado, rejeitado,
                    after("Pedir_aprovacao")),
}
sem_validas = {
    "Email_sem_validas": email("Planificação: nenhuma atividade importada",
                               "<p>Não foi encontrada nenhuma linha válida no ficheiro.</p>" + ERROS_HTML +
                               "<p>Corrija o ficheiro e carregue-o novamente.</p>" + RODAPE, {}),
}

acts = {}
acts["Validas"] = {"type": "InitializeVariable", "inputs": {"variables": [{"name": "Validas", "type": "array", "value": []}]},
                   "runAfter": {}}
acts["Erros"] = {"type": "InitializeVariable", "inputs": {"variables": [{"name": "Erros", "type": "array", "value": []}]},
                 "runAfter": after("Validas")}
acts["Lista_unidades"] = compose(UNIDADES, after("Erros"))
acts["Lista_programas"] = compose(PROGRAMAS, after("Lista_unidades"))
acts["Lista_tipos"] = compose(TIPOS, after("Lista_programas"))
acts["Lista_concelhos"] = compose(CONCELHOS, after("Lista_tipos"))
acts["Esperar"] = {"type": "Wait", "inputs": {"interval": {"count": 1, "unit": "Minute"}}, "runAfter": after("Lista_concelhos")}
acts["Perfis"] = rest("GET", "_api/web/lists(guid'%s')/items?$select=NomeId,Email,CategoriaProfissional,Polo_x002f_Servi_x00e7_oUSP&$top=1000" % L_PERF,
                      None, after("Esperar"))
acts["Locais_perfis"] = {"type": "Select", "runAfter": after("Perfis"),
                         "inputs": {"from": "@body('Perfis')?['value']",
                                    "select": "@first(split(toLower(coalesce(item()?['Email'], '')), '@'))"}}
acts["Perfil_autor"] = dict(PERF_DE("first(split(%s, '@'))" % AUTOR), runAfter=after("Locais_perfis"))
acts["Eu_sharepoint"] = rest("POST", "_api/web/ensureuser",
                             "@{string(setProperty(json('{}'), 'logonName', triggerOutputs()?['body/Author/Claims']))}",
                             after("Perfil_autor"))
acts["Ficheiro"] = sp("HttpRequest", {"dataset": SITE, "parameters/method": "GET",
                                      "parameters/uri": "_api/v2.0/drives/%s/root:/@{encodeUriComponent(%s)}?$select=id" % (DRIVE, NOME_FICH),
                                      "parameters/headers": {"Accept": "application/json"}}, after("Eu_sharepoint"))
acts["Ler_linhas"] = conn("shared_excelonlinebusiness", "GetItems",
                          {"source": EXCEL_SOURCE, "drive": DRIVE, "file": "@body('Ficheiro')?['id']",
                           "table": "Atividades", "dateTimeFormat": "ISO 8601"}, after("Ficheiro"))
acts["Ler_linhas"]["runtimeConfiguration"] = {"paginationPolicy": {"minimumItemCount": 2000}}
acts["Linhas"] = {"type": "Query", "runAfter": after("Ler_linhas"),
                  "inputs": {"from": "@outputs('Ler_linhas')?['body/value']",
                             "where": "@or(not(empty(trim(string(coalesce(item()?['Data'], ''))))), not(empty(trim(string(coalesce(item()?['Tipo de atividade'], ''))))))"}}
acts["Para_cada_linha"] = {"type": "Foreach", "foreach": "@body('Linhas')", "runAfter": after("Linhas"),
                           "runtimeConfiguration": {"concurrency": {"repetitions": 1}}, "actions": linha}
acts["Ha_validas"] = cond({"greater": ["@length(variables('Validas'))", 0]}, com_validas, sem_validas,
                          after("Para_cada_linha"))

trigger = {"Quando_e_carregado_um_ficheiro": {
    "type": "OpenApiConnection",
    "recurrence": {"interval": 1, "frequency": "Minute"},
    "splitOn": "@triggerOutputs()?['body/value']",
    "conditions": [{"expression": "@endsWith(toLower(triggerOutputs()?['body/{FilenameWithExtension}']), '.xlsx')"}],
    "runtimeConfiguration": {"concurrency": {"runs": 1}},
    "inputs": {"host": {"apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
                        "connectionName": "shared_sharepointonline", "operationId": "GetOnNewFileItems"},
               "parameters": {"dataset": SITE, "table": L_PLAN},
               "authentication": "@parameters('$authentication')"}}}

defn = {"$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {"$connections": {"defaultValue": {}, "type": "Object"},
                       "$authentication": {"defaultValue": {}, "type": "SecureObject"}},
        "triggers": trigger, "actions": acts}


def package(fname, display, desc, defn):
    flow_res, flow_id = str(uuid.uuid4()), str(uuid.uuid4())
    res, apis_map, conns_map, conn_refs, deps = {}, {}, {}, {}, []
    for api, nome in APIS.items():
        a_res, c_res = str(uuid.uuid4()), str(uuid.uuid4())
        res[a_res] = {"id": "/providers/Microsoft.PowerApps/apis/" + api, "name": api, "type": "Microsoft.PowerApps/apis",
                      "suggestedCreationType": "Existing", "details": {"displayName": nome, "iconUri": ICON[api]},
                      "configurableBy": "System", "hierarchy": "Child", "dependsOn": []}
        res[c_res] = {"type": "Microsoft.PowerApps/apis/connections", "suggestedCreationType": "Existing",
                      "creationType": "Existing", "details": {"displayName": nome, "iconUri": ICON[api]},
                      "configurableBy": "User", "hierarchy": "Child", "dependsOn": [a_res]}
        apis_map[api], conns_map[api] = a_res, c_res
        conn_refs[api] = {"connectionName": api.replace("shared_", "shared-") + "-placeholder", "source": "Embedded",
                          "id": "/providers/Microsoft.PowerApps/apis/" + api, "tier": "NotSpecified"}
        deps += [a_res, c_res]
    res[flow_res] = {"type": "Microsoft.Flow/flows", "suggestedCreationType": "New", "creationType": "Existing, New, Update",
                     "details": {"displayName": display}, "configurableBy": "User", "hierarchy": "Root", "dependsOn": deps}
    manifest = {"schema": "1.0", "details": {"displayName": display, "description": desc,
                                             "createdTime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.0000000Z"),
                                             "packageTelemetryId": str(uuid.uuid4()), "creator": "N/A", "sourceEnvironment": ""},
                "resources": res}
    flow_def = {"name": flow_id, "id": "/providers/Microsoft.Flow/flows/" + flow_id, "type": "Microsoft.Flow/flows",
                "properties": {"apiId": "/providers/Microsoft.PowerApps/apis/shared_logicflows", "displayName": display,
                               "definition": defn, "connectionReferences": conn_refs,
                               "flowFailureAlertSubscribed": False, "isManaged": False}}
    path = os.path.join(OUT, fname)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        z.writestr("Microsoft.Flow/flows/manifest.json",
                   json.dumps({"packageSchemaVersion": "1.0", "flowAssets": {"assetPaths": [flow_res]}}))
        base = "Microsoft.Flow/flows/%s/" % flow_res
        z.writestr(base + "definition.json", json.dumps(flow_def, ensure_ascii=False, indent=2))
        z.writestr(base + "apisMap.json", json.dumps(apis_map))
        z.writestr(base + "connectionsMap.json", json.dumps(conns_map))
    print(path)


package("fluxo_importar_planificacao.zip", "Calendário USP — Importar planificação anual",
        "Lê o Excel carregado em Planificação anual, valida, pede aprovação a quem o carregou e cria as atividades.", defn)
