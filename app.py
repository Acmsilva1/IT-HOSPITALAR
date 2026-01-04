import streamlit as st
import pandas as pd
# Importa as duas funções do data_loader
from data_loader import load_all_rotinas_from_drive, append_new_rotina 

# --- FUNÇÕES DE PÁGINA ---

def main_view(df_rotinas, setor_options):
    """Lógica da Página de Visualização de Rotinas (Código Original)"""
    st.header("🔍 Visualização de Rotinas do SGC Hospitalar")
    
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


def admin_view(setor_options):
    """NOVA Lógica da Página de Gerenciamento de Dados (Formulário)"""
    st.header("🛠️ Gerenciamento de Rotinas (Criação de Processos)")
    
    st.warning("🚨 Esta página será protegida por senha na próxima etapa de governança.")
    st.info("Preencha o formulário abaixo para adicionar uma nova rotina diretamente no Google Sheets. O novo processo aparecerá na visualização após salvar.")
    
    st.subheader("Adicionar Nova Rotina")
    
    # Criação do Formulário
    with st.form(key='rotina_form'):
        
        # CAMPO 1: Setor (Determina a ABA de destino no Sheets)
        selected_setor = st.selectbox(
            "1. Setor de Destino (Aba na Planilha):", 
            options=["— Selecione um Setor —"] + setor_options, 
            key='setor_input'
        )
        
        st.markdown("---")
        
        # CAMPO 2 e 3: Título e ID (Colunas 'TITULO_PROCEDIMENTO' e 'ID_DA_ROTINA')
        col1, col2 = st.columns(2)
        with col1:
            titulo = st.text_input("2. Título do Procedimento (TITULO_PROCEDIMENTO):", key='titulo_input')
        with col2:
            id_rotina = st.text_input("3. ID da Rotina (ID_DA_ROTINA, Ex: CC-001):", key='id_input')
            
        # CAMPO 4: Fluxo Principal (Coluna 'FLUXO_PRINCIPAL')
        fluxo_principal = st.text_input("4. Fluxo Principal (FLUXO_PRINCIPAL, Ex: TASY > [Menu] > [Submenu]):", key='fluxo_input')
        
        # CAMPO 5: Ações/Passos (Coluna 'ACOES' - Usa '\n' para ser convertido em '#')
        acoes = st.text_area(
            "5. Ações/Passo a Passo (ACOES) - Separe cada passo com uma quebra de linha!:", 
            key='acoes_input',
            height=200
        )
        
        # CAMPO 6: Observações (Coluna 'OBSERVACOES')
        observacoes = st.text_area("6. Observações (OBSERVACOES - Avisos, Dicas, etc.):", key='obs_input')
        
        # Botão de Envio
        submit_button = st.form_submit_button(label='💾 Salvar Nova Rotina no Sheets')

    # Lógica de Envio
    if submit_button:
        # Checagem mínima
        if not titulo or not acoes or selected_setor == "— Selecione um Setor —":
            st.error("🚨 Preencha o Título, as Ações/Passos e selecione um Setor de destino.")
            return

        # Prepara os dados. CHAVES DEVEM BATER COM OS CABEÇALHOS DA PLANILHA!
        data_to_save = {
            "ID_DA_ROTINA": id_rotina,
            "TITULO_PROCEDIMENTO": titulo,
            "FLUXO_PRINCIPAL": fluxo_principal,
            "ACOES": acoes.replace('\n', '#'), # Converte quebras de linha para o separador '#'
            "OBSERVACOES": observacoes
        }
        
        # Chama a função de escrita, usando o setor selecionado como nome da aba
        with st.spinner(f"Salvando rotina no Sheets na aba {selected_setor}..."):
            if append_new_rotina(data_to_save, selected_setor):
                # Limpa o cache para garantir que a visualização de rotinas veja a nova linha imediatamente
                load_all_rotinas_from_drive.clear()
                st.success(f"Rotina '{titulo}' salva com sucesso! Pressione 'Atualizar Dados Agora' ou F5 na visualização para ver a mudança.")
                # Opcional: st.rerun() aqui forçaria a visualização imediata, mas é melhor forçar o usuário a usar o botão, por enquanto.
            else:
                st.warning("Falha ao salvar. Verifique logs ou credenciais.")

# --- FUNÇÃO PRINCIPAL ---

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
    
    # --- SELEÇÃO DE PÁGINA na Sidebar (para o Admin) ---
    st.sidebar.header("Módulos")
    
    PAGES = {
        "🔍 Visualização de Rotinas": lambda: main_view(df_rotinas, setor_options),
        "🛠️ Gerenciamento de Dados": lambda: admin_view(setor_options) # Novo módulo
    }
    
    selection = st.sidebar.radio("Ir para:", list(PAGES.keys()))
    
    # Executa a função da página selecionada
    PAGES[selection]()

if __name__ == '__main__':
    main()
