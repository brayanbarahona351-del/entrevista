import streamlit as st
from fpdf import FPDF

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema D.S.P. - Formulario Completo", layout="wide")

class DSP_PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 5, 'REPUBLICA DE HONDURAS | SECRETARIA DE SEGURIDAD', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCION DE SANIDAD POLICIAL (D.S.P.)', 0, 1, 'C')
        self.ln(5)

def generar_pdf(datos, informe_ia):
    pdf = DSP_PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    def c(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, c("ENTREVISTA PSICOLÓGICA PARA ADULTOS"), 0, 1, 'C')

    for seccion, campos in datos.items():
        pdf.set_font("helvetica", 'B', 10)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 7, c(seccion), 1, 1, 'L', True)
        pdf.set_font("helvetica", '', 9)
        for k, v in campos.items():
            pdf.multi_cell(185, 5, c(f"{k}: {v}"))
        pdf.ln(2)
    
    # Página de Informe IA
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, c("INFORME DE RESULTADOS E IA"), 0, 1, 'C')
    for k, v in informe_ia.items():
        pdf.set_font("helvetica", 'B', 10)
        pdf.cell(0, 7, c(k), 0, 1, 'L')
        pdf.set_font("helvetica", '', 9)
        pdf.multi_cell(185, 5, c(v))
        pdf.ln(2)
        
    return pdf.output()

# --- MOTOR DE IA ---
def analizar_ia(motivo, personalidad, sintomas):
    corpus = (motivo + " " + personalidad).lower()
    folder_psicometria = "https://drive.google.com/drive/folders/1lrH7AKPKXOVeFkcc_EdO03E0Ar5k4wbv"
    folder_proyectivos = "https://drive.google.com/drive/folders/1yji6O5YIcYOjW1IG0fIhp4MJZgrcToys"
    
    recom = []
    if any(x in corpus for x in ["morir", "suicid", "triste", "lloro"]):
        recom.append(f"MMPI-2 / SCL-90-R: {folder_psicometria}")
    if any(x in corpus for x in ["voces", "veo", "sombras"]):
        recom.append(f"Batería Proyectiva (HTP/Machover): {folder_proyectivos}")
    
    return {
        "DIAGNÓSTICO SUGERIDO": "Análisis basado en narrativa clínica.",
        "TESTS RECOMENDADOS": "\n".join(recom) if recom else f"Evaluación Estándar (16PF): {folder_psicometria}"
    }

# --- INTERFAZ STREAMLIT (TODAS LAS PREGUNTAS) ---
st.title("📋 Expediente Clínico D.S.P. (Versión Completa)")

tabs = st.tabs(["I. Datos Generales", "II-V. Motivo y Salud", "VI. Familia", "VII-IX. Social y Desarrollo", "X-XI. Sexualidad y Personalidad"])

with tabs[0]:
    st.subheader("I. DATOS GENERALES")
    nombre = st.text_input("Nombre Completo")
    c1, c2, c3 = st.columns(3)
    lugar_nac = c1.text_input("Lugar y Fecha de Nacimiento")
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

with tabs[1]:
    st.subheader("II-V. MOTIVO Y SALUD")
    motivo = st.text_area("II. Motivo de Consulta")
    antecedentes_sit = st.text_area("III. Antecedentes de la situación (Desarrollo de síntomas)")
    funciones = st.text_input("Funciones Orgánicas (Sueño, Apetito, Sed, Defecación)")
    alergias = st.text_input("¿Padece Alergias?")
    medicamentos = st.text_input("¿Toma Medicamentos?")
    infancia = st.text_area("IV. Enfermedades infancia, cirugías u hospitalizaciones")
    st.write("V. SÍNTOMAS (Marque todos los presentes en su vida):")
    s_lista = ["Insomnio", "Pesadillas", "Sonambulismo", "Comerse las uñas", "Maltrato Físico", "Escucha voces", "Miedos o fobias", "Golpes en la cabeza", "Ver cosas extrañas", "Orinarse en la cama", "Consumo de drogas", "Mareos o desmayos", "Accidentes", "Intentos suicidas", "Tartamudez", "Ganas de morir", "Tics nerviosos"]
    seleccionados = st.multiselect("Hallazgos:", s_lista)

with tabs[2]:
    st.subheader("VI. INFORMACIÓN FAMILIAR")
    conyugue = st.text_input("Nombre, edad, ocupación y salud del Cónyuge")
    pareja_rel = st.text_area("Relación de pareja")
    padre = st.text_area("Nombre del Padre, relación y castigos")
    madre = st.text_area("Nombre de la Madre, relación y castigos")
    hermanos = st.text_input("Número de hermanos y
