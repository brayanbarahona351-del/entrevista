import streamlit as st
from fpdf import FPDF

# Configuración de página
st.set_page_config(page_title="Sistema D.S.P. - Formulario Completo", layout="wide")

class DSP_PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 5, 'REPUBLICA DE HONDURAS | SECRETARIA DE SEGURIDAD', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCION DE SANIDAD POLICIAL (D.S.P.)', 0, 1, 'C')
        self.ln(5)

def generar_documento(entrevista_data, informe_data):
    pdf = DSP_PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # --- PARTE 1: ENTREVISTA ---
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "ENTREVISTA PSICOLOGICA PARA ADULTOS", 0, 1, 'C')
    
    for seccion, campos in entrevista_data.items():
        pdf.set_font("helvetica", 'B', 10)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 8, seccion, 1, 1, 'L', True)
        pdf.set_font("helvetica", '', 9)
        pdf.ln(1)
        for k, v in campos.items():
            # Usamos un ancho fijo (180) en lugar de 0 para evitar el error de espacio
            pdf.multi_cell(180, 5, f"{k}: {v}")
        pdf.ln(2)

    # --- PARTE 2: INFORME Y SUGERENCIAS ---
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "INFORME DE RESULTADOS Y RECOMENDACIONES", 0, 1, 'C')
    pdf.ln(5)
    for k, v in informe_data.items():
        pdf.set_font("helvetica", 'B', 11)
        pdf.cell(0, 8, k, 0, 1, 'L')
        pdf.set_font("helvetica", '', 10)
        pdf.multi_cell(180, 5, v)
        pdf.ln(3)

    return pdf.output()

st.title("📋 Expediente Estandarizado D.S.P.")

# I. DATOS GENERALES [cite: 7-24]
with st.expander("I. DATOS GENERALES", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        nombre = st.text_input("Nombre Completo")
        lugar_nac = st.text_input("Lugar y Fecha de Nacimiento")
        nacionalidad = st.text_input("Nacionalidad")
        religion = st.text_input("Religión")
    with col2:
        sexo = st.selectbox("Sexo", ["M", "F"])
        est_civil = st.text_input("Estado Civil")
        edad = st.text_input("Edad")
        celular = st.text_input("Celular")
    with col3:
        ocupacion = st.text_input("Ocupación actual / Asignación")
        militar = st.radio("¿Prestó servicio militar?", ["Sí", "No"])
        direccion = st.text_input("Dirección Actual")
        educacion = st.text_input("Nivel educativo")
    pasatiempos = st.text_input("Pasatiempos y Deportes ")

# II-V. MOTIVO, ANTECEDENTES Y SÍNTOMAS [cite: 25-70]
with st.expander("II-V. MOTIVO, ANTECEDENTES Y SALUD"):
    motivo = st.text_area("II. Motivo de consulta")
    antecedentes_sit = st.text_area("III. Antecedentes de la situación y familiares")
    funciones = st.text_input("Funciones orgánicas (sueño, apetito, sed, defecación)")
    alergias_med = st.text_input("Alergias y Medicamentos regulares [cite: 32-37]")
    cirugias = st.text_area("Enfermedades infancia, cirugías y hospitalizaciones [cite: 42-46]")
    
    st.write("V. Marque hallazgos (Tabla de Síntomas [cite: 70]):")
    sintomas_pdf = ["Insomnio", "Pesadillas", "Maltrato Físico", "Escucha voces", "Miedos o fobias", "Ver cosas extrañas", "Intentos suicidas", "Ganas de morir", "Consumo de drogas", "Tartamudez", "Tics nerviosos"]
    seleccion = st.multiselect("Síntomas identificados:", sintomas_pdf)

# VI. INFORMACIÓN FAMILIAR [cite: 71-124]
with st.expander("VI. INFORMACIÓN FAMILIAR"):
    conyugue = st.text_input("Cónyuge: Nombre, edad, salud y relación")
    padre = st.text_area("Padre: Nombre, relación e imposición de castigos")
    madre = st.text_area("Madre: Nombre, relación e imposición de castigos")
    hermanos = st.text_input("Hermanos: Cantidad, posición y con quién se lleva mejor")
    encargado = st.text_input("¿Quién fue encargado de su crianza? [cite: 106]")
    historia_fam = st.text_area("Antecedentes: Alcoholismo, maltrato o enfermedades mentales en familia")

# VII-X. SOCIAL, DESARROLLO Y SEXUALIDAD [cite: 130-188]
with st.expander("VII-X. SOCIAL, DESARROLLO Y SEXUALIDAD"):
    st.subheader("Social y Hábitos")
    social = st.text_area("Relación laboral, situación económica y problemas legales [cite: 131-135]")
    habitos = st.text_input("Hábitos: Fuma, alcohol, drogas [cite: 141-147]")
    st.subheader("Desarrollo y Escuela")
    desarrollo = st.text_area("Embarazo, parto, lactancia y desarrollo motor [cite: 149-165]")
    escolar = st.text_area("Historia escolar: Edad de inicio, problemas y materias [cite: 174-182]")
    st.subheader("Historia Sexual")
    sexual = st.text_area("Noviazgo, primera relación y opiniones sexuales [cite: 183-188]")

# XI. PERSONALIDAD PREVIA [cite: 191-204]
with st.expander("XI. PERSONALIDAD PREVIA"):
    personalidad = st.text_area("Seguridad, decisiones, miedo abandono, rencor, impulsividad, celos, timidez")

# --- LÓGICA DE SALIDA ---
if st.button("GENERAR EXPEDIENTE COMPLETO E INFORME"):
    datos_e = {
        "I. DATOS GENERALES": {"Nombre": nombre, "Edad": edad, "Educación": educacion, "Militar": militar},
        "II-III. MOTIVO Y ANTECEDENTES": {"Motivo": motivo, "Historia": antecedentes_sit, "Funciones": funciones},
        "V. SALUD FISICA": {"Síntomas": ", ".join(seleccion), "Cirugías": cirugias},
        "VI. FAMILIA": {"Padres": padre + " / " + madre, "Hermanos": hermanos, "Antecedentes": historia_fam},
        "VII-X. DESARROLLO Y SOCIAL": {"Social": social, "Desarrollo": desarrollo, "Escolar": escolar, "Sexual": sexual},
        "XI. PERSONALIDAD": {"Rasgos": personalidad}
    }

    # Informe dinámico según síntomas
    diag = "Paciente evaluado."
    tests = "• Test de Personalidad 16PF-5"
    terapia = "Terapia Cognitivo-Conductual"

    if "Intentos suicidas" in seleccion or "Ganas de morir" in seleccion:
        diag = "RIESGO AUTOLÍTICO DETECTADO."
        tests = "• Escala de Desesperanza de Beck\n• Inventario de Depresión de Beck"
        terapia = "Terapia Dialéctico-Conductual (DBT)."
    elif "Escucha voces" in seleccion:
        diag = "INDICADORES PSICÓTICOS."
        tests = "• MMPI-2\n• Millon (MCMI-IV)"
        terapia = "Evaluación Psiquiátrica."

    datos_i = {"DIAGNÓSTICO": diag, "PRUEBAS SUGERIDAS": tests, "TRATAMIENTO": terapia}

    pdf_bytes = generar_documento(datos_e, datos_i)
    st.success("✅ Archivo listo.")
    st.download_button("⬇️ Descargar PDF Completo", data=pdf_bytes, file_name=f"DSP_{nombre}.pdf", mime="application/pdf")
