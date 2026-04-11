import streamlit as st
import pandas as pd
import os
import io
from docx import Document
from datetime import datetime, date, time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="D.S.P. Honduras - Sistema Inteligente", layout="wide")
DB_FILE = "base_datos_pacientes.xlsx"

COLS = [
    "Nombre", "Identidad", "Edad", "Lugar_Nac", "Religion", "Ocupacion", 
    "Militar", "Motivo", "Sintomas", "Funciones_Org", "Antecedentes_Fam", 
    "Desarrollo_Inf", "Historia_Escolar", "Historia_Sexual", 
    "Personalidad_Previa", "Seguimiento", "Proxima_Cita"
]

# --- 2. FUNCIONES DE DATOS ---
def cargar_db():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame(columns=COLS)
    try:
        df = pd.read_excel(DB_FILE)
        df = df.astype(str).replace('nan', '')
        for col in COLS:
            if col not in df.columns:
                df[col] = ""
        return df
    except:
        return pd.DataFrame(columns=COLS)

def guardar_en_db(datos_dict):
    df = cargar_db()
    nuevo_registro = {k: str(v) for k, v in datos_dict.items()}
    if not df.empty and nuevo_registro["Nombre"] in df["Nombre"].values:
        df = df[df["Nombre"] != nuevo_registro["Nombre"]]
    df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)
    df.to_excel(DB_FILE, index=False)

# --- 3. MOTOR DE IA (ANALIZA TODA LA ENTREVISTA) ---
def analizar_ia_completo(d):
    # Unimos los textos clave para el análisis
    texto_analisis = f"{d['Motivo']} {d['Sintomas']} {d['Antecedentes_Fam']} {d['Personalidad_Previa']}".lower()
    
    # Enlaces de tus carpetas de Drive
    drive_psico = "https://drive.google.com/drive/folders/1lrH7AKPKXOVeFkcc_EdO03E0Ar5k4wbv"
    drive_proy = "https://drive.google.com/drive/folders/1yji6O5YIcYOjW1IG0fIhp4MJZgrcToys"
    
    # Resultados por defecto
    res = {
        "diag": "Sin indicadores agudos detectados.",
        "tests": f"Batería básica (16PF y Barsit): {drive_psico}",
        "plan": "Seguimiento psicológico de rutina."
    }

    # Lógica de detección de riesgos
    if any(word in texto_analisis for word in ["morir", "suicid", "triste", "solo", "vacío"]):
        res["diag"] = "INDICADORES DEPRESIVOS / RIESGO AUTOLÍTICO."
        res["tests"] = f"Aplicar MMPI-2, SCL-90-R y Beck: {drive_psico}"
        res["plan"] = "Psicoterapia Cognitivo-Conductual y plan de seguridad inmediato."
        
    elif any(word in texto_analisis for word in ["ira", "golpe", "impulso", "enojo", "pelea"]):
        res["diag"] = "RASGOS DE IMPULSIVIDAD / BAJO CONTROL DE IRA."
        res["tests"] = f"Aplicar 16PF (Escala Q4) e IPV: {drive_psico}"
        res["plan"] = "Entrenamiento en asertividad y manejo de estrés."
        
    elif any(word in texto_analisis for word in ["voces", "veo", "sombras", "paranoid"]):
        res["diag"] = "POSIBLE ALTERACIÓN PERCEPTIVA O JUICIO DE REALIDAD."
        res["tests"] = f"Batería Proyectiva (HTP, Machover, Persona bajo la lluvia): {drive_proy}"
        res["plan"] = "Evaluación clínica profunda y posible interconsulta psiquiátrica."

    return res

# --- 4. INTERFAZ ---
df_db = cargar_db()

with st.sidebar:
    st.header("📂 Expedientes")
    opciones = ["NUEVO REGISTRO"] + df_db["Nombre"].tolist()
    sel = st.selectbox("Buscar Paciente:", opciones)
    p = df_db[df_db["Nombre"] == sel].iloc[0].to_dict() if sel != "NUEVO REGISTRO" else {c: "" for c in COLS}

