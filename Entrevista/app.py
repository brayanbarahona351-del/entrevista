import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN DE PANTALLA ---
st.set_page_config(page_title="D.S.P. Honduras - Protocolo Oficial", layout="wide")

# --- 2. GESTIÓN DE BASE DE DATOS LOCAL ---
DB_FILE = "DB_DSP_ENTREVISTAS_COMPLETAS.xlsx"

def cargar_db():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    try:
        return pd.read_excel(DB_FILE).astype(str).replace('nan', '')
    except:
        return pd.DataFrame()

def guardar_db(datos_dict):
    df = cargar_db()
    if not df.empty and "Identidad" in df.columns:
        df = df[df["Identidad"] != str(datos_dict["Identidad"])]
    df_final = pd.concat([df, pd.DataFrame([datos_dict])], ignore_index=True)
    df_final.to_excel(DB_FILE, index=False)

# --- 3. MOTOR DE ANÁLISIS CLÍNICO CON JUSTIFICACIÓN ---
def motor_ia_dsp(datos):
    cuerpo = f"{datos.get('motivo', '')} {datos.get('opinion', '')}".lower().strip()
    checks = datos.get('checks', [])
    
    if len(cuerpo) < 10 and not checks:
        return {
            "estado": "PENDIENTE",
            "rec": "Información insuficiente.",
            "just_rec": "No se puede recomendar una intervención sin datos clínicos base.",
            "test": "N/A",
            "just_test": "La aplicación de reactivos debe estar orientada por una hipótesis diagnóstica previa."
        }

    # Lógica de Riesgo Autolítico
    if any(x in cuerpo for x in ["suicid", "muerte", "matar", "ganas de morir"]) or "Intentos suicidas" in checks or "Ganas de morir" in checks:
        return {
            "estado": "ALERTA: Riesgo Autolítico Detectado",
            "rec": "Remisión inmediata a Psiquiatría y activación de protocolo de vigilancia.",
            "just_rec": "Ante la presencia de ideación o intentos previos, la prioridad es la preservación de la vida y el abordaje farmacológico para estabilizar el afecto.",
            "test": "Inventario de Desesperanza de Beck (BHS) y Escala de Ideación Suicida de Beck (ISB).",
            "just_test": "Estos tests permiten cuantificar la severidad del riesgo y el nivel de pesimismo hacia el futuro, predictores clave del acto suicida."
        }
    
    # Lógica de Organicidad / Psicosis
    elif any(x in cuerpo for x in ["voces", "alucinacion", "extrañas", "convulsion"]) or "Escucha voces" in checks:
        return {
            "estado": "INDICADOR: Posible Compromiso Orgánico o Psicótico",
            "rec": "Interconsulta con Neurología y evaluación psiquiátrica profunda.",
            "just_rec": "Es imperativo descartar lesiones cerebrales o desequilibrios neuroquímicos antes de proceder con psicoterapia, ya que el origen podría ser biológico.",
            "test": "Test Gestáltico Visomotor de Bender y SCL-90-R.",
            "just_test": "El Bender detecta signos de maduración o daño orgánico, mientras que el SCL-90-R mapea síntomas psicóticos y paranoides."
        }

    # Lógica General (Estrés Policial / Adaptación)
    else:
        return {
            "estado": "ESTADO: Reacción de Ajuste / Estrés Laboral",
            "rec": "Terapia Breve Centrada en Soluciones y entrenamiento en Higiene Mental.",
            "just_rec": "Para personal policial, el manejo de la carga laboral y el estrés traumático secundario previene el burnout y mejora el rendimiento operativo.",
            "test": "16PF-5 y Test HTP (Casa-Árbol-Persona).",
            "just_test": "El 16PF provee un perfil de personalidad estable para entender sus mecanismos de defensa, y el HTP revela aspectos proyectivos del yo y el entorno familiar."
        }

# --- 4. INTERFAZ ---
st.title("🛡️ Protocolo de Entrevista Psicológica - D.S.P.")

tabs = st.tabs(["I-II. Identificación", "III-V. Clínica", "VI. Familia", "VII-IX. Social", "X. Desarrollo", "XI-XII. Análisis"])

with tabs[0]:
    st.subheader("I. DATOS GENERALES")
    c1, c2 = st.columns(2)
    nombre = c1.text_input("Nombre Completo")
    identidad = c2.text_input("Número de Identidad")
    motivo = st.text_area("II. MOTIVO DE CONSULTA")

with tabs[1]:
    st.subheader("III-V. SÍNTOMAS Y CLÍNICA")
    lista_sintomas = ["Insomnio", "Mareos o desmayos", "Comerse las uñas", "Intentos suicidas", "Escucha voces", "Ganas de morir", "Consumo de drogas"]
    seleccionados = st.multiselect("Marque síntomas presentados:", lista_sintomas)
    ant_clinicos = st.text_area("Antecedentes de la situación:")

with tabs[2]:
    st.subheader("VI. INFORMACIÓN FAMILIAR")
    st.write("**Padre**")
    p_det = st.text_input("Edad, Vivo/Muerto, Ocupación, Salud", key="p_det_fix")
    p_rel = st.text_area("Relación con el padre e imposición de castigos:", key="p_rel_fix")
    
    st.write("**Madre**")
    m_det = st.text_input("Edad, Vivo/Muerto, Ocupación, Salud", key="m_det_fix")
    m_rel = st.text_area("Relación con la madre e imposición de castigos:", key="m_rel_fix")

with tabs[5]:
    st.subheader("XII. OBSERVACIONES Y RECOMENDACIONES")
    opinion_prof = st.text_area("Opinión Profesional:")
    
    if st.button("🧠 GENERAR ANÁLISIS COMPLETO"):
        res = motor_ia_dsp({"motivo": motivo, "opinion": opinion_prof, "checks": seleccionados})
        st.session_state["analisis"] = res

    if "analisis" in st.session_state:
        a = st.session_state["analisis"]
        st.divider()
        st.info(f"**DIAGNÓSTICO PRELIMINAR:** {a['estado']}")
        
        col_rec, col_test = st.columns(2)
        with col_rec:
            st.success(f"**RECOMENDACIÓN:**\n{a['rec']}")
            st.write(f"*¿Por qué?*: {a['just_rec']}")
        with col_test:
            st.warning(f"**TESTS SUGERIDOS:**\n{a['test']}")
            st.write(f"*¿Por qué?*: {a['just_test']}")

    psicologo = st.text_input("Firma del Psicólogo Evaluador")

# --- 5. EXPORTACIÓN ---
if st.button("💾 GUARDAR Y EXPORTAR WORD"):
    if identidad and nombre:
        doc = Document()
        doc.add_heading('INFORME DE EVALUACIÓN PSICOLÓGICA - D.S.P.', 0)
        
        # Agregar Justificaciones al Word
        if "analisis" in st.session_state:
            a = st.session_state["analisis"]
            doc.add_heading('Análisis Clínico', level=1)
            doc.add_paragraph(f"Impresión: {a['estado']}")
            doc.add_heading('Plan de Intervención', level=2)
            doc.add_paragraph(f"Recomendación: {a['rec']}")
            doc.add_paragraph(f"Justificación Técnica: {a['just_rec']}")
            doc.add_heading('Evaluación Psicométrica Sugerida', level=2)
            doc.add_paragraph(f"Batería: {a['test']}")
            doc.add_paragraph(f"Justificación de Tests: {a['just_test']}")
        
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        st.download_button("📥 DESCARGAR INFORME", buf, f"Informe_{identidad}.docx")
