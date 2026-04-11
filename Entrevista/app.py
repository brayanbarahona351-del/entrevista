import streamlit as st
import pandas as pd
import os
import io
from docx import Document
from datetime import datetime, date, time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="D.S.P. - Gestión Integral", layout="wide")
DB_FILE = "base_datos_pacientes.xlsx"

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_db():
    if os.path.exists(DB_FILE):
        df = pd.read_excel(DB_FILE)
        # Aseguramos que existan las columnas de seguimiento y citas
        for col in ["Seguimiento", "Proxima_Cita"]:
            if col not in df.columns:
                df[col] = ""
        return df
    else:
        return pd.DataFrame(columns=["Nombre", "Identidad", "Edad", "Motivo", "Sintomas", "Historia", "Personalidad", "Diagnostico", "Recomendaciones", "Seguimiento", "Proxima_Cita"])

def guardar_en_db(datos):
    df = cargar_db()
    if datos["Nombre"] in df["Nombre"].values:
        # Actualizamos fila existente
        idx = df.index[df["Nombre"] == datos["Nombre"]][0]
        for key, value in datos.items():
            df.at[idx, key] = value
    else:
        df = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
    df.to_excel(DB_FILE, index=False)

# --- INTERFAZ ---
st.title("🛡️ Sistema D.S.P. - Entrevista, Seguimiento y Citas")

df_db = cargar_db()

# SIDEBAR: GESTIÓN DE EXPEDIENTES Y AGENDA
with st.sidebar:
    st.header("📂 Expedientes")
    sel = st.selectbox("Buscar Paciente:", ["NUEVO REGISTRO"] + df_db["Nombre"].tolist())
    p = df_db[df_db["Nombre"] == sel].iloc[0].to_dict() if sel != "NUEVO REGISTRO" else {}
    
    st.divider()
    st.header("📅 Próximas Citas")
    # Mostrar solo pacientes que tienen cita programada
    citas_activas = df_db[df_db["Proxima_Cita"].notna() & (df_db["Proxima_Cita"] != "")]
    if not citas_activas.empty:
        for i, row in citas_activas.iterrows():
            st.info(f"👤 {row['Nombre']}\n🗓️ {row['Proxima_Cita']}")
    else:
        st.write("No hay citas programadas.")

# PESTAÑAS
tabs = st.tabs(["I-V. Clínica", "VI-IX. Historia", "X-XI. Personalidad", "📈 Seguimiento", "📅 Programar Cita"])

# (Las pestañas de Clínica, Historia y Personal
