import json, uuid, zipfile, os, sys, datetime

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

SITE = "https://snspt.sharepoint.com/sites/USPBaixoVouga-piloto_calendario_partilhado"
L_ATIV = "a6676e1a-3536-4ead-a52d-7ac9b95c6989"
L_UNID = "521d9acb-0860-4924-b6ad-8deea2965548"
FALLBACK = "USP.BV@ulsra.min-saude.pt"
APP_URL = ("https://apps.powerapps.com/play/e/Default-22c84608-f01d-46c5-8024-63cc962e5f51/"
           "a/50d606a5-77cc-4e8b-a6ee-1ebd49de9840?tenantId=22c84608-f01d-46c5-8024-63cc962e5f51")
SP = "/providers/Microsoft.PowerApps/apis/shared_sharepointonline"
OL = "/providers/Microsoft.PowerApps/apis/shared_office365"
T = "triggerOutputs()?['body/{}']"


def tr(f):
    return T.format(f)


def sp(op, params, run_after=None):
    a = {"type": "OpenApiConnection",
         "inputs": {"host": {"apiId": SP, "connectionName": "shared_sharepointonline", "operationId": op},
                    "parameters": params, "authentication": "@parameters('$authentication')"}}
    a["runAfter"] = run_after or {}
    return a


def ol(op, params, run_after=None):
    a = {"type": "OpenApiConnection",
         "inputs": {"host": {"apiId": OL, "connectionName": "shared_office365", "operationId": op},
                    "parameters": params, "authentication": "@parameters('$authentication')"}}
    a["runAfter"] = run_after or {}
    return a


def compose(v, run_after=None):
    return {"type": "Compose", "inputs": v, "runAfter": run_after or {}}


def after(name):
    return {name: ["Succeeded"]}


def graph(method, uri, body, run_after):
    p = {"Uri": uri, "Method": method, "ContentType": "application/json"}
    if body is not None:
        p["Body"] = body
    return ol("HttpRequest", p, run_after)


def guardar_id(valor, run_after):
    return sp("HttpRequest", {
        "dataset": SITE,
        "parameters/method": "POST",
        "parameters/uri": "_api/web/lists(guid'%s')/items(@{%s})" % (L_ATIV, tr("ID")),
        "parameters/headers": {"Accept": "application/json;odata=nometadata",
                               "Content-Type": "application/json;odata=nometadata",
                               "IF-MATCH": "*", "X-HTTP-Method": "MERGE"},
        "parameters/body": "{\"evento_calendario_id\": \"%s\"}" % valor}, run_after)


# ---------------- Fluxo 1: Atividade -> Calendario
ESTADO = tr("estado/Value")
acts = {}
acts["Obter_unidade"] = sp("GetItems", {
    "dataset": SITE, "table": L_UNID,
    "$filter": "Title eq '@{replace(%s, '''', '''''')}'" % tr("polo_servi_x00e7_o/Value"),
    "$top": 1})
acts["Caixa"] = compose("@coalesce(first(outputs('Obter_unidade')?['body/value'])?['email_calendario'], '%s')" % FALLBACK,
                        after("Obter_unidade"))
acts["Assinatura"] = compose("@{%s}#@{%s}#@{%s}" % (ESTADO, tr("data_hora"), tr("duracao_minutos")), after("Caixa"))
acts["Id_atual"] = compose("@coalesce(%s, '')" % tr("evento_calendario_id"), after("Assinatura"))
acts["Grupo"] = sp("GetItems", {"dataset": SITE, "table": L_ATIV,
                                "$filter": "Title eq '@{%s}'" % tr("Title")}, after("Id_atual"))
acts["Participam"] = {"type": "Query", "runAfter": after("Grupo"),
                      "inputs": {"from": "@outputs('Grupo')?['body/value']",
                                 "where": "@not(equals(item()?['participa'], false))"}}
