import streamlit as st
import pandas as pd
import gspread
# A importação antiga e com erro (gspread.utils) já não está mais aqui.

# ... (código das listas e SPREADSHEET_ID, etc.) ...

@st.cache_data(ttl=600)
def load_all_rotinas_from_drive():
    # ... (código do 'all_data = []' e try/except) ...
    
    try:
        # 1. Autenticação Segura via Streamlit Secrets (CORRIGIDO PARA service_account_from_dict!)
        # Esta função foi feita para consumir o dicionário de secrets do Streamlit.
        gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        
        # 2. Abre a planilha pelo ID
        sh = gc.open_by_key(SPREADSHEET_ID)
        
        # ... (o resto da lógica permanece a mesma) ...