st.title("🛡️ Asistente Clínico Inteligente D.S.P.")

tabs = st.tabs(["I. Generales", "II-V. Clínica", "VI-IX. Historia", "X-XI. Personalidad", "📈 Seguimiento"])

with tabs[0]:
    nombre = st.text_input("Nombre Completo", value=p.get("Nombre", ""))
    identidad = st.text_input("Identidad", value=p.get("Identidad", ""))
    edad = st.text_input("Edad", value=p.get("Edad", ""))

with tabs[1]:
    motivo = st.text_area("II. Motivo de Consulta", value=p.get("Motivo", ""))
    s_op = ["Ganas de morir", "Escucha voces", "Insomnio", "Agresividad", "Consumo sustancias"]
    s_prev = str(p.get("Sintomas", "")).split(", ")
    sintomas = st.multiselect("V. Síntomas detectados:", s_op, default=[s for s in s_prev if s in s_op])

with tabs[2]:
    familia = st.text_area("VI-IX. Familia y Antecedentes", value=p.get("Antecedentes_Fam", ""))
    escolar = st.text_area("Historia Escolar y Desarrollo", value=p.get("Historia_Escolar", ""))

with tabs[3]:
    sexual = st.text_area("X. Historia Sexual", value=p.get("Historia_Sexual", ""))
    personalidad = st.text_area("XI. Rasgos de Personalidad", value=p.get("Personalidad_Previa", ""))

with tabs[4]:
    st.subheader("Bitácora y Citas")
    historial = str(p.get("Seguimiento", ""))
    st.text_area("Historial previo:", value=historial, height=100, disabled=True)
    nueva_nota = st.text_area("Evolución de hoy:")
    c1, c2 = st.columns(2)
    f_cita = c1.date_input("Próxima Cita", value=date.today())
    h_cita = c2.time_input("Hora sugerida", value=time(8, 0))

# --- 5. PROCESAMIENTO ---
st.divider()
if st.button("💾 ANALIZAR CASO Y GUARDAR TODO"):
    if nombre and motivo:
        # Nota acumulativa
        final_seg = historial + (f"\n[{date.today()}]: {nueva_nota}" if nueva_nota else "")
        cita_str = f"{f_cita} {h_cita}"
        
        datos = {
            "Nombre": nombre, "Identidad": identidad, "Edad": edad,
            "Motivo": motivo, "Sintomas": ", ".join(sintomas),
            "Antecedentes_Fam": familia, "Historia_Escolar": escolar, 
            "Historia_Sexual": sexual, "Personalidad_Previa": personalidad,
            "Seguimiento": final_seg, "Proxima_Cita": cita_str
        }

        # Ejecución de IA
        ia = analizar_ia_completo(datos)
        
        st.subheader("🧠 Resultados del Análisis de IA")
        st.error(f"**Impresión Diagnóstica:** {ia['diag']}")
        st.info(f"**Tests Sugeridos:** {ia['tests']}")
        st.success(f"**Plan Terapéutico:** {ia['plan']}")

        # Guardado y Word
        guardar_en_db(datos)
        
        doc = Document()
        doc.add_heading('EXPEDIENTE PSICOLÓGICO D.S.P.', 0)
        for k, v in datos.items():
            doc.add_paragraph(f"{k}: {v}")
        
        doc.add_page_break()
        doc.add_heading('ANÁLISIS E INTERPRETACIÓN IA', level=1)
        doc.add_paragraph(f"Diagnóstico: {ia['diag']}")
        doc.add_paragraph(f"Tests Recomendados: {ia['tests']}")
        doc.add_paragraph(f"Plan Terapéutico: {ia['plan']}")
        
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        st.download_button("📥 Descargar Documento Word", buf, f"DSP_{nombre}.docx")
    else:
        st.error("Es obligatorio ingresar el Nombre y el Motivo de Consulta.")
