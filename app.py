import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import os
from datetime import datetime
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TACTICAL OPS | SIG JABOTICABAL", layout="wide", page_icon="🛡️")

# --- CSS PARA DESTAQUE DE BOTÕES (FUNDO CLARO) ---
st.markdown("""
    <style>
    /* Estilização Geral do Texto */
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #1e3a8a !important; font-family: 'Segoe UI', sans-serif; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }

    /* BOTÃO PRINCIPAL: ADICIONAR NOVO ALVO (AZUL FORTE) */
    div.stButton > button[key="btn_add_alvo"] {
        background-color: #1d4ed8 !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        height: 50px !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }

    /* BOTÃO PRINCIPAL: GERAR DOSSIÊ FINAL (VERDE FORTE) */
    div.stButton > button[key="btn_gerar_pdf"] {
        background-color: #15803d !important;
        color: white !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        height: 70px !important;
        border-radius: 12px !important;
        border: 2px solid #166534 !important;
        box-shadow: 0 10px 15px rgba(21, 128, 61, 0.3) !important;
        text-transform: uppercase;
    }

    /* BOTÕES SECUNDÁRIOS (AGENTE/ENDEREÇO) */
    div.stButton > button[key*="ba_"], div.stButton > button[key*="be_"] {
        background-color: #f3f4f6 !important;
        color: #1f2937 !important;
        border: 1px solid #d1d5db !important;
    }

    /* BOTÃO REMOVER (VERMELHO) */
    div.stButton > button[key*="rem_"] {
        background-color: #dc2626 !important;
        color: white !important;
        border: none !important;
    }

    /* Containers de Alvo */
    div[data-testid="stExpander"], div.stVerticalBlock > div[style*="border"] {
        background-color: #f9fafb !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 10px !important;
        padding: 20px !important;
    }

    label { font-weight: bold !important; color: #374151 !important; }
    </style>
""", unsafe_allow_html=True)

if 'alvos' not in st.session_state:
    st.session_state.alvos = []

# --- CLASSE DO PDF ---
class TacticalPDF(FPDF):
    def header(self):
        self.set_fill_color(30, 58, 138)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 8)
        self.cell(0, 6, 'DOCUMENTO RESTRITO - USO EXCLUSIVO DAS FORÇAS DE SEGURANÇA', 0, 1, 'C', True)
        self.ln(3)

    def draw_pattern_grid(self, x, y, label):
        self.set_font('Helvetica', 'B', 7)
        self.set_text_color(150, 150, 150)
        self.text(x, y - 2, label)
        for r in range(3):
            for c in range(3):
                self.ellipse(x + (c * 5), y + (r * 5), 0.8, 0.8)

    def footer(self):
        self.set_y(-75)
        self.set_fill_color(240, 240, 240)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(0, 0, 0)
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
        self.cell(0, 10, f'SIG JABOTICABAL | OPERACIONAL | PÁGINA {self.page_no()}', 0, 0, 'C')

def gerar_qr_rota(orig, dest):
    url = f"https://www.google.com/maps/dir/?api=1&origin={urllib.parse.quote(orig)}&destination={urllib.parse.quote(dest)}"
    qr = qrcode.make(url)
    path = f"qr_{hash(dest)}.png"
    qr.save(path)
    return path

# --- INTERFACE ---
st.title("🛡️ TACTICAL OPS: SIG JABOTICABAL")

with st.container(border=True):
    st.subheader("📋 Configuração da Missão")
    c1, c2 = st.columns([2, 1])
    nome_op = c1.text_input("NOME DA OPERAÇÃO", "OPERAÇÃO")
    unidade = c1.text_input("UNIDADE DE COMANDO", "SIG JABOTICABAL")
    data_op = c2.text_input("DATA/HORA BRIEFING", "27/01/2026 03:30")
    h_hora = c2.text_input("H-HORA (EXECUÇÃO)", "06:00")
    # Endereço solicitado
    end_origem = st.text_input("📍 PONTO DE PARTIDA (GPS)", "Praça Pedro Dória, s/n, Centro, Jaboticabal - SP, CEP: 14870-000")

st.markdown("<br>", unsafe_allow_html=True)
if st.button("➕ ADICIONAR NOVO ALVO TÁTICO", key="btn_add_alvo"):
    st.session_state.alvos.append({
        'nome': '', 'vulgo': '', 'mandado': 'BUSCA E APREENSÃO',
        'enderecos': [''], 'agentes': [''], 'viatura': '',
        'foto_alvo': None, 'foto_casa': None
    })

