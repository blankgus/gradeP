import streamlit as st
from google_auth_oauthlib.flow import Flow
import os
import json
import requests

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

def get_google_flow():
    with open("client_secret.json", "r") as f:
        client_config = json.load(f)["web"]
    return Flow.from_client_config(
        client_config,
        scopes=[
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid"
        ],
        redirect_uri="http://localhost:8501"
    )

def login():
    flow = get_google_flow()
    auth_url, _ = flow.authorization_url(prompt="consent")
    st.markdown(f'<a href="{auth_url}" style="display:inline-block;background:#4285F4;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">🔐 Login com Google</a>', unsafe_allow_html=True)

def handle_redirect():
    if "code" in st.query_params:
        flow = get_google_flow()
        flow.fetch_token(code=st.query_params["code"])
        resp = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {flow.credentials.token}"}
        )
        st.session_state.user = resp.json()
        st.query_params.clear()
        st.rerun()
