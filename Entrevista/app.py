import streamlit as st
import pandas as pd
import os
import io
from docx import Document
from datetime import datetime, date, time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="D.S.P. Honduras - Sistema Seguro", layout="wide")
DB_FILE = "base_datos_dsp_v3.xlsx"

# Definición de todos los campos del protocolo de 6 páginas
CAMPOS = [
    "Nombre", "Identidad", "Edad", "Rango_Militar", "Antigüedad", 
    "Motivo_Consulta", "Sintomas", "Enfermedades", "Operaciones", 
    "Medicamentos", "Funciones_Org", "Historia_Familiar", 
    "Historia_Escolar", "Historia_Sexual", "Examen_Mental", 
    "Personalidad_Previa", "Seguimiento", "Proxima_Cita"
]

# --- 2. FUNCIONES DE DATOS ---
def cargar_db():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame(columns=CAMPOS)
    try:
        df = pd.read_excel(DB_FILE)
        return df.astype(str).replace('nan', '')
    except:
        return pd.DataFrame(columns=CAMPOS)

def guardar_db(datos):
    df = cargar_db()
    if not df.empty and datos["Nombre"] in df["Nombre"].values:
        df = df[df["Nombre"] != datos["Nombre"]]
    df = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
    df.to_excel(DB_FILE, index=False)

# --- 3. MOTOR DE IA ---
def analizar_caso(d):
    texto = f"{d['Motivo_Consulta']} {d['Sintomas']} {d['Examen_Mental']}".lower()
    drive = "https://drive.google.com/drive/folders/1lrH7AKPKXOVeFkcc_EdO03E0Ar5k4wbv"
    
    res = {"diag": "Perfil Adaptativo", "tests": f"Batería Básica: {drive}", "plan": "Monitoreo"}
    
    if any(x in texto for x in ["morir", "suicid", "solo"]):
        res = {"diag": "RIESGO DEPRESIVO", "tests": f"MMPI-2 / Beck: {drive}", "plan": "Intervención Urgente"}
    elif any(x in texto for x in ["ira", "golpe", "pelea"]):
        res = {"diag": "IMPULSIVIDAD", "tests": f"IPV / 16PF: {drive}", "plan": "Control de Impulsos"}
    return res

# --- 4. INTERFAZ ---
st.title("🛡️ Sistema de Gestión Psicológica D.S.P.")
db = cargar_db()

with st.sidebar:
    st.header("📂 Expedientes")
    sel = st.selectbox("Buscar:", ["NUEVO REGISTRO"] + db["Nombre"].tolist())
    # Si es nuevo, inicializa todo vacío. Si existe, carga los datos.
    p = db[db["Nombre"] == sel].iloc[0].to_dict() if sel != "NUEVO REGISTRO" else {c: "" for c in CAMPOS}

tabs = st.tabs(["I. Datos", "II. Clínica", "III. Historias", "IV. Examen/IA"])

with tabs[0]:
    c1, c2 = st.columns(2)
    nombre = c1.text_input("Nombre Completo", value=p["Nombre"])
    identidad = c2.text_input("Identidad", value=p["Identidad"])
    rango = c1.text_input("Rango Militar", value=p["Rango_Militar"])
    edad = c2.text_input("Edad", value=p["Edad"])

with tabs[1]:
    motivo = st.text_area("Motivo de Consulta", value=p["Motivo_Consulta"])
    sintomas = st.text_area("Síntomas y Hallazgos", value=p["Sintomas"])
    c3, c4 = st.columns(2)
    enf = c3.text_input("Enfermedades", value=p["Enfermedades"])
    med = c4.text_input("Medicamentos", value=p["Medicamentos"])

with tabs[2]:
    familia = st.text_area("Historia Familiar", value=p["Historia_Familiar"])
    sexual = st.text_area("Historia Sexual", value=p["Historia_Sexual"])
    escolar = st.text_area("Historia Escolar", value=p["Historia_Escolar"])

with tabs[3]:
    examen = st.text_area("Examen Mental", value=p["Examen_Mental"])
    perso = st.text_area("Personalidad Previa", value=p["Personalidad_Previa"])
    st.divider()
    nota_hoy = st.text_area("Nota de Seguimiento:")
    f_cita = st.date_input("Próxima Cita")

# --- 5. BOTÓN FINAL ---
if st.button("💾 GUARDAR Y ANALIZAR"):
    if nombre and motivo:
        # Construir el diccionario de datos
        datos_finales = {
            "Nombre": nombre, "Identidad": identidad, "Edad": edad, 
            "Rango_Militar": rango, "Motivo_Consulta": motivo, 
            "Sintomas": sintomas, "Enfermedades": enf, "Medicamentos": med,
            "Historia_Familiar": familia, "Historia_Sexual": sexual, 
            "Historia_Escolar": escolar, "Examen_Mental": examen, 
            "Personalidad_Previa": perso, 
            "Seguimiento": p["Seguimiento"] + f"\n[{date.today()}]: {nota_hoy}",
            "Proxima_Cita": str(f_cita)
        }
        
        # IA y Guardado
        res_ia = analizar_caso(datos_finales)
        guardar_db(datos_finales)
        
        # Mostrar resultados
        st.subheader("🧠 Análisis de IA")
        st.error(f"Diagnóstico: {res_ia['diag']}")
        st.info(f"Pruebas: {res_ia['tests']}")
        
        # Generar Word
        doc = Document()
        doc.add_heading('EXPEDIENTE D.S.P.', 0)
        for k, v in datos_finales.items():
            doc.add_paragraph(f"{k}: {v}")
        
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        st.download_button("📥 Descargar Word", buf, f"Expediente_{nombre}.docx")
    else:
        st.warning("Complete el Nombre y el Motivo.")
