import requests
import streamlit as st
from datetime import date, datetime
from zoneinfo import ZoneInfo

def manutencaoDetalhes(manutencaoId, token):
    url = f"https://maintenance-backend.mottu.cloud/api/v2.5/Manutencao/Detalhes/Geral/{manutencaoId}"
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}

    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json()['dataResult']
        return data
    except Exception as e:
        return [{"id": 0, "plataforma": "Erro"}]

def get_historico_por_mecanico(mecanicoId, token):
    url = f"https://maintenance-backend.mottu.cloud/api/v2.6/Manutencao/HistoricoPorMecanico?mecanicoId={mecanicoId}&pagina=1&quantidadePorPagina=30"
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        manutencoes = r.json()["dataResult"]["manutencoes"]
        finalizadas_interna = []
        finalizadas_cliente = []
        ultimaAtividade = "2025-01-01T00:00:00"
        emManutencao = False
        if manutencoes and manutencoes[0]["situacao"] == 2:
            emManutencao = True
             
        for manutencao in manutencoes:
            boxrapido = False
            if manutencao["atualizacaoData"] > ultimaAtividade:
                ultimaAtividade = manutencao["atualizacaoData"]

            if manutencao["situacao"] == 4:
                #manutencao_info = manutencaoDetalhes(manutencao["id"], token)

                #if "box" in manutencao_info["plataforma"].lower():
                #    boxrapido = True


                if manutencao["tipo"] in [3,4,6,9,15] and manutencao["atualizacaoData"][:10] == str(datetime.now(ZoneInfo("America/Sao_Paulo")).date()):
                    finalizadas_interna.append({
                    "id": manutencao["id"],
                    "placa": manutencao["placa"],
                    "boxrapido": boxrapido
                })

                if manutencao["tipo"] in [1,2,5,7,10,11,12,13] and manutencao["atualizacaoData"][:10] == str(datetime.now(ZoneInfo("America/Sao_Paulo")).date()):
                    finalizadas_cliente.append({
                    "id": manutencao["id"],
                    "placa": manutencao["placa"],
                    "boxrapido": boxrapido
                })


        return finalizadas_interna,finalizadas_cliente,ultimaAtividade,emManutencao

    except Exception as e:
        return [{"id": 0, "placa": "Erro", "boxrapido": False}]

def get_parciais(lugar_id, mecs, token):
    url = f"https://maintenance-backend.mottu.cloud/api/v2/Manutencao/Realizadas/Lugar/{lugar_id}"
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json().get("dataResult", {})

        backlog = data.get("qtdMotosInternas", 0)
        # Usar dicionário para garantir unicidade por ID
        internas_feitas = {}
        clientes_feitas = {}
        #debug = []

        for mec_id in mecs:
            mecs[mec_id]["ultima_atividade"] = None
            mecs[mec_id]["emManutencao"] = False

        
        for mecanico in data["manutencoesMecanico"]:
            if isinstance(mecanico["mecanicoId"], int) and mecanico["nome"] != "N/A":
                finalizadas_interna,finalizadas_cliente,ultima_atividade,emManutencao = get_historico_por_mecanico(mecanico["mecanicoId"],token)
                #debug.append({"nome": mecanico["nome"], "id":mecanico["mecanicoId"], "finalizadas": len(finalizadas)})
                id = str(mecanico["mecanicoId"])
                if id in mecs.keys():
                   mecs[id]["ultima_atividade"] = ultima_atividade
                   mecs[id]["emManutencao"] = emManutencao

                # Adicionar cada item de finalizadas ao dicionário usando ID como chave
                for manutencao in finalizadas_interna:
                    internas_feitas[manutencao["id"]] = manutencao
                for manutencao in finalizadas_cliente:
                    clientes_feitas[manutencao["id"]] = manutencao
        
        # Converter o dicionário para lista
        internas_feitas = list(internas_feitas.values())
        clientes_feitas = list(clientes_feitas.values())

        return {
            "internas_feitas": internas_feitas,
            "clientes_feitas": clientes_feitas,
            "qtdInternas": len(internas_feitas),
            "qtdClientes": len(clientes_feitas),
            "backlog": backlog,
            "mecs": mecs
        }

    except Exception as e:
        return {"internas_feitas": [],"clientes_feitas": [],"qtdInternas": 0,"qtdClientes": 0, "backlog": 0, "mecs": mecs}

def get_rampas(lugar_id, token):
    url = f"https://maintenance-backend.mottu.cloud/api/v2.6/Ativas/{lugar_id}/Ativas?Tipos=0&Tipos=1&Tipos=2&Tipos=3&Tipos=4&Tipos=5&Tipos=6&Tipos=7&Tipos=9&Tipos=10&Tipos=11&Tipos=12&Tipos=13&Tipos=14&Tipos=15&Situacoes=2&Pagina=1&QuantidadePorPagina=40"
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json()["dataResult"]["manutencoes"]
        dict_rampas = []
        for manutencao in data:
            if "alinh" in manutencao["plataforma"].lower() or "iot" in manutencao["plataforma"].lower():
                continue
            box_rapido = False
            tipo_manutencao = None
            plataforma = manutencao["plataforma"]
            mecanico = manutencao["ultimoMecanicoNome"]
            placa = manutencao["placa"]
            if manutencao["tipo"] in [3,4,6,9,15]:
                tipo_manutencao = "Interna"
            if manutencao["tipo"] in [1,2,5,7,10,11,12,13]:
                tipo_manutencao = "Cliente"
            if "box" in manutencao["plataforma"].lower():
                box_rapido = True

            dict_rampas.append({
                "plataforma": plataforma,
                "mecanico": mecanico,
                "tipo_manutencao": tipo_manutencao,
                "box_rapido": box_rapido,
                "placa": placa,
            })
            
        return dict_rampas

    except Exception as e:
        return {
                "plataforma": "Erro",
                "mecanico": "Erro",
                "tipo_manutencao": "Erro",
                "box_rapido": False,
                "placa": "Erro",
        }
