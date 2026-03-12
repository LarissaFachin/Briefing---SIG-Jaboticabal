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
    /* Botão Adicionar Novo Alvo (Azul Forte) */
    .stButton>button[key="add"] { background-color: #1d4ed8 !important; color: white; font-weight: bold; width: 100%; height: 50px; border-radius: 8px; }
    /* Botão Gerar Dossiê (Verde Sucesso) */
    .stButton>button[key="pdf"] { background-color: #15803d !important; color: white; font-size: 20px; font-weight: bold; width: 100%; height: 60px; border-radius: 10px; }
    .stButton>button[key*="rem"] { background-color: #dc3545 !important; color: white; }
    div[data-testid="stExpander"] { border: 1px solid #d1d5db; border-radius: 10px; background-color: #f8f9fa; }
    label { font-weight: bold !important; color: #333 !important; }
    </style>
""", unsafe_allow_html=True)

if 'alvos' not in st.session_state:
    st.session_state.alvos = []

# --- CLASSE DO PDF PROFISSIONAL ---
class TacticalPDF(FPDF):
    def header(self):
        self.set_fill_color(0, 0, 0)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 8)
        self.cell(0, 6, 'S I G I L O S O   -   D O C U M E N T O   D E   I N T E L I G Ê N C I A   -   R E S T R I T O', 0, 1, 'C', True)
        self.ln(2)

    def draw_section_bullet(self, x, y):
        self.set_fill_color(26, 51, 126) 
        self.rect(x, y + 1.2, 2.5, 2.5, 'F')

    def draw_footer_elements(self):
        self.set_y(-68) # Subi um pouco para garantir que caiba com o conteúdo
        self.set_font('Helvetica', 'B', 9); self.set_text_color(0, 0, 0)
        self.cell(0, 8, 'R E L A T Ó R I O  D E  O C O R R Ê N C I A  E  A P R E E N S Õ E S  D E  C A M P O', 'B', 1, 'C')
        for _ in range(3): self.cell(0, 6, '', 'B', 1)
        
        curr_y = self.get_y() + 4
        for i in range(1, 5):
            x_pos = 15 + ((i-1)*18)
            self.set_font('Helvetica', 'B', 6); self.set_text_color(100, 100, 100)
            self.text(x_pos, curr_y - 2, f"DISP. {i}")
            for r in range(3):
                for c in range(3):
                    self.ellipse(x_pos + (c * 4), curr_y + (r * 4), 0.8, 0.8)
        
        self.line(100, curr_y - 2, 100, curr_y + 15)
        self.set_xy(105, curr_y - 2); self.set_font('Helvetica', 'B', 7)
        self.cell(0, 4, 'CHECKLIST DE DISPOSITIVOS (IMEI/SN)', 0, 1)
        for _ in range(2): self.set_x(105); self.cell(0, 6, '', 'B', 1)

        self.set_y(-8); self.set_font('Helvetica', '', 6); self.set_text_color(150, 150, 150)
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

# --- INTERFACE ---
st.title("🛡️ TACTICAL OPS: SIG JABOTICABAL")

with st.container(border=True):
    st.subheader("📋 Configuração da Operação")
    c1, c2 = st.columns([2, 1])
    nome_op = c1.text_input("NOME DA OPERAÇÃO", "OPERAÇÃO")
    unidade = c1.text_input("UNIDADE DE COMANDO", "SIG JABOTICABAL")
    data_op = c2.text_input("DATA/HORA BRIEFING", "27/01/2026 03:30")
    h_hora = c2.text_input("H-HORA (EXECUÇÃO)", "06:00")
    end_origem = st.text_input("📍 PONTO DE PARTIDA (GPS)", "Praça Pedro Dória, s/n, Centro, Jaboticabal - SP, CEP: 14870-000")

st.markdown("<br>", unsafe_allow_html=True)
if st.button("➕ ADICIONAR NOVO ALVO TÁTICO", key="add"):
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
        
        alv_c1, alv_c2 = st.columns(2)
        alvo['viatura'] = alv_c1.text_input("Viatura / Prefixo", key=f"via_{idx}")
        alvo['agentes'] = alv_c2.text_input("Agentes (separe por vírgula)", key=f"a_{idx}")

        f1, f2 = st.columns(2)
        alvo['foto_alvo'] = f1.file_uploader("Foto do Alvo", key=f"fa_{idx}")
        alvo['foto_casa'] = f2.file_uploader("Foto da Fachada", key=f"fc_{idx}")

        st.write("📍 **Localidades de Cumprimento**")
        for e_idx, end in enumerate(alvo['enderecos']):
            alvo['enderecos'][e_idx] = st.text_input(f"Endereço {e_idx+1}", value=end, key=f"e_{idx}_{e_idx}")
        
        if st.button("➕ Adicionar Endereço", key=f"be_{idx}"):
            alvo['enderecos'].append(''); st.rerun()

        if st.button("🗑️ Remover Alvo", key=f"rem_{idx}"):
            st.session_state.alvos.pop(idx); st.rerun()

# --- GERAÇÃO DO PDF ---
if st.session_state.alvos and st.button("🛰️ GERAR DOSSIÊ TÁTICO FINAL", key="pdf"):
    pdf = TacticalPDF()
    # Desativa quebra automática para evitar páginas em branco indesejadas
    pdf.set_auto_page_break(auto=True, margin=10)
    
    for i, alvo in enumerate(st.session_state.alvos):
        pdf.add_page()
        
        # Cabeçalho da Operação
        pdf.set_font('Helvetica', 'B', 22); pdf.set_text_color(0, 0, 0)
        pdf.cell(130, 10, nome_op.upper(), 0, 0)
        
        pdf.line(148, 16, 148, 26)
        pdf.set_xy(150, 17); pdf.set_font('Helvetica', '', 6); pdf.set_text_color(100, 100, 100)
        pdf.cell(50, 4, 'COMANDO OPERACIONAL', 0, 1, 'R')
        pdf.set_font('Helvetica', 'B', 10); pdf.set_text_color(0, 0, 0)
        pdf.set_x(150); pdf.cell(50, 5, unidade.upper(), 0, 1, 'R')
        
        # Grid de Informações
        pdf.set_y(30); pdf.set_font('Helvetica', 'B', 6); pdf.set_text_color(100, 100, 100)
        pdf.cell(47, 4, 'PONTO DE ENCONTRO', 'TLR', 0)
        pdf.cell(47, 4, 'BRIEFING (DATA/HORA)', 'TLR', 0)
        pdf.cell(47, 4, 'H-HORA (EXECUÇÃO)', 'TLR', 0)
        pdf.cell(47, 4, 'ID MISSÃO', 'TLR', 1)
        
        pdf.set_font('Helvetica', 'B', 7); pdf.set_text_color(0, 0, 0)
        x_g, y_g = pdf.get_x(), pdf.get_y()
        pdf.multi_cell(47, 4, end_origem, 'BLR', 'L')
        pdf.set_xy(x_g + 47, y_g); pdf.set_text_color(30, 50, 120); pdf.cell(47, 8, data_op, 'BLR', 0)
        pdf.set_text_color(200, 0, 0); pdf.cell(47, 8, h_hora, 'BLR', 0)
        pdf.set_text_color(0, 0, 0); pdf.cell(47, 8, f'#{i+1001:06d}', 'BLR', 1)

        # Banner de Mandado
        pdf.ln(3)
        pdf.set_fill_color(26, 51, 126); pdf.set_text_color(255, 255, 255); pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 9, alvo['mandado'].upper(), 0, 1, 'C', True)

        # DESTAQUE DO ALVO (COM NUMERAÇÃO)
        pdf.ln(2); pdf.set_text_color(0, 0, 0); pdf.set_font('Helvetica', 'B', 15)
        pdf.cell(0, 8, f"ALVO {i+1}: {alvo['nome'].upper()}", 0, 1)
        pdf.set_font('Helvetica', 'B', 10); pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 5, f"VULGO: {alvo['vulgo'].upper()}", 0, 1)

        # FOTOS COMPACTAS (Altura reduzida para 45mm para caber tudo)
        pdf.ln(1); y_f = pdf.get_y()
        h_foto = 45 # Reduzido de 50 para 45
        if alvo['foto_alvo']:
            path_a = f"tmp_a_{i}.png"
            Image.open(alvo['foto_alvo']).save(path_a)
            pdf.image(path_a, x=10, y=y_f, w=93, h=h_foto)
            pdf.set_xy(10, y_f + (h_foto - 4))
            pdf.set_fill_color(0,0,0); pdf.set_text_color(255,255,255)
            pdf.set_font('Helvetica', 'B', 7); pdf.cell(93, 4, " IDENTIFICAÇÃO POSITIVA", 0, 0, 'L', True)

        if alvo['foto_casa']:
            path_c = f"tmp_c_{i}.png"
            Image.open(alvo['foto_casa']).save(path_c)
            pdf.image(path_c, x=107, y=y_f, w=93, h=h_foto)
            pdf.set_xy(107, y_f + (h_foto - 4)); pdf.set_text_color(255,255,255)
            pdf.cell(93, 4, " PERÍMETRO DE ENTRADA", 0, 0, 'L', True)
        
        # LOGÍSTICA
        pdf.set_y(y_f + h_foto + 3); c_y = pdf.get_y()
        pdf.draw_section_bullet(10, c_y)
        pdf.set_xy(14, c_y); pdf.set_font('Helvetica', 'B', 8); pdf.set_text_color(30, 50, 120); pdf.cell(91, 6, 'INTELIGÊNCIA ESTRATÉGICA', 0, 0)
        
        pdf.draw_section_bullet(107, c_y)
        pdf.set_xy(111, c_y); pdf.cell(89, 6, 'LOGÍSTICA DE EQUIPE', 0, 1)
        
        pdf.set_font('Helvetica', '', 7); pdf.set_text_color(100, 100, 100)
        pdf.set_x(10); pdf.cell(95, 4, 'LOCALIDADES CADASTRADAS', 0, 0)
        pdf.cell(95, 4, 'VIATURA / EFETIVO OPERACIONAL', 0, 1)
        
        pdf.set_font('Helvetica', 'B', 8); pdf.set_text_color(0, 0, 0); y_desc = pdf.get_y()
        end_limpo = alvo['enderecos'][0][:45] + "..." if len(alvo['enderecos'][0]) > 45 else alvo['enderecos'][0]
        pdf.multi_cell(92, 4, f"LOCAL: {end_limpo.upper()}", 0, 'L')
        
        pdf.set_xy(107, y_desc)
        agentes_f = " | ".join([a.strip() for a in alvo['agentes'].split(',') if a.strip()])
        pdf.multi_cell(93, 4, f"VTR: {alvo['viatura'].upper()}\nEFETIVO: {agentes_f}", 0, 'L')

        # GPS SLIM (Ajuste de posição para não empurrar o rodapé)
        pdf.ln(3)
        for e_idx, ender in enumerate(alvo['enderecos'][:2]):
            if ender.strip():
                # Bloco de QR mais compacto (20mm de altura)
                pdf.set_fill_color(248, 250, 255); pdf.rect(10, pdf.get_y(), 190, 20, 'F')
                qr_p = gerar_qr(end_origem, ender)
                pdf.image(qr_p, x=12, y=pdf.get_y() + 1, w=18, h=18)
                pdf.set_xy(35, pdf.get_y() + 2); pdf.set_font('Helvetica', 'B', 7); pdf.set_text_color(30, 50, 120)
                pdf.cell(0, 4, f'ROTA GPS #{e_idx+1} - {ender.upper()[:40]}', 0, 1)
                pdf.set_font('Helvetica', '', 6); pdf.set_text_color(100, 100, 100)
                pdf.set_x(35); pdf.multi_cell(0, 4, f"ORIGEM: {end_origem}\nDESTINO: {ender}")
                pdf.ln(1); os.remove(qr_p)

        # Desenha o rodapé técnico (FIXO NO FINAL DA FOLHA)
        pdf.draw_footer_elements()

    # Finalização
    nome_final = "Dossie_SIG_Jaboticabal.pdf"
    pdf.output(nome_final)
    with open(nome_final, "rb") as f:
        st.download_button("📩 BAIXAR DOSSIÊ TÁTICO FINAL", f, file_name=nome_final)
