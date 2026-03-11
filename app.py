import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import io

# --- CONFIGURAÇÃO DA PÁGINA E ESTILO CSS (DASHBOARD DARK OPS) ---
st.set_page_config(layout="wide", page_title="OPS - Painel de Alvos")

st.markdown("""
    <style>
    /* Fundo principal */
    .stApp { background-color: #05080d; color: white; }
    
    /* Barra lateral */
    [data-testid="stSidebar"] { background-color: #0b111b; border-right: 1px solid #1e293b; }
    
    /* Card de Operação e Alvos */
    .op-card {
        background-color: #0b111b;
        border: 1px solid #1e293b;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    
    /* Botões */
    .stButton>button {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
    }
    
    /* Inputs */
    input, textarea, select {
        background-color: #161e2c !important;
        color: white !important;
        border: 1px solid #374151 !important;
    }

    /* Badge H-HORA */
    .badge-hora {
        background-color: #2e1a05;
        color: #f59e0b;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO BANCO DE DADOS (MEMÓRIA) ---
if 'alvos' not in st.session_state:
    st.session_state.alvos = []
if 'view' not in st.session_state:
    st.session_state.view = 'painel' # Alterna entre 'painel' e 'cadastro'

# --- FUNÇÕES DE NAVEGAÇÃO ---
def ir_para_cadastro(): st.session_state.view = 'cadastro'
def ir_para_painel(): st.session_state.view = 'painel'

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.markdown("<h2 style='color:#2563eb;'>T OPS</h2>", unsafe_allow_html=True)
    st.button("🎯 Painel de Alvos", on_click=ir_para_painel)
    st.button("📄 Dossie Digital")
    st.divider()
    st.button("🔒 Segurança")

# --- TELA 1: PAINEL DE ALVOS (DASHBOARD) ---
if st.session_state.view == 'painel':
    col_t1, col_t2 = st.columns([4, 1])
    with col_t1:
        st.markdown("<h1>OPERAÇÃO <span style='color:#2563eb;'>CERBERUS</span></h1>", unsafe_allow_html=True)
        st.markdown("<p><span style='background:#1e293b; padding:5px 10px; border-radius:10px;'>📍 DIG DISE</span> <span class='badge-hora'>H-HORA: 06:00</span></p>", unsafe_allow_html=True)
    with col_t2:
        st.button("➕ NOVO ALVO", on_click=ir_para_cadastro)

    st.divider()

    if not st.session_state.alvos:
        st.markdown("""
            <div style='text-align:center; padding:100px; color:#475569;'>
                <div style='font-size:50px;'>🎯</div>
                <p>NENHUM ALVO CADASTRADO</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        for i, alvo in enumerate(st.session_state.alvos):
            with st.container():
                st.markdown(f"""
                <div class="op-card">
                    <div style="display:flex; justify-content:space-between;">
                        <div>
                            <h3 style="margin:0; color:#3b82f6;">{alvo['nome'].upper()}</h3>
                            <p style="color:#94a3b8;">VULGO: {alvo['vulgo'].upper()} | {len(alvo['enderecos'])} ENDEREÇO(S)</p>
                        </div>
                        <div style="color:#10b981; font-weight:bold;">CADASTRADO</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- TELA 2: NOVO ALVO TÁTICO (FORMULÁRIO IGUAL À FOTO) ---
elif st.session_state.view == 'cadastro':
    st.markdown("<h2>🎯 NOVO ALVO TÁTICO</h2>", unsafe_allow_html=True)
    
    with st.form("form_alvo"):
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("### 👤 QUALIFICAÇÃO DO OBJETIVO")
            nome = st.text_input("Nome Completo")
            vulgo = st.text_input("Vulgo / Apelido")
            mandado = st.selectbox("Mandado", ["Busca e Apreensão", "Prisão Preventiva", "Temporária"])
            foto_alvo = st.file_uploader("RETRATO DO ALVO (ANEXAR)", type=['jpg','png'])

        with c2:
            st.markdown("### 👥 COMPOSIÇÃO DA EQUIPE")
            responsavel = st.text_input("Responsável / Delegado / Agente")
            equipe = st.text_area("Policiais na Equipe (Um por linha)")
            st.markdown("### 📝 OBSERVAÇÕES E PONTOS CRÍTICOS")
            obs = st.text_area("Descreva observações táticas e riscos...", height=150)

        st.divider()
        st.markdown("### 📍 ENDEREÇOS DE CUMPRIMENTO")
        st.info("Para este sistema, cadastre os endereços abaixo. O PDF gerará uma página para cada.")
        
        # Lógica de endereços dentro do formulário (usamos área de texto para simplificar múltiplos no st.form)
        enderecos_raw = st.text_area("Insira os endereços (Separe cada endereço por uma LINHA NOVA)")
        foto_local = st.file_uploader("LOCAL DA FACHADA (ANEXAR FOTO DO PRIMEIRO LOCAL)", type=['jpg','png'])

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            if st.form_submit_button("CANCELAR"): ir_para_painel()
        with col_f2:
            submit = st.form_submit_button("SALVAR ALVO")
            
            if submit:
                lista_ends = [{"rua": e.strip(), "foto": foto_local} for e in enderecos_raw.split('\n') if e.strip()]
                novo_alvo = {
                    "nome": nome,
                    "vulgo": vulgo,
                    "mandado": mandado,
                    "responsavel": responsavel,
                    "equipe": equipe,
                    "obs": obs,
                    "enderecos": lista_ends,
                    "foto_alvo": foto_alvo
                }
                st.session_state.alvos.append(novo_alvo)
                st.success("Alvo salvo com sucesso!")
                # Aqui você pode chamar a função de PDF se quiser baixar na hora
                ir_para_painel()
                st.rerun()

# --- FUNÇÃO DO PDF (PARA QUANDO PRECISAR GERAR) ---
# (A lógica do PDF permanece a mesma que te enviei antes, focada em criar uma página por endereço)
