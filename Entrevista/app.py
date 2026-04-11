import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date, time

# 1. CONFIGURACIÓN Y COLUMNAS OFICIALES
st.set_page_config(page_title="D.S.P. Honduras", layout="wide")
DB_FILE = "base_datos_dsp_v5.xlsx"
CAMPOS = [
    "Nombre", "Identidad", "Edad", "Rango", "Antigüedad", "Motivo", "Sintomas", 
    "Salud_Meds", "Sueno_Apetito", "H_Familiar", "H_Infancia", "H_Escolar", 
    "H_Sexual", "Examen_Mental", "Personalidad", "Seguimiento", "Cita"
]

# 2. FUNCIONES DE DATOS
def cargar_db():
    if not os.path.exists(DB_FILE): return pd.DataFrame(columns=CAMPOS)
    try:
        df = pd.read_excel(DB_FILE)
        return df.astype(str).replace('nan', '')
    except: return pd.DataFrame(columns=CAMPOS)

def guardar_db(datos):
    df = cargar_db()
    if not df.empty and datos["Nombre"] in df["Nombre"].values:
        df = df[df["Nombre"] != datos["Nombre"]]
    pd.concat([df, pd.DataFrame([datos])], ignore_index=True).to_excel(DB_FILE, index=False)

# 3. MOTOR IA
def motor_ia(d):
    t = f"{d['Motivo']} {d['Sintomas']} {d['Examen_Mental']}".lower()
    url = "https://drive.google.com/drive/folders/1lrH7AKPKXOVeFkcc_EdO03E0Ar5k4wbv"
    if any(x in t for x in ["morir", "suicid", "triste"]):
        return "RIESGO DEPRESIVO", "MMPI-2 / BECK", "Intervención Urgente", url
    if any(x in t for x in ["ira", "pelea", "arma"]):
        return "CONTROL IMPULSOS", "IPV / 16PF", "Manejo de Ira", url
    return "Estable", "16PF / Barsit", "Seguimiento", url

# 4. INTERFAZ
st.title("🛡️ Sistema Integral D.S.P.")
db = cargar_db()
with st.sidebar:
    sel = st.selectbox("Expedientes:", ["NUEVO"] + db["Nombre"].tolist())
    p = db[db["Nombre"] == sel].iloc[0].to_dict() if sel != "NUEVO" else {c: "" for c in CAMPOS}

t1, t2, t3, t4 = st.tabs(["DATOS", "CLÍNICA", "HISTORIAS", "EXAMEN/IA"])

with t1:
    c1, c2 = st.columns(2)
    nom = c1.text_input("Nombre Completo", value=p["Nombre"])
    ide = c2.text_input("Identidad", value=p["Identidad"])
    ran = c1.text_input("Rango Militar", value=p["Rango"])
    eda = c2.text_input("Edad", value=p["Edad"])

with t2:
    mot = st.text_area("Motivo de Consulta", value=p["Motivo"])
    sin = st.text_area("Síntomas y Hallazgos", value=p["Sintomas"])
    sal = st.text_input("Salud y Medicamentos", value=p["Salud_Meds"])
    org = st.text_input("Sueño / Apetito", value=p["Sueno_Apetito"])

with t3:
    fam = st.text_area("Historia Familiar", value=p["H_Familiar"])
    inf = st.text_area("Desarrollo Infantil", value=p["H_Infancia"])
    esc = st.text_area("Historia Escolar", value=p["H_Escolar"])
    sex = st.text_area("Historia Sexual", value=p["H_Sexual"])

with t4:
    exm = st.text_area("Examen Mental", value=p["Examen_Mental"])
    per = st.text_area("Personalidad Previa", value=p["Personalidad"])
    st.divider()
    nota = st.text_area("Evolución de hoy:")
    cita = st.date_input("Próxima Cita")

# 5. PROCESAMIENTO
if st.button("💾 GUARDAR Y ANALIZAR"):
    if nom and mot:
        d_f = {
            "Nombre": nom, "Identidad": ide, "Edad": eda, "Rango": ran, "Antigüedad": p["Antigüedad"],
            "Motivo": mot, "Sintomas": sin, "Salud_Meds": sal, "Sueno_Apetito": org,
            "H_Familiar": fam, "H_Infancia": inf, "H_Escolar": esc, "H_Sexual": sex,
            "Examen_Mental": exm, "Personalidad": per,
            "Seguimiento": p["Seguimiento"] + f"\n[{date.today()}]: {nota}", "Cita": str(cita)
        }
        diag, test, plan, link = motor_ia(d_f)
        guardar_db(d_f)
        st.error(f"**IA Diagnóstico:** {diag}"); st.info(f"**Tests:** {test} ({link})"); st.success(f"**Plan:** {plan}")
        
        doc = Document()
        doc.add_heading('EXPEDIENTE D.S.P.', 0)
        for k, v in d_f.items(): doc.add_paragraph(f"{k}: {v}")
        buf = io.BytesIO(); doc.save(buf); buf.seek(0)
        st.download_button("📥 Descargar Word", buf, f"Expediente_{nom}.docx")
    else: st.warning("Nombre y Motivo requeridos.")
