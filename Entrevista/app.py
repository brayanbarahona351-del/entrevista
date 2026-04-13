import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN DE PANTALLA ---
st.set_page_config(page_title="D.S.P. Honduras - Protocolo", layout="wide")

# --- 2. GESTIÓN DE BASE DE DATOS ---
DB_FILE = "DB_DSP_EXPEDIENTES.xlsx"

def cargar_db():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    try:
        df = pd.read_excel(DB_FILE)
        return df.astype(str).replace('nan', '')
    except:
        return pd.DataFrame()

def guardar_db(datos_dict):
    df = cargar_db()
    if not df.empty and "Identidad" in df.columns:
        df = df[df["Identidad"] != str(datos_dict["Identidad"])]
    df_final = pd.concat([df, pd.DataFrame([datos_dict])], ignore_index=True)
    df_final.to_excel(DB_FILE, index=False)
    return df_final

def v_idx(opcion, lista):
    try: return lista.index(opcion)
    except: return 0

# --- 3. MOTOR DE ANÁLISIS MEJORADO (CON VALIDACIÓN DE VACÍO) ---
def motor_ia_gemini(datos):
    # Consolidar texto de áreas críticas
    texto_clinico = f"{datos.get('Motivo', '')} {datos.get('Opinion', '')} {datos.get('Impulsos', '')}".lower().strip()
    check_list = datos.get('Check_Vida', [])

    # VALIDACIÓN: Si no hay texto suficiente, no dar diagnósticos al azar
    if len(texto_clinico) < 10 and not check_list:
        return ("SIN DATOS SUFICIENTES", 
                "Por favor, complete el motivo de consulta o la opinión profesional para generar un análisis.", 
                "N/A")

    # Lógica de detección
    if any(x in texto_clinico for x in ["suicid", "muerte", "matar", "quitarme la vida"]) or "Ideas Suicidas" in check_list:
        res = "ALERTA CRÍTICA: Riesgo Autolítico Detectado."
        rec = "Protocolo de vigilancia inmediata, remisión a psiquiatría y notificación a superiores."
        tests = "Beck (BDI-II), Escala de Desesperanza de Beck."
    
    elif any(x in texto_clinico for x in ["convulsiones", "desmayo", "memoria", "golpe"]):
        res = "INDICADOR: Posible compromiso orgánico/neurológico."
        rec = "Interconsulta obligatoria con Neurología antes de diagnóstico psicológico."
        tests = "Test Gestáltico Visomotor de Bender, Test de Retención Visual de Benton."
    
    elif any(x in texto_clinico for x in ["ira", "agresiv", "pelea", "arma", "golpeo"]) or "Tics" in check_list:
        res = "PERFIL: Indicadores de impulsividad y baja tolerancia a la frustración."
        rec = "Evaluación de control de impulsos y terapia cognitivo-conductual para manejo de ira."
        tests = "16PF-5 (Escala de Estabilidad), STAXI-2, IPV."
    
    else:
        res = "ESTADO: Evaluación preliminar sin indicadores de riesgo agudo."
        rec = "Continuar con entrevista clínica profunda y aplicación de batería básica."
        tests = "16PF-5, HTP (Casa-Árbol-Persona), SCL-90-R."
    
    return res, rec, tests

# --- 4. CARGA DE DATOS ---
db_actual = cargar_db()
with st.sidebar:
    st.header("📂 ARCHIVO D.S.P.")
    id_list = ["--- NUEVO ---"] + (db_actual["Identidad"].tolist() if not db_actual.empty else [])
    seleccion = st.selectbox("Buscar Identidad:", id_list)
    d = db_actual[db_actual["Identidad"] == seleccion].iloc[0].to_dict() if seleccion != "--- NUEVO ---" else {}

# Inicializar estados de la IA para evitar que se borren
if "ia_res" not in st.session_state: st.session_state["ia_res"] = d.get("Conclusiones", "Pendiente de análisis")
if "ia_rec" not in st.session_state: st.session_state["ia_rec"] = d.get("Recomendaciones", "Pendiente de análisis")
if "ia_test" not in st.session_state: st.session_state["ia_test"] = d.get("Tests", "Pendiente de análisis")

st.title("🛡️ Protocolo de Evaluación Psicológica - D.S.P.")

# --- 5. TABS DE EVALUACIÓN ---
tabs = st.tabs(["Identificación", "Salud Orgánica", "Historia Familiar", "Desarrollo/Sexo", "Análisis y Cierre"])

