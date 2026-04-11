import streamlit as st
import pandas as pd
import os
import io
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Sistema IA D.S.P. Honduras", layout="wide")
DB_FILE = "base_datos_pacientes.xlsx"

# --- FUNCIONES DE BASE DE DATOS (EXCEL PRIVADO) ---
def cargar_db():
    if os.path.exists(DB_FILE):
        return pd.read_excel(DB_FILE)
    else:
        return pd.DataFrame(columns=["Nombre", "Identidad", "Edad", "Motivo", "Sintomas", "Historia", "Personalidad", "Diagnostico", "Recomendaciones"])

def guardar_en_db(datos):
    df = cargar_db()
    if datos["Nombre"] in df["Nombre"].values:
        df.loc[df["Nombre"] == datos["Nombre"]] = datos
    else:
        df = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
    df.to_excel(DB_FILE, index=False)

# --- MOTOR DE INTELIGENCIA ARTIFICIAL ---
def motor_ia_clinica(motivo, personalidad, sintomas_list):
    texto = (motivo + " " + personalidad).lower()
    # Enlaces de tus carpetas de Drive
    folder_psicometria = "https://drive.google.com/drive/folders/1lrH7AKPKXOVeFkcc_EdO03E0Ar5k4wbv"
    folder_proyectivos = "https://drive.google.com/drive/folders/1yji6O5YIcYOjW1IG0fIhp4MJZgrcToys"
    
    diag = "Paciente orientado, sin indicadores de psicopatología aguda evidente en el discurso inicial."
    tests = []
    terapia = "Acompañamiento psicológico para fortalecimiento de rasgos de personalidad."

    # Lógica de detección basada en tus manuales
    if any(x in texto for x in ["morir", "suicid", "triste", "solo", "desesperanza"]):
        diag = "INDICADORES DEPRESIVOS / RIESGO AUTOLÍTICO: Se detecta lenguaje de desesperanza y afecto negativo."
        tests.append(f"MMPI-2 y SCL-90-R (Foco en escalas clínicas): {folder_psicometria}")
        terapia = "Terapia Cognitivo-Conductual (TCC) centrada en reestructuración cognitiva y prevención de riesgo."

    if any(x in texto for x in ["ira", "golpe", "impulso", "enojo", "pelea"]):
        diag = "INDICADORES DE AGRESIVIDAD: Tendencia a la reactividad impulsiva y baja tolerancia a la frustración."
        tests.append(f"16PF-5 (Factores O, Q4) e IPV: {folder_psicometria}")
        terapia = "Entrenamiento en Control de Impulsos y técnicas de Desactivación Fisiológica."

    if any(x in texto for x in ["voces", "sombras", "paranoid", "persiguen"]):
        diag = "INDICADORES PSICÓTICOS: Alteraciones en el juicio de realidad y posible distorsión perceptiva."
        tests.append(f"Batería Proyectiva (HTP, Machover, Persona bajo la lluvia): {folder_proyectivos}")
        terapia = "Evaluación psiquiátrica complementaria e intervención clínica profunda."

    if not tests:
        tests.append(f"Evaluación Psicométrica de Rutina (Barsit y 16PF): {folder_psicometria}")

    return {
        "DIAGNOSTICO": diag,
        "TESTS": "\n".join(tests),
        "TERAPIA": terapia
    }

# --- GENERADOR DE WORD ---
def generar_word_dsp(datos_e, resultados_ia):
    doc = Document()
    doc.add_heading('DIRECCIÓN DE SANIDAD POLICIAL (D.S.P.)', 0)
    doc.add_heading('INFORME PSICOLÓGICO Y RESULTADOS DE IA', level=1)

    for sec, campos in datos_e.items():
        doc.add_heading(sec, level=2)
        for k, v in campos.items():
            doc.add_paragraph(f"{k}: {v}")

    doc.add_page_break()
    doc.add_heading('ANÁLISIS E INTERPRETACIÓN DE IA', level=1)
    doc.add_heading('Impresión Diagnóstica:', level=2)
    doc.add_paragraph(resultados_ia["DIAGNOSTICO"])
    doc.add_heading('Batería de Tests Recomendada (Links Directos):', level=2)
    doc.add_paragraph(resultados_ia["TESTS"])
    doc.add_heading('Plan Terapéutico Sugerido:', level=2)
    doc.add_paragraph(resultados_ia["TERAPIA"])

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- INTERFAZ ---
st.title("🧠 Asistente Clínico Inteligente D.S.P.")

