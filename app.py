import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import io
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL (ESTILO DASHBOARD DARK OPS) ---
st.set_page_config(layout="wide", page_title="SISTEMA OPS - TÁTICO")

st.markdown("""
    <style>
    .stApp { background-color: #050a14; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0b1424; border-right: 2px solid #1e3a8a; }
    
    /* Títulos e Labels */
    h1, h2, h3 { font-family: 'Inter', sans-serif; color: white !important; font-style: italic; }
    label { color: #3b82f6 !important; font-weight: bold !important; font-size: 14px !important; }
    
    /* Cards do Painel Principal */
    .op-header { background-color: #0b111b; border: 1px solid #1e293b; padding: 25px; border-radius: 20px; margin-bottom: 25px; }
    .alvo-card { background-color: #0f172a; border-left: 5px solid #2563eb; padding: 20px; border-radius: 15px; margin-bottom: 15px; }
    
    /* Botões */
    .stButton>button { background-color: #2563eb !important; color: white !important; font-weight: bold !important; border-radius: 8px !important; border: none !important; transition: 0.3s; }
    .stButton>button:hover { background-color: #1d4ed8 !important; transform: scale(1.02); }
    
    /* Badges */
    .badge-hora { background-color: #2e1a05; color: #f59e0b; padding: 4px 12px; border-radius: 20px; font-weight: bold; border: 1px solid #f59e0b; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADOS (BANCO DE DADOS TEMPORÁRIO) ---
if 'alvos' not in st.session_state: st.session_state.alvos = []
if 'missao' not in st.session_state: 
    st.session_state.missao = {
        'nome': 'Operação', 'unidade': 'Delegacia do Município', 
        'ponto': 'Rua Antonio Freitas', 'data_br': '04/03/2026 05:30', 
        'h_hora': '04/03/2026 06:00', 'resumo': ''
    }
if 'view' not in st.session_state: st.session_state.view = 'painel'

# --- CLASSE DO PDF (ESTRUTURA ORIGINAL SOLICITADA) ---
class BriefingPDF(FPDF):
    def header_op(self, missao):
        self.set_fill_color(0, 0, 0)
        self.rect(10, 10, 190, 8, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", 'B', 8)
        self.cell(190, 8, "S I G I L O S O   -   D O C U M E N T O   D E   I N T E L I G Ê N C I A   -   R E S T R I T O", 0, 1, 'C')
        self.set_text_color(0, 0, 0)
        self.ln(2)
        self.set_font("Arial", 'B', 22)
        self.cell(140, 10, missao['nome'].upper(), 0, 0)
        self.set_xy(160, 20); self.cell(40, 12, missao['unidade'].upper(), 1, 1, 'C')
        self.set_xy(10, 42); self.set_font("Arial", 'B', 6)
        self.cell(60, 12, f"PONTO DE ENCONTRO: {missao['ponto'].upper()}", 1)
        self.cell(50, 12, f"BRIEFING: {missao['data_br']}", 1)
        self.cell(40, 12, f"H-HORA: {missao['h_hora']}", 1)
        self.cell(40, 12, f"ID MISSÃO: #{id(missao)%100000}", 1)

    def draw_footer_fiel(self):
        self.set_xy(10, 205); self.set_font("Arial", 'B', 8)
        self.cell(190, 8, "RELATÓRIO DE OCORRÊNCIA E APREENSÕES DE CAMPO", 'T', 1, 'C')
        for _ in range(4): self.cell(190, 6, "_"*110, 0, 1)
        self.ln(5); self.set_font("Arial", 'B', 7)
        self.cell(60, 5, "CHECKLIST DE DISPOSITIVOS (IMEI/SN)", 0, 1)
        for _ in range(3): self.cell(100, 5, "_"*60, 0, 1)

# --- NAVEGAÇÃO ---
def ir_para(view): st.session_state.view = view

# --- TELA 1: PAINEL PRINCIPAL (DASHBOARD) ---
if st.session_state.view == 'painel':
    st.markdown('<div class="op-header">', unsafe_allow_html=True)
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown(f"<h1>{st.session_state.missao['nome'].upper()} <span style='cursor:pointer;' onclick='ir_para(\"edit_missao\")'>✏️</span></h1>", unsafe_allow_html=True)
        st.markdown(f"📍 {st.session_state.missao['ponto']} | <span class='badge-hora'>H-HORA: {st.session_state.missao['h_hora']}</span>", unsafe_allow_html=True)
    with c2:
        if st.button("➕ NOVO ALVO"): ir_para('novo_alvo')
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✏️ EDITAR DADOS DA OPERAÇÃO"): ir_para('edit_missao')

    st.divider()
    
    # LISTA DE ALVOS CADASTRADOS
    if not st.session_state.alvos:
        st.info("Nenhum alvo cadastrado no painel operacional.")
    else:
        for idx, alvo in enumerate(st.session_state.alvos):
            with st.container():
                st.markdown(f"""<div class='alvo-card'>
                <h2 style='margin:0;'>{alvo['nome'].upper()}</h2>
                <p><b>Mandado:</b> {alvo['tipo']} | <b>VTR:</b> {alvo['viatura']}</p>
                <p style='color:#94a3b8;'>Integrantes: {', '.join(alvo['equipe'])}</p>
                </div>""", unsafe_allow_html=True)

    if st.session_state.alvos:
        st.divider()
        if st.button("🚀 GERAR PDF DE TODOS OS ALVOS"):
            pdf = BriefingPDF()
            for alvo in st.session_state.alvos:
                for ed in alvo['enderecos']:
                    pdf.add_page()
                    pdf.header_op(st.session_state.missao)
                    # Conteúdo do Alvo... (simplificado para o exemplo)
                    pdf.set_xy(10, 60); pdf.set_font("Arial", 'B', 14)
                    pdf.cell(190, 10, f"ALVO: {alvo['nome']} | VTR: {alvo['viatura']}", 1, 1)
                    pdf.draw_footer_fiel()
            
            pdf_out = pdf.output(dest='S').encode('latin-1', 'replace')
            st.download_button("⬇️ BAIXAR PDF COMPLETO", data=pdf_out, file_name="Operacao_Completa.pdf")

# --- TELA 2: EDITAR MISSÃO (MODAL DO LÁPIS) ---
elif st.session_state.view == 'edit_missao':
    st.markdown("<h2>🖊️ EDITAR DADOS DA OPERAÇÃO</h2>", unsafe_allow_html=True)
    with st.container():
        st.session_state.missao['nome'] = st.text_input("Nome da Operação", st.session_state.missao['nome'])
        st.session_state.missao['unidade'] = st.text_input("Equipe Responsável", st.session_state.missao['unidade'])
        st.session_state.missao['ponto'] = st.text_input("Endereço do Briefing", st.session_state.missao['ponto'])
        c1, c2 = st.columns(2)
        st.session_state.missao['data_br'] = c1.text_input("Horário Briefing", st.session_state.missao['data_br'])
        st.session_state.missao['h_hora'] = c2.text_input("H-Hora (Execução)", st.session_state.missao['h_hora'])
        st.session_state.missao['resumo'] = st.text_area("Resumo da Missão", st.session_state.missao['resumo'])
        
        c_b1, c_b2 = st.columns(2)
        if c_b1.button("Cancelar"): ir_para('painel')
        if c_b2.button("Salvar Alterações"): ir_para('painel')

# --- TELA 3: NOVO ALVO TÁTICO (FORMULÁRIO ORGANIZADO) ---
elif st.session_state.view == 'novo_alvo':
    st.markdown("<h2>🎯 NOVO ALVO TÁTICO</h2>", unsafe_allow_html=True)
    
    if 'temp_equipe' not in st.session_state: st.session_state.temp_equipe = []
    if 'temp_ends' not in st.session_state: st.session_state.temp_ends = []

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.write("👤 QUALIFICAÇÃO DO OBJETIVO")
            nome = st.text_input("Nome Completo")
            vulgo = st.text_input("Vulgo / Apelido")
            tipo = st.selectbox("Tipo", ["Busca e Apreensão", "Prisão Preventiva"])
            viatura = st.text_input("Viatura (VTR)")
            foto_alvo = st.file_uploader("Retrato do Alvo")
        
        with col2:
            st.write("👥 COMPOSIÇÃO DA EQUIPE")
            membro = st.text_input("Nome do Policial")
            if st.button("➕ Adicionar Integrante"):
                if membro: st.session_state.temp_equipe.append(membro)
            st.info(f"Equipe: {', '.join(st.session_state.temp_equipe)}")

        st.divider()
        st.write("📍 ENDEREÇOS DE CUMPRIMENTO")
        end_rua = st.text_input("Endereço (Rua, Nº, Bairro)")
        end_obs = st.text_area("Observações Táticas")
        foto_casa = st.file_uploader("Foto da Fachada")
        if st.button("➕ Adicionar Este Endereço"):
            if end_rua: st.session_state.temp_ends.append({'rua': end_rua, 'obs': end_obs, 'foto': foto_casa})
        st.success(f"{len(st.session_state.temp_ends)} endereço(s) vinculados a este alvo.")

        c_f1, c_f2 = st.columns(2)
        if c_f1.button("CANCELAR"): 
            st.session_state.temp_equipe = []; st.session_state.temp_ends = []; ir_para('painel')
        if c_f2.button("✅ SALVAR ALVO NO PAINEL"):
            novo = {
                'nome': nome, 'vulgo': vulgo, 'tipo': tipo, 'viatura': viatura,
                'equipe': st.session_state.temp_equipe, 'enderecos': st.session_state.temp_ends,
                'foto': foto_alvo
            }
            st.session_state.alvos.append(novo)
            st.session_state.temp_equipe = []; st.session_state.temp_ends = []; ir_para('painel')
            st.rerun()
