import requests
import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import time
from google.cloud import bigquery

# ==============================
# CONFIGURAÇÕES
# ==============================
st.set_page_config(page_title="Produtividade Manutenções", page_icon="⚙️", layout="wide")
st.title("⚙️ Acompanhamento de Produtividade — Mottu")




filiais = {
    "Mottu Abaetetuba": 282, "Mottu Alagoinhas": 110, "Mottu Ananindeua": 122, "Mottu Anápolis": 58,
    "Mottu Aparecida de Goiânia": 123, "Mottu Aracaju": 29, "Mottu Aracati": 274, "Mottu Arapiraca": 52,
    "Mottu Araçatuba": 109, "Mottu Avaré": 454, "Mottu Barreiras": 259, "Mottu Bauru": 175,
    "Mottu Bayeux": 384, "Mottu Belo Horizonte": 3, "Mottu Belém": 18, "Mottu Blumenau": 356,
    "Mottu Boa Vista": 61, "Mottu Bragança": 238, "Mottu Brasília": 10, "Mottu Butantã": 1,
    "Mottu Cabo Frio": 283, "Mottu Camaçari": 173, "Mottu Campina Grande": 38, "Mottu Campinas": 7,
    "Mottu Campo Grande": 31, "Mottu Campos dos Goytacazes": 285, "Mottu Caruaru": 39, "Mottu Cascavel": 397,
    "Mottu Castanhal": 365, "Mottu Caucaia": 458, "Mottu Caxias": 366, "Mottu Caxias do Sul": 69,
    "Mottu Colatina": 474, "Mottu Contagem": 53, "Mottu Crato": 295, "Mottu Criciúma": 51,
    "Mottu Cuiabá": 30, "Mottu Curitiba": 4, "Mottu Divinópolis": 174, "Mottu Dourados": 77,
    "Mottu Duque de Caxias": 469, "Mottu Eunápolis": 417, "Mottu Feira de Santana": 40, "Mottu Florianópolis": 32,
    "Mottu Fortaleza": 9, "Mottu Franca": 75, "Mottu Fátima": 114, "Mottu Goiânia": 15,
    "Mottu Governador Valadares": 76, "Mottu Guarulhos": 83, "Mottu Icoaraci": 404, "Mottu Imperatriz": 65,
    "Mottu Interlagos": 37, "Mottu Ipatinga": 55, "Mottu Ipiranga": 94, "Mottu Ipojuca": 267,
    "Mottu Itabuna": 116, "Mottu Itajaí": 111, "Mottu Itapetininga": 449, "Mottu Itapipoca": 357,
    "Mottu Jacarepaguá": 248, "Mottu Jandira": 41, "Mottu Jequié": 271, "Mottu Ji Paraná": 416,
    "Mottu Joinville": 56, "Mottu João Pessoa": 28, "Mottu Juazeiro": 45, "Mottu Juazeiro do Norte": 46,
    "Mottu Juiz de Fora": 95, "Mottu Jundiaí": 33, "Mottu Lagarto": 462, "Mottu Limão - Zona Norte": 36,
    "Mottu Linhares": 258, "Mottu Londrina": 49, "Mottu Macapá": 66, "Mottu Macaé": 266,
    "Mottu Maceió": 22, "Mottu Manaus": 5, "Mottu Marabá": 68, "Mottu Maracanaú": 180,
    "Mottu Maringá": 50, "Mottu Messejana": 402, "Mottu Mexico CDMX Cien Metros": 85,
    "Mottu Mexico CDMX Colegio Militar": 11, "Mottu Mexico CDMX Tlalpan": 71, "Mottu Mexico Cancún": 107,
    "Mottu Mexico Guadalajara": 47, "Mottu Mexico Guadalajara Centro": 113, "Mottu Mexico Los Reyes": 413,
    "Mottu Mexico Monterrey": 43, "Mottu Mexico Monterrey La Fe": 106, "Mottu Mexico Mérida": 249,
    "Mottu Mexico Puebla": 48, "Mottu Mexico Querétaro": 42, "Mottu Mexico Toluca": 459,
    "Mottu Mogi das Cruzes": 86, "Mottu Montes Claros": 57, "Mottu Mossoró": 67, "Mottu Natal": 27,
    "Mottu Niterói": 105, "Mottu Olinda": 84, "Mottu Palmas": 60, "Mottu Parauapebas": 79,
    "Mottu Parnamirim": 118, "Mottu Parnaíba": 115, "Mottu Patos": 300, "Mottu Pelotas": 203,
    "Mottu Petrolina": 309, "Mottu Pindamonhangaba": 311, "Mottu Piracicaba": 44, "Mottu Piçarreira": 183,
    "Mottu Ponta Grossa": 319, "Mottu Porto Alegre": 8, "Mottu Porto Seguro": 329, "Mottu Porto Velho": 59,
    "Mottu Pouso Alegre": 472, "Mottu Praia Grande": 82, "Mottu Presidente Prudente": 252,
    "Mottu Recife": 16, "Mottu Ribeirão Preto": 17, "Mottu Rio Branco": 62, "Mottu Rio Verde": 73,
    "Mottu Rondonópolis": 70, "Mottu Salvador": 6, "Mottu Santa Maria": 455, "Mottu Santarém": 81,
    "Mottu Santos": 24, "Mottu Serra": 19, "Mottu Sete Lagoas": 372, "Mottu Sobral": 74,
    "Mottu Sorocaba": 34, "Mottu São Bernardo": 23, "Mottu São Carlos": 64, "Mottu São José do Rio Preto": 63,
    "Mottu São José dos Campos": 20, "Mottu São Luís": 21, "Mottu São Miguel": 13, "Mottu Taboão": 35,
    "Mottu Teixeira de Freitas": 284, "Mottu Teresina": 26, "Mottu Toledo": 463, "Mottu Uberaba": 78,
    "Mottu Uberlândia": 25, "Mottu Valparaíso": 310, "Mottu Vila Isabel": 225, "Mottu Vila Velha": 72,
    "Mottu Vitória": 405, "Mottu Vitória da Conquista": 80, "Mottu Vitória de Santo Antão": 250,
    "Mottu Volta Redonda": 396, "Mottu Várzea Grande": 473
}

