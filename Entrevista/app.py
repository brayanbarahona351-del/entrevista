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

# --- 2. MOTOR DE IA: RECOMENDACIONES EXPANDIDAS ---
def realizar_analisis_ia(motivo, sintomas):
    texto = (str(motivo) + str(sintomas)).lower()
    if any(x in texto for x in ["morir", "suicid", "muerte"]):
        concl = "RIESGO ALTO: Ideación autolítica activa."
        recom = "Remitir a psiquiatría. Vigilancia 24/7. Terapia semanal."
        tests = "Tests sugeridos:\n1. Beck (BDI-II): https://bit.ly/test-beck\n2. SCL-90-R: https://bit.ly/scl-90\n3. Escala de Desesperanza de Beck (BHS).\n4. Inventario de Depresión de Zung."
    elif any(x in texto for x in ["ira", "arma", "pelea"]):
        concl = "INDICADOR: Dificultad marcada en control de impulsos."
        recom = "Entrenamiento en asertividad. Terapia cognitivo-conductual."
        tests = "Tests sugeridos:\n1. MMPI-2: https://bit.ly/mmpi-2-ref\n2. IPV: https://bit.ly/ipv-test\n3. Cuestionario STAXI-2 (Ira).\n4. Test Proyectivo de la Figura Humana (Karen Machover)."
    else:
        concl = "ESTADO: Estable con sintomatología leve."
        recom = "Seguimiento quincenal. Higiene del sueño."
        tests = "Tests sugeridos:\n1. 16PF-5: https://bit.ly/16pf5-ref\n2. Test HTP (Casa-Árbol-Persona).\n3. Inventario de Ansiedad de Beck (BAI)."
    return concl, recom, tests

# --- 3. GESTIÓN DE BÚSQUEDA ---
db_actual = cargar_db()
with st.sidebar:
    st.header("🔍 BUSCADOR DE ARCHIVO")
    id_lista = ["--- REGISTRO NUEVO ---"] + (db_actual["Identidad"].tolist() if not db_actual.empty else [])
    seleccion = st.selectbox("Seleccionar Identidad:", id_lista)
    datos_c = db_actual[db_actual["Identidad"] == seleccion].iloc[0].to_dict() if seleccion != "--- REGISTRO NUEVO ---" else {}

st.title("🛡️ Protocolo Integral de Evaluación Psicológica - D.S.P.")

# --- 4. CUESTIONARIO COMPLETO SIN RECORTES ---
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
    sexo = c5.selectbox("5. Sexo", ["M", "F"], index=0 if datos_c.get("Sexo")=="M" else 1)
    est_civil = c6.selectbox("6. Estado Civil", ["Soltero", "Casado", "Divorciado", "Unión Libre", "Viudo"], 
                             index=["Soltero", "Casado", "Divorciado", "Unión Libre", "Viudo"].index(datos_c.get("Estado_Civil", "Soltero")))
    
    c7, c8, c9 = st.columns(3)
    nac = c7.text_input("7. Nacionalidad", value=datos_c.get("Nacionalidad", ""))
    relig = c8.text_input("8. Religión", value=datos_c.get("Religion", ""))
    cel = c9.text_input("9. Celular", value=datos_c.get("Celular", ""))

with t2:
    st.subheader("II. MOTIVO Y ANTECEDENTES")
    motivo = st.text_area("10. Motivo de Consulta (Vaciado literal)", value=datos_c.get("Motivo", ""))
    ant_sit = st.text_area("11. ¿Cuándo se sintió bien por última vez? (Antecedentes)", value=datos_c.get("Ant_Sit", ""))

with t3:
    st.subheader("III-IV. FUNCIONES ORGÁNICAS")
    c10, c11, c12, c13 = st.columns(4)
    sueño = c10.selectbox("12. Sueño", ["Normal", "Insomnio", "Hipersomnia", "Interrumpido"], value=datos_c.get("Sueño", "Normal"))
    apetito = c11.selectbox("13. Apetito", ["Normal", "Aumentado", "Disminuido"], value=datos_c.get("Apetito", "Normal"))
    sed = c12.text_input("14. Sed", value=datos_c.get("Sed", ""))
    defec = c13.text_input("15. Defecación", value=datos_c.get("Defec", ""))

