import streamlit as st
import pandas as pd
import os
import io
from docx import Document
from datetime import datetime, date, time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="D.S.P. - IA & Base de Datos", layout="wide")
DB_FILE = "base_datos_pacientes.xlsx"

# Estructura de la Base de Datos
COLS = ["Nombre", "Identidad", "Edad", "Motivo", "Sintomas", "Familia", "Historia", "Personalidad", "Seguimiento", "Proxima_Cita"]

# --- 2. FUNCIONES DE BASE DE DATOS ---
def cargar_db():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame(columns=COLS)
    try:
        # Cargamos y forzamos todo a texto para evitar errores de tipo (Dtype)
        df = pd.read_excel(DB_FILE)
        df = df.astype(str).replace('nan', '')
        return df
    except:
        return pd.DataFrame(columns=COLS)

def guardar_en_db(datos_dict):
    df = cargar_db()
    # Si el paciente ya existe, lo eliminamos de la lista para insertar la versión actualizada
    if not df.empty and str(datos_dict["Nombre"]) in df["Nombre"].values:
        df = df[df["Nombre"] != datos_dict["Nombre"]]
    
    # Insertar el nuevo registro
    df = pd.concat([df, pd.DataFrame([datos_dict])], ignore_index=True)
    df.to_excel(DB_FILE, index=False)

# --- 3. MOTOR DE INTELIGENCIA ARTIFICIAL ---
def motor_ia_clinico(d):
    # La IA analiza la suma de toda la información ingresada
    entrevista_total = f"{d['Motivo']} {d['Sintomas']} {d['Familia']} {d['Historia']} {d['Personalidad']}".lower()
    
    # Enlaces de tus carpetas de Google Drive
    drive_psico = "https://drive.google.com/drive/folders/1lrH7AKPKXOVeFkcc_EdO03E0Ar5k4wbv"
    drive_proy = "https://drive.google.com/drive/folders/1yji6O5YIcYOjW1IG0fIhp4MJZgrcToys"
    
    # Diagnóstico por defecto
    analisis = {
        "diagnostico": "Sin indicadores de patología grave. Perfil adaptativo.",
        "tests": f"Batería estándar (16PF, Barsit, Raven): {drive_psico}",
        "terapia": "Sesiones de consejería y apoyo emocional."
    }

    # Lógica de detección basada en palabras clave de toda la entrevista
    if any(x in entrevista_total for x in ["morir", "suicid", "triste", "solo", "vacío", "culpa"]):
        analisis["diagnostico"] = "INDICADORES DE DEPRESIÓN CON POSIBLE RIESGO AUTOLÍTICO."
        analisis["tests"] = f"Aplicar MMPI-2, Escala de Beck y SCL-90-R: {drive_psico}"
        analisis["terapia"] = "Terapia Cognitivo-Conductual (TCC) con enfoque en activación conductual."

    elif any(x in entrevista_total for x in ["ira", "golpe", "impulso", "enojo", "pelea", "violento"]):
        analisis["diagnostico"] = "RASGOS DE IMPULSIVIDAD Y DIFICULTAD EN CONTROL DE AFECTOS."
        analisis["tests"] = f"Aplicar IPV, 16PF (Factores de estabilidad) y HTP: {drive_psico}"
        analisis["terapia"] = "Entrenamiento en asertividad y técnicas de control de impulsos."

    elif any(x in entrevista_total for x in ["voces", "veo", "sombras", "paranoid", "persiguen"]):
        analisis["diagnostico"] = "INDICADORES DE ALTERACIÓN EN EL JUICIO DE REALIDAD."
        analisis["tests"] = f"Batería Proyectiva (HTP, Machover, Persona Bajo la Lluvia): {drive_proy}"
        analisis["terapia"] = "Evaluación clínica profunda y remisión a psiquiatría."

    return analisis

# --- 4. INTERFAZ ---
st.title("🛡️ Gestión Clínica D.S.P. con IA")

db = cargar_db()
with st.sidebar:
    st.header("📂 Base de Datos")
    paciente_sel = st.selectbox("Seleccionar Expediente:", ["NUEVO REGISTRO"] + db["Nombre"].tolist())
    
    # Cargar datos si no es nuevo
    p = db[db["Nombre"] == paciente_sel].iloc[0].to_dict() if paciente_sel != "NUEVO REGISTRO" else {c: "" for c in COLS}

tabs = st.tabs(["Generales", "Clínica", "Historia", "IA y Resultados"])

with tabs[0]:
    c1, c2 = st.columns(2)
    nombre = c1.text_input("Nombre Completo", value=p.get("Nombre", ""))
    identidad = c2.text_input("Identidad", value=p.get("Identidad", ""))
    edad = st.text_input("Edad", value=p.get("Edad", ""))

with tabs[1]:
    motivo = st.text_area("II. Motivo de Consulta", value=p.get("Motivo", ""))
    opciones = ["Ganas de morir", "Escucha voces", "Insomnio", "Agresividad", "Consumo de Alcohol/Drogas"]
    sintomas = st.multiselect("V. Hallazgos:", opciones, default=[s for s in str(p.get("Sintomas", "")).split(", ") if s in opciones])

with tabs[2]:
    familia = st.text_area("VI. Familia", value=p.get("Familia", ""))
    historia = st.text_area("VII-IX. Desarrollo y Escolaridad", value=p.get("Historia", ""))
    personalidad = st.text_area("XI. Personalidad Previa", value=p.get("Personalidad", ""))

with tabs[3]:
    st.subheader("Análisis de IA y Citas")
    historial_seg = str(p.get("Seguimiento", ""))
    nueva_nota = st.text_area("Evolución de hoy:")
    
    st.divider()
    c3, c4 = st.columns(2)
    f_cita = c3.date_input("Próxima Cita", value=date.today())
    h_cita = c4.time_input("Hora", value=time(8, 0))

# --- 5. BOTÓN DE ACCIÓN ---
if st.button("💾 GUARDAR EN BASE DE DATOS Y ANALIZAR"):
    if nombre and motivo:
        # Preparar datos
        cita_full = f"{f_cita} {h_cita}"
        seguimiento_act = historial_seg + (f"\n[{date.today()}]: {nueva_nota}" if nueva_nota else "")
        
        datos_paciente = {
            "Nombre": nombre, "Identidad": identidad, "Edad": edad,
            "Motivo": motivo, "Sintomas": ", ".join(sintomas),
            "Familia": familia, "Historia": historia, "Personalidad": personalidad,
            "Seguimiento": seguimiento_act, "Proxima_Cita": cita_full
        }

        # Ejecutar IA
        res_ia = motor_ia_clinico(datos_paciente)
        
        st.subheader("🧠 Resultados de la IA")
        st.error(f"**Diagnóstico:** {res_ia['diagnostico']}")
        st.info(f"**Tests Sugeridos:** {res_ia['tests']}")
        st.success(f"**Plan:** {res_ia['terapia']}")

        # Guardar en Excel
        guardar_en_db(datos_paciente)
        
        # Generar Word
        doc = Document()
        doc.add_heading(f"EXPEDIENTE D.S.P. - {nombre}", 0)
        doc.add_heading("Resultados de la IA", level=1)
        doc.add_paragraph(f"Diagnóstico: {res_ia['diagnostico']}")
        doc.add_paragraph(f"Plan Terapéutico: {res_ia['terapia']}")
        
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        st.download_button("📥 Descargar Reporte Word", buf, f"DSP_{nombre}.docx")
    else:
        st.warning("El Nombre y el Motivo de consulta son necesarios.")
