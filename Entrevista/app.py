import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN Y BASE DE DATOS ---
st.set_page_config(page_title="D.S.P. Honduras - Sistema Integral v27", layout="wide")
DB_FILE = "DB_DSP_FINAL_MAESTRO.xlsx"

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

# --- 2. MOTOR DE IA CONSULTIVO ---
def motor_ia_dsp(motivo, checklist, opinion_prof):
    texto = (str(motivo) + str(checklist) + str(opinion_prof)).lower()
    if any(x in texto for x in ["suicid", "morir", "matar", "vida", "solo"]):
        concl = "RIESGO CRÍTICO: Ideación autolítica detectada."
        recom = "Remisión inmediata a psiquiatría y vigilancia estrecha."
        tests = "1. Beck (BDI-II): https://bit.ly/test-beck\n2. SCL-90-R: https://bit.ly/scl-90\n3. BHS (Desesperanza)."
    elif any(x in texto for x in ["ira", "arma", "pelea", "agresiv"]):
        concl = "PERFIL CONDUCTUAL: Rasgos de impulsividad marcados."
        recom = "Terapia de manejo de ira y evaluación de idoneidad operativa."
        tests = "1. MMPI-2: https://bit.ly/mmpi-2-ref\n2. IPV: https://bit.ly/ipv-test\n3. STAXI-2 (Ira)."
    else:
        concl = "ESTADO: Ajuste emocional estable."
        recom = "Seguimiento preventivo y técnicas de autocuidado."
        tests = "1. 16PF-5: https://bit.ly/16pf5-ref\n2. Test HTP\n3. Inventario de Ansiedad (BAI)."
    
    feedback = f"Sugerencia IA sobre su opinión: Al observar '{opinion_prof}', se recomienda profundizar en el área de personalidad proyectiva."
    return concl, recom, tests, feedback

# --- 3. BÚSQUEDA ---
db_actual = cargar_db()
with st.sidebar:
    st.header("📂 EXPEDIENTES D.S.P.")
    id_list = ["--- REGISTRO NUEVO ---"] + (db_actual["Identidad"].tolist() if not db_actual.empty else [])
    seleccion = st.selectbox("Seleccionar Identidad:", id_list)
    d = db_actual[db_actual["Identidad"] == seleccion].iloc[0].to_dict() if seleccion != "--- REGISTRO NUEVO ---" else {}

st.title("🛡️ Protocolo de Entrevista Clínica Completo - D.S.P.")

# --- 4. LAS 12 ÁREAS SIN OMISIONES ---
tabs = st.tabs([
    "I-II. ID / Motivo", "III-V. Salud Médica", "VI. Checklist Vida", 
    "VII. Familiares", "VIII-IX. Desarrollo", "X-XI. Sexo/Pers.", "XII-XIII. Opinión/IA"
])

with tabs[0]:
    st.subheader("I. IDENTIFICACIÓN Y II. MOTIVO")
    c1, c2, c3 = st.columns(3)
    identidad = c1.text_input("1. Identidad", value=d.get("Identidad", ""))
    nombre = c2.text_input("2. Nombre", value=d.get("Nombre", ""))
    f_nac = c3.text_input("3. Lugar y Fecha Nacimiento", value=d.get("F_Nac", ""))
    edad = st.text_input("4. Edad", value=d.get("Edad", ""))
    sexo = st.selectbox("5. Sexo", ["M", "F"], index=v_idx(d.get("Sexo"), ["M", "F"]))
    ec_l = ["Soltero", "Casado", "Divorciado", "Unión Libre", "Viudo"]; est_civil = st.selectbox("6. Estado Civil", ec_l, index=v_idx(d.get("Estado_Civil"), ec_l))
    nacionalidad = st.text_input("7. Nacionalidad", value=d.get("Nacionalidad", ""))
    religion = st.text_input("8. Religión", value=d.get("Religion", ""))
    celular = st.text_input("9. Celular", value=d.get("Celular", ""))
    ocupacion = st.text_input("10. Ocupación", value=d.get("Ocupacion", ""))
    direccion = st.text_input("11. Dirección", value=d.get("Direccion", ""))
    asignacion = st.text_input("12. Asignación/Unidad", value=d.get("Asignacion", ""))
    remitido = st.text_input("13. Remitido por", value=d.get("Remitido", ""))
    motivo = st.text_area("14. Motivo de Consulta (Vaciado literal)", value=d.get("Motivo", ""))

