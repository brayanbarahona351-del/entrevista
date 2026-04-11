import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN Y BASE DE DATOS ---
st.set_page_config(page_title="D.S.P. - Protocolo Clínico Maestro", layout="wide")
DB_FILE = "DB_DSP_HONDURAS_FINAL.xlsx"

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

# --- FUNCIÓN DE SEGURIDAD PARA SELECTBOX ---
def validar_indice(opcion, lista):
    """Evita el TypeError si el dato de la DB no coincide con la lista"""
    try:
        return lista.index(opcion)
    except (ValueError, KeyError):
        return 0

# --- 2. MOTOR DE IA: RECOMENDACIONES EXPANDIDAS ---
def realizar_analisis_ia(motivo, sintomas):
    texto = (str(motivo) + str(sintomas)).lower()
    if any(x in texto for x in ["morir", "suicid", "muerte"]):
        concl = "RIESGO ALTO: Indicadores de ideación autolítica activa."
        recom = "Remisión a psiquiatría inmediata. Vigilancia 24/7. Psicoterapia semanal de apoyo."
        tests = "Tests sugeridos:\n1. Beck (BDI-II): https://bit.ly/test-beck\n2. SCL-90-R: https://bit.ly/scl-90\n3. Escala de Desesperanza de Beck (BHS).\n4. Test de Plutchik de Impulsividad."
    elif any(x in texto for x in ["ira", "arma", "pelea", "golpe"]):
        concl = "INDICADOR: Dificultad marcada en control de impulsos y gestión de agresividad."
        recom = "Entrenamiento en asertividad y manejo de ira. Evaluación de idoneidad operativa."
        tests = "Tests sugeridos:\n1. MMPI-2: https://bit.ly/mmpi-2-ref\n2. IPV: https://bit.ly/ipv-test\n3. Cuestionario de Ira STAXI-2.\n4. Test de Zulliger."
    else:
        concl = "ESTADO: Sintomatología leve/moderada sin riesgo agudo aparente."
        recom = "Seguimiento quincenal. Psicoeducación en higiene del sueño y manejo de estrés."
        tests = "Tests sugeridos:\n1. 16PF-5: https://bit.ly/16pf5-ref\n2. Test HTP (Casa-Árbol-Persona).\n3. Inventario de Ansiedad de Beck (BAI)."
    return concl, recom, tests

# --- 3. GESTIÓN DE BÚSQUEDA ---
db_actual = cargar_db()
with st.sidebar:
    st.header("🔍 ARCHIVO DE EXPEDIENTES")
    id_lista = ["--- REGISTRO NUEVO ---"] + (db_actual["Identidad"].tolist() if not db_actual.empty else [])
    seleccion = st.selectbox("Seleccionar Identidad:", id_lista)
    datos_c = db_actual[db_actual["Identidad"] == seleccion].iloc[0].to_dict() if seleccion != "--- REGISTRO NUEVO ---" else {}

st.title("🛡️ Protocolo Integral de Evaluación Psicológica - D.S.P.")

# --- 4. CUESTIONARIO COMPLETO (SIN RECORTES) ---
t1, t2, t3, t4, t5, t6, t7, t8 = st.tabs([
    "I. Identificación", "II. Motivo/Antecedentes", "III-IV. Orgánicas", 
    "V-VI. Salud/Sintomas", "VII. Familia", "VIII-IX. Desarrollo", 
    "X-XI. Sexo/Personalidad", "XII. ANÁLISIS E IA"
])

with t1:
    st.subheader("I. DATOS DE IDENTIFICACIÓN")
    c1, c2, c3 = st.columns(3)
    id_pac = c1.text_input("1. Número de Identidad", value=datos_c.get("Identidad", ""))
    nom_pac = c2.text_input("2. Nombre Completo", value=datos_c.get("Nombre", ""))
    f_nac = c3.text_input("3. Lugar y Fecha de Nacimiento", value=datos_c.get("F_Nac", ""))
    
    c4, c5, c6 = st.columns(3)
    edad = c4.text_input("4. Edad", value=datos_c.get("Edad", ""))
    sexo_lista = ["M", "F"]
    sexo = c5.selectbox("5. Sexo", sexo_lista, index=validar_indice(datos_c.get("Sexo"), sexo_lista))
    ec_lista = ["Soltero", "Casado", "Divorciado", "Unión Libre", "Viudo"]
    est_civil = c6.selectbox("6. Estado Civil", ec_lista, index=validar_indice(datos_c.get("Estado_Civil"), ec_lista))

with t2:
    st.subheader("II. MOTIVO Y ANTECEDENTES")
    motivo = st.text_area("10. Motivo de Consulta (Vaciado literal)", value=datos_c.get("Motivo", ""))
    ant_sit = st.text_area("11. Antecedentes de la situación actual", value=datos_c.get("Ant_Sit", ""))

