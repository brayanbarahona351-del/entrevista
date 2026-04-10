import streamlit as st
from fpdf import FPDF
from datetime import date

# Configuración de página
st.set_page_config(page_title="Sistema D.S.P. Honduras", layout="wide")

class DSP_PDF(FPDF):
    def header(self):
        # Usamos fuentes estándar que soportan latin-1 o configuramos para UTF-8
        self.set_font('Arial', 'B', 10)
        self.cell(0, 5, 'REPUBLICA DE HONDURAS | SECRETARIA DE SEGURIDAD', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCION GENERAL POLICIA NACIONAL', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCION DE SANIDAD POLICIAL (D.S.P.) | DEPTO. PSICOLOGIA', 0, 1, 'C')
        self.ln(5)

def generar_pdf_completo(entrevista_data, resultados_data):
    pdf = DSP_PDF()
    pdf.add_page()
    
    # Título Principal [cite: 6]
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "ENTREVISTA PSICOLOGICA PARA ADULTOS", 0, 1, 'C')
    
    # Función para limpiar texto y evitar errores de encoding
    def clean(txt):
        return str(txt).encode('latin-1', 'replace').decode('latin-1')

    for seccion, campos in entrevista_data.items():
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 7, clean(seccion), 1, 1, 'L', 1)
        pdf.ln(1)
        for k, v in campos.items():
            pdf.set_font("Arial", 'B', 9)
            pdf.write(5, clean(f"{k}: "))
            pdf.set_font("Arial", '', 9)
            pdf.write(5, clean(f"{v}\n"))
        pdf.ln(3)

    # --- PÁGINA DE INFORME Y SUGERENCIAS ---
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "INFORME DE RESULTADOS Y SUGERENCIAS CLINICAS", 0, 1, 'C')
    pdf.ln(5)

    for seccion, contenido in resultados_data.items():
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 8, clean(seccion), 0, 1, 'L')
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 5, clean(contenido))
        pdf.ln(3)

    # Espacio para firmas [cite: 201, 203]
    pdf.ln(20)
    pdf.cell(90, 10, "__________________________", 0, 0, 'C')
    pdf.cell(90, 10, "__________________________", 0, 1, 'C')
    pdf.cell(90, 5, "Firma del Paciente", 0, 0, 'C')
    pdf.cell(90, 5, "Psicologo Evaluador", 0, 1, 'C')

    return pdf.output()

st.title("Sistema Integral D.S.P. - Entrevista e Informe")

