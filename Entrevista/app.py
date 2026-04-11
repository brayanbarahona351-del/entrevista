import streamlit as st
import pandas as pd
import os, io
from docx import Document
from docx.shared import Pt
from datetime import datetime, date

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema Integral D.S.P.", layout="wide")
DB_FILE = "base_datos_dsp_final.xlsx"

def cargar_db():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    try: return pd.read_excel(DB_FILE).astype(str).replace('nan', '')
    except: return pd.DataFrame()

if 'datos' not in st.session_state:
    st.session_state.datos = {}

# --- 2. MOTOR DE ANÁLISIS IA ---
def analizar_con_ia(d):
    """Genera un análisis clínico basado en los datos ingresados."""
    texto_clínico = f"{d.get('Motivo', '')} {str(d.get('Sintomas_X', ''))} {d.get('Impulsos', '')}".lower()
    analisis = "Paciente orientado en tiempo y espacio. "
    tests = "16PF, BARSIT. "
    terapia = "Apoyo psicológico básico y seguimiento. "
    
    # Lógica de detección de riesgos
    if any(x in texto_clínico for x in ["morir", "suicid", "triste", "solo", "vida"]):
        analisis += "Se detectan indicadores de riesgo depresivo y/o ideación suicida. Requiere vigilancia."
        tests = "MMPI-2, Inventario de Depresión de Beck (BDI-II), SCL-90-R."
        terapia = "Terapia Cognitivo-Conductual enfocada en crisis y posible remisión a psiquiatría."
    elif any(x in texto_clínico for x in ["ira", "golpe", "arma", "pelea", "ley", "drogas"]):
        analisis += "Indicadores de baja tolerancia a la frustración y riesgo de conducta impulsiva/agresiva."
        tests = "Test de Personalidad IPV, HTP (Casa-Árbol-Persona), 16PF."
        terapia = "Entrenamiento en manejo de la ira y control de impulsos."
    else:
        analisis += "No se observan indicadores críticos de riesgo inmediato durante la evaluación."
        
    return analisis, tests, terapia

# --- 3. INTERFAZ ---
st.title("🛡️ Gestión Clínica e Informe Final - D.S.P.")
tabs = st.tabs(["I. Generales", "II-V. Clínica", "VI-IX. Historia/Desarrollo", "X-XI. Personalidad", "XII. INFORME FINAL E IA"])

# --- (Las pestañas I a XI mantienen la estructura anterior para no perder datos) ---
with tabs[0]:
    c1, c2 = st.columns(2)
    st.session_state.datos["Nombre"] = c1.text_input("Nombre Completo")
    st.session_state.datos["Identidad"] = c2.text_input("Identidad")
    st.session_state.datos["Edad"] = st.text_input("Edad")
    st.session_state.datos["Motivo"] = st.text_area("Motivo de Consulta")

with tabs[1]:
    f1, f2 = st.columns(2)
    st.session_state.datos["Sueño"] = f1.text_input("Sueño")
    st.session_state.datos["Apetito"] = f2.text_input("Apetito")
    sints = ["Pesadillas", "Ganas de morir", "Escucha voces", "Drogas", "Alcohol", "Ira", "Fobias"]
    st.session_state.datos["Sintomas_X"] = st.multiselect("Síntomas detectados:", sints)

with tabs[2]:
    st.session_state.datos["Historia_Familiar"] = st.text_area("Resumen Historia Familiar")
    st.session_state.datos["Desarrollo"] = st.text_area("Resumen Desarrollo (Parto, Hitos, Escuela)")

with tabs[3]:
    st.session_state.datos["Impulsos"] = st.text_input("Control de Impulsos")
    st.session_state.datos["Relaciones"] = st.text_input("Relaciones Interpersonales")