with t3:
    st.subheader("III-IV. FUNCIONES ORGÁNICAS")
    c10, c11, c12, c13 = st.columns(4)
    s_lista = ["Normal", "Insomnio", "Hipersomnia", "Interrumpido"]
    sueño = c10.selectbox("12. Sueño", s_lista, index=validar_indice(datos_c.get("Sueño"), s_lista))
    a_lista = ["Normal", "Aumentado", "Disminuido"]
    apetito = c11.selectbox("13. Apetito", a_lista, index=validar_indice(datos_c.get("Apetito"), a_lista))
    sed = c12.text_input("14. Sed", value=datos_c.get("Sed", ""))
    defec = c13.text_input("15. Defecación", value=datos_c.get("Defec", ""))

with t4:
    st.subheader("V-VI. SALUD Y SÍNTOMAS")
    alergias = st.text_input("16. Alergias", value=datos_c.get("Alergias", ""))
    meds = st.text_input("17. Medicamentos actuales", value=datos_c.get("Meds", ""))
    hosp = st.text_input("18. Hospitalizaciones", value=datos_c.get("Hosp", ""))
    st.write("**20. Síntomas Neuroticos**")
    s_list = ["Pesadillas", "Terror Nocturno", "Enuresis", "Tics", "Fobias", "Drogas", "Ideas Suicidas"]
    sintomas = st.multiselect("Marque presentes:", s_list, default=eval(datos_c.get("Sintomas", "[]")) if datos_c else [])

with t5:
    st.subheader("VII. ÁREA FAMILIAR")
    p_rel = st.text_area("22. Relación con el padre y castigos", value=datos_c.get("P_Rel", ""))
    m_rel = st.text_area("24. Relación con la madre y castigos", value=datos_c.get("M_Rel", ""))
    hist_fel = st.text_area("27. Historia feliz en familia", value=datos_c.get("Hist_Fel", ""))

with t6:
    st.subheader("VIII-IX. DESARROLLO")
    c14, c15, c16 = st.columns(3)
    gateo = c14.text_input("30. Edad gateó", value=datos_c.get("Gateo", ""))
    camino = c15.text_input("31. Edad caminó", value=datos_c.get("Camino", ""))
    esfinter = c16.text_input("33. Edad esfínteres", value=datos_c.get("Esfinter", ""))
    esc_cond = st.text_area("37. Conducta escolar", value=datos_c.get("Esc_Cond", ""))

with t7:
    st.subheader("X-XI. SEXUALIDAD Y PERSONALIDAD")
    menarquia = st.text_input("38. Menarquia/Eyaculación", value=datos_c.get("Menarquia", ""))
    sex_opi = st.text_area("39. Opinión sexualidad", value=datos_c.get("Sex_Opi", ""))
    pers_imp = st.text_input("43. Actos impulsivos", value=datos_c.get("Pers_Imp", ""))

with t8:
    st.subheader("XII. ANÁLISIS E IA")
    if st.button("🧠 GENERAR ANÁLISIS E INFORME"):
        c_ia, r_ia, t_ia = realizar_analisis_ia(motivo, sintomas)
        st.session_state["ia_concl"] = c_ia
        st.session_state["ia_recom"] = r_ia
        st.session_state["ia_tests"] = t_ia

    concl_f = st.text_area("Conclusiones", value=st.session_state.get("ia_concl", datos_c.get("Concl", "")))
    recom_f = st.text_area("Recomendaciones y Seguimiento", value=st.session_state.get("ia_recom", datos_c.get("Recom", "")))
    tests_f = st.text_area("Tests y Enlaces (Base + Otros)", value=st.session_state.get("ia_tests", datos_c.get("Tests", "")))
    psicologo = st.text_input("Psicólogo Evaluador", value=datos_c.get("Psicologo", ""))

# --- 5. GUARDADO ---
if st.button("💾 GUARDAR Y GENERAR WORD"):
    if id_pac and nom_pac:
        reg = {
            "Identidad": id_pac, "Nombre": nom_pac, "F_Nac": f_nac, "Edad": edad, "Sexo": sexo,
            "Estado_Civil": est_civil, "Motivo": motivo, "Ant_Sit": ant_sit, "Sueño": sueño,
            "Apetito": apetito, "Sed": sed, "Defec": defec, "Alergias": alergias, "Meds": meds,
            "Hosp": hosp, "Sintomas": str(sintomas), "P_Rel": p_rel, "M_Rel": m_rel,
            "Hist_Fel": hist_fel, "Gateo": gateo, "Camino": camino, "Esfinter": esfinter,
            "Esc_Cond": esc_cond, "Menarquia": menarquia, "Sex_Opi": sex_opi, "Pers_Imp": pers_imp,
            "Concl": concl_f, "Recom": recom_f, "Tests": tests_f, "Psicologo": psicologo
        }
        guardar_db(reg)
        st.success("✅ Guardado exitoso.")
        
        doc = Document()
        doc.add_heading('PROTOCOLO CLÍNICO D.S.P.', 0)
        for k, v in reg.items():
            p = doc.add_paragraph()
            p.add_run(f"{k}: ").bold = True
            p.add_run(str(v))
        
        buf = io.BytesIO(); doc.save(buf); buf.seek(0)
        st.download_button("📥 DESCARGAR WORD", buf, f"Expediente_{id_pac}.docx")
