# token_manager.py
import requests
import streamlit as st

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
