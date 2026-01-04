# data_loader.py
import streamlit as st
import pandas as pd
import gspread
import gspread.utils # Essencial para o update_rotina

# --- Configurações de Governança ---

SHEET_NAMES = [
    'REGULACAO',
    'INTERNACAO',
    'UTI',
    'CENTRO_CIRURGICO',
    'RECEPCAO_PS',
    'RECEPCAO_CENTRAL',
    'PORTARIA',
    'MEDICOS',
    'ENFERMAGEM',
    'MANUTENCAO'
]

try:
    SPREADSHEET_ID = st.secrets["spreadsheet_ids"]["rotinas_hospitalares"] 
except KeyError:
    # Caso o secret falhe, use None e o erro será tratado na função de carga
    SPREADSHEET_ID = None

# --- Função Principal de Carga de Dados (Read) ---

@st.cache_data 
def load_all_rotinas_from_drive():
    """Carrega dados de todas as abas da Planilha Google, garantindo colunas consistentes."""
    all_data = []
    
    try:
        if not SPREADSHEET_ID:
            raise KeyError("ID da planilha 'rotinas_hospitalares' não encontrado nos secrets.")
            
        gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        sh = gc.open_by_key(SPREADSHEET_ID)
        
        # 1. Definir o cabeçalho alvo (Garantir que a nova coluna existe na planilha)
        # O Sheets deve ter: ID_DA_ROTINA, TITULO_PROCEDIMENTO, FLUXO_PRINCIPAL, ACOES, OBSERVACOES, URL_IMAGEM
        
        for name in SHEET_NAMES:
            worksheet = sh.worksheet(name)
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            # 2. Adiciona a coluna 'SETOR' e garante que a URL_IMAGEM exista
            df['SETOR'] = name
            
            # Tratamento de coluna faltando (garante que não quebra se faltar URL_IMAGEM em abas antigas)
            if 'URL_IMAGEM' not in df.columns:
                df['URL_IMAGEM'] = '' 
            
            all_data.append(df)

        # 3. Concatena tudo
        df_final = pd.concat(all_data, ignore_index=True)
        return df_final

    except KeyError as e:
        st.error(f"ERRO DE CONFIGURAÇÃO: Chave {e} faltando. Verifique secrets.toml ou as chaves.")
        return pd.DataFrame()
    except gspread.exceptions.APIError as e:
        st.error(f"ERRO DE PERMISSÃO: Service Account precisa ser Editor. Detalhes: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro Inesperado na carga de dados: {e}")
        return pd.DataFrame()

# --- As funções: append_new_rotina, update_rotina, delete_rotina (invariáveis, pois as mudanças foram no app.py) ---
# ... (Mantenha o resto do data_loader.py inalterado, como na resposta anterior) ...
