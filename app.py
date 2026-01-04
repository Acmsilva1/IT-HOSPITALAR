# app.py
import streamlit as st
import pandas as pd
# Importa todas as funções de data_loader
from data_loader import load_all_rotinas_from_drive, append_new_rotina, update_rotina, delete_rotina 

# --- FUNÇÕES DE PÁGINA (Definidas no escopo global para evitar NameError) ---

def main_view(df_rotinas, setor_options):
    """Lógica da Página de Visualização de Rotinas (Read)"""
    st.header("🔍 Visualização de Rotinas do SGC Hospitalar")
    # ... (código de navegação e filtros) ...
    
    st.sidebar.header("🧭 Navegação por Setor")
    menu_options = ["— Selecione um Setor —"] + setor_options
    selected_setor = st.sidebar.selectbox("Escolha a Área de Interesse", menu_options)
    st.markdown("---")

    if selected_setor == "— Selecione um Setor —":
        # ... (tela de boas vindas) ...
        st.header("Seja bem-vindo(a) ao Guia de Rotinas Tasy/SGC")
        st.info(f"Use o menu lateral para acessar as rotinas específicas de cada uma das **{len(setor_options)}** áreas.")
    else:
        # ... (código de filtro e exibição) ...
        search_query = st.sidebar.text_input(f"🔎 Buscar em Rotinas de {selected_setor}")
        st.header(f"Setor: {selected_setor} Rotinas Tasy")
        df_filtered = df_rotinas[df_rotinas['SETOR'] == selected_setor].copy()

        # [Código de filtro de busca inalterado]

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

                # --- NOVO BLOCO: Exibição da Imagem (st.expander para não poluir) ---
                image_url = row.get('URL_IMAGEM')
                if image_url and str(image_url).strip():
                    with st.expander("🖼️ Clique para visualizar o Anexo/Fluxograma"):
                        st.image(str(image_url), caption=f"Anexo para: {row['TITULO_PROCEDIMENTO']}", width=400)
                # --- FIM NOVO BLOCO ---
                
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
    # ... (código do formulário CREATE) ...
    with st.form(key='rotina_form'):
        
        selected_setor = st.selectbox("1. Setor de Destino:", options=["— Selecione um Setor —"] + setor_options, key='create_setor_input')
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1: titulo = st.text_input("2. Título do Procedimento:", key='create_titulo_input')
        with col2: id_rotina = st.text_input("3. ID da Rotina:", key='create_id_input')
            
        fluxo_principal = st.text_input("4. Fluxo Principal:", key='create_fluxo_input')
        acoes = st.text_area("5. Ações/Passo a Passo:", key='create_acoes_input', height=200)
        observacoes = st.text_area("6. Observações:", key='create_obs_input')
        
        st.markdown("---")
        st.markdown("#### 🖼️ Anexo Visual (Imagem)")

        # Campo de URL para a imagem
        anexo_url = st.text_input("7. URL da Imagem/Fluxograma (Link Direto):", key='create_anexo_url', help="Cole o link direto da imagem aqui (salva no Drive/GitHub, etc.).")

        # Uploader para pré-visualização
        uploaded_file = st.file_uploader("Upload de Imagem para PRÉ-VISUALIZAÇÃO:", type=['png', 'jpg', 'jpeg'], key='temp_file_uploader')
        
        if uploaded_file is not None:
            st.image(uploaded_file, caption=f"Pré-visualização: {uploaded_file.name}", width=250)
            st.info("Lembre-se: Você precisa salvar o link de acesso no campo 7 para persistência.")
        
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
            "OBSERVACOES": observacoes,
            "URL_IMAGEM": anexo_url # Novo Campo
        }
        
        with st.spinner(f"Salvando rotina no Sheets na aba {selected_setor}..."):
            if append_new_rotina(data_to_save, selected_setor):
                load_all_rotinas_from_drive.clear()
                st.success(f"Rotina '{titulo}' salva com sucesso!")
            else:
                st.warning("Falha ao salvar. Verifique logs ou credenciais.")