# --- CAPTURA DE TODAS LAS SECCIONES DEL PDF ---
# I. DATOS GENERALES [cite: 7-24]
with st.expander("I. DATOS GENERALES", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        nombre = st.text_input("Nombre Completo [cite: 8]")
        nacimiento = st.text_input("Lugar y Fecha de Nacimiento [cite: 9]")
        nacionalidad = st.text_input("Nacionalidad [cite: 10]")
    with c2:
        edad = st.text_input("Edad [cite: 14]")
        civil = st.text_input("Estado Civil [cite: 12]")
        celular = st.text_input("Celular [cite: 15]")
    with c3:
        ocupacion = st.text_input("Ocupación y Asignación [cite: 16, 17]")
        militar = st.radio("¿Presto servicio militar? [cite: 18]", ["Si", "No"])
        educacion = st.text_input("Nivel educativo [cite: 21]")

# III, IV y V. ANTECEDENTES Y SALUD [cite: 28, 57, 70]
with st.expander("ANTECEDENTES, SINTOMAS Y SALUD FISICA"):
    motivo = st.text_area("II. MOTIVO DE CONSULTA [cite: 25]")
    historia = st.text_area("III. ANTECEDENTES DE LA SITUACION [cite: 29]")
    organicas = st.text_input("Funciones organicas (sueño, apetito, sed, defecacion) [cite: 31]")
    
    st.write("V. TABLA DE SINTOMAS (Marque los hallazgos) [cite: 70]")
    sintomas_pdf = ["Insomnio", "Pesadillas", "Intentos suicidas", "Escucha voces", "Ganas de morir", "Consumo de drogas", "Maltrato Fisico", "Problemas de aprendizaje", "Tics nerviosos"]
    seleccionados = st.multiselect("Sintomas identificados:", sintomas_pdf)
    obs_sintomas = st.text_area("Observaciones de salud fisica [cite: 69]")

# VI. INFORMACIÓN FAMILIAR [cite: 71-124]
with st.expander("VI. INFORMACION FAMILIAR"):
    rel_padres = st.text_area("Relacion con Padres e Imposicion de castigos [cite: 88, 91, 96]")
    antecedentes_f = st.text_area("Antecedentes familiares (Alcoholismo, Depresion, enfermedades mentales) [cite: 119, 124]")

# X. HISTORIA SEXUAL [cite: 183-188]
with st.expander("X. HISTORIA SEXUAL"):
    primera_rel = st.text_input("Edad de primera relacion sexual [cite: 186]")
    opiniones_sex = st.text_area("Opinion sobre masturbacion, relaciones y homosexualidad [cite: 187, 188]")

# XI. PERSONALIDAD PREVIA [cite: 191-199]
with st.expander("XI. PERSONALIDAD PREVIA"):
    per_prev = st.text_area("Seguridad, Toma de decisiones, Impulsividad, Rencor [cite: 192, 193, 196, 197]")

# --- GENERACION DE RESULTADOS ---
if st.button("GENERAR EXPEDIENTE E INFORME"):
    # Estructura de la Entrevista
    entrevista = {
        "I. DATOS GENERALES": {"Nombre": nombre, "Edad": edad, "Ocupacion": ocupacion, "Militar": militar},
        "II. MOTIVO": {"Descripcion": motivo},
        "III. ANTECEDENTES": {"Historia": historia, "Funciones": organicas},
        "V. SALUD FISICA": {"Sintomas": ", ".join(seleccionados), "Observaciones": obs_sintomas},
        "VI. FAMILIA": {"Relacion y Antecedentes": rel_padres + " / " + antecedentes_f},
        "X. HISTORIA SEXUAL": {"Detalles": primera_rel + " - " + opiniones_sex},
        "XI. PERSONALIDAD": {"Rasgos": per_prev}
    }

    # Lógica de Informe Basada en Resultados
    alertas = "No se detectan riesgos agudos."
    tests = "• Test de Personalidad 16PF-5"
    terapia = "Terapia Cognitivo-Conductual"

    if "Intentos suicidas" in seleccionados or "Ganas de morir" in seleccionados:
        alertas = "ALERTA: Riesgo Autolitico detectado[cite: 70]. Requiere intervencion inmediata."
        tests = "• Escala de Desesperanza de Beck\n• Inventario de Depresion de Beck"
        terapia = "Terapia Dialectico-Conductual (DBT) e Intervencion en Crisis."
    elif "Escucha voces" in seleccionados:
        alertas = "ALERTA: Indicadores perceptivos/psicoticos[cite: 70]."
        tests = "• MMPI-2\n• Examen Multiaxial de Millon (MCMI-IV)"
        terapia = "Evaluacion Psiquiatrica y TCC para Psicosis."

    informe = {
        "1. IMPRESION DIAGNOSTICA": alertas,
        "2. BATERIA DE TESTS RECOMENDADA": tests,
        "3. PLAN DE TERAPIA": terapia,
        "4. TIPO DE INTERVENCION": "Clinica Especializada"
    }

    pdf_output = generar_pdf_completo(entrevista, informe)
    
    st.success("✅ Documentos listos para descarga.")
    st.download_button(
        label="⬇️ DESCARGAR EXPEDIENTE COMPLETO (PDF)",
        data=pdf_output,
        file_name=f"DSP_Expediente_{nombre.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
