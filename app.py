import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import os
from datetime import datetime
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="TACTICAL OPS - Intelligence Framework", layout="wide")

# Inicialização da memória para múltiplos alvos
if 'alvos' not in st.session_state:
    st.session_state.alvos = []

class TacticalPDF(FPDF):
    def header(self):
        # Cabeçalho de Segurança
        self.set_fill_color(0, 0, 0)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 8)
        self.cell(0, 5, 'SIGILOSO   -   DOCUMENTO DE INTELIGÊNCIA   -   RESTRITO', 0, 1, 'C', True)
        self.ln(3)

    def draw_pattern_grid(self, x, y, label):
        """Desenha o grid de bolinhas de desbloqueio (3x3)"""
        self.set_font('Helvetica', 'B', 6)
        self.set_text_color(100, 100, 100)
        self.text(x + 5, y - 2, label)
        
        self.set_draw_color(50, 50, 50)
        radius = 1
        for row in range(3):
            for col in range(3):
                self.ellipse(x + (col * 5), y + (row * 5), radius, radius)

    def footer(self):
        # --- SEÇÃO: RELATÓRIO DE OCORRÊNCIA ---
        self.set_y(-75)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(0, 0, 0)
        self.set_draw_color(200, 200, 200)
        self.cell(0, 6, 'RELATÓRIO DE OCORRÊNCIA E APREENSÕES DE CAMPO', 'B', 1, 'C')
        for _ in range(3):
            self.cell(0, 6, '', 'B', 1)

        # --- SEÇÃO: CHECKLIST E CÓDIGOS (ESTILO ANEXO) ---
        self.ln(4)
        curr_y = self.get_y()
        
        # Lado Esquerdo: Grids de Desbloqueio
        self.draw_pattern_grid(15, curr_y + 5, "DISP. 1")
        self.draw_pattern_grid(45, curr_y + 5, "DISP. 2")
        self.draw_pattern_grid(15, curr_y + 22, "DISP. 3")
        self.draw_pattern_grid(45, curr_y + 22, "DISP. 4")

        # Divisória Vertical
        self.set_draw_color(220, 220, 220)
        self.line(75, curr_y, 75, curr_y + 35)

        # Lado Direito: Checklist IMEI
        self.set_xy(80, curr_y)
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(100, 100, 130)
        self.cell(0, 5, 'CHECKLIST DE DISPOSITIVOS (IMEI/SN)', 0, 1)
        self.set_draw_color(200, 200, 255)
        for _ in range(3):
            self.set_x(80)
            self.cell(0, 8, '', 'B', 1)

        # Numeração de Página
        self.set_y(-10)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'TACTICAL OPS FRAMEWORK | DATA/HORA: {datetime.now().strftime("%d/%m/%Y %H:%M")} | PÁGINA {self.page_no()}', 0, 0, 'C')

def gerar_qr_rota(origem, destino):
    orig_enc = urllib.parse.quote(origem)
    dest_enc = urllib.parse.quote(destino)
    url = f"https://www.google.com/maps/dir/?api=1&origin={orig_enc}&destination={dest_enc}"
    qr = qrcode.make(url)
    path = f"temp_qr_{hash(destino)}.png"
    qr.save(path)
    return path