# Lista de Alvos
for idx, alvo in enumerate(st.session_state.alvos):
    with st.container(border=True):
        st.markdown(f"### 🎯 ALVO #{idx+1}")
        c1, c2, c3 = st.columns([2, 1, 1])
        alvo['nome'] = c1.text_input("Nome Completo", value=alvo['nome'], key=f"n_{idx}")
        alvo['vulgo'] = c2.text_input("Vulgo", value=alvo['vulgo'], key=f"v_{idx}")
        alvo['mandado'] = c3.selectbox("Mandado", ["BUSCA E APREENSÃO", "PRISÃO PREVENTIVA", "TEMPORÁRIA"], key=f"m_{idx}")
        
        # Logística
        st.write("👥 **Logística e Equipe Escalada**")
        alvo['viatura'] = st.text_input("Viatura (Prefixo/Modelo)", value=alvo['viatura'], key=f"via_{idx}")
        cols_ag = st.columns(3)
        for i_ag in range(len(alvo['agentes'])):
            alvo['agentes'][i_ag] = cols_ag[i_ag % 3].text_input(f"Agente {i_ag+1}", value=alvo['agentes'][i_ag], key=f"a_{idx}_{i_ag}")
        if st.button("➕ Adicionar Policial", key=f"ba_{idx}"):
            alvo['agentes'].append(''); st.rerun()

        # Fotos
        st.markdown("---")
        f1, f2 = st.columns(2)
        alvo['foto_alvo'] = f1.file_uploader("📸 Retrato do Alvo", key=f"fa_{idx}")
        alvo['foto_casa'] = f2.file_uploader("🏠 Fachada da Residência", key=f"fc_{idx}")

        # Endereços
        st.write("📍 **Localidades e Alvos GPS**")
        for e_i, end in enumerate(alvo['enderecos']):
            alvo['enderecos'][e_i] = st.text_input(f"Endereço {e_i+1}", value=end, key=f"e_{idx}_{e_i}")
        if st.button("➕ Adicionar Endereço", key=f"be_{idx}"):
            alvo['enderecos'].append(''); st.rerun()

        if st.button("🗑️ Remover Alvo do Plano", key=f"rem_{idx}"):
            st.session_state.alvos.pop(idx); st.rerun()

# Botão Gerar PDF
if st.session_state.alvos:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🛰️ GERAR DOSSIÊ TÁTICO FINAL", key="btn_gerar_pdf"):
        pdf = TacticalPDF()
        for i, alvo in enumerate(st.session_state.alvos):
            pdf.add_page()
            
            # Cabeçalho: Apenas Página 1
            if i == 0:
                pdf.set_font('Helvetica', 'B', 18); pdf.set_text_color(30, 58, 138)
                pdf.cell(0, 10, nome_op.upper(), 0, 1)
                pdf.set_font('Helvetica', 'B', 10); pdf.cell(0, 5, f"UNIDADE: {unidade.upper()}", 0, 1)
                pdf.ln(2)
                pdf.set_fill_color(240, 240, 240); pdf.set_font('Helvetica', 'B', 8); pdf.set_text_color(0,0,0)
                pdf.cell(63, 8, f" ORIGEM: {end_origem[:35]}...", 1, 0, 'L', True)
                pdf.cell(63, 8, f" BRIEFING: {data_op}", 1, 0, 'L', True)
                pdf.cell(64, 8, f" H-HORA: {h_hora}", 1, 1, 'L', True)
                pdf.ln(5)

            # Header do Alvo
            pdf.set_fill_color(30, 58, 138); pdf.set_text_color(255, 255, 255); pdf.set_font('Helvetica', 'B', 12)
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
            
            # Logística (Equipe) - Antes dos Endereços
            pdf.set_font('Helvetica', 'B', 10); pdf.cell(0, 8, "LOGÍSTICA E EQUIPE OPERACIONAL", 'B', 1); pdf.ln(2)
            pdf.set_font('Helvetica', 'B', 9); pdf.cell(22, 6, "VIATURA: ", 0, 0)
            pdf.set_font('Helvetica', '', 9); pdf.cell(0, 6, alvo['viatura'].upper(), 0, 1)
            pdf.set_font('Helvetica', 'B', 9); pdf.cell(22, 6, "EFETIVO: ", 0, 0)
            pdf.set_font('Helvetica', '', 9)
            pdf.multi_cell(0, 6, " | ".join([a for a in alvo['agentes'] if a.strip()]))
            pdf.ln(3)

            # Endereços e GPS - No Final
            pdf.set_font('Helvetica', 'B', 10); pdf.cell(0, 8, "ROTAS GPS TÁTICAS", 'B', 1); pdf.ln(2)
            for end in alvo['enderecos']:
                if end.strip():
                    qr_p = gerar_qr_rota(end_origem, end); curr_y = pdf.get_y()
                    if curr_y > 185: pdf.add_page(); curr_y = 20
                    pdf.image(qr_p, x=10, y=curr_y, w=22)
                    pdf.set_xy(35, curr_y + 4); pdf.set_font('Helvetica', 'B', 8)
                    pdf.multi_cell(0, 4, f"DESTINO: {end.upper()}\nSAÍDA: {end_origem.upper()}")
                    pdf.set_y(curr_y + 25); os.remove(qr_p)

        filename = f"Briefing_SIG_{datetime.now().strftime('%d%m%Y')}.pdf"
        pdf.output(filename)
        with open(filename, "rb") as f:
            st.download_button("📩 BAIXAR DOSSIÊ TÁTICO AGORA", f, file_name=filename)
