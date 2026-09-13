import streamlit as st
import pandas as pd
from supabase import create_client, Client

st.set_page_config(page_title="Kanban Produção - PRF", page_icon="🏗️", layout="wide")

PRF_TURQUOISE = "#0097A7"

# ==========================================
# LIGAÇÃO À BASE DE DADOS
# ==========================================
SUPABASE_URL = "https://hybquplraoiarwfwxiwn.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh5YnF1cGxyYW9pYXJ3Znd4aXduIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkzMDYwMDgsImV4cCI6MjEwNDg4MjAwOH0.1EFqdshaIQJU96rMr8ep9ED6HAkAmmrfz_dTxGN4Hi8"

@st.cache_resource
def init_connection():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase: Client = init_connection()

def obter_cartoes():
    resposta = supabase.table("cartoes_kanban").select("*").order("data_criacao", desc=True).execute()
    return resposta.data

def criar_cartao(referencia, tipo):
    supabase.table("cartoes_kanban").insert({"referencia": referencia, "tipo": tipo}).execute()

def atualizar_fase(card_id, nova_fase):
    supabase.table("cartoes_kanban").update({"fase": nova_fase}).eq("id", card_id).execute()

def atualizar_trabalhador(card_id, novo_trabalhador):
    supabase.table("cartoes_kanban").update({"trabalhador": novo_trabalhador}).eq("id", card_id).execute()

# ==========================================
# BARRA LATERAL
# ==========================================
with st.sidebar:
    st.markdown(f"""
        <div style="background-color:{PRF_TURQUOISE}; padding:15px; border-radius:10px; text-align:center; margin-bottom:20px;">
            <span style="color:white; font-size:28px; font-weight:bold; letter-spacing:2px;">PRF</span><br>
            <span style="color:white; font-size:10px;">PRODUÇÃO KANBAN</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.subheader("➕ Adicionar Obra")
    
    nova_ref = st.text_input("Referência / Conjunto (ex: HY25003)")
    tipo_obra = st.selectbox("Tipo de Obra", ["Normal", "Urgente", "Retrabalho", "Ferramental"])
    
    if st.button("Criar Cartão", use_container_width=True):
        if nova_ref:
            criar_cartao(nova_ref, tipo_obra)
            st.success(f"Obra adicionada!")
            st.rerun()
        else:
            st.warning("Insere uma referência válida.")

# ==========================================
# QUADRO KANBAN
# ==========================================
st.title("📊 Quadro Kanban de Produção")
st.markdown("---")

fases = ['Projeto', 'Desenho', 'Material', 'Produção', 'Qualidade', 'Tratamento', 'Concluído']
colunas_ui = st.columns(len(fases))

dados = obter_cartoes()
df_cartoes = pd.DataFrame(dados)

# Dicionário de Cores baseado no teu exemplo
cores_tipo = {
    "Normal": {"header": "#4A7A8C", "bg": "#DCE8EC"},      # Azul esverdeado
    "Urgente": {"header": "#A83636", "bg": "#F5D5D5"},     # Vermelho
    "Retrabalho": {"header": "#D99536", "bg": "#FCEBD4"},  # Amarelo/Laranja
    "Ferramental": {"header": "#5C955C", "bg": "#DFF0DF"}, # Verde
}

lista_operadores = [
    "Não Atribuído", "Tubista - Suellen", "Tubista - José", 
    "Serralheiro - Junior", "Soldador - Alexandre", 
    "Soldador - Jorge", "Máquina - Orbital"
]

for i, fase in enumerate(fases):
    with colunas_ui[i]:
        # Título da coluna mais limpo
        st.markdown(f"<div style='text-align: center; font-weight: bold; color: #555; background-color: #f0f0f0; padding: 5px; border-radius: 5px; margin-bottom: 15px;'>{fase.upper()}</div>", unsafe_allow_html=True)
        
        if not df_cartoes.empty and 'fase' in df_cartoes.columns:
            cartoes_nesta_fase = df_cartoes[df_cartoes['fase'] == fase]
            
            for index, cartao in cartoes_nesta_fase.iterrows():
                tipo = cartao.get('tipo', 'Normal')
                if tipo not in cores_tipo: tipo = 'Normal'
                
                c_head = cores_tipo[tipo]['header']
                c_bg = cores_tipo[tipo]['bg']
                
                # Gera as iniciais do trabalhador para o Avatar
                trab_nome = str(cartao['trabalhador'])
                iniciais = trab_nome.split('-')[-1].strip()[0:2].upper() if '-' in trab_nome else "NA"
                
                # DESIGN DO CARTÃO (HTML/CSS)
                html_cartao = f"""
                <div style="background-color: {c_bg}; border: 1px solid #ccc; border-radius: 6px; overflow: hidden; box-shadow: 0 3px 6px rgba(0,0,0,0.15); margin-bottom: 10px;">
                    <!-- Cabeçalho Colorido -->
                    <div style="background-color: {c_head}; color: white; padding: 4px 8px; font-size: 11px; font-weight: bold; display: flex; justify-content: space-between; align-items: center;">
                        <span>{tipo.upper()}</span>
                        <!-- Avatar Redondo -->
                        <span style="background-color: #f1f1f1; color: {c_head}; border-radius: 50%; width: 22px; height: 22px; display: inline-flex; justify-content: center; align-items: center; font-size: 10px; font-weight: 900; border: 1px solid white;">{iniciais}</span>
                    </div>
                    
                    <!-- Corpo do Cartão -->
                    <div style="padding: 12px 10px;">
                        <div style="font-size: 14px; font-weight: 800; color: #333; margin-bottom: 5px;">{cartao['referencia']}</div>
                        <div style="font-size: 11px; color: #555;">Resp: <b>{cartao['trabalhador']}</b></div>
                    </div>
                    
                    <!-- Rodapé com Ícones -->
                    <div style="background-color: rgba(255,255,255,0.5); padding: 4px 8px; border-top: 1px solid #ddd; font-size: 12px; display: flex; gap: 10px; color: #555;">
                        <span title="Tempo Gasto">⏱️ {cartao.get('tempo_gasto_minutos', 0)}m</span>
                        <span title="Fase Atual">🏷️ {fase}</span>
                    </div>
                </div>
                """
                
                with st.container():
                    # Renderiza o visual
                    st.markdown(html_cartao, unsafe_allow_html=True)
                    
                    # Funcionalidades abaixo do visual do cartão
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        nova_fase = st.selectbox("Mover:", fases, index=fases.index(fase), key=f"mv_{cartao['id']}", label_visibility="collapsed")
                        if nova_fase != fase:
                            atualizar_fase(cartao['id'], nova_fase)
                            st.rerun()
                            
                    if fase == "Produção":
                        with st.expander("👤 Atribuir"):
                            try: idx_atual = lista_operadores.index(cartao['trabalhador'])
                            except: idx_atual = 0
                            novo_trab = st.selectbox("Operador:", lista_operadores, index=idx_atual, key=f"tr_{cartao['id']}")
                            if novo_trab != cartao['trabalhador']:
                                atualizar_trabalhador(cartao['id'], novo_trab)
                                st.rerun()
                    st.write("") # Espaço final do cartão
