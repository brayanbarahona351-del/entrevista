import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN Y BASE DE DATOS ---
st.set_page_config(page_title="D.S.P. Honduras - Sistema Maestro", layout="wide")
DB_FILE = "DB_DSP_HONDURAS_OFICIAL.xlsx"

def cargar_db():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    try: return pd.read_excel(DB_FILE).astype(str).replace('nan', '')
    except: return pd.DataFrame()

def guardar_db(datos_dict):
    df = cargar_db()
    if not df.empty and "Identidad" in df.columns:
        # Esto evita que se repita el paciente: borra el anterior antes de guardar el nuevo
        df = df[df["Identidad"] != str(datos_dict["Identidad"])]
    df_final = pd.concat([df, pd.DataFrame([datos_dict])], ignore_index=True)
    df_final.to_excel(DB_FILE, index=False)
    return df_final

# --- 2. MOTOR DE RECOMENDACIONES E IA ---
def generar_recomendaciones_auto(motivo, sintomas):
    recom = "Se sugiere: "
    tests = []
    texto = (str(motivo) + str(sintomas)).lower()
    
    if any(x in texto for x in ["triste", "morir", "suicida", "solo", "llanto"]):
        recom += "Intervención inmediata en crisis, vigilancia de red de apoyo y psicoterapia cognitivo-conductual para depresión. "
        tests = ["Beck (BDI-II) - https://bit.ly/test-beck", "SCL-90-R - https://bit.ly/scl-90"]
    elif any(x in texto for x in ["ira", "enojo", "golpe", "arma", "pelea"]):
        recom += "Entrenamiento en control de impulsos y manejo de la ira. Evaluación de personalidad antisocial. "
        tests = ["MMPI-2 - https://bit.ly/mmpi-2-ref", "16PF-5 - https://bit.ly/16pf5-ref"]
    else:
        recom += "Seguimiento psicológico quincenal para monitoreo de bienestar emocional. "
        tests = ["16PF-5 - https://bit.ly/16pf5-ref"]
        
    return recom, tests

# --- 3. GESTIÓN DE BÚSQUEDA ---
db_actual = cargar_db()
with st.sidebar:
    st.header("🔍 BUSCAR PACIENTE")
    opciones = ["--- NUEVO REGISTRO ---"]
    if not db_actual.empty:
        opciones += db_actual["Identidad"].tolist()
    
    seleccion = st.selectbox("Buscar por Identidad:", opciones)
    
    datos_cargados = {}
    if seleccion != "--- NUEVO REGISTRO ---":
        datos_cargados = db_actual[db_actual["Identidad"] == seleccion].iloc[0].to_dict()
        st.success(f"Cargado: {datos_cargados.get('Nombre')}")

st.title("🛡️ Protocolo de Entrevista e Informe D.S.P.")

# --- 4. TABS CON TODAS LAS PREGUNTAS ---
t1, t2, t3, t4, t5, t6 = st.tabs(["I-II. Generales", "III-V. Salud", "VI. Familia", "VII-IX. Desarrollo", "X-XII. Informe Final", "📊 Base de Datos"])

with t1:
    st.subheader("I. DATOS GENERALES")
    c1, c2, c3 = st.columns(3)
    identidad = c1.text_input("Identidad (Código Único)", value=datos_cargados.get("Identidad", ""))
    nombre = c2.text_input("Nombre Completo", value=datos_cargados.get("Nombre", ""))
    f_nac = c3.text_input("Fecha y Lugar Nacimiento", value=datos_cargados.get("F_Nac", ""))
    
    c4, c5, c6 = st.columns(3)
    edad = c4.text_input("Edad", value=datos_cargados.get("Edad", ""))
    sexo = c5.selectbox("Sexo", ["M", "F"], index=0 if datos_cargados.get("Sexo")=="M" else 1)
    est_civil = c6.text_input("Estado Civil", value=datos_cargados.get("Estado_Civil", ""))
    
    motivo = st.text_area("II. MOTIVO DE CONSULTA", value=datos_cargados.get("Motivo", ""))

