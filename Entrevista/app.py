import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="D.S.P. Honduras - Protocolo Oficial v24", layout="wide")
DB_FILE = "DB_DSP_SISTEMA_MAESTRO.xlsx"

def cargar_db():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    try: return pd.read_excel(DB_FILE).astype(str).replace('nan', '')
    except: return pd.DataFrame()

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

# --- 2. MOTOR DE IA ACTUALIZADO ---
def motor_ia_dsp(motivo, sintomas_vida):
    texto = (str(motivo) + str(sintomas_vida)).lower()
    if any(x in texto for x in ["suicid", "morir", "matar", "solo", "vida"]):
        concl = "RIESGO AUTOLESIVO: Indicadores de ideación suicida y desesperanza clínica detectada."
        segui = "PLAN: Intervención en crisis inmediata, contrato de vida y remisión a psiquiatría hospitalaria."
        tests = "1. Beck (BDI-II): https://bit.ly/test-beck\n2. SCL-90-R: https://bit.ly/scl-90\n3. ADICIONAL: BHS (Desesperanza)\n4. ADICIONAL: Inventario de Riesgo Suicida."
    elif any(x in texto for x in ["ira", "agresiv", "arma", "pelea", "golpe"]):
        concl = "PERFIL CONDUCTUAL: Dificultad en control de impulsos y posible rasgo explosivo intermitente."
        segui = "PLAN: Terapia TCC para manejo de ira, entrenamiento en asertividad y revisión de idoneidad operativa."
        tests = "1. MMPI-2: https://bit.ly/mmpi-2-ref\n2. IPV: https://bit.ly/ipv-test\n3. ADICIONAL: STAXI-2 (Ira)\n4. ADICIONAL: Test de Zulliger."
    else:
        concl = "ESTADO: Ajuste emocional estable con presencia de estresores normativos."
        segui = "PLAN: Sesiones de descarga emocional y técnicas de respiración diafragmática."
        tests = "1. 16PF-5: https://bit.ly/16pf5-ref\n2. ADICIONAL: Test HTP\n3. ADICIONAL: Inventario de Ansiedad (BAI)."
    return concl, segui, tests

# --- 3. GESTIÓN DE EXPEDIENTES ---
db_actual = cargar_db()
with st.sidebar:
    st.header("📂 ARCHIVO CLÍNICO")
    id_list = ["--- NUEVO ---"] + (db_actual["Identidad"].tolist() if not db_actual.empty else [])
    seleccion = st.selectbox("Buscar por Identidad:", id_list)
    d = db_actual[db_actual["Identidad"] == seleccion].iloc[0].to_dict() if seleccion != "--- NUEVO ---" else {}

st.title("🛡️ Protocolo de Evaluación Psicológica D.S.P.")

# --- 4. LAS 12 ÁREAS (SIN RECORTES) ---
tabs = st.tabs(["I-II", "III-V", "VI. Checklist", "VII. FAMILIA EXTENDIDA", "VIII-IX", "X-XI", "XII. INFORME IA"])

with tabs[0]:
    st.subheader("I. IDENTIFICACIÓN Y II. MOTIVO")
    c1, c2, c3 = st.columns(3)
    identidad = c1.text_input("Identidad", value=d.get("Identidad", ""))
    nombre = c2.text_input("Nombre Completo", value=d.get("Nombre", ""))
    edad = c3.text_input("Edad", value=d.get("Edad", ""))
    motivo = st.text_area("Motivo de consulta literal:", value=d.get("Motivo", ""))

with tabs[1]:
    st.subheader("III-V. ORGÁNICAS Y SALUD")
    c4, c5, c6 = st.columns(3)
    s_l = ["Normal", "Insomnio", "Hipersomnia"]; sueño = c4.selectbox("Sueño", s_l, index=v_idx(d.get("Sueño"), s_l))
    cefaleas = c5.text_input("Cefaleas", value=d.get("Cefaleas", ""))
    convulsiones = c6.text_input("Convulsiones", value=d.get("Convulsiones", ""))
    hosp = st.text_input("Hospitalizaciones y Cirugías", value=d.get("Hosp", ""))

with tabs[2]:
    st.subheader("VI. ¿HA PRESENTADO ESTO EN SU VIDA?")
    v_list = ["Pesadillas", "Enuresis", "Tics", "Drogas", "Alcohol", "Ideas Suicidas", "Fobias", "Alucinaciones"]
    check_vida = st.multiselect("Marque con una X:", v_list, default=eval(d.get("Check_Vida", "[]")) if d else [])

with tabs[3]:
    st.subheader("VII. ÁREA FAMILIAR (DETALLADA)")
    col_p, col_m = st.columns(2)
    with col_p:
        st.write("**DATOS DEL PADRE**")
        p_nom = st.text_input("Nombre Padre", value=d.get("P_Nom", ""))
        p_edad = st.text_input("Edad Padre", value=d.get("P_Edad", ""))
        p_vive = st.selectbox("¿Vive?", ["Sí", "No"], index=v_idx(d.get("P_Vive"), ["Sí", "No"]))
        p_salud = st.text_input("Estado de Salud Padre", value=d.get("P_Salud", ""))
        p_ocupa = st.text_input("Ocupación Padre", value=d.get("P_Ocupa", ""))
        p_rel = st.text_area("Relación y Castigos (Padre)", value=d.get("P_Rel", ""))
    with col_m:
        st.write("**DATOS DE LA MADRE**")
        m_nom = st.text_input("Nombre Madre", value=d.get("M_Nom", ""))
        m_edad = st.text_input("Edad Madre", value=d.get("M_Edad", ""))
        m_vive = st.selectbox("¿Vive? ", ["Sí", "No"], index=v_idx(d.get("M_Vive"), ["Sí", "No"]))
        m_salud = st.text_input("Estado de Salud Madre", value=d.get("M_Salud", ""))
        m_ocupa = st.text_input("Ocupación Madre", value=d.get("M_Ocupa", ""))
        m_rel = st.text_area("Relación y Castigos (Madre)", value=d.get("M_Rel", ""))
    
    st.write("---")
    rel_padres = st.text_area("Relación entre los Padres (Dinámica de pareja)", value=d.get("Rel_Padres", ""))
    social = st.text_area("Área Social (Amigos, Vecinos, Ambiente)", value=d.get("Social", ""))

