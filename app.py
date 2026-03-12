import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gerador de Briefing Policial", layout="wide")

class PDF_Briefing(FPDF):
    def header(self):
        # Cabeçalho padrão (Sigiloso)
        self.set_fill_color(0, 0, 0)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 8)
        self.cell(0, 5, 'SIGILOSO   -   DOCUMENTO DE INTELIGÊNCIA   -   RESTRITO', 0, 1, 'C', True)
        self.ln(5)

    def footer(self):
        # Relatório de Ocorrência fixo no rodapé de todas as páginas
        self.set_y(-60)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, 'RELATÓRIO DE OCORRÊNCIA E APREENSÕES DE CAMPO', 0, 1, 'C')
        self.set_draw_color(200, 200, 200)
        for _ in range(5):
            self.cell(0, 8, '', 'B', 1)
        
        self.set_y(-10)
        self.set_font('Arial', 'I', 6)
        self.cell(0, 10, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")} | Página {self.page_no()}', 0, 0, 'C')

def gerar_qr(texto):
    qr = qrcode.make(texto)
    path = f"qr_{hash(texto)}.png"
    qr.save(path)
    return path

# --- INTERFACE STREAMLIT ---
st.title("🗟 Sistema de Briefing Tático")

# 1. Dados da Operação
st.sidebar.header("DADOS DA OPERAÇÃO")
nome_operacao = st.sidebar.text_input("Nome da Operação", "OPERAÇÃO CERBERUS")
equipe_resp = st.sidebar.text_input("Equipe Responsável", "DIG DISE ITAPETININGA")
ponto_encontro = st.sidebar.text_input("Ponto de Encontro", "Sede da Delegacia")
data_briefing = st.sidebar.text_input("Briefing (Data/Hora)", "27/01/2026 03:30")
h_hora = st.sidebar.text_input("H-Hora (Execução)", "06:00")

# 2. Dados do Alvo
st.header("Dados do Alvo Tático")
col1, col2 = st.columns(2)

with col1:
    nome_alvo = st.text_input("Nome do Alvo")
    vulgo = st.text_input("Vulgo / Apelido")
    mandado = st.selectbox("Tipo de Mandado", ["PRISÃO PREVENTIVA", "BUSCA E APREENSÃO", "PRISÃO TEMPORÁRIA"])
    foto_alvo = st.file_uploader("Foto do Alvo", type=['jpg', 'png', 'jpeg'])

with col2:
    equipe_nome = st.text_input("Nome da Equipe (Ex: EQUIPE ALPHA)")
    comandante = st.text_input("Comandante da Equipe")
    agentes = st.text_area("Agentes Escalados (separados por vírgula)")
    foto_residencia = st.file_uploader("Foto da Residência", type=['jpg', 'png', 'jpeg'])

st.subheader("Endereços do Objetivo")
addr1 = st.text_input("Endereço Principal (Rua, Número, Bairro, Cidade)")
addr2 = st.text_input("Endereço Secundário/Apoio (Opcional)")
riscos = st.text_area("Riscos e Pontos Críticos", "Portão reforçado, presença de cães, câmeras no local.")

if st.button("GERAR PDF DE BRIEFING"):
    pdf = PDF_Briefing()
    pdf.add_page()
    
    # Cabeçalho da Operação
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(140, 10, nome_operacao.upper(), 0, 0)
    pdf.set_font('Arial', '', 8)
    pdf.cell(50, 10, f"COMANDO: {equipe_resp}", 1, 1, 'C')
    pdf.ln(2)
    
    # Barra de informações rápidas
    pdf.set_font('Arial', 'B', 7)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(48, 8, f"PONTO ENCONTRO: {ponto_encontro}", 1, 0, 'L', True)
    pdf.cell(48, 8, f"BRIEFING: {data_briefing}", 1, 0, 'L', True)
    pdf.cell(48, 8, f"H-HORA: {h_hora}", 1, 0, 'L', True)
    pdf.cell(46, 8, f"ID MISSÃO: #748599", 1, 1, 'L', True)
    pdf.ln(5)

    # Nome do Alvo e Mandado
    pdf.set_fill_color(30, 50, 100)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(140, 10, f" ALVO: {nome_alvo.upper()}", 0, 0, 'L', True)
    pdf.cell(50, 10, mandado, 0, 1, 'C', True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 5, f"VULGO: {vulgo}", 0, 1)
    pdf.ln(2)

    # Fotos (Lado a Lado)
    y_fotos = pdf.get_y()
    if foto_alvo:
        img_alvo = Image.open(foto_alvo)
        img_alvo.save("temp_alvo.png")
        pdf.image("temp_alvo.png", x=10, y=y_fotos, w=90, h=60)
        pdf.set_xy(10, y_fotos + 55)
        pdf.set_fill_color(0,0,0, 100)
        pdf.set_text_color(255,255,255)
        pdf.cell(90, 5, "IDENTIFICAÇÃO POSITIVA", 0, 0, 'L', True)
    
    if foto_residencia:
        img_res = Image.open(foto_residencia)
        img_res.save("temp_res.png")
        pdf.image("temp_res.png", x=105, y=y_fotos, w=95, h=60)
        pdf.set_xy(105, y_fotos + 55)
        pdf.cell(95, 5, "PERÍMETRO DE ENTRADA", 0, 0, 'L', True)
    
    pdf.ln(15)
    pdf.set_text_color(0,0,0)
    pdf.set_y(y_fotos + 65)

    # Inteligência e Logística
    curr_y = pdf.get_y()
    pdf.set_font('Arial', 'B', 9)
    pdf.set_text_color(30, 50, 150)
    pdf.cell(95, 5, "INTELIGÊNCIA ESTRATÉGICA", 0, 0)
    pdf.cell(95, 5, "LOGÍSTICA DE EQUIPE", 0, 1)
    
    pdf.set_font('Arial', '', 8)
    pdf.set_text_color(0, 0, 0)
    
    # Coluna 1: Endereços e Riscos
    pdf.set_xy(10, pdf.get_y())
    pdf.multi_cell(90, 5, f"ENDEREÇO 1: {addr1}\n\nENDEREÇO 2: {addr2}\n\nRISCOS: {riscos}", 1)
    
    # Coluna 2: Equipe
    pdf.set_xy(105, curr_y + 5)
    pdf.multi_cell(95, 5, f"EQUIPE: {equipe_nome}\nCOMANDANTE: {comandante}\nAGENTES: {agentes}", 1)

    # QR Codes de Rota
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 8)
    pdf.cell(0, 5, "ROTAS GPS TÁTICAS (GOOGLE MAPS)", 0, 1)
    
    # Gerar QR para Endereço 1
    if addr1:
        url_maps1 = f"https://www.google.com/maps/search/?api=1&query={addr1.replace(' ', '+')}"
        qr_path1 = gerar_qr(url_maps1)
        pdf.image(qr_path1, x=10, y=pdf.get_y()+2, w=25)
        pdf.set_xy(37, pdf.get_y()+5)
        pdf.multi_cell(60, 4, f"ESCANEIE PARA ROTA:\n{addr1[:40]}...", 0)
        os.remove(qr_path1)

    # Gerar QR para Endereço 2
    if addr2:
        url_maps2 = f"https://www.google.com/maps/search/?api=1&query={addr2.replace(' ', '+')}"
        qr_path2 = gerar_qr(url_maps2)
        pdf.image(qr_path2, x=105, y=pdf.get_y()-20, w=25)
        pdf.set_xy(132, pdf.get_y()-17)
        pdf.multi_cell(60, 4, f"ESCANEIE PARA ROTA 2:\n{addr2[:40]}...", 0)
        os.remove(qr_path2)

    # Salvar PDF
    pdf_file = "briefing_operacional.pdf"
    pdf.output(pdf_file)
    
    with open(pdf_file, "rb") as f:
        st.download_button("⬇️ BAIXAR PDF FINAL", f, file_name=pdf_file)
