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

@st.cache_data 
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


# --- Função: Escrita no Google Sheets (Create) ---

def append_new_rotina(data: dict, sheet_name: str):
    """
    Conecta ao Google Sheets e anexa uma nova linha de dados (Rotina).
    """
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

# --- NOVA FUNÇÃO: Atualizar Rotina Existente (Update) ---

def update_rotina(sheet_name: str, old_title: str, new_data: dict):
    """
    Busca uma rotina pelo TITULO_PROCEDIMENTO na aba específica e atualiza sua linha.
    """
    try:
        gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
        sh = gc.open_by_key(SPREADSHEET_ID)
        worksheet = sh.worksheet(sheet_name)
        
        # 1. Obter todos os valores da planilha para encontrar a linha
        all_values = worksheet.get_all_values()
        headers = all_values[0]
        
        # Localiza o índice da coluna do TITULO_PROCEDIMENTO (para buscar)
        try:
            title_col_index = headers.index("TITULO_PROCEDIMENTO")
        except ValueError:
            st.error("Coluna 'TITULO_PROCEDIMENTO' não encontrada. Verifique os cabeçalhos do Sheets.")
            return False

        # 2. Encontrar o índice da linha que corresponde ao título
        row_index_to_update = -1
        # Começamos a buscar da linha 2 (índice 1 no array, pois all_values[0] são os headers)
        for i, row in enumerate(all_values[1:]): 
            if row[title_col_index] == old_title:
                # O índice da linha no Sheets é i + 2 (1 para headers, 1 para conversão de índice 0)
                row_index_to_update = i + 2 
                break
        
        if row_index_to_update == -1:
            st.warning(f"Rotina com título '{old_title}' não encontrada para edição na aba '{sheet_name}'.")
            return False
            
        # 3. Preparar os novos valores na ordem correta dos cabeçalhos
        new_values_list = []
        for header in headers:
            # Pega o novo valor do dicionário 'new_data'.
            # Se o header não estiver no dicionário, tentamos pegar o valor antigo para evitar apagar.
            new_val = new_data.get(header.strip(), all_values[row_index_to_update - 1][headers.index(header)])
            new_values_list.append(str(new_val))

        # 4. Atualizar a linha inteira no Sheets
        # Cria a string de faixa (ex: 'A5:F5')
        range_to_update = f'A{row_index_to_update}:{gspread.utils.rowcol_to_a1(row_index_to_update, len(headers))}'
        
        worksheet.update(range_to_update, [new_values_list], value_input_option='USER_ENTERED')
        
        return True

    except Exception as e:
        st.error(f"Erro ao atualizar a rotina '{old_title}' na aba '{sheet_name}'. Detalhes: {e}")
        return False
