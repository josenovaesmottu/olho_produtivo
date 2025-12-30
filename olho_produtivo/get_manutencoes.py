import requests
import streamlit as st
from datetime import date


def get_historico_por_mecanico(mecanicoId, token):
    url = f"https://maintenance-backend.mottu.cloud/api/v2.6/Manutencao/HistoricoPorMecanico?mecanicoId={mecanicoId}&pagina=1&quantidadePorPagina=30"
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        manutencoes = r.json()["dataResult"]["manutencoes"]
        finalizadas = 0
        for manutencao in manutencoes:
            if manutencao["situacao"] == 4 and manutencao["tipo"] in [3,4,6,9,15] and manutencao["atualizacaoData"][:10] == str(date.today()):
                finalizadas += 1
        return finalizadas

    except Exception as e:
        return 0


def get_parciais(lugar_id, token):
    url = f"https://maintenance-backend.mottu.cloud/api/v2/Manutencao/Realizadas/Lugar/{lugar_id}"
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json().get("dataResult", {})

        backlog = data.get("qtdMotosInternas", 0)
        internas_feitas = 0
        debug = []
        for mecanico in data["manutencoesMecanico"]:
            if isinstance(mecanico["mecanicoId"], int) and mecanico["nome"] != "N/A":
                #realizadas = mecanico.get("qtdInternas", 0)
                #finalizadas =  min(historico,realizadas) 
                finalizadas = get_historico_por_mecanico(mecanico["mecanicoId"],token)
                debug.append({"nome": mecanico["nome"], "id":mecanico["mecanicoId"], "finalizadas": finalizadas})
                internas_feitas += finalizadas

        return {
            "qtdInternas": internas_feitas,
            "backlog": backlog ,
        }

    except Exception as e:
        return {"lugarId": lugar_id, "lugarNome": "Erro", "qtdInternas": 0, "backlog": 0, "erro": str(e)}

def get_rampas(lugar_id, token):
    url = f"https://maintenance-backend.mottu.cloud/api/v2.6/Ativas/{lugar_id}/Ativas?Tipos=0&Tipos=1&Tipos=2&Tipos=3&Tipos=4&Tipos=5&Tipos=6&Tipos=7&Tipos=9&Tipos=10&Tipos=11&Tipos=12&Tipos=13&Tipos=14&Tipos=15&Situacoes=2&Pagina=1&QuantidadePorPagina=40"
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json()["dataResult"]["manutencoes"]
        rampas_ativas = 0
        for manutencoes in data:
            if "rampa" in manutencoes["plataforma"].lower() or "box" in manutencoes["plataforma"].lower():
                rampas_ativas += 1

        return {
            "rampas_ativas": rampas_ativas,
        }

    except Exception as e:
        return {"rampas_ativas": 0}