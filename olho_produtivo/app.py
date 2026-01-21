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
from funcoes_auxiliares import get_progress_color, safe_divide, ordem_rampas, safe_int, format_time_delta

st_autorefresh(interval= 15 * 60 * 1000, key="dataframerefresh")
st.set_page_config(page_title="Produtividade Manutenções", page_icon="⚙️", layout="wide")

# Estilos CSS globais
st.markdown("""
<style>
.mecanicos-container {
    display: flex;
    overflow-x: auto;
    padding-bottom: 10px;
    gap: 8px;
    white-space: nowrap;
}
.mecanico-card {
    min-width: 100px;
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 8px;
    text-align: center;
    margin-right: 4px;
    display: inline-block;
}
.mecanico-nome {
    font-weight: bold;
    font-size: 14px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
</style>
""", unsafe_allow_html=True)

st.title("⚙️ PAINEL DE PRODUÇÃO")

filiais_path = Path(__file__).parent / "filiais.json"
filiais = json.load(filiais_path.open("r", encoding="utf-8"))
regionais = ["-- GRANDES + JUMBO --","Francisco","Bruno","Flávio","Júlio","Leonardo","Luan","Lucas","Maurício","Rogério"]

token = retorna_token()

regional_sel = st.selectbox("Selecione o regional:", regionais)
st.caption("O dashboard atualiza automaticamente a cada 15min ou manualmente.")

if st.button("🔄 Atualizar agora"):
    st.rerun()

if regional_sel == "-- GRANDES + JUMBO --":
    filiais_interesse = filiais["Bruno"] + filiais["Francisco"] + filiais["Júlio"]
else:
    filiais_interesse = filiais[regional_sel]

progress = st.progress(0)
for i, filial in enumerate(filiais_interesse):
    parcial = get_parciais(filial["id"], filial["mecs"], token)
    rampas = get_rampas(filial["id"], token) 

    filial["internas_realizadas"] = parcial["qtdInternas"]
    filial["lista_internas_realizadas"] = parcial["internas_feitas"]
    filial["clientes_realizadas"] = parcial["qtdClientes"]
    filial["lista_clientes_realizadas"] = parcial["clientes_feitas"]
    filial["backlog"] = parcial["backlog"]
    
    filial["rampas"] = rampas
    filial["rampas_ativas"] = len(rampas)

    filial["progresso_internas"] = safe_divide(filial["internas_realizadas"], filial["meta_interna"])
    filial["ocupacao_rampas"] = safe_divide(filial["rampas_ativas"], filial["meta_rampa"])
    filial["mecs"] = parcial["mecs"]
    progress.progress((i + 1) / len(filiais_interesse))


df = pd.DataFrame(filiais_interesse)
df = df.sort_values(by="progresso_internas", ascending=False)

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
col_nome, col_backlog, col_internas, col_rampas, col_mecanicos = st.columns([2, 1, 2, 2, 4])
col_nome.markdown("**Filial**")
col_backlog.markdown("**Backlog**")
col_internas.markdown("**Internas**")
col_rampas.markdown("**Rampas Ativas (Azul = Cliente, Verde = Interna)**")
col_mecanicos.markdown("**EM TESTES - Mecânicos (Verde = Em manutenção, Roxo = Sem manutenção)**")

