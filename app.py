import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import os
from datetime import datetime
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA UI ---
st.set_page_config(page_title="TACTICAL OPS FRAMEWORK", layout="wide", page_icon="🛡️")

# CSS para interface profissional
st.markdown("""
    <style>
    .main { background-color: #0d1117; }
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Inter', sans-serif; }
    div[data-testid="stExpander"], div.stVerticalBlock > div[style*="border"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }
    div.stButton > button[key="btn_add_alvo"] { background-color: #238636 !important; color: white !important; width: 100% !important; font-weight: bold; }
    div.stButton > button[key="btn_gerar_pdf"] { background-color: #1f6feb !important; color: white !important; font-size: 20px !important; font-weight: 900 !important; width: 100% !important; height: 60px !important; }
    label { color: #8b949e !important; font-size: 12px !important; font-weight: 600 !important; }
    </style>
""", unsafe_allow_html=True)

if 'alvos' not in st.session_state:
    st.session_state.alvos = []

# --- CLASSE DO PDF PROFISSIONAL ---
class TacticalPDF(FPDF):
    def header(self):
        # Tarja Superior Restrita
        self.set_fill_color(0, 0, 0)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 8)
        self.cell(0, 6, 'SIGILOSO  -  DOCUMENTO DE INTELIGÊNCIA  -  RESTRITO', 0, 1, 'C', True)
        self.ln(5)

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
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, 'RELATÓRIO DE OCORRÊNCIA E APREENSÕES DE CAMPO', 'B', 1, 'C', True)
        for _ in range(3): self.cell(0, 6, '', 'B', 1)
        
        curr_y = self.get_y() + 5
        for i in range(1, 5): self.draw_pattern_grid(15 + ((i-1)*18), curr_y, f"DISP {i}")
        self.line(88, curr_y-2, 88, curr_y+15)
        self.set_xy(92, curr_y)
        self.set_font('Helvetica', 'B', 7)
        self.cell(0, 4, 'CHECKLIST DISPOSITIVOS (IMEI/SN)', 0, 1)
        for _ in range(2):
            self.set_x(92)
            self.cell(0, 7, '', 'B', 1)

        self.set_y(-10)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f'GERADO EM: {datetime.now().strftime("%d/%m/%Y %H:%M")} | SIG JABOTICABAL | PÁGINA {self.page_no()}', 0, 0, 'C')

def gerar_qr_rota(orig, dest):
    url = f"https://www.google.com/maps/dir/?api=1&origin={urllib.parse.quote(orig)}&destination={urllib.parse.quote(dest)}"
    qr = qrcode.make(url)
    path = f"qr_{hash(dest)}.png"
    qr.save(path)
    return path

# --- INTERFACE ---
st.title("🛡️ TACTICAL OPS FRAMEWORK")

with st.container(border=True):
    st.subheader("📋 Configuração da Missão")
    c1, c2 = st.columns([2, 1])
    nome_op = c1.text_input("NOME DA OPERAÇÃO", "OPERAÇÃO")
    unidade = c1.text_input("UNIDADE DE COMANDO", "SIG JABOTICABAL")
    data_op = c2.text_input("DATA/HORA BRIEFING", "27/01/2026 03:30")
    h_hora = c2.text_input("H-HORA (EXECUÇÃO)", "06:00")
    end_origem = st.text_input("📍 PONTO DE PARTIDA (ENDEREÇO COMPLETO)", "Praça Pedro Dória, s/n, Centro, Jaboticabal - SP, CEP: 14870-000")

st.markdown("<br>", unsafe_allow_html=True)

if st.button("➕ ADICIONAR NOVO ALVO TÁTICO", key="btn_add_alvo"):
    st.session_state.alvos.append({
        'nome': '', 'vulgo': '', 'mandado': 'BUSCA E APREENSÃO',
        'enderecos': [''], 'agentes': [''], 'viatura': '',
        'foto_alvo': None, 'foto_casa': None
    })