acts["Participantes"] = {"type": "Select", "runAfter": after("Participam"),
                         "inputs": {"from": "@body('Participam')",
                                    "select": {"emailAddress": {"address": "@item()?['profissional/Email']",
                                                                "name": "@item()?['profissional/DisplayName']"},
                                               "type": "required"}}}
acts["Fim"] = compose("@addMinutes(%s, int(coalesce(%s, 60)))" % (tr("data_hora"), tr("duracao_minutos")),
                      after("Participantes"))
acts["Titulo"] = compose(
    "@{if(equals(%s, 'Adiado'), '[ADIADA] ', if(equals(%s, 'Realizado'), '✓ ', ''))}@{%s} — @{%s}"
    % (ESTADO, ESTADO, tr("tipo_atividade/Value"), tr("polo_servi_x00e7_o/Value")), after("Fim"))
acts["Descricao"] = compose(
    "<p><b>Programa:</b> @{%s}<br><b>Local:</b> @{coalesce(%s, '—')}<br><b>Concelho:</b> @{coalesce(%s, '—')}"
    "<br><b>Duração:</b> @{%s} min<br><b>Notas:</b> @{coalesce(%s, '')}</p>"
    "<p style=\"color:#666\">Evento criado automaticamente pela app Calendário Partilhado USP Baixo Vouga. "
    "Para alterar, adiar ou cancelar, use a app (Os meus eventos) — alterações feitas aqui no Outlook não passam para a app.</p>"
    % (tr("programa/Value"), tr("local"), tr("concelho/Value"), tr("duracao_minutos"), tr("observacoes")),
    after("Titulo"))

evento_base = {
    "subject": "@{outputs('Titulo')}",
    "body": {"contentType": "HTML", "content": "@{outputs('Descricao')}"},
    "start": {"dateTime": "@{%s}" % tr("data_hora"), "timeZone": "UTC"},
    "end": {"dateTime": "@{outputs('Fim')}", "timeZone": "UTC"},
    "location": {"displayName": "@{coalesce(%s, '')}" % tr("local")},
}
evento_novo = dict(evento_base)
evento_novo.update({"attendees": "@body('Participantes')", "isReminderOn": True,
                    "reminderMinutesBeforeStart": 30, "allowNewTimeProposals": False})

criar = {
    "Evento_novo": compose(evento_novo),
    "Criar_evento": graph("POST", "https://graph.microsoft.com/v1.0/users/@{outputs('Caixa')}/events",
                          "@{string(outputs('Evento_novo'))}", after("Evento_novo")),
    "Guardar_id": guardar_id("@{outputs('Caixa')}|@{body('Criar_evento')?['id']}|@{outputs('Assinatura')}",
                             after("Criar_evento")),
}

MB = "@{first(split(outputs('Id_atual'), '|'))}"
EV = "@{encodeUriComponent(split(outputs('Id_atual'), '|')[1])}"
atualizar = {
    "Cancelada": {
        "type": "If", "runAfter": {},
        "expression": {"equals": [ESTADO.join(["@", ""]) if False else "@" + ESTADO, "Cancelado"]},
        "actions": {
            "Cancelar_evento": graph("POST", "https://graph.microsoft.com/v1.0/users/%s/events/%s/cancel" % (MB, EV),
                                     "{\"comment\": \"Atividade cancelada na app Calendário Partilhado USP.\"}", {})},
        "else": {"actions": {
            "Evento_alterado": compose(evento_base),
            "Atualizar_evento": graph("PATCH", "https://graph.microsoft.com/v1.0/users/%s/events/%s" % (MB, EV),
                                      "@{string(outputs('Evento_alterado'))}", after("Evento_alterado"))}}},
    "Guardar_assinatura": guardar_id(
        "@{first(split(outputs('Id_atual'), '|'))}|@{split(outputs('Id_atual'), '|')[1]}|@{outputs('Assinatura')}",
        after("Cancelada")),
}

