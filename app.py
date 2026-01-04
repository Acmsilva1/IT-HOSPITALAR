import streamlit as st
import pandas as pd
# Importa todas as funções de data_loader
from data_loader import load_all_rotinas_from_drive, append_new_rotina, update_rotina, delete_rotina 

# ... (Mantenha as funções main_view, create_rotina_tab, edit_rotina_tab, login_screen, etc.
# definidas no escopo global, antes da função main()) ...


# ----------------------------------------------------------------------
# FUNÇÕES ATUALIZADAS (APENAS AS PARTES ALTERADAS)
# ----------------------------------------------------------------------

# --- FUNÇÃO ATUALIZADA: main_view (Para EXIBIR a imagem) ---

def main_view(df_rotinas, setor_options):
    """Lógica da Página de Visualização de Rotinas (Read)"""
    # ... (código de navegação e filtros inalterado) ...
    
    # ... (Dentro do loop "for index, row in df_filtered.iterrows():") ...
    
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

            # --- NOVO BLOCO: Exibição da Imagem (Sem poluir a tela) ---
            image_url = row.get('URL_IMAGEM')
            if image_url and str(image_url).strip():
                # O expander esconde a imagem até o clique, mantendo a tela limpa
                with st.expander("🖼️ Clique para visualizar o Anexo/Fluxograma"):
                    # Exibe a imagem com um tamanho moderado (400px)
                    st.image(str(image_url), caption=f"Anexo para: {row['TITULO_PROCEDIMENTO']}", width=400)
            # --- FIM NOVO BLOCO ---
            
            st.markdown("#### 🚀 Passo a Passo Objetivo:")
            
            for i, passo in enumerate(acoes_list):
                 if passo and passo.strip():
                    st.markdown(f"*{i+1}.* **{passo.strip()}**")
            
            st.markdown("---") 
    else:
        st.warning("Nenhuma rotina encontrada com os filtros selecionados.")
        
# --- FUNÇÃO ATUALIZADA: create_rotina_tab (Para Adicionar a imagem/URL) ---

def create_rotina_tab(setor_options):
    """Lógica da Sub-Aba para Criação de Novas Rotinas (Create)"""
    st.subheader("Adicionar Nova Rotina")
    st.info("Preencha o formulário para adicionar uma nova rotina diretamente no Google Sheets.")
    
    with st.form(key='rotina_form'):
        
        # ... (Campos de 1 a 5 - Setor, Título, Ações - inalterados) ...
        selected_setor = st.selectbox(
            "1. Setor de Destino (Aba na Planilha):", 
            options=["— Selecione um Setor —"] + setor_options, 
            key='create_setor_input'
        )
        # ... (Resto do Formulário inalterado) ...
        
        observacoes = st.text_area("6. Observações (OBSERVACOES - Avisos, Dicas, etc.):", key='create_obs_input')
        
        st.markdown("---")
        st.markdown("#### 🖼️ Anexo Visual (Imagem)")

        # 7. CAMPO PARA SALVAR A URL (LINK PERSISTENTE)
        anexo_url = st.text_input(
            "7. URL da Imagem/Fluxograma (Link Direto):", 
            key='create_anexo_url',
            help="Cole o link direto da imagem aqui (salva no Drive/GitHub, etc.). Esta URL será salva na planilha."
        )

        # 8. BOTÃO DE UPLOAD (Apenas para pré-visualização no momento do cadastro)
        uploaded_file = st.file_uploader(
            "Upload de Imagem para PRÉ-VISUALIZAÇÃO (PNG, JPG):",
            type=['png', 'jpg', 'jpeg'],
            key='temp_file_uploader'
        )
        
        if uploaded_file is not None:
            st.image(uploaded_file, caption=f"Pré-visualização: {uploaded_file.name}", width=250)
            st.info("Lembre-se: O arquivo foi carregado, mas você precisa salvar o link de acesso no campo 7!")
        
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
            "URL_IMAGEM": anexo_url # <-- NOVO CAMPO: Se vazio, salvará vazio.
        }
        
        with st.spinner(f"Salvando rotina no Sheets na aba {selected_setor}..."):
            if append_new_rotina(data_to_save, selected_setor):
                load_all_rotinas_from_drive.clear()
                st.success(f"Rotina '{titulo}' salva com sucesso! Pressione 'Atualizar Dados Agora' na Visualização para ver a mudança.")
            else:
                st.warning("Falha ao salvar. Verifique logs ou credenciais.")

# ... (Mantenha as demais funções e a função main() inalteradas, ou use o código completo
# da resposta anterior para a estrutura geral.)
