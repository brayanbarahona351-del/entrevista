import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="D.S.P. Honduras - Protocolo Oficial", layout="wide")
DB_FILE = "DB_DSP_MAESTRO_FINAL.xlsx"

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

# --- 2. MOTOR DE IA (RECOMENDACIONES Y TESTS) ---
def motor_ia_dsp(motivo, sintomas_vida):
    texto = (str(motivo) + str(sintomas_vida)).lower()
    
    if any(x in texto for x in ["suicid", "morir", "matar", "solo"]):
        concl = "RIESGO AUTOLESIVO: Indicadores de ideación suicida y desesperanza."
        segui = "Intervención inmediata, contrato de no agresión, remisión a psiquiatría y terapia familiar."
        tests = "1. Beck (BDI-II): https://bit.ly/test-beck\n2. SCL-90-R: https://bit.ly/scl-90\n3. ADICIONAL: Escala de Desesperanza de Beck (BHS)\n4. ADICIONAL: Test de Plutchik."
    elif any(x in texto for x in ["ira", "agresiv", "arma", "pelea"]):
        concl = "PERFIL CONDUCTUAL: Rasgos de impulsividad y baja tolerancia a la frustración."
        segui = "Psicoterapia enfocada en control de impulsos y manejo de ira (TCC)."
        tests = "1. MMPI-2: https://bit.ly/mmpi-2-ref\n2. IPV: https://bit.ly/ipv-test\n3. ADICIONAL: STAXI-2 (Inventario de Ira).\n4. ADICIONAL: Test proyectivo de la Figura Humana."
    else:
        concl = "ESTADO: Ajuste emocional dentro de parámetros normales con estresores externos."
        segui = "Monitoreo mensual y técnicas de higiene mental laboral."
        tests = "1. 16PF-5: https://bit.ly/16pf5-ref\n2. ADICIONAL: Test HTP (Casa-Árbol-Persona).\n3. ADICIONAL: Inventario de Ansiedad de Beck (BAI)."
    
    return concl, segui, tests

# --- 3. BÚSQUEDA ---
db_actual = cargar_db()
with st.sidebar:
    st.header("📂 EXPEDIENTES")
    id_list = ["--- NUEVO ---"] + (db_actual["Identidad"].tolist() if not db_actual.empty else [])
    seleccion = st.selectbox("Buscar Identidad:", id_list)
    d = db_actual[db_actual["Identidad"] == seleccion].iloc[0].to_dict() if seleccion != "--- NUEVO ---" else {}

st.title("🛡️ Protocolo de Evaluación Psicológica D.S.P.")

# --- 4. LAS 12 ÁREAS DEL PROTOCOLO ---
tabs = st.tabs([
    "1-2. Identificación/Motivo", "3-4. Orgánicas/Antecedentes", "5. Salud Médica", 
    "6. Checklist Vida", "7. Familia/Padres", "8-9. Desarrollo/Escuela", 
    "10-11. Sexo/Personalidad", "12. ANÁLISIS IA"
])

with tabs[0]:
    st.subheader("I. DATOS DE IDENTIFICACIÓN")
    c1, c2, c3 = st.columns(3)
    identidad = c1.text_input("Identidad", value=d.get("Identidad", ""))
    nombre = c2.text_input("Nombre Completo", value=d.get("Nombre", ""))
    f_nac = c3.text_input("Fecha/Lugar Nacimiento", value=d.get("F_Nac", ""))
    
    c4, c5, c6 = st.columns(3)
    edad = c4.text_input("Edad", value=d.get("Edad", ""))
    s_l = ["M", "F"]; sexo = c5.selectbox("Sexo", s_l, index=v_idx(d.get("Sexo"), s_l))
    ec_l = ["Soltero", "Casado", "Divorciado", "Unión Libre", "Viudo"]; est_civil = c6.selectbox("Estado Civil", ec_l, index=v_idx(d.get("Estado_Civil"), ec_l))
    
    c7, c8, c9 = st.columns(3)
    nacionalidad = c7.text_input("Nacionalidad", value=d.get("Nacionalidad", ""))
    religion = c8.text_input("Religión", value=d.get("Religion", ""))
    celular = c9.text_input("Celular", value=d.get("Celular", ""))
    
    ocupacion = st.text_input("Ocupación", value=d.get("Ocupacion", ""))
    direccion = st.text_input("Dirección", value=d.get("Direccion", ""))
    asignacion = st.text_input("Asignación/Unidad", value=d.get("Asignacion", ""))
    remitido = st.text_input("Remitido por", value=d.get("Remitido", ""))
    
    st.subheader("II. MOTIVO DE CONSULTA")
    motivo = st.text_area("Describa el motivo de consulta literal:", value=d.get("Motivo", ""))

