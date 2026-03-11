import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import io
from datetime import datetime
import urllib.parse

# --- CONFIGURAÇÃO VISUAL TÁTICA ---
st.set_page_config(layout="wide", page_title="SISTEMA OPS - TÁTICO")

st.markdown("""
    <style>
    .stApp { background-color: #050a14; color: #ffffff; }
    
    /* Painel da Operação */
    .op-header { 
        background-color: #0b111b; 
        border: 2px solid #1e3a8a; 
        padding: 25px; 
        border-radius: 20px; 
        margin-bottom: 25px; 
    }
    
    /* Ficha de Alvos no Painel */
    .alvo-card { 
        background-color: #0f172a; 
        border-left: 8px solid #2563eb; 
        padding: 20px; 
        border-radius: 12px; 
        margin-bottom: 15px;
        border: 1px solid #1e293b;
    }
    
    label { color: #60a5fa !important; font-weight: bold !important; font-size: 13px !important; }
    input, textarea, select { background-color: #161e2c !important; color: white !important; border: 1px solid #374151 !important; }
    
    .stButton>button { 
        background-color: #2563eb !important; 
        color: white !important; 
        font-weight: bold !important; 
        border-radius: 6px !important;
        border: none !important;
    }
    
    .badge-vtr { background-color: #1e3a8a; color: #60a5fa; padding: 4px 12px; border-radius: 4px; font-weight: bold; border: 1px solid #3b82f6; }
    .badge-hora { background-color: #2e1a05; color: #f59e0b; padding: 4px 12px; border-radius: 20px; font-weight: bold; border: 1px solid #f59e0b; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE DADOS ---
if 'alvos' not in st.session_state: st.session_state.alvos = []
if 'missao' not in st.session_state: 
    st.session_state.missao = {
        'nome': 'Operação Cerberus', 'unidade': 'SIG - JABOTICABAL', 
        'ponto': 'Rua Antonio Freitas', 'data_br': '11/03/2026 05:30', 
        'h_hora': '11/03/2026 06:00', 'resumo': ''
    }
if 'view' not in st.session_state: st.session_state.view = 'painel'

# --- CLASSE DO PDF (FIEL AO MODELO ORIGINAL) ---
class BriefingPDF(FPDF):
    def header_op(self, missao):
        self.set_fill_color(0, 0, 0)
        self.rect(10, 10, 190, 8, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", 'B', 8)
        self.cell(190, 8, "S I G I L O S O   -   D O C U M E N T O   D E   I N T E L I G Ê N C I A   -   R E S T R I T O", 0, 1, 'C')
        self.set_text_color(0, 0, 0)
        self.ln(2)
        self.set_font("Arial", 'B', 22)
        self.cell(140, 10, missao['nome'].upper(), 0, 0)
        self.set_xy(160, 20); self.set_font("Arial", 'B', 10); self.cell(40, 12, missao['unidade'].upper(), 1, 1, 'C')
        self.set_xy(10, 42); self.set_font("Arial", 'B', 6)
        self.cell(60, 12, f"PONTO DE ENCONTRO: {missao['ponto'].upper()}", 1)
        self.cell(50, 12, f"BRIEFING: {missao['data_br']}", 1)
        self.cell(40, 12, f"H-HORA: {missao['h_hora']}", 1)
        self.cell(40, 12, f"ID MISSÃO: #740599", 1)

    def draw_footer_fiel(self):
        self.set_xy(10, 210); self.set_font("Arial", 'B', 8)
        self.cell(190, 8, "RELATÓRIO DE OCORRÊNCIA E APREENSÕES DE CAMPO", 'T', 1, 'C')
        for _ in range(3): self.cell(190, 6, "_"*110, 0, 1)
        self.ln(5); self.set_font("Arial", 'B', 7)
        self.cell(60, 5, "CHECKLIST DE DISPOSITIVOS (IMEI/SN)", 0, 1)
        for _ in range(3): self.cell(100, 4, "_"*60, 0, 1)

# --- TELA 1: PAINEL PRINCIPAL ---
if st.session_state.view == 'painel':
    st.markdown('<div class="op-header">', unsafe_allow_html=True)
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown(f"<h1>{st.session_state.missao['nome'].upper()} <span style='cursor:pointer; font-size:22px;' onclick='window.location.reload();'>✏️</span></h1>", unsafe_allow_html=True)
        st.markdown(f"📍 {st.session_state.missao['ponto']} | <span class='badge-hora'>H-HORA: {st.session_state.missao['h_hora']}</span>", unsafe_allow_html=True)
    with c2:
        if st.button("➕ NOVO ALVO"): st.session_state.view = 'novo_alvo'; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✏️ EDITAR DADOS DA OPERAÇÃO"): st.session_state.view = 'edit_missao'; st.rerun()

    st.divider()
    
    # LISTA DE ALVOS
    if not st.session_state.alvos:
        st.info("Nenhum alvo cadastrado no painel.")
    else:
        for idx, alvo in enumerate(st.session_state.alvos):
            with st.container():
                st.markdown(f"""
                <div class='alvo-card'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <h2 style='margin:0;'>{alvo['nome'].upper()}</h2>
                        <span class='badge-vtr'>VTR: {alvo['vtr'].upper()}</span>
                    </div>
                    <p style='margin:5px 0;'><b>VULGO:</b> {alvo['vulgo'].upper()} | <b>MANDADO:</b> {alvo['tipo'].upper()}</p>
                    <p style='color:#94a3b8; font-size:12px;'><b>EQUIPE:</b> {', '.join(alvo['equipe'])}</p>
                    <p style='color:#3b82f6; font-size:12px;'>📍 {len(alvo['enderecos'])} endereço(s) vinculado(s)</p>
                </div>
                """, unsafe_allow_html=True)

    if st.session_state.alvos:
        st.divider()
        if st.button("🚀 GERAR PDF DE TODOS OS ALVOS"):
            pdf = BriefingPDF()
            for alvo in st.session_state.alvos:
                for idx_e, ed in enumerate(alvo['enderecos']):
                    pdf.add_page()
                    pdf.header_op(st.session_state.missao)
                    
                    # Banner do Alvo
                    pdf.set_fill_color(26, 58, 108); pdf.rect(10, 58, 190, 15, 'F')
                    pdf.set_text_color(255, 255, 255); pdf.set_xy(12, 60); pdf.set_font("Arial", 'B', 14)
                    pdf.cell(100, 10, f"ALVO: {alvo['nome'].upper()} | VTR: {alvo['vtr'].upper()}")
                    
                    # Fotos
                    if alvo['foto_alvo']:
                        pdf.image(alvo['foto_alvo'], 10, 75, 93, 65)
                    if ed['foto']:
                        pdf.image(ed['foto'], 105, 75, 95, 65)

                    # Rota e QR Code
                    rota_url = f"https://www.google.com/maps/dir/{urllib.parse.quote(st.session_state.missao['ponto'])}/{urllib.parse.quote(ed['rua'])}"
                    qr = qrcode.make(rota_url)
                    qr_img = io.BytesIO()
                    qr.save(qr_img, format='PNG')
                    pdf.image(qr_img, 10, 180, 25, 25)
                    
                    pdf.draw_footer_fiel()
            
            # CORREÇÃO DO ERRO DO PDF
            pdf_bytes = pdf.output()
            if isinstance(pdf_bytes, bytearray):
                pdf_bytes = bytes(pdf_bytes)
            
            st.download_button("⬇️ BAIXAR PDF COMPLETO", data=pdf_bytes, file_name="Dossie_Tatico.pdf", mime="application/pdf")

# --- TELA 2: EDITAR MISSÃO ---
elif st.session_state.view == 'edit_missao':
    st.title("🖊️ EDITAR DADOS DA OPERAÇÃO")
    with st.form("edit_op"):
        nome_op = st.text_input("Nome da Operação", st.session_state.missao['nome'])
        unidade_op = st.text_input("Equipe Responsável (Unidade)", st.session_state.missao['unidade'])
        ponto_op = st.text_input("Endereço do Ponto de Encontro", st.session_state.missao['ponto'])
        c1, c2 = st.columns(2)
        data_op = c1.text_input("Horário Briefing", st.session_state.missao['data_br'])
        h_hora_op = c2.text_input("H-Hora", st.session_state.missao['h_hora'])
        resumo_op = st.text_area("Resumo / Diretrizes da Missão", st.session_state.missao['resumo'])
        
        cb1, cb2 = st.columns(2)
        if cb1.form_submit_button("CANCELAR"): st.session_state.view = 'painel'; st.rerun()
        if cb2.form_submit_button("SALVAR ALTERAÇÕES"):
            st.session_state.missao.update({'nome': nome_op, 'unidade': unidade_op, 'ponto': ponto_op, 'data_br': data_op, 'h_hora': h_hora_op, 'resumo': resumo_op})
            st.session_state.view = 'painel'; st.rerun()

# --- TELA 3: NOVO ALVO TÁTICO ---
elif st.session_state.view == 'novo_alvo':
    st.title("🎯 NOVO ALVO TÁTICO")
    
    if 't_equipe' not in st.session_state: st.session_state.t_equipe = []
    if 't_ends' not in st.session_state: st.session_state.t_ends = []

    c1, c2 = st.columns(2)
    with c1:
        st.write("### 👤 QUALIFICAÇÃO")
        nome_a = st.text_input("Nome Completo")
        vulgo_a = st.text_input("Vulgo / Apelido")
        tipo_a = st.selectbox("Tipo de Mandado", ["Busca e Apreensão", "Prisão Preventiva"])
        vtr_a = st.text_input("Viatura (VTR)")
        f_alvo = st.file_uploader("Retrato do Alvo (IDENTIFICAÇÃO)")
    
    with c2:
        st.write("### 👥 COMPOSIÇÃO DA EQUIPE")
        membro = st.text_input("Adicionar Policial")
        if st.button("➕"):
            if membro: st.session_state.t_equipe.append(membro)
        st.info(f"Equipe Atual: {', '.join(st.session_state.t_equipe)}")
        obs_a = st.text_area("Observações Táticas / Riscos", height=150)

    st.divider()
    st.write("### 📍 ENDEREÇOS E FACHADA")
    end_rua = st.text_input("Endereço Completo (Rua, Nº, Bairro)")
    
    if end_rua:
        st.markdown(f"🔗 [📍 Verificar no Google Maps](https://www.google.com/maps/search/{urllib.parse.quote(end_rua)})")
    
    f_casa = st.file_uploader("Foto da Fachada (PERÍMETRO)")
    
    if st.button("➕ ADICIONAR ESTE ENDEREÇO"):
        if end_rua:
            st.session_state.t_ends.append({'rua': end_rua, 'foto': f_casa})
            st.success(f"Endereço vinculado. Total: {len(st.session_state.t_ends)}")

    st.divider()
    b1, b2 = st.columns(2)
    if b1.button("CANCELAR"): st.session_state.t_equipe = []; st.session_state.t_ends = []; st.session_state.view = 'painel'; st.rerun()
    if b2.button("✅ SALVAR ALVO NO PAINEL"):
        if nome_a:
            st.session_state.alvos.append({
                'nome': nome_a, 'vulgo': vulgo_a, 'tipo': tipo_a, 'vtr': vtr_a,
                'equipe': st.session_state.t_equipe, 'enderecos': st.session_state.t_ends,
                'foto_alvo': f_alvo, 'obs': obs_a
            })
            st.session_state.t_equipe = []; st.session_state.t_ends = []; st.session_state.view = 'painel'; st.rerun()
