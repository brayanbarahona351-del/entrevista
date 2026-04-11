import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN Y BASE DE DATOS ---
st.set_page_config(page_title="D.S.P. Honduras - Protocolo Oficial v25", layout="wide")
DB_FILE = "DB_DSP_MAESTRO_HONDURAS.xlsx"

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

# --- 2. MOTOR DE ANÁLISIS IA ---
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

# --- 3. BÚSQUEDA ---
db_actual = cargar_db()
with st.sidebar:
    st.header("📂 ARCHIVO D.S.P.")
    id_list = ["--- NUEVO REGISTRO ---"] + (db_actual["Identidad"].tolist() if not db_actual.empty else [])
    seleccion = st.selectbox("Identidad del Paciente:", id_list)
    d = db_actual[db_actual["Identidad"] == seleccion].iloc[0].to_dict() if seleccion != "--- NUEVO REGISTRO ---" else {}

st.title("🛡️ Protocolo de Entrevista Clínica Exhaustiva - D.S.P.")

# --- 4. LAS 12 ÁREAS DEL PROTOCOLO (TOTALMENTE DESPLEGADAS) ---
tabs = st.tabs([
    "I-II. Identificación", "III-V. Salud Médica", "VI. Checklist Vida", 
    "VII. Familiares", "VIII-IX. Desarrollo", "X-XI. Sexo/Pers.", "XII. RESULTADOS IA"
])

with tabs[0]:
    st.subheader("I. IDENTIFICACIÓN Y II. MOTIVO")
    c1, c2, c3 = st.columns(3)
    id_pac = c1.text_input("Número de Identidad", value=d.get("Identidad", ""))
    nom_pac = c2.text_input("Nombre Completo", value=d.get("Nombre", ""))
    f_nac = c3.text_input("Fecha/Lugar de Nacimiento", value=d.get("F_Nac", ""))
    
    c4, c5, c6 = st.columns(3)
    edad = c4.text_input("Edad Actual", value=d.get("Edad", ""))
    s_l = ["M", "F"]; sexo = c5.selectbox("Sexo", s_l, index=v_idx(d.get("Sexo"), s_l))
    ec_l = ["Soltero", "Casado", "Divorciado", "Unión Libre", "Viudo"]; est_civil = c6.selectbox("Estado Civil", ec_l, index=v_idx(d.get("Estado_Civil"), ec_l))
    
    nacionalidad = st.text_input("Nacionalidad", value=d.get("Nacionalidad", ""))
    ocupacion = st.text_input("Ocupación/Grado", value=d.get("Ocupacion", ""))
    asignacion = st.text_input("Asignación o Unidad", value=d.get("Asignacion", ""))
    remitido = st.text_input("Remitido por:", value=d.get("Remitido", ""))
    
    motivo = st.text_area("II. MOTIVO DE CONSULTA (Vaciado literal del paciente)", value=d.get("Motivo", ""))

with tabs[1]:
    st.subheader("III-IV. FUNCIONES ORGÁNICAS Y ANTECEDENTES")
    ant_sit = st.text_area("¿Cuándo comenzó la situación actual?", value=d.get("Ant_Sit", ""))
    
    c7, c8, c9, c10 = st.columns(4)
    su_l = ["Normal", "Insomnio", "Hipersomnia", "Interrumpido"]; sueño = c7.selectbox("Sueño", su_l, index=v_idx(d.get("Sueño", "Normal"), su_l))
    ap_l = ["Normal", "Aumentado", "Disminuido"]; apetito = c8.selectbox("Apetito", ap_l, index=v_idx(d.get("Apetito", "Normal"), ap_l))
    sed = c9.text_input("Sed", value=d.get("Sed", ""))
    defec = c10.text_input("Defecación", value=d.get("Defec", ""))
    
    st.subheader("V. ESTADO DE SALUD MÉDICA")
    c11, c12, c13, c14 = st.columns(4)
    convulsiones = c11.text_input("Convulsiones", value=d.get("Convulsiones", ""))
    cefaleas = c12.text_input("Cefaleas", value=d.get("Cefaleas", ""))
    resp = c13.text_input("Enf. Respiratorias", value=d.get("Resp", ""))
    infec = c14.text_input("Infecciones", value=d.get("Infecciones", ""))
    
    c15, c16 = st.columns(2)
    alergias = c15.text_input("Alergias", value=d.get("Alergias", ""))
    meds = c16.text_input("Medicamentos Actuales", value=d.get("Meds", ""))
    
    hosp = st.text_input("Hospitalizaciones (Motivo y Tiempo)", value=d.get("Hosp", ""))
    cirugias = st.text_input("Cirugías (Tipo y Fecha)", value=d.get("Cirugias", ""))