# --- 4. NUEVA SECCIÓN: INFORME FINAL ---
with tabs[4]:
    st.subheader("📝 Cierre del Caso y Análisis de IA")
    
    if st.button("🧠 GENERAR PRE-ANÁLISIS DE IA"):
        analisis, tests_sug, plan_sug = analizar_con_ia(st.session_state.datos)
        st.session_state.datos["IA_Analisis"] = analisis
        st.session_state.datos["IA_Tests"] = tests_sug
        st.session_state.datos["IA_Plan"] = plan_sug
        st.info("La IA ha generado una propuesta basada en los datos ingresados. Puede editarla abajo.")

    colA, colB = st.columns(2)
    st.session_state.datos["Analisis_Clinico"] = colA.text_area("Análisis y Hallazgos (IA + Criterio)", value=st.session_state.datos.get("IA_Analisis", ""))
    st.session_state.datos["Tests_Recomendados"] = colB.text_area("Pruebas Psicométricas Sugeridas", value=st.session_state.datos.get("IA_Tests", ""))
    
    st.session_state.datos["Concluciones"] = st.text_area("Conclusiones Clínicas")
    st.session_state.datos["Recomendaciones"] = st.text_area("Recomendaciones Terapéuticas")
    st.session_state.datos["Terapia"] = st.text_area("Tipo de Terapia / Plan de Acción", value=st.session_state.datos.get("IA_Plan", ""))
    
    st.divider()
    c3, c4 = st.columns(2)
    st.session_state.datos["Psicologo"] = c3.text_input("Psicólogo Evaluador")
    st.session_state.datos["Proxima_Cita"] = c4.date_input("Próxima Cita", value=date.today())

# --- 5. GUARDADO E IMPRESIÓN DEL INFORME ---
if st.button("💾 GUARDAR Y GENERAR INFORME FINAL"):
    if st.session_state.datos.get("Nombre") and st.session_state.datos.get("Identidad"):
        # Guardar en Excel
        df_nuevo = pd.DataFrame([st.session_state.datos])
        db = cargar_db()
        pd.concat([db, df_nuevo], ignore_index=True).to_excel(DB_FILE, index=False)
        
        # --- GENERAR WORD PROFESIONAL ---
        doc = Document()
        
        # Encabezado
        header = doc.add_heading('INFORME PSICOLÓGICO CLÍNICO - D.S.P. HONDURAS', 0)
        header.alignment = 1
        
        # Sección Datos Personales
        doc.add_heading('1. DATOS GENERALES', level=1)
        doc.add_paragraph(f"Nombre: {st.session_state.datos['Nombre']}")
        doc.add_paragraph(f"Identidad: {st.session_state.datos['Identidad']}")
        doc.add_paragraph(f"Fecha de Evaluación: {date.today()}")
        
        # Motivo
        doc.add_heading('2. MOTIVO DE CONSULTA', level=1)
        doc.add_paragraph(st.session_state.datos['Motivo'])
        
        # Análisis
        doc.add_heading('3. ANÁLISIS E INTERPRETACIÓN (IA & CLÍNICA)', level=1)
        doc.add_paragraph(st.session_state.datos['Analisis_Clinico'])
        
        # Conclusiones y Recomendaciones
        doc.add_heading('4. CONCLUSIONES', level=1)
        doc.add_paragraph(st.session_state.datos['Concluciones'])
        
        doc.add_heading('5. RECOMENDACIONES Y TEST', level=1)
        doc.add_paragraph(f"Tests sugeridos: {st.session_state.datos['Tests_Recomendados']}")
        doc.add_paragraph(f"Recomendaciones generales: {st.session_state.datos['Recomendaciones']}")
        
        # Plan Terapéutico
        doc.add_heading('6. PLAN TERAPÉUTICO', level=1)
        doc.add_paragraph(st.session_state.datos['Terapia'])
        
        # Firma
        doc.add_paragraph("\n\n\n__________________________")
        doc.add_paragraph(f"Firma y Sello: {st.session_state.datos['Psicologo']}")
        
        # Preparar archivo
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        
        st.success("✅ Expediente e Informe guardados con éxito.")
        st.download_button(
            label="📥 DESCARGAR INFORME FINAL (WORD)",
            data=buf,
            file_name=f"Informe_{st.session_state.datos['Identidad']}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    else:
        st.error("Nombre e Identidad son requeridos.")
