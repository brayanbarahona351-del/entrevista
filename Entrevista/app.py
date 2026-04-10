import streamlit as st
from fpdf import FPDF
from datetime import date

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema D.S.P. Honduras", layout="wide")

class DSP_PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 5, 'REPÚBLICA DE HONDURAS | SECRETARÍA DE SEGURIDAD', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCIÓN GENERAL POLICÍA NACIONAL', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCIÓN DE SANIDAD POLICIAL (D.S.P.) | DEPTO. PSICOLOGÍA', 0, 1, 'C')
        self.ln(5)

def generar_pdf_completo(entrevista_data, resultados_data):
    pdf = DSP_PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Título Entrevista
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "ENTREVISTA PSICOLÓGICA PARA ADULTOS", 0, 1, 'C')
    pdf.set_font("Arial", size=10)

    for seccion, campos in entrevista_data.items():
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 7, seccion, 1, 1, 'L', 1)
        pdf.ln(1)
        for k, v in campos.items():
            pdf.set_font("Arial", 'B', 10)
            pdf.write(5, f"{k}: ")
            pdf.set_font("Arial", '', 10)
            pdf.write(5, f"{v}\n")
        pdf.ln(3)

    # Nueva página para el Informe de Resultados
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "INFORME DE RESULTADOS Y SUGERENCIAS CLÍNICAS", 0, 1, 'C')
    pdf.ln(5)

    for seccion, contenido in resultados_data.items():
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, seccion, 0, 1, 'L')
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 5, contenido)
        pdf.ln(3)

    # Firmas [cite: 201-203]
    pdf.ln(20)
    pdf.cell(90, 10, "__________________________", 0, 0, 'C')
    pdf.cell(90, 10, "__________________________", 0, 1, 'C')
    pdf.cell(90, 5, "Firma del Paciente", 0, 0, 'C')
    pdf.cell(90, 5, "Psicólogo Evaluador", 0, 1, 'C')

    return pdf.output(dest='S').encode('latin-1')

# --- INTERFAZ DE USUARIO ---
st.title("Sistema de Entrevista y Diagnóstico D.S.P.")