# Exibir cada filial
for _, row in df.iterrows():
    nome = row["nome"]
    backlog = safe_int(row["backlog"],0)
    internas = safe_int(row["internas_realizadas"],0)
    meta_interna = safe_int(row["meta_interna"], 1)  # Default 1 para evitar divisão por zero
    rampas_ativas = safe_int(row["rampas_ativas"],0)
    #rampas_clientes = row["rampas_clientes"] or 0
    #rampas_internas = row["rampas_internas"] or 0
    meta_rampa = safe_int(row["meta_rampa"],1)
    
    # Calcular proporções
    prop_internas = row["progresso_internas"]
    prop_rampas = row["ocupacao_rampas"]
    
    # Layout: Nome | Backlog | Barra Internas | Barra Rampas | Mecânicos
    col_nome, col_backlog, col_internas, col_rampas, col_mecanicos = st.columns([2, 1, 2, 2, 4])
        
    with col_nome:
        st.write(f"{nome}")
    
    with col_backlog:
        st.write(f"{backlog}")
    
    with col_internas:
        # Barra de progresso internas (vermelho → verde) com valores nas laterais
        cor = get_progress_color(prop_internas)
        pct = min(prop_internas * 100, 100)
        
        # Criar tooltip com informações das internas realizadas
        lista_internas = row.get("lista_internas_realizadas", [])
        if lista_internas:
            placas = [item.get("placa", "N/A") for item in lista_internas]
            tooltip_internas = "\n".join([f"Placa: {placa}" for placa in placas])
            # Escapar aspas para não quebrar o HTML
            tooltip_internas = tooltip_internas.replace('"', '&quot;')
        else:
            tooltip_internas = "Nenhuma interna realizada"
        
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-weight: bold; min-width: 25px;">{internas}</span>
            <div style="background-color: #ddd; border-radius: 5px; height: 20px; flex: 1;">
                <div style="background-color: {cor}; width: {pct}%; height: 100%; border-radius: 5px;" title="{tooltip_internas}"></div>
            </div>
            <span style="color: #666; min-width: 25px;">{meta_interna}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col_rampas:
        # Barra segmentada de rampas
        if meta_rampa > 0:
            segments_html = ""
            rampas_list = sorted(row["rampas"], key=ordem_rampas)
            total_slots = max(len(rampas_list), int(meta_rampa))
            
            # Iterar sobre cada slot de rampa
            for j in range(total_slots):
                # Se temos uma rampa neste índice
                if j < len(rampas_list):
                    rampa = rampas_list[j]
                    # Verificar o tipo da rampa
                    if rampa["tipo_manutencao"] == "Cliente":
                        color = "#3632a8"  # Azul - cliente
                    else:
                        color = "#28a745"  # Verde - interna
                    
                    # Verificar se é box rápido
                    border_style = ""
                    if rampa.get("box_rapido", False):
                        # Borda quadriculada para box rápido (estilo bandeira F1)
                        border_style = "border: 2px dashed white; background-image: linear-gradient(45deg, rgba(255,255,255,.3) 25%, transparent 25%, transparent 50%, rgba(255,255,255,.3) 50%, rgba(255,255,255,.3) 75%, transparent 75%, transparent); background-size: 8px 8px;"
                    
                    # Criar tooltip com informações da rampa
                    tooltip = f"Mecânico: {rampa.get('mecanico', 'N/A')}\nPlataforma: {rampa.get('plataforma', 'N/A')}\nPlaca: {rampa.get('placa', 'N/A')}\nTipo: {rampa.get('tipo_manutencao', 'N/A')}\nBox Rápido: {'Sim' if rampa.get('box_rapido') else 'Não'}"
                    
                    # Escapar aspas para não quebrar o HTML
                    tooltip = tooltip.replace('"', '&quot;')
                else:
                    # Slot vazio (abaixo da meta)
                    color = "#dc3545"  # Vermelho - inativa
                    border_style = ""
                    tooltip = "Rampa vazia"
                
                segments_html += f'<div style="flex: 1; background-color: {color}; height: 20px; margin: 0 1px; border-radius: 3px; {border_style}" title="{tooltip}"></div>'
            
            st.markdown(f"""
            <div style="display: flex; width: 100%;">
                {segments_html}
            </div>
            <div style="text-align: center; font-size: 11px; color: #666;">{len(rampas_list)}/{meta_rampa}</div>
            """, unsafe_allow_html=True)
        else:
            st.write("—")
    
    with col_mecanicos:
        # Exibir mecânicos de forma simples
        mecs = row.get("mecs", {})
        if mecs:
            # Criar uma string simples com contagem de mecânicos por status
            em_manutencao_count = 0
            sem_manutencao_count = 0
            inativos_count = 0
            
            for mec_id, mec_data in mecs.items():
                ultima_atividade = mec_data.get("ultima_atividade")
                em_manutencao = mec_data.get("emManutencao", False)
                delta_texto = format_time_delta(ultima_atividade)
                
                if ultima_atividade is None or delta_texto == "sem atividade":
                    inativos_count += 1
                elif em_manutencao:
                    em_manutencao_count += 1
                else:
                    sem_manutencao_count += 1
            
            # Criar layout com duas colunas para colocar o dropdown à direita
            col1, col2 = st.columns([3, 1])
            
            # Exibir resumo com ícones coloridos na coluna da esquerda
            with col1:
                st.markdown(f"<span style='color:green'>🟢 Em manutenção: {em_manutencao_count}</span> | "
                          f"<span style='color:purple'>🟣 Sem manutenção: {sem_manutencao_count}</span> | "
                          f"<span style='color:gray'>⚫ Inativos: {inativos_count}</span>", 
                          unsafe_allow_html=True)
            
            # Usar expander na coluna da direita
            with col2:
                with st.expander(f"Ver detalhes ({len(mecs)})"): 
                    # Criar tabela para exibir os mecânicos
                    mecanicos_data = []
                    
                    # Adicionar cada mecânico à lista
                    for mec_id, mec_data in mecs.items():
                        nome_mec = mec_data.get("nome", "Desconhecido")
                        ultima_atividade = mec_data.get("ultima_atividade")
                        em_manutencao = mec_data.get("emManutencao", False)
                        delta_texto = format_time_delta(ultima_atividade)
                        
                        if ultima_atividade is None or delta_texto == "sem atividade":
                            status = "Inativo"
                        elif em_manutencao:
                            status = "Em manutenção"
                        else:
                            status = "Sem manutenção"
                        
                        mecanicos_data.append({
                            "Nome": nome_mec,
                            "Status": status,
                            "Tempo": delta_texto
                        })
                    
                    # Criar e exibir DataFrame
                    df_mecanicos = pd.DataFrame(mecanicos_data)
                    st.dataframe(df_mecanicos, hide_index=True)
        else:
            st.write("Sem mecânicos")

st.divider()