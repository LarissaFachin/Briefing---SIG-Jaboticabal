import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import os
from datetime import datetime
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TACTICAL OPS | SIG JABOTICABAL", layout="wide", page_icon="🛡️")

# --- CSS DE ALTA PERFORMANCE (DARK TACTICAL THEME) ---
st.markdown("""
    <style>
    /* Reset e Fundo Principal */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }

    /* Estilização de Títulos */
    h1, h2, h3 {
        color: #58a6ff !important;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        border-bottom: 2px solid #30363d;
        padding-bottom: 10px;
    }

    /* Cards de Containers */
    [data-testid="stVerticalBlock"] > div:has(div.stExpander),
    div.stVerticalBlock > div[style*="border"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3) !important;
    }

    /* Customização dos Inputs */
    .stTextInput input, .stSelectbox div, .stTextArea textarea {
        background-color: #0d1117 !important;
        color: #ffffff !important;
        border: 1px solid #484f58 !important;
        border-radius: 6px !important;
    }

    /* --- BOTÕES TÁTICOS (Cores Específicas) --- */
    
    /* 1. Botão Adicionar Novo Alvo (AZUL DE DESTAQUE) */
    div.stButton > button[key="btn_add_alvo"] {
        background-color: #1f6feb !important;
        color: white !important;
        border-radius: 8px !important;
        height: 50px !important;
        font-size: 16px !important;
        font-weight: bold !important;
        border: 1px solid #388bfd !important;
    }

    /* 2. Botões de Ação Positiva (VERDE) */
    div.stButton > button[key*="ba_"], 
    div.stButton > button[key*="be_"] {
        background-color: #238636 !important;
        color: white !important;
        border: none !important;
        border-radius: 5px !important;
        font-size: 13px !important;
    }

    /* 3. Botão de Remover (VERMELHO) */
    div.stButton > button[key*="rem_"] {
        background-color: #da3633 !important;
        color: white !important;
        border: none !important;
        opacity: 0.9;
    }
    div.stButton > button[key*="rem_"]:hover {
        opacity: 1;
        background-color: #f85149 !important;
    }

    /* 4. BOTÃO FINAL GERAR DOSSIÊ (OURO/AMARELO TÁTICO) */
    div.stButton > button[key="btn_gerar_pdf"] {
        background-color: #e3b341 !important;
        color: #0d1117 !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        height: 70px !important;
        border-radius: 15px !important;
        box-shadow: 0 0 20px rgba(227, 179, 65, 0.4) !important;
        border: 2px solid #f1e05a !important;
        margin-top: 30px !important;
    }

    /* Labels */
    label {
        color: #8b949e !important;
        font-weight: bold !important;
        font-size: 0.85rem !important;
    }
    
    /* Linha divisória profissional */
    hr {
        border-top: 1px solid #30363d !important;
        margin: 25px 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADO ---
if 'alvos' not in st.session_state:
    st.session_state.alvos = []

# --- CLASSE DO PDF ---
class TacticalPDF(FPDF):
    def header(self):
        self.set_fill_color(1, 4, 9)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 8)
        self.cell(0, 6, 'DOCUMENTO RESTRITO - USO EXCLUSIVO DAS FORÇAS DE SEGURANÇA', 0, 1, 'C', True)
        self.ln(3)

    def draw_pattern_grid(self, x, y, label):
        self.set_font('Helvetica', 'B', 7)
        self.set_text_color(100, 100, 100)
        self.text(x, y - 2, label)
        for r in range(3):
            for c in range(3):
                self.ellipse(x + (c * 5), y + (r * 5), 0.8, 0.8)

    def footer(self):
        self.set_y(-75)
        self.set_fill_color(248, 248, 248)
        self.set_font('Helvetica', 'B', 9)
        self.cell(0, 8, 'RELATÓRIO DE OCORRÊNCIA E APREENSÕES DE CAMPO', 'B', 1, 'C', True)
        for _ in range(3): self.cell(0, 6, '', 'B', 1)
        curr_y = self.get_y() + 5
        for i in range(1, 5): self.draw_pattern_grid(15 + ((i-1)*18), curr_y, f"DISP {i}")
        self.line(88, curr_y-2, 88, curr_y+15)
        self.set_xy(92, curr_y)
        self.set_font('Helvetica', 'B', 7)
        self.cell(0, 4, 'CHECKLIST DISPOSITIVOS (IMEI/SN)', 0, 1)
        for _ in range(2): self.set_x(92); self.cell(0, 7, '', 'B', 1)
        self.set_y(-10); self.set_font('Helvetica', 'I', 6); self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'SIG JABOTICABAL | PÁGINA {self.page_no()}', 0, 0, 'C')

def gerar_qr_rota(orig, dest):
    url = f"https://www.google.com/maps/dir/?api=1&origin={urllib.parse.quote(orig)}&destination={urllib.parse.quote(dest)}"
    qr = qrcode.make(url)
    path = f"qr_{hash(dest)}.png"
    qr.save(path)
    return path

# --- INTERFACE PRINCIPAL ---
st.title("🛡️ TACTICAL OPS: INTELLIGENCE MODULE")

# 1. CABEÇALHO DA OPERAÇÃO
with st.container(border=True):
    st.subheader("📁 Configuração da Missão")
    c1, c2 = st.columns([2, 1])
    nome_op = c1.text_input("NOME DA OPERAÇÃO", "OPERAÇÃO")
    unidade = c1.text_input("UNIDADE DE COMANDO", "SIG JABOTICABAL")
    data_op = c2.text_input("DATA/HORA BRIEFING", "27/01/2026 03:30")
    h_hora = c2.text_input("H-HORA (EXECUÇÃO)", "06:00")
    end_origem = st.text_input("📍 PONTO DE PARTIDA (GPS)", "Praça Pedro Dória, s/n, Centro, Jaboticabal - SP, CEP: 14870-000")

st.markdown("<br>", unsafe_allow_html=True)

# Botão de Adicionar Alvo
if st.button("➕ ADICIONAR NOVO ALVO TÁTICO", key="btn_add_alvo"):
    st.session_state.alvos.append({
        'nome': '', 'vulgo': '', 'mandado': 'BUSCA E APREENSÃO',
        'enderecos': [''], 'agentes': [''], 'viatura': '',
        'foto_alvo': None, 'foto_casa': None
    })

# 2. LISTA DE ALVOS
for idx, alvo in enumerate(st.session_state.alvos):
    with st.container(border=True):
        st.markdown(f"### 🎯 ALVO #{idx+1}")
        
        # Qualificação
        c1, c2, c3 = st.columns([2, 1, 1])
        alvo['nome'] = c1.text_input("Nome Completo", value=alvo['nome'], key=f"n_{idx}")
        alvo['vulgo'] = c2.text_input("Vulgo / Apelido", value=alvo['vulgo'], key=f"v_{idx}")
        alvo['mandado'] = c3.selectbox("Tipo de Mandado", ["BUSCA E APREENSÃO", "PRISÃO PREVENTIVA", "TEMPORÁRIA"], key=f"m_{idx}")
        
        # Logística
        st.markdown("<hr>", unsafe_allow_html=True)
        st.write("🚔 **Logística e Equipe Operacional**")
        alvo['viatura'] = st.text_input("Viatura (Prefixo/Modelo)", value=alvo['viatura'], key=f"via_{idx}")
        
        num_ag = len(alvo['agentes'])
        cols_ag = st.columns(3)
        for i_ag in range(num_ag):
            alvo['agentes'][i_ag] = cols_ag[i_ag % 3].text_input(f"Agente {i_ag+1}", value=alvo['agentes'][i_ag], key=f"a_{idx}_{i_ag}")
        
        if st.button("➕ Adicionar Policial", key=f"ba_{idx}"):
            alvo['agentes'].append(''); st.rerun()

        # Fotos e Reconhecimento
        st.markdown("<hr>", unsafe_allow_html=True)
        f1, f2 = st.columns(2)
        alvo['foto_alvo'] = f1.file_uploader("👤 Retrato do Alvo", key=f"fa_{idx}")
        alvo['foto_casa'] = f2.file_uploader("🏠 Fachada da Residência", key=f"fc_{idx}")

        # Localidades
        st.write("📍 **Localidades e Objetivos GPS**")
        for e_i, end in enumerate(alvo['enderecos']):
            alvo['enderecos'][e_i] = st.text_input(f"Endereço {e_i+1}", value=end, key=f"e_{idx}_{e_i}")
        
        if st.button("➕ Adicionar Endereço", key=f"be_{idx}"):
            alvo['enderecos'].append(''); st.rerun()

        # Botão Excluir Alvo
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ REMOVER ALVO DO PLANO", key=f"rem_{idx}"):
            st.session_state.alvos.pop(idx); st.rerun()

# 3. GERAÇÃO DO PDF FINAL
if st.session_state.alvos:
    st.markdown("<br><hr>", unsafe_allow_html=True)
    if st.button("🚀 GERAR DOSSIÊ TÁTICO FINAL", key="btn_gerar_pdf"):
        pdf = TacticalPDF()
        for i, alvo in enumerate(st.session_state.alvos):
            pdf.add_page()
            
            if i == 0:
                pdf.set_font('Helvetica', 'B', 18); pdf.set_text_color(0, 30, 80)
                pdf.cell(0, 10, nome_op.upper(), 0, 1)
                pdf.set_font('Helvetica', 'B', 10); pdf.cell(0, 5, f"UNIDADE: {unidade.upper()}", 0, 1)
                pdf.ln(2)
                pdf.set_fill_color(240, 240, 240); pdf.set_font('Helvetica', 'B', 8); pdf.set_text_color(0,0,0)
                pdf.cell(63, 8, f" ORIGEM: {end_origem[:35]}...", 1, 0, 'L', True)
                pdf.cell(63, 8, f" BRIEFING: {data_op}", 1, 0, 'L', True)
                pdf.cell(64, 8, f" H-HORA: {h_hora}", 1, 1, 'L', True)
                pdf.ln(5)

            # Header Alvo
            pdf.set_fill_color(0, 35, 90); pdf.set_text_color(255, 255, 255); pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(125, 10, f" ALVO: {alvo['nome'].upper()}", 0, 0, 'L', True)
            pdf.cell(65, 10, alvo['mandado'], 0, 1, 'R', True)
            pdf.set_text_color(0,0,0); pdf.set_font('Helvetica', 'B', 9)
            pdf.cell(0, 6, f"VULGO: {alvo['vulgo']}", 0, 1)

            y_f = pdf.get_y() + 2
            if alvo['foto_alvo']:
                path_a = f"tmp_a_{i}.png"; Image.open(alvo['foto_alvo']).save(path_a)
                pdf.image(path_a, x=10, y=y_f, w=92, h=62)
                pdf.set_xy(10, y_f + 57); pdf.set_fill_color(0,0,0); pdf.set_text_color(255,255,255)
                pdf.cell(92, 5, " IDENTIFICAÇÃO POSITIVA", 0, 0, 'L', True)
            if alvo['foto_casa']:
                path_c = f"tmp_c_{i}.png"; Image.open(alvo['foto_casa']).save(path_c)
                pdf.image(path_c, x=105, y=y_f, w=95, h=62)
                pdf.set_xy(105, y_f + 57); pdf.set_text_color(255,255,255)
                pdf.cell(95, 5, " PERÍMETRO DE ENTRADA", 0, 1, 'L', True)
            
            pdf.set_y(y_f + 68); pdf.set_text_color(0,0,0)
            
            # Logística
            pdf.set_font('Helvetica', 'B', 10); pdf.cell(0, 8, "LOGÍSTICA E EQUIPE OPERACIONAL", 'B', 1); pdf.ln(2)
            pdf.set_font('Helvetica', 'B', 9); pdf.cell(22, 6, "VIATURA: ", 0, 0)
            pdf.set_font('Helvetica', '', 9); pdf.cell(0, 6, alvo['viatura'].upper() if alvo['viatura'] else "NÃO INFORMADA", 0, 1)
            pdf.set_font('Helvetica', 'B', 9); pdf.cell(22, 6, "EFETIVO: ", 0, 0)
            pdf.set_font('Helvetica', '', 9)
            pdf.multi_cell(0, 6, " | ".join([a for a in alvo['agentes'] if a.strip()]))
            pdf.ln(3)

            # Rotas
            pdf.set_font('Helvetica', 'B', 10); pdf.cell(0, 8, "ROTAS GPS TÁTICAS", 'B', 1); pdf.ln(2)
            for end in alvo['enderecos']:
                if end.strip():
                    qr_p = gerar_qr_rota(end_origem, end); curr_y = pdf.get_y()
                    if curr_y > 185: pdf.add_page(); curr_y = 20
                    pdf.image(qr_p, x=10, y=curr_y, w=22)
                    pdf.set_xy(35, curr_y + 4); pdf.set_font('Helvetica', 'B', 8)
                    pdf.multi_cell(0, 4, f"DESTINO: {end.upper()}\nSAÍDA: {end_origem.upper()}")
                    pdf.set_y(curr_y + 25); os.remove(qr_p)

        pdf_name = f"Dossie_SIG_{datetime.now().strftime('%d%m%Y')}.pdf"
        pdf.output(pdf_name)
        with open(pdf_name, "rb") as f:
            st.download_button("📩 BAIXAR DOSSIÊ DE INTELIGÊNCIA COMPLETO", f, file_name=pdf_name)
