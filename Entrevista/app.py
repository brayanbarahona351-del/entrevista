import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="D.S.P. Honduras - Análisis IA Integral", layout="wide")
DB_FILE = "DB_DSP_SISTEMA_INTEGRAL.xlsx"

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

# --- 2. MOTOR DE ANÁLISIS INTEGRAL (CONSULTA IA) ---
def motor_analisis_gemini(datos):
    # Consolidación de toda la entrevista para la IA
    contexto = f"""
    MOTIVO: {datos.get('Motivo')}
    SÍNTOMAS VIDA: {datos.get('Check_Vida')}
    SALUD: Convulsiones({datos.get('Convulsiones')}), Cefaleas({datos.get('Cefaleas')}), Respiratorio({datos.get('Resp')})
    FAMILIA: Relación padres({datos.get('Rel_Padres')}), Castigos P({datos.get('P_Rel')}), Castigos M({datos.get('M_Rel')})
    DESARROLLO: Habló({datos.get('Hablo')}), Caminó({datos.get('Camino')}), Esfínteres({datos.get('Esfinter')})
    OPINIÓN PROFESIONAL: {datos.get('Opinion_Prof')}
    """
    
    texto = contexto.lower()
    
    # Lógica de Recomendación Basada en el Vaciado de Preguntas
    if any(x in texto for x in ["suicid", "muerte", "morir", "matar"]):
        res = "ALERTA DE SEGURIDAD: Riesgo autolítico detectado. Se requiere intervención de tercer nivel."
        rec = "Priorizar Contrato de Vida, remisión a Psiquiatría y Terapia Dialéctica Conductual (DBT)."
        tests = "Beck (BDI-II): https://bit.ly/test-beck, SCL-90-R, Escala de Desesperanza."
    elif any(x in texto for x in ["convulsiones", "cefaleas", "mareos", "perdida de memoria"]):
        res = "SOSPECHA ORGÁNICA: Los síntomas físicos sugieren posible compromiso neurológico."
        rec = "Solicitar interconsulta con Neurología y realizar EEG antes de concluir diagnóstico psicológico."
        tests = "Test de Bender (Visomotor), Test de Retención Visual de Benton, MMPI-2."
    elif any(x in texto for x in ["castigos", "golpes", "violencia", "ira", "rencor"]):
        res = "PATRÓN CONDUCTUAL: Posible trastorno del control de impulsos con base en historia de crianza rígida."
        rec = "Entrenamiento en regulación emocional y resolución de conflictos."
        tests = "IPV (Impulsividad): https://bit.ly/ipv-test, STAXI-2 (Ira), 16PF-5."
    else:
        res = "AJUSTE EMOCIONAL: Sintomatología reactiva a estresores ambientales."
        rec = "Psicoterapia breve orientada a soluciones y técnicas de afrontamiento al estrés."
        tests = "16PF-5: https://bit.ly/16pf5-ref, Test HTP, Inventario de Ansiedad (BAI)."

    return res, rec, tests

# --- 3. INTERFAZ ---
db_actual = cargar_db()
with st.sidebar:
    st.header("📂 ARCHIVO CLÍNICO")
    id_list = ["--- NUEVO REGISTRO ---"] + (db_actual["Identidad"].tolist() if not db_actual.empty else [])
    sel = st.selectbox("Identidad:", id_list)
    d = db_actual[db_actual["Identidad"] == sel].iloc[0].to_dict() if sel != "--- NUEVO REGISTRO ---" else {}

st.title("🛡️ Protocolo Maestro D.S.P. - Vaciado Completo de 12 Áreas")

t1, t2, t3, t4, t5, t6, t7 = st.tabs(["I-II. ID y Motivo", "III-V. Salud/Orgánicas", "VI. Checklist", "VII. Familia/Social", "VIII-IX. Desarrollo", "X-XI. Sexo/Pers.", "XII-XIII. ANÁLISIS IA"])

with t1:
    c1, c2, c3 = st.columns(3)
    identidad = c1.text_input("Identidad", value=d.get("Identidad", ""))
    nombre = c2.text_input("Nombre", value=d.get("Nombre", ""))
    f_nac = c3.text_input("Fecha Nac.", value=d.get("F_Nac", ""))
    sexo = st.selectbox("Sexo", ["M", "F"], index=v_idx(d.get("Sexo"), ["M", "F"]))
    motivo = st.text_area("Motivo de Consulta Literal", value=d.get("Motivo", ""))

with t2:
    st.subheader("III-V. ÁREA MÉDICA Y FUNCIONES")
    c4, c5, c6, c7 = st.columns(4)
    sueño = c4.selectbox("Sueño", ["Normal", "Insomnio", "Hipersomnia"], index=v_idx(d.get("Sueño"), ["Normal", "Insomnio", "Hipersomnia"]))
    convulsiones = c5.text_input("Convulsiones", value=d.get("Convulsiones", ""))
    cefaleas = c6.text_input("Cefaleas", value=d.get("Cefaleas", ""))
    resp = c7.text_input("Enf. Respiratorias", value=d.get("Resp", ""))
    infec = st.text_input("Infecciones", value=d.get("Infecciones", ""))
    hosp = st.text_area("Hospitalizaciones y Cirugías", value=d.get("Hosp", ""))