# --- INTERFACE DE USUÁRIO (STREAMLIT) ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTextInput, .stTextArea, .stSelectbox { border-radius: 5px; }
    h1 { color: #4A90E2; font-family: 'Courier New'; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ TACTICAL OPS: Intelligence System")

# 1. DADOS TÁTICOS DA OPERAÇÃO
with st.container(border=True):
    st.subheader("📋 Dados da Operação")
    col1, col2, col3 = st.columns([2, 1, 1])
    nome_op = col1.text_input("NOME DA OPERAÇÃO", "OPERAÇÃO CERBERUS")
    data_br = col2.text_input("BRIEFING (DATA/HORA)", "27/01/2026 03:30")
    h_hora = col3.text_input("H-HORA (EXECUÇÃO)", "06:00")
    
    end_origem = st.text_input("📍 PONTO DE PARTIDA / ORIGEM (Para GPS)", "DIG DISE ITAPETININGA")

# 2. GESTÃO DE ALVOS
st.divider()
if st.button("➕ ADICIONAR NOVO ALVO TÁTICO"):
    st.session_state.alvos.append({
        'nome': '', 'vulgo': '', 'mandado': 'PRISÃO PREVENTIVA',
        'enderecos': [''], 'agentes': [''], 'obs': '',
        'foto_alvo': None, 'foto_casa': None
    })

for idx, alvo in enumerate(st.session_state.alvos):
    with st.expander(f"🎯 ALVO #{idx+1}: {alvo['nome'] if alvo['nome'] else 'NOVO ALVO'}", expanded=True):
        c1, c2 = st.columns(2)
        alvo['nome'] = c1.text_input("Nome Completo", value=alvo['nome'], key=f"n_{idx}")
        alvo['vulgo'] = c2.text_input("Vulgo / Apelido", value=alvo['vulgo'], key=f"v_{idx}")
        alvo['mandado'] = c1.selectbox("Tipo de Mandado", ["PRISÃO PREVENTIVA", "BUSCA E APREENSÃO", "TEMPORÁRIA"], key=f"m_{idx}")
        alvo['obs'] = c2.text_area("Observações / Riscos", value=alvo['obs'], key=f"o_{idx}")

        f1, f2 = st.columns(2)
        alvo['foto_alvo'] = f1.file_uploader("Retrato do Alvo", key=f"fa_{idx}")
        alvo['foto_casa'] = f2.file_uploader("Local da Fachada", key=f"fc_{idx}")

        st.markdown("---")
        # Endereços
        st.write("**📍 Endereços (Geram Rota GPS)**")
        for e_idx, end in enumerate(alvo['enderecos']):
            alvo['enderecos'][e_idx] = st.text_input(f"Endereço {e_idx+1}", value=end, key=f"e_{idx}_{e_idx}")
        if st.button("➕ Novo Endereço", key=f"be_{idx}"):
            alvo['enderecos'].append('')
            st.rerun()

        # Agentes
        st.write("**👥 Equipe Escalada**")
        for a_idx, age in enumerate(alvo['agentes']):
            alvo['agentes'][a_idx] = st.text_input(f"Policial {a_idx+1}", value=age, key=f"a_{idx}_{a_idx}")
        if st.button("➕ Novo Policial", key=f"ba_{idx}"):
            alvo['agentes'].append('')
            st.rerun()
        
        if st.button("🗑️ Remover Alvo", key=f"rem_{idx}"):
            st.session_state.alvos.pop(idx)
            st.rerun()

# 3. GERAÇÃO DO PDF FINAL
if st.session_state.alvos and st.button("🛰️ GERAR BRIEFING COMPLETO (PDF)"):
    pdf = TacticalPDF()
    
    for alvo in st.session_state.alvos:
        pdf.add_page()
        
        # Seção Operação
        pdf.set_font('Helvetica', 'B', 16)
        pdf.cell(0, 10, nome_op.upper(), 0, 1)
        
        pdf.set_fill_color(240, 240, 240)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.cell(63, 8, f" PONTO ENCONTRO: {end_origem[:30]}", 1, 0, 'L', True)
        pdf.cell(63, 8, f" BRIEFING: {data_br}", 1, 0, 'L', True)
        pdf.cell(64, 8, f" H-HORA: {h_hora}", 1, 1, 'L', True)
        pdf.ln(4)

        # Seção Alvo
        pdf.set_fill_color(0, 30, 80)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(140, 10, f" ALVO: {alvo['nome'].upper()}", 0, 0, 'L', True)
        pdf.cell(50, 10, alvo['mandado'], 0, 1, 'C', True)
        
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(0, 6, f"VULGO: {alvo['vulgo']}", 0, 1)
        pdf.ln(2)

        # Fotos
        curr_y = pdf.get_y()
        if alvo['foto_alvo']:
            img_alvo = Image.open(alvo['foto_alvo'])
            img_alvo.save("tmp_a.png")
            pdf.image("tmp_a.png", x=10, y=curr_y, w=90, h=60)
            pdf.set_xy(10, curr_y + 55)
            pdf.set_fill_color(0,0,0)
            pdf.set_text_color(255,255,255)
            pdf.cell(90, 5, " IDENTIFICAÇÃO POSITIVA", 0, 0, 'L', True)

        if alvo['foto_casa']:
            img_casa = Image.open(alvo['foto_casa'])
            img_casa.save("tmp_c.png")
            pdf.image("tmp_c.png", x=105, y=curr_y, w=95, h=60)
            pdf.set_xy(105, curr_y + 55)
            pdf.cell(95, 5, " PERÍMETRO DE ENTRADA", 0, 1, 'L', True)
        
        pdf.set_y(curr_y + 65)
        pdf.set_text_color(0,0,0)

        # Inteligência e Rotas
        pdf.set_font('Helvetica', 'B', 10)
        pdf.set_text_color(0, 30, 100)
        pdf.cell(0, 8, "INTELIGÊNCIA ESTRATÉGICA E ROTAS GPS TÁTICAS", 'B', 1)
        pdf.ln(2)
        
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(0, 0, 0)
        
        for end in alvo['enderecos']:
            if end.strip():
                qr_path = gerar_qr_rota(end_origem, end)
                y_antes_qr = pdf.get_y()
                pdf.image(qr_path, x=10, y=y_antes_qr, w=22)
                pdf.set_xy(35, y_antes_qr + 5)
                pdf.set_font('Helvetica', 'B', 8)
                pdf.multi_cell(0, 4, f"ROTA GPS ATIVA:\nDE: {end_origem}\nPARA: {end}")
                pdf.set_y(y_antes_qr + 25)
                os.remove(qr_path)

        # Equipe
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(0, 6, "EQUIPE OPERACIONAL:", 0, 1)
        pdf.set_font('Helvetica', '', 8)
        equipe_limpa = [a for a in alvo['agentes'] if a.strip()]
        pdf.multi_cell(0, 5, " | ".join(equipe_limpa), 1)
        
        pdf.ln(2)
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_text_color(200, 0, 0)
        pdf.multi_cell(0, 4, f"RISCOS/OBS: {alvo['obs']}")

    final_pdf = "Briefing_Tactical_Ops.pdf"
    pdf.output(final_pdf)
    with open(final_pdf, "rb") as f:
        st.download_button("💾 BAIXAR DOCUMENTO DE INTELIGÊNCIA", f, file_name=final_pdf)
