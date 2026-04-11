import streamlit as st
import pandas as pd
import os
import io
from docx import Document
from datetime import datetime, date, time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema Integral D.S.P.", layout="wide")
DB_FILE = "base_datos_completa_dsp.xlsx"

# Lista maestra de todas las columnas del protocolo oficial
COLS_OFICIALES = [
    "Nombre", "Identidad", "Edad", "Lugar_Nacimiento", "Estado_Civil", "Religion", 
    "Ocupacion", "Grado_Militar", "Antigüedad", "Motivo_Consulta", "Sintomas", 
    "Enfermedades_Previas", "Operaciones", "Medicamentos", "Funciones_Organicas",
    "Historia_Familiar", "Desarrollo_Infantil", "Historia_Escolar", 
    "Historia_Sexual", "Examen_Mental", "Personalidad_Previa", 
    "Seguimiento", "Proxima_Cita"
]

# --- 2. FUNCIONES DE DATOS ---
def cargar_db():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame(columns=COLS_OFICIALES)
    try:
        df = pd.read_excel(DB_FILE)
        df = df.astype(str).replace('nan', '')
        # Asegurar que todas las columnas existan si el excel es viejo
        for col in COLS_OFICIALES:
            if col not in df.columns:
                df[col] = ""
        return df
    except:
        return pd.DataFrame(columns=COLS_OFICIALES)

def guardar_en_db(datos):
    df = cargar_db()
    nuevo_reg = {k: str(v) for k, v in datos.items()}
    if not df.empty and nuevo_reg["Nombre"] in df["Nombre"].values:
        df = df[df["Nombre"] != nuevo_reg["Nombre"]]
    df = pd.concat([df, pd.DataFrame([nuevo_reg])], ignore_index=True)
    df.to_excel(DB_FILE, index=False)

# --- 3. MOTOR DE IA (ESCANEA TODA LA ENTREVISTA) ---
def motor_ia_avanzado(d):
    # Unificamos toda la información para una lectura profunda
    corpus = f"{d['Motivo_Consulta']} {d['Sintomas']} {d['Examen_Mental']} {d['Personalidad_Previa']} {d['Historia_Familiar']}".lower()
    
    psico_drive = "https://drive.google.com/drive/folders/1lrH7AKPKXOVeFkcc_EdO03E0Ar5k4wbv"
    proy_drive = "https://drive.google.com/drive/folders/1yji6O5YIcYOjW1IG0fIhp4MJZgrcToys"
    
    res = {"diag": "Perfil estable.", "tests": f"16PF y Barsit: {psico_drive}", "plan": "Orientación psicológica."}

    # Lógica de detección de patrones
    if any(x in corpus for x in ["morir", "suicid", "triste", "solo", "desesperanza", "vacío"]):
        res = {
            "diag": "SINTOMATOLOGÍA DEPRESIVA / ALTO RIESGO AUTOLÍTICO.",
            "tests": f"MMPI-2, Escala de Beck y SCL-90-R: {psico_drive}",
            "plan": "Psicoterapia Cognitivo-Conductual y activación de protocolo de seguridad."
        }
    elif any(x in corpus for x in ["ira", "golpe", "impulso", "enojo", "pelea", "arma", "agresivo"]):
        res = {
            "diag": "RASGOS DE IMPULSIVIDAD Y DIFICULTAD EN CONTROL DE AGRESIVIDAD.",
            "tests": f"16PF (Q4), IPV y Test de la Figura Humana: {psico_drive}",
            "plan": "Entrenamiento en manejo de ira y técnicas de desensibilización."
        }
    elif any(x in corpus for x in ["voces", "veo", "sombras", "paranoid", "miedo", "persecucion"]):
        res = {
            "diag": "INDICADORES DE PSICOSIS O ALTERACIÓN PERCEPTIVA.",
            "tests": f"Batería Proyectiva Completa (HTP, Persona bajo la lluvia): {proy_drive}",
            "plan": "Evaluación por Psiquiatría y contención clínica inmediata."
        }
    return res

# --- 4. INTERFAZ ---
st.title("🧠 Sistema de Evaluación Psicológica D.S.P.")
db = cargar_db()

with st.sidebar:
    st.header("📂 Expedientes Actuales")
    sel = st.selectbox("Seleccionar:", ["NUEVO REGISTRO"] + db["Nombre"].tolist())
    p = db[db["Nombre"] == sel].iloc[0].to_dict() if sel != "NUEVO REGISTRO" else {c: "" for c in COLS_OFICIALES}

# Organización por Pestañas Técnicas
tabs = st.tabs(["I. Datos Generales", "II-V. Clínica", "VI-IX. Historia Personal", "X-XI. Examen y Personalidad", "📅 Citas y Seguimiento"])

with tabs[0]:
    st.subheader("I. DATOS GENERALES Y MILITARES")
    c1, c2 = st.columns(2)
    nombre = c1.text_input("Nombre Completo", value=p.get("Nombre", ""))
    identidad = c2.text_input("Identidad", value=p.get("Identidad", ""))
    edad = c1.text_input("Edad", value=p.get("Edad", ""))
    lugar = c2
