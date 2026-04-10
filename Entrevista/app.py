import streamlit as st
from datetime import date

# 1. Configuración y Estilos de Impresión
st.set_page_config(page_title="Expediente Clínico D.S.P.", layout="wide")

st.markdown("""
    <style>
    /* Estilo para la pantalla */
    .main { background-color: #f0f2f6; }
    
    /* Estilo específico para IMPRESIÓN */
    @media print {
        .stButton, .stDownloadButton, footer, header, .stSidebar {
            display: none !important;
        }
        .report-container {
            border: none !important;
            box-shadow: none !important;
        }
    }
    
    .report-container {
        background-color: white;
        padding: 30px;
        border-radius: 5px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .header-clinico { text-align: center; line-height: 1.2; margin-bottom: 20px; }
    .seccion-titulo { 
        background-color: #1f4e79; 
        color: white; 
        padding: 8px; 
        margin-top: 15px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- INICIO DEL CUERPO DE LA APP ---
with st.container():
    st.markdown('<div class="report-container">', unsafe_allow_html=True)
    
    # Membrete Institucional [cite: 1-5]
    st.markdown("""
        <div class="header-clinico">
            <h3 style='margin:0;'>REPÚBLICA DE HONDURAS</h3>
            <h4 style='margin:0;'>SECRETARÍA DE SEGURIDAD | POLICÍA NACIONAL</h4>
            <h5 style='margin:0;'>DIRECCIÓN DE SANIDAD POLICIAL (D.S.P.)</h5>
            <p style='margin:0;'>DEPARTAMENTO DE PSICOLOGÍA</p>
            <hr>
            <h3 style='color: #1f4e79;'>ENTREVISTA PSICOLÓGICA PARA ADULTOS</h3>
        </div>
    """, unsafe_allow_html=True)

    # I. DATOS GENERALES [cite: 7, 8, 14, 16]
    st.markdown('<div class="seccion-titulo">I. DATOS GENERALES</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        nombre = st.text_input("Nombre Completo [cite: 8]")
        edad = st.number_input("Edad [cite: 14]", min_value=0)
        sexo = st.selectbox("Sexo [cite: 12]", ["M", "F"])
    with c2:
        ocupacion = st.text_input("Ocupación actual [cite: 16]")
        militar = st.radio("¿Presto servicio militar? [cite: 18, 19]", ["Sí", "No"], horizontal=True)
        fecha = st.date_input("Fecha de Aplicación [cite: 202]", date.today())

    # II. MOTIVO DE CONSULTA [cite: 25]
    st.markdown('<div class="seccion-titulo">II. MOTIVO DE CONSULTA</div>', unsafe_allow_html=True)
    motivo = st.text_area("Describa el motivo reportado")
    prof_motivo = st.text_area("Observaciones y profundización clínica")

    # V. SALUD FÍSICA (Cribado de síntomas) [cite: 57, 70]
    st.markdown('<div class="seccion-titulo">V. SALUD FÍSICA Y RIESGOS</div>', unsafe_allow_html=True)
    st.write("Seleccione los hallazgos identificados en la tabla de síntomas[cite: 70]:")
    
    col_v1, col_v2, col_v3 = st.columns(3)
    with col_v1:
        s_insomnio = st.checkbox("Insomnio")
        s_suicida = st.checkbox("Intentos suicidas")
        s_voces = st.checkbox("Escucha voces")
    with col_v2:
        s_drogas = st.checkbox("Consumo de drogas")
        s_morir = st.checkbox("Ganas de morir")
        s_maltrato = st.checkbox("Maltrato Físico")
    with col_v3:
        s_aprendizaje = st.checkbox("Problemas de aprendizaje")
        s_fobia = st.checkbox("Miedos o fobias")
        s_panico = st.checkbox("Crisis de pánico")

    prof_salud = st.text_area("Profundización sobre salud física y síntomas neurológicos")

    # XI. PERSONALIDAD PREVIA [cite: 191, 192, 193]
    st.markdown('<div class="seccion-titulo">XI. PERSONALIDAD PREVIA</div>', unsafe_allow_html=True)
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        seguridad = st.text_area("Seguridad en sí mismo [cite: 192]")
        decisiones = st.text_area("Toma de decisiones [cite: 193]")
    with col_p2:
        impulsividad = st.text_area("Actos impulsivos [cite: 197]")
        rencor = st.text_area("Rencoroso [cite: 196]")

    # --- CIERRE DEL REPORTE ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <table style="width:100%; border:none;">
            <tr>
                <td style="text-align:center; border:none;">__________________________<br>Firma del Paciente [cite: 203]</td>
                <td style="text-align:center; border:none;">__________________________<br>Psicólogo Evaluador [cite: 201]</td>
            </tr>
        </table>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- BOTÓN DE IMPRESIÓN ---
st.sidebar.title("Opciones")
if st.sidebar.button("🖨️ Preparar para Imprimir"):
    st.sidebar.success("¡Listo! Ahora presiona 'Ctrl + P' en tu teclado.")
    st.balloons()

# --- INTERPRETACIÓN CLÍNICA (Solo visible en pantalla) ---
with st.sidebar.expander("Sugerencias Automáticas"):
    if s_suicida or s_morir:
        st.error("Riesgo detectado. Sugerencia: Aplicar Escala de Beck e intervención inmediata.")
    elif s_voces:
        st.warning("Indicadores perceptivos. Sugerencia: Aplicar MMPI-2.")
    else:
        st.info("Paciente estable. Sugerencia: TCC o 16PF-5.")
