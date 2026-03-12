import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import os
from datetime import datetime
import urllib.parse

# --- CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="TACTICAL OPS | SIG JABOTICABAL", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button[key="add"] { background-color: #28a745 !important; color: white; font-weight: bold; width: 100%; }
    .stButton>button[key="pdf"] { background-color: #1A337E !important; color: white; font-size: 20px; font-weight: bold; width: 100%; height: 60px; border-radius: 10px; }
    .stButton>button[key*="rem"] { background-color: #dc3545 !important; color: white; }
    div[data-testid="stExpander"] { border: 1px solid #d1d5db; border-radius: 10px; background-color: #f8f9fa; }
    label { font-weight: bold !important; color: #333 !important; }
    </style>
""", unsafe_allow_html=True)

if 'alvos' not in st.session_state:
    st.session_state.alvos = []

# --- CLASSE DO PDF (ESTRUTURA PROFISSIONAL IDENTICA AO MODELO) ---
class TacticalPDF(FPDF):
    def header(self):
        # Tarja Preta Superior
        self.set_fill_color(0, 0, 0)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 8)
        self.cell(0, 6, 'S I G I L O S O   -   D O C U M E N T O   D E   I N T E L I G Ê N C I A   -   R E S T R I T O', 0, 1, 'C', True)
        self.ln(5)

    def draw_section_bullet(self, x, y):
        """Desenha o quadradinho azul de seção (evita erro Unicode)"""
        self.set_fill_color(26, 51, 126) 
        self.rect(x, y + 1.5, 3, 3, 'F')

    def footer(self):
        # Relatório de Ocorrência
        self.set_y(-75)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, 'R E L A T Ó R I O  D E  O C O R R Ê N C I A  E  A P R E E N S Õ E S  D E  C A M P O', 'B', 1, 'C')
        for _ in range(3): self.cell(0, 6, '', 'B', 1)
        
        curr_y = self.get_y() + 5
        # Grids de Desbloqueio (DISP 1 a 4)
        for i in range(1, 5):
            x_pos = 15 + ((i-1)*20)
            self.set_font('Helvetica', 'B', 6)
            self.set_text_color(100, 100, 100)
            self.text(x_pos, curr_y - 2, f"DISP. {i}")
            for r in range(3):
                for c in range(3):
                    self.ellipse(x_pos + (c * 4), curr_y + (r * 4), 0.8, 0.8)
        
        # Checklist IMEI
        self.line(100, curr_y - 2, 100, curr_y + 20)
        self.set_xy(105, curr_y - 2)
        self.set_font('Helvetica', 'B', 7)
        self.cell(0, 4, 'CHECKLIST DE DISPOSITIVOS (IMEI/SN)', 0, 1)
        for _ in range(2):
            self.set_x(105)
            self.cell(0, 8, '', 'B', 1)

        # Rodapé Institucional
        self.set_y(-10)
        self.set_font('Helvetica', '', 6)
        self.set_text_color(150, 150, 150)
        agora = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        self.cell(60, 10, 'TACTICALOPS INTELLIGENCE FRAMEWORK', 0, 0, 'L')
        self.cell(70, 10, f'DATA/HORA DOC: {agora}', 0, 0, 'C')
        self.cell(0, 10, f'PÁGINA {self.page_no()}', 0, 0, 'R')

def gerar_qr(orig, dest):
    url = f"https://www.google.com/maps/dir/?api=1&origin={urllib.parse.quote(orig)}&destination={urllib.parse.quote(dest)}"
    qr = qrcode.make(url)
    path = f"qr_{hash(dest)}.png"
    qr.save(path)
    return path

# --- INTERFACE STREAMLIT ---
st.title("🛡️ TACTICAL OPS: SIG JABOTICABAL")

with st.container(border=True):
    st.subheader("📋 Configuração da Missão")
    c1, c2 = st.columns([2, 1])
    nome_op = c1.text_input("NOME DA OPERAÇÃO", "OPERAÇÃO")
    unidade = c1.text_input("UNIDADE DE COMANDO", "SIG JABOTICABAL")
    data_op = c2.text_input("DATA/HORA BRIEFING", "27/01/2026 03:30")
    h_hora = c2.text_input("H-HORA (EXECUÇÃO)", "06:00")
    end_origem = st.text_input("📍 PONTO DE PARTIDA (GPS)", "Praça Pedro Dória, s/n, Centro, Jaboticabal - SP")

st.markdown("<br>", unsafe_allow_html=True)
if st.button("➕ ADICIONAR NOVO ALVO", key="add"):
    st.session_state.alvos.append({
        'nome': '', 'vulgo': '', 'mandado': 'BUSCA E APREENSÃO',
        'enderecos': [''], 'agentes': '', 'viatura': '',
        'foto_alvo': None, 'foto_casa': None
    })

for idx, alvo in enumerate(st.session_state.alvos):
    with st.expander(f"🎯 ALVO #{idx+1}", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        alvo['nome'] = c1.text_input("Nome Completo", key=f"n_{idx}")
        alvo['vulgo'] = c2.text_input("Vulgo", key=f"v_{idx}")
        alvo['mandado'] = c3.selectbox("Mandado", ["BUSCA E APREENSÃO", "PRISÃO PREVENTIVA", "TEMPORÁRIA"], key=f"m_{idx}")
        
        alvo['viatura'] = st.text_input("Viatura / Prefixo", key=f"via_{idx}")
        alvo['agentes'] = st.text_area("Agentes Escalados", key=f"a_{idx}")

        f1, f2 = st.columns(2)
        alvo['foto_alvo'] = f1.file_uploader("Foto do Alvo", key=f"fa_{idx}")
        alvo['foto_casa'] = f2.file_uploader("Foto da Fachada", key=f"fc_{idx}")

        alvo['enderecos'][0] = st.text_input("Endereço de Cumprimento", key=f"e_{idx}")

        if st.button("🗑️ Remover Alvo", key=f"rem_{idx}"):
            st.session_state.alvos.pop(idx); st.rerun()

# --- GERAÇÃO DO PDF ---
if st.session_state.alvos and st.button("🛰️ GERAR DOSSIÊ TÁTICO FINAL", key="pdf"):
    pdf = TacticalPDF()
    for i, alvo in enumerate(st.session_state.alvos):
        pdf.add_page()
        
        # Cabeçalho: Operação e Comando
        pdf.set_font('Helvetica', 'B', 24); pdf.set_text_color(0, 0, 0)
        pdf.cell(130, 10, nome_op.upper(), 0, 0)
        
        # Comando Operacional (Direita)
        pdf.line(148, 20, 148, 32)
        pdf.set_xy(150, 22); pdf.set_font('Helvetica', '', 6); pdf.set_text_color(100, 100, 100)
        pdf.cell(50, 4, 'COMANDO OPERACIONAL', 0, 1, 'R')
        pdf.set_font('Helvetica', 'B', 10); pdf.set_text_color(0, 0, 0)
        pdf.set_x(150); pdf.cell(50, 5, unidade.upper(), 0, 1, 'R')
        
        # Grid de Informações
        pdf.set_y(38)
        pdf.set_font('Helvetica', 'B', 6); pdf.set_text_color(100, 100, 100)
        pdf.cell(47, 4, 'PONTO DE ENCONTRO', 'TLR', 0)
        pdf.cell(47, 4, 'BRIEFING (DATA/HORA)', 'TLR', 0)
        pdf.cell(47, 4, 'H-HORA (EXECUÇÃO)', 'TLR', 0)
        pdf.cell(47, 4, 'ID MISSÃO', 'TLR', 1)
        
        pdf.set_font('Helvetica', 'B', 8); pdf.set_text_color(0, 0, 0)
        x_grid, y_grid = pdf.get_x(), pdf.get_y()
        pdf.multi_cell(47, 4, end_origem, 'BLR', 'L')
        pdf.set_xy(x_grid + 47, y_grid)
        pdf.set_text_color(30, 50, 120); pdf.cell(47, 8, data_op, 'BLR', 0)
        pdf.set_text_color(200, 0, 0); pdf.cell(47, 8, h_hora, 'BLR', 0)
        pdf.set_text_color(0, 0, 0); pdf.cell(47, 8, f'#{i+1001:06d}', 'BLR', 1)

        # Banner Azul de Mandado
        pdf.ln(4)
        pdf.set_fill_color(26, 51, 126); pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 10, alvo['mandado'].upper(), 0, 1, 'C', True)

        # Fotos (Side by Side)
        pdf.ln(3)
        y_fotos = pdf.get_y()
        if alvo['foto_alvo']:
            Image.open(alvo['foto_alvo']).save(f"tmp_a_{i}.png")
            pdf.image(f"tmp_a_{i}.png", x=10, y=y_fotos, w=93, h=65)
            pdf.set_xy(10, y_fotos + 60); pdf.set_fill_color(0,0,0); pdf.set_text_color(255,255,255)
            pdf.set_font('Helvetica', 'B', 7); pdf.cell(93, 5, " IDENTIFICAÇÃO POSITIVA", 0, 0, 'L', True)

        if alvo['foto_casa']:
            Image.open(alvo['foto_casa']).save(f"tmp_c_{i}.png")
            pdf.image(f"tmp_c_{i}.png", x=107, y=y_fotos, w=93, h=65)
            pdf.set_xy(107, y_fotos + 60); pdf.set_text_color(255,255,255)
            pdf.cell(93, 5, " PERÍMETRO DE ENTRADA", 0, 0, 'L', True)
        
        # Colunas Inteligência e Logística
        pdf.set_y(y_fotos + 72); curr_y = pdf.get_y()
        
        pdf.draw_section_bullet(10, curr_y)
        pdf.set_xy(14, curr_y); pdf.set_font('Helvetica', 'B', 8); pdf.set_text_color(30, 50, 120)
        pdf.cell(91, 6, 'INTELIGÊNCIA ESTRATÉGICA', 0, 0)
        
        pdf.draw_section_bullet(107, curr_y)
        pdf.set_xy(111, curr_y); pdf.cell(89, 6, 'LOGÍSTICA DE EQUIPE', 0, 1)
        
        pdf.set_font('Helvetica', '', 7); pdf.set_text_color(100, 100, 100)
        pdf.set_x(10); pdf.cell(95, 4, 'ALVO / ENDEREÇO DE CUMPRIMENTO', 0, 0)
        pdf.cell(95, 4, 'VIATURA / EFETIVO OPERACIONAL', 0, 1)
        
        pdf.set_font('Helvetica', 'B', 8); pdf.set_text_color(0, 0, 0); y_desc = pdf.get_y()
        pdf.multi_cell(92, 4, f"ALVO: {alvo['nome'].upper()}\nENDEREÇO: {alvo['enderecos'][0]}", 0, 'L')
        pdf.set_xy(107, y_desc)
        pdf.multi_cell(93, 4, f"VTR: {alvo['viatura'].upper()}\nAGENTES: {alvo['agentes']}", 0, 'L')

        # GPS Section
        pdf.ln(4)
        pdf.set_fill_color(248, 250, 255); pdf.rect(10, pdf.get_y(), 190, 25, 'F')
        qr_p = gerar_qr(end_origem, alvo['enderecos'][0])
        pdf.image(qr_p, x=12, y=pdf.get_y() + 2, w=20)
        pdf.set_xy(35, pdf.get_y() + 4); pdf.set_font('Helvetica', 'B', 8); pdf.set_text_color(30, 50, 120)
        pdf.cell(0, 5, 'ROTA GPS TÁTICA', 0, 1)
        pdf.set_font('Helvetica', '', 7); pdf.set_text_color(100, 100, 100)
        pdf.set_x(35); pdf.multi_cell(0, 4, f"Escaneie o QR Code para abrir no Google Maps.\nORIGEM: {end_origem} -> DESTINO: {alvo['enderecos'][0]}")
        os.remove(qr_p)

    # Nome correto para evitar NameError
    output_pdf = "Dossie_SIG_Jaboticabal.pdf"
    pdf.output(output_pdf)
    with open(output_pdf, "rb") as f:
        st.download_button("📩 BAIXAR DOSSIÊ TÁTICO FINAL", f, file_name=output_pdf)
