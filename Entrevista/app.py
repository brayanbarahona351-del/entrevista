import streamlit as st
from fpdf import FPDF
from datetime import date

# Configuración de página
st.set_page_config(page_title="Sistema D.S.P. - Formulario Completo", layout="wide")

class DSP_PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 5, 'REPUBLICA DE HONDURAS | SECRETARIA DE SEGURIDAD', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCION GENERAL POLICIA NACIONAL', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCION DE SANIDAD POLICIAL (D.S.P.)', 0, 1, 'C')
        self.ln(5)

def generar_documento(entrevista_completa, informe_clinico):
    # Definir márgenes amplios para evitar el error de "Not enough horizontal space"
    pdf = DSP_PDF()
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.add_page()
    
    # --- SECCIONES DE LA ENTREVISTA ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "ENTREVISTA PSICOLOGICA PARA ADULTOS", 0, 1, 'C')
    
    for seccion, contenido in entrevista_completa.items():
        pdf.set_font("Arial", 'B', 10)
        pdf.set_fill_color(230, 230, 230)
        # Usamos ancho de 0 para que use todo el espacio disponible entre márgenes
        pdf.cell(0, 7, seccion.upper(), 1, 1, 'L', True)
        pdf.ln(1)
        pdf.set_font("Arial", '', 9)
        for k, v in contenido.items():
            # multi_cell con ancho 0 para evitar errores de espacio horizontal
            pdf.multi_cell(0, 5, f"{k}: {v}")
        pdf.ln(3)

    # --- PÁGINA DE INFORME ---
    pdf.add_page()
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "INFORME DE RESULTADOS Y RECOMENDACIONES", 0, 1, 'C')
    pdf.ln(5)
    
    for k, v in informe_clinico.items():
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 7, k, 0, 1, 'L')
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 5, v)
        pdf.ln(3)

    # Firmas [cite: 201-203]
    pdf.ln(20)
    pdf.cell(90, 10, "__________________________", 0, 0, 'C')
    pdf.cell(90, 10, "__________________________", 0, 1, 'C')
    pdf.cell(90, 5, "Firma del Paciente", 0, 0, 'C')
    pdf.cell(90, 5, "Psicologo Evaluador", 0, 1, 'C')
    
    return pdf.output()

st.title("📋 Registro Estandarizado D.S.P. Honduras")

# --- TODAS LAS CASILLAS DEL PDF ORIGINAL ---

