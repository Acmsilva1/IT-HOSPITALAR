import streamlit as st
import pandas as pd
import gspread

# --- Configurações de Governança ---

# Lista de todas as abas (Worksheets) a serem lidas para unificação
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

# ID da planilha lido dos secrets para segurança
try:
    SPREADSHEET_ID = st.secrets["spreadsheet_ids"]["rotinas_hospitalares"] 
except KeyError:
    # Caso essa chave não exista, a exceção será tratada na função principal, mas 
    # é bom ter o try/except para evitar falhas imediatas de script loading.
    SPREADSHEET_ID = None

# --- Função Principal de Carga de Dados ---

@st.cache_data(ttl=600) # Armazena em cache por 10 minutos
def load_all_rotinas_from_drive():
    """
    Carrega dados de todas as abas da Planilha Google de forma segura 
    e os consolida em um único DataFrame.
    """
    all_data = []
    
    try:
        # 1. Autenticação Segura via Streamlit Secrets (CORREÇÃO FINAL)
        # Usa service_account_from_dict, a função correta para dicionários de credenciais.
        gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        
        # 2. Abre a planilha pelo ID
        if not SPREADSHEET_ID:
            raise KeyError("ID da planilha não encontrado nos secrets.")
            
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
        # Erro comum: Chave faltando ou incorreta no secrets.toml
        st.error(f"ERRO DE CONFIGURAÇÃO (KeyError): Verifique se a chave '{e}' está correta nos Secrets.")
        return pd.DataFrame()
    except gspread.exceptions.APIError as e:
        # Erro comum: A Service Account não tem permissão de Leitor na planilha.
        st.error(f"ERRO DE PERMISSÃO (403 Forbidden): Certifique-se de que a Service Account ({st.secrets['gcp_service_account']['client_email']}) foi adicionada como Leitor na Planilha Google.")
        return pd.DataFrame()
    except Exception as e:
        # Erros genéricos de conexão
        st.error(f"Erro Inesperado ao carregar dados: {e}")
        return pd.DataFrame()
