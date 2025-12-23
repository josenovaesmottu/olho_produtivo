import requests
import streamlit as st

def retorna_token():
    #username = st.secrets["MOTTU_USERNAME"]
    #password = st.secrets["MOTTU_PASSWORD"]
    username = "victor.mello@mottu.com.br"
    password = "9PUCHTAX@"

    url = "https://sso.mottu.cloud/realms/Internal/protocol/openid-connect/token"
    payload = {
        "username": username,
        "password": password,
        "grant_type": "password",
        "client_id": "admin-v3-frontend-client",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        token = response.json()["access_token"]
    return token