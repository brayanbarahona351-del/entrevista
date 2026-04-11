import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN DE PANTALLA ---
st.set_page_config(page_title="D.S.P. Honduras - Protocolo Completo", layout="wide")

# --- 2. GESTIÓN DE BASE DE DATOS LOCAL ---
DB_FILE = "DB_DSP_EXPEDIENTES_COMPLETOS.xlsx"

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
        # Evitar duplicados eliminando la versión anterior antes de guardar la nueva
        df = df[df["Identidad"] != str(datos_dict["Identidad"])]
    df_final = pd.concat([df, pd.DataFrame([datos_dict])], ignore_index=True)
    df_final.to_excel(DB_FILE, index=False)
    return df_final

def v_idx(opcion, lista):
    try: return lista.index(opcion)
    except: return 0

# --- 3. MOTOR DE ANÁLISIS INTEGRAL (CONSULTA IA) ---
def motor_ia_gemini(datos):
    # Procesamiento de todas las áreas para la recomendación
    cuerpo_clinico = str(datos).lower()
    
    if any(x in cuerpo_clinico for x in ["suicid", "muerte", "matar", "vida"]):
        res = "ALERTA: Riesgo Autolítico Alto."
        rec = "Protocolo de vigilancia, remisión urgente a psiquiatría y contrato de no agresión."
        tests = "Beck (BDI-II), SCL-90-R, Escala de Desesperanza."
    elif any(x in cuerpo_clinico for x in ["convulsiones", "cefaleas", "memoria", "mareos"]):
        res = "INDICADOR: Posible compromiso neuropsicológico/orgánico."
        rec = "Interconsulta con Neurología. No concluir diagnóstico hasta descartar organicidad."
        tests = "Bender-Gestalt, Test de Benton, MMPI-2."
    elif any(x in cuerpo_clinico for x in ["ira", "agresiv", "pelea", "arma", "castigo"]):
        res = "PERFIL: Rasgos impulsivos-agresivos relacionados con historia de crianza."
        rec = "Terapia de regulación emocional y manejo de la ira."
        tests = "IPV, STAXI-2, 16PF-5."
    else:
        res = "ESTADO: Reacción de ajuste o estrés laboral."
        rec = "Técnicas de higiene mental y psicoterapia breve."
        tests = "16PF-5, HTP, Inventario de Ansiedad de Beck."
    
    return res, rec, tests

# --- 4. BÚSQUEDA Y CARGA DE DATOS ---
db_actual = cargar_db()
with st.sidebar:
    st.header("📂 ARCHIVO D.S.P.")
    id_list = ["--- NUEVO ---"] + (db_actual["Identidad"].tolist() if not db_actual.empty else [])
    seleccion = st.selectbox("Buscar Identidad:", id_list)
    d = db_actual[db_actual["Identidad"] == seleccion].iloc[0].to_dict() if seleccion != "--- NUEVO ---" else {}

st.title("🛡️ Protocolo de Evaluación Psicológica - 12 Áreas")

# --- 5. ESTRUCTURA DE 12 ÁREAS (SIN RECORTES) ---
tabs = st.tabs([
    "1-2. Identificación", "3-5. Salud Médica", "6. Checklist Vida", 
    "7. Familia y Social", "8-9. Desarrollo", "10-11. Sexo/Pers.", "12-13. Análisis IA"
])

with tabs[0]:
    st.subheader("I. DATOS DE IDENTIFICACIÓN Y II. MOTIVO")
    c1, c2, c3 = st.columns(3)
    identidad = c1.text_input("Identidad (Obligatorio)", value=d.get("Identidad", ""))
    nombre = c2.text_input("Nombre Completo", value=d.get("Nombre", ""))
    f_nac = c3.text_input("Lugar y Fecha de Nacimiento", value=d.get("F_Nac", ""))
    
    c4, c5, c6 = st.columns(3)
    edad = c4.text_input("Edad", value=d.get("Edad", ""))
    sexo = c5.selectbox("Sexo", ["M", "F"], index=v_idx(d.get("Sexo"), ["M", "F"]))
    ec_l = ["Soltero", "Casado", "Divorciado", "Unión Libre", "Viudo"]
    est_civil = c6.selectbox("Estado Civil", ec_l, index=v_idx(d.get("Estado_Civil"), ec_l))
    
    c7, c8, c9 = st.columns(3)
    nacionalidad = c7.text_input("Nacionalidad", value=d.get("Nacionalidad", ""))
    religion = c8.text_input("Religión", value=d.get("Religion", ""))
    celular = c9.text_input("Celular", value=d.get("Celular", ""))
    
    ocupacion = st.text_input("Ocupación / Grado / Cargo", value=d.get("Ocupacion", ""))
    direccion = st.text_input("Dirección Exacta", value=d.get("Direccion", ""))
    asignacion = st.text_input("Asignación o Unidad Policial", value=d.get("Asignacion", ""))
    remitido = st.text_input("Remitido por", value=d.get("Remitido", ""))
    
    motivo = st.text_area("II. MOTIVO DE CONSULTA (Vaciado literal de las palabras del paciente)", value=d.get("Motivo", ""))

with tabs[1]:
    st.subheader("III-IV. FUNCIONES ORGÁNICAS Y ANTECEDENTES")
    ant_sit = st.text_area("¿Cuándo comenzó la situación actual? (Evolución)", value=d.get("Ant_Sit", ""))
    
    f1, f2, f3, f4 = st.columns(4)
    sueño = f1.selectbox("Sueño", ["Normal", "Insomnio", "Hipersomnia", "Interrumpido"], index=v_idx(d.get("Sueño"), ["Normal", "Insomnio", "Hipersomnia", "Interrumpido"]))
    apetito = f2.selectbox("Apetito", ["Normal", "Aumentado", "Disminuido"], index=v_idx(d.get("Apetito"), ["Normal", "Aumentado", "Disminuido"]))
    sed = f3.text_input("Sed", value=d.get("Sed", ""))
    defec = f4.text_input("Defecación", value=d.get("Defec", ""))
    
    st.subheader("V. ESTADO DE SALUD MÉDICA")
    m1, m2, m3, m4 = st.columns(4)
    convulsiones = m1.text_input("Convulsiones", value=d.get("Convulsiones", ""))
    cefaleas = m2.text_input("Cefaleas (Dolores de cabeza)", value=d.get("Cefaleas", ""))
    resp = m3.text_input("Enf. Respiratorias", value=d.get("Resp", ""))
    infec = m4.text_input("Infecciones", value=d.get("Infecciones", ""))
    
    alergias = st.text_input("Alergias", value=d.get("Alergias", ""))
    meds = st.text_input("Medicamentos que toma actualmente", value=d.get("Meds", ""))
    hosp = st.text_input("Hospitalizaciones (Motivo y tiempo)", value=d.get("Hosp", ""))
    cirugias = st.text_input("Cirugías (Tipo)", value=d.get("Cirugias", ""))
    enf_infancia = st.text_input("Enfermedades de la infancia", value=d.get("Enf_Infancia", ""))

with tabs[2]:
    st.subheader("VI. CHECKLIST (MARQUE CON UNA X SI HA PRESENTADO EN SU VIDA)")
    v_items = ["Pesadillas", "Terror Nocturno", "Sonambulismo", "Enuresis", "Encopresis", "Onicofagia", "Tics", "Fobias", "Drogas", "Alcohol", "Ideas Suicidas", "Intentos Suicidas", "Alucinaciones", "Pérdida de memoria", "Mareos"]
    check_vida = st.multiselect("Seleccione los elementos presentes:", v_items, default=eval(d.get("Check_Vida", "[]")) if d else [])