with t4:
    st.subheader("V-VI. SALUD Y SÍNTOMAS NEUROTICOS")
    alergias = st.text_input("16. Alergias", value=datos_c.get("Alergias", ""))
    meds = st.text_input("17. Medicamentos actuales", value=datos_c.get("Meds", ""))
    hosp = st.text_input("18. Hospitalizaciones (Motivo/Tiempo)", value=datos_c.get("Hosp", ""))
    enf_inf = st.text_input("19. Enfermedades en la infancia", value=datos_c.get("Enf_Inf", ""))
    
    st.write("**20. Checklist de Síntomas Neuroticos**")
    sint_list = ["Pesadillas", "Terror Nocturno", "Sonambulismo", "Enuresis", "Encopresis", "Onicofagia", "Tics", "Fobias", "Drogas", "Alcohol", "Ideas Suicidas"]
    sintomas = st.multiselect("Marque todos los presentes:", sint_list, default=eval(datos_c.get("Sintomas", "[]")) if datos_c else [])

with t5:
    st.subheader("VII. INFORMACIÓN FAMILIAR")
    p_nom = st.text_input("21. Nombre del Padre", value=datos_c.get("P_Nom", ""))
    p_rel = st.text_area("22. Relación con el padre y tipo de castigos", value=datos_c.get("P_Rel", ""))
    m_nom = st.text_input("23. Nombre de la Madre", value=datos_c.get("M_Nom", ""))
    m_rel = st.text_area("24. Relación con la madre y tipo de castigos", value=datos_c.get("M_Rel", ""))
    hermanos = st.text_input("25. Número de hermanos y lugar que ocupa", value=datos_c.get("Hermanos", ""))
    crianza = st.text_input("26. ¿Quién lo crió?", value=datos_c.get("Crianza", ""))
    hist_fel = st.text_area("27. Historia feliz vivida en familia", value=datos_c.get("Hist_Fel", ""))

with t6:
    st.subheader("VIII-IX. DESARROLLO")
    embarazo = st.text_input("28. Circunstancias del embarazo (¿Planeado/Deseado?)", value=datos_c.get("Embarazo", ""))
    parto = st.text_input("29. Tipo de parto (Fórceps, incubadora, etc.)", value=datos_c.get("Parto", ""))
    gateo = st.text_input("30. ¿A qué edad gateó?", value=datos_c.get("Gateo", ""))
    camino = st.text_input("31. ¿A qué edad caminó?", value=datos_c.get("Camino", ""))
    hablo = st.text_input("32. ¿A qué edad habló?", value=datos_c.get("Hablo", ""))
    esfinter = st.text_input("33. ¿A qué edad controló esfínteres?", value=datos_c.get("Esfinter", ""))
    
    st.write("**Datos Escolares**")
    esc_edad = st.text_input("34. Edad de inicio escolar", value=datos_c.get("Esc_Edad", ""))
    esc_dif = st.text_input("35. Materias de dificultad", value=datos_c.get("Esc_Dif", ""))
    esc_apren = st.selectbox("36. Tipo de aprendizaje", ["Visual", "Auditivo", "Kinestésico"], value=datos_c.get("Esc_Apren", "Visual"))
    esc_cond = st.text_area("37. Conducta y rendimiento escolar", value=datos_c.get("Esc_Cond", ""))

