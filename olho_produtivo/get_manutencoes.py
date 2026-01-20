import requests
import streamlit as st
from datetime import date, datetime
from zoneinfo import ZoneInfo

def get_historico_por_mecanico(mecanicoId, token):
    url = f"https://maintenance-backend.mottu.cloud/api/v2.6/Manutencao/HistoricoPorMecanico?mecanicoId={mecanicoId}&pagina=1&quantidadePorPagina=30"
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        manutencoes = r.json()["dataResult"]["manutencoes"]
        finalizadas = []
        ultimaAtividade = "2024-01-01T12:00:00.00000"
        emManutencao = False
        if manutencoes[0]["situacao"] == 2:
            emManutencao = True
        for manutencao in manutencoes:
            if manutencao["atualizacaoData"] > ultimaAtividade:
                ultimaAtividade = manutencao["atualizacaoData"]
            if manutencao["situacao"] == 4 and manutencao["tipo"] in [3,4,6,9,15] and manutencao["atualizacaoData"][:10] == str(datetime.now(ZoneInfo("America/Sao_Paulo")).date()):
                finalizadas.append({
                    "id": manutencao["id"],
                    "placa": manutencao["placa"]
                })
        return finalizadas, ultimaAtividade, emManutencao

    except Exception as e:
        return [{"id": 0, "placa": "Erro"}], "Erro"

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
        debug = []
        
        for mec in mecs:
            mecs[mec]["ultima_atividade"] = None
            mecs[mec]["emManutencao"] = False

        for mecanico in data["manutencoesMecanico"]:
            if isinstance(mecanico["mecanicoId"], int) and mecanico["nome"] != "N/A":
                finalizadas, ultima_atividade, emManutencao = get_historico_por_mecanico(mecanico["mecanicoId"], token)                
                id = str(mecanico["mecanicoId"])
                mecs[id]["ultima_atividade"] = ultima_atividade
                mecs[id]["emManutencao"] = emManutencao

                debug.append({"nome": mecanico["nome"], "id": mecanico["mecanicoId"], "finalizadas": len(finalizadas), "emManutencao": emManutencao})
                
                # Adicionar cada item de finalizadas ao dicionário usando ID como chave
                for manutencao in finalizadas:
                    internas_feitas[manutencao["id"]] = manutencao
        
        # Converter o dicionário para lista
        internas_feitas = list(internas_feitas.values())

        return {
            "internas_feitas": internas_feitas,
            "qtdInternas": len(internas_feitas),
            "backlog": backlog,
            "mecs": mecs
        }

    except Exception as e:
        return {"internas_feitas": [],"qtdInternas": 0, "backlog": 0,"mecs": mecs}

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
