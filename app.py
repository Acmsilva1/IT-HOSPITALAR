import streamlit as st
import pandas as pd
# Importa as três funções de manipulação e o load
from data_loader import load_all_rotinas_from_drive, append_new_rotina, update_rotina, delete_rotina 

# --- FUNÇÕES DE PÁGINA ---

def main_view(df_rotinas, setor_options):
    """Lógica da Página de Visualização de Rotinas (Read)"""
    st.header("🔍 Visualização de Rotinas do SGC Hospitalar")
    # ... (restante do código da main_view inalterado) ...
    st.sidebar.header("🧭 Navegação por Setor")
    
    menu_options = ["— Selecione um Setor —"] + setor_options
    
    selected_setor = st.sidebar.selectbox(
        "Escolha a Área de Interesse", 
        menu_options
    )
    
    st.markdown("---")

    if selected_setor == "— Selecione um Setor —":
        st.header("Seja bem-vindo(a) ao Guia de Rotinas Tasy/SGC")
        st.info(
            f"Use o menu lateral (**Navegação por Setor**) para acessar as rotinas específicas "
            f"de cada uma das **{len(setor_options)}** áreas."
        )
        st.markdown("##### Foco em Ação, Não em Burocracia.")
        st.caption("Última atualização de dados: " + pd.Timestamp.now().strftime("%d/%m/%Y %H:%M:%S"))
    
    else:
        st.sidebar.markdown("---")
        search_query = st.sidebar.text_input(
            f"🔎 Buscar em Rotinas de {selected_setor}",
            help="Busca no Título do Procedimento e nas Ações/Passos."
        )

        st.header(f"Setor: {selected_setor} Rotinas Tasy")
        df_filtered = df_rotinas[df_rotinas['SETOR'] == selected_setor].copy()

        if search_query:
            search_query = search_query.lower()
            df_filtered = df_filtered[
                df_filtered['TITULO_PROCEDIMENTO'].astype(str).str.lower().str.contains(search_query) | 
                df_filtered['ACOES'].astype(str).str.lower().str.contains(search_query)
            ]
        
        st.subheader(f"Total de Rotinas Encontradas: {len(df_filtered)}")
        
        if not df_filtered.empty:
            for index, row in df_filtered.iterrows():
                st.markdown(f"### 📋 {row['TITULO_PROCEDIMENTO']}")
                
                acoes_str = row['ACOES']
                acoes_list = acoes_str.split('#') if isinstance(acoes_str, str) and '#' in acoes_str else [acoes_str]
                
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.metric("ID da Rotina", row['ID_DA_ROTINA'])
                    st.markdown(f"**🔗 Fluxo Tasy:** **{row['FLUXO_PRINCIPAL']}**") 
                with col2:
                    st.warning(f"⚠️ Observações: {row['OBSERVACOES']}" if row['OBSERVACOES'] else "Sem observações críticas.")

                st.markdown("#### 🚀 Passo a Passo Objetivo:")
                
                for i, passo in enumerate(acoes_list):
                     if passo and passo.strip():
                        st.markdown(f"*{i+1}.* **{passo.strip()}**")
                
                st.markdown("---") 
        else:
            st.warning("Nenhuma rotina encontrada com os filtros selecionados.")
            
    st.sidebar.caption("Lembrete LGPD: SGC lida apenas com metadados de processos, sem Dados Pessoais.")


