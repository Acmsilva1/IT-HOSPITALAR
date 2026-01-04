# data_loader.py
import streamlit as st
import pandas as pd
import gspread
import gspread.utils # <-- CORREÇÃO: Importado globalmente para evitar o erro de escopo

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
    SPREADSHEET_ID = None

# --- Função Principal de Carga de Dados (Read) ---

@st.cache_data 
def load_all_rotinas_from_drive():
    """Carrega dados de todas as abas da Planilha Google."""
    all_data = []
    
    try:
        gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        
        if not SPREADSHEET_ID:
            raise KeyError("ID da planilha não encontrado nos secrets.")
            
        sh = gc.open_by_key(SPREADSHEET_ID)
        
        for name in SHEET_NAMES:
            worksheet = sh.worksheet(name)
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            df['SETOR'] = name
            all_data.append(df)

        df_final = pd.concat(all_data, ignore_index=True)
        return df_final

    except KeyError as e:
        st.error(f"ERRO DE CONFIGURAÇÃO (KeyError): Verifique se a chave '{e}' está correta nos Secrets.")
        return pd.DataFrame()
    except gspread.exceptions.APIError as e:
        st.error(f"ERRO DE PERMISSÃO (403 Forbidden): Certifique-se de que a Service Account foi adicionada como Editor na Planilha Google.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro Inesperado ao carregar dados: {e}")
        return pd.DataFrame()


# --- Função: Escrita no Google Sheets (Create) ---

def append_new_rotina(data: dict, sheet_name: str):
    """Conecta ao Google Sheets e anexa uma nova linha de dados (Rotina)."""
    try:
        gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        sh = gc.open_by_key(SPREADSHEET_ID)
        worksheet = sh.worksheet(sheet_name)
        
        headers = worksheet.row_values(1)
        values = [data.get(header.strip(), '') for header in headers]
        
        worksheet.append_row(values, value_input_option='USER_ENTERED')
        
        return True

    except Exception as e:
        st.error(f"Erro ao escrever na aba {sheet_name}. Detalhes: {e}")
        return False

# --- Função: Atualizar Rotina Existente (Update) ---

def update_rotina(sheet_name: str, old_title: str, new_data: dict):
    """Busca uma rotina pelo TITULO_PROCEDIMENTO na aba específica e atualiza sua linha."""
    try:
        gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        sh = gc.open_by_key(SPREADSHEET_ID)
        worksheet = sh.worksheet(sheet_name)
        
        all_values = worksheet.get_all_values()
        headers = all_values[0]
        
        try:
            title_col_index = headers.index("TITULO_PROCEDIMENTO")
        except ValueError:
            st.error("Coluna 'TITULO_PROCEDIMENTO' não encontrada. Verifique os cabeçalhos do Sheets.")
            return False

        row_index_to_update = -1
        for i, row in enumerate(all_values[1:]): 
            if row[title_col_index] == old_title:
                row_index_to_update = i + 2 
                break
        
        if row_index_to_update == -1:
            st.warning(f"Rotina com título '{old_title}' não encontrada para edição na aba '{sheet_name}'.")
            return False
            
        new_values_list = []
        for header in headers:
            new_val = new_data.get(header.strip(), all_values[row_index_to_update - 1][headers.index(header)])
            new_values_list.append(str(new_val))

        # Atualizar a linha inteira no Sheets (usa gspread.utils importado globalmente)
        range_to_update = f'A{row_index_to_update}:{gspread.utils.rowcol_to_a1(row_index_to_update, len(headers))}'
        
        worksheet.update(range_to_update, [new_values_list], value_input_option='USER_ENTERED')
        
        return True

    except Exception as e:
        st.error(f"Erro ao atualizar a rotina '{old_title}' na aba '{sheet_name}'. Detalhes: {e}")
        return False


# --- Função: Excluir Rotina (Delete) ---

def delete_rotina(sheet_name: str, title_to_delete: str):
    """Busca uma rotina pelo TITULO_PROCEDIMENTO na aba específica e a deleta."""
    try:
        gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"]) 
        sh = gc.open_by_key(SPREADSHEET_ID)
        worksheet = sh.worksheet(sheet_name)
        
        all_values = worksheet.get_all_values()
        headers = all_values[0]
        
        try:
            title_col_index = headers.index("TITULO_PROCEDIMENTO")
        except ValueError:
            st.error("Coluna 'TITULO_PROCEDIMENTO' não encontrada. Verifique os cabeçalhos do Sheets.")
            return False

        row_index_to_delete = -1
        for i, row in enumerate(all_values[1:]): 
            if row[title_col_index] == title_to_delete:
                row_index_to_delete = i + 2 
                break
        
        if row_index_to_delete == -1:
            st.warning(f"Rotina com título '{title_to_delete}' não encontrada para exclusão na aba '{sheet_name}'.")
            return False
            
        worksheet.delete_rows(row_index_to_delete)
        
        return True

    except Exception as e:
        st.error(f"Erro ao deletar a rotina '{title_to_delete}' na aba '{sheet_name}'. Detalhes: {e}")
        return False