regionais = {
    "Bruno": [31, 68, 25, 63, 81, 79, 38, 62, 66, 8, 3, 19, 72, 15, 118, 40, 39],
    "Flávio": [82, 24, 83, 33, 94, 7, 13, 37, 36, 41, 477, 86, 44, 1, 34, 35, 23],
    "Francisco": [59, 5, 61, 30, 4, 29, 28, 27, 26, 6, 9, 114, 21, 16, 84, 18, 122, 17],
    "Leonardo": [77, 455, 474, 416, 285, 357, 463, 397, 259, 174, 300, 55, 203, 417, 356, 372, 473, 319],
    "Lucas": [249, 107, 42, 113, 47, 48, 106, 43, 71, 413, 11, 85, 459],
    "Rogério": [271, 274, 258, 110, 329, 69, 51, 73, 70, 76, 252, 284, 95, 115, 238, 74, 80, 109],
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
# QUERY BIGQUERY — METAS
# ==============================
@st.cache_data(ttl=1800)
def get_metas():
    client = bigquery.Client(project="dm-mottu-aluguel")
    query = """
        SELECT
          filial,
          COUNT(*) AS meta
        FROM `dm-mottu-aluguel.exp_frota.ordem_de_producao`
        GROUP BY filial
    """
    df_meta = client.query(query).to_dataframe()
    return df_meta


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

# ==============================
# METAS (BigQuery)
# ==============================
try:
    df_meta = get_metas()
except Exception as e:
    st.warning(f"Erro ao carregar metas: {e}")
    df_meta = pd.DataFrame(columns=["filial", "meta"])

# Faz o merge entre nome da filial e meta
df = df.merge(df_meta, left_on="lugarNome", right_on="filial", how="left")
df.drop(columns=["filial"], inplace=True)
df["meta"] = df["meta"].fillna(0)

# Calcula atingimento
df["atingimento (%)"] = (df["qtdInternas"] / df["meta"]) * 100
df["atingimento (%)"] = df["atingimento (%)"].fillna(0).round(1)


# ==============================
# FUNÇÃO DE COR
# ==============================
def cor_atingimento(val):
    if val < 50:
        color = 'red'
    elif val < 80:
        color = 'orange'
    else:
        color = 'green'
    return f'color: {color}; font-weight: bold'


# ==============================
# EXIBIÇÃO
# ==============================
df = df.sort_values(by="qtdInternas", ascending=False)
hora_brasil = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%H:%M:%S")

st.subheader(f"📍 Regional {regional_sel} — Atualizado às {hora_brasil}")
col1, col2 = st.columns(2)
col1.metric("Total de internas (hoje)", int(df["qtdInternas"].sum()))
col2.metric("Backlog total", int(df["backlog"].sum()))

styled_df = df.style.applymap(cor_atingimento, subset=["atingimento (%)"])

st.dataframe(
    styled_df.format({
        "atingimento (%)": "{:.1f}",
        "meta": "{:.0f}",
        "qtdInternas": "{:.0f}",
        "backlog": "{:.0f}"
    }).hide(axis="index"),
    use_container_width=True,
    height=500
)

st.caption("Para atualizar automaticamente, recarregue a página após o intervalo definido.")

