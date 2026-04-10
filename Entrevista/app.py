import streamlit as st
from fpdf import FPDF
from datetime import date

# Configuración de la interfaz
st.set_page_config(page_title="Sistema Clínico D.S.P.", layout="wide")

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 5, 'REPUBLICA DE HONDURAS | SECRETARIA DE SEGURIDAD', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCION GENERAL POLICIA NACIONAL', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCION DE SANIDAD POLICIAL (D.S.P.)', 0, 1, 'C')
        self.ln(10)

def crear_pdf(datos_entrevista, datos_informe):
    pdf = PDF()
    pdf.add_page()
    
    # --- PARTE 1: ENTREVISTA COMPLETA ---
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(0, 10, "ENTREVISTA PSICOLOGICA PARA ADULTOS", 0, 1, 'C')
    pdf.ln(5)
    
    for seccion, contenido in datos_entrevista.items():
        pdf.set_font("helvetica", 'B', 11)
        pdf.set_fill_color(220, 230, 240)
        pdf.cell(0, 8, seccion.upper(), 1, 1, 'L', True)
        pdf.set_font("helvetica", '', 10)
        pdf.ln(2)
        for clave, valor in contenido.items():
            pdf.multi_cell(0, 6, f"{clave}: {valor}")
        pdf.ln(4)

    # --- PARTE 2: INFORME DE RESULTADOS (PÁGINA NUEVA) ---
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(0, 10, "INFORME DE RESULTADOS Y SUGERENCIAS", 0, 1, 'C')
    pdf.ln(10)
    
    for titulo, texto in datos_informe.items():
        pdf.set_font("helvetica", 'B', 12)
        pdf.cell(0, 8, titulo, 0, 1, 'L')
        pdf.set_font("helvetica", '', 11)
        pdf.multi_cell(0, 7, texto)
        pdf.ln(5)

    # Espacio para firmas 
    pdf.ln(20)
    pdf.cell(90, 10, "__________________________", 0, 0, 'C')
    pdf.cell(90, 10, "__________________________", 0, 1, 'C')
    pdf.cell(90, 5, "Firma del Paciente", 0, 0, 'C')
    pdf.cell(90, 5, "Psicologo Evaluador", 0, 1, 'C')
    
    return pdf.output()

st.title("📋 Registro de Entrevista Estandarizada D.S.P.")

# --- FORMULARIO IGUAL AL PDF ---
with st.expander("I. DATOS GENERALES", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre Completo [cite: 8]")
        nacimiento = st.text_input("Lugar y Fecha de Nacimiento [cite: 9]")
        nacionalidad = st.text_input("Nacionalidad [cite: 10]")
        religion = st.text_input("Religión [cite: 11]")
    with col2:
        edad = st.text_input("Edad [cite: 14]")
        civil = st.text_input("Estado Civil [cite: 12]")
        ocupacion = st.text_input("Ocupación actual y Asignación [cite: 16, 17]")
        militar = st.radio("¿Prestó servicio militar? [cite: 18]", ["Sí", "No"])

with st.expander("III, IV y V. ANTECEDENTES Y SÍNTOMAS"):
    motivo = st.text_area("II. MOTIVO DE CONSULTA [cite: 25]")
    antecedentes = st.text_area("III. ANTECEDENTES CLINICOS Y PSICOLOGICOS [cite: 28]")
    funciones = st.text_input("Funciones orgánicas (sueño, apetito, sed, defecación) [cite: 31]")
    
    st.write("V. Marque hallazgos presentados[cite: 70]:")
    sintomas = st.multiselect("Síntomas:", ["Insomnio", "Pesadillas", "Intentos suicidas", "Escucha voces", "Ganas de morir", "Consumo de drogas", "Maltrato Físico", "Crisis de pánico", "Ver cosas extrañas"])

with st.expander("VI. INFORMACIÓN FAMILIAR Y SOCIAL"):
    padres = st.text_area("Relación con los padres e Imposición de castigos [cite: 88, 91, 96, 97]")
    social = st.text_area("VII. Conducta y relaciones en escuela/trabajo [cite: 131]")

with st.expander("X y XI. HISTORIA SEXUAL Y PERSONALIDAD"):
    sexual = st.text_area("X. Historia Sexual (Opiniones y experiencias) [cite: 183, 187, 188]")
    personalidad = st.text_area("XI. Personalidad Previa (Seguridad, decisiones, impulsividad) [cite: 191, 192, 193, 197]")

# --- BOTÓN DE PROCESAMIENTO ---
if st.button("GENERAR EXPEDIENTE E INFORME"):
    # Organizar Entrevista
    datos_e = {
        "I. Datos Generales": {"Nombre": nombre, "Edad": edad, "Nacionalidad": nacionalidad, "Militar": militar},
        "II. Motivo": {"Descripción": motivo},
        "III. Antecedentes": {"Historia": antecedentes, "Funciones": funciones},
        "V. Síntomas": {"Hallazgos": ", ".join(sintomas)},
        "X. Historia Sexual": {"Detalles": sexual},
        "XI. Personalidad": {"Rasgos": personalidad}
    }

    # Lógica de Informe Automático
    diagnostico = "Paciente estable."
    tests = "• Inventario de Personalidad 16PF-5\n"
    terapia = "• Terapia Cognitivo-Conductual"

    if "Intentos suicidas" in sintomas or "Ganas de morir" in sintomas:
        diagnostico = "ALERTA: Riesgo Autolítico detectado."
        tests += "• Escala de Desesperanza de Beck (BHS)\n• Inventario de Depresión de Beck (BDI-II)"
        terapia = "• Terapia Dialéctico-Conductual (DBT)\n• Intervención en Crisis"
    elif "Escucha voces" in sintomas:
        diagnostico = "ALERTA: Posibles indicadores psicóticos."
        tests += "• MMPI-2\n• Examen Multiaxial de Millon (MCMI-IV)"
        terapia = "• Evaluación Psiquiátrica\n• Terapia de Aceptación y Compromiso"

    datos_i = {
        "IMPRESIÓN DIAGNÓSTICA PRELIMINAR": diagnostico,
        "PRUEBAS PSICOMÉTRICAS RECOMENDADAS": tests,
        "PLAN TERAPÉUTICO SUGERIDO": terapia
    }

    # Generar y mostrar botón de descarga
    pdf_bytes = crear_pdf(datos_e, datos_i)
    st.success("✅ Documento generado. Haz clic abajo para descargar.")
    st.download_button(
        label="⬇️ Descargar Expediente e Informe (PDF)",
        data=pdf_bytes,
        file_name=f"Expediente_DSP_{nombre.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