for idx, alvo in enumerate(st.session_state.alvos):
    with st.container(border=True):
        st.markdown(f"### 🎯 ALVO #{idx+1}")
        col_a, col_b, col_c = st.columns([2, 1, 1])
        alvo['nome'] = col_a.text_input("Nome Completo", value=alvo['nome'], key=f"n_{idx}")
        alvo['vulgo'] = col_b.text_input("Vulgo / Apelido", value=alvo['vulgo'], key=f"v_{idx}")
        alvo['mandado'] = col_c.selectbox("Tipo de Mandado", ["BUSCA E APREENSÃO", "PRISÃO PREVENTIVA", "TEMPORÁRIA"], key=f"m_{idx}")
        
        st.markdown("---")
        st.write("👥 **Logística e Equipe Escalada**")
        alvo['viatura'] = st.text_input("Viatura (Prefixo/Modelo)", value=alvo['viatura'], key=f"via_{idx}")
        
        num_ag = len(alvo['agentes'])
        cols_ag = st.columns(3)
        for i_ag in range(num_ag):
            alvo['agentes'][i_ag] = cols_ag[i_ag % 3].text_input(f"Agente {i_ag+1}", value=alvo['agentes'][i_ag], key=f"a_{idx}_{i_ag}")
        
        if st.button("➕ Adicionar Policial", key=f"ba_{idx}"):
            alvo['agentes'].append(''); st.rerun()

        st.markdown("---")
        f1, f2 = st.columns(2)
        alvo['foto_alvo'] = f1.file_uploader("📸 Retrato do Alvo", key=f"fa_{idx}")
        alvo['foto_casa'] = f2.file_uploader("🏠 Fachada da Residência", key=f"fc_{idx}")

        st.write("📍 **Localidades e Alvos GPS**")
        for e_i, end in enumerate(alvo['enderecos']):
            alvo['enderecos'][e_i] = st.text_input(f"Endereço {e_i+1}", value=end, key=f"e_{idx}_{e_i}")
        
        if st.button("➕ Adicionar Endereço", key=f"be_{idx}"):
            alvo['enderecos'].append(''); st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Remover Alvo do Plano", key=f"rem_{idx}"):
            st.session_state.alvos.pop(idx); st.rerun()

