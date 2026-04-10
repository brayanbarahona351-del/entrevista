import streamlit as st
from fpdf import FPDF
from datetime import date

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema Clínico D.S.P.", layout="wide")

# --- FUNCIÓN PARA GENERAR PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 5, 'REPÚBLICA DE HONDURAS | SECRETARÍA DE SEGURIDAD', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCIÓN DE SANIDAD POLICIAL (D.S.P.)', 0, 1, 'C')
        self.ln(10)

def generar_pdf(datos):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    
    for seccion, contenido in datos.items():
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(0, 8, f"{seccion}", 0, 1, 'L', 1)
        pdf.ln(2)
        for k, v in contenido.items():
            pdf.multi_cell(0, 5, f"{k}: {v}")
        pdf.ln(5)
    
    return pdf.output(dest='S').encode('latin-1')

# --- FORMULARIO DE ENTRADA ---
st.title("📋 Entrevista Psicológica Estandarizada")

# I. DATOS GENERALES [cite: 7-24]
with st.expander("I. DATOS GENERALES", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre Completo [cite: 8]")
        nacimiento = st.text_input("Lugar y Fecha de Nacimiento [cite: 9]")
        nacionalidad = st.text_input("Nacionalidad [cite: 10]")
        religion = st.text_input("Religión [cite: 11]")
    with col2:
        edad = st.number_input("Edad [cite: 14]", 18, 100)
        estado_civil = st.text_input("Estado Civil [cite: 12]")
        ocupacion = st.text_input("Ocupación actual [cite: 16]")
        militar = st.radio("¿Prestó servicio militar? ", ["Sí", "No"])

# III. ANTECEDENTES Y FUNCIONES ORGÁNICAS [cite: 28-38]
with st.expander("III. ANTECEDENTES CLÍNICOS"):
    antecedentes_sit = st.text_area("Antecedentes de la situación [cite: 29]")
    funciones = st.text_input("Funciones orgánicas (sueño, apetito, sed, defecación) [cite: 31]")
    alergias = st.text_input("¿Padece alergias? [cite: 32]")
    medicamentos = st.text_input("¿Toma medicamentos regularmente? [cite: 35]")

# V. SALUD FÍSICA (TABLA DE SÍNTOMAS) 
with st.expander("V. SALUD FÍSICA"):
    sintomas = st.multiselect("Marque síntomas presentados ", 
        ["Insomnio", "Intentos suicidas", "Escucha voces", "Ganas de morir", "Consumo de drogas", "Maltrato Físico", "Pesadillas", "Crisis de pánico"])

# VI. INFORMACIÓN FAMILIAR 
with st.expander("VI. INFORMACIÓN FAMILIAR"):
    conyugue = st.text_input("Nombre del Cónyuge [cite: 73]")
    relacion_padres = st.text_area("Tipo de relación con los padres [cite: 88, 96]")
    alcoholismo_fam = st.radio("¿Antecedentes de alcoholismo en la familia? [cite: 119]", ["No", "Sí"])

# XI. PERSONALIDAD PREVIA [cite: 191-199]
with st.expander("XI. PERSONALIDAD PREVIA"):
    seguridad = st.text_input("Seguridad en sí mismo [cite: 192]")
    decisiones = st.text_input("Toma de decisiones [cite: 193]")
    impulsividad = st.text_input("Actos impulsivos [cite: 197]")

# --- PROCESAMIENTO Y DESCARGA ---
if st.button("PREPARAR ARCHIVO PARA DESCARGA"):
    dict_datos = {
        "I. DATOS GENERALES": {"Nombre": nombre, "Edad": edad, "Ocupación": ocupacion},
        "II. MOTIVO": {"Descripción": "Completado en entrevista"},
        "III. ANTECEDENTES": {"Funciones": funciones, "Medicamentos": medicamentos},
        "V. SÍNTOMAS": {"Detectados": ", ".join(sintomas)},
        "XI. PERSONALIDAD": {"Seguridad": seguridad, "Decisiones": decisiones}
    }
    
    pdf_bytes = generar_pdf(dict_datos)
    
    st.download_button(
        label="⬇️ Descargar Entrevista en PDF",
        data=pdf_bytes,
        file_name=f"Entrevista_{nombre.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
