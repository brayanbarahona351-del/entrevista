import streamlit as st
import pandas as pd
import os
import io
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="D.S.P. Word System", layout="wide")

# Inicializar variables para evitar NameError
nombre = ""
motivo = ""
identidad = ""
edad = ""
sintomas = []
familia = ""
desarrollo = ""
personalidad = ""

# --- FUNCIONES ---
def generar_word(datos, informe_ia):
    doc = Document()
    doc.add_heading('DIRECCIÓN DE SANIDAD POLICIAL - HONDURAS', 0)
    for sec, campos in datos.items():
        doc.add_heading(sec, level=1)
        for k, v in campos.items():
            doc.add_paragraph(f"{k}: {v}")
    
    doc.add_heading('RECOMENDACIONES IA', level=1)
    for k, v in informe_ia.items():
        doc.add_paragraph(f"{k}: {v}")

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- INTERFAZ ---
st.title("📋 Expediente Clínico D.S.P. en Word")

# Usamos columnas o pestañas, pero definimos las variables claramente
tabs = st.tabs(["I. Generales", "II-V. Salud", "VI-IX. Historia", "X-XI. Personalidad"])

with tabs[0]:
    nombre = st.text_input("Nombre Completo", key="nom")
    identidad = st.text_input("Identidad", key="id")
    edad = st.text_input("Edad", key="ed")

with tabs[1]:
    motivo = st.text_area("Motivo de consulta", key="mot")
    sintomas = st.multiselect("Síntomas:", ["Insomnio", "Ganas de morir", "Agresividad"], key="sin")

with tabs[2]:
    familia = st.text_area("Historia Familiar", key="fam")
    desarrollo = st.text_area("Desarrollo Infantil", key="des")

with tabs[3]:
    personalidad = st.text_area("Rasgos de Personalidad", key="per")

st.divider()

# EL BOTÓN AHORA SÍ RECONOCE LAS VARIABLES
if st.button("📝 GENERAR EXPEDIENTE WORD"):
    if nombre and motivo: # Aquí ya no habrá NameError
        # 1. Datos para el documento
        datos_doc = {
            "I. DATOS GENERALES": {"Nombre": nombre, "ID": identidad, "Edad": edad},
            "II. CLÍNICA": {"Motivo": motivo, "Síntomas": ", ".join(sintomas)},
            "III. HISTORIA": {"Familia": familia, "Desarrollo": desarrollo},
            "IV. PERSONALIDAD": {"Rasgos": personalidad}
        }
        
        # 2. Análisis IA (Simple)
        res_ia = {
            "Diagnóstico": "Análisis preliminar generado.",
            "Acción": "Revisar carpetas de Drive de Psicometría."
        }
        
        # 3. Generar y Descargar
        word_data = generar_word(datos_doc, res_ia)
        
        st.success("✅ Documento Word creado.")
        st.download_button(
            label="⬇️ Descargar Word",
            data=word_data,
            file_name=f"Expediente_{nombre}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        st.warning("El Nombre y el Motivo son obligatorios para generar el documento.")