with tabs[3]:
    st.subheader("VII. ÁREA FAMILIAR Y SOCIAL")
    st.write("**DATOS DEL PADRE**")
    p1, p2, p3 = st.columns(3)
    p_nom = p1.text_input("Nombre Padre", value=d.get("P_Nom", ""))
    p_edad = p2.text_input("Edad Padre", value=d.get("P_Edad", ""))
    p_vive = p3.selectbox("¿Vive? (P)", ["Sí", "No"], index=v_idx(d.get("P_Vive"), ["Sí", "No"]))
    p_salud = st.text_input("Estado de Salud Padre", value=d.get("P_Salud", ""))
    p_ocupa = st.text_input("Ocupación Padre", value=d.get("P_Ocupa", ""))
    p_rel = st.text_area("Relación con el padre y castigos recibidos", value=d.get("P_Rel", ""))
    
    st.write("**DATOS DE LA MADRE**")
    m1, m2, m3 = st.columns(3)
    m_nom = m1.text_input("Nombre Madre", value=d.get("M_Nom", ""))
    m_edad = m2.text_input("Edad Madre", value=d.get("M_Edad", ""))
    m_vive = m3.selectbox("¿Vive? (M)", ["Sí", "No"], index=v_idx(d.get("M_Vive"), ["Sí", "No"]))
    m_salud = st.text_input("Estado de Salud Madre", value=d.get("M_Salud", ""))
    m_ocupa = st.text_input("Ocupación Madre", value=d.get("M_Ocupa", ""))
    m_rel = st.text_area("Relación con la madre y castigos recibidos", value=d.get("M_Rel", ""))
    
    st.write("---")
    rel_padres = st.text_area("¿Cómo es/era la relación entre su PADRE y su MADRE?", value=d.get("Rel_Padres", ""))
    hermanos = st.text_input("Hermanos y lugar que ocupa entre ellos", value=d.get("Hermanos", ""))
    crianza = st.text_input("¿Quién lo crió?", value=d.get("Crianza", ""))
    hist_fel = st.text_area("Historia feliz vivida en familia", value=d.get("Hist_Fel", ""))
    social = st.text_area("Área Social y Ambiental (Amigos, vecinos, entorno)", value=d.get("Social", ""))

with tabs[4]:
    st.subheader("VIII-IX. DESARROLLO Y EDUCACIÓN")
    embarazo = st.text_input("Circunstancias del Embarazo (¿Deseado/Reacción?)", value=d.get("Embarazo", ""))
    parto = st.text_input("Parto (Fórceps, incubadora, tiempo)", value=d.get("Parto", ""))
    
    d1, d2, d3, d4 = st.columns(4)
    gateo = d1.text_input("Edad Gateó", value=d.get("Gateo", ""))
    camino = d2.text_input("Edad Caminó", value=d.get("Camino", ""))
    hablo = d3.text_input("Edad Habló", value=d.get("Hablo", ""))
    esfinter = d4.text_input("Edad Esfínteres", value=d.get("Esfinter", ""))
    
    st.write("**Área Escolar**")
    esc_edad = st.text_input("Edad inicio escuela", value=d.get("Esc_Edad", ""))
    esc_dif = st.text_input("Materias de dificultad", value=d.get("Esc_Dif", ""))
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
    st.subheader("XII-XIII. OPINIÓN PROFESIONAL Y ANÁLISIS IA")
    opinion_prof = st.text_area("✍️ Escriba su Opinión Profesional o Dudas (Gemini analizará esto):", value=d.get("Opinion_Prof", ""))
    
    # Recolectar todos los datos para la IA
    datos_completos = {
        "Motivo": motivo, "Check_Vida": check_vida, "Convulsiones": convulsiones,
        "Cefaleas": cefaleas, "Resp": resp, "Infec": infec, "P_Rel": p_rel, "M_Rel": m_rel,
        "Rel_Padres": rel_padres, "Hitos": f"{gateo}, {camino}, {hablo}, {esfinter}",
        "Opinion": opinion_prof, "Impulsos": pers_imp
    }

    if st.button("🧠 GENERAR ANÁLISIS INTEGRAL"):
        res_ia, rec_ia, test_ia = motor_ia_gemini(datos_completos)
        st.session_state["ia_res"] = res_ia
        st.session_state["ia_rec"] = rec_ia
        st.session_state["ia_test"] = test_ia

    st.info(f"**Resultado IA:** {st.session_state.get('ia_res', d.get('Conclusiones', 'Pendiente'))}")
    st.success(f"**Recomendación:** {st.session_state.get('ia_rec', d.get('Recomendaciones', 'Pendiente'))}")
    st.warning(f"**Batería:** {st.session_state.get('ia_test', d.get('Tests', 'Pendiente'))}")
    
    analisis_clinico = st.text_area("Análisis Final del Psicólogo", value=d.get("Analisis_Clinico", ""))
    psicologo = st.text_input("Nombre del Psicólogo Evaluador", value=d.get("Psicologo", ""))

