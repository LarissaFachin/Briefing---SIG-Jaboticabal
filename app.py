import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import io
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL E ESTILO (ALTO CONTRASTE) ---
st.set_page_config(layout="wide", page_title="SISTEMA OPS - TÁTICO")

st.markdown("""
    <style>
    .stApp { background-color: #050a14; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0b1424; border-right: 2px solid #1e3a8a; }
    
    /* Inputs e Labels */
    label { color: #f8fafc !important; font-weight: bold !important; font-size: 16px !important; }
    input, textarea, select { background-color: #1e293b !important; color: white !important; border: 1px solid #3b82f6 !important; }
    
    /* Botões */
    .stButton>button { background-color: #2563eb !important; color: white !important; font-weight: bold !important; border-radius: 5px !important; height: 45px; }
    .stButton>button:hover { background-color: #1d4ed8 !important; border: 1px solid white !important; }
    
    /* Cards */
    .card { background-color: #0f172a; border: 1px solid #1e40af; padding: 25px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5); }
    .badge-hora { background-color: #450a0a; color: #ef4444; padding: 5px 15px; border-radius: 5px; font-weight: bold; border: 1px solid #ef4444; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADOS ---
if 'alvos' not in st.session_state: st.session_state.alvos = []
if 'missao' not in st.session_state: 
    st.session_state.missao = {
        'nome': 'OPERAÇÃO', 'unidade': 'DELEGACIA', 'ponto': '', 'data_br': '', 'h_hora': '', 'resumo': ''
    }
if 'view' not in st.session_state: st.session_state.view = 'painel'

# --- FUNÇÕES DE NAVEGAÇÃO ---
def mudar_view(nova_view): st.session_state.view = nova_view

# --- CLASSE DO PDF (FIEL AO MODELO ANEXADO) ---
class BriefingPDF(FPDF):
    def header_fiel(self, missao):
        # Header Superior
        self.set_fill_color(0, 0, 0)
        self.rect(10, 10, 190, 8, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", 'B', 8)
        self.cell(190, 8, "S I G I L O S O   -   D O C U M E N T O   D E   I N T E L I G Ê N C I A   -   R E S T R I T O", 0, 1, 'C')
        
        # Nome da Op e Comando
        self.set_text_color(0, 0, 0)
        self.ln(2)
        self.set_font("Arial", 'B', 22)
        self.cell(140, 10, missao['nome'].upper(), 0, 0)
        
        self.set_font("Arial", '', 6)
        self.set_xy(155, 20)
        self.cell(45, 5, "COMANDO OPERACIONAL", 1, 1, 'C')
        self.set_font("Arial", 'B', 10)
        self.set_x(155)
        self.cell(45, 10, missao['unidade'].upper(), 1, 1, 'C')
        
        # Grid de Missão
        self.set_xy(10, 42)
        self.set_font("Arial", 'B', 6)
        self.cell(60, 12, f"PONTO DE ENCONTRO: {missao['ponto'].upper()}", 1)
        self.cell(50, 12, f"BRIEFING: {missao['data_br']}", 1)
        self.set_text_color(200, 0, 0)
        self.cell(40, 12, f"H-HORA: {missao['h_hora']}", 1)
        self.set_text_color(0, 0, 0)
        self.cell(40, 12, f"ID MISSÃO: #740599", 1)

    def draw_footer_fiel(self, pagina):
        # Relatório de Ocorrência e Checklist
        self.set_xy(10, 205)
        self.set_font("Arial", 'B', 8)
        self.cell(190, 8, "RELATÓRIO DE OCORRÊNCIA E APREENSÕES DE CAMPO", 'T', 1, 'C')
        for _ in range(4): self.cell(190, 6, "_"*110, 0, 1)
        
        # Desenho dos Celulares (Simbolizado)
        self.ln(5)
        self.set_font("Arial", 'B', 7)
        self.cell(60, 5, "CHECKLIST DE DISPOSITIVOS (IMEI/SN)", 0, 1)
        for _ in range(3): self.cell(100, 5, "_"*60, 0, 1)
        
        self.set_font("Arial", '', 6)
        self.set_xy(10, 280)
        self.cell(190, 5, f"TACTICALOPS INTELLIGENCE FRAMEWORK | DATA/HORA DOC: {datetime.now().strftime('%d/%m/%Y %H:%M')} | PÁGINA {pagina}", 0, 0, 'C')

# --- INTERFACE ---
with st.sidebar:
    st.markdown("<h1 style='color:#3b82f6;'>T-OPS</h1>", unsafe_allow_html=True)
    if st.button("🏠 Painel Principal"): mudar_view('painel')
    if st.button("⚙️ Editar Missão"): mudar_view('missao')
    if st.button("🎯 Cadastrar Alvo"): mudar_view('alvo')

# --- TELA 1: PAINEL ---
if st.session_state.view == 'painel':
    st.title("🛡️ Painel de Operações")
    st.markdown(f"""<div class='card'>
        <h2>{st.session_state.missao['nome']}</h2>
        <p>Unidade: {st.session_state.missao['unidade']} | Ponto: {st.session_state.missao['ponto']}</p>
        <span class='badge-hora'>H-HORA: {st.session_state.missao['h_hora']}</span>
    </div>""", unsafe_allow_html=True)
    
    if not st.session_state.alvos:
        st.warning("Nenhum alvo cadastrado.")
    else:
        for a in st.session_state.alvos:
            st.markdown(f"<div class='card'>🎯 {a['nome']} ({a['vulgo']}) - {len(a['enderecos'])} locais</div>", unsafe_allow_html=True)

# --- TELA 2: EDITAR MISSÃO ---
elif st.session_state.view == 'missao':
    st.title("⚙️ Dados Gerais da Operação")
    with st.container():
        st.session_state.missao['nome'] = st.text_input("Nome da Operação", st.session_state.missao['nome'])
        st.session_state.missao['unidade'] = st.text_input("Equipe Responsável (Unidade)", st.session_state.missao['unidade'])
        c1, c2 = st.columns(2)
        st.session_state.missao['data_br'] = c1.text_input("Horário Briefing (DD/MM/AAAA HH:MM)", st.session_state.missao['data_br'])
        st.session_state.missao['h_hora'] = c2.text_input("H-Hora (Execução)", st.session_state.missao['h_hora'])
        st.session_state.missao['ponto'] = st.text_input("Endereço do Briefing (Ponto de Encontro)", st.session_state.missao['ponto'])
        st.session_state.missao['resumo'] = st.text_area("Resumo / Diretrizes da Missão")
        if st.button("Salvar Missão"): mudar_view('painel')

# --- TELA 3: CADASTRO DE ALVO ---
elif st.session_state.view == 'alvo':
    st.title("🎯 Cadastro de Novo Alvo")
    
    # Estados temporários para as listas dinâmicas
    if 'temp_equipe' not in st.session_state: st.session_state.temp_equipe = []
    if 'temp_ends' not in st.session_state: st.session_state.temp_ends = []

    with st.form("alvo_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo do Alvo")
            vulgo = st.text_input("Vulgo")
            mandado = st.selectbox("Tipo", ["Prisão Preventiva", "Busca e Apreensão"])
            foto_alvo = st.file_uploader("Foto ID Alvo")
        
        with col2:
            st.write("👥 COMPOSIÇÃO DA EQUIPE")
            integrante = st.text_input("Nome do Integrante")
            if st.form_submit_button("➕ Adicionar Integrante"):
                if integrante: st.session_state.temp_equipe.append(integrante)
            st.write(f"Equipe: {', '.join(st.session_state.temp_equipe)}")

        st.divider()
        st.write("📍 ENDEREÇOS DO ALVO")
        end_rua = st.text_input("Endereço (Rua, Nº, Bairro)")
        end_obs = st.text_area("Riscos e Pontos Críticos")
        foto_casa = st.file_uploader("Foto da Fachada")
        if st.form_submit_button("➕ Adicionar Endereço"):
            if end_rua: st.session_state.temp_ends.append({'rua': end_rua, 'obs': end_obs, 'foto': foto_casa})
        st.write(f"{len(st.session_state.temp_ends)} endereço(s) adicionado(s)")

        c_b1, c_b2 = st.columns(2)
        if c_b1.form_submit_button("CANCELAR / VOLTAR"): 
            st.session_state.temp_equipe = []; st.session_state.temp_ends = []; mudar_view('painel')
        
        if c_b2.form_submit_button("✅ SALVAR ALVO E GERAR PDF"):
            novo_alvo = {
                'nome': nome, 'vulgo': vulgo, 'mandado': mandado, 'foto': foto_alvo,
                'equipe': st.session_state.temp_equipe, 'enderecos': st.session_state.temp_ends
            }
            st.session_state.alvos.append(novo_alvo)
            
            # Gerar PDF
            pdf = BriefingPDF()
            for idx_a, alvo in enumerate(st.session_state.alvos):
                for idx_e, ed in enumerate(alvo['enderecos']):
                    pdf.add_page()
                    pdf.header_fiel(st.session_state.missao)
                    
                    # Banner do Alvo
                    pdf.set_fill_color(26, 58, 108)
                    pdf.rect(10, 58, 190, 15, 'F')
                    pdf.set_text_color(255, 255, 255)
                    pdf.set_xy(12, 60); pdf.set_font("Arial", 'B', 14)
                    pdf.cell(100, 10, f"ALVO: {alvo['nome'].upper()}", 0, 0)
                    pdf.set_font("Arial", 'B', 8); pdf.cell(80, 10, alvo['mandado'].upper(), 0, 1, 'R')

                    # Fotos
                    if alvo['foto']: 
                        img_a = Image.open(alvo['foto']).save("t_alvo.jpg")
                        pdf.image("t_alvo.jpg", 10, 75, 93, 65)
                    if ed['foto']:
                        img_e = Image.open(ed['foto']).save("t_casa.jpg")
                        pdf.image("t_casa.jpg", 105, 75, 95, 65)

                    # Info Tática
                    pdf.set_xy(10, 145); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 8)
                    pdf.cell(95, 8, "INTELIGÊNCIA ESTRATÉGICA", 0, 0)
                    pdf.cell(95, 8, "LOGÍSTICA DE EQUIPE", 0, 1)
                    pdf.set_font("Arial", '', 7)
                    pdf.multi_cell(95, 4, f"LOCAL: {ed['rua'].upper()}\nRISCOS: {ed['obs'].upper()}")
                    pdf.set_xy(105, 153)
                    pdf.multi_cell(95, 4, f"EQUIPE: {', '.join(alvo['equipe'])}")

                    # QR Code com ROTA TÁTICA
                    # Rota: Ponto Encontro -> Endereço Alvo
                    rota_url = f"https://www.google.com/maps/dir/{st.session_state.missao['ponto'].replace(' ','+')}/{ed['rua'].replace(' ','+')}"
                    qr = qrcode.make(rota_url).save("t_qr.png")
                    pdf.image("t_qr.png", 10, 185, 25, 25)
                    pdf.set_xy(37, 190); pdf.set_font("Arial", 'B', 7)
                    pdf.cell(100, 5, "ROTA GPS TÁTICA (PONTO ENCONTRO -> ALVO)", 0, 1)
                    
                    pdf.draw_footer_fiel(pdf.page_no())

            pdf_out = pdf.output(dest='S').encode('latin-1', 'replace')
            st.download_button("⬇️ BAIXAR BRIEFING PDF", data=pdf_out, file_name="Briefing_Ops.pdf")
            st.session_state.temp_equipe = []; st.session_state.temp_ends = []