with tabs[2]:
    st.subheader("VI. CHECKLIST: MARQUE CON UNA X SI HA PRESENTADO EN SU VIDA:")
    items_vida = [
        "Pesadillas", "Terror Nocturno", "Sonambulismo", "Enuresis", "Encopresis", 
        "Onicofagia", "Tics", "Fobias", "Drogas", "Alcohol", "Ideas Suicidas", 
        "Intentos Suicidas", "Alucinaciones", "Pérdida de Memoria", "Mareos"
    ]
    check_vida = st.multiselect("Marque los síntomas presentados:", items_vida, 
                                 default=eval(d.get("Check_Vida", "[]")) if d else [])

with tabs[3]:
    st.subheader("VII. ÁREA FAMILIAR Y SOCIAL")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**DATOS DEL PADRE**")
        p_nom = st.text_input("Nombre del Padre", value=d.get("P_Nom", ""))
        p_edad = st.text_input("Edad del Padre", value=d.get("P_Edad", ""))
        p_vive = st.selectbox("¿Vive? (Padre)", ["Sí", "No"], index=v_idx(d.get("P_Vive"), ["Sí", "No"]))
        p_salud = st.text_input("Salud del Padre", value=d.get("P_Salud", ""))
        p_ocupa = st.text_input("Ocupación del Padre", value=d.get("P_Ocupa", ""))
        p_rel = st.text_area("Relación y Castigos (Padre)", value=d.get("P_Rel", ""))
    with col2:
        st.write("**DATOS DE LA MADRE**")
        m_nom = st.text_input("Nombre de la Madre", value=d.get("M_Nom", ""))
        m_edad = st.text_input("Edad de la Madre", value=d.get("M_Edad", ""))
        m_vive = st.selectbox("¿Vive? (Madre)", ["Sí", "No"], index=v_idx(d.get("M_Vive"), ["Sí", "No"]))
        m_salud = st.text_input("Salud de la Madre", value=d.get("M_Salud", ""))
        m_ocupa = st.text_input("Ocupación de la Madre", value=d.get("M_Ocupa", ""))
        m_rel = st.text_area("Relación y Castigos (Madre)", value=d.get("M_Rel", ""))
    
    st.write("---")
    rel_padres = st.text_area("¿Cómo era la relación entre su Padre y su Madre?", value=d.get("Rel_Padres", ""))
    hermanos = st.text_input("Número de hermanos y lugar que ocupa", value=d.get("Hermanos", ""))
    crianza = st.text_input("¿Quién lo crió?", value=d.get("Crianza", ""))
    hist_fel = st.text_area("Historia feliz vivida en familia", value=d.get("Hist_Fel", ""))
    social = st.text_area("Relación social (Amigos, vecinos, entorno)", value=d.get("Social", ""))

with tabs[4]:
    st.subheader("VIII-IX. DESARROLLO Y EDUCACIÓN")
    embarazo = st.text_input("Circunstancia Embarazo (Deseado/Reacción)", value=d.get("Embarazo", ""))
    parto = st.text_input("Parto (Fórceps, incubadora, tiempo)", value=d.get("Parto", ""))
    
    c17, c18, c19, c20 = st.columns(4)
    gateo = c17.text_input("Edad Gateó", value=d.get("Gateo", ""))
    camino = c18.text_input("Edad Caminó", value=d.get("Camino", ""))
    hablo = c19.text_input("Edad Habló", value=d.get("Hablo", ""))
    esfinter = c20.text_input("Edad Esfínteres", value=d.get("Esfinter", ""))
    
    st.write("**Área Escolar**")
    esc_edad = st.text_input("Edad inicio escuela", value=d.get("Esc_Edad", ""))
    esc_dif = st.text_input("Materias dificultad", value=d.get("Esc_Dif", ""))
    esc_cond = st.text_area("Conducta y rendimiento escolar", value=d.get("Esc_Cond", ""))