with tabs[1]:
    st.subheader("III-IV. ORGÁNICAS Y ANTECEDENTES")
    ant_sit = st.text_area("15. Antecedentes (¿Cuándo comenzó la situación actual?)", value=d.get("Ant_Sit", ""))
    f1, f2, f3, f4 = st.columns(4)
    sueño = f1.selectbox("16. Sueño", ["Normal", "Insomnio", "Hipersomnia", "Interrumpido"], index=v_idx(d.get("Sueño"), ["Normal", "Insomnio", "Hipersomnia", "Interrumpido"]))
    apetito = f2.selectbox("17. Apetito", ["Normal", "Aumentado", "Disminuido"], index=v_idx(d.get("Apetito"), ["Normal", "Aumentado", "Disminuido"]))
    sed = f3.text_input("18. Sed", value=d.get("Sed", ""))
    defec = f4.text_input("19. Defecación", value=d.get("Defec", ""))
    
    st.subheader("V. SALUD MÉDICA DETALLADA")
    m1, m2, m3, m4 = st.columns(4)
    convulsiones = m1.text_input("20. Convulsiones", value=d.get("Convulsiones", ""))
    cefaleas = m2.text_input("21. Cefaleas", value=d.get("Cefaleas", ""))
    resp = m3.text_input("22. Enf. Respiratorias", value=d.get("Resp", ""))
    infec = m4.text_input("23. Infecciones", value=d.get("Infecciones", ""))
    alergias = st.text_input("24. Alergias", value=d.get("Alergias", ""))
    meds = st.text_input("25. Medicamentos actuales", value=d.get("Meds", ""))
    hosp = st.text_input("26. Hospitalizaciones", value=d.get("Hosp", ""))
    cirugias = st.text_input("27. Cirugías", value=d.get("Cirugias", ""))
    enf_inf = st.text_input("28. Enfermedades infancia", value=d.get("Enf_Inf", ""))

with tabs[2]:
    st.subheader("VI. CHECKLIST VIDA (Marque con una X si ha presentado)")
    v_items = ["Pesadillas", "Terror Nocturno", "Sonambulismo", "Enuresis", "Encopresis", "Onicofagia", "Tics", "Fobias", "Drogas", "Alcohol", "Ideas Suicidas", "Intentos Suicidas", "Alucinaciones", "Pérdida de memoria", "Mareos"]
    check_vida = st.multiselect("Seleccione síntomas:", v_items, default=eval(d.get("Check_Vida", "[]")) if d else [])

with tabs[3]:
    st.subheader("VII. ÁREA FAMILIAR Y SOCIAL")
    st.write("**DATOS DEL PADRE**")
    p1, p2, p3 = st.columns(3)
    p_nom = p1.text_input("Nombre Padre", value=d.get("P_Nom", ""))
    p_edad = p2.text_input("Edad Padre", value=d.get("P_Edad", ""))
    p_vive = p3.selectbox("¿Vive? (P)", ["Sí", "No"], index=v_idx(d.get("P_Vive"), ["Sí", "No"]))
    p4, p5 = st.columns(2)
    p_salud = p4.text_input("Salud Padre", value=d.get("P_Salud", ""))
    p_ocupa = p5.text_input("Ocupación Padre", value=d.get("P_Ocupa", ""))
    p_rel = st.text_area("Relación Padre y Castigos", value=d.get("P_Rel", ""))
    
    st.write("**DATOS DE LA MADRE**")
    m1, m2, m3 = st.columns(3)
    m_nom = m1.text_input("Nombre Madre", value=d.get("M_Nom", ""))
    m_edad = m2.text_input("Edad Madre", value=d.get("M_Edad", ""))
    m_vive = m3.selectbox("¿Vive? (M)", ["Sí", "No"], index=v_idx(d.get("M_Vive"), ["Sí", "No"]))
    m4, m5 = st.columns(2)
    m_salud = m4.text_input("Salud Madre", value=d.get("M_Salud", ""))
    m_ocupa = m5.text_input("Ocupación Madre", value=d.get("M_Ocupa", ""))
    m_rel = st.text_area("Relación Madre y Castigos", value=d.get("M_Rel", ""))
    
    st.write("---")
    rel_padres = st.text_area("Relación entre los Padres (Pareja)", value=d.get("Rel_Padres", ""))
    hermanos = st.text_input("Hermanos y lugar que ocupa", value=d.get("Hermanos", ""))
    crianza = st.text_input("¿Quién lo crió?", value=d.get("Crianza", ""))
    hist_fel = st.text_area("Historia feliz en familia", value=d.get("Hist_Fel", ""))
    social = st.text_area("Área Social (Amigos, vecinos, ambiente)", value=d.get("Social", ""))

with tabs[4]:
    st.subheader("VIII-IX. DESARROLLO Y EDUCACIÓN")
    embarazo = st.text_input("Embarazo (¿Deseado/Reacción?)", value=d.get("Embarazo", ""))
    parto = st.text_input("Parto (Incubadora/Fórceps)", value=d.get("Parto", ""))
    c20, c21, c22, c23 = st.columns(4)
    gateo = c20.text_input("Edad Gateó", value=d.get("Gateo", ""))
    camino = c21.text_input("Edad Caminó", value=d.get("Camino", ""))
    hablo = c22.text_input("Edad Habló", value=d.get("Hablo", ""))
    esfinter = c23.text_input("Edad Esfínteres", value=d.get("Esfinter", ""))
    esc_edad = st.text_input("Edad inicio escuela", value=d.get("Esc_Edad", ""))
    esc_dif = st.text_input("Materias dificultad", value=d.get("Esc_Dif", ""))
    esc_cond = st.text_area("Conducta y rendimiento escolar", value=d.get("Esc_Cond", ""))

