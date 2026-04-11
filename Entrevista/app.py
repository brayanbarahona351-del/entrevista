import streamlit as st
from fpdf import FPDF

# --- CONFIGURACIÓN DE PESTAÑA ---
st.set_page_config(page_title="Sistema D.S.P. IA - Completo", layout="wide")

class DSP_PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 5, 'REPUBLICA DE HONDURAS | SECRETARIA DE SEGURIDAD', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCION DE SANIDAD POLICIAL (D.S.P.)', 0, 1, 'C')
        self.ln(5)

def generar_pdf(entrevista, informe_ia):
    pdf = DSP_PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    def c(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    # Pág 1: Datos de Entrevista
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, c("ENTREVISTA PSICOLÓGICA PARA ADULTOS"), 0, 1, 'C')
    
    for sec, campos in entrevista.items():
        pdf.set_font("helvetica", 'B', 10)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 7, c(sec), 1, 1, 'L', True)
        pdf.set_font("helvetica", '', 9)
        for k, v in campos.items():
            pdf.multi_cell(185, 5, c(f"{k}: {v}"))
        pdf.ln(2)

    # Pág 2: Análisis de IA
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, c("INFORME DE ANÁLISIS CLÍNICO (IA)"), 0, 1, 'C')
    for k, v in informe_ia.items():
        pdf.set_font("helvetica", 'B', 11)
        pdf.cell(0, 8, c(k), 0, 1, 'L')
        pdf.set_font("helvetica", '', 10)
        pdf.multi_cell(185, 5, c(v))
        pdf.ln(3)

    return pdf.output()

# --- MOTOR DE IA CLINICA ---
def analizar_ia(motivo, personalidad, sintomas):
    texto = (motivo + " " + personalidad).lower()
    folder_psicometria = "https://drive.google.com/drive/folders/1lrH7AKPKXOVeFkcc_EdO03E0Ar5k4wbv"
    folder_proyectivos = "https://drive.google.com/drive/folders/1yji6O5YIcYOjW1IG0fIhp4MJZgrcToys"
    
    recom = []
    diag = "Paciente orientado. Discurso coherente."
    
    if any(x in texto for x in ["morir", "suicid", "triste", "solo"]):
        diag = "INDICADORES DEPRESIVOS / RIESGO AUTOLÍTICO DETECTADO."
        recom.append(f"MMPI-2 / SCL-90-R: {folder_psicometria}")
    if any(x in texto for x in ["voces", "veo", "sombras", "paranoid"]):
        diag = "INDICADORES PSICÓTICOS / ALTERACIÓN PERCEPTIVA."
        recom.append(f"Batería Proyectiva (HTP, Machover): {folder_proyectivos}")
    if any(x in texto for x in ["ira", "golpe", "impulso", "enojo"]):
        diag = "RASGOS DE IMPULSIVIDAD Y CONTROL DE IRA."
        recom.append(f"16PF-5 (Factor O, Q4) e IPV: {folder_psicometria}")

    return {
        "IMPRESIÓN DIAGNÓSTICA": diag,
        "TESTS RECOMENDADOS (TUS CARPETAS)": "\n".join(recom) if recom else f"Evaluación de Rutina (16PF): {folder_psicometria}",
        "PLAN SUGERIDO": "Seguimiento clínico y aplicación de batería según manuales."
    }

# --- INTERFAZ COMPLETA ---
st.title("🛡️ Sistema Inteligente D.S.P. - Expediente Completo")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["I. Generales", "II-V. Salud", "VI. Familia", "VII-IX. Desarrollo", "X-XI. Personalidad"])

with tab1:
    nombre = st.text_input("Nombre Completo")
    c1, c2, c3 = st.columns(3)
    nacimiento = c1.text_input("Lugar y Fecha de Nacimiento")
    nacionalidad = c2.text_input("Nacionalidad")
    religion = c3.text_input("Religión")
    sexo = c1.selectbox("Sexo", ["M", "F"])
    est_civil = c2.text_input("Estado Civil")
    edad = c3.text_input("Edad")
    ocupacion = c1.text_input("Ocupación / Asignación")
    militar = c2.radio("¿Servicio Militar?", ["Sí", "No"], horizontal=True)
    educacion = c3.text_input("Nivel Educativo")
    direccion = st.text_input("Dirección Actual")
    celular = st.text_input("Celular")
    remitido = st.text_input("Remitido por")
    pasatiempos = st.text_input("Pasatiempos y Deportes")

with tab2:
    motivo = st.text_area("II. Motivo de Consulta")
    antecedentes = st.text_area("III. Antecedentes de la situación (Síntomas)")
    funciones = st.text_input("Funciones Orgánicas (Sueño, Apetito, etc.)")
    medicamentos = st.text_input("Medicamentos / Alergias")
    infancia = st.text_area("IV. Enfermedades infancia, cirugías u hospitalizaciones")
    st.write("V. Hallazgos Síntomáticos:")
    s_lista = ["Ganas de morir", "Escucha voces", "Insomnio", "Pesadillas", "Agresividad", "Consumo drogas", "Accidentes", "Tics"]
    seleccionados = st.multiselect("Marque síntomas:", s_lista)

with tab3:
    conyugue = st.text_input("Cónyuge: Nombre, salud y relación")
    padre = st.text_area("Nombre del Padre, relación y castigos")
    madre = st.text_area("Nombre de la Madre, relación y castigos")
    hermanos = st.text_input("Número de hermanos y posición")
    encargado = st.text_input("¿Quién lo crió?")
    familia_ant = st.text_area("Antecedentes Familiares (Alcohol, enfermedades mentales)")

with tab4:
    social = st.text_area("VII. Situación laboral, económica y legal")
    habitos = st.text_input("VIII. Hábitos (Fuma, alcohol)")
    st.write("IX. Desarrollo:")
    embarazo = st.text_input("Embarazo y Parto")
    lactancia = st.text_input("Lactancia y Alimentación")
    motor = st.text_input("Desarrollo Motor y Lenguaje")
    esfinteres = st.text_input("Control de Esfínteres")
    escolar = st.text_area("Historia Escolar (Materias, conducta)")

with tab5:
    sexual = st.text_area("X. Historia Sexual (1ra relación, opiniones)")
    personalidad = st.text_area("XI. Personalidad Previa (Seguridad, rencor, celos, impulsividad)")

# --- EJECUCIÓN ---
if st.button("ANALIZAR CASO Y GENERAR EXPEDIENTE"):
    if nombre and motivo:
        res_ia = analizar_ia(motivo, personalidad, seleccionados)
        
        datos_pdf = {
            "I. DATOS GENERALES": {"Nombre": nombre, "Edad": edad, "Militar": militar},
            "II-V. MOTIVO Y SALUD": {"Motivo": motivo, "Sintomas": ", ".join(seleccionados), "Funciones": funciones},
            "VI. FAMILIA": {"Padres": f"{padre} / {madre}", "Hermanos": hermanos, "Crianza": encargado},
            "VII-IX. DESARROLLO": {"Escolar": escolar, "Social": social, "Parto": embarazo},
            "X-XI. PERSONALIDAD": {"Sexual": sexual, "Rasgos": personalidad}
        }
        
        pdf_out = generar_pdf(datos_pdf, res_ia)
        
        st.success("✅ Análisis de IA y PDF generados.")
        st.download_button(
            label="⬇️ Descargar PDF Completo",
            data=bytes(pdf_out),
            file_name=f"DSP_{nombre.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    else:
        st.error("Faltan campos obligatorios (Nombre y Motivo).")
