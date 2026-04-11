import streamlit as st
import pandas as pd
import os
import io
from docx import Document
from datetime import datetime, date, time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="D.S.P. Honduras - Sistema Integral", layout="wide")
DB_FILE = "base_datos_dsp_v4.xlsx"

# Estructura de 6 páginas
CAMPOS = [
    "Nombre", "Identidad", "Edad", "Lugar_Nacimiento", "Grado_Militar", "Antigüedad", 
    "Motivo_Consulta", "Sintomas", "Enfermedades", "Medicamentos", "Sueno", "Apetito", 
    "Historia_Familiar", "Desarrollo_Infantil", "Historia_Escolar", "Historia_Sexual", 
    "Examen_Mental", "Personalidad_Previa", "Seguimiento", "Proxima_Cita"
]

# --- 2. FUNCIONES DE DATOS (REPARADAS) ---
def cargar_db():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame(columns=CAMPOS)
    try:
        df = pd.read_excel(DB_FILE)
        df = df.astype(str).replace('nan', '')
        for c in CAMPOS:
            if c not in df.columns: df[c] = ""
        return df
    except Exception:
        return pd.DataFrame(columns=CAMPOS)

def guardar_db(datos):
    df = cargar_db()
    if not df.empty and datos["Nombre"] in df["Nombre"].values:
        df = df[df["Nombre"] != datos["Nombre"]]
    df = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
    df.to_excel(DB_FILE, index=False)

# --- 3. MOTOR DE IA ---
def motor_ia_dsp(d):
    # Analiza la totalidad de la información
    corpus = f"{d['Motivo_Consulta']} {d['Sintomas']} {d['Examen_Mental']} {d['Personalidad_Previa']}".lower()
    drive = "https://drive.google.com/drive/folders/1lrH7AKPKXOVeFkcc_EdO03E0Ar5k4wbv"
    
    res = {"diag": "Estable.", "tests": f"16PF: {drive}", "plan": "Seguimiento preventivo."}

    if any(x in corpus for x in ["morir", "suicid", "triste", "solo"]):
        res = {"diag": "RIESGO DEPRESIVO/SUICIDA", "tests": f"MMPI-2 y Beck: {drive}", "plan": "Intervención urgente."}
    elif any(x in corpus for x in ["ira", "impulso", "enojo", "arma"]):
        res = {"diag": "CONTROL DE IMPULSOS", "tests": f"IPV e HTP: {drive}", "plan": "Manejo de ira."}
    return res

# --- 4. INTERFAZ ---
st.title("🛡️ Gestión Clínica D.S.P. Honduras")
db = cargar_db()

with st.sidebar:
    st.header("📂 Expedientes")
    sel = st.selectbox("Paciente:", ["NUEVO REGISTRO"] + db["Nombre"].tolist())
    p = db[db["Nombre"] == sel].iloc[0].to_dict() if sel != "NUEVO REGISTRO" else {c: "" for c in CAMPOS}

tabs = st.tabs(["I. Generales", "II. Clínica", "III. Historia", "IV. Examen/IA"])

with tabs[0]:
    st.subheader("Datos Militares y Generales")
    c1, c2 = st.columns(2)
    nombre = c1.text_input("Nombre", value=p["Nombre"])
    identidad = c2.text_input("Identidad", value=p["Identidad"])
    grado = c1.text_input("Rango Militar", value=p["Grado_Militar"])
    antigüedad = c2.text_input("Antigüedad", value=p["Antigüedad"])

with tabs[1]:
    st.subheader("Motivo y Salud")
    motivo = st.text_area("Motivo de Consulta", value=p["Motivo_Consulta"])
    sintomas = st.text_area("Sintomatología Detallada", value=p["Sintomas"])
    c3, c4, c5 = st.columns(3)
    sueno = c3.text_input("Sueño", value=p["Sueno"])
    apetito = c4.text_input("Apetito", value=p["Apetito"])
    meds = c5.text_input("Medicamentos", value=p["Medicamentos"])

with tabs[2]:
    st.subheader("Historias de