with tabs[5]:
    st.subheader("X-XI. SEXUALIDAD Y PERSONALIDAD")
    menarquia = st.text_input("Menarquia / Eyaculación", value=d.get("Menarquia", ""))
    sex_opi = st.text_area("Opinión Sexualidad, Matrimonio y Masturbación", value=d.get("Sex_Opi", ""))
    sex_rel = st.text_input("Edad primera relación", value=d.get("Sex_Rel", ""))
    noviazgo = st.text_input("Edad primer noviazgo", value=d.get("Noviazgo", ""))
    pers_conf = st.text_input("¿Confía en personas? (Celos/Rencor)", value=d.get("Pers_Conf", ""))
    pers_imp = st.text_input("¿Actos impulsivos? (¿Arrepentimiento?)", value=d.get("Pers_Imp", ""))

with tabs[6]:
    st.subheader("XIII. OPINIÓN Y RESULTADOS IA")
    opinion_u = st.text_area("✍️ Su Opinión Profesional:", value=d.get("Opinion_Prof", ""))
    if st.button("🧠 PROCESAR INFORME IA"):
        c_ia, r_ia, t_ia, f_ia = motor_ia_dsp(motivo, check_vida, opinion_u)
        st.session_state["ia_concl"] = c_ia
        st.session_state["ia_recom"] = r_ia
        st.session_state["ia_tests"] = t_ia
        st.session_state["ia_feed"] = f_ia
    st.info(st.session_state.get("ia_feed", "Aún no hay feedback."))
    concl_f = st.text_area("Conclusiones", value=st.session_state.get("ia_concl", d.get("Conclusiones", "")))
    recom_f = st.text_area("Recomendaciones", value=st.session_state.get("ia_recom", d.get("Recomendaciones", "")))
    tests_f = st.text_area("Tests Sugeridos", value=st.session_state.get("ia_tests", d.get("Tests", "")))
    psicologo = st.text_input("Evaluador", value=d.get("Psicologo", ""))

# --- 5. GUARDADO ---
if st.button("💾 GUARDAR Y GENERAR INFORME"):
    if identidad and nombre:
        reg = {
            "Identidad": identidad, "Nombre": nombre, "F_Nac": f_nac, "Edad": edad, "Sexo": sexo, "Estado_Civil": est_civil,
            "Nacionalidad": nacionalidad, "Religion": religion, "Celular": celular, "Ocupacion": ocupacion, "Direccion": direccion,
            "Asignacion": asignacion, "Remitido": remitido, "Motivo": motivo, "Ant_Sit": ant_sit, "Sueño": sueño, "Apetito": apetito,
            "Sed": sed, "Defec": defec, "Convulsiones": convulsiones, "Cefaleas": cefaleas, "Resp": resp, "Infecciones": infec,
            "Alergias": alergias, "Meds": meds, "Hosp": hosp, "Cirugias": cirugias, "Enf_Inf": enf_inf, "Check_Vida": str(check_vida),
            "P_Nom": p_nom, "P_Edad": p_edad, "P_Vive": p_vive, "P_Salud": p_salud, "P_Ocupa": p_ocupa, "P_Rel": p_rel,
            "M_Nom": m_nom, "M_Edad": m_edad, "M_Vive": m_vive, "M_Salud": m_salud, "M_Ocupa": m_ocupa, "M_Rel": m_rel,
            "Rel_Padres": rel_padres, "Hermanos": hermanos, "Crianza": crianza, "Hist_Fel": hist_fel, "Social": social,
            "Embarazo": embarazo, "Parto": parto, "Gateo": gateo, "Camino": camino, "Hablo": hablo, "Esfinter": esfinter,
            "Esc_Edad": esc_edad, "Esc_Dif": esc_dif, "Esc_Cond": esc_cond, "Menarquia": menarquia, "Sex_Opi": sex_opi,
            "Sex_Rel": sex_rel, "Noviazgo": noviazgo, "Pers_Conf": pers_conf, "Pers_Imp": pers_imp, "Opinion_Prof": opinion_u,
            "Conclusiones": concl_f, "Recomendaciones": recom_f, "Tests": tests_f, "Psicologo": psicologo, "Fecha": str(date.today())
        }
        guardar_db(reg)
        doc = Document(); doc.add_heading('INFORME D.S.P.', 0)
        doc.add_heading('RESULTADOS IA', 1); doc.add_paragraph(f"Conclusiones: {concl_f}\nRec: {recom_f}\nTests: {tests_f}")
        doc.add_heading('DATOS COMPLETOS', 1)
        for k, v in reg.items(): doc.add_paragraph(f"{k}: {v}")
        buf = io.BytesIO(); doc.save(buf); buf.seek(0)
        st.success("Guardado."); st.download_button("Descargar Word", buf, f"Informe_{identidad}.docx")