with t2:
    st.subheader("III-V. SALUD Y SÍNTOMAS")
    f1, f2, f3, f4 = st.columns(4)
    sue = f1.text_input("Sueño", value=datos_cargados.get("Sueño", ""))
    ape = f2.text_input("Apetito", value=datos_cargados.get("Apetito", ""))
    sed = f3.text_input("Sed", value=datos_cargados.get("Sed", ""))
    defec_val = f4.text_input("Defecación", value=datos_cargados.get("Defec", ""))
    
    sintomas = st.multiselect("Checklist Síntomas:", ["Pesadillas", "Ideas Suicidas", "Ira", "Drogas", "Alcohol"], 
                              default=eval(datos_cargados.get("Checklist", "[]")) if datos_cargados else [])

with t3:
    st.subheader("VI. ÁREA FAMILIAR")
    p_rel = st.text_area("Relación con Padre y Castigos", value=datos_cargados.get("P_Rel", ""))
    m_rel = st.text_area("Relación con Madre y Castigos", value=datos_cargados.get("M_Rel", ""))
    hist_fel = st.text_area("Historia familiar feliz", value=datos_cargados.get("Hist_Fel", ""))

with t4:
    st.subheader("VII-IX. DESARROLLO")
    embarazo = st.text_input("Circunstancias Embarazo/Parto", value=datos_cargados.get("Parto", ""))
    hitos = st.text_input("Desarrollo Motor (Gateo/Caminar)", value=datos_cargados.get("Hitos", ""))
    escuela = st.text_area("Historia Escolar (Conducta/Rendimiento)", value=datos_cargados.get("Escuela", ""))

with t5:
    st.subheader("X-XII. INFORME Y RECOMENDACIONES")
    
    if st.button("🧠 GENERAR RECOMENDACIONES AUTOMÁTICAS"):
        r_auto, t_auto = generar_recomendaciones_auto(motivo, sintomas)
        st.session_state["recom_gen"] = r_auto
        st.session_state["tests_gen"] = "\n".join(t_auto)

    analisis = st.text_area("Análisis Clínico", value=datos_cargados.get("Analisis", ""))
    conclusiones = st.text_area("Conclusiones", value=datos_cargados.get("Conclusiones", ""))
    
    # Aquí se muestran las recomendaciones generadas
    recom_final = st.text_area("Recomendaciones Terapéuticas", value=st.session_state.get("recom_gen", datos_cargados.get("Recom", "")))
    tests_final = st.text_area("Tests Recomendados y Enlaces", value=st.session_state.get("tests_gen", datos_cargados.get("Tests", "")))
    
    psicologo = st.text_input("Psicólogo Evaluador", value=datos_cargados.get("Psicologo", ""))

with t6:
    st.subheader("📊 Base de Datos")
    st.dataframe(db_actual)
    if not db_actual.empty:
        buf_ex = io.BytesIO()
        db_actual.to_excel(buf_ex, index=False)
        st.download_button("📥 Descargar Excel Máster", buf_ex, "DSP_DATABASE.xlsx")

# --- 5. GUARDADO E IMPRESIÓN ---
if st.button("💾 GUARDAR Y GENERAR EXPEDIENTE COMPLETO"):
    if identidad and nombre:
        dict_final = {
            "Identidad": identidad, "Nombre": nombre, "F_Nac": f_nac, "Edad": edad, "Sexo": sexo,
            "Estado_Civil": est_civil, "Motivo": motivo, "Sueño": sue, "Apetito": ape, "Sed": sed,
            "Defec": defec_val, "Checklist": str(sintomas), "P_Rel": p_rel, "M_Rel": m_rel,
            "Hist_Fel": hist_fel, "Parto": embarazo, "Hitos": hitos, "Escuela": escuela,
            "Analisis": analisis, "Conclusiones": conclusiones, "Recom": recom_final,
            "Tests": tests_final, "Psicologo": psicologo, "Fecha": str(date.today())
        }
        guardar_db(dict_final)
        st.success(f"✅ Registro de {nombre} actualizado correctamente.")

        # GENERAR WORD
        doc = Document()
        doc.add_heading('EXPEDIENTE CLÍNICO COMPLETO - D.S.P.', 0)
        for clave, valor in dict_final.items():
            p = doc.add_paragraph()
            p.add_run(f"{clave}: ").bold = True
            p.add_run(str(valor))
        
        buf_w = io.BytesIO()
        doc.save(buf_w)
        buf_w.seek(0)
        st.download_button("📥 Descargar Protocolo y Recomendaciones (Word)", buf_w, f"Expediente_{identidad}.docx")
    else:
        st.error("Identidad y Nombre son obligatorios.")
