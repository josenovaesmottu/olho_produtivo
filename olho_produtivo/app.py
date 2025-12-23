import requests
import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import time
import json
from pathlib import Path
from get_token import retorna_token
from get_manutencoes import get_parciais, get_rampas

st.set_page_config(page_title="Produtividade Manutenções", page_icon="⚙️", layout="wide")
st.title("⚙️ Acompanhamento de Produtividade — Mottu")

filiais_path = Path(__file__).parent / "filiais.json"
filiais = json.load(filiais_path.open("r", encoding="utf-8"))
regionais = ["Bruno","Flávio","Francisco","Júlio","Leonardo","Luan","Lucas","Maurício","Rogério","Luciano"]

token = retorna_token()

regional_sel = st.selectbox("Selecione a regional:", regionais)
#regional_sel = "Francisco"
intervalo = st.number_input("Atualizar automaticamente (minutos):", min_value=1, max_value=30, value=5)
st.caption("O dashboard atualiza automaticamente a cada intervalo definido ou manualmente.")

if st.button("🔄 Atualizar agora"):
    st.experimental_rerun()

filiais_interesse = filiais[regional_sel]
progress = st.progress(0)
for i, filial in enumerate(filiais_interesse):
    parcial = get_parciais(filial["id"], token)
    rampas = get_rampas(filial["id"], token) 

    filial["internas_realizadas"] = parcial["qtdInternas"]
    filial["backlog"] = parcial["backlog"]
    filial["rampas_ativas"] = rampas["rampas_ativas"]
 
    progress.progress((i + 1) / len(filiais_interesse))


df = pd.DataFrame(filiais_interesse)
df = df.sort_values(by="internas_realizadas", ascending=False)

# ==============================
# EXIBIÇÃO
# ==============================

hora_brasil = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%H:%M:%S")
st.subheader(f"📍 Regional {regional_sel} — Atualizado às {hora_brasil}")

col1, col2, col3 = st.columns(3)
col1.metric("Total de internas (hoje)", int(df["internas_realizadas"].sum()))
col2.metric("Backlog total", int(df["backlog"].sum()))
col3.metric("Rampas ativas", int(df["rampas_ativas"].sum()))

st.divider()

# Função para gerar cor do vermelho ao verde baseado na proporção
def get_progress_color(ratio):
    """Retorna cor RGB de vermelho (0%) a verde (100%)"""
    ratio = min(max(ratio, 0), 1)  # Clamp entre 0 e 1
    red = int(255 * (1 - ratio))
    green = int(255 * ratio)
    return f"rgb({red}, {green}, 50)"

# Exibir cada filial
for _, row in df.iterrows():
    nome = row["nome"]
    backlog = row["backlog"] or 0
    internas = row["internas_realizadas"] or 0
    meta_interna = row["meta_interna"] or 1
    rampas_ativas = row["rampas_ativas"] or 0
    meta_rampa = row["meta_rampa"] or 0
    
    # Calcular proporções
    prop_internas = internas / meta_interna if meta_interna > 0 else 0
    prop_rampas = rampas_ativas / meta_rampa if meta_rampa > 0 else 0
    
    # Layout: Nome | Backlog | Barra Internas | Barra Rampas
    col_nome, col_backlog, col_internas, col_rampas = st.columns([2, 1, 2, 2])
    
    with col_nome:
        st.write(f"**{nome}**")
    
    with col_backlog:
        st.metric("Backlog", backlog, label_visibility="collapsed")
    
    with col_internas:
        # Barra de progresso internas (vermelho → verde)
        cor = get_progress_color(prop_internas)
        pct = min(prop_internas * 100, 100)
        st.markdown(f"""
        <div style="background-color: #ddd; border-radius: 5px; height: 25px; width: 100%;">
            <div style="background-color: {cor}; width: {pct}%; height: 100%; border-radius: 5px; text-align: center; color: white; font-size: 12px; line-height: 25px;">
                {internas}/{meta_interna}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_rampas:
        # Barra segmentada de rampas
        if meta_rampa > 0:
            segments_html = ""
            for j in range(int(meta_rampa)):
                if j < rampas_ativas:
                    color = "#28a745"  # Verde - ativa
                else:
                    color = "#dc3545"  # Vermelho - inativa
                segments_html += f'<div style="flex: 1; background-color: {color}; height: 25px; margin: 0 1px; border-radius: 3px;"></div>'
            
            st.markdown(f"""
            <div style="display: flex; width: 100%;">
                {segments_html}
            </div>
            <div style="text-align: center; font-size: 11px; color: #666;">{int(rampas_ativas)}/{int(meta_rampa)} rampas</div>
            """, unsafe_allow_html=True)
        else:
            st.write("—")

st.divider()
st.caption("Para atualizar automaticamente, recarregue a página após o intervalo definido.")




