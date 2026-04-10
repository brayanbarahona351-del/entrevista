import streamlit as st
from fpdf import FPDF
from datetime import date

# Configuración de página
st.set_page_config(page_title="Sistema D.S.P. - Entrevista Completa", layout="wide")

class DSP_PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 5, 'REPUBLICA DE HONDURAS | SECRETARIA DE SEGURIDAD', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCION GENERAL POLICIA NACIONAL', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCION DE SANIDAD POLICIAL (D.S.P.)', 0, 1, 'C')
        self.cell(0, 5, 'DEPARTAMENTO DE PSICOLOGIA', 0, 1, 'C')
        self.ln(5)

def generar_documento(datos_entrevista, resultados_clinicos):
    pdf = DSP_PDF()
    pdf.add_page()
    
    # --- PÁGINA 1-5: ENTREVISTA ---
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "ENTREVISTA PSICOLOGICA PARA ADULTOS", 0, 1, 'C')
    
    for seccion, campos in datos_entrevista.items():
        pdf.set_font("helvetica", 'B', 10)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 7, seccion, 1, 1, 'L', True)
        pdf.set_font("helvetica", '', 9)
        pdf.ln(1)
        for k, v in campos.items():
            pdf.multi_cell(0, 5, f"{k}: {v}")
        pdf.ln(2)

    # --- PÁGINA FINAL: INFORME DE RESULTADOS ---
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "INFORME DE RESULTADOS Y RECOMENDACIONES", 0, 1, 'C')
    pdf.ln(5)
    for k, v in resultados_clinicos.items():
        pdf.set_font("helvetica", 'B', 11)
        pdf.cell(0, 8, k, 0, 1, 'L')
        pdf.set_font("helvetica", '', 10)
        pdf.multi_cell(0, 5, v)
        pdf.ln(3)

    # Firmas finales [cite: 201-203]
    pdf.ln(20)
    pdf.cell(90, 10, "__________________________", 0, 0, 'C')
    pdf.cell(90, 10, "__________________________", 0, 1, 'C')
    pdf.cell(90, 5, "Firma del Paciente", 0, 0, 'C')
    pdf.cell(90, 5, "Psicologo Evaluador", 0, 1, 'C')
    
    return pdf.output()

st.title("📋 Formulario Estandarizado D.S.P.")