with tabs[5]:
    st.subheader("X-XI. SEXUALIDAD Y PERSONALIDAD")
    menarquia = st.text_input("Menarquia / Primera Eyaculación", value=d.get("Menarquia", ""))
    sex_opi = st.text_area("Opinión Sexualidad, Matrimonio y Masturbación", value=d.get("Sex_Opi", ""))
    sex_rel = st.text_input("Edad primera relación sexual", value=d.get("Sex_Rel", ""))
    noviazgo = st.text_input("Edad primer noviazgo", value=d.get("Noviazgo", ""))
    
    pers_conf = st.text_input("¿Confía en las personas? (Celos, rencor)", value=d.get("Pers_Conf", ""))
    pers_imp = st.text_input("¿Actos impulsivos? (¿Se arrepiente?)", value=d.get("Pers_Imp", ""))

with tabs[6]:
    st.subheader("XII. ANÁLISIS, CONCLUSIONES Y RECOMENDACIONES")
    if st.button("🧠 GENERAR ANÁLISIS E INFORME IA"):
        c_ia, r_ia, t_ia = motor_ia_dsp(motivo, check_vida)
        st.session_state["ia_concl"] = c_ia
        st.session_state["ia_recom"] = r_ia
        st.session_state["ia_tests"] = t_ia

    analisis_prof = st.text_area("Análisis Clínico Profesional", value=d.get("Analisis", ""))
    concl_f = st.text_area("Conclusiones Clínicas", value=st.session_state.get("ia_concl", d.get("Conclusiones", "")))
    recom_f = st.text_area("Recomendaciones de Seguimiento", value=st.session_state.get("ia_recom", d.get("Recomendaciones", "")))
    tests_f = st.text_area("Batería de Tests y Enlaces Sugeridos", value=st.session_state.get("ia_tests", d.get("Tests", "")))
    psicologo = st.text_input("Psicólogo Evaluador", value=d.get("Psicologo", ""))

# --- 5. GUARDADO Y WORD ---
if st.button("💾 GUARDAR Y GENERAR DOCUMENTO WORD"):
    if id_pac and nom_pac:
        reg = {
            "Identidad": id_pac, "Nombre": nom_pac, "F_Nac": f_nac, "Edad": edad, "Sexo": sexo,
            "Estado_Civil": est_civil, "Nacionalidad": nacionalidad, "Ocupacion": ocupacion,
            "Asignacion": asignacion, "Remitido": remitido, "Motivo": motivo, "Ant_Sit": ant_sit,
            "Sueño": sueño, "Apetito": apetito, "Sed": sed, "Defec": defec, "Convulsiones": convulsiones,
            "Cefaleas": cefaleas, "Resp": resp, "Infecciones": infec, "Alergias": alergias,
            "Meds": meds, "Hosp": hosp, "Cirugias": cirugias, "Check_Vida": str(check_vida),
            "P_Nom": p_nom, "P_Edad": p_edad, "P_Vive": p_vive, "P_Salud": p_salud, "P_Ocupa": p_ocupa,
            "P_Rel": p_rel, "M_Nom": m_nom, "M_Edad": m_edad, "M_Vive": m_vive, "M_Salud": m_salud,
            "M_Ocupa": m_ocupa, "M_Rel": m_rel, "Rel_Padres": rel_padres, "Hermanos": hermanos,
            "Crianza": crianza, "Hist_Fel": hist_fel, "Social": social, "Embarazo": embarazo,
            "Parto": parto, "Gateo": gateo, "Camino": camino, "Hablo": hablo, "Esfinter": esfinter,
            "Esc_Edad": esc_edad, "Esc_Dif": esc_dif, "Esc_Cond": esc_cond, "Menarquia": menarquia,
            "Sex_Opi": sex_opi, "Sex_Rel": sex_rel, "Noviazgo": noviazgo, "Pers_Conf": pers_conf,
            "Pers_Imp": pers_imp, "Analisis": analisis_prof, "Conclusiones": concl_f,
            "Recomendaciones": recom_f, "Tests": tests_f, "Psicologo": psicologo, "Fecha": str(date.today())
        }
        guardar_db(reg)
        
        doc = Document()
        doc.add_heading('PROTOCOLO CLÍNICO D.S.P. - HONDURAS', 0)
        
        # Primero Resultados IA
        doc.add_heading('I. CONCLUSIONES Y RECOMENDACIONES (IA)', level=1)
        doc.add_paragraph(f"CONCLUSIONES: {concl_f}")
        doc
