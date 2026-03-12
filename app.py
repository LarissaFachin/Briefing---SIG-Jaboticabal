import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import os
from datetime import datetime
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TACTICAL OPS | SIG JABOTICABAL", layout="wide", page_icon="🛡️")

# --- CSS AVANÇADO PARA BOTÕES PROFISSIONAIS ---
st.markdown("""
    <style>
    /* Fundo e Container Principal */
    .main { background-color: #0b0e14; }
    
    /* Estilização dos Botões de ADICIONAR (Verde) */
    div.stButton > button:first-child[key*="ba_"], 
    div.stButton > button:first-child[key*="be_"],
    div.stButton > button:first-child[key*="add_alvo"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
        transition: 0.3s !important;
    }
    div.stButton > button:hover[key*="ba_"], 
    div.stButton > button:hover[key*="be_"] {
        background-color: #218838 !important;
        transform: scale(1.02);
    }

    /* Estilização dos Botões de REMOVER (Vermelho) */
    div.stButton > button:first-child[key*="rem_"] {
        background-color: #dc3545 !important;
        color: white !important;
        border: none !important;
    }
    div.stButton > button:hover[key*="rem_"] {
        background-color: #c82333 !important;
    }

    /* Estilização do Botão de GERAR DOSSIÊ (Azul Tático) */
    div.stButton > button:first-child[key*="gerar_final"] {
        background-color: #0056b3 !important;
        color: white !important;
        font-size: 1.2rem !important;
        height: 3em !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    }

    /* Melhoria nos inputs e expanders */
    div[data-testid="stExpander"] { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 8px; 
    }
    label { color: #8b949e !important; font-weight: bold !important; font-size: 0.8rem !important; }
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
        self.set_text_color(120, 120, 120)
        self.text(x, y - 2, label)
        for r in range(3):
            for c in range(3):
                self.ellipse(x + (c * 5), y + (r * 5), 0.8, 0.8)

    def footer(self):
        self.set_y(-75)
        self.set_draw_color(200, 200, 200)
        self.set_fill_color(248, 248, 248)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(0, 0, 0)
        self.cell(0, 7, 'RELATÓRIO DE OCORRÊNCIA E APREENSÕES DE CAMPO', 'B', 1, 'C', True)
        for _ in range(3): self.cell(0, 6, '', 'B', 1)
        
        curr_y = self.get_y() + 5
        for i in range(1, 5): self.draw_pattern_grid(10 + ((i-1)*18), curr_y, f"DISP {i}")
        self.line(85, curr_y-2, 85, curr_y+15)
        self.set_xy(90, curr_y)
        self.set_font('Helvetica', 'B', 7)
        self.cell(0, 4, 'CHECKLIST DISPOSITIVOS (IMEI/SN)', 0, 1)
        for _ in range(2):
            self.set_x(90)
            self.cell(0, 6, '', 'B', 1)

        self.set_y(-10)
        self.set_font('Helvetica', 'I', 6)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'TACTICAL OPS SYSTEM | SIG JABOTICABAL | PÁGINA {self.page_no()}', 0, 0, 'C')

def gerar_qr_rota(orig, dest):
    url = f"https://www.google.com/maps/dir/?api=1&origin={urllib.parse.quote(orig)}&destination={urllib.parse.quote(dest)}"
    qr = qrcode.make(url)
    path = f"qr_{hash(dest)}.png"
    qr.save(path)
    return path

# --- INTERFACE PRINCIPAL ---
st.title("🛡️ TACTICAL OPS FRAMEWORK")

with st.container(border=True):
    st.subheader("📋 Configuração da Missão")
    c1, c2 = st.columns([2, 1])
    nome_op = c1.text_input("NOME DA OPERAÇÃO", "OPERAÇÃO")
    unidade = c1.text_input("UNIDADE DE COMANDO", "SIG JABOTICABAL")
    data_op = c2.text_input("DATA/HORA BRIEFING", "27/01/2026 03:30")
    h_hora = c2.text_input("H-HORA (EXECUÇÃO)", "06:00")
    end_origem = st.text_input("📍 PONTO DE PARTIDA (GPS)", "Sede da Unidade")

st.divider()

# Botão de Adicionar Alvo com ID específico para o CSS
if st.button("➕ ADICIONAR NOVO ALVO TÁTICO", key="add_alvo"):
    st.session_state.alvos.append({
        'nome': '', 'vulgo': '', 'mandado': 'BUSCA E APREENSÃO',
        'enderecos': [''], 'agentes': [''], 'viatura': '',
        'foto_alvo': None, 'foto_casa': None
    })

for idx, alvo in enumerate(st.session_state.alvos):
    with st.container(border=True):
        st.markdown(f"### 🎯 ALVO #{idx+1}")
        
        # Nome e Mandado
        col_a, col_b, col_c = st.columns([2, 1, 1])
        alvo['nome'] = col_a.text_input("Nome Completo", value=alvo['nome'], key=f"n_{idx}")
        alvo['vulgo'] = col_b.text_input("Vulgo", value=alvo['vulgo'], key=f"v_{idx}")
        alvo['mandado'] = col_c.selectbox("Mandado", ["BUSCA E APREENSÃO", "PRISÃO PREVENTIVA", "TEMPORÁRIA"], key=f"m_{idx}")
        
        # Logística (Viatura e Agentes)
        st.markdown("---")
        st.write("👥 **Logística da Equipe**")
        alvo['viatura'] = st.text_input("Viatura (Prefixo/Modelo)", value=alvo['viatura'], key=f"via_{idx}")
        
        num_ag = len(alvo['agentes'])
        cols_ag = st.columns(3)
        for i_ag in range(num_ag):
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

        # Botão de Remover
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Remover Alvo do Plano", key=f"rem_{idx}"):
            st.session_state.alvos.pop(idx); st.rerun()

# Botão Final
if st.session_state.alvos:
    st.divider()
    if st.button("🛰️ GERAR DOSSIÊ TÁTICO FINAL", key="gerar_final"):
        pdf = TacticalPDF()
        for i, alvo in enumerate(st.session_state.alvos):
            pdf.add_page()
            
            if i == 0:
                pdf.set_font('Helvetica', 'B', 18); pdf.set_text_color(0, 30, 80)
                pdf.cell(0, 10, nome_op.upper(), 0, 1)
                pdf.set_font('Helvetica', 'B', 10); pdf.cell(0, 5, f"UNIDADE: {unidade.upper()}", 0, 1)
                pdf.ln(2)
                pdf.set_fill_color(240, 240, 240); pdf.set_font('Helvetica', 'B', 8); pdf.set_text_color(0,0,0)
                pdf.cell(63, 8, f" ORIGEM: {end_origem[:30]}", 1, 0, 'L', True)
                pdf.cell(63, 8, f" BRIEFING: {data_op}", 1, 0, 'L', True)
                pdf.cell(64, 8, f" H-HORA: {h_hora}", 1, 1, 'L', True)
                pdf.ln(4)

            pdf.set_fill_color(0, 35, 90); pdf.set_text_color(255, 255, 255); pdf.set_font('Helvetica', 'B', 12)
            pdf.cell(125, 10, f" ALVO: {alvo['nome'].upper()}", 0, 0, 'L', True)
            pdf.cell(65, 10, alvo['mandado'], 0, 1, 'R', True)
            
            pdf.set_text_color(0,0,0); pdf.set_font('Helvetica', 'B', 9)
            pdf.cell(0, 6, f"VULGO: {alvo['vulgo']}", 0, 1)

            y_fotos = pdf.get_y() + 2
            if alvo['foto_alvo']:
                path_a = f"tmp_alvo_{i}.png"; Image.open(alvo['foto_alvo']).save(path_a)
                pdf.image(path_a, x=10, y=y_fotos, w=92, h=62)
                pdf.set_xy(10, y_fotos + 57); pdf.set_fill_color(0,0,0); pdf.set_text_color(255,255,255)
                pdf.cell(92, 5, " IDENTIFICAÇÃO POSITIVA", 0, 0, 'L', True)
            if alvo['foto_casa']:
                path_c = f"tmp_casa_{i}.png"; Image.open(alvo['foto_casa']).save(path_c)
                pdf.image(path_c, x=105, y=y_fotos, w=95, h=62)
                pdf.set_xy(105, y_fotos + 57); pdf.set_text_color(255,255,255)
                pdf.cell(95, 5, " PERÍMETRO DE ENTRADA", 0, 1, 'L', True)
            
            pdf.set_y(y_fotos + 68); pdf.set_text_color(0,0,0)
            
            # Logística
            pdf.set_font('Helvetica', 'B', 10); pdf.cell(0, 8, "LOGÍSTICA E EQUIPE", 'B', 1); pdf.ln(2)
            pdf.set_font('Helvetica', 'B', 9); pdf.cell(22, 6, "VIATURA: ", 0, 0)
            pdf.set_font('Helvetica', '', 9); pdf.cell(0, 6, alvo['viatura'].upper(), 0, 1)
            pdf.set_font('Helvetica', 'B', 9); pdf.cell(22, 6, "EFETIVO: ", 0, 0)
            pdf.set_font('Helvetica', '', 9)
            pdf.multi_cell(0, 6, " | ".join([a for a in alvo['agentes'] if a.strip()]))
            pdf.ln(2)

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

        pdf_out = "Dossie_SIG_Jaboticabal.pdf"
        pdf.output(pdf_out)
        with open(pdf_out, "rb") as f:
            st.download_button("📩 CLIQUE AQUI PARA BAIXAR O PDF", f, file_name=pdf_out)
