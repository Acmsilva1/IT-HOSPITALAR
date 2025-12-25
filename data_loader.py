import streamlit as st
import pandas as pd
import gspread
# A importação antiga e com erro (gspread.utils) foi removida.

# Lista de todas as abas (Worksheets) a serem lidas
SHEET_NAMES = [
    'REGULACAO',
    'INTERNACAO',
    'UTI',
    'CENTRO_CIRURGICO',
    'RECEPCAO_PS',
    'RECEPCAO_CENTRAL',
    'PORTARIA',
    'MEDICOS' 
]

# ID da sua planilha (1pHQr_ZII7Kv4WT-lYwJ1h4xiWUxB4RxSpgy7KFIEK5k)
SPREADSHEET_ID = st.secrets["spreadsheet_ids"]["rotinas_hospitalares"] 

@st.cache_data(ttl=600) # Cache por 10 minutos para evitar chamadas excessivas à API
def load_all_rotinas_from_drive():
    """
    Carrega dados de todas as abas da Planilha Google de forma segura 
    usando as credenciais do Streamlit Secrets.
    """
    all_data = []
    
    try:
        # 1. Autenticação Segura via Streamlit Secrets (CORRIGIDO!)
        # O StreamlitSecrets injeta o dicionário JSON diretamente.
        gc = gspread.service_account(info=st.secrets["gcp_service_account"])
        
        # 2. Abre a planilha pelo ID
        sh = gc.open_by_key(SPREADSHEET_ID)
        
        # 3. Itera sobre todas as abas e unifica os dados
        for name in SHEET_NAMES:
            worksheet = sh.worksheet(name)
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            # Adiciona a coluna 'SETOR' para fácil filtragem
            df['SETOR'] = name
            all_data.append(df)

        # 4. Concatena tudo em um DataFrame único
        df_final = pd.concat(all_data, ignore_index=True)
        return df_final

    except KeyError as e:
        st.error(f"ERRO DE CONFIGURAÇÃO: Chave secreta '{e}' não encontrada. Verifique .streamlit/secrets.toml ou a configuração de Secrets no Streamlit Sharing.")
        return pd.DataFrame()
    except Exception as e:
        # Se falhar aqui, o problema é na permissão da planilha ou no JSON formatado errado.
        st.error(f"Erro ao conectar ou ler a planilha: {e}. Verifique o acesso da Service Account.")
        return pd.DataFrame()
