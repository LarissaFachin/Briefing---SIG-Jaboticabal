import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image, ImageOps
import io
import os
from datetime import datetime

# --- TEMA TÁTICO AVANÇADO (CSS) ---
st.set_page_config(layout="wide", page_title="INTEL - SISTEMA DE BRIEFING", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #020617;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Header Estilo Comando */
    .command-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #020617 100%);
        border-left: 5px solid #3b82f6;
        padding: 20px;
        border-radius: 0px 15px 15px 0px;
        margin-bottom: 30px;
        box-shadow: 10px 10px 20px rgba(0,0,0,0.5);
    }
    
    /* Cards de Alvo Estilo Dossier */
    .target-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid #334155;
        border-top: 4px solid #3b82f6;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .target-card:hover {
        border-top: 4px solid #60a5fa;
        background: rgba(30, 41, 59, 0.8);
        transform: translateY(-5px);
    }
    
    /* Inputs Estilizados */
    .stTextInput>div>div>input, .stTextArea>div>textarea, .stSelectbox>div>div {
        background-color: #0f172a !important;
        color: #3b82f6 !important;
        border: 1px solid #1e3a8a !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* Botão de Missão */
    .stButton>button {
        background: #1e40af !important;
        color: white !important;
        border: 1px solid #3b82f6 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: bold !important;
        border-radius: 4px !important;
        width: 100%;
    }
    
    .badge-vtr {
        background: #fbbf24;
        color: #000;
        padding: 2px 8px;
        font-size: 10px;
        font-weight: bold;
        border-radius: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE DADOS ---
if 'alvos' not in st.session_state: st.session_state.alvos = []
if 'missao' not in st.session_state: 
    st.session_state.missao = {
        'nome': 'OPERAÇÃO ALPHA', 'unidade': 'SIG - JABOTICABAL', 
        'ponto': 'Rua Antonio Freitas, 100', 'data_br': '2026-03-11 05:30', 
        'h_hora': '2026-03-11 06:00', 'resumo': 'Diretrizes táticas padrão.'
    }
if 'view' not in st.session_state: st.session_state.view = 'painel'

# --- MOTOR DE PDF PROFISSIONAL ---
class TacticalPDF(FPDF):
    def header(self):
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 35, 'F')
        self.set_xy(10, 10)
        self.set_font("Courier", 'B', 16)
        self.set_text_color(255, 255, 255)
        self.cell(140, 10, f"RELATORIO OPERACIONAL: {st.session_state.missao['nome'].upper()}", 0, 0)
        self.set_font("Courier", 'B', 8)
        self.cell(40, 10, "CONFIDENCIAL / RESTRITO", 0, 1, 'R')
        
    def add_target_page(self, alvo, endereco):
        self.add_page()
        # Banner Alvo
        self.set_fill_color(30, 58, 138)
        self.rect(10, 40, 190, 15, 'F')
        self.set_text_color(255, 255, 255)
        self.set_xy(15, 42)
        self.set_font("Arial", 'B', 14)
        self.cell(100, 10, f"OBJETIVO: {alvo['nome'].upper()} ({alvo['vulgo'].upper()})")
        self.set_font("Arial", 'B', 9)
        self.cell(80, 10, f"VTR: {alvo['viatura'].upper()} | {alvo['tipo'].upper()}", 0, 1, 'R')

        # Rodapé Tático
        self.set_xy(10, 220)
        self.set_text_color(0, 0, 0)
        self.set_font("Arial", 'B', 10)
        self.cell(190, 8, "RELATORIO DE CAMPO E APREENSÕES", 'T', 1, 'C')
        self.set_font("Arial", '', 8)
        for _ in range(5): self.cell(190, 6, "." * 130, 0, 1)

# --- NAVEGAÇÃO ---
def ir_para(v): st.session_state.view = v

# --- BARRA SUPERIOR (STATUS) ---
st.markdown(f"""
<div class="command-header">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div>
            <span style="color:#60a5fa; font-size:12px;">OPERACIONAL / STATUS: ATIVO</span>
            <h2 style="margin:0; letter-spacing:3px;">{st.session_state.missao['nome'].upper()} <span style='font-size:18px; cursor:pointer;' onclick='ir_para("config")'>✏️</span></h2>
            <span style="color:#94a3b8; font-size:14px;">📍 {st.session_state.missao['ponto']} | 🕒 H-HORA: {st.session_state.missao['h_hora']}</span>
        </div>
        <div style="text-align:right;">
            <span style="color:#94a3b8; font-size:12px;">UNIDADE</span><br>
            <span style="color:#3b82f6; font-weight:bold;">{st.session_state.missao['unidade']}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- MENU DE ABAS ---
tab_painel, tab_cadastro, tab_config = st.tabs(["🎯 PAINEL DE ALVOS", "➕ CADASTRAR ALVO", "⚙️ CONFIGURAÇÕES"])

# --- TAB 1: PAINEL ---
with tab_painel:
    if not st.session_state.alvos:
        st.markdown("<div style='text-align:center; padding:50px; color:#334155;'>AGUARDANDO CADASTRO DE OBJETIVOS...</div>", unsafe_allow_html=True)
    else:
        cols = st.columns(3)
        for idx, a in enumerate(st.session_state.alvos):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="target-card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <span style="color:#60a5fa; font-size:10px;">ID #{idx+6537}</span>
                        <span class="badge-vtr">{a['viatura'].upper()}</span>
                    </div>
                    <h3 style="margin:10px 0;">{a['nome'].upper()}</h3>
                    <p style="color:#94a3b8; font-size:12px; margin-bottom:5px;">VULGO: {a['vulgo'].upper()}</p>
                    <p style="color:#3b82f6; font-size:12px;">📍 {len(a['enderecos'])} Endereço(s)</p>
                    <div style="font-size:11px; color:#475569; border-top:1px solid #1e293b; padding-top:10px;">
                        EQUIPE: {", ".join(a['equipe'][:2])}...
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        if st.button("🚀 FINALIZAR E GERAR RELATÓRIO PDF"):
            pdf = TacticalPDF()
            for alvo in st.session_state.alvos:
                for ed in alvo['enderecos']:
                    pdf.add_target_page(alvo, ed)
                    # QR Code Rota
                    rota_url = f"https://www.google.com/maps/dir/{st.session_state.missao['ponto'].replace(' ','+')}/{ed['rua'].replace(' ','+')}"
                    qr = qrcode.make(rota_url)
                    qr_img = io.BytesIO()
                    qr.save(qr_img, format='PNG')
                    pdf.image(qr_img, 10, 180, 25, 25)
            
            # Geração estável para o Streamlit Cloud
            pdf_bytes = pdf.output() 
            st.download_button("⬇️ DOWNLOAD DOSSIE TÁTICO", data=bytes(pdf_bytes), file_name="Dossie_Intel.pdf", mime="application/pdf")

# --- TAB 2: CADASTRO ---
with tab_cadastro:
    st.markdown("### 📋 FICHA DE QUALIFICAÇÃO TÁTICA")
    
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            nome_a = st.text_input("NOME COMPLETO")
            vulgo_a = st.text_input("VULGO / ALCUNHA")
            tipo_a = st.selectbox("TIPO DE MANDADO", ["BUSCA E APREENSÃO", "PRISÃO PREVENTIVA", "TEMPORÁRIA"])
            vtr_a = st.text_input("VIATURA DESIGNADA (VTR)")
        
        with c2:
            st.write("👥 COMPOSIÇÃO DA EQUIPE")
            membro = st.text_input("NOME DO POLICIAL")
            if 'temp_equipe' not in st.session_state: st.session_state.temp_equipe = []
            if st.button("➕ ADICIONAR INTEGRANTE"):
                if membro: st.session_state.temp_equipe.append(membro)
            st.code(", ".join(st.session_state.temp_equipe) if st.session_state.temp_equipe else "NENHUM MEMBRO")

    st.divider()
    st.markdown("### 📍 LOGÍSTICA DE ENDEREÇOS")
    end_rua = st.text_input("ENDEREÇO COMPLETO (Rua, Número, Bairro, Cidade)")
    if end_rua:
        st.markdown(f"🔗 [ABRIR LOCALIZAÇÃO NO GOOGLE MAPS](https://www.google.com/maps/search/{end_rua.replace(' ', '+')})")
    
    col_img1, col_img2 = st.columns(2)
    f_alvo = col_img1.file_uploader("RETRATO DO ALVO", type=['jpg', 'png'])
    f_casa = col_img2.file_uploader("FACHADA DA RESIDÊNCIA", type=['jpg', 'png'])

    if st.button("💾 SALVAR OBJETIVO NO PAINEL"):
        if nome_a and end_rua:
            novo_alvo = {
                'nome': nome_a, 'vulgo': vulgo_a, 'tipo': tipo_a, 'viatura': vtr_a,
                'equipe': st.session_state.temp_equipe, 
                'enderecos': [{'rua': end_rua, 'foto': f_casa}],
                'foto_alvo': f_alvo
            }
            st.session_state.alvos.append(novo_alvo)
            st.session_state.temp_equipe = []
            st.success("OBJETIVO INTEGRADO AO PAINEL.")
            st.rerun()

# --- TAB 3: CONFIGURAÇÕES DA MISSÃO ---
with tab_config:
    st.markdown("### ⚙️ DIRETRIZES DA OPERAÇÃO")
    with st.form("config_op"):
        st.session_state.missao['nome'] = st.text_input("NOME DA OPERAÇÃO", st.session_state.missao['nome'])
        st.session_state.missao['unidade'] = st.text_input("UNIDADE RESPONSÁVEL", st.session_state.missao['unidade'])
        st.session_state.missao['ponto'] = st.text_input("PONTO DE ENCONTRO (COORDENADA ZERO)", st.session_state.missao['ponto'])
        st.session_state.missao['h_hora'] = st.text_input("H-HORA (EXECUÇÃO)", st.session_state.missao['h_hora'])
        st.session_state.missao['resumo'] = st.text_area("DIRETRIZES ESTRATÉGICAS", st.session_state.missao['resumo'])
        if st.form_submit_button("ATUALIZAR SISTEMA"):
            st.success("DADOS DA MISSÃO ATUALIZADOS.")
            st.rerun()
