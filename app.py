import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import io
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL (ESTILO DASHBOARD INTELIGÊNCIA) ---
st.set_page_config(layout="wide", page_title="SISTEMA OPS - TÁTICO")

st.markdown("""
    <style>
    .stApp { background-color: #050a14; color: #ffffff; }
    
    /* Cabeçalho da Operação */
    .op-header { background-color: #0b111b; border: 2px solid #1e3a8a; padding: 25px; border-radius: 20px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
    
    /* Ficha do Alvo (Estilo Militar) */
    .alvo-card { 
        background-color: #0f172a; 
        border-left: 8px solid #2563eb; 
        padding: 25px; 
        border-radius: 12px; 
        margin-bottom: 20px;
        border-top: 1px solid #1e3a8a;
        border-right: 1px solid #1e3a8a;
        border-bottom: 1px solid #1e3a8a;
    }
    
    label { color: #60a5fa !important; font-weight: bold !important; text-transform: uppercase; font-size: 12px !important; }
    
    /* Botões */
    .stButton>button { background-color: #2563eb !important; color: white !important; font-weight: bold !important; border-radius: 6px !important; border: none !important; height: 45px; }
    
    .badge-vtr { background-color: #1e3a8a; color: #60a5fa; padding: 3px 10px; border-radius: 4px; border: 1px solid #3b82f6; font-size: 12px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- BANCO DE DADOS EM MEMÓRIA ---
if 'alvos' not in st.session_state: st.session_state.alvos = []
if 'missao' not in st.session_state: 
    st.session_state.missao = {
        'nome': 'Operação', 'unidade': 'DELEGACIA DO MUNICÍPIO', 
        'ponto': 'Rua Antonio Freitas', 'data_br': '04/03/2026 05:30', 
        'h_hora': '04/03/2026 06:00', 'resumo': ''
    }
if 'view' not in st.session_state: st.session_state.view = 'painel'

# --- CLASSE DO PDF (LAYOUT FIEL AO MODELO) ---
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
        self.set_xy(160, 20); self.set_font("Arial", 'B', 10); self.cell(40, 12, missao['unidade'].upper(), 1, 1, 'C')
        self.set_xy(10, 42); self.set_font("Arial", 'B', 6)
        self.cell(60, 12, f"PONTO DE ENCONTRO: {missao['ponto'].upper()}", 1)
        self.cell(50, 12, f"BRIEFING: {missao['data_br']}", 1)
        self.cell(40, 12, f"H-HORA: {missao['h_hora']}", 1)
        self.cell(40, 12, f"ID MISSÃO: #{id(missao)%100000}", 1)

    def draw_footer_fiel(self):
        self.set_xy(10, 210); self.set_font("Arial", 'B', 8)
        self.cell(190, 8, "RELATÓRIO DE OCORRÊNCIA E APREENSÕES DE CAMPO", 'T', 1, 'C')
        for _ in range(3): self.cell(190, 6, "_"*110, 0, 1)

# --- TELA 1: PAINEL PRINCIPAL ---
if st.session_state.view == 'painel':
    st.markdown('<div class="op-header">', unsafe_allow_html=True)
    col_t1, col_t2 = st.columns([4, 1])
    with col_t1:
        st.markdown(f"<h1>{st.session_state.missao['nome'].upper()} <span style='font-size:20px; color:#3b82f6;' onclick='ir_para(\"edit_missao\")'>✏️</span></h1>", unsafe_allow_html=True)
        st.markdown(f"📍 {st.session_state.missao['ponto']} | 🕒 {st.session_state.missao['h_hora']}", unsafe_allow_html=True)
    with col_t2:
        if st.button("➕ NOVO ALVO"): st.session_state.view = 'novo_alvo'; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✏️ EDITAR DADOS GERAIS DA MISSÃO"): st.session_state.view = 'edit_missao'; st.rerun()

    st.divider()
    
    # LISTA DE FICHAS TÁTICAS
    for idx, alvo in enumerate(st.session_state.alvos):
        with st.container():
            st.markdown(f"""
            <div class='alvo-card'>
                <div style='display:flex; justify-content:space-between;'>
                    <h2 style='margin:0;'>{alvo['nome'].upper()}</h2>
                    <span class='badge-vtr'>VTR: {alvo['viatura'].upper()}</span>
                </div>
                <hr style='border: 0.5px solid #1e3a8a; margin: 10px 0;'>
                <p><b>ALCUNHA:</b> {alvo['vulgo'].upper()} | <b>TIPO:</b> {alvo['tipo'].upper()}</p>
                <p style='color:#94a3b8; font-size:13px;'><b>EQUIPE:</b> {', '.join(alvo['equipe'])}</p>
                <p style='color:#60a5fa;'>📍 {len(alvo['enderecos'])} endereço(s) vinculado(s)</p>
            </div>
            """, unsafe_allow_html=True)

    if st.session_state.alvos:
        st.divider()
        if st.button("🚀 GERAR PDF DE TODOS OS ALVOS"):
            pdf = BriefingPDF()
            for alvo in st.session_state.alvos:
                for idx_e, ed in enumerate(alvo['enderecos']):
                    pdf.add_page()
                    pdf.header_op(st.session_state.missao)
                    # Banner do Alvo
                    pdf.set_fill_color(26, 58, 108); pdf.rect(10, 58, 190, 15, 'F')
                    pdf.set_text_color(255, 255, 255); pdf.set_xy(12, 60); pdf.set_font("Arial", 'B', 14)
                    pdf.cell(100, 10, f"ALVO: {alvo['nome'].upper()} | VTR: {alvo['viatura'].upper()}")
                    
                    # Fotos (Simplificado)
                    pdf.set_fill_color(200, 200, 200); pdf.rect(10, 75, 93, 65, 'D')
                    pdf.rect(105, 75, 95, 65, 'D')
                    
                    # Rota Tática QR Code
                    rota_url = f"https://www.google.com/maps/dir/{st.session_state.missao['ponto'].replace(' ','+')}/{ed['rua'].replace(' ','+')}"
                    qr = qrcode.make(rota_url).save("t_qr.png")
                    pdf.image("t_qr.png", 10, 175, 25, 25)
                    pdf.set_xy(38, 180); pdf.set_font("Arial", 'B', 8); pdf.cell(100, 5, "ROTA: PONTO ENCONTRO -> ALVO")
                    
                    pdf.draw_footer_fiel()
            
            # CORREÇÃO DO ERRO DE GERAÇÃO:
            pdf_bytes = pdf.output()
            st.download_button("⬇️ BAIXAR PDF OPERACIONAL", data=pdf_bytes, file_name="Dossie_Operacional.pdf", mime="application/pdf")

# --- TELA 2: EDITAR MISSÃO ---
elif st.session_state.view == 'edit_missao':
    st.title("🖊️ EDITAR DADOS DA OPERAÇÃO")
    with st.container():
        st.session_state.missao['nome'] = st.text_input("Nome da Operação", st.session_state.missao['nome'])
        st.session_state.missao['ponto'] = st.text_input("Endereço do Ponto de Encontro", st.session_state.missao['ponto'])
        st.session_state.missao['h_hora'] = st.text_input("H-Hora", st.session_state.missao['h_hora'])
        if st.button("Salvar e Voltar"): st.session_state.view = 'painel'; st.rerun()

# --- TELA 3: NOVO ALVO TÁTICO ---
elif st.session_state.view == 'novo_alvo':
    st.title("🎯 NOVO ALVO TÁTICO")
    
    if 't_equipe' not in st.session_state: st.session_state.t_equipe = []
    if 't_ends' not in st.session_state: st.session_state.t_ends = []

    c1, c2 = st.columns(2)
    with c1:
        nome = st.text_input("Nome Completo")
        vulgo = st.text_input("Vulgo / Apelido")
        tipo = st.selectbox("Tipo", ["Busca e Apreensão", "Prisão Preventiva"])
        vtr = st.text_input("Viatura (VTR)")
    
    with c2:
        membro = st.text_input("Adicionar Policial na Equipe")
        if st.button("➕ Integrante"):
            if membro: st.session_state.t_equipe.append(membro)
        st.info(f"Equipe: {', '.join(st.session_state.t_equipe)}")

    st.divider()
    st.write("📍 ENDEREÇOS")
    end_rua = st.text_input("Endereço Completo (Rua, Nº, Bairro, Cidade)")
    
    # VÍNCULO COM GOOGLE MAPS EM TEMPO REAL
    if end_rua:
        maps_link = f"https://www.google.com/maps/search/{end_rua.replace(' ', '+')}"
        st.markdown(f"[📍 Verificar este endereço no Google Maps]({maps_link})")

    obs = st.text_area("Observações do Local")
    if st.button("➕ Adicionar Endereço a este Alvo"):
        if end_rua: st.session_state.t_ends.append({'rua': end_rua, 'obs': obs})
    st.success(f"{len(st.session_state.t_ends)} endereço(s) cadastrados.")

    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("CANCELAR"): st.session_state.view = 'painel'; st.rerun()
    if col_btn2.button("✅ SALVAR ALVO"):
        st.session_state.alvos.append({
            'nome': nome, 'vulgo': vulgo, 'tipo': tipo, 'viatura': vtr,
            'equipe': st.session_state.t_equipe, 'enderecos': st.session_state.t_ends
        })
        st.session_state.t_equipe = []; st.session_state.t_ends = []; st.session_state.view = 'painel'; st.rerun()
