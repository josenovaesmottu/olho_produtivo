import requests
import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import time

# ==============================
# CONFIGURAÇÕES
# ==============================
st.set_page_config(page_title="Produtividade Manutenções", page_icon="⚙️", layout="wide")
st.title("⚙️ Acompanhamento de Produtividade — Mottu")

filiais = {
    "Mottu Fortaleza": 9, "Mottu Guarulhos": 83, "Mottu Recife": 16, "Mottu Salvador": 6
    # (...demais filiais omitidas por brevidade)
}

regionais = {
    "Francisco": [9, 83, 16, 6],
}

id_para_nome = {v: k for k, v in filiais.items()}

# ==============================
# TOKEN
# ==============================
def retorna_token():
    username = st.secrets["MOTTU_USERNAME"]
    password = st.secrets["MOTTU_PASSWORD"]

    url = "https://sso.mottu.cloud/realms/Internal/protocol/openid-connect/token"
    payload = {
        "username": username,
        "password": password,
        "grant_type": "password",
        "client_id": "admin-v3-frontend-client",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    r = requests.post(url, data=payload, headers=headers, timeout=20)
    if r.status_code == 200:
        return r.json().get("access_token")

    st.error(f"Erro ao gerar token ({r.status_code}): {r.text}")
    return None


# ==============================
# GET MANUTENÇÕES
# ==============================
def get_manutencoes(lugar_id, token):
    url = f"https://maintenance-backend.mottu.cloud/api/v2/Manutencao/Realizadas/Lugar/{lugar_id}"
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json().get("dataResult", {})

        return {
            "lugarId": lugar_id,
            "lugarNome": data.get("lugarNome", id_para_nome.get(lugar_id, f"ID {lugar_id}")),
            "qtdInternas": data.get("qtdInternas", 0),
            "backlog": data.get("qtdMotosInternas", 0),
        }
    except Exception as e:
        return {"lugarId": lugar_id, "lugarNome": "Erro", "qtdInternas": 0, "backlog": 0, "erro": str(e)}


# ==============================
# INTERFACE
# ==============================
regional_sel = st.selectbox("Selecione a regional:", list(regionais.keys()))
intervalo = st.number_input("Atualizar automaticamente (minutos):", min_value=1, max_value=30, value=5)
st.caption("O dashboard atualiza automaticamente a cada intervalo definido ou manualmente.")

if st.button("🔄 Atualizar agora"):
    st.experimental_rerun()

# ==============================
# EXECUÇÃO
# ==============================
token = retorna_token()
if not token:
    st.stop()

lugar_ids = regionais.get(regional_sel, [])
if not lugar_ids:
    st.warning("Nenhuma filial cadastrada nessa regional.")
    st.stop()

resultados = []
progress = st.progress(0)
for i, lid in enumerate(lugar_ids):
    res = get_manutencoes(lid, token)
    resultados.append(res)
    progress.progress((i + 1) / len(lugar_ids))
    time.sleep(0.1)

df = pd.DataFrame(resultados)
df = df.sort_values(by="qtdInternas", ascending=False)

# Define o ID como índice
df = df.set_index("lugarId")

# Horário local Brasil
hora_brasil = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%H:%M:%S")

# ==============================
# EXIBIÇÃO
# ==============================
st.subheader(f"📍 Regional {regional_sel} — Atualizado às {hora_brasil}")
col1, col2 = st.columns(2)
col1.metric("Total de internas (hoje)", int(df["qtdInternas"].sum()))
col2.metric("Backlog total", int(df["backlog"].sum()))

st.dataframe(
    df[["lugarNome", "qtdInternas", "backlog"]]
    .rename(columns={
        "lugarNome": "Filial",
        "qtdInternas": "Internas (hoje)",
        "backlog": "Backlog"
    }),
    use_container_width=True,
    height=500,
)

st.caption("Para atualizar automaticamente, recarregue a página após o intervalo definido.")
