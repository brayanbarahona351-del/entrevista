import streamlit as st
import pandas as pd
import os
import io
from docx import Document
from datetime import datetime, date, time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="D.S.P. Honduras - Sistema Inteligente", layout="wide")
DB_FILE = "base_datos_pacientes.xlsx"

# Columnas oficiales del sistema
COLS = [
    "Nombre", "Identidad", "Edad", "Lugar_Nac", "Religion", "Ocupacion", 
    "Militar", "Motivo", "Sintomas", "Funciones_Org", "Antecedentes_Fam", 
    "Desarrollo_Inf", "Historia_Escolar", "Historia_Sexual", 
    "Personalidad_Previa", "Seguimiento", "Proxima_Cita"
]

# --- 2. FUNCIONES DE DATOS (A PRUEBA DE ERRORES) ---
def cargar_db():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame(columns=COLS)
    try:
        df = pd.read_excel(DB_FILE)
        # Forzar a que todo sea texto para evitar el TypeError
        df = df.astype(str).replace('nan', '')
        for col in COLS:
            if col not in df.columns:
                df[col] = ""
        return df
    except:
        return pd.DataFrame(columns=COLS)

def guardar_en_db(datos_dict):
    df = cargar_db()
    # Convertir todos los valores a string para evitar conflictos de tipo
    nuevo_registro = {k: str(v) for k, v in datos_dict.items()}
    
    if not df.empty and nuevo_registro["Nombre"] in df["Nombre"].values:
        df = df[df["Nombre"] != nuevo_registro["Nombre"]] # Eliminar viejo
    
    df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
    df.to_excel(DB_FILE, index=False)

# --- 3. MOTOR DE IA (ANALIZA TODA LA ENTREVISTA) ---
def analizar_ia_completo(d):
    # Unificamos todo el texto de la entrevista para el análisis
    full_text = f"{d['Motivo']} {d['Sintomas']} {d['Antecedentes_Fam']} {d['Personalidad_Previa']} {d['Historia_Sexual']}".lower()
    
    # Enlaces de tus carpetas
    f_psicometria = "https
