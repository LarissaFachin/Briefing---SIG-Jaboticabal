import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import os
from datetime import datetime
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TACTICAL OPS | Intelligence Framework", layout="wide", page_icon="🛡️")

# CSS Customizado
st.markdown("""
    <style>
    .main { background-color: #0b0e14; }
    div[data-testid="stExpander"] { background-color: #161b22; border: 1px solid #30363d; }
    .stButton>button { width: 100%; font-weight: bold; }
    h1, h2, h3 { color: #58a6ff !important; }
    label { color: #8b949e !important; }
    </style>
""", unsafe_allow_html=True)

if 'alvos' not in st.session_state:
    st.session_state.alvos = []

# --- CLASSE DO PDF ---
class TacticalPDF(FPDF):
    def header(self):
        self.set_fill_color(1, 4, 9)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 8)
        self.cell(0, 6, 'DOCUMENTO RESTRITO - USO EXCLUSIVO DAS FORÇAS DE SEGURANÇA', 0, 1, 'C', True)
        self.ln(2)

    def draw_pattern_grid(self, x, y, label):
        self.set_font('Helvetica', 'B', 7)
        self.set_text_color(80, 80, 80)
        self.text(x, y - 2, label)
        for r in range(3):
            for c in range(3):
                self.ellipse(x + (c * 5), y + (r * 5), 0.8, 0.8)

    def footer(self):
        self.set_y(-75)
        self.set_fill_color(245, 245, 245)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(0, 0, 0)
        self.cell(0, 7, 'RELATÓRIO DE CAMPO E APREENSÕES', 1, 1, 'C', True)
        for _ in range(3): self.cell(0, 6, '', 'B', 1)
        
        curr_y = self.get_y() + 5
        for i in range(1, 5): self.draw_pattern_grid(10 + ((i-1)*18), curr_y, f"DISP {i}")
        self.line(85, curr_y-2, 85, curr_y+15)
        self.set_xy(90, curr_y)
        self.set_font('Helvetica', 'B', 7)
        self.cell(0, 4, 'CHECKLIST DISPOSITIVOS (MARCA / IMEI / SN)', 0, 1)
        for _ in range(2):
            self.set_x(90)
            self.cell(0, 6, '', 'B', 1)

        self.set_y(-10)
        self.set_font('Helvetica', 'I', 6)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f'TACTICAL OPS FRAMEWORK | PÁGINA {self.page_no()}', 0, 0, 'C')

def gerar_qr_rota(orig, dest):
    url = f"https://www.google.com/maps/dir/?api=1&origin={urllib.parse.quote(orig)}&destination={urllib.parse.quote(dest)}"
    qr = qrcode.make(url)
    path = f"qr_{hash(dest)}.png"
    qr.save(path)
    return path

# --- INTERFACE ---
st.title("🛡️ TACTICAL OPS FRAMEWORK")

with st.container(border=True):
    st.subheader("📋 Dados da Operação")
    c1, c2 = st.columns([2, 1])
    nome_op = c1.text_input("NOME DA OPERAÇÃO", "OPERAÇÃO CERBERUS")
    unidade_comando = c1.text_input("UNIDADE DE COMANDO", "DIG DISE - ITAPETININGA")
    data_op = c2.text_input("DATA/HORA BRIEFING", "27/03/2026 04:00")
    h_hora = c2.text_input("H-HORA (EXECUÇÃO)", "06:00")
    end_origem = st.text_input("📍 PONTO DE CONCENTRAÇÃO (GPS ORIGEM)", "Sede da Delegacia")

