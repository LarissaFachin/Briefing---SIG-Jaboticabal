import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import io
import urllib.parse
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL DE ALTO CONTRASTE ---
st.set_page_config(layout="wide", page_title="SISTEMA OPS - TÁTICO", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Fundo escuro profundo para contraste */
    .stApp { background-color: #020617; color: #ffffff; }
    
    /* Labels (Títulos dos campos) - AGORA BEM VISÍVEIS */
    label { 
        color: #60a5fa !important; 
        font-weight: bold !important; 
        font-size: 15px !important; 
        text-transform: uppercase;
        margin-bottom: 10px !important;
    }
    
    /* Inputs (Caixas de texto) */
    .stTextInput>div>div>input, .stTextArea>div>textarea, .stSelectbox>div>div {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 2px solid #3b82f6 !important;
        border-radius: 8px !important;
        font-size: 16px !important;
    }

    /* Cards e Seções */
    .section-card {
        background-color: #0f172a;
        border: 1px solid #1e40af;
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 25px;
    }
    
    /* Botões */
    .stButton>button {
        background-color: #2563eb !important;
        color: white !important;
        font-weight: bold !important;
        height: 45px !important;
        border-radius: 8px !important;
        width: 100%;
    }
    
    .badge-vtr { background-color: #1e3a8a; color: #ffffff; padding: 5px 12px; border-radius: 5px; border: 1px solid #3b82f6; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE DADOS ---
if 'alvos' not in st.session_state: st.session_state.alvos = []
if 'missao' not in st.session_state: 
    st.session_state.missao = {
        'nome': 'OPERAÇÃO', 'unidade': 'SIG - JABOTICABAL', 
        'ponto': 'PONTO DE ENCONTRO', 'data_br': '11/03/2026 05:30', 
        'h_hora': '11/03/2026 06:00', 'resumo': ''
    }
if 'view' not in st.session_state: st.session_state.view = 'painel'
if 'temp_equipe' not in st.session_state: st.session_state.temp_equipe = []
if 'temp_ends' not in st.session_state: st.session_state.temp_ends = []

# --- MOTOR DO PDF ---
class BriefingPDF(FPDF):
    def header_op(self, missao):
        self.set_fill_color(0, 0, 0)
        self.rect(10, 10, 190, 8, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", 'B', 8)
        self.cell(190, 8, "S I G I L O S O   -   D O C U M E N T O   D E   I N T E L I G Ê N C I A   -   R E S T R I T O", 0, 1, 'C')
        self.set_text_color(0, 0, 0)
        self.ln(2)
        self.set_font("Arial", 'B', 20)
        self.cell(140, 12, missao['nome'].upper(), 0, 0)
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
    st.markdown(f"""
    <div class="section-card" style="border-left: 10px solid #2563eb;">
        <h1 style="margin:0;">{st.session_state.missao['nome'].upper()}</h1>
        <p style="color:#94a3b8; font-size:18px;">📍 {st.session_state.missao['ponto']} | 🕒 H-HORA: {st.session_state.missao['h_hora']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])
    if col_nav1.button("➕ NOVO ALVO"): st.session_state.view = 'novo_alvo'; st.rerun()
    if col_nav2.button("✏️ EDITAR OPERAÇÃO"): st.session_state.view = 'edit_missao'; st.rerun()
    
    st.divider()
    
    if not st.session_state.alvos:
        st.info("Aguardando cadastro de alvos...")
    else:
        for a in st.session_state.alvos:
            st.markdown(f"""
            <div class="section-card">
                <div style="display:flex; justify-content:space-between;">
                    <h2 style="margin:0; color:#3b82f6;">{a['nome'].upper()}</h2>
                    <span class="badge-vtr">VTR: {a['vtr'].upper()}</span>
                </div>
                <p><b>VULGO:</b> {a['vulgo']} | <b>EQUIPE:</b> {', '.join(a['equipe'])}</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🚀 GERAR DOSSIÊ PDF COMPLETO"):
            pdf = BriefingPDF()
            for alvo in st.session_state.alvos:
                for ed in alvo['enderecos']:
                    pdf.add_page()
                    pdf.header_op(st.session_state.missao)
                    
                    # Banner Alvo
                    pdf.set_fill_color(26, 58, 108); pdf.rect(10, 58, 190, 15, 'F')
                    pdf.set_text_color(255, 255, 255); pdf.set_xy(12, 60); pdf.set_font("Arial", 'B', 14)
                    pdf.cell(100, 10, f"ALVO: {alvo['nome'].upper()} | VTR: {alvo['vtr'].upper()}")
                    
                    # Fotos
                    if alvo['foto_alvo']:
                        pdf.image(alvo['foto_alvo'], 10, 75, 93, 65)
                    if ed['foto']:
                        pdf.image(ed['foto'], 105, 75, 95, 65)
                    
                    # Infos Táticas
                    pdf.set_xy(10, 145); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 9)
                    pdf.cell(95, 8, "INTELIGÊNCIA ESTRATÉGICA", 0, 0)
                    pdf.cell(95, 8, "LOGÍSTICA DE EQUIPE", 0, 1)
                    pdf.set_font("Arial", '', 7)
                    pdf.set_xy(10, 153); pdf.multi_cell(95, 4, f"LOCAL: {ed['rua'].upper()}\nRISCOS: {ed['obs'].upper()}")
                    pdf.set_xy(105, 153); pdf.multi_cell(95, 4, f"RESPONSÁVEL: {alvo['responsavel'].upper()}\nEQUIPE: {', '.join(alvo['equipe']).upper()}")

                    # QR Code Rota
                    rota_url = f"https://www.google.com/maps/dir/{urllib.parse.quote(st.session_state.missao['ponto'])}/{urllib.parse.quote(ed['rua'])}"
                    qr = qrcode.make(rota_url)
                    qr_img = io.BytesIO()
                    qr.save(qr_img, format='PNG')
                    pdf.image(qr_img, 10, 182, 25, 25)
                    pdf.set_xy(37, 187); pdf.set_font("Arial", 'B', 7); pdf.cell(100, 5, "ROTA GPS TÁTICA")
                    
                    pdf.draw_footer_fiel()
            
            st.download_button("⬇️ BAIXAR PDF", data=pdf.output(dest='S'), file_name="Briefing.pdf", mime="application/pdf")

# --- TELA 2: EDITAR MISSÃO ---
elif st.session_state.view == 'edit_missao':
    st.markdown("<h2>🖊️ EDITAR OPERAÇÃO</h2>", unsafe_allow_html=True)
    with st.container():
        st.session_state.missao['nome'] = st.text_input("NOME DA OPERAÇÃO", st.session_state.missao['nome'])
        st.session_state.missao['ponto'] = st.text_input("PONTO DE ENCONTRO", st.session_state.missao['ponto'])
        c1, c2 = st.columns(2)
        st.session_state.missao['data_br'] = c1.text_input("DATA/HORA BRIEFING", st.session_state.missao['data_br'])
        st.session_state.missao['h_hora'] = c2.text_input("H-HORA", st.session_state.missao['h_hora'])
        if st.button("SALVAR E VOLTAR"): st.session_state.view = 'painel'; st.rerun()

# --- TELA 3: NOVO ALVO TÁTICO ---
elif st.session_state.view == 'novo_alvo':
    st.markdown("<h2>🎯 NOVO ALVO TÁTICO</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.write("### 👤 QUALIFICAÇÃO")
        nome_a = st.text_input("NOME COMPLETO")
        vulgo_a = st.text_input("VULGO")
        tipo_a = st.selectbox("TIPO DE MANDADO", ["Busca e Apreensão", "Prisão Preventiva"])
        vtr_a = st.text_input("VIATURA (VTR)")
        resp_a = st.text_input("RESPONSÁVEL (DELEGADO/AGENTE)")
        f_alvo = st.file_uploader("FOTO DO ALVO")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.write("### 👥 EQUIPE")
        membro = st.text_input("NOME DO POLICIAL")
        if st.button("➕ ADICIONAR INTEGRANTE"):
            if membro: st.session_state.temp_equipe.append(membro)
        st.info(f"EQUIPE ESCALADA: {', '.join(st.session_state.temp_equipe)}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.write("### 📍 ENDEREÇOS E FACHADA")
    end_rua = st.text_input("ENDEREÇO (RUA, Nº, BAIRRO, CIDADE)")
    end_obs = st.text_area("OBSERVAÇÕES TÁTICAS / RISCOS")
    f_casa = st.file_uploader("FOTO DA FACHADA")
    
    if st.button("➕ INCLUIR ESTE ENDEREÇO"):
        if end_rua:
            st.session_state.temp_ends.append({'rua': end_rua, 'obs': end_obs, 'foto': f_casa})
            st.success(f"Endereço adicionado com sucesso! (Total: {len(st.session_state.temp_ends)})")
    
    if st.session_state.temp_ends:
        st.write("**Endereços inclusos:**")
        for e in st.session_state.temp_ends: st.write(f"- {e['rua']}")
    st.markdown('</div>', unsafe_allow_html=True)

    c_b1, c_b2 = st.columns(2)
    if c_b1.button("❌ CANCELAR"): 
        st.session_state.temp_equipe = []; st.session_state.temp_ends = []; st.session_state.view = 'painel'; st.rerun()
    if c_b2.button("✅ SALVAR ALVO NO PAINEL"):
        if nome_a and st.session_state.temp_ends:
            st.session_state.alvos.append({
                'nome': nome_a, 'vulgo': vulgo_a, 'tipo': tipo_a, 'vtr': vtr_a, 'responsavel': resp_a,
                'equipe': list(st.session_state.temp_equipe), 'enderecos': list(st.session_state.temp_ends),
                'foto_alvo': f_alvo
            })
            st.session_state.temp_equipe = []; st.session_state.temp_ends = []; st.session_state.view = 'painel'; st.rerun()
        else:
            st.error("Erro: Preencha o Nome e adicione pelo menos um Endereço.")
