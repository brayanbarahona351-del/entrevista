import streamlit as st
import pandas as pd
import os
import io
from docx import Document
from datetime import datetime, date, time

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="D.S.P. Honduras - Visión Completa", layout="wide")

# Forzamos que el archivo de base de datos sea nuevo si el anterior da problemas
DB_FILE = "base_datos_dsp_v2.xlsx"

# Lista maestra de campos oficiales
CAMPOS = [
    "Nombre", "Identidad", "Edad", "Lugar_Nacimiento", "Estado_Civil", "Religion", 
    "Ocupacion", "Grado_Militar", "Antigüedad", "Motivo_Consulta", "Sintomas", 
    "Enfermedades_Previas", "Operaciones", "Medicamentos", "Funciones_Organicas",
    "Historia_Familiar", "Desarrollo_Infantil", "Historia_Escolar", 
    "Historia_Sexual", "Examen_Mental", "Personalidad_Previa", 
    "Seguimiento", "Proxima_Cita"
]

# --- 2. FUNCIONES DE DATOS ---
def cargar_datos():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame(columns=CAMPOS)
    try:
        df = pd.read_excel(DB_FILE)
        df = df.astype(str).replace('nan', '')
        # Si faltan columnas por versiones viejas, las agregamos aquí
        for c in CAMPOS:
            if c not in df.columns:
                df[c] = ""
        return df
    except:
        return pd.DataFrame(columns=CAMPOS)

def guardar_datos(datos_dict):
    df = cargar_datos()
    # Convertir todo a string para evitar errores de visualización
    nuevo_registro = {k: str(v) for k, v in datos_dict.items()}
    
    if not df.empty and nuevo_registro["Nombre"] in df["Nombre"].values:
        df = df[df["Nombre"] != nuevo_registro["Nombre"]]
    
    df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
    df.to_excel(DB_FILE, index=False)

# --- 3. MOTOR DE IA ---
def analizar_ia(d):
    texto_total = f"{d['Motivo_Consulta']} {d['Sintomas']} {d['Examen_Mental']} {d['Personalidad_Previa']}".lower()
    
    # Enlaces oficiales de tus recursos
    p_drive = "https://drive.google.com/drive/folders/1lrH7AKPKXOVeFkcc_EdO03E0Ar5k4wbv"
    
    res = {"diag": "Estable", "tests": f"16PF: {p_drive}", "plan": "Seguimiento preventivo."}

    if any(x in texto_total for x in ["morir", "suicid", "triste", "solo"]):
        res = {"diag": "RIESGO DEPRESIVO/SUICIDA", "tests": f"MMPI-2 y Beck: {p_drive}", "plan": "Intervención en crisis y TCC."}
    elif any(x in texto_total for x in ["ira", "impulso", "pelea", "agresivo"]):
        res = {"diag": "CONTROL DE IMPULSOS", "tests": f"IPV y 16PF: {p_drive}", "plan": "Manejo de ira."}
    
    return res

# --- 4. INTERFAZ VISUAL ---
st.title("🛡️ Sistema de Gestión Psicológica D.S.P.")
st.markdown("---")

df_actual = cargar_datos()

# Sidebar para navegación
with st.sidebar:
    st.header("📂 Expedientes")
    paciente_sel = st.selectbox("Buscar por Nombre:", ["NUEVO REGISTRO"] + df_actual["Nombre"].tolist())
    p = df_actual[df_actual["Nombre"] == paciente_sel].iloc[0].to_dict() if paciente_sel != "NUEVO REGISTRO" else {c: "" for c in CAMPOS}
    
    if st.button("♻️ Limpiar Pantalla"):
        st.rerun()

# Pestañas Principales (Si no ves alguna, revisa el zoom del navegador)
tabs = st.tabs(["📋 Datos", "🩺 Clínica", "📖 Historia", "🧠 Examen y Personalidad", "📅 Citas"])

with tabs[0]:
    st.subheader("Información General")
    c1, c2 = st.columns(2)
    nombre = c1.text_input("Nombre", value=p.get("Nombre", ""))
    identidad = c2.text_input("ID", value=p.get("Identidad", ""))
    grado = c1.text_input("Grado Militar", value=p.get("Grado_Militar", ""))
    antigüedad = c2.text_input("Antigüedad", value=p.get("Antigüedad", ""))

with tabs[1]:
    st.subheader("Evaluación Clínica")
    motivo = st.text_area("Motivo de Consulta", value=p.