with tabs[1]:
    st.subheader("III. ANTECEDENTES Y IV. ORGÁNICAS")
    ant_sit = st.text_area("¿Cuándo comenzó la situación actual?", value=d.get("Ant_Sit", ""))
    
    f1, f2, f3, f4 = st.columns(4)
    su_l = ["Normal", "Insomnio", "Hipersomnia", "Interrumpido"]; sueño = f1.selectbox("Sueño", su_l, index=v_idx(d.get("Sueño", "Normal"), su_l))
    ap_l = ["Normal", "Aumentado", "Disminuido"]; apetito = f2.selectbox("Apetito", ap_l, index=v_idx(d.get("Apetito", "Normal"), ap_l))
    sed = f3.text_input("Sed", value=d.get("Sed", ""))
    defec = f4.text_input("Defecación", value=d.get("Defec", ""))

with tabs[2]:
    st.subheader("V. ESTADO DE SALUD MÉDICA")
    c10, c11 = st.columns(2)
    alergias = c10.text_input("Alergias", value=d.get("Alergias", ""))
    meds = c11.text_input("Medicamentos que toma", value=d.get("Meds", ""))
    
    c12, c13 = st.columns(2)
    hosp = c12.text_input("Hospitalizaciones (Motivo/Tiempo)", value=d.get("Hosp", ""))
    cirugias = c13.text_input("Cirugías", value=d.get("Cirugias", ""))
    
    st.write("**Antecedentes Médicos Específicos:**")
    m1, m2, m3, m4 = st.columns(4)
    convulsiones = m1.text_input("Convulsiones", value=d.get("Convulsiones", ""))
    cefaleas = m2.text_input("Cefaleas (Dolores de cabeza)", value=d.get("Cefaleas", ""))
    resp = m3.text_input("Enf. Respiratorias", value=d.get("Resp", ""))
    infec = m4.text_input("Infecciones", value=d.get("Infecciones", ""))
    
    enf_inf = st.text_input("Enfermedades en la infancia", value=d.get("Enf_Inf", ""))

with tabs[3]:
    st.subheader("VI. CHECKLIST: ¿HA PRESENTADO ALGO DE ESTO EN SU VIDA?")
    check_list = [
        "Pesadillas", "Terror Nocturno", "Sonambulismo", "Enuresis", "Encopresis", 
        "Onicofagia", "Tics", "Fobias", "Drogas", "Alcohol", "Ideas Suicidas",
        "Intentos Suicidas", "Alucinaciones", "Pérdida de memoria", "Mareos"
    ]
    seleccion_vida = st.multiselect("Marque con una X (Seleccione):", check_list, 
                                     default=eval(d.get("Check_Vida", "[]")) if d else [])

with tabs[4]:
    st.subheader("VII. ÁREA FAMILIAR Y SOCIAL")
    p_nom = st.text_input("Nombre del Padre", value=d.get("P_Nom", ""))
    p_rel = st.text_area("Relación con el padre y castigos", value=d.get("P_Rel", ""))
    m_nom = st.text_input("Nombre de la Madre", value=d.get("M_Nom", ""))
    m_rel = st.text_area("Relación con la madre y castigos", value=d.get("M_Rel", ""))
    
    st.write("**Relación entre los Padres**")
    rel_padres = st.text_area("¿Cómo es/era la relación entre padre y madre?", value=d.get("Rel_Padres", ""))
    
    hermanos = st.text_input("Hermanos y lugar que ocupa", value=d.get("Hermanos", ""))
    crianza = st.text_input("¿Quién lo crió?", value=d.get("Crianza", ""))
    hist_fel = st.text_area("Historia feliz vivida en familia", value=d.get("Hist_Fel", ""))
    
    st.write("**Área Social y Ambiental**")
    social = st.text_area("Relación con amigos, vecinos y ambiente social", value=d.get("Social", ""))

with tabs[5]:
    st.subheader("VIII-IX. DESARROLLO Y EDUCACIÓN")
    embarazo = st.text_input("Circunstancias embarazo (¿Deseado/Reacción?)", value=d.get("Embarazo", ""))
    parto = st.text_input("Parto (Incubadora, fórceps, tiempo)", value=d.get("Parto", ""))
    
    c14, c15, c16, c17 = st.columns(4)
    gateo = c14.text_input("Edad Gateó", value=d.get("Gateo", ""))
    camino = c15.text_input("Edad Caminó", value=d.get("Camino", ""))
    hablo = c16.text_input("Edad Habló", value=d.get("Hablo", ""))
    esfinter = c17.text_input("Edad Esfínteres", value=d.get("Esfinter", ""))
    
    st.write("**Datos Escolares**")
    esc_edad = st.text_input("Edad inicio escuela", value=d.get("Esc_Edad", ""))
    esc_dif = st.text_input("Materias de dificultad", value=d.get("Esc_Dif", ""))
    esc_cond = st.text_area("Conducta y rendimiento escolar", value=d.get("Esc_Cond", ""))

