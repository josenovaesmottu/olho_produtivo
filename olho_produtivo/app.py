import requests
import streamlit as st
import pandas as pd
from datetime import datetime
import time

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
    "Júlio": [59, 5, 61, 30, 4, 29, 28, 27, 26, 6, 9, 114, 21, 16, 84, 18, 122, 17],
    "Leonardo": [77, 455, 474, 416, 285, 357, 463, 397, 259, 174, 300, 55, 203, 417, 356, 372, 473, 319, 507, 462, 489, 505, 476, 396, 478, 469, 497, 366, 458, 267, 475, 449, 454, 472],
    "Lucas": [249, 107, 42, 113, 47, 48, 106, 43, 71, 413, 11, 87, 85, 459, 499],
    "Rogério": [271, 274, 258, 110, 329, 69, 51, 73, 70, 76, 252, 284, 95, 115, 238, 74, 80, 109, 49, 50, 310, 295, 405, 384, 283, 225, 266, 248, 402, 250, 404, 365, 282, 64, 175, 311],
    "Jessica": [376, 486, 491, 257, 290, 260, 456, 307, 470, 301, 297, 240, 303, 294, 399, 223, 224, 299, 480, 345, 306, 242, 241, 237, 247, 218, 304, 254, 268, 269, 289, 291, 287, 288, 296, 305, 230, 226, 228, 236, 227, 229, 231, 286, 264, 496, 501, 494, 253, 261, 251, 217, 465, 500, 488, 373, 355, 451, 446, 460, 457, 448, 452, 453, 221, 216, 222, 220, 272, 232, 233, 234, 235, 362, 364, 374, 358, 359, 450, 361, 468, 471, 466, 490, 263, 262, 354, 351, 371, 367, 369, 353, 370, 326, 211, 325, 323, 210, 331, 338, 368, 506, 314, 316, 333, 377, 342, 317, 315, 332, 447, 388, 512, 352, 360, 339, 341, 348, 308, 503, 350, 508, 380, 385, 383, 390, 378, 386, 391, 387, 401, 382, 393, 395, 392, 467, 381, 400, 394, 492, 403, 389, 379, 398, 375, 344, 322, 320, 327, 337, 340, 347, 330, 343, 324, 346, 349, 328, 336, 493, 483, 498, 510, 481, 487, 495, 485, 504, 318, 482, 502, 479, 124, 239, 424, 181, 119, 335, 212, 423, 186, 104, 422, 99, 215, 409, 120, 415, 121, 171, 419, 208, 213, 204, 187, 408, 273, 182, 214, 161, 184, 160, 219, 188, 406, 172, 96, 464, 177, 206, 100, 293, 461, 112, 279, 445, 407, 302, 275, 169, 205, 425, 209, 178, 334, 321, 411, 484, 179, 270, 276, 278, 412, 418, 292, 98, 176, 410, 117, 185, 298, 414, 207, 170, 280, 281, 97, 277],
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

st.caption("Para atualizar automaticamente, recarregue a página após o intervalo definido.")
