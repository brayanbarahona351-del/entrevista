import streamlit as st
from fpdf import FPDF

# Configuración de página
st.set_page_config(page_title="Sistema D.S.P. - Formulario Oficial", layout="wide")

class DSP_PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 5, 'REPUBLICA DE HONDURAS | SECRETARIA DE SEGURIDAD', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCION GENERAL POLICIA NACIONAL | D.S.P.', 0, 1, 'C')
        self.ln(5)

def generar_documento(entrevista_data, informe_data):
    pdf = DSP_PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Función para limpiar caracteres especiales y evitar el error de codificación
    def c(texto):
        return str(texto).encode('latin-1', 'replace').decode('latin-1')

    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, c("ENTREVISTA PSICOLÓGICA PARA ADULTOS"), 0, 1, 'C')

    for seccion, campos in entrevista_data.items():
        pdf.set_font("helvetica", 'B', 10)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 7, c(seccion), 1, 1, 'L', True)
        pdf.set_font("helvetica", '', 9)
        pdf.ln(1)
        for k, v in campos.items():
            pdf.multi_cell(185, 5, c(f"{k}: {v}"))
        pdf.ln(2)

    # SEGUNDA PÁGINA: INFORME DE RESULTADOS
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, c("INFORME DE RESULTADOS Y SUGERENCIAS CLÍNICAS"), 0, 1, 'C')
    pdf.ln(5)
    for k, v in informe_data.items():
        pdf.set_font("helvetica", 'B', 11)
        pdf.cell(0, 8, c(k), 0, 1, 'L')
        pdf.set_font("helvetica", '', 10)
        pdf.multi_cell(185, 5, c(v))
        pdf.ln(3)

    return pdf.output()

st.title("📋 Formulario Estandarizado D.S.P. Completo")

