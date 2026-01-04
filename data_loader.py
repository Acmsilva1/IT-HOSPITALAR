import streamlit as st
import pandas as pd
import gspread

# --- Configurações de Governança (Sem Alteração) ---

# Lista de todas as abas (Worksheets) a serem lidas para unificação
SHEET_NAMES = [
    'REGULACAO',
    'INTERNACAO',
    'UTI',
    'CENTRO_CIRURGICO',
    'RECEPCAO_PS',
    'RECEPCAO_CENTRAL',
    'PORTARIA',
    'MEDICOS',
    'ENFERMAGEM',   # <<-- NOVA ABA
    'MANUTENCAO'    # <<-- NOVA ABA
]

# ID da planilha lido dos secrets para segurança
try:
    SPREADSHEET_ID = st.secrets["spreadsheet_ids"]["rotinas_hospitalares"] 
except KeyError:
    SPREADSHEET_ID = None

# --- Função Principal de Carga de Dados ---

@st.cache_data # ALTERADO: Removido o (ttl=600). Agora o cache só é limpo com .clear() ou F5.
def load_all_rotinas_from_drive():
    """
    Carrega dados de todas as abas da Planilha Google de forma segura 
    e os consolida em um único DataFrame.
    """
    all_data = []
    
    # ... (Resto do código sem alteração) ...
    try:
        # 1. Autenticação Segura (função corrigida)
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
        st.error(f"ERRO DE CONFIGURAÇÃO (KeyError): Verifique se a chave '{e}' está correta nos Secrets.")
        return pd.DataFrame()
    except gspread.exceptions.APIError as e:
        # Lembrete de governança: Certifique-se que este e-mail tem acesso de Leitor.
        st.error(f"ERRO DE PERMISSÃO (403 Forbidden): Certifique-se de que a Service Account foi adicionada como Leitor na Planilha Google.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro Inesperado ao carregar dados: {e}")
        return pd.DataFrame()