with tabs[4]:
    st.subheader("VIII-IX. DESARROLLO Y ESCUELA")
    gateo = st.text_input("Edad Gateó", value=d.get("Gateo", ""))
    camino = st.text_input("Edad Caminó", value=d.get("Camino", ""))
    esfinter = st.text_input("Edad Control Esfínteres", value=d.get("Esfinter", ""))
    esc_cond = st.text_area("Conducta y Rendimiento Escolar", value=d.get("Esc_Cond", ""))

with tabs[5]:
    st.subheader("X-XI. SEXUALIDAD Y PERSONALIDAD")
    menarquia = st.text_input("Menarquia/Eyaculación", value=d.get("Menarquia", ""))
    sex_opi = st.text_area("Opinión sobre Sexualidad/Matrimonio", value=d.get("Sex_Opi", ""))
    pers_imp = st.text_input("¿Actos impulsivos? (¿Arrepentimiento?)", value=d.get("Pers_Imp", ""))

with tabs[6]:
    st.subheader("XII. RESULTADOS DEL ANÁLISIS IA")
    if st.button("🧠 GENERAR INFORME CLÍNICO"):
        c_ia, r_ia, t_ia = motor_ia_dsp(motivo, check_vida)
        st.session_state["ia_concl"] = c_ia
        st.session_state["ia_recom"] = r_ia
        st.session_state["ia_tests"] = t_ia

    # Estos campos ahora capturan lo generado por la IA
    concl_f = st.text_area("Conclusiones", value=st.session_state.get("ia_concl", d.get("Conclusiones", "")))
    recom_f = st.text_area("Recomendaciones de Seguimiento", value=st.session_state.get("ia_recom", d.get("Recomendaciones", "")))
    tests_f = st.text_area("Tests Sugeridos y Enlaces", value=st.session_state.get("ia_tests", d.get("Tests", "")))
    psicologo = st.text_input("Psicólogo Evaluador", value=d.get("Psicologo", ""))

# --- 5. GUARDADO Y GENERACIÓN DE WORD ---
if st.button("💾 GUARDAR Y DESCARGAR INFORME COMPLETO"):
    if identidad and nombre:
        # CONSOLIDACIÓN DE DATOS
        reg = {
            "Identidad": identidad, "Nombre": nombre, "Edad": edad, "Motivo": motivo,
            "Sueño": sueño, "Cefaleas": cefaleas, "Convulsiones": convulsiones, "Hosp": hosp,
            "Check_Vida": str(check_vida), "P_Nom": p_nom, "P_Edad": p_edad, "P_Vive": p_vive,
            "P_Salud": p_salud, "P_Ocupa": p_ocupa, "P_Rel": p_rel, "M_Nom": m_nom,
            "M_Edad": m_edad, "M_Vive": m_vive, "M_Salud": m_salud, "M_Ocupa": m_ocupa,
            "M_Rel": m_rel, "Rel_Padres": rel_padres, "Social": social, "Gateo": gateo,
            "Camino": camino, "Esfinter": esfinter, "Esc_Cond": esc_cond, "Menarquia": menarquia,
            "Sex_Opi": sex_opi, "Pers_Imp": pers_imp, "Conclusiones": concl_f,
            "Recomendaciones": recom_f, "Tests": tests_f, "Psicologo": psicologo, "Fecha": str(date.today())
        }
        guardar_db(reg)
        
        # CREACIÓN DEL WORD INCLUYENDO RESULTADOS IA
        doc = Document()
        doc.add_heading('INFORME PSICOLÓGICO - D.S.P. HONDURAS', 0)
        
        doc.add_heading('1. DATOS GENERALES', level=1)
        doc.add_paragraph(f"Nombre: {nombre}\nID: {identidad}\nEvaluador: {psicologo}\nFecha: {date.today()}")
        
        doc.add_heading('2. RESULTADOS DEL ANÁLISIS E IA', level=1)
        doc.add_paragraph(f"CONCLUSIONES:\n{concl_f}")
        doc.add_paragraph(f"RECOMENDACIONES:\n{recom_f}")
        doc.add_paragraph(f"BATERÍA DE TESTS:\n{tests_f}")
        
        doc.add_heading('3. ANTECEDENTES DETALLADOS', level=1)
        for k, v in reg.items():
            if k not in ["Conclusiones", "Recomendaciones", "Tests"]: # Evitar duplicar
                doc.add_paragraph(f"{k}: {v}")
        
        buf = io.BytesIO(); doc.save(buf); buf.seek(0)
        st.success("✅ Informe generado con éxito.")
        st.download_button("📥 DESCARGAR INFORME (.DOCX)", buf, f"Informe_{identidad}.docx")
    else:
        st.error("Error: Debe completar Nombre e Identidad.")
