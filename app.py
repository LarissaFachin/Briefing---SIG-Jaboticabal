import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import io
import os
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL TÁTICA AVANÇADA ---
st.set_page_config(layout="wide", page_title="SISTEMA OPS - TÁTICO")

st.markdown("""
    <style>
    .stApp { background-color: #050a14; color: #ffffff; }
    
    /* Cabeçalho da Operação */
    .op-header { 
        background-color: #0b111b; 
        border: 2px solid #1e3a8a; 
        padding: 25px; 
        border-radius: 20px; 
        margin-bottom: 25px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.5); 
    }
    
    /* Cards de Alvos no Painel */
    .alvo-card { 
        background-color: #0f172a; 
        border-left: 8px solid #2563eb; 
        padding: 20px; 
        border-radius: 12px; 
        margin-bottom: 15px;
        border-top: 1px solid #1e293b;
        border-right: 1px solid #1e293b;
        border-bottom: 1px solid #1e293b;
    }
    
    /* Estilo de Inputs e Labels */
    label { color: #60a5fa !important; font-weight: bold !important; font-size: 13px !important; text-transform: uppercase; }
    input, textarea, select { background-color: #161e2c !important; color: white !important; border: 1px solid #374151 !important; }
    
    /* Botões */
    .stButton>button { 
        background-color: #2563eb !important; 
        color: white !important; 
        font-weight: bold !important; 
        border-radius: 6px !important; 
        border: none !important; 
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #1d4ed8 !important; transform: translateY(-2px); }
    
    .badge-vtr { background-color: #1e3a8a; color: #60a5fa; padding: 4px 12px; border-radius: 4px; font-weight: bold; border: 1px solid #3b82f6; }
    .badge-hora { background-color: #2e1a05; color: #f59e0b; padding: 4px 12px; border-radius: 20px; font-weight: bold; border: 1px solid #f59e0b; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADOS ---
if 'alvos' not in st.session_state: st.session_state.alvos = []
if 'missao' not in st.session_state: 
    st.session_state.missao = {
        'nome': 'Operação Cerberus', 'unidade': 'DELEGACIA DO MUNICÍPIO', 
        'ponto': 'Rua Antonio Freitas', 'data_br': '11/03/2026 05:30', 
        'h_hora': '11/03/2026 06:00', 'resumo': ''
    }
if 'view' not in st.session_state: st.session_state.view = 'painel'

# --- CLASSE DO PDF (LAYOUT FIEL AO ANEXO) ---
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
        self.cell(40, 12, f"ID MISSÃO: #{id(missao)%100000}", 1)

    def draw_footer_fiel(self):
        self.set_xy(10, 210); self.set_font("Arial", 'B', 8)
        self.cell(190, 8, "RELATÓRIO DE OCORRÊNCIA E APREENSÕES DE CAMPO", 'T', 1, 'C')
        for _ in range(3): self.cell(190, 6, "_"*110, 0, 1)
        self.ln(5); self.set_font("Arial", 'B', 7)
        self.cell(60, 5, "CHECKLIST DE DISPOSITIVOS (IMEI/SN)", 0, 1)
        for _ in range(3): self.cell(100, 4, "_"*60, 0, 1)

# --- NAVEGAÇÃO ---
def ir_para(v): st.session_state.view = v

# --- TELA 1: PAINEL PRINCIPAL ---
if st.session_state.view == 'painel':
    st.markdown('<div class="op-header">', unsafe_allow_html=True)
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown(f"<h1>{st.session_state.missao['nome'].upper()} <span style='cursor:pointer; font-size:20px;' onclick='ir_para(\"edit_missao\")'>✏️</span></h1>", unsafe_allow_html=True)
        st.markdown(f"📍 {st.session_state.missao['ponto']} | <span class='badge-hora'>H-HORA: {st.session_state.missao['h_hora']}</span>", unsafe_allow_html=True)
    with c2:
        if st.button("➕ NOVO ALVO"): ir_para('novo_alvo'); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✏️ EDITAR DADOS GERAIS DA MISSÃO"): ir_para('edit_missao'); st.rerun()

    st.divider()
    
    # LISTA DE ALVOS CADASTRADOS (CARDS PROFISSIONAIS)
    if not st.session_state.alvos:
        st.info("Nenhum alvo cadastrado no painel operacional.")
    else:
        for idx, alvo in enumerate(st.session_state.alvos):
            with st.container():
                st.markdown(f"""
                <div class='alvo-card'>
                    <div style='display:flex; justify-content:space-between; align-items:center;'>
                        <h2 style='margin:0;'>{alvo['nome'].upper()}</h2>
                        <span class='badge-vtr'>VTR: {alvo['viatura'].upper()}</span>
                    </div>
                    <p style='margin:5px 0;'><b>VULGO:</b> {alvo['vulgo'].upper()} | <b>MANDADO:</b> {alvo['tipo'].upper()}</p>
                    <p style='color:#94a3b8; font-size:12px;'><b>EQUIPE:</b> {', '.join(alvo['equipe'])}</p>
                    <p style='color:#3b82f6; font-size:12px;'>📍 {len(alvo['enderecos'])} endereço(s) vinculado(s)</p>
                </div>
                """, unsafe_allow_html=True)

    if st.session_state.alvos:
        st.divider()
        if st.button("🚀 FINALIZAR E GERAR PDF COMPLETO"):
            pdf = BriefingPDF()
            for alvo in st.session_state.alvos:
                for idx_e, ed in enumerate(alvo['enderecos']):
                    pdf.add_page()
                    pdf.header_op(st.session_state.missao)
                    
                    # Banner Alvo
                    pdf.set_fill_color(26, 58, 108); pdf.rect(10, 58, 190, 15, 'F')
                    pdf.set_text_color(255, 255, 255); pdf.set_xy(12, 60); pdf.set_font("Arial", 'B', 14)
                    pdf.cell(100, 10, f"ALVO: {alvo['nome'].upper()} | VTR: {alvo['viatura'].upper()}")
                    
                    # Fotos (Lado a Lado)
                    if alvo['foto_alvo']:
                        img_alvo = Image.open(alvo['foto_alvo']).convert("RGB")
                        img_alvo.save("temp_alvo.jpg")
                        pdf.image("temp_alvo.jpg", 10, 75, 93, 65)
                    
                    if ed['foto']:
                        img_casa = Image.open(ed['foto']).convert("RGB")
                        img_casa.save(f"temp_casa_{idx_e}.jpg")
                        pdf.image(f"temp_casa_{idx_e}.jpg", 105, 75, 95, 65)

                    # QR Code com Rota
                    rota_url = f"https://www.google.com/maps/dir/{st.session_state.missao['ponto'].replace(' ','+')}/{ed['rua'].replace(' ','+')}"
                    qr = qrcode.make(rota_url).save("temp_qr.png")
                    pdf.image("temp_qr.png", 10, 180, 25, 25)
                    pdf.set_xy(38, 185); pdf.set_font("Arial", 'B', 8); pdf.set_text_color(0,0,0)
                    pdf.cell(100, 5, "ROTA: PONTO ENCONTRO -> ALVO")
                    
                    pdf.draw_footer_fiel()
            
            # Geração segura do PDF em bytes
            pdf_bytes = pdf.output()
            st.download_button("⬇️ BAIXAR DOSSIÊ OPERACIONAL", data=pdf_bytes, file_name="Dossie_Tatico.pdf", mime="application/pdf")

# --- TELA 2: EDITAR MISSÃO ---
elif st.session_state.view == 'edit_missao':
    st.markdown("<h2>🖊️ EDITAR DADOS DA OPERAÇÃO</h2>", unsafe_allow_html=True)
    with st.form("form_edit_op"):
        nome_op = st.text_input("Nome da Operação", st.session_state.missao['nome'])
        unidade_op = st.text_input("Unidade Responsável", st.session_state.missao['unidade'])
        ponto_op = st.text_input("Endereço do Ponto de Encontro", st.session_state.missao['ponto'])
        c1, c2 = st.columns(2)
        data_op = c1.text_input("Horário Briefing", st.session_state.missao['data_br'])
        h_hora_op = c2.text_input("H-Hora", st.session_state.missao['h_hora'])
        resumo_op = st.text_area("Diretrizes da Missão", st.session_state.missao['resumo'])
        
        c_b1, c_b2 = st.columns(2)
        if c_b1.form_submit_button("CANCELAR"): ir_para('painel'); st.rerun()
        if c_b2.form_submit_button("SALVAR ALTERAÇÕES"):
            st.session_state.missao.update({'nome': nome_op, 'unidade': unidade_op, 'ponto': ponto_op, 'data_br': data_op, 'h_hora': h_hora_op, 'resumo': resumo_op})
            ir_para('painel'); st.rerun()

# --- TELA 3: NOVO ALVO TÁTICO ---
elif st.session_state.view == 'novo_alvo':
    st.markdown("<h2>🎯 NOVO ALVO TÁTICO</h2>", unsafe_allow_html=True)
    
    if 'temp_equipe' not in st.session_state: st.session_state.temp_equipe = []
    if 'temp_ends' not in st.session_state: st.session_state.temp_ends = []

    c1, c2 = st.columns(2)
    with c1:
        st.write("### 👤 QUALIFICAÇÃO")
        nome_a = st.text_input("Nome Completo")
        vulgo_a = st.text_input("Vulgo / Apelido")
        tipo_a = st.selectbox("Tipo de Mandado", ["Busca e Apreensão", "Prisão Preventiva"])
        vtr_a = st.text_input("Viatura (VTR)")
        foto_alvo = st.file_uploader("Retrato do Alvo (IDENTIFICAÇÃO)")
    
    with c2:
        st.write("### 👥 EQUIPE")
        membro = st.text_input("Adicionar Policial")
        if st.button("➕ INTEGRANTE"):
            if membro: st.session_state.temp_equipe.append(membro)
        st.info(f"Equipe Atual: {', '.join(st.session_state.temp_equipe)}")
        obs_a = st.text_area("Observações / Pontos Críticos", height=120)

    st.divider()
    st.write("### 📍 LOGÍSTICA DE ENDEREÇOS")
    end_rua = st.text_input("Endereço Completo (Rua, Nº, Bairro, Cidade)")
    
    # Vínculo com Google Maps
    if end_rua:
        st.markdown(f"🔗 [Verificar no Google Maps](https://www.google.com/maps/search/{end_rua.replace(' ', '+')})")
    
    foto_casa = st.file_uploader("Foto da Fachada (PERÍMETRO)")
    
    if st.button("➕ ADICIONAR ESTE ENDEREÇO"):
        if end_rua:
            st.session_state.temp_ends.append({'rua': end_rua, 'foto': foto_casa})
            st.success(f"Endereço adicionado. Total: {len(st.session_state.temp_ends)}")

    st.divider()
    cb1, cb2 = st.columns(2)
    if cb1.button("CANCELAR"): st.session_state.temp_equipe = []; st.session_state.temp_ends = []; ir_para('painel'); st.rerun()
    if cb2.button("✅ SALVAR ALVO NO PAINEL"):
        if nome_a:
            st.session_state.alvos.append({
                'nome': nome_a, 'vulgo': vulgo_a, 'tipo': tipo_a, 'viatura': vtr_a,
                'equipe': st.session_state.temp_equipe, 'enderecos': st.session_state.temp_ends,
                'foto_alvo': foto_alvo, 'obs': obs_a
            })
            st.session_state.temp_equipe = []; st.session_state.temp_ends = []; ir_para('painel'); st.rerun()