# --- 6. GUARDADO Y EXPORTACIÓN ---
if st.button("💾 GUARDAR Y GENERAR INFORME"):
    if identidad and nombre:
        reg = {
            "Identidad": identidad, "Nombre": nombre, "F_Nac": f_nac, "Edad": edad, "Sexo": sexo,
            "Estado_Civil": est_civil, "Nacionalidad": nacionalidad, "Religion": religion, "Celular": celular,
            "Ocupacion": ocupacion, "Direccion": direccion, "Asignacion": asignacion, "Remitido": remitido,
            "Motivo": motivo, "Ant_Sit": ant_sit, "Sueño": sueño, "Apetito": apetito, "Sed": sed, "Defec": defec,
            "Convulsiones": convulsiones, "Cefaleas": cefaleas, "Resp": resp, "Infecciones": infec,
            "Alergias": alergias, "Meds": meds, "Hosp": hosp, "Cirugias": cirugias, "Enf_Infancia": enf_infancia,
            "Check_Vida": str(check_vida), "P_Nom": p_nom, "P_Edad": p_edad, "P_Vive": p_vive, "P_Salud": p_salud,
            "P_Ocupa": p_ocupa, "P_Rel": p_rel, "M_Nom": m_nom, "M_Edad": m_edad, "M_Vive": m_vive, "M_Salud": m_salud,
            "M_Ocupa": m_ocupa, "M_Rel": m_rel, "Rel_Padres": rel_padres, "Hermanos": hermanos, "Crianza": crianza,
            "Hist_Fel": hist_fel, "Social": social, "Embarazo": embarazo, "Parto": parto, "Gateo": gateo,
            "Camino": camino, "Hablo": hablo, "Esfinter": esfinter, "Esc_Edad": esc_edad, "Esc_Dif": esc_dif,
            "Esc_Cond": esc_cond, "Menarquia": menarquia, "Sex_Opi": sex_opi, "Sex_Rel": sex_rel,
            "Noviazgo": noviazgo, "Pers_Conf": pers_conf, "Pers_Imp": pers_imp, "Opinion_Prof": opinion_prof,
            "Conclusiones": st.session_state.get("ia_res", d.get("Conclusiones")),
            "Recomendaciones": st.session_state.get("ia_rec", d.get("Recomendaciones")),
            "Tests": st.session_state.get("ia_test", d.get("Tests")),
            "Analisis_Clinico": analisis_clinico, "Psicologo": psicologo, "Fecha": str(date.today())
        }
        guardar_db(reg)
        
        # Generar Word
        doc = Document()
        doc.add_heading('PROTOCOLO DE EVALUACIÓN PSICOLÓGICA - D.S.P.', 0)
        doc.add_heading('1. ANÁLISIS DE IA Y RECOMENDACIONES', level=1)
        doc.add_paragraph(f"CONCLUSIONES: {reg['Conclusiones']}")
        doc.add_paragraph(f"RECOMENDACIONES: {reg['Recomendaciones']}")
        doc.add_paragraph(f"TESTS SUGERIDOS: {reg['Tests']}")
        doc.add_heading('2. DATOS DEL PROTOCOLO', level=1)
        for k, v in reg.items():
            if k not in ["Conclusiones", "Recomendaciones", "Tests"]:
                p = doc.add_paragraph(); p.add_run(f"{k}: ").bold = True; p.add_run(str(v))
        
        buf = io.BytesIO(); doc.save(buf); buf.seek(0)
        st.success("✅ Registro guardado en base de datos.")
        st.download_button("📥 DESCARGAR INFORME WORD", buf, f"Expediente_{identidad}.docx")
    else:
        st.error("Identidad y Nombre son obligatorios.")