def create_rotina_tab(setor_options):
    """Lógica da Sub-Aba para Criação de Novas Rotinas (Create)"""
    st.subheader("Adicionar Nova Rotina")
    st.info("Preencha o formulário para adicionar uma nova rotina diretamente no Google Sheets.")
    
    with st.form(key='rotina_form'):
        
        selected_setor = st.selectbox(
            "1. Setor de Destino (Aba na Planilha):", 
            options=["— Selecione um Setor —"] + setor_options, 
            key='create_setor_input'
        )
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            titulo = st.text_input("2. Título do Procedimento (TITULO_PROCEDIMENTO):", key='create_titulo_input')
        with col2:
            id_rotina = st.text_input("3. ID da Rotina (ID_DA_ROTINA, Ex: CC-001):", key='create_id_input')
            
        fluxo_principal = st.text_input("4. Fluxo Principal (FLUXO_PRINCIPAL, Ex: TASY > [Menu] > [Submenu]):", key='create_fluxo_input')
        
        acoes = st.text_area(
            "5. Ações/Passo a Passo (ACOES) - Separe cada passo com uma quebra de linha!:", 
            key='create_acoes_input',
            height=200
        )
        
        observacoes = st.text_area("6. Observações (OBSERVACOES - Avisos, Dicas, etc.):", key='create_obs_input')
        
        submit_button = st.form_submit_button(label='💾 Salvar Nova Rotina no Sheets')

    if submit_button:
        if not titulo or not acoes or selected_setor == "— Selecione um Setor —":
            st.error("🚨 Preencha o Título, as Ações/Passos e selecione um Setor de destino.")
            return

        data_to_save = {
            "ID_DA_ROTINA": id_rotina,
            "TITULO_PROCEDIMENTO": titulo,
            "FLUXO_PRINCIPAL": fluxo_principal,
            "ACOES": acoes.replace('\n', '#'), 
            "OBSERVACOES": observacoes
        }
        
        with st.spinner(f"Salvando rotina no Sheets na aba {selected_setor}..."):
            if append_new_rotina(data_to_save, selected_setor):
                load_all_rotinas_from_drive.clear()
                st.success(f"Rotina '{titulo}' salva com sucesso! Pressione 'Atualizar Dados Agora' na Visualização para ver a mudança.")
            else:
                st.warning("Falha ao salvar. Verifique logs ou credenciais.")


def edit_rotina_tab(df_rotinas):
    """Lógica da Sub-Aba para Edição/Exclusão de Rotinas Existentes (Update/Delete)"""
    st.subheader("Alterar ou Excluir Rotina Existente")
    st.info("Selecione uma rotina para carregar, editar ou deletar seus dados. A alteração será salva no Google Sheets.")
    
    # 1. SELEÇÃO DA ROTINA
    rotina_tuples = [(f"{row['TITULO_PROCEDIMENTO']} ({row['SETOR']})", row['TITULO_PROCEDIMENTO']) 
                     for index, row in df_rotinas.iterrows()]
    
    display_options = ["— Selecione uma Rotina —"] + [t[0] for t in rotina_tuples]
    
    selected_display_option = st.selectbox(
        "Selecione a Rotina para Editar/Excluir:",
        options=display_options,
        key='edit_selectbox'
    )
    
    if selected_display_option == "— Selecione uma Rotina —":
        return

    # 2. CARREGAMENTO DOS DADOS ATUAIS
    selected_title = selected_display_option.split(' (')[0]
    current_data = df_rotinas[df_rotinas['TITULO_PROCEDIMENTO'] == selected_title].iloc[0]
    sheet_name = current_data['SETOR']
    
    initial_acoes = current_data['ACOES'].replace('#', '\n') if isinstance(current_data['ACOES'], str) else ""

    st.markdown("---")
    st.caption(f"Rotina Selecionada: **{current_data['TITULO_PROCEDIMENTO']}** na aba **{sheet_name}**")
    
    # 3. FORMULÁRIO DE EDIÇÃO (Pré-preenchido)
    with st.form(key='edit_rotina_form'):
        
        titulo = st.text_input("1. Título do Procedimento (TITULO_PROCEDIMENTO):", 
                               value=current_data['TITULO_PROCEDIMENTO'], 
                               key='edit_titulo_input',
                               help="ATENÇÃO: Este é o campo que identifica a linha no Sheets. Edite apenas se for INTENÇÃO mudar o título.")
        
        col1, col2 = st.columns(2)
        with col1:
            id_rotina = st.text_input("2. ID da Rotina (ID_DA_ROTINA):", 
                                      value=current_data['ID_DA_ROTINA'], 
                                      key='edit_id_input')
        with col2:
            fluxo_principal = st.text_input("3. Fluxo Principal (FLUXO_PRINCIPAL):", 
                                            value=current_data['FLUXO_PRINCIPAL'], 
                                            key='edit_fluxo_input')

        acoes = st.text_area(
            "4. Ações/Passo a Passo (ACOES) - Separe cada passo com uma quebra de linha!:", 
            value=initial_acoes,
            key='edit_acoes_input',
            height=250
        )
        
        observacoes = st.text_area("5. Observações (OBSERVACOES):", 
                                   value=current_data['OBSERVACOES'], 
                                   key='edit_obs_input')
        
        st.markdown("---")
        
        # Botões de Ação (UPDATE e DELETE)
        col_update, col_delete = st.columns(2)
        
        with col_update:
            submit_update = st.form_submit_button(label='✍️ Salvar Alterações (UPDATE)')
            
        with col_delete:
            submit_delete = st.form_submit_button(label='🗑️ Excluir Rotina Permanentemente', type="primary")


    # 4. LÓGICA DE SALVAMENTO (UPDATE)
    if submit_update:
        if not titulo or not acoes:
            st.error("🚨 O Título e as Ações/Passos não podem ficar vazios.")
            return
            
        data_to_update = {
            "ID_DA_ROTINA": id_rotina,
            "TITULO_PROCEDIMENTO": titulo, 
            "FLUXO_PRINCIPAL": fluxo_principal,
            "ACOES": acoes.replace('\n', '#'),
            "OBSERVACOES": observacoes
        }
        
        with st.spinner(f"Atualizando rotina no Sheets na aba {sheet_name}..."):
            # O título ORIGINAL é usado para encontrar a linha!
            if update_rotina(sheet_name, current_data['TITULO_PROCEDIMENTO'], data_to_update):
                load_all_rotinas_from_drive.clear() 
                st.success(f"Rotina '{titulo}' atualizada com sucesso na aba '{sheet_name}'!")
                st.rerun() 
            else:
                st.warning("Falha ao atualizar. Verifique logs ou credenciais.")

    # 5. LÓGICA DE EXCLUSÃO (DELETE)
    if submit_delete:
        # Pede confirmação antes de deletar
        st.warning("CONFIRMAÇÃO: Você tem certeza que deseja EXCLUIR permanentemente esta rotina? Se sim, clique no botão 'Excluir Rotina Permanentemente' novamente.")
        
        # Cria um botão de confirmação separado para a exclusão
        if st.button(f"CONFIRMAR EXCLUSÃO: {selected_title}", type="secondary"):
            with st.spinner(f"Excluindo rotina '{selected_title}' na aba {sheet_name}..."):
                if delete_rotina(sheet_name, selected_title):
                    load_all_rotinas_from_drive.clear()
                    st.success(f"Rotina '{selected_title}' DELETADA com sucesso! Recarregando a página...")
                    st.rerun()
                else:
                    st.error("Falha ao deletar. Rotina não excluída.")


