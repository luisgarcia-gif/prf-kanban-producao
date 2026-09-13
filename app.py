import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Kanban Produção - PRF", 
    page_icon="🏗️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# PALETA DE CORES PRF
PRF_TURQUOISE = "#0097A7"

# ==========================================
# 2. LIGAÇÃO À BASE DE DADOS (SUPABASE)
# ==========================================
SUPABASE_URL = "https://hybquplraoiarwfwxiwn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5YnF1cGxyYW9pYXJ3Znd4aXduIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkzMDYwMDgsImV4cCI6MjEwNDg4MjAwOH0.1EFqdshaIQJU96rMr8ep9ED6HAkAmmrfz_dTxGN4Hi8"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_connection()

# Funções de Base de Dados
def obter_cartoes():
    resposta = supabase.table("cartoes_kanban").select("*").order("data_criacao", desc=True).execute()
    return resposta.data

def criar_cartao(referencia):
    supabase.table("cartoes_kanban").insert({"referencia": referencia}).execute()

def atualizar_fase(card_id, nova_fase):
    supabase.table("cartoes_kanban").update({"fase": nova_fase}).eq("id", card_id).execute()

# ==========================================
# 3. BARRA LATERAL (NOVA OBRA)
# ==========================================
with st.sidebar:
    st.markdown(f"""
        <div style="background-color:{PRF_TURQUOISE}; padding:15px; border-radius:10px; text-align:center;">
            <span style="color:white; font-size:28px; font-weight:bold; letter-spacing:2px;">PRF</span><br>
            <span style="color:white; font-size:10px;">PRODUÇÃO KANBAN</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("➕ Adicionar Obra")
    
    nova_ref = st.text_input("Referência / Conjunto (ex: HY25003)")
    
    if st.button("Criar Cartão", use_container_width=True):
        if nova_ref:
            criar_cartao(nova_ref)
            st.success(f"Obra {nova_ref} adicionada!")
            st.rerun()
        else:
            st.warning("Insere uma referência válida.")

# ==========================================
# 4. QUADRO KANBAN (INTERFACE PRINCIPAL)
# ==========================================
st.title("📊 Quadro Kanban de Produção")

fases = ['Projeto', 'Desenho', 'Material', 'Produção', 'Qualidade', 'Tratamento', 'Concluído']
colunas_ui = st.columns(len(fases))

dados = obter_cartoes()
df_cartoes = pd.DataFrame(dados)

st.markdown("""
<style>
    div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        border-left: 5px solid #0097A7;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

for i, fase in enumerate(fases):
    with colunas_ui[i]:
        st.markdown(f"<h5 style='text-align: center; color: #006064;'>{fase}</h5>", unsafe_allow_html=True)
        st.markdown("---")
        
        if not df_cartoes.empty and 'fase' in df_cartoes.columns:
            cartoes_nesta_fase = df_cartoes[df_cartoes['fase'] == fase]
            
            for index, cartao in cartoes_nesta_fase.iterrows():
                with st.container():
                    st.markdown(f"**📦 {cartao['referencia']}**")
                    st.caption(f"👷 {cartao['trabalhador']}")
                    
                    nova_fase = st.selectbox(
                        "Mover", 
                        fases, 
                        index=fases.index(fase), 
                        key=f"move_{cartao['id']}",
                        label_visibility="collapsed"
                    )
                    
                    if nova_fase != fase:
                        atualizar_fase(cartao['id'], nova_fase)
                        st.rerun()
