import streamlit as st
from fpdf import FPDF

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IA Clínica - D.S.P. Honduras", layout="wide")

class DSP_PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 5, 'REPUBLICA DE HONDURAS | SECRETARIA DE SEGURIDAD', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCION DE SANIDAD POLICIAL (D.S.P.)', 0, 1, 'C')
        self.ln(5)

def generar_pdf(datos_entrevista, informe_ia):
    pdf = DSP_PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Esta función limpia el texto para evitar el error de codificación 'latin-1'
    def c(t):
        return str(t).encode('latin-1', 'replace').decode('latin-1')

    # Página 1: Entrevista
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, c("ENTREVISTA PSICOLÓGICA COMPLETA"), 0, 1, 'C')

    for seccion, campos in datos_entrevista.items():
        pdf.set_font("helvetica", 'B', 10)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 7, c(seccion), 1, 1, 'L', True)
        pdf.set_font("helvetica", '', 9)
        for k, v in campos.items():
            pdf.multi_cell(185, 5, c(f"{k}: {v}"))
        pdf.ln(2)

    # Página 2: Informe IA
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, c("INFORME DE RESULTADOS E IA"), 0, 1, 'C')
    for k, v in informe_ia.items():
        pdf.set_font("helvetica", 'B', 10)
        pdf.cell(0, 7, c(k), 0, 1, 'L')
        pdf.set_font("helvetica", '', 9)
        pdf.multi_cell(185, 5, c(v))
        pdf.ln(3)

    # IMPORTANTE: Usamos output() sin parámetros extras y lo pasamos a bytes después
    return pdf.output()

# --- MOTOR DE IA ---
def analizar_ia(motivo, personalidad):
    link_psicometria = "https://drive.google.com/drive/folders/1lrH7AKPKXOVeFkcc_EdO03E0Ar5k4wbv"
    link_proyectivos = "https://drive.google.com/drive/folders/1yji6O5YIcYOjW1IG0fIhp4MJZgrcToys"
    
    recom = []
    texto = (motivo + " " + personalidad).lower()
    
    if any(x in texto for x in ["morir", "suicid", "triste"]):
        recom.append(f"MMPI-2 y SCL-90-R: {link_psicometria}")
    if any(x in texto for x in ["voces", "veo", "sombra"]):
        recom.append(f"Batería Proyectiva (HTP): {link_proyectivos}")
    
    return {
        "SUGERENCIA CLÍNICA": "Evaluación prioritaria basada en narrativa.",
        "TESTS RECOMENDADOS": "\n".join(recom) if recom else f"Evaluación de rutina (16PF): {link_psicometria}"
    }

# --- INTERFAZ ---
st.title("📋 Expediente Estandarizado D.S.P.")

t1, t2, t3, t4 = st.tabs(["Generales", "Salud", "Familia", "Vida y Personalidad"])

with t1:
    nombre = st.text_input("Nombre Completo")
    edad = st.text_input("Edad")
    militar = st.radio("¿Servicio Militar?", ["No", "Sí"], horizontal=True)
    educacion = st.text_input("Nivel Educativo")

with t2:
    motivo = st.text_area("Motivo de consulta")
    sintomas = st.multiselect("Síntomas:", ["Insomnio", "Ganas de morir", "Escucha voces", "Agresividad"])
    antecedentes = st.text_area("Antecedentes de la situación")

with t3:
    hermanos = st.text_input("Número de hermanos y posición") # CORREGIDO: comilla cerrada
    padres = st.text_area("Relación con padres y castigos")
    familia_ant = st.text_area("Antecedentes familiares (Alcoholismo, etc.)")

with t4:
    desarrollo = st.text_area("Desarrollo (Embarazo, parto, motor, escolaridad)")
    personalidad = st.text_area("Rasgos de Personalidad (Impulsividad, rencor, etc.)")

if st.button("GENERAR INFORME"):
    if not nombre or not motivo:
        st.error("Por favor rellene Nombre y Motivo.")
    else:
        # 1. Analizar
        info_ia = analizar_ia(motivo, personalidad)
        
        # 2. Estructurar
        datos = {
            "I. DATOS": {"Nombre": nombre, "Edad": edad, "Militar": militar},
            "II. MOTIVO": {"Detalle": motivo, "Sintomas": ", ".join(sintomas)},
            "III. FAMILIA": {"Hermanos": hermanos, "Padres": padres},
            "IV. VIDA": {"Desarrollo": desarrollo, "Personalidad": personalidad}
        }
        
        # 3. Generar PDF
        pdf_out = generar_pdf(datos, info_ia)
        
        # 4. Descarga (Convertimos a bytes para evitar el error de Streamlit)
        st.success("✅ Documento listo para descargar.")
        st.download_button(
            label="⬇️ Descargar PDF",
            data=bytes(pdf_out),
            file_name=f"DSP_{nombre.replace(' ', '_')}.pdf",
            mime="application/pdf
