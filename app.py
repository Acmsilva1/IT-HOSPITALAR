import streamlit as st
import pandas as pd
from data_loader import load_all_rotinas_from_drive 

st.set_page_config(
    page_title="SGC Hospitalar - Rotinas", 
    layout="wide"
)

# --- Carregamento de Dados ---
# Tenta carregar os dados. A função trata erros de conexão e credenciais.
df_rotinas = load_all_rotinas_from_drive()

# --- Configuração de Layout e Título ---
st.title("🏥 Sistema de Gerenciamento de Conhecimento Hospitalar (SGC)")

if df_rotinas.empty:
    # Se der erro (credenciais/permissão), o data_loader já mostra a mensagem.
    st.info("Aguardando dados da Planilha. Se o erro acima persistir, verifique as credenciais e as permissões.")
    st.markdown("---")
else:
    # Obtém a lista de setores (abas)
    setor_options = sorted(df_rotinas['SETOR'].unique().tolist())

    # --- Sidebar: Menu Principal de Seleção ---
    st.sidebar.header("🧭 Navegação por Setor")
    
    # Adiciona a opção de "Tela Inicial" para não mostrar dados na abertura
    menu_options = ["— Selecione um Setor —"] + setor_options
    
    # Widget de seleção na barra lateral
    selected_setor = st.sidebar.selectbox(
        "Escolha a Área de Interesse", 
        menu_options
    )
    
    # --- Corpo da Aplicação (Onde a Mágica Acontece) ---
    st.markdown("---")

    if selected_setor == "— Selecione um Setor —":
        # 1. Tela Inicial Limpa (sem dados brutos)
        st.header("Seja bem-vindo(a) ao Guia de Rotinas Tasy/SGC")
        st.info(
            f"Use o menu lateral (**Navegação por Setor**) para acessar as rotinas específicas "
            f"de cada uma das **{len(setor_options)}** áreas (como INTERNACAO, UTI, etc.)."
        )
        st.markdown("##### Foco em Ação, Não em Burocracia.")
        st.caption("Última atualização de dados: " + pd.Timestamp.now().strftime("%d/%m/%Y %H:%M:%S"))

    else:
        # 2. Tela de Visualização do Setor Selecionado
        
        # Filtro de Busca (Aparece somente após a seleção do setor)
        st.sidebar.markdown("---")
        search_query = st.sidebar.text_input(
            f"🔎 Buscar em Rotinas de {selected_setor}",
            help="Busca no Título do Procedimento e nas Ações/Passos."
        )

        st.header(f"Setor: {selected_setor} Rotinas Tasy")
        df_filtered = df_rotinas[df_rotinas['SETOR'] == selected_setor].copy()

        # Aplicação do Filtro de Texto
        if search_query:
            search_query = search_query.lower()
            df_filtered = df_filtered[
                df_filtered['TITULO_PROCEDIMENTO'].astype(str).str.lower().str.contains(search_query) | 
                df_filtered['ACOES'].astype(str).str.lower().str.contains(search_query)
            ]
        
        st.subheader(f"Total de Rotinas Encontradas: {len(df_filtered)}")
        
        # --- Apresentação dos Resultados Detalhados ---
        if not df_filtered.empty:
            for index, row in df_filtered.iterrows():
                st.markdown(f"### 📋 {row['TITULO_PROCEDIMENTO']}")
                
                acoes_str = row['ACOES']
                # Garante que a quebra por '#' funcione e trate valores nulos/simples
                acoes_list = acoes_str.split('#') if isinstance(acoes_str, str) and '#' in acoes_str else [acoes_str]
                
                # Tabela de Metadados (visão rápida)
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("ID da Rotina", row['ID_DA_ROTINA'])
                    st.caption(f"Fluxo: {row['FLUXO_PRINCIPAL']}")
                with col2:
                    st.warning(f"⚠️ Observações: {row['OBSERVACOES']}" if row['OBSERVACOES'] else "Sem observações críticas.")

                st.markdown("#### 🚀 Passo a Passo Objetivo:")
                
                # Renderização do Passo a Passo em lista
                for i, passo in enumerate(acoes_list):
                     if passo and passo.strip():
                        st.markdown(f"*{i+1}.* **{passo.strip()}**")
                
                st.markdown("---") # Separador visual
        else:
            st.warning("Nenhuma rotina encontrada com os filtros selecionados. Tente termos menos específicos.")

# --- Rodapé ---
st.sidebar.caption("Lembrete LGPD: SGC lida apenas com metadados de processos, sem Dados Pessoais.")