df_db = cargar_db()
with st.sidebar:
    st.header("📂 Expedientes")
    sel = st.selectbox("Buscar Paciente:", ["NUEVO REGISTRO"] + df_db["Nombre"].tolist())
    p = df_db[df_db["Nombre"] == sel].iloc[0].to_dict() if sel != "NUEVO REGISTRO" else {}

tabs = st.tabs(["Datos", "Clínica", "Historia", "IA y Resultados"])

with tabs[0]:
    nombre = st.text_input("Nombre Completo", value=p.get("Nombre", ""))
    identidad = st.text_input("Identidad", value=p.get("Identidad", ""))
    edad = st.text_input("Edad", value=p.get("Edad", ""))

with tabs[1]:
    motivo = st.text_area("Motivo de Consulta", value=p.get("Motivo", ""))
    s_lista = ["Ganas de morir", "Escucha voces", "Insomnio", "Agresividad", "Consumo drogas"]
    s_guardados = str(p.get("Sintomas", "")).split(", ")
    sintomas = st.multiselect("Síntomas:", s_lista, default=[s for s in s_guardados if s in s_lista])

with tabs[2]:
    familia = st.text_area("Historia Familiar", value=p.get("Familia", ""))
    desarrollo = st.text_area("Desarrollo Infantil/Escolar", value=p.get("Historia", ""))
    personalidad = st.text_area("Rasgos de Personalidad", value=p.get("Personalidad", ""))

with tabs[3]:
    if st.button("🔍 ANALIZAR CASO CON IA"):
        if nombre and motivo:
            res_ia = motor_ia_clinica(motivo, personalidad, sintomas)
            st.subheader("Resultados del Análisis:")
            st.warning(f"**Impresión Diagnóstica:** {res_ia['DIAGNOSTICO']}")
            st.info(f"**Tests Recomendados:** {res_ia['TESTS']}")
            st.success(f"**Plan de Terapia:** {res_ia['TERAPIA']}")
            
            # Guardar en Base de Datos
            datos_save = {
                "Nombre": nombre, "Identidad": identidad, "Edad": edad, "Motivo": motivo,
                "Sintomas": ", ".join(sintomas), "Familia": familia, "Historia": desarrollo,
                "Personalidad": personalidad, "Diagnostico": res_ia["DIAGNOSTICO"], "Recomendaciones": res_ia["TESTS"]
            }
            guardar_en_db(datos_save)
            
            # Generar Word
            datos_doc = {
                "I. DATOS": {"Nombre": nombre, "ID": identidad, "Edad": edad},
                "II. CLÍNICA": {"Motivo": motivo, "Sintomas": ", ".join(sintomas)},
                "III. HISTORIA": {"Familiar": familia, "Desarrollo": desarrollo, "Personalidad": personalidad}
            }
            word_file = generar_word_dsp(datos_doc, res_ia)
            
            st.download_button("⬇️ Descargar Expediente Word", word_file, f"DSP_{nombre}.docx")
        else:
            st.error("Nombre y Motivo son obligatorios.")

st.divider()
with st.expander("🔐 Administración Privada"):
    clave = st.text_input("Clave Maestra", type="password")
    if clave == "DSP2024":
        st.dataframe(cargar_db())
        with open(DB_FILE, "rb") as f:
            st.download_button("📥 Descargar Base de Datos Excel", f, "DB_Pacientes.xlsx")