st.divider()
if st.button("➕ ADICIONAR NOVO ALVO"):
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
        alvo['vulgo'] = col_b.text_input("Vulgo", value=alvo['vulgo'], key=f"v_{idx}")
        alvo['mandado'] = col_c.selectbox("Mandado", ["BUSCA E APREENSÃO", "PRISÃO PREVENTIVA", "TEMPORÁRIA"], key=f"m_{idx}")
        
        alvo['viatura'] = st.text_input("Viatura Utilizada (Prefixo/Modelo)", value=alvo['viatura'], key=f"via_{idx}")

        f1, f2 = st.columns(2)
        alvo['foto_alvo'] = f1.file_uploader("📸 Retrato do Suspeito", key=f"fa_{idx}")
        alvo['foto_casa'] = f2.file_uploader("🏠 Fachada do Local", key=f"fc_{idx}")

        st.write("**📍 Endereços**")
        for e_i, end in enumerate(alvo['enderecos']):
            alvo['enderecos'][e_i] = st.text_input(f"Endereço {e_i+1}", value=end, key=f"e_{idx}_{e_i}")
        if st.button("➕ Novo Endereço", key=f"be_{idx}"):
            alvo['enderecos'].append(''); st.rerun()

        st.write("**👥 Equipe**")
        num_ag = len(alvo['agentes'])
        for r in range((num_ag // 3) + 1):
            cols = st.columns(3)
            for c in range(3):
                ag_idx = r * 3 + c
                if ag_idx < num_ag:
                    alvo['agentes'][ag_idx] = cols[c].text_input(f"Agente {ag_idx+1}", value=alvo['agentes'][ag_idx], key=f"a_{idx}_{ag_idx}")
        
        c_btn1, c_btn2, _ = st.columns([1, 1, 2])
        if c_btn1.button("➕ Adicionar Policial", key=f"ba_{idx}"):
            alvo['agentes'].append(''); st.rerun()
        if c_btn2.button("🗑️ Remover Alvo", key=f"rem_{idx}"):
            st.session_state.alvos.pop(idx); st.rerun()

if st.session_state.alvos and st.button("🚀 GERAR PDF"):
    pdf = TacticalPDF()
    for i_alvo, alvo in enumerate(st.session_state.alvos):
        pdf.add_page()
        
        # Dados da Operação apenas na primeira página
        if i_alvo == 0:
            pdf.set_font('Helvetica', 'B', 18); pdf.set_text_color(0, 30, 80)
            pdf.cell(0, 10, nome_op.upper(), 0, 1)
            pdf.set_font('Helvetica', 'B', 10); pdf.cell(0, 5, f"UNIDADE: {unidade_comando.upper()}", 0, 1)
            pdf.ln(2)
            pdf.set_fill_color(240, 240, 240); pdf.set_font('Helvetica', 'B', 8); pdf.set_text_color(0,0,0)
            pdf.cell(63, 8, f" ORIGEM: {end_origem[:30]}", 1, 0, 'L', True)
            pdf.cell(63, 8, f" BRIEFING: {data_op}", 1, 0, 'L', True)
            pdf.cell(64, 8, f" H-HORA: {h_hora}", 1, 1, 'L', True)
            pdf.ln(4)

        # Cabeçalho do Alvo (Ajustado para não cortar texto)
        pdf.set_fill_color(0, 35, 90); pdf.set_text_color(255, 255, 255); pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(125, 10, f" ALVO: {alvo['nome'].upper()}", 0, 0, 'L', True)
        pdf.cell(65, 10, alvo['mandado'], 0, 1, 'R', True) # Largura maior (65) e alinhado à direita
        pdf.set_text_color(0,0,0); pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(0, 6, f"VULGO: {alvo['vulgo']}", 0, 1)

        # Fotos (Com nomes temporários únicos para não repetir)
        y_f = pdf.get_y() + 2
        if alvo['foto_alvo']:
            tmp_a = f"tmp_alvo_{i_alvo}.png"
            Image.open(alvo['foto_alvo']).save(tmp_a)
            pdf.image(tmp_a, x=10, y=y_f, w=92, h=62)
        if alvo['foto_casa']:
            tmp_c = f"tmp_casa_{i_alvo}.png"
            Image.open(alvo['foto_casa']).save(tmp_c)
            pdf.image(tmp_c, x=105, y=y_f, w=95, h=62)
        
        pdf.set_y(y_f + 65)
        pdf.set_font('Helvetica', 'B', 10); pdf.cell(0, 8, "ROTAS GPS TÁTICAS", 'B', 1); pdf.ln(2)
        pdf.set_font('Helvetica', '', 8)
        for end in alvo['enderecos']:
            if end.strip():
                q_p = gerar_qr_rota(end_origem, end); c_y = pdf.get_y()
                pdf.image(q_p, x=10, y=c_y, w=22)
                pdf.set_xy(35, c_y + 4); pdf.multi_cell(0, 4, f"DESTINO: {end}\nSAÍDA: {end_origem}")
                pdf.set_y(c_y + 25); os.remove(q_p)

        # Logística da Equipe
        pdf.set_font('Helvetica', 'B', 9); pdf.cell(0, 8, "LOGÍSTICA E EQUIPE:", 0, 1)
        pdf.set_font('Helvetica', 'B', 8); pdf.cell(0, 5, f"VIATURA: {alvo['viatura'].upper()}", 0, 1)
        pdf.set_font('Helvetica', '', 8)
        ag_str = " | ".join([a for a in alvo['agentes'] if a.strip()])
        pdf.multi_cell(0, 6, f"EFETIVO: {ag_str}", 1)

    output = "Tactical_Briefing.pdf"
    pdf.output(output)
    with open(output, "rb") as f:
        st.download_button("📩 BAIXAR BRIEFING COMPLETO", f, file_name=output)