def admin_view(df_rotinas, setor_options):
    """Função Principal do Módulo de Gerenciamento (Tabs)"""
    st.header("🛠️ Gerenciamento de Rotinas (Criação e Edição/Exclusão)")
    st.warning("🚨 Esta página será protegida por senha na próxima etapa de governança.")
    st.info("Utilize as abas abaixo para gerenciar os processos hospitalares.")
    
    tab1, tab2 = st.tabs(["➕ Criar Nova Rotina", "✏️ Alterar/Excluir Rotina Existente"])
    
    with tab1:
        create_rotina_tab(setor_options)
        
    with tab2:
        edit_rotina_tab(df_rotinas) 


# --- FUNÇÃO PRINCIPAL (Estrutura da Aplicação) ---

def main():
    st.set_page_config(
        page_title="SGC Hospitalar - Rotinas", 
        layout="wide"
    )

    st.title("🏥 Sistema de Gerenciamento de Conhecimento Hospitalar (SGC)")

    # --- Lógica Global de Atualização (Mantida) ---
    col_refresh, col_title_info = st.columns([1, 4])
    
    with col_refresh:
        if st.button("🔄 Atualizar Dados Agora", help="Força a busca e o recarregamento dos dados mais recentes da fonte (Google Drive/Planilha)."):
            load_all_rotinas_from_drive.clear()
            st.rerun()

    col_title_info.info("A página é atualizada automaticamente ao ser aberta e quando o botão 'Atualizar Dados Agora' é pressionado.")
    st.markdown("---")

    # --- Carregamento de Dados ---
    with st.spinner('Buscando e carregando dados do SGC Hospitalar...'):
        df_rotinas = load_all_rotinas_from_drive()

    if df_rotinas.empty:
        st.error("Não foi possível carregar os dados. Verifique a conexão com o Sheets e as credenciais.")
        return
        
    setor_options = sorted(df_rotinas['SETOR'].unique().tolist())
    
    # --- SELEÇÃO DE PÁGINA na Sidebar ---
    st.sidebar.header("Módulos")
    
    PAGES = {
        "🔍 Visualização de Rotinas": lambda: main_view(df_rotinas, setor_options),
        "🛠️ Gerenciamento de Dados": lambda: admin_view(df_rotinas, setor_options) 
    }
    
    selection = st.sidebar.radio("Ir para:", list(PAGES.keys()))
    
    PAGES[selection]()

if __name__ == '__main__':
    main()