with tabs[0]:
    st.subheader("I. Datos Generales y Motivo")
    c1, c2 = st.columns(2)
    identidad = c1.text_input("Identidad (ID)", value=d.get("Identidad", ""))
    nombre = c2.text_input("Nombre Completo", value=d.get("Nombre", ""))
    motivo = st.text_area("II. MOTIVO DE CONSULTA (Palabras literales)", value=d.get("Motivo", ""))

with tabs[1]:
    st.subheader("III. Funciones y Salud")
    c3, c4 = st.columns(2)
    sueño = c3.selectbox("Sueño", ["Normal", "Insomnio", "Hipersomnia"], index=v_idx(d.get("Sueño"), ["Normal", "Insomnio", "Hipersomnia"]))
    apetito = c4.selectbox("Apetito", ["Normal", "Aumentado", "Disminuido"], index=v_idx(d.get("Apetito"), ["Normal", "Aumentado", "Disminuido"]))
    check_vida = st.multiselect("Checklist de Vida:", ["Ideas Suicidas", "Intentos Suicidas", "Alcohol", "Drogas", "Tics", "Alucinaciones"], default=eval(d.get("Check_Vida", "[]")) if d else [])

with tabs[2]:
    st.subheader("IV. Área Familiar")
    p_rel = st.text_area("Relación con el Padre / Castigos", value=d.get("P_Rel", ""))
    m_rel = st.text_area("Relación con la Madre / Castigos", value=d.get("M_Rel", ""))

with tabs[3]:
    st.subheader("V. Desarrollo y Personalidad")
    pers_imp = st.text_input("¿Actos impulsivos? (¿Se arrepiente?)", value=d.get("Pers_Imp", ""))
    sex_opi = st.text_area("Opinión sobre Sexualidad", value=d.get("Sex_Opi", ""))

with tabs[4]:
    st.subheader("VI. Opinión Profesional e IA")
    opinion_prof = st.text_area("Observaciones del Evaluador:", value=d.get("Opinion_Prof", ""))
    
    if st.button("🧠 EJECUTAR ANÁLISIS CLÍNICO IA"):
        datos_para_ia = {
            "Motivo": motivo,
            "Opinion": opinion_prof,
            "Check_Vida": check_vida,
            "Impulsos": pers_imp
        }
        res, rec, tst = motor_ia_gemini(datos_para_ia)
        st.session_state["ia_res"] = res
        st.session_state["ia_rec"] = rec
        st.session_state["ia_test"] = tst

    # Mostrar resultados (estén guardados o recién generados)
    st.info(f"**Resultado:** {st.session_state['ia_res']}")
    st.success(f"**Sugerencia:** {st.session_state['ia_rec']}")
    st.warning(f"**Batería:** {st.session_state['ia_test']}")

    psicologo = st.text_input("Firma: Psicólogo Evaluador", value=d.get("Psicologo", ""))

# --- 6. GUARDADO ---
if st.button("💾 GUARDAR EXPEDIENTE Y GENERAR WORD"):
    if identidad and nombre:
        reg = {
            "Identidad": identidad, "Nombre": nombre, "Motivo": motivo,
            "Sueño": sueño, "Apetito": apetito, "Check_Vida": str(check_vida),
            "P_Rel": p_rel, "M_Rel": m_rel, "Pers_Imp": pers_imp,
            "Sex_Opi": sex_opi, "Opinion_Prof": opinion_prof,
            "Conclusiones": st.session_state["ia_res"],
            "Recomendaciones": st.session_state["ia_rec"],
            "Tests": st.session_state["ia_test"],
            "Psicologo": psicologo, "Fecha": str(date.today())
        }
        guardar_db(reg)
        
        # Generar Documento
        doc = Document()
        doc.add_heading('INFORME PSICOLÓGICO - D.S.P.', 0)
        doc.add_paragraph(f"Paciente: {nombre} | ID: {identidad}")
        doc.add_heading('Análisis Preliminar', level=1)
        doc.add_paragraph(st.session_state["ia_res"])
        doc.add_heading('Recomendaciones', level=1)
        doc.add_paragraph(st.session_state["ia_rec"])
        
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        st.download_button("📥 DESCARGAR INFORME", buf, f"Informe_{identidad}.docx")
    else:
        st.error("Faltan datos obligatorios (Identidad y Nombre).")