def edit_rotina_tab(df_rotinas):
    """Lógica da Sub-Aba para Edição/Exclusão de Rotinas Existentes (Update/Delete)"""
    # ... (código de seleção de rotina inalterado) ...
    rotina_tuples = [(f"{row['TITULO_PROCEDIMENTO']} ({row['SETOR']})", row['TITULO_PROCEDIMENTO']) 
                     for index, row in df_rotinas.iterrows()]
    display_options = ["— Selecione uma Rotina —"] + [t[0] for t in rotina_tuples]
    selected_display_option = st.selectbox("Selecione a Rotina para Editar/Excluir:", options=display_options, key='edit_selectbox')
    
    if selected_display_option == "— Selecione uma Rotina —": return
    
    selected_title = selected_display_option.split(' (')[0]
    current_data = df_rotinas[df_rotinas['TITULO_PROCEDIMENTO'] == selected_title].iloc[0]
    sheet_name = current_data['SETOR']
    initial_acoes = current_data['ACOES'].replace('#', '\n') if isinstance(current_data['ACOES'], str) else ""
    initial_anexo_url = current_data.get('URL_IMAGEM', '') # Obtém o valor, ou vazio se a coluna não existir
    
    with st.form(key='edit_rotina_form'):
        # ... (Campos Título, ID, Fluxo, Ações, Observações inalterados) ...
        
        # Campo de URL para a imagem na edição
        anexo_url = st.text_input("URL do Anexo (Link direto):", value=initial_anexo_url, key='edit_anexo_url')
        
        # Uploader para pré-visualização
        uploaded_file = st.file_uploader("Upload de Imagem para PRÉ-VISUALIZAÇÃO:", type=['png', 'jpg', 'jpeg'], key='temp_file_uploader_edit')
        
        if uploaded_file is not None:
            st.image(uploaded_file, caption=f"Pré-visualização: {uploaded_file.name}", width=250)
            st.info("Lembre-se: Você precisa salvar o link de acesso no campo de URL!")
            
        # ... (Botões de Ação - UPDATE e DELETE - inalterados) ...

    # 4. LÓGICA DE SALVAMENTO (UPDATE)
    if submit_update:
        # ... (verificações inalteradas) ...
            
        data_to_update = {
            # ... (demais campos)
            "ACOES": acoes.replace('\n', '#'),
            "OBSERVACOES": observacoes,
            "URL_IMAGEM": anexo_url # <-- Salva o link atualizado
        }
        
        # ... (lógica de chamada update_rotina inalterada) ...

    # 5. LÓGICA DE EXCLUSÃO (DELETE)
    # ... (código inalterado) ...

def login_screen():
    # ... (código inalterado) ...
    try:
        ADMIN_PASSWORD = st.secrets["auth"]["admin_password"]
    except KeyError:
        st.error("ERRO DE CONFIGURAÇÃO: Chave 'admin_password' não encontrada no arquivo secrets.toml.")
        return False
        
    st.header("🔑 Acesso Administrativo")
    with st.form("login_form"):
        password = st.text_input("Senha de Administrador:", type="password")
        submit_button = st.form_submit_button("Entrar")

    if submit_button:
        if password == ADMIN_PASSWORD:
            st.session_state['logged_in'] = True
            st.success("Acesso concedido!")
            st.rerun() 
        else:
            st.error("Senha incorreta. Acesso Negado.")
            st.session_state['logged_in'] = False
            
    return st.session_state.get('logged_in', False)

def admin_view(df_rotinas, setor_options):
    # ... (código inalterado) ...
    st.header("🛠️ Gerenciamento de Rotinas")
    st.success("🔒 Área protegida: Logado como Administrador.")
    
    tab1, tab2 = st.tabs(["➕ Criar Nova Rotina", "✏️ Alterar/Excluir Rotina Existente"])
    
    with tab1: create_rotina_tab(setor_options)
    with tab2: edit_rotina_tab(df_rotinas) 

def admin_controller(df_rotinas, setor_options):
    if st.session_state.get('logged_in', False):
        admin_view(df_rotinas, setor_options)
    else:
        login_screen()

# --- FUNÇÃO PRINCIPAL (Estrutura da Aplicação) ---

def main():
    st.set_page_config(page_title="SGC Hospitalar - Rotinas", layout="wide")
    st.title("🏥 Sistema de Gerenciamento de Conhecimento Hospitalar (SGC)")

    # ... (Lógica Global de Atualização inalterada) ...
    col_refresh, col_title_info = st.columns([1, 4])
    with col_refresh:
        if st.button("🔄 Atualizar Dados Agora"):
            load_all_rotinas_from_drive.clear()
            st.rerun()
    col_title_info.info("A página é atualizada automaticamente.")
    st.markdown("---")

    # --- Carregamento de Dados ---
    with st.spinner('Buscando e carregando dados do SGC Hospitalar...'):
        df_rotinas = load_all_rotinas_from_drive()

    if df_rotinas.empty:
        # Se falhar o carregamento, exibe o erro da função load_all_rotinas_from_drive e para
        return
        
    setor_options = sorted(df_rotinas['SETOR'].unique().tolist())
    
    # --- SELEÇÃO DE PÁGINA na Sidebar ---
    st.sidebar.header("Módulos")
    PAGES_OPTIONS = ["🔍 Visualização de Rotinas", "🛠️ Gerenciamento de Dados"]
    selection = st.sidebar.radio("Ir para:", PAGES_OPTIONS)
    
    # Chama a função correta
    if selection == "🛠️ Gerenciamento de Dados":
        admin_controller(df_rotinas, setor_options)
    else:
        main_view(df_rotinas, setor_options)

if __name__ == '__main__':
    main()
