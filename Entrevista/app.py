import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN Y BASE DE DATOS ---
st.set_page_config(page_title="D.S.P. - Protocolo Clínico Integral", layout="wide")
DB_FILE = "DB_DSP_OFICIAL_HONDURAS.xlsx"

def cargar_db():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    try: return pd.read_excel(DB_FILE).astype(str).replace('nan', '')
    except: return pd.DataFrame()

def guardar_db(datos_dict):
    df = cargar_db()
    if not df.empty and "Identidad" in df.columns:
        # ELIMINA DUPLICADOS: Busca el ID y quita la versión vieja antes de guardar
        df = df[df["Identidad"] != str(datos_dict["Identidad"])]
    df_final = pd.concat([df, pd.DataFrame([datos_dict])], ignore_index=True)
    df_final.to_excel(DB_FILE, index=False)
    return df_final

# --- 2. MOTOR DE ANÁLISIS E IA (CONCLUSIONES Y RECOMENDACIONES) ---
def realizar_analisis_clinico_ia(motivo, sintomas):
    texto = (str(motivo) + str(sintomas)).lower()
    
    # Lógica de Conclusiones
    if any(x in texto for x in ["morir", "suicid", "muerte", "matar"]):
        concl = "Paciente presenta indicadores de riesgo autolítico. Estado emocional frágil con ideación recurrente."
        recom = "URGENTE: Remisión a Psiquiatría y vigilancia 24/7. Iniciar protocolo de prevención de suicidio."
        tests = "Tests: Beck (Depresión): https://bit.ly/test-beck | SCL-90-R: https://bit.ly/scl-90"
    elif any(x in texto for x in ["ira", "enojo", "golpe", "pelea", "arma"]):
        concl = "Se observan rasgos de impulsividad y dificultades en la gestión de la ira. Posible trastorno disocial o explosivo intermitente."
        recom = "Seguimiento: Terapia de control de impulsos. Evaluación de idoneidad para el uso de equipo reglamentario."
        tests = "Tests: MMPI-2 (Personalidad): https://bit.ly/mmpi-2-ref | IPV (Impulsividad): https://bit.ly/ipv-test"
    else:
        concl = "Sintomatología ansiosa leve. Rasgos adaptativos dentro de los parámetros esperados bajo estrés laboral."
        recom = "Seguimiento: Sesiones de descarga emocional mensuales y técnicas de higiene del sueño."
        tests = "Tests: 16PF-5: https://bit.ly/16pf5-ref | STAI (Ansiedad): https://bit.ly/stai-ref"
        
    return concl, recom, tests

# --- 3. INTERFAZ DE BÚSQUEDA ---
db_actual = cargar_db()
with st.sidebar:
    st.header("📂 ARCHIVO DE EXPEDIENTES")
    id_lista = ["--- REGISTRAR NUEVO ---"]
    if not db_actual.empty:
        id_lista += db_actual["Identidad"].tolist()
    
    seleccion = st.selectbox("Seleccionar por Identidad:", id_lista)
    datos_cargados = {}
    if seleccion != "--- REGISTRAR NUEVO ---":
        datos_cargados = db_actual[db_actual["Identidad"] == seleccion].iloc[0].to_dict()
        st.success(f"Cargado: {datos_cargados.get('Nombre')}")

st.title("🛡️ Protocolo Integral de Evaluación - D.S.P.")

# --- 4. CUESTIONARIO COMPLETO (SIN RECORTES) ---
tabs = st.tabs(["I-II. Identificación", "III-V. Orgánicas/Salud", "VI. Familia", "VII-IX. Desarrollo", "X-XI. Sexualidad", "XII. ANÁLISIS IA", "📊 Base de Datos"])

with tabs[0]:
    st.subheader("I. DATOS GENERALES")
    c1, c2, c3 = st.columns(3)
    identidad = c1.text_input("Número de Identidad", value=datos_cargados.get("Identidad", ""))
    nombre = c2.text_input("Nombre Completo", value=datos_cargados.get("Nombre", ""))
    f_nac = c3.text_input("Fecha y Lugar de Nacimiento", value=datos_cargados.get("F_Nac", ""))
    
    c4, c5, c6 = st.columns(3)
    edad = c4.text_input("Edad", value=datos_cargados.get("Edad", ""))
    sexo = c5.selectbox("Sexo", ["M", "F"], index=0 if datos_cargados.get("Sexo")=="M" else 1)
    est_civil = c6.text_input("Estado Civil", value=datos_cargados.get("Estado_Civil", ""))
    
    st.subheader("II. MOTIVO DE CONSULTA")
    motivo = st.text_area("Describa el motivo de su consulta según el paciente:", value=datos_cargados.get("Motivo", ""))

with tabs[1]:
    st.subheader("III. ANTECEDENTES Y IV. ORGÁNICAS")
    ant_sit = st.text_area("¿Cuándo comenzó la situación actual?", value=datos_cargados.get("Ant_Sit", ""))
    
    f1, f2, f3, f4 = st.columns(4)
    sue = f1.text_input("Sueño", value=datos_cargados.get("Sueño", ""))
    ape = f2.text_input("Apetito", value=datos_cargados.get("Apetito", ""))
    sed = f3.text_input("Sed", value=datos_cargados.get("Sed", ""))
    defec = f4.text_input("Defecación", value=datos_cargados.get("Defec", ""))
    
    st.subheader("V. ESTADO DE SALUD")
    hosp = st.text_input("Hospitalizaciones", value=datos_cargados.get("Hosp", ""))
    enf_inf = st.text_input("Enfermedades infancia", value=datos_cargados.get("Enf_Inf", ""))
    sint_neur = st.multiselect("Síntomas Neuroticos:", ["Ideas Suicidas", "Pesadillas", "Enuresis", "Ira", "Drogas", "Tics"], 
                               default=eval(datos_cargados.get("Checklist", "[]")) if datos_cargados else [])

with tabs[2]:
    st.subheader("VI. INFORMACIÓN FAMILIAR")
    p_nom = st.text_input("Nombre Padre", value=datos_cargados.get("P_Nom", ""))
    p_rel = st.text_area("Relación Padre y Castigos", value=datos_cargados.get("P_Rel", ""))
    m_nom = st.text_input("Nombre Madre", value=datos_cargados.get("M_Nom", ""))
    m_rel = st.text_area("Relación Madre y Castigos", value=datos_cargados.get("M_Rel", ""))
    hist_fel = st.text_area("Historia feliz en familia", value=datos_cargados.get("Hist_Fel", ""))

with tabs[3]:
    st.subheader("VII-IX. DESARROLLO")
    embarazo = st.text_input("Circunstancia Embarazo (¿Deseado?)", value=datos_cargados.get("Embarazo", ""))
    parto = st.text_input("Parto (Incubadora/Fórceps)", value=datos_cargados.get("Parto", ""))
    hitos = st.text_input("Desarrollo motor (Gateo/Caminar)", value=datos_cargados.get("Hitos", ""))
    esfinter = st.text_input("Control de esfínteres (Edad)", value=datos_cargados.get("Esfinter", ""))
    st.write("**Área Escolar**")
    esc_cond = st.text_area("Conducta y rendimiento escolar", value=datos_cargados.get("Esc_Cond", ""))

with tabs[4]:
    st.subheader("X-XI. SEXUALIDAD Y PERSONALIDAD")
    sex_men = st.text_input("Menarquia/Eyaculación (Edad)", value=datos_cargados.get("Sex_Men", ""))
    sex_opi = st.text_area("Opinión sobre sexualidad y matrimonio", value=datos_cargados.get("Sex_Opi", ""))
    pers_conf = st.text_input("¿Confía en las personas? (Celos/Rencor)", value=datos_cargados.get("Pers_Conf", ""))
    pers_imp = st.text_input("¿Actos impulsivos? (¿Se arrepiente?)", value=datos_cargados.get("Pers_Imp", ""))

with tabs[5]:
    st.subheader("XII. ANÁLISIS PROFESIONAL E IA")
    
    if st.button("🧠 PROCESAR ANÁLISIS Y RECOMENDACIONES"):
        c_ia, r_ia, t_ia = realizar_analisis_clinico_ia(motivo, sint_neur)
        st.session_state["ia_concl"] = c_ia
        st.session_state["ia_recom"] = r_ia
        st.session_state["ia_tests"] = t_ia

    analisis = st.text_area("Análisis Clínico Detallado", value=datos_cargados.get("Analisis", ""))
    
    # CAMPOS QUE RECIBEN LA INFO DE LA IA
    conclusiones_f = st.text_area("Conclusiones Clínicas", value=st.session_state.get("ia_concl", datos_cargados.get("Concl", "")))
    recom_f = st.text_area("Recomendaciones de Seguimiento", value=st.session_state.get("ia_recom", datos_cargados.get("Recom", "")))
    tests_f = st.text_area("Tests Recomendados y Enlaces", value=st.session_state.get("ia_tests", datos_cargados.get("Tests", "")))
    
    psicologo = st.text_input("Psicólogo Evaluador", value=datos_cargados.get("Psicologo", ""))

with tabs[6]:
    st.subheader("📊 Base de Datos General")
    st.dataframe(db_actual)

# --- 5. GUARDADO E IMPRESIÓN ---
if st.button("💾 GUARDAR Y GENERAR PROTOCOLO"):
    if identidad and nombre:
        registro = {
            "Identidad": identidad, "Nombre": nombre, "F_Nac": f_nac, "Edad": edad, "Sexo": sexo,
            "Estado_Civil": est_civil, "Motivo": motivo, "Ant_Sit": ant_sit, "Sueño": sue,
            "Apetito": ape, "Sed": sed, "Defec": defec, "Hosp": hosp, "Enf_Inf": enf_inf,
            "Checklist": str(sint_neur), "P_Nom": p_nom, "P_Rel": p_rel, "M_Nom": m_nom,
            "M_Rel": m_rel, "Hist_Fel": hist_fel, "Embarazo": embarazo, "Parto": parto,
            "Hitos": hitos, "Esfinter": esfinter, "Esc_Cond": esc_cond, "Sex_Men": sex_men,
            "Sex_Opi": sex_opi, "Pers_Conf": pers_conf, "Pers_Imp": pers_imp, "Analisis": analisis,
            "Concl": conclusiones_f, "Recom": recom_f, "Tests": tests_f, "Psicologo": psicologo
        }
        guardar_db(registro)
        st.success(f"Expediente {identidad} guardado. No hay duplicados.")

        # GENERACIÓN DEL WORD COMPLETO
        doc = Document()
        doc.add_heading('PROTOCOLO CLÍNICO DE EVALUACIÓN - D.S.P.', 0)
        for k, v in registro.items():
            p = doc.add_paragraph()
            p.add_run(f"{k}: ").bold = True
            p.add_run(str(v))
        
        buf_w = io.BytesIO(); doc.save(buf_w); buf_w.seek(0)
        st.download_button("📥 DESCARGAR PROTOCOLO COMPLETO", buf_w, f"Protocolo_{identidad}.docx")
    else:
        st.error("Identidad y Nombre son obligatorios.")
