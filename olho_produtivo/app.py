import requests
import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
import time
import json
from pathlib import Path
from streamlit_autorefresh import st_autorefresh
from get_token import retorna_token
from get_manutencoes import get_parciais, get_rampas
from funcoes_auxiliares import get_progress_color, safe_divide

st_autorefresh(interval= 15 * 60 * 1000, key="dataframerefresh")
st.set_page_config(page_title="Produtividade Manutenções", page_icon="⚙️", layout="wide")
st.title("⚙️ Acompanhamento de Produtividade — Mottu")

filiais_path = Path(__file__).parent / "filiais.json"
filiais = json.load(filiais_path.open("r", encoding="utf-8"))
regionais = ["GERAL","Francisco","Bruno","Flávio","Júlio","Leonardo","Luan","Lucas","Maurício","Rogério"]

token = retorna_token()

regional_sel = st.selectbox("Selecione o regional:", regionais)
st.caption("O dashboard atualiza automaticamente a cada 15min ou manualmente.")

if st.button("🔄 Atualizar agora"):
    st.rerun()

if regional_sel == "GERAL":
    filiais_interesse = filiais["Bruno"] + filiais["Francisco"] + filiais["Flávio"]
else:
    filiais_interesse = filiais[regional_sel]

progress = st.progress(0)
for i, filial in enumerate(filiais_interesse):
    parcial = get_parciais(filial["id"], token)
    rampas = get_rampas(filial["id"], token) 

    filial["internas_realizadas"] = parcial["qtdInternas"]
    filial["backlog"] = parcial["backlog"]
    filial["rampas_ativas"] = rampas["rampas_ativas"]
    filial["rampas_clientes"] = rampas["clientes"]
    filial["rampas_internas"] = rampas["internas"]

    filial["progresso_internas"] = safe_divide(filial["internas_realizadas"], filial["meta_interna"])
    filial["ocupacao_rampas"] = safe_divide(filial["rampas_ativas"], filial["meta_rampa"])

    progress.progress((i + 1) / len(filiais_interesse))


df = pd.DataFrame(filiais_interesse)
df = df.sort_values(by="progresso_internas", ascending=True)

# ==============================
# EXIBIÇÃO
# ==============================

hora_brasil = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%H:%M:%S")
st.subheader(f"📍 Regional {regional_sel} — Atualizado às {hora_brasil}")

col1, col2, col3 = st.columns(3)
total_internas = int(df["internas_realizadas"].sum())
meta_total_internas = int(df["meta_interna"].fillna(0).sum())
prop_total_internas = safe_divide(total_internas, meta_total_internas)
cor_total_internas = get_progress_color(prop_total_internas)
pct_total_internas = min(prop_total_internas * 100, 100)
with col1:
    st.markdown("**Total de internas (hoje)**")
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 8px;">
        <span style="font-weight: bold; min-width: 25px;">{total_internas}</span>
        <div style="background-color: #ddd; border-radius: 5px; height: 20px; flex: 1;">
            <div style="background-color: {cor_total_internas}; width: {pct_total_internas}%; height: 100%; border-radius: 5px;"></div>
        </div>
        <span style="color: #666; min-width: 25px;">{meta_total_internas}</span>
    </div>
    """, unsafe_allow_html=True)
col2.metric("Backlog total", int(df["backlog"].sum()))
col3.metric("Rampas ativas", int(df["rampas_ativas"].sum()))

st.divider()

# Headers
col_nome, col_backlog, col_internas, col_rampas = st.columns([2, 1, 2, 2])
col_nome.markdown("**Filial**")
col_backlog.markdown("**Backlog**")
col_internas.markdown("**Internas**")
col_rampas.markdown("**Rampas Ativas (Azul = Cliente, Verde = Interna)**")

# Exibir cada filial
for _, row in df.iterrows():
    nome = row["nome"]
    backlog = row["backlog"] or 0
    internas = row["internas_realizadas"] or 0
    meta_interna = row["meta_interna"] or 1
    rampas_ativas = row["rampas_ativas"] or 0
    rampas_clientes = row["rampas_clientes"] or 0
    rampas_internas = row["rampas_internas"] or 0
    meta_rampa = row["meta_rampa"] or 0
    
    # Calcular proporções
    prop_internas = row["progresso_internas"]
    prop_rampas = row["ocupacao_rampas"]
    
    # Layout: Nome | Backlog | Barra Internas | Barra Rampas
    col_nome, col_backlog, col_internas, col_rampas = st.columns([2, 1, 2, 2])
    
    with col_nome:
        st.write(f"**{nome}**")
    
    with col_backlog:
        st.write(f"{backlog}")
    
    with col_internas:
        # Barra de progresso internas (vermelho → verde) com valores nas laterais
        cor = get_progress_color(prop_internas)
        pct = min(prop_internas * 100, 100)
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-weight: bold; min-width: 25px;">{internas}</span>
            <div style="background-color: #ddd; border-radius: 5px; height: 20px; flex: 1;">
                <div style="background-color: {cor}; width: {pct}%; height: 100%; border-radius: 5px;"></div>
            </div>
            <span style="color: #666; min-width: 25px;">{meta_interna}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col_rampas:
        # Barra segmentada de rampas
        if meta_rampa > 0:
            segments_html = ""
            for j in range(1,int(meta_rampa)+1):
                if j <= rampas_clientes:
                    color = "#3632a8" # azul - cliente
                elif j <= (rampas_internas + rampas_clientes):
                    color = "#28a745"  # Verde - interna
                else:
                    color = "#dc3545"  # Vermelho - inativa
                segments_html += f'<div style="flex: 1; background-color: {color}; height: 20px; margin: 0 1px; border-radius: 3px;"></div>'
            
            st.markdown(f"""
            <div style="display: flex; width: 100%;">
                {segments_html}
            </div>
            <div style="text-align: center; font-size: 11px; color: #666;">{int(rampas_ativas)}/{int(meta_rampa)}</div>
            """, unsafe_allow_html=True)
        else:
            st.write("—")

st.divider()