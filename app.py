import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import os
from datetime import datetime
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador de Briefing Tático", layout="wide")

# Inicialização do estado (Memória do programa)
if 'alvos' not in st.session_state:
    st.session_state.alvos = []

class PDF_Briefing(FPDF):
    def header(self):
        # Tarja Superior Sigilosa
        self.set_fill_color(0, 0, 0)
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 8)
        self.cell(0, 5, 'SIGILOSO   -   DOCUMENTO DE INTELIGÊNCIA   -   RESTRITO', 0, 1, 'C', True)
        self.ln(5)

    def footer(self):
        # Relatório de Ocorrência fixo no rodapé
        self.set_y(-55)
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(0, 0, 0)
        self.set_draw_color(180, 180, 180)
        self.cell(0, 8, 'RELATÓRIO DE OCORRÊNCIA E APREENSÕES DE CAMPO', 'B', 1, 'C')
        for _ in range(4):
            self.cell(0, 8, '', 'B', 1)
        
        self.set_y(-10)
        self.set_font('Helvetica', 'I', 6)
        self.cell(0, 10, f'PÁGINA {self.page_no()}', 0, 0, 'C')

def gerar_qr_rota(origem, destino):
    # Cria URL de rota do Google Maps
    orig_enc = urllib.parse.quote(origem)
    dest_enc = urllib.parse.quote(destino)
    url = f"https://www.google.com/maps/dir/?api=1&origin={orig_enc}&destination={dest_enc}&travelmode=driving"
    
    qr = qrcode.make(url)
    path = f"qr_{hash(destino)}.png"
    qr.save(path)
    return path, url

# --- INTERFACE ---
st.title("🛡️ Sistema de Briefing Operacional")

# 1. DADOS GERAIS DA OPERAÇÃO
with st.expander("1. DADOS DA OPERAÇÃO (FIXOS PARA TODOS OS ALVOS)", expanded=True):
    col_op1, col_op2 = st.columns(2)
    nome_operacao = col_op1.text_input("Nome da Operação", "OPERAÇÃO CERBERUS")
    origem_operacao = col_op1.text_input("Endereço de Origem (Para o GPS)", "Rua Exemplo, 100 - Centro")
    data_briefing = col_op2.text_input("Briefing (Data/Hora)", "27/01/2026 03:30")
    h_hora = col_op2.text_input("H-Hora (Execução)", "06:00")

# 2. GESTÃO DE ALVOS
st.header("🎯 Alvos Táticos")

def adicionar_alvo():
    st.session_state.alvos.append({
        'nome': '', 'vulgo': '', 'mandado': 'PRISÃO PREVENTIVA',
        'fotos': {'alvo': None, 'residencia': None},
        'enderecos': [''], 'agentes': [''], 'riscos': ''
    })

if st.button("➕ ADICIONAR NOVO ALVO"):
    adicionar_alvo()

# Renderização dos Alvos
for idx_alvo, alvo in enumerate(st.session_state.alvos):
    with st.container(border=True):
        col_a, col_b = st.columns([4, 1])
        col_a.subheader(f"Alvo #{idx_alvo + 1}")
        if col_b.button(f"🗑️ Remover Alvo", key=f"rem_alvo_{idx_alvo}"):
            st.session_state.alvos.pop(idx_alvo)
            st.rerun()

        c1, c2 = st.columns(2)
        alvo['nome'] = c1.text_input("Nome Completo", value=alvo['nome'], key=f"nome_{idx_alvo}")
        alvo['vulgo'] = c2.text_input("Vulgo", value=alvo['vulgo'], key=f"vulgo_{idx_alvo}")
        alvo['mandado'] = c1.selectbox("Mandado", ["PRISÃO PREVENTIVA", "BUSCA E APREENSÃO", "TEMPORÁRIA"], key=f"mand_{idx_alvo}")
        alvo['riscos'] = c2.text_area("Riscos/Observações", value=alvo['riscos'], key=f"risc_{idx_alvo}")

        # Fotos
        f1, f2 = st.columns(2)
        alvo['fotos']['alvo'] = f1.file_uploader("Foto do Alvo", key=f"f1_{idx_alvo}")
        alvo['fotos']['residencia'] = f2.file_uploader("Foto da Fachada", key=f"f2_{idx_alvo}")

        # Endereços Dinâmicos
        st.write("📍 **Endereços de Cumprimento**")
        for idx_end, end in enumerate(alvo['enderecos']):
            alvo['enderecos'][idx_end] = st.text_input(f"Endereço {idx_end+1}", value=end, key=f"end_{idx_alvo}_{idx_end}")
        
        if st.button("➕ Adicionar Endereço", key=f"btn_end_{idx_alvo}"):
            alvo['enderecos'].append('')
            st.rerun()

        # Agentes Dinâmicos
        st.write("👥 **Equipe Operacional (Agentes)**")
        for idx_age, age in enumerate(alvo['agentes']):
            alvo['agentes'][idx_age] = st.text_input(f"Agente {idx_age+1}", value=age, key=f"age_{idx_alvo}_{idx_age}")
        
        if st.button("➕ Adicionar Agente", key=f"btn_age_{idx_alvo}"):
            alvo['agentes'].append('')
            st.rerun()

# 3. GERAÇÃO DO PDF
if st.session_state.alvos and st.button("🚀 GERAR PDF COMPLETO"):
    pdf = PDF_Briefing()
    
    for alvo in st.session_state.alvos:
        pdf.add_page()
        
        # Cabeçalho Operação
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, nome_operacao.upper(), 0, 1)
        
        # Grid de Informações
        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_fill_color(245, 245, 245)
        pdf.cell(95, 8, f" BRIEFING: {data_briefing}", 1, 0, 'L', True)
        pdf.cell(95, 8, f" H-HORA: {h_hora}", 1, 1, 'L', True)
        pdf.ln(2)

        # Seção Alvo
        pdf.set_fill_color(30, 50, 100)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(140, 10, f" ALVO: {alvo['nome'].upper()}", 0, 0, 'L', True)
        pdf.cell(50, 10, alvo['mandado'], 0, 1, 'C', True)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(0, 6, f"VULGO: {alvo['vulgo']}", 0, 1)

        # Fotos
        y_fotos = pdf.get_y()
        if alvo['fotos']['alvo']:
            img1 = Image.open(alvo['fotos']['alvo'])
            img1.save("temp1.png")
            pdf.image("temp1.png", x=10, y=y_fotos, w=90, h=60)
            pdf.set_xy(10, y_fotos+55)
            pdf.set_fill_color(0,0,0)
            pdf.set_text_color(255,255,255)
            pdf.cell(90, 5, " IDENTIFICAÇÃO POSITIVA", 0, 0, 'L', True)

        if alvo['fotos']['residencia']:
            img2 = Image.open(alvo['fotos']['residencia'])
            img2.save("temp2.png")
            pdf.image("temp2.png", x=105, y=y_fotos, w=90, h=60)
            pdf.set_xy(105, y_fotos+55)
            pdf.set_text_color(255,255,255)
            pdf.cell(90, 5, " PERÍMETRO DE ENTRADA", 0, 1, 'L', True)
        
        pdf.set_text_color(0,0,0)
        pdf.set_y(y_fotos + 65)

        # Endereços e QR Codes
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(0, 10, "INTELIGÊNCIA ESTRATÉGICA E ROTAS", 0, 1)
        
        for ender in alvo['enderecos']:
            if ender.strip():
                curr_y = pdf.get_y()
                qr_p, qr_url = gerar_qr_rota(origem_operacao, ender)
                pdf.image(qr_p, x=10, y=curr_y, w=20)
                pdf.set_xy(32, curr_y + 2)
                pdf.set_font('Helvetica', 'B', 8)
                pdf.multi_cell(0, 4, f"DESTINO: {ender}\nORIGEM: {origem_operacao}")
                pdf.set_y(curr_y + 22)
                os.remove(qr_p)

        # Equipe e Agentes
        pdf.ln(2)
        pdf.set_font('Helvetica', 'B', 9)
        pdf.cell(0, 8, "EQUIPE OPERACIONAL ESCALADA:", 0, 1)
        pdf.set_font('Helvetica', '', 8)
        agentes_str = " | ".join([a for a in alvo['agentes'] if a.strip()])
        pdf.multi_cell(0, 5, agentes_str, 1)

    pdf_output = "Briefing_Completo.pdf"
    pdf.output(pdf_output)
    with open(pdf_output, "rb") as f:
        st.download_button("📩 Baixar Briefing PDF", f, file_name=pdf_output)