# --- GERAÇÃO DO PDF ---
if st.session_state.alvos:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🛰️ GERAR DOSSIÊ TÁTICO FINAL", key="btn_gerar_pdf"):
        pdf = TacticalPDF()
        for i, alvo in enumerate(st.session_state.alvos):
            pdf.add_page()
            
            # 1. TÍTULO OPERAÇÃO (GRANDE E CENTRALIZADO)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Helvetica', 'B', 24)
            pdf.cell(0, 15, nome_op.upper(), 0, 1, 'C')
            
            # Comando Operacional
            pdf.set_font('Helvetica', 'B', 10)
            pdf.cell(0, 5, f"COMANDO: {unidade.upper()}", 0, 1, 'R')
            pdf.ln(5)

            # 2. BOX DE DADOS TÉCNICOS (CORREÇÃO DE TEXTO LONGO)
            pdf.set_fill_color(245, 245, 245)
            pdf.set_draw_color(200, 200, 200)
            pdf.set_font('Helvetica', 'B', 8)
            
            # Captura a posição para desenhar o box
            x_start = pdf.get_x()
            y_start = pdf.get_y()
            
            # Dados fixos
            pdf.cell(47, 10, f" BRIEFING: {data_op}", 1, 0, 'L', True)
            pdf.cell(47, 10, f" H-HORA: {h_hora}", 1, 0, 'L', True)
            pdf.cell(46, 10, f" MISSÃO: #{datetime.now().strftime('%M%S')}", 1, 0, 'L', True)
            
            # Endereço (Multi-cell para não cortar)
            pdf.set_xy(x_start + 140, y_start)
            pdf.multi_cell(50, 5, f" LOCAL: {end_origem}", 1, 'L', True)
            
            pdf.set_y(y_start + 15)

            # 3. BARRA DE MANDADO (CENTRALIZADA AZUL)
            pdf.set_fill_color(0, 31, 63) # Navy Blue
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Helvetica', 'B', 13)
            pdf.cell(0, 12, alvo['mandado'].upper(), 0, 1, 'C', True)
            
            # 4. ALVO (FORA DA BARRA, NEGRITO)
            pdf.ln(3)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font('Helvetica', 'B', 16)
            pdf.cell(0, 10, f"ALVO: {alvo['nome'].upper()}", 0, 1, 'L')
            
            pdf.set_font('Helvetica', 'B', 10)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(0, 6, f"VULGO: {alvo['vulgo'].upper()}", 0, 1)

            # Fotos
            y_fotos = pdf.get_y() + 5
            if alvo['foto_alvo']:
                path_a = f"tmp_alvo_{i}.png"
                Image.open(alvo['foto_alvo']).save(path_a)
                pdf.image(path_a, x=10, y=y_fotos, w=92, h=62)
                pdf.set_xy(10, y_fotos + 58)
                pdf.set_fill_color(0,0,0)
                pdf.set_text_color(255,255,255)
                pdf.set_font('Helvetica', 'B', 8)
                pdf.cell(92, 4, " IDENTIFICAÇÃO POSITIVA", 0, 0, 'L', True)
            
            if alvo['foto_casa']:
                path_c = f"tmp_casa_{i}.png"
                Image.open(alvo['foto_casa']).save(path_c)
                pdf.image(path_c, x=105, y=y_fotos, w=95, h=62)
                pdf.set_xy(105, y_fotos + 58)
                pdf.set_text_color(255,255,255)
                pdf.cell(95, 4, " PERÍMETRO DE ENTRADA", 0, 1, 'L', True)
            
            pdf.set_y(y_fotos + 70)
            pdf.set_text_color(0, 0, 0)
            
            # 5. LOGÍSTICA
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(0, 8, "LOGÍSTICA E EQUIPE OPERACIONAL", 'B', 1); pdf.ln(2)
            
            pdf.set_font('Helvetica', 'B', 9)
            pdf.cell(25, 6, "VIATURA:", 0, 0)
            pdf.set_font('Helvetica', '', 9)
            pdf.cell(0, 6, alvo['viatura'].upper() if alvo['viatura'] else "NÃO INFORMADA", 0, 1)
            
            pdf.set_font('Helvetica', 'B', 9)
            pdf.cell(25, 6, "EFETIVO:", 0, 0)
            pdf.set_font('Helvetica', '', 9)
            agentes_str = " | ".join([a for a in alvo['agentes'] if a.strip()])
            pdf.multi_cell(0, 6, agentes_str if agentes_str else "AGUARDANDO ESCALA")
            pdf.ln(3)

            # 6. ROTAS GPS
            pdf.set_font('Helvetica', 'B', 11)
            pdf.cell(0, 8, "ROTAS GPS TÁTICAS", 'B', 1); pdf.ln(2)
            
            for end in alvo['enderecos']:
                if end.strip():
                    qr_p = gerar_qr_rota(end_origem, end)
                    curr_y = pdf.get_y()
                    if curr_y > 185: pdf.add_page(); curr_y = 20
                    pdf.image(qr_p, x=10, y=curr_y, w=22)
                    pdf.set_xy(35, curr_y + 4)
                    pdf.set_font('Helvetica', 'B', 8)
                    pdf.multi_cell(0, 4, f"DESTINO: {end.upper()}\nSAÍDA: {end_origem.upper()}")
                    pdf.set_y(curr_y + 25); os.remove(qr_p)

        pdf_output = "Dossie_Tactical_SIG.pdf"
        pdf.output(pdf_output)
        with open(pdf_output, "rb") as f:
            st.download_button("📩 BAIXAR DOSSIÊ TÁTICO FINAL", f, file_name=pdf_output)
