import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import os
from datetime import datetime
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TACTICAL OPS | Intelligence Framework", layout="wide", page_icon="🛡️")

# CSS para Visual Profissional (Dark Dossier Style)
st.markdown("""
    <style>
    .main { background-color: #0b0e14; }
    div[data-testid="stExpander"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 4px;
        font-weight: bold;
        text-transform: uppercase;
    }
    .dossier-card {
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f6feb;
        background-color: #0d1117;
        margin-bottom: 20px;
    }
    h1, h2, h3 { color: #58a6ff !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    label { color: #8b949e !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

if 'alvos' not in st.session_state:
    st.session_state.alvos = []

# --- CLASSE DO PDF CUSTOMIZADO ---
class TacticalPDF(FPDF):
    def header(self):
        # Tarja Superior
        self.set_fill_color(1, 4, 9)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 8)
        self.cell(0, 6, 'DOCUMENTO RESTRITO - USO EXCLUSIVO DAS FORÇAS DE SEGURANÇA', 0, 1, 'C', True)
        self.ln(4)

    def draw_pattern_grid(self, x, y, label):
        self.set_font('Helvetica', 'B', 7)
        self.set_text_color(80, 80, 80)
        self.text(x, y - 2, label)
        self.set_draw_color(150, 150, 150)
        for r in range(3):
            for c in range(3):
                self.ellipse(x + (c * 5), y + (r * 5), 0.8, 0.8)

    def footer(self):
        self.set_y(-75)
        self.set_draw_color(50, 50, 50)
        self.set_fill_color(245, 245, 245)
        self.set_font('Helvetica', 'B', 9)
        self.cell(0, 7, 'RELATÓRIO DE CAMPO E APREENSÕES', 1, 1, 'C', True)
        
        # Linhas de Ocorrência
        for _ in range(3): self.cell(0, 6, '', 'B', 1)
        
        # Checklist e Patterns (Estilo Anexo)
        curr_y = self.get_y() + 5
        for i in range(1, 5):
            self.draw_pattern_grid(10 + ((i-1)*18), curr_y, f"DISP {i}")
            
        self.line(85, curr_y-2, 85, curr_y+15) # Divisória
        
        self.set_xy(90, curr_y)
        self.set_font('Helvetica', 'B', 7)
        self.cell(0, 4, 'CHECKLIST DISPOSITIVOS (MARCA / IMEI / SN)', 0, 1)
        for _ in range(2):
            self.set_x(90)
            self.cell(0, 6, '', 'B', 1)

        self.set_y(-10)
        self.set_font('Helvetica', 'I', 6)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f'ID: {datetime.now().strftime("%Y%m%d%H%M")} | TACTICAL OPS FRAMEWORK | PÁGINA {self.page_no()}', 0, 0, 'C')

# --- FUNÇÕES DE APOIO ---
def gerar_qr_rota(orig, dest):
    url = f"https://www.google.com/maps/dir/?api=1&origin={urllib.parse.quote(orig)}&destination={urllib.parse.quote(dest)}"
    qr = qrcode.make(url)
    path = f"qr_{hash(dest)}.png"
    qr.save(path)
    return path

# --- INTERFACE ---
st.title("🛡️ TACTICAL OPS FRAMEWORK")
st.subheader("Módulo de Briefing e Inteligência Operacional")

# 1. DADOS DA OPERAÇÃO
with st.container(border=True):
    col1, col2 = st.columns([2, 1])
    with col1:
        nome_op = st.text_input("NOME DA OPERAÇÃO", "OPERAÇÃO CERBERUS")
        unidade_comando = st.text_input("DELEGACIA / UNIDADE DE COMANDO", "DIG DISE - 1ª DELEGACIA DE INVESTIGAÇÕES")
    with col2:
        data_op = st.text_input("DATA/HORA BRIEFING", "27/03/2026 04:00")
        h_hora = st.text_input("H-HORA (EXECUÇÃO)", "06:00")
    
    end_origem = st.text_input("📍 PONTO DE CONCENTRAÇÃO (Endereço para Rota GPS)", "Rua da Delegacia, 100")

# 2. GESTÃO DE ALVOS (DOSSIÊS)
st.divider()
c_btn1, c_btn2, _ = st.columns([1, 1, 2])
if c_btn1.button("➕ ADICIONAR ALVO", type="primary"):
    st.session_state.alvos.append({
        'nome': '', 'vulgo': '', 'mandado': 'PRISÃO PREVENTIVA',
        'enderecos': [''], 'agentes': [''], 'obs': '',
        'foto_alvo': None, 'foto_casa': None
    })

for idx, alvo in enumerate(st.session_state.alvos):
    with st.container(border=True):
        st.markdown(f"### 🎯 DOSSIÊ DO ALVO #{idx+1}")
        
        c1, c2, c3 = st.columns([2, 1, 1])
        alvo['nome'] = c1.text_input("Nome Completo", value=alvo['nome'], key=f"n_{idx}")
        alvo['vulgo'] = c2.text_input("Vulgo", value=alvo['vulgo'], key=f"v_{idx}")
        alvo['mandado'] = c3.selectbox("Mandado", ["PRISÃO PREVENTIVA", "BUSCA E APREENSÃO", "TEMPORÁRIA"], key=f"m_{idx}")

        # Fotos
        f1, f2 = st.columns(2)
        alvo['foto_alvo'] = f1.file_uploader("📸 Retrato do Suspeito", key=f"fa_{idx}")
        alvo['foto_casa'] = f2.file_uploader("🏠 Fachada do Local", key=f"fc_{idx}")

        # Endereços
        st.write("**📍 Endereços de Cumprimento**")
        for e_idx, end in enumerate(alvo['enderecos']):
            alvo['enderecos'][e_idx] = st.text_input(f"Local {e_idx+1}", value=end, key=f"e_{idx}_{e_idx}")
        
        if st.button("➕ Adicionar Endereço", key=f"be_{idx}"):
            alvo['enderecos'].append('')
            st.rerun()

        # EQUIPE EM LINHA (3 AGENTES POR LINHA)
        st.write("**👥 Equipe Escalada (Agentes)**")
        num_agentes = len(alvo['agentes'])
        rows = (num_agentes // 3) + 1
        
        for r in range(rows):
            cols = st.columns(3)
            for c in range(3):
                idx_age = r * 3 + c
                if idx_age < num_agentes:
                    alvo['agentes'][idx_age] = cols[c].text_input(f"Agente {idx_age+1}", value=alvo['agentes'][idx_age], key=f"a_{idx}_{idx_age}")
        
        c_age1, c_age2, _ = st.columns([1, 1, 2])
        if c_age1.button("➕ Adicionar Policial", key=f"ba_{idx}"):
            alvo['agentes'].append('')
            st.rerun()
        if c_age2.button("🗑️ Remover Alvo", key=f"rem_{idx}"):
            st.session_state.alvos.pop(idx)
            st.rerun()

# 3. GERAÇÃO DO PDF
if st.session_state.alvos:
    st.divider()
    if st.button("🚀 FINALIZAR E GERAR PDF DE INTELIGÊNCIA"):
        pdf = TacticalPDF()
        for alvo in st.session_state.alvos:
            pdf.add_page()
            
            # Cabeçalho Detalhado
            pdf.set_font('Helvetica', 'B', 18)
            pdf.set_text_color(0, 30, 80)
            pdf.cell(0, 10, nome_op.upper(), 0, 1)
            pdf.set_font('Helvetica', 'B', 10)
            pdf.cell(0, 5, f"UNIDADE DE COMANDO: {unidade_comando.upper()}", 0, 1)
            pdf.ln(2)

            # Barra de Dados Fixos
            pdf.set_fill_color(240, 240, 240)
            pdf.set_font('Helvetica', 'B', 8)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(63, 8, f" ORIGEM: {end_origem[:30]}", 1, 0, 'L', True)
            pdf.cell(63, 8, f" BRIEFING: {data_op}", 1, 0, 'L', True)
            pdf.cell(64, 8, f" H-HORA: {h_hora}", 1, 1, 'L', True)
            pdf.ln(5)

            # Bloco Alvo
            pdf.set_fill_color(0, 35, 90)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(145, 10, f" ALVO: {alvo['nome'].upper()}", 0, 0, 'L', True)
            pdf.cell(45, 10, alvo['mandado'], 0, 1, 'C', True)
            pdf.set_text_color(0,0,0)
            pdf.set_font('Helvetica', 'B', 9)
            pdf.cell(0, 6, f"VULGO: {alvo['vulgo']}", 0, 1)

            # Fotos
            y_fotos = pdf.get_y() + 2
            if alvo['foto_alvo']:
                Image.open(alvo['foto_alvo']).save("tmp_a.png")
                pdf.image("tmp_a.png", x=10, y=y_fotos, w=92, h=62)
            if alvo['foto_casa']:
                Image.open(alvo['foto_casa']).save("tmp_c.png")
                pdf.image("tmp_c.png", x=105, y=y_fotos, w=95, h=62)
            
            pdf.set_y(y_fotos + 65)

            # Rotas e Inteligência
            pdf.set_font('Helvetica', 'B', 10)
            pdf.cell(0, 8, "COORDENADAS E ROTAS GPS TÁTICAS", 'B', 1)
            pdf.ln(2)
            for end in alvo['enderecos']:
                if end.strip():
                    q_path = gerar_qr_rota(end_origem, end)
                    cur_y = pdf.get_y()
                    pdf.image(q_path, x=10, y=cur_y, w=22)
                    pdf.set_xy(35, cur_y + 4)
                    pdf.set_font('Helvetica', 'B', 8)
                    pdf.multi_cell(0, 4, f"ROTA ATIVA:\nDE: {end_origem}\nPARA: {end}")
                    pdf.set_y(cur_y + 25)
                    os.remove(q_path)

            # Agentes Escalados
            pdf.set_font('Helvetica', 'B', 9)
            pdf.cell(0, 8, "EQUIPE TÁTICA ESCALADA:", 0, 1)
            pdf.set_font('Helvetica', '', 8)
            agentes_formatados = " | ".join([a for a in alvo['agentes'] if a.strip()])
            pdf.multi_cell(0, 6, agentes_formatados, 1)

        pdf_file = "TACTICAL_OPS_BRIEFING.pdf"
        pdf.output(pdf_file)
        with open(pdf_file, "rb") as f:
            st.download_button("📩 BAIXAR DOSSIÊ COMPLETO", f, file_name=pdf_file)
