import streamlit as st
import pandas as pd
# Importe todas as funções de data_loader
from data_loader import load_all_rotinas_from_drive, append_new_rotina, update_rotina, delete_rotina 
# ... (outros imports) ...

# --- FUNÇÕES DE PÁGINA: main_view, create_rotina_tab, edit_rotina_tab (Inalteradas) ---
# ... (Mantenha as funções de visualização e CRUD aqui) ...

# --- NOVA FUNÇÃO: Tela de Login e Autenticação ---

def login_screen():
    """Mostra a tela de login e verifica a senha."""
    
    # Busca a senha segura nos secrets
    try:
        ADMIN_PASSWORD = st.secrets["auth"]["admin_password"]
    except KeyError:
        st.error("ERRO DE CONFIGURAÇÃO: Chave 'admin_password' não encontrada nos secrets.")
        # Se não encontrar a chave, não permite acesso
        return False
        
    st.header("🔑 Acesso Administrativo")
    st.info("Esta área exige autenticação para gerenciar (Criar, Alterar, Excluir) rotinas hospitalares.")
    
    with st.form("login_form"):
        password = st.text_input("Senha de Administrador:", type="password")
        submit_button = st.form_submit_button("Entrar")

    if submit_button:
        # Lembrete de governança: Sempre use comparações seguras para senhas em produção!
        if password == ADMIN_PASSWORD:
            st.session_state['logged_in'] = True
            st.success("Acesso concedido! Bem-vindo(a) ao Gerenciamento de Dados.")
            st.rerun() # Força o Streamlit a recarregar a página e ir para o conteúdo
        else:
            st.error("Senha incorreta. Acesso Negado.")
            st.session_state['logged_in'] = False
            
    return st.session_state.get('logged_in', False)


def admin_view(df_rotinas, setor_options):
    """Função Principal do Módulo de Gerenciamento (Tabs)"""
    # Esta função só será chamada SE o login for bem-sucedido
    st.header("🛠️ Gerenciamento de Rotinas (Criação e Edição/Exclusão)")
    st.success("🔒 Área protegida: Logado como Administrador.")
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

    # ... (Lógica de Atualização e Carregamento de Dados inalterada) ...

    # --- SELEÇÃO DE PÁGINA na Sidebar ---
    st.sidebar.header("Módulos")
    
    PAGES = {
        "🔍 Visualização de Rotinas": main_view,
        # O Gerenciamento agora aponta para uma função Lambda que verifica o login
        "🛠️ Gerenciamento de Dados": lambda: admin_controller(df_rotinas, setor_options)
    }
    
    selection = st.sidebar.radio("Ir para:", list(PAGES.keys()))
    
    # Nova função de controle que verifica o login antes de mostrar o conteúdo
    if selection == "🛠️ Gerenciamento de Dados":
        admin_controller(df_rotinas, setor_options)
    else:
        main_view(df_rotinas, setor_options) # Use a main_view diretamente para o modo de leitura

def admin_controller(df_rotinas, setor_options):
    """Controla o acesso à área de administração."""
    if st.session_state.get('logged_in', False):
        admin_view(df_rotinas, setor_options)
    else:
        login_screen()

if __name__ == '__main__':
    main()
