# app.py
import streamlit as st
import pandas as pd
import time
from datetime import datetime
import requests

from token_manager import retorna_token  # importa o token de outro arquivo

# ==============================
# CONFIGURAÇÕES
# ==============================
st.set_page_config(page_title="Produtividade Manutenções", page_icon="⚙️", layout="wide")
st.title("⚙️ Acompanhamento de Produtividade — Mottu")

# ... (dicionários de filiais e regionais iguais aos que você já tem)

id_para_nome = {v: k for k, v in filiais.items()}

# ==============================
# FUNÇÕES
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
        }
    except Exception as e:
        return {"lugarId": lugar_id, "lugarNome": "Erro", "qtdInternas": 0, "erro": str(e)}


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
    st.error("Erro ao gerar token. Verifique as variáveis de ambiente.")
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

st.subheader(f"📍 Regional {regional_sel} — Atualizado em {datetime.now().strftime('%H:%M:%S')}")
st.metric("Total de internas (hoje)", int(df["qtdInternas"].sum()))
st.dataframe(
    df[["lugarNome", "qtdInternas"]]
    .rename(columns={"lugarNome": "Filial", "qtdInternas": "Internas feitas (hoje)"}),
    use_container_width=True,
    height=500,
)
