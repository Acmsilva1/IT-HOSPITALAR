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
    'MEDICOS',
    'ENFERMAGEM',
    'MANUTENCAO'
]

# ID da planilha lido dos secrets para segurança
try:
    SPREADSHEET_ID = st.secrets["spreadsheet_ids"]["rotinas_hospitalares"] 
except KeyError:
    SPREADSHEET_ID = None

# --- Função Principal de Carga de Dados (Read) ---

@st.cache_data # ALTERADO: Removido o (ttl=600). O cache agora só é limpo com .clear() ou F5.
def load_all_rotinas_from_drive():
    """
    Carrega dados de todas as abas da Planilha Google de forma segura 
    e os consolida em um único DataFrame.
    """
    all_data = []
    
    try:
        # 1. Autenticação Segura
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
        st.error(f"ERRO DE PERMISSÃO (403 Forbidden): Certifique-se de que a Service Account foi adicionada como Leitor na Planilha Google.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro Inesperado ao carregar dados: {e}")
        return pd.DataFrame()


# --- NOVA FUNÇÃO: Escrita no Google Sheets (Append) ---

def append_new_rotina(data: dict, sheet_name: str):
    """
    Conecta ao Google Sheets e anexa uma nova linha de dados (Rotina).
    
    data: Dicionário onde as chaves devem bater com os nomes das colunas.
    sheet_name: A aba específica onde a rotina será adicionada.
    """
    try:
        # 1. Autenticação Segura
        gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        
        # 2. Abre a planilha pelo ID
        if not SPREADSHEET_ID:
            raise KeyError("ID da planilha não encontrado nos secrets.")
            
        sh = gc.open_by_key(SPREADSHEET_ID)
        
        # 3. Abre a aba desejada
        worksheet = sh.worksheet(sheet_name)
        
        # 4. Obtém os cabeçalhos (para garantir a ordem correta)
        headers = worksheet.row_values(1)
        
        # 5. Cria a lista de valores na ordem dos cabeçalhos
        values = [data.get(header.strip(), '') for header in headers]
        
        # 6. Anexa a nova linha
        worksheet.append_row(values, value_input_option='USER_ENTERED')
        
        return True

    except Exception as e:
        st.error(f"Erro ao escrever na aba {sheet_name}. Detalhes: {e}")
        return False