acts["Decidir"] = {
    "type": "If", "runAfter": after("Descricao"),
    "expression": {"and": [{"equals": ["@outputs('Id_atual')", ""]}, {"equals": ["@" + ESTADO, "Planeado"]}]},
    "actions": criar,
    "else": {"actions": {
        "Mudou": {
            "type": "If", "runAfter": {},
            "expression": {"and": [{"not": {"equals": ["@outputs('Id_atual')", ""]}},
                                   {"not": {"equals": ["@last(split(outputs('Id_atual'), '|'))",
                                                       "@outputs('Assinatura')"]}}]},
            "actions": atualizar, "else": {"actions": {}}}}},
}

trigger1 = {"Quando_uma_atividade_muda": {
    "type": "OpenApiConnection",
    "recurrence": {"interval": 1, "frequency": "Minute"},
    "splitOn": "@triggerOutputs()?['body/value']",
    "conditions": [{"expression": "@equals(triggerOutputs()?['body/registante'], true)"}],
    "runtimeConfiguration": {"concurrency": {"runs": 1}},
    "inputs": {"host": {"apiId": SP, "connectionName": "shared_sharepointonline", "operationId": "GetOnUpdatedItems"},
               "parameters": {"dataset": SITE, "table": L_ATIV},
               "authentication": "@parameters('$authentication')"}}}

# ---------------- Fluxo 3: Resumo diario
acts3 = {}
acts3["Pendentes"] = sp("GetItems", {
    "dataset": SITE, "table": L_ATIV,
    "$filter": "(estado eq 'Planeado' and data_hora lt '@{utcNow()}') or estado eq 'Adiado'",
    "$top": 5000})
acts3["Emails"] = {"type": "Select", "runAfter": after("Pendentes"),
                   "inputs": {"from": "@outputs('Pendentes')?['body/value']",
                              "select": "@toLower(item()?['profissional/Email'])"}}
acts3["Distintos"] = compose("@union(body('Emails'), body('Emails'))", after("Emails"))
por_pessoa = {
    "Da_pessoa": {"type": "Query", "runAfter": {},
                  "inputs": {"from": "@outputs('Pendentes')?['body/value']",
                             "where": "@equals(toLower(item()?['profissional/Email']), items('Para_cada_pessoa'))"}},
    "Tabela": {"type": "Table", "runAfter": after("Da_pessoa"),
               "inputs": {"from": "@body('Da_pessoa')", "format": "HTML", "columns": [
                   {"header": "Data", "value": "@if(equals(item()?['estado/Value'], 'Adiado'), 'sem data', formatDateTime(convertFromUtc(item()?['data_hora'], 'GMT Standard Time'), 'dd/MM/yyyy HH:mm'))"},
                   {"header": "Atividade", "value": "@item()?['tipo_atividade/Value']"},
                   {"header": "Unidade", "value": "@item()?['polo_servi_x00e7_o/Value']"},
                   {"header": "Situação", "value": "@if(equals(item()?['estado/Value'], 'Adiado'), 'Por reagendar', 'Em atraso')"}]}},
    "Enviar_email": ol("SendEmailV2", {
        "emailMessage/To": "@items('Para_cada_pessoa')",
        "emailMessage/Subject": "Calendário USP: @{length(body('Da_pessoa'))} atividade(s) por fechar",
        "emailMessage/Body": ("<p>Bom dia,</p><p>Tem atividades que já passaram ou ficaram sem data e ainda não foram "
                              "fechadas na app Calendário Partilhado USP:</p>@{body('Tabela')}"
                              "<p>Abra a app e, em <b>Os meus eventos</b> (painel <b>Por fechar</b>), indique para cada uma "
                              "se foi <b>realizada</b>, <b>adiada</b> ou <b>cancelada</b>.</p>"
                              "<p><a href=\"%s\">Abrir a app Calendário Partilhado USP</a></p>"
                              "<p style=\"color:#666;font-size:12px\">Mensagem automática, enviada nos dias úteis às 8h00 "
                              "apenas a quem tem atividades por fechar.</p>") % APP_URL,
        "emailMessage/Importance": "Normal"}, after("Tabela")),
}
acts3["Para_cada_pessoa"] = {"type": "Foreach", "foreach": "@outputs('Distintos')", "runAfter": after("Distintos"),
                             "actions": por_pessoa}