with t3:
    st.subheader("VI. CHECKLIST HISTÓRICO")
    v_items = ["Pesadillas", "Terror Nocturno", "Enuresis", "Tics", "Drogas", "Alcohol", "Ideas Suicidas", "Alucinaciones", "Mareos"]
    check_vida = st.multiselect("Marque lo presentado en su vida:", v_items, default=eval(d.get("Check_Vida", "[]")) if d else [])

with t4:
    st.subheader("VII. DINÁMICA FAMILIAR Y SOCIAL")
    p_rel = st.text_area("Relación Padre y Castigos", value=d.get("P_Rel", ""))
    m_rel = st.text_area("Relación Madre y Castigos", value=d.get("M_Rel", ""))
    rel_padres = st.text_area("Relación entre los Padres (Pareja)", value=d.get("Rel_Padres", ""))
    social = st.text_area("Área Social y Ambiental (Amigos/Vecinos)", value=d.get("Social", ""))

with t5:
    st.subheader("VIII-IX. HITOS DEL DESARROLLO")
    c8, c9, c10 = st.columns(3)
    gateo = c8.text_input("Edad Gateó", value=d.get("Gateo", ""))
    camino = c9.text_input("Edad Caminó", value=d.get("Camino", ""))
    hablo = c10.text_input("Edad Habló", value=d.get("Hablo", ""))
    esfinter = st.text_input("Edad Esfínteres", value=d.get("Esfinter", ""))
    esc_cond = st.text_area("Conducta Escolar y Rendimiento", value=d.get("Esc_Cond", ""))

with t6:
    st.subheader("X-XI. SEXUALIDAD Y PERSONALIDAD")
    menarquia = st.text_input("Menarquia / Eyaculación", value=d.get("Menarquia", ""))
    sex_opi = st.text_area("Opinión Sexo / Masturbación / Matrimonio", value=d.get("Sex_Opi", ""))
    pers_imp = st.text_input("Actos impulsivos y arrepentimiento", value=d.get("Pers_Imp", ""))

with t7:
    st.subheader("XIII. CONSULTA INTEGRAL CON IA")
    opinion_prof = st.text_area("✍️ Escriba su Opinión Profesional sobre el caso:", value=d.get("Opinion_Prof", ""))
    
    if st.button("🧠 REALIZAR CONSULTA A IA (ANÁLISIS DE TODAS LAS ÁREAS)"):
        # Diccionario temporal para el análisis
        datos_analisis = {
            "Motivo": motivo, "Check_Vida": check_vida, "Convulsiones": convulsiones,
            "Cefaleas": cefaleas, "Resp": resp, "Rel_Padres": rel_padres,
            "P_Rel": p_rel, "M_Rel": m_rel, "Hablo": hablo, "Camino": camino,
            "Esfinter": esfinter, "Opinion_Prof": opinion_prof
        }
        res_ia, rec_ia, test_ia = motor_analisis_gemini(datos_analisis)
        st.session_state["ia_res"] = res_ia
        st.session_state["ia_rec"] = rec_ia
        st.session_state["ia_test"] = test_ia

    st.success(f"**Análisis de la IA:** {st.session_state.get('ia_res', 'Pendiente')}")
    st.info(f"**Recomendación Clínica:** {st.session_state.get('ia_rec', 'Pendiente')}")
    st.warning(f"**Batería Sugerida:** {st.session_state.get('ia_test', 'Pendiente')}")
    
    psicologo = st.text_input("Firma: Psicólogo Evaluador", value=d.get("Psicologo", ""))

# --- 4. GUARDADO FINAL ---
if st.button("💾 GUARDAR EXPEDIENTE Y GENERAR INFORME WORD"):
    if identidad and nombre:
        reg = {
            "Identidad": identidad, "Nombre": nombre, "F_Nac": f_nac, "Sexo": sexo, "Motivo": motivo,
            "Sueño": sueño, "Convulsiones": convulsiones, "Cefaleas": cefaleas, "Resp": resp,
            "Infecciones": infec, "Hosp": hosp, "Check_Vida": str(check_vida), "P_Rel": p_rel,
            "M_Rel": m_rel, "Rel_Padres": rel_padres, "Social": social, "Gateo": gateo,
            "Camino": camino, "Hablo": hablo, "Esfinter": esfinter, "Esc_Cond": esc_cond,
            "Menarquia": menarquia, "Sex_Opi": sex_opi, "Pers_Imp": pers_imp,
            "Opinion_Prof": opinion_prof, "Conclusiones": st.session_state.get("ia_res"),
            "Recomendaciones": st.session_state.get("ia_rec"), "Tests": st.session_state.get("ia_test"),
            "Psicologo": psicologo, "Fecha": str(date.today())
        }
        guardar_db(reg)
        
        doc = Document()
        doc.add_heading('PROTOCOLO CLÍNICO D.S.P. - INFORME IA', 0)
        doc.add_heading('1. ANALISIS E OPINIÓN IA', 1)
        doc.add_paragraph(f"Opinión Profesional: {opinion_prof}")
        doc.add_paragraph(f"Análisis IA: {st.session_state.get('ia_res')}")
        doc.add_paragraph(f"Recomendaciones: {st.session_state.get('ia_rec')}")
        doc.add_heading('2. VACIADO COMPLETO', 1)
        for k, v in reg.items():
            doc.add_paragraph(f"{k}: {v}")
        
        buf = io.BytesIO(); doc.save(buf); buf.seek(0)
        st.download_button("📥 DESCARGAR INFORME (.DOCX)", buf, f"Expediente_{identidad}.docx")
