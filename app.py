import streamlit as st
from fpdf import FPDF
import qrcode
from PIL import Image
import io
import urllib.parse
from datetime import datetime

# --- CONFIGURAÇÃO VISUAL TÁTICA ---
st.set_page_config(layout="wide", page_title="SISTEMA OPS - JABOTICABAL")

st.markdown("""
    <style>
    .stApp { background-color: #050a14; color: #ffffff; }
    
    /* Header da Operação */
    .op-header { background-color: #0b111b; border: 2px solid #1e3a8a; padding: 25px; border-radius: 20px; margin-bottom: 25px; }
    
    /* Card de Pré-visualização do Alvo (IGUAL IMAGEM 2) */
    .alvo-card-preview {
        background-color: #0b1424;
        border: 1px solid #1e293b;
        border-radius: 25px;
        padding: 20px;
        margin-bottom: 20px;
        max-width: 450px;
    }
    .id-badge { background-color: #1e3a8a; color: #60a5fa; padding: 2px 10px; border-radius: 5px; font-size: 12px; font-weight: bold; }
    .mandado-badge { background-color: #2563eb; color: white; padding: 5px 15px; border-radius: 5px; font-size: 13px; font-weight: bold; margin-top: 10px; display: inline-block; }
    
    /* Botões */
    .stButton>button { background-color: #2563eb !important; color: white !important; font-weight: bold !important; border-radius: 8px !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE DADOS ---
if 'alvos' not in st.session_state: st.session_state.alvos = []
if 'missao' not in st.session_state: 
    st.session_state.missao = {
        'nome': 'OPERAÇÃO CERBERUS', 'unidade': 'SIG - JABOTICABAL', 
        'ponto': 'Rua Antonio Freitas', 'data_br': '11/03/2026 05:30', 
        'h_hora': '11/03/2026 06:00', 'resumo': ''
    }
if 'view' not in st.session_state: st.session_state.view = 'painel'

# --- CLASSE DO PDF (LAYOUT FIEL AO BRIEFING POLICIAL) ---
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
        self.cell(140, 12, missao['nome'].upper(), 0, 0)
        
        self.set_xy(160, 20); self.set_font("Arial", 'B', 10); self.cell(40, 12, missao['unidade'].upper(), 1, 1, 'C')
        
        self.set_xy(10, 42); self.set_font("Arial", 'B', 6)
        self.cell(60, 12, f"PONTO DE ENCONTRO: {missao['ponto'].upper()}", 1)
        self.cell(50, 12, f"BRIEFING: {missao['data_br']}", 1)
        self.cell(40, 12, f"H-HORA: {missao['h_hora']}", 1)
        self.cell(40, 12, f"ID MISSÃO: #740599", 1)

    def draw_footer_fiel(self):
        self.set_xy(10, 215); self.set_font("Arial", 'B', 8)
        self.cell(190, 8, "RELATÓRIO DE OCORRÊNCIA E APREENSÕES DE CAMPO", 'T', 1, 'C')
        for _ in range(4): self.cell(190, 6, "_"*110, 0, 1)
        self.ln(5); self.set_font("Arial", 'B', 7)
        self.cell(60, 5, "CHECKLIST DE DISPOSITIVOS (IMEI/SN)", 0, 1)
        for _ in range(3): self.cell(100, 5, "_"*60, 0, 1)

# --- TELA 1: PAINEL PRINCIPAL ---
if st.session_state.view == 'painel':
    st.markdown('<div class="op-header">', unsafe_allow_html=True)
    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown(f"<h1>{st.session_state.missao['nome'].upper()}</h1>", unsafe_allow_html=True)
        st.markdown(f"📍 {st.session_state.missao['ponto']} | <span class='badge-hora'>H-HORA: {st.session_state.missao['h_hora']}</span>", unsafe_allow_html=True)
    with c2:
        if st.button("➕ NOVO ALVO"): st.session_state.view = 'novo_alvo'; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✏️ EDITAR DADOS DA OPERAÇÃO"): st.session_state.view = 'edit_missao'; st.rerun()

    st.divider()
    
    # LISTA DE ALVOS (VISUAL IGUAL IMAGEM 2)
    if not st.session_state.alvos:
        st.info("Nenhum alvo cadastrado.")
    else:
        col_list = st.columns(3)
        for idx, alvo in enumerate(st.session_state.alvos):
            with col_list[idx % 3]:
                st.markdown(f"""
                <div class="alvo-card-preview">
                    <div style="text-align:center; background:#161e2c; height:150px; border-radius:15px; margin-bottom:15px;">
                        <span style="line-height:150px; color:#374151;">📸 FOTO DO ALVO</span>
                    </div>
                    <span class="id-badge">ID: {idx + 6537}</span>
                    <h2 style="margin:5px 0;">{alvo['nome'].upper()}</h2>
                    <div class="mandado-badge">{alvo['tipo'].upper()}</div>
                    <div style="margin-top:15px; font-size:14px; color:#94a3b8;">
                        📍 {alvo['enderecos'][0]['rua'] if alvo['enderecos'] else 'Sem local'}<br>
                        👤 Responsável: {alvo['responsavel']}<br>
                        👥 EQUIPE: {', '.join(alvo['equipe']) if alvo['equipe'] else 'Nenhum membro'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # QR Code visível na prévia (Imagem 2)
                if alvo['enderecos']:
                    end = alvo['enderecos'][0]['rua']
                    rota_link = f"https://www.google.com/maps/dir/{urllib.parse.quote(st.session_state.missao['ponto'])}/{urllib.parse.quote(end)}"
                    qr_prev = qrcode.make(rota_link)
                    buf = io.BytesIO()
                    qr_prev.save(buf, format='PNG')
                    st.image(buf, width=100, caption="ROTA TÁTICA")

    if st.session_state.alvos:
        st.divider()
        if st.button("🚀 FINALIZAR E GERAR PDF"):
            pdf = BriefingPDF()
            for alvo in st.session_state.alvos:
                for ed in alvo['enderecos']:
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

                    # INFORMAÇÕES DO ALVO NO PDF (Resolvendo o problema de não aparecer nada)
                    pdf.set_xy(10, 145); pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", 'B', 9)
                    pdf.cell(95, 8, "INTELIGÊNCIA ESTRATÉGICA", 0, 0)
                    pdf.cell(95, 8, "LOGÍSTICA DE EQUIPE", 0, 1)
                    
                    pdf.set_font("Arial", '', 7)
                    pdf.set_xy(10, 153); pdf.multi_cell(95, 4, f"LOCAL: {ed['rua'].upper()}\nRISCOS: {ed['obs'].upper()}")
                    pdf.set_xy(105, 153); pdf.multi_cell(95, 4, f"EQUIPE: {', '.join(alvo['equipe']).upper()}\nRESPONSÁVEL: {alvo['responsavel'].upper()}")

                    # QR Code com texto (Imagem 3)
                    rota_url = f"https://www.google.com/maps/dir/{urllib.parse.quote(st.session_state.missao['ponto'])}/{urllib.parse.quote(ed['rua'])}"
                    qr = qrcode.make(rota_url)
                    qr_buf = io.BytesIO()
                    qr.save(qr_buf, format='PNG')
                    pdf.image(qr_buf, 10, 185, 25, 25)
                    pdf.set_xy(37, 190); pdf.set_font("Arial", 'B', 7)
                    pdf.cell(100, 5, "ROTA GPS TÁTICA", 0, 1)
                    pdf.set_font("Arial", '', 6)
                    pdf.set_x(37); pdf.cell(150, 4, "Escaneie o QR Code com seu celular para abrir a rota no Google Maps automaticamente.", 0, 1)
                    pdf.set_x(37); pdf.cell(150, 4, f"ORIGEM: {st.session_state.missao['ponto']} -> DESTINO: {ed['rua']}", 0, 1)
                    
                    pdf.draw_footer_fiel()
            
            # GERAÇÃO SEGURA
            pdf_bytes = pdf.output(dest='S').encode('latin-1', 'replace')
            st.download_button("⬇️ BAIXAR PDF COMPLETO", data=pdf_bytes, file_name="Briefing_Tatico.pdf", mime="application/pdf")

# --- TELA 2: EDITAR MISSÃO ---
elif st.session_state.view == 'edit_missao':
    st.markdown("<h2>🖊️ EDITAR DADOS DA OPERAÇÃO</h2>", unsafe_allow_html=True)
    with st.form("edit_op"):
        nome_op = st.text_input("Nome da Operação", st.session_state.missao['nome'])
        unidade_op = st.text_input("Unidade Responsável", st.session_state.missao['unidade'])
        ponto_op = st.text_input("Endereço do Briefing", st.session_state.missao['ponto'])
        c1, c2 = st.columns(2)
        dt_br = c1.text_input("Horário Briefing", st.session_state.missao['data_br'])
        h_h = c2.text_input("H-Hora", st.session_state.missao['h_hora'])
        
        if st.form_submit_button("Salvar Alterações"):
            st.session_state.missao.update({'nome': nome_op, 'unidade': unidade_op, 'ponto': ponto_op, 'data_br': dt_br, 'h_hora': h_h})
            st.session_state.view = 'painel'; st.rerun()

# --- TELA 3: NOVO ALVO TÁTICO ---
elif st.session_state.view == 'novo_alvo':
    st.markdown("<h2>🎯 NOVO ALVO TÁTICO</h2>", unsafe_allow_html=True)
    
    if 't_equipe' not in st.session_state: st.session_state.t_equipe = []
    if 't_ends' not in st.session_state: st.session_state.t_ends = []

    c1, c2 = st.columns(2)
    with c1:
        st.write("### 👤 QUALIFICAÇÃO")
        nome_a = st.text_input("Nome Completo")
        vulgo_a = st.text_input("Vulgo")
        tipo_a = st.selectbox("Mandado", ["Busca e Apreensão", "Prisão Preventiva"])
        vtr_a = st.text_input("Viatura (VTR)")
        f_alvo = st.file_uploader("Foto Alvo")
    
    with c2:
        st.write("### 👥 EQUIPE")
        resp = st.text_input("Responsável (Delegado/Agente)")
        membro = st.text_input("Adicionar Policial")
        if st.button("➕ INTEGRANTE"):
            if membro: st.session_state.t_equipe.append(membro)
        st.info(f"Equipe: {', '.join(st.session_state.t_equipe)}")

    st.divider()
    st.write("### 📍 ENDEREÇOS")
    end_rua = st.text_input("Rua, Número, Bairro")
    obs_rua = st.text_area("Riscos/Obs")
    f_casa = st.file_uploader("Foto Casa")
    if st.button("➕ ENDEREÇO"):
        if end_rua: st.session_state.t_ends.append({'rua': end_rua, 'obs': obs_rua, 'foto': f_casa})
    
    colb1, colb2 = st.columns(2)
    if colb1.button("VOLTAR"): st.session_state.t_equipe = []; st.session_state.t_ends = []; st.session_state.view = 'painel'; st.rerun()
    if colb2.button("✅ SALVAR ALVO"):
        st.session_state.alvos.append({
            'nome': nome_a, 'vulgo': vulgo_a, 'tipo': tipo_a, 'vtr': vtr_a, 'responsavel': resp,
            'equipe': st.session_state.t_equipe, 'enderecos': st.session_state.t_ends, 'foto_alvo': f_alvo
        })
        st.session_state.t_equipe = []; st.session_state.t_ends = []; st.session_state.view = 'painel'; st.rerun()