# I. DATOS GENERALES (Pág 1)
with st.expander("I. DATOS GENERALES", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre = st.text_input("Nombre Completo")
        nacimiento = st.text_input("Lugar y Fecha de Nacimiento")
        nacionalidad = st.text_input("Nacionalidad")
        religion = st.text_input("Religión")
    with col2:
        sexo = st.selectbox("Sexo", ["M", "F"])
        estado_civil = st.text_input("Estado Civil")
        edad = st.text_input("Edad")
        celular = st.text_input("Celular")
    with col3:
        ocupacion = st.text_input("Ocupación actual / Asignación")
        militar = st.radio("¿Prestó servicio militar?", ["Sí", "No"], horizontal=True)
        educacion = st.text_input("Nivel educativo")
        remitido = st.text_input("Remitido por")
    pasatiempo = st.text_input("Pasatiempo")
    deportes = st.text_input("Deportes")

# II-V. MOTIVO, ANTECEDENTES Y SÍNTOMAS (Pág 1 y 2)
with st.expander("II-V. MOTIVO, ANTECEDENTES Y SALUD FÍSICA"):
    motivo = st.text_area("II. Motivo de consulta")
    antecedentes_sit = st.text_area("III. Antecedentes de la situación (Desarrollo de síntomas)")
    funciones = st.text_input("Funciones orgánicas (Sueño, apetito, sed, defecación)")
    alergias = st.text_input("¿Padece alergias? ¿Cuáles?")
    medicamentos = st.text_input("¿Toma medicamentos? ¿Para qué?")
    infancia = st.text_area("Enfermedades de la infancia, cirugías y hospitalizaciones")
    
    st.write("V. Marque los hallazgos presentados:")
    s_lista = ["Pesadillas", "Sonambulismo", "Comerse las uñas", "Maltrato Físico", "Escucha voces", "Miedos o fobias", "Golpes en la cabeza", "Ver cosas extrañas", "Orinarse en la cama", "Consumo de drogas", "Mareos o desmayos", "Accidentes", "Intentos suicidas", "Tartamudez", "Caminar dormido", "Ganas de morir", "Problemas de aprendizaje", "Tics nerviosos"]
    seleccion = st.multiselect("Hallazgos:", s_lista)

# VI. INFORMACIÓN FAMILIAR (Pág 3)
with st.expander("VI. INFORMACIÓN FAMILIAR"):
    conyugue = st.text_input("Cónyuge: Nombre, edad, ocupación y salud")
    rel_pareja = st.text_area("Relación de pareja")
    padre = st.text_area("Nombre del Padre, relación e imposición de castigos")
    madre = st.text_area("Nombre de la Madre, relación e imposición de castigos")
    hermanos = st.text_input("Número de hermanos y posición entre ellos")
    crianza = st.text_input("¿Quién fue el encargado de su crianza?")
    antecedentes_f = st.text_area("Antecedentes familiares (Alcoholismo, maltrato, depresión, enfermedad mental)")

# VII-IX. SOCIAL Y DESARROLLO (Pág 4 y 5)
with st.expander("VII-IX. SOCIAL, HÁBITOS Y DESARROLLO"):
    social = st.text_area("VII. Situación laboral, económica y problemas legales")
    habitos = st.text_input("VIII. Hábitos (Fumar, alcohol, drogas)")
    desarrollo = st.text_area("IX. Desarrollo (Embarazo, parto, lactancia, desarrollo motor, esfínteres)")
    escolar = st.text_area("Historia escolar (Dificultades, materias preferidas, repitencia)")

# X-XI. SEXUALIDAD Y PERSONALIDAD (Pág 5 y 6)
with st.expander("X-XI. HISTORIA SEXUAL Y PERSONALIDAD PREVIA"):
    sexual = st.text_area("X. Historia Sexual (Noviazgo, 1ra relación, opiniones masturbación y homosexualidad)")
    personalidad = st.text_area("XI. Personalidad Previa (Seguridad, decisiones, abandono, rencor, impulsividad, celos)")

# --- GENERACIÓN DE SALIDA ---
if st.button("GENERAR EXPEDIENTE COMPLETO E INFORME"):
    entrevista = {
        "I. DATOS GENERALES": {"Nombre": nombre, "Edad": edad, "Celular": celular, "Educacion": educacion},
        "II-III. MOTIVO Y ANTECEDENTES": {"Motivo": motivo, "Situacion": antecedentes_sit, "Funciones": funciones},
        "V. SALUD FISICA": {"Sintomas": ", ".join(seleccion), "Medicamentos": medicamentos, "Infancia": infancia},
        "VI. FAMILIA": {"Pareja": conyugue, "Padre": padre, "Madre": madre, "Antecedentes": antecedentes_f},
        "VII-IX. SOCIAL Y DESARROLLO": {"Social": social, "Escolar": escolar, "Desarrollo": desarrollo},
        "X-XI. SEXUALIDAD Y PERSONALIDAD": {"Sexual": sexual, "Personalidad": personalidad}
    }

    # Informe sugerido
    diagnostico = "Estable."
    tests = "• Test de Personalidad 16PF-5"
    terapia = "• Terapia Cognitivo-Conductual"

    if "Intentos suicidas" in seleccion or "Ganas de morir" in seleccion:
        diagnostico = "RIESGO AUTOLÍTICO DETECTADO."
        tests = "• Escala de Desesperanza de Beck\n• Inventario de Depresión de Beck"
        terapia = "• Terapia Dialéctico-Conductual (DBT)\n• Intervención en Crisis"
    elif "Escucha voces" in seleccion:
        diagnostico = "INDICADORES PSICÓTICOS."
        tests = "• MMPI-2\n• MCMI-IV (Millon)"
        terapia = "• Evaluación Psiquiátrica\n• Terapia Clínica"

    informe = {"IMPRESIÓN DIAGNÓSTICA": diagnostico, "BATERÍA DE TESTS": tests, "PLAN TERAPÉUTICO": terapia}

    pdf_bytes = generar_documento(entrevista, informe)
    st.success("✅ Documento generado sin errores de tildes.")
    st.download_button("⬇️ Descargar PDF Completo", data=pdf_bytes, file_name=f"DSP_{nombre}.pdf", mime="application/pdf")