with tabs[6]:
    st.subheader("X-XI. SEXUALIDAD Y PERSONALIDAD")
    menarquia = st.text_input("Menarquia / Eyaculación", value=d.get("Menarquia", ""))
    sex_opi = st.text_area("Opinión sobre sexualidad, matrimonio y masturbación", value=d.get("Sex_Opi", ""))
    sex_rel = st.text_input("Edad primera relación sexual", value=d.get("Sex_Rel", ""))
    noviazgo = st.text_input("Edad primer noviazgo", value=d.get("Noviazgo", ""))
    
    st.write("**Rasgos de Personalidad**")
    pers_conf = st.text_input("¿Confía en las personas? (Celos, rencor)", value=d.get("Pers_Conf", ""))
    pers_imp = st.text_input("¿Actos impulsivos? (¿Se arrepiente?)", value=d.get("Pers_Imp", ""))

with tabs[7]:
    st.subheader("XII. ANÁLISIS, CONCLUSIONES Y RECOMENDACIONES (IA)")
    if st.button("🧠 GENERAR ANÁLISIS E INFORME"):
        concl_ia, segui_ia, tests_ia = motor_ia_dsp(motivo, seleccion_vida)
        st.session_state["ia_concl"] = concl_ia
        st.session_state["ia_recom"] = segui_ia
        st.session_state["ia_tests"] = tests_ia

    analisis_p = st.text_area("Análisis Clínico Profesional", value=d.get("Analisis", ""))
    conclusiones = st.text_area("Conclusiones", value=st.session_state.get("ia_concl", d.get("Conclusiones", "")))
    recomendaciones = st.text_area("Recomendaciones de Seguimiento", value=st.session_state.get("ia_recom", d.get("Recomendaciones", "")))
    tests_sug = st.text_area("Batería de Tests y Enlaces", value=st.session_state.get("ia_tests", d.get("Tests", "")))
    psicologo = st.text_input("Psicólogo Evaluador", value=d.get("Psicologo", ""))

# --- 5. GUARDADO ---
if st.button("💾 GUARDAR REGISTRO Y GENERAR WORD"):
    if identidad and nombre:
        reg = {
            "Identidad": identidad, "Nombre": nombre, "F_Nac": f_nac, "Edad": edad, "Sexo": sexo,
            "Estado_Civil": est_civil, "Nacionalidad": nacionalidad, "Religion": religion,
            "Celular": celular, "Ocupacion": ocupacion, "Direccion": direccion, "Asignacion": asignacion,
            "Remitido": remitido, "Motivo": motivo, "Ant_Sit": ant_sit, "Sueño": sueño, "Apetito": apetito,
            "Sed": sed, "Defec": defec, "Alergias": alergias, "Meds": meds, "Hosp": hosp, "Cirugias": cirugias,
            "Convulsiones": convulsiones, "Cefaleas": cefaleas, "Resp": resp, "Infecciones": infec,
            "Enf_Inf": enf_inf, "Check_Vida": str(seleccion_vida), "P_Nom": p_nom, "P_Rel": p_rel,
            "M_Nom": m_nom, "M_Rel": m_rel, "Rel_Padres": rel_padres, "Hermanos": hermanos,
            "Crianza": crianza, "Hist_Fel": hist_fel, "Social": social, "Embarazo": embarazo,
            "Parto": parto, "Gateo": gateo, "Camino": camino, "Hablo": hablo, "Esfinter": esfinter,
            "Esc_Edad": esc_edad, "Esc_Dif": esc_dif, "Esc_Cond": esc_cond, "Menarquia": menarquia,
            "Sex_Opi": sex_opi, "Sex_Rel": sex_rel, "Noviazgo": noviazgo, "Pers_Conf": pers_conf,
            "Pers_Imp": pers_imp, "Analisis": analisis_p, "Conclusiones": conclusiones,
            "Recomendaciones": recomendaciones, "Tests": tests_sug, "Psicologo": psicologo, "Fecha": str(date.today())
        }
        guardar_db(reg)
        st.success(f"✅ Registro de {nombre} guardado correctamente.")
        
        doc = Document()
        doc.add_heading('PROTOCOLO CLÍNICO D.S.P. - HONDURAS', 0)
        for k, v in reg.items():
            p = doc.add_paragraph()
            p.add_run(f"{k}: ").bold = True
            p.add_run(str(v))
        
        buf = io.BytesIO(); doc.save(buf); buf.seek(0)
        st.download_button("📥 DESCARGAR PROTOCOLO COMPLETO", buf, f"Expediente_{identidad}.docx")
    else:
        st.error("Identidad y Nombre son obligatorios.")