# I. DATOS GENERALES [cite: 7-24]
with st.expander("I. DATOS GENERALES", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        nombre = st.text_input("Nombre Completo")
        nacimiento = st.text_input("Lugar y Fecha de Nacimiento")
        nacionalidad = st.text_input("Nacionalidad")
    with c2:
        edad = st.text_input("Edad")
        civil = st.text_input("Estado Civil")
        religion = st.text_input("Religión")
    with c3:
        ocupacion = st.text_input("Ocupación y Asignación")
        militar = st.radio("¿Prestó servicio militar?", ["Sí", "No"])
        celular = st.text_input("Celular")

# III. ANTECEDENTES Y SALUD [cite: 28-38, 70]
with st.expander("III. ANTECEDENTES Y SALUD FÍSICA"):
    motivo = st.text_area("II. MOTIVO DE CONSULTA [cite: 25]")
    historia = st.text_area("Antecedentes de la situación (¿Cuándo se sintió bien por última vez?) [cite: 29]")
    organicas = st.text_input("Funciones orgánicas (sueño, apetito, sed, defecación) [cite: 31]")
    sintomas = st.multiselect("Marque hallazgos (Sección V) [cite: 70]", 
        ["Insomnio", "Pesadillas", "Intentos suicidas", "Escucha voces", "Ganas de morir", "Consumo de drogas", "Maltrato Físico", "Ver cosas extrañas", "Problemas de aprendizaje"])
    obs_sintomas = st.text_area("Espacio para profundizar en síntomas")

# VI. INFORMACIÓN FAMILIAR [cite: 72-124]
with st.expander("VI. INFORMACIÓN FAMILIAR"):
    conyugue = st.text_input("Nombre del Cónyuge")
    rel_padre = st.text_area("Relación con el Padre y Castigos [cite: 88, 91]")
    rel_madre = st.text_area("Relación con la Madre y Castigos [cite: 96, 97]")
    antecedentes_fam = st.text_area("Alcoholismo o enfermedades mentales en la familia [cite: 119, 124]")

# X. HISTORIA SEXUAL [cite: 183-188]
with st.expander("X. HISTORIA SEXUAL"):
    primera_rel = st.text_input("Edad de la primera relación sexual")
    opinion_sex = st.text_area("Opinión sobre masturbación y relaciones sexuales")
    opinion_homo = st.text_area("Opinión sobre homosexualidad")

# XI. PERSONALIDAD PREVIA [cite: 191-199]
with st.expander("XI. PERSONALIDAD PREVIA"):
    seguridad = st.text_area("Seguridad en sí mismo y toma de decisiones")
    impulsividad = st.text_area("Actos impulsivos y Rencor")

# --- LÓGICA DE RESULTADOS ---
if st.button("GENERAR ENTREVISTA E INFORME COMPLETO"):
    # 1. Preparar datos de la entrevista
    entrevista = {
        "I. DATOS GENERALES": {"Nombre": nombre, "Edad": edad, "Ocupación": ocupacion, "Militar": militar, "Religión": religion},
        "II. MOTIVO": {"Descripción": motivo},
        "III. ANTECEDENTES": {"Historia": historia, "Funciones": organicas},
        "V. SALUD FÍSICA": {"Síntomas": ", ".join(sintomas), "Observaciones": obs_sintomas},
        "VI. FAMILIA": {"Cónyuge": conyugue, "Rel. Padre": rel_padre, "Rel. Madre": rel_madre, "Antecedentes Fam": antecedentes_fam},
        "X. HISTORIA SEXUAL": {"1ra Relación": primera_rel, "Opiniones": opinion_sex, "Homosexualidad": opinion_homo},
        "XI. PERSONALIDAD": {"Seguridad": seguridad, "Impulsividad": impulsividad}
    }

    # 2. Generar sugerencias automáticas según resultados
    alertas = ""
    tests = "• Test de Personalidad 16PF-5\n"
    terapia = "• Terapia Cognitivo-Conductual (Enfoque general)"
    tipo_t = "Orientación y Reestructuración Cognitiva"

    if "Intentos suicidas" in sintomas or "Ganas de morir" in sintomas:
        alertas = "ALERTA: Riesgo Autolítico detectado. Requiere vigilancia inmediata."
        tests += "• Escala de Desesperanza de Beck (BHS)\n• Inventario de Depresión de Beck (BDI-II)"
        terapia = "• Terapia Dialéctico-Conductual (DBT)\n• Intervención en Crisis"
        tipo_t = "Terapia de apoyo y manejo de crisis vital"
    elif "Escucha voces" in sintomas or "Ver cosas extrañas" in sintomas:
        alertas = "ALERTA: Posibles indicadores de alteración perceptiva (Psicosis)."
        tests += "• Examen Multiaxial de Millon (MCMI-IV)\n• MMPI-2"
        terapia = "• Evaluación Psiquiátrica Urgente\n• Terapia Cognitiva para Psicosis"
        tipo_t = "Terapia Farmacológica y Clínica"

    resultados = {
        "1. IMPRESIÓN DIAGNÓSTICA PRELIMINAR": alertas if alertas else "No se detectan riesgos agudos inmediatos.",
        "2. TESTS PSICOMÉTRICOS A APLICAR": tests,
        "3. PLAN TERAPÉUTICO SUGERIDO": terapia,
        "4. TIPO DE TERAPIA": tipo_t
    }

    # 3. Generar PDF y botón de descarga
    pdf_final = generar_pdf_completo(entrevista, resultados)
    
    st.success("✅ Documentos generados con éxito.")
    st.download_button(
        label="⬇️ DESCARGAR ENTREVISTA + INFORME (PDF)",
        data=pdf_final,
        file_name=f"Expediente_{nombre.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