with st.expander("I. DATOS GENERALES", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        nombre = st.text_input("Nombre Completo [cite: 8]")
        nacimiento = st.text_input("Lugar y Fecha de Nacimiento [cite: 9]")
        nacionalidad = st.text_input("Nacionalidad [cite: 10]")
        religion = st.text_input("Religión [cite: 11]")
    with c2:
        sexo = st.selectbox("Sexo [cite: 12]", ["M", "F"])
        estado_civil = st.text_input("Estado Civil [cite: 12]")
        edad = st.text_input("Edad [cite: 14]")
        celular = st.text_input("Celular [cite: 15]")
    with c3:
        ocupacion = st.text_input("Ocupación actual [cite: 16]")
        asignacion = st.text_input("Asignación [cite: 17]")
        militar = st.radio("¿Prestó servicio militar? [cite: 18]", ["Sí", "No"])
        educacion = st.text_input("Nivel educativo [cite: 21]")

with st.expander("II, III, IV y V. MOTIVO, ANTECEDENTES Y SALUD"):
    motivo = st.text_area("Motivo de consulta [cite: 25]")
    antecedentes_sit = st.text_area("Antecedentes de la situación y familiares [cite: 29-30]")
    organicas = st.text_input("Funciones orgánicas (sueño, apetito, sed, defecación) [cite: 31]")
    medicamentos = st.text_input("¿Toma medicamentos? (¿Para qué?) [cite: 35-38]")
    infancia = st.text_area("Enfermedades infancia y cirugías [cite: 42-46]")
    
    st.write("V. Marque hallazgos presentados[cite: 70]:")
    sintomas_lista = ["Insomnio", "Pesadillas", "Maltrato Fisico", "Escucha voces", "Miedos o fobias", "Ver cosas extrañas", "Intentos suicidas", "Ganas de morir", "Consumo de drogas", "Tics nerviosos"]
    seleccion = st.multiselect("Síntomas:", sintomas_lista)

with st.expander("VI. INFORMACION FAMILIAR"):
    conyugue = st.text_input("Nombre, edad y relación con Cónyuge [cite: 73-79]")
    padre = st.text_area("Nombre del Padre, relación y castigos [cite: 81-91]")
    madre = st.text_area("Nombre de la Madre, relación y castigos [cite: 95-97]")
    hermanos = st.text_input("Hermanos y posición en la familia [cite: 100-103]")
    antecedentes_f = st.text_area("Antecedentes familiares (Alcoholismo, maltrato, enfermedades mentales) [cite: 119-124]")

with st.expander("VII a X. SOCIAL, DESARROLLO Y SEXUALIDAD"):
    social = st.text_area("Situación económica, laboral y dificultades legales [cite: 131-135]")
    desarrollo = st.text_area("Embarazo, parto, lactancia y desarrollo motor [cite: 149-165]")
    escolar = st.text_area("Historia escolar y materias dificultadas [cite: 174-182]")
    sexual = st.text_area("Noviazgo, primera relación y opiniones sexuales [cite: 183-188]")

with st.expander("XI. PERSONALIDAD PREVIA"):
    personalidad = st.text_area("Seguridad, decisiones, rencor, impulsividad, celos, timidez [cite: 191-204]")

# --- GENERACIÓN DE RESULTADOS ---
if st.button("GENERAR EXPEDIENTE E INFORME COMPLETO"):
    # Estructura Entrevista
    datos_e = {
        "I. DATOS GENERALES": {"Nombre": nombre, "Edad": edad, "Nacionalidad": nacionalidad, "Militar": militar, "Educación": educacion},
        "II-III. MOTIVO Y ANTECEDENTES": {"Motivo": motivo, "Historia": antecedentes_sit, "Funciones": organicas},
        "V. SALUD FISICA": {"Síntomas": ", ".join(seleccion), "Medicamentos": medicamentos, "Infancia": infancia},
        "VI. FAMILIA": {"Pareja": conyugue, "Padre": padre, "Madre": madre, "Antecedentes": antecedentes_f},
        "VII-X. DESARROLLO Y SOCIAL": {"Social": social, "Desarrollo": desarrollo, "Escolar": escolar, "Sexual": sexual},
        "XI. PERSONALIDAD": {"Rasgos": personalidad}
    }

    # Lógica de Informe Automático
    diagnostico = "Sin riesgos agudos detectados."
    tests = "• Test de Personalidad 16PF-5"
    terapia = "Terapia Cognitivo-Conductual"

    if "Intentos suicidas" in seleccion or "Ganas de morir" in seleccion:
        diagnostico = "RIESGO AUTOLÍTICO DETECTADO."
        tests = "• Escala de Desesperanza de Beck\n• Inventario de Depresión de Beck"
        terapia = "Terapia Dialéctico-Conductual (DBT)."
    elif "Escucha voces" in seleccion:
        diagnostico = "INDICADORES PSICÓTICOS."
        tests = "• MMPI-2\n• Millon (MCMI-IV)"
        terapia = "Evaluación Psiquiátrica y Terapia Clínica."

    datos_i = {
        "1. IMPRESIÓN DIAGNÓSTICA": diagnostico,
        "2. TESTS SUGERIDOS": tests,
        "3. PLAN TERAPÉUTICO": terapia,
        "4. TIPO DE TERAPIA": "Intervención Especializada"
    }

    pdf_bytes = generar_documento(datos_e, datos_i)
    st.success("✅ Documento generado correctamente.")
    st.download_button(
        label="⬇️ DESCARGAR EXPEDIENTE E INFORME (PDF)",
        data=pdf_bytes,
        file_name=f"Expediente_DSP_{nombre.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
