import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import io

# --- CONFIGURAÇÃO DA PÁGINA (ESTILO DARK) ---
st.set_page_config(layout="wide", page_title="OPS - Painel Tático")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { background-color: #2e5cb8; color: white; border-radius: 5px; width: 100%; }
    .address-card { border: 1px solid #2e5cb8; padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: #1a1c23; }
    </style>
    """, unsafe_allow_html=True)

# --- CLASSE PARA GERAR O PDF IGUAL AO MODELO ---
class BriefingPDF(FPDF):
    def header_op(self, op_name, mission_id, meeting_pt, briefing_dt, h_hora):
        self.set_fill_color(0, 0, 0)
        self.rect(10, 10, 190, 8, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", 'B', 8)
        self.cell(190, 8, "S I G I L O S O   -   D O C U M E N T O   D E   I N T E L I G Ê N C I A   -   R E S T R I T O", 0, 1, 'C')
        
        self.set_text_color(0, 0, 0)
        self.set_font("Arial", 'B', 18)
        self.ln(2)
        self.cell(140, 10, op_name.upper(), 0, 0)
        
        # ID Missão e Comando
        self.set_font("Arial", 'B', 8)
        self.set_xy(160, 20)
        self.cell(40, 10, "DEL POL SMA", 1, 1, 'C')

        # Faixa de dados da missão
        self.set_xy(10, 35)
        self.set_font("Arial", 'B', 6)
        # Grid layout (simplificado)
        self.cell(50, 10, f"PONTO: {meeting_pt}", 1)
        self.cell(50, 10, f"DATA: {briefing_dt}", 1)
        self.cell(50, 10, f"H-HORA: {h_hora}", 1)
        self.cell(40, 10, f"ID: {mission_id}", 1)
        self.ln(15)

    def draw_target_info(self, alvo_nome, vulgo, tipo_mandado):
        self.set_fill_color(26, 58, 108)
        self.rect(10, 50, 190, 12, 'F')
        self.set_text_color(255, 255, 255)
        self.set_xy(12, 52)
        self.set_font("Arial", 'B', 12)
        self.cell(100, 8, f"ALVO: {alvo_nome.upper()} (VULGO: {vulgo.upper()})", 0, 0)
        self.set_xy(165, 52)
        self.cell(30, 8, tipo_mandado.upper(), 0, 1, 'R')

# --- INTERFACE DO USUÁRIO ---
st.title("📂 Painel de Alvos Táticos")

# 1. Cadastro da Operação
with st.expander("⚙️ Configurações da Operação", expanded=True):
    col1, col2, col3 = st.columns(3)
    op_name = col1.text_input("Nome da Operação", "OPERAÇÃO CERBERUS")
    mission_id = col2.text_input("ID Missão", "#740599")
    meeting_pt = col3.text_input("Local do Briefing", "DIG DISE ITAPETININGA")
    h_hora = col1.text_input("H-Hora", "06:00")
    briefing_dt = col2.text_input("Data", "27/01/2026")

# 2. Cadastro do Alvo e seus múltiplos endereços
st.divider()
st.subheader("👤 Qualificação do Alvo")
col_a, col_b, col_c = st.columns([2, 1, 1])
alvo_nome = col_a.text_input("Nome Completo")
vulgo = col_b.text_input("Vulgo/Apelido")
tipo_mandado = col_c.selectbox("Mandado", ["Prisão Preventiva", "Busca e Apreensão", "Temporária"])
foto_alvo = st.file_uploader("Foto do Alvo", type=['jpg', 'png'])

# Lógica de Múltiplos Endereços
if 'enderecos' not in st.session_state:
    st.session_state.enderecos = []

def add_address():
    st.session_state.enderecos.append({"rua": "", "equipe": "", "obs": "", "foto": None})

st.button("➕ Adicionar Novo Endereço para este Alvo", on_click=add_address)

for i, ender in enumerate(st.session_state.enderecos):
    st.markdown(f"<div class='address-card'>", unsafe_allow_html=True)
    st.write(f"📍 **Local de Cumprimento #{i+1}**")
    col1, col2 = st.columns(2)
    ender['rua'] = col1.text_input(f"Endereço Completo", key=f"rua_{i}")
    ender['equipe'] = col2.text_input(f"Comandante / Equipe", key=f"eq_{i}")
    ender['obs'] = st.text_area(f"Riscos e Pontos Críticos", key=f"obs_{i}")
    ender['foto'] = st.file_uploader(f"Foto da Fachada #{i+1}", type=['jpg', 'png'], key=f"f_{i}")
    st.markdown("</div>", unsafe_allow_html=True)

# 3. Geração do PDF
if st.button("🚀 GERAR DOSSIÊ COMPLETO"):
    pdf = BriefingPDF()
    
    for ender in st.session_state.enderecos:
        pdf.add_page()
        pdf.header_op(op_name, mission_id, meeting_pt, briefing_dt, h_hora)
        pdf.draw_target_info(alvo_nome, vulgo, tipo_mandado)
        
        # Fotos
        if foto_alvo:
            # Salvar imagem temporária para o PDF
            img = Image.open(foto_alvo)
            img.save(f"temp_alvo.png")
            pdf.image("temp_alvo.png", 10, 65, 90, 65)
            
        if ender['foto']:
            img_f = Image.open(ender['foto'])
            img_f.save(f"temp_casa_{i}.png")
            pdf.image(f"temp_casa_{i}.png", 105, 65, 95, 65)

        # Dados do Local
        pdf.set_xy(10, 135)
        pdf.set_font("Arial", 'B', 8)
        pdf.set_text_color(26, 58, 108)
        pdf.cell(100, 5, "INTELIGÊNCIA ESTRATÉGICA / ENDEREÇO", 0, 1)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(180, 5, ender['rua'].upper())
        
        # QR Code Dinâmico
        qr_url = f"https://www.google.com/maps/search/{ender['rua'].replace(' ', '+')}"
        qr = qrcode.make(qr_url)
        qr.save("temp_qr.png")
        pdf.image("temp_qr.png", 10, 200, 30, 30)
        pdf.set_xy(45, 210)
        pdf.set_font("Arial", 'B', 8)
        pdf.cell(100, 5, "ESCANEIE PARA ROTA NO GOOGLE MAPS", 0, 1)

    # Output
    pdf_output = pdf.output(dest='S').encode('latin-1')
    st.download_button("⬇️ Baixar PDF Operacional", data=pdf_output, file_name="briefing.pdf")