trigger3 = {"Dias_uteis_8h": {
    "type": "Recurrence",
    "recurrence": {"frequency": "Week", "interval": 1, "timeZone": "GMT Standard Time",
                   "schedule": {"weekDays": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                                "hours": ["8"], "minutes": [0]}}}}


def definition(triggers, actions):
    return {"$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
            "contentVersion": "1.0.0.0",
            "parameters": {"$connections": {"defaultValue": {}, "type": "Object"},
                           "$authentication": {"defaultValue": {}, "type": "SecureObject"}},
            "triggers": triggers, "actions": actions}


ICON = {"shared_sharepointonline": "https://connectoricons-prod.azureedge.net/releases/v1.0.1676/1.0.1676.3617/sharepointonline/icon.png",
        "shared_office365": "https://connectoricons-prod.azureedge.net/releases/v1.0.1682/1.0.1682.3647/office365/icon.png"}
NAMES = {"shared_sharepointonline": "SharePoint", "shared_office365": "Office 365 Outlook"}


def package(fname, display, desc, defn):
    flow_res = str(uuid.uuid4())
    flow_id = str(uuid.uuid4())
    res = {}
    apis_map, conns_map, conn_refs = {}, {}, {}
    deps = []
    for api in ["shared_sharepointonline", "shared_office365"]:
        a_res, c_res = str(uuid.uuid4()), str(uuid.uuid4())
        res[a_res] = {"id": "/providers/Microsoft.PowerApps/apis/" + api, "name": api,
                      "type": "Microsoft.PowerApps/apis", "suggestedCreationType": "Existing",
                      "details": {"displayName": NAMES[api], "iconUri": ICON[api]},
                      "configurableBy": "System", "hierarchy": "Child", "dependsOn": []}
        res[c_res] = {"type": "Microsoft.PowerApps/apis/connections", "suggestedCreationType": "Existing",
                      "creationType": "Existing",
                      "details": {"displayName": "usp.ulsra@arscentro.min-saude.pt", "iconUri": ICON[api]},
                      "configurableBy": "User", "hierarchy": "Child", "dependsOn": [a_res]}
        apis_map[api] = a_res
        conns_map[api] = c_res
        conn_refs[api] = {"connectionName": api.replace("shared_", "shared-") + "-placeholder", "source": "Embedded",
                          "id": "/providers/Microsoft.PowerApps/apis/" + api, "tier": "NotSpecified"}
        deps += [a_res, c_res]
    res[flow_res] = {"type": "Microsoft.Flow/flows", "suggestedCreationType": "New",
                     "creationType": "Existing, New, Update", "details": {"displayName": display},
                     "configurableBy": "User", "hierarchy": "Root", "dependsOn": deps}
    manifest = {"schema": "1.0",
                "details": {"displayName": display, "description": desc,
                            "createdTime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.0000000Z"),
                            "packageTelemetryId": str(uuid.uuid4()), "creator": "N/A", "sourceEnvironment": ""},
                "resources": res}
    flow_def = {"name": flow_id, "id": "/providers/Microsoft.Flow/flows/" + flow_id, "type": "Microsoft.Flow/flows",
                "properties": {"apiId": "/providers/Microsoft.PowerApps/apis/shared_logicflows",
                               "displayName": display, "definition": defn, "connectionReferences": conn_refs,
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


package("fluxo_atividade_calendario.zip", "Calendário USP — Atividade para calendário",
        "Cria e atualiza o evento no calendário da Unidade quando uma atividade é planeada ou muda de estado.",
        definition(trigger1, acts))
package("fluxo_resumo_diario.zip", "Calendário USP — Resumo diário de pendentes",
        "Dias úteis às 8h00: envia a cada profissional a lista de atividades em atraso ou por reagendar.",
        definition(trigger3, acts3))