with t7:
    st.subheader("X-XI. SEXUALIDAD Y PERSONALIDAD")
    menarquia = st.text_input("38. Menarquia (Mujeres) o Primera Eyaculación (Hombres)", value=datos_c.get("Menarquia", ""))
    sex_opi = st.text_area("39. Opinión sobre sexualidad, matrimonio y masturbación", value=datos_c.get("Sex_Opi", ""))
    sex_rel = st.text_input("40. Edad de primera relación sexual", value=datos_c.get("Sex_Rel", ""))
    noviazgo = st.text_input("41. Edad de primer noviazgo", value=datos_c.get("Noviazgo", ""))
    
    st.write("**Rasgos de Personalidad**")
    pers_conf = st.text_input("42. ¿Confía en las personas? (Celos, rencor)", value=datos_c.get("Pers_Conf", ""))
    pers_imp = st.text_input("43. ¿Actos impulsivos? (¿Se arrepiente?)", value=datos_c.get("Pers_Imp", ""))

with t8:
    st.subheader("XII. ANÁLISIS, CONCLUSIONES Y RECOMENDACIONES (IA)")
    if st.button("🧠 EJECUTAR ANÁLISIS CLÍNICO"):
        c_ia, r_ia, t_ia = realizar_analisis_ia(motivo, sintomas)
        st.session_state["ia_concl"] = c_ia
        st.session_state["ia_recom"] = r_ia
        st.session_state["ia_tests"] = t_ia

    analisis = st.text_area("Análisis Clínico Profesional", value=datos_c.get("Analisis", ""))
    concl_f = st.text_area("Conclusiones Clínicas", value=st.session_state.get("ia_concl", datos_c.get("Concl", "")))
    recom_f = st.text_area("Plan de Seguimiento y Recomendaciones", value=st.session_state.get("ia_recom", datos_c.get("Recom", "")))
    tests_f = st.text_area("Batería de Tests (Base + Sugerencias IA)", value=st.session_state.get("ia_tests", datos_c.get("Tests", "")))
    psicologo = st.text_input("Psicólogo Evaluador", value=datos_c.get("Psicologo", ""))

# --- 5. GUARDADO ---
if st.button("💾 GUARDAR REGISTRO Y GENERAR PROTOCOLO"):
    if id_pac and nom_pac:
        reg = {
            "Identidad": id_pac, "Nombre": nom_pac, "F_Nac": f_nac, "Edad": edad, "Sexo": sexo,
            "Estado_Civil": est_civil, "Nacionalidad": nac, "Religion": relig, "Celular": cel,
            "Motivo": motivo, "Ant_Sit": ant_sit, "Sueño": sueño, "Apetito": apetito, "Sed": sed,
            "Defec": defec, "Alergias": alergias, "Meds": meds, "Hosp": hosp, "Enf_Inf": enf_inf,
            "Sintomas": str(sintomas), "P_Nom": p_nom, "P_Rel": p_rel, "M_Nom": m_nom, "M_Rel": m_rel,
            "Hermanos": hermanos, "Crianza": crianza, "Hist_Fel": hist_fel, "Embarazo": embarazo,
            "Parto": parto, "Gateo": gateo, "Camino": camino, "Hablo": hablo, "Esfinter": esfinter,
            "Esc_Edad": esc_edad, "Esc_Dif": esc_dif, "Esc_Apren": esc_apren, "Esc_Cond": esc_cond,
            "Menarquia": menarquia, "Sex_Opi": sex_opi, "Sex_Rel": sex_rel, "Noviazgo": noviazgo,
            "Pers_Conf": pers_conf, "Pers_Imp": pers_imp, "Analisis": analisis, "Concl": concl_f,
            "Recom": recom_f, "Tests": tests_f, "Psicologo": psicologo, "Fecha": str(date.today())
        }
        guardar_db(reg)
        st.success("✅ Guardado exitoso. Expediente actualizado.")
        
        doc = Document()
        doc.add_heading('PROTOCOLO CLÍNICO D.S.P. - HONDURAS', 0)
        for k, v in reg.items():
            p = doc.add_paragraph()
            p.add_run(f"{k}: ").bold = True
            p.add_run(str(v))
        
        buf = io.BytesIO(); doc.save(buf); buf.seek(0)
        st.download_button("📥 DESCARGAR PROTOCOLO COMPLETO", buf, f"Protocolo_{id_pac}.docx")