# --- SECCIÓN I: DATOS GENERALES [cite: 7-24] ---
with st.expander("I. DATOS GENERALES", expanded=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        nombre = st.text_input("Nombre Completo")
        nacimiento = st.text_input("Lugar y Fecha de Nacimiento")
        nacionalidad = st.text_input("Nacionalidad")
        religion = st.text_input("Religión")
        sexo = st.selectbox("Sexo", ["M", "F"])
    with c2:
        edad = st.text_input("Edad")
        estado_civil = st.text_input("Estado Civil")
        celular = st.text_input("Celular")
        ocupacion = st.text_input("Ocupación actual")
        asignacion = st.text_input("Asignación")
    with c3:
        militar = st.radio("¿Presto servicio militar?", ["Sí", "No"], horizontal=True)
        direccion = st.text_input("Dirección Actual")
        nivel_ed = st.text_input("Nivel educativo")
        remitido = st.text_input("Remitido por")
        pasatiempos = st.text_input("Pasatiempo y Deportes")

# --- SECCIÓN II Y III: MOTIVO Y ANTECEDENTES [cite: 25-46] ---
with st.expander("II y III. MOTIVO Y ANTECEDENTES"):
    motivo = st.text_area("II. MOTIVO DE CONSULTA")
    antecedentes_sit = st.text_area("III. ANTECEDENTES DE LA SITUACIÓN (Desarrollo de síntomas, última vez que se sintió bien)")
    organicas = st.text_input("Funciones orgánicas (sueño, apetito, sed, defecación)")
    alergias = st.text_input("¿Padece alergias? (Especifique)")
    medicamentos = st.text_input("¿Toma medicamentos regularmente? (¿Para qué?)")
    infancia = st.text_area("Enfermedades de la infancia, cirugías u hospitalizaciones")

# --- SECCIÓN IV Y V: SÍNTOMAS Y SALUD FÍSICA [cite: 51-70] ---
with st.expander("IV y V. SÍNTOMAS Y SALUD FÍSICA"):
    st.write("Marque los síntomas que ha presentado en su vida:")
    col_s1, col_s2, col_s3 = st.columns(3)
    opciones_v = ["Insomnio", "Pesadillas", "Comerse las uñas", "Maltrato Físico", "Escucha voces", "Miedos o fobias", "Golpes en la cabeza", "Ver cosas extrañas", "Orinarse en la cama", "Consumo de drogas", "Mareos o desmayos", "Accidentes", "Intentos suicidas", "Tartamudez", "Caminar dormido", "Ganas de morir", "Problemas de aprendizaje", "Tics nerviosos"]
    
    seleccion = st.multiselect("Seleccione todos los que apliquen:", opciones_v)
    obs_neuro = st.text_area("Síntomas Neuróticos (Pesadillas, Sonambulismo, Enuresis, Onicofagia, Obsesiones, Fobias)")

# --- SECCIÓN VI: INFORMACIÓN FAMILIAR [cite: 71-124] ---
with st.expander("VI. INFORMACIÓN FAMILIAR"):
    conyugue = st.text_input("Nombre, edad y ocupación del Cónyuge")
    rel_conyugue = st.text_area("Describa su relación de pareja")
    padre = st.text_area("Nombre del Padre, relación e imposición de castigos")
    madre = st.text_area("Nombre de la Madre, relación e imposición de castigos")
    hermanos = st.text_input("Número de hermanos, posición entre ellos y con quién se lleva mejor")
    crianza = st.text_input("¿Quién fue el encargado de su crianza?")
    antecedentes_f = st.text_area("Antecedentes familiares (Alcoholismo, maltrato, depresión, enfermedades mentales)")

# --- SECCIÓN VII A X: SOCIAL, HÁBITOS Y DESARROLLO [cite: 130-188] ---
with st.expander("VII a X. SOCIAL, DESARROLLO Y SEXUALIDAD"):
    st.subheader("VII. Social/Ambiental")
    social = st.text_area("Relaciones laborales, satisfacción, estrés y situación económica")
    legal = st.text_input("¿Ha tenido dificultades con la ley?")
    st.subheader("IX. Antecedentes Personales")
    desarrollo = st.text_area("Embarazo, parto, lactancia, desarrollo motor y control de esfínteres")
    escolar = st.text_area("Historia escolar (Edad de inicio, dificultades, materias preferidas)")
    st.subheader("X. Historia Sexual")
    sexual = st.text_area("Primer noviazgo, primera relación sexual, opinión sobre masturbación y homosexualidad")

# --- SECCIÓN XI: PERSONALIDAD PREVIA [cite: 191-199] ---
with st.expander("XI. PERSONALIDAD PREVIA"):
    personalidad = st.text_area("Seguridad, Toma de decisiones, Miedo al abandono, Confianza, Rencor, Impulsividad, Timidez, Celos")

# --- PROCESO DE GENERACIÓN ---
if st.button("FINALIZAR Y GENERAR EXPEDIENTE COMPLETO"):
    # Diccionario de la Entrevista
    datos_e = {
        "I. Datos Generales": {"Nombre": nombre, "Edad": edad, "Militar": militar, "Celular": celular, "Educación": nivel_ed},
        "II y III. Motivo y Antecedentes": {"Motivo": motivo, "Historia": antecedentes_sit, "Funciones": organicas, "Medicamentos": medicamentos},
        "V. Salud Fisica": {"Hallazgos": ", ".join(seleccion), "Observaciones": obs_neuro},
        "VI. Familia": {"Detalles": conyugue + " / " + padre + " / " + madre, "Antecedentes": antecedentes_f},
        "VII-X. Desarrollo y Social": {"Social": social, "Desarrollo": desarrollo, "Escolar": escolar, "Sexual": sexual},
        "XI. Personalidad": {"Rasgos": personalidad}
    }

    # Lógica de Informe Automático
    diagnostico = "No se detectan riesgos agudos."
    tests = "• Inventario de Personalidad 16PF-5"
    terapia = "Terapia Cognitivo-Conductual"

    if "Intentos suicidas" in seleccion or "Ganas de morir" in seleccion:
        diagnostico = "RIESGO AUTOLÍTICO DETECTADO. Requiere protocolo de vigilancia."
        tests = "• Escala de Desesperanza de Beck (BHS)\n• Inventario de Depresión de Beck (BDI-II)"
        terapia = "Terapia Dialéctico-Conductual (DBT) e Intervención en Crisis."
    elif "Escucha voces" in seleccion or "Ver cosas extrañas" in seleccion:
        diagnostico = "INDICADORES PSICÓTICOS / ALTERACIÓN PERCEPTIVA."
        tests = "• MMPI-2\n• Examen Multiaxial de Millon (MCMI-IV)"
        terapia = "Evaluación Psiquiátrica y Terapia Cognitiva para Psicosis."

    datos_i = {
        "1. IMPRESIÓN DIAGNÓSTICA": diagnostico,
        "2. TESTS RECOMENDADOS": tests,
        "3. PLAN TERAPÉUTICO": terapia,
        "4. TIPO DE TERAPIA": "Intervención Clínica Especializada"
    }

    pdf_bytes = generar_documento(datos_e, datos_i)
    st.success("✅ El expediente y el informe han sido generados exitosamente.")
    st.download_button(
        label="⬇️ DESCARGAR EXPEDIENTE COMPLETO + INFORME",
        data=pdf_bytes,
        file_name=f"DSP_Expediente_{nombre.replace(' ', '_')}.pdf",
        mime="application/pdf"
    )
