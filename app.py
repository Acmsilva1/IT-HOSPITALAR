import streamlit as st
import pandas as pd
# Importa a função do módulo de dados para manter o código limpo
from data_loader import load_all_rotinas_from_drive 

st.set_page_config(
    page_title="SGC Hospitalar - Rotinas", 
    layout="wide"
)

# --- Carregamento de Dados ---
# Tenta carregar os dados; se falhar, exibe o erro do data_loader.py
df_rotinas = load_all_rotinas_from_drive()

# --- Configuração de Layout e Título ---
st.title("🏥 Sistema de Gerenciamento de Conhecimento Hospitalar")
st.markdown("---")

if not df_rotinas.empty:
    
    # --- Sidebar com Filtros (Simulando a Navegação do Diagrama) ---
    st.sidebar.header("🔎 Filtros de Rotinas")
    
    # Filtro 1: Seleção do Setor (as abas)
    setor_options = ['TODOS'] + sorted(df_rotinas['SETOR'].unique().tolist())
    selected_setor = st.sidebar.selectbox("Setor Principal", setor_options)
    
    # Filtro 2: Busca por Palavra-Chave
    search_query = st.sidebar.text_input("Buscar em Título/Ações")

    # --- Aplicação dos Filtros ---
    df_filtered = df_rotinas.copy()
    
    # 1. Filtrar por Setor
    if selected_setor != 'TODOS':
        df_filtered = df_filtered[df_filtered['SETOR'] == selected_setor]

    # 2. Filtrar por Busca de Texto
    if search_query:
        search_query = search_query.lower()
        df_filtered = df_filtered[
            df_filtered['TITULO_PROCEDIMENTO'].astype(str).str.lower().str.contains(search_query) | 
            df_filtered['ACOES'].astype(str).str.lower().str.contains(search_query)
        ]

    # --- Apresentação dos Resultados ---
    st.subheader(f"Rotinas Encontradas: {len(df_filtered)}")

    if not df_filtered.empty:
        for index, row in df_filtered.iterrows():
            st.markdown(f"### 📋 {row['TITULO_PROCEDIMENTO']} ({row['SETOR']})")
            
            # Divide as ações por '#' (seu delimitador) para criar a lista de passos
            acoes_str = row['ACOES']
            acoes_list = acoes_str.split('#') if isinstance(acoes_str, str) and '#' in acoes_str else [acoes_str]
            
            # Tabela de Metadados (visão rápida)
            col1, col2, col3 = st.columns(3)
            col1.metric("ID da Rotina", row['ID_DA_ROTINA'])
            col2.metric("Fluxo Principal", row['FLUXO_PRINCIPAL'])
            col3.markdown(f"**Observações:** *{row['OBSERVACOES']}*")
            
            st.markdown("#### 🚀 Passo a Passo Objetivo:")
            
            # Renderização do Passo a Passo
            for i, passo in enumerate(acoes_list):
                 if passo.strip(): # Garante que não renderize passos vazios
                    st.markdown(f"*{i+1}.* **{passo.strip()}**")
            
            st.markdown("---") # Separador visual para a próxima rotina
    else:
        st.warning("Nenhuma rotina encontrada com os filtros selecionados. Tente termos menos específicos.")

# --- Dica LGPD no Rodapé ---
st.sidebar.caption("Lembrete LGPD: Este SGC lida apenas com metadados de processos, sem Dados Pessoais Sensíveis.")
