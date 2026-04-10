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
    
    # Función para manejar tildes y eñes sin que explote el programa
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

    # SEGUNDA PÁGINA: INFORME Y SUGERENCIAS
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, c("INFORME DE RESULTADOS Y RECOMENDACIONES"), 0, 1, 'C')
    pdf.ln(5)
    for k, v in informe_data.items():
        pdf.set_font("helvetica", 'B', 11)
        pdf.cell(0, 8, c(k), 0, 1, 'L')
        pdf.set_font("helvetica", '', 10)
        pdf.multi_cell(185, 5, c(v))
        pdf.ln(3)

    # RETORNO DE BYTES (Solución al error de Streamlit)
    return pdf.output()

st.title("📋 Registro Estandarizado D.S.P. (Completo)")

# --- SECCIONES EXACTAS DEL PDF ---

with st.expander("I. DATOS GENERALES", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre = st.text_input("Nombre Completo")
        nacimiento = st.text_input("Lugar y Fecha de Nacimiento")
        nacionalidad = st.text_input("Nacionalidad")
    with col2:
        religion = st.text_input("Religión")
        sexo = st.selectbox("Sexo", ["M", "F"])
        estado_civil = st.text_input("Estado Civil")
    with col3:
        edad = st.text_input("Edad")
        celular = st.text_input("Celular")
        ocupacion = st.text_input("Ocupación / Asignación")
    
    militar = st.radio("¿Prestó servicio militar?", ["Sí", "No"], horizontal=True)
    direccion = st.text_input("Dirección Actual")
    nivel_ed = st.text_input("Nivel educativo")
    remitido = st.text_input("Remitido por")
    pasatiempos = st.text_input("Pasatiempos y Deportes")

with st.expander("II-V. MOTIVO Y SALUD FÍSICA"):
    motivo = st.text_area("II. Motivo de consulta")
    antecedentes_sit = st.text_area("III. Antecedentes de la situación (Desarrollo de síntomas)")
    funciones = st.text_input("Funciones orgánicas (Sueño, apetito, sed, defecación)")
    alergias_med = st.text_input("Alergias y Medicamentos (¿Para qué?)")
    cirugias = st.text_area("IV. Cirugías, hospitalizaciones y enfermedades infancia")
    
    st.write("V. Hallazgos presentados:")
    s_lista = ["Pesadillas", "Sonambulismo", "Comerse las uñas", "Maltrato Físico", "Escucha voces", "Miedos o fobias", "Golpes en la cabeza", "Ver cosas extrañas", "Orinarse en la cama", "Consumo de drogas", "Mareos o desmayos", "Accidentes", "Intentos suicidas", "Tartamudez", "Caminar dormido", "Ganas de morir", "Problemas de aprendizaje", "Tics nerviosos"]
    seleccion = st.multiselect("Marque todos los que apliquen:", s_lista)

with st.expander("VI. INFORMACIÓN FAMILIAR"):
    conyugue = st.text_input("Cónyuge: Nombre, edad, ocupación y relación")
    padre = st.text_area("Padre: Nombre, relación y castigos")
    madre = st.text_area("Madre: Nombre, relación y castigos")
    hermanos = st.text_input("Hermanos: Cantidad, posición y relación")
    antecedentes_f = st.text_area("Antecedentes familiares (Alcohol, enfermedad mental, etc.)")

with st.expander("VII-IX. SOCIAL, HÁBITOS Y DESARROLLO"):
    social = st.text_area("Situación laboral, económica y problemas legales")
    habitos = st.text_input("Hábitos (Fumar, alcohol, drogas)")
    desarrollo = st.text_area("Desarrollo: Embarazo, parto, lactancia, motor, esfínteres")
    escolar = st.text_area("Historia escolar: Inicio, problemas, materias preferidas")

with st.expander("X-XI. SEXUALIDAD Y PERSONALIDAD"):
    sexual = st.text_area("Historia Sexual: Noviazgo, 1ra relación, opiniones")
    personalidad = st.text_area("Personalidad: Seguridad, decisiones, rencor, impulsividad, celos")

# --- LÓGICA DE SALIDA ---
if st.button("GENERAR DOCUMENTOS FINALES"):
    datos_e = {
        "I. DATOS GENERALES": {"Nombre": nombre, "Edad": edad, "Educacion": nivel_ed},
        "II-V. SALUD": {"Motivo": motivo, "Sintomas": ", ".join(seleccion), "Funciones": funciones},
        "VI. FAMILIA": {"Padres": padre + " / " + madre, "Antecedentes": antecedentes_f},
        "VII-IX. DESARROLLO": {"Escolar": escolar, "Desarrollo": desarrollo},
        "X-XI. PERSONALIDAD": {"Rasgos": personalidad}
    }

    # Informe Automático
    diag = "Estable."
    tests = "• Test de Personalidad 16PF-5"
    terapia = "• Terapia Cognitivo-Conductual"

    if "Intentos suicidas" in seleccion or "Ganas de morir" in seleccion:
        diag = "RIESGO AUTOLÍTICO."
        tests = "• Escala de Beck (Depresión y Desesperanza)"
        terapia = "• Terapia Dialéctico-Conductual (DBT)"
    elif "Escucha voces" in seleccion:
        diag = "INDICADORES PSICÓTICOS."
        tests = "• MMPI-2 / MCMI-IV"
        terapia = "• Evaluación Psiquiátrica"

    datos_i = {"DIAGNÓSTICO": diag, "TESTS": tests, "TRATAMIENTO": terapia}

    # Generar PDF
    pdf_output = generar_documento(datos_e, datos_i)
    
    # IMPORTANTE: Convertir a bytes para que Streamlit lo acepte
    pdf_bytes = bytes(pdf_output)
    
    st.success("✅ Archivo generado. Presiona el botón de abajo.")
    st.download_button(
        label="⬇️ DESCARGAR PDF COMPLETO",
        data=pdf_bytes,
        file_name=f"DSP_{nombre.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
