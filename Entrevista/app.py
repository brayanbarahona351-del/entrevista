import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="D.S.P. Honduras - Protocolo Integral", layout="wide")
DB_FILE = "DB_DSP_SISTEMA_COMPLETO.xlsx"

# --- 2. FUNCIONES DE BASE DE DATOS ---
def cargar_db():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    try: return pd.read_excel(DB_FILE).astype(str).replace('nan', '')
    except: return pd.DataFrame()

def guardar_db(datos_dict):
    df = cargar_db()
    if not df.empty and "Identidad" in df.columns:
        # Evita duplicados: Elimina la versión vieja antes de insertar la nueva
        df = df[df["Identidad"] != str(datos_dict["Identidad"])]
    df_final = pd.concat([df, pd.DataFrame([datos_dict])], ignore_index=True)
    df_final.to_excel(DB_FILE, index=False)
    return df_final

def validar_idx(opcion, lista):
    """Evita el TypeError: Si el dato no está en la lista, selecciona el índice 0"""
    try: return lista.index(opcion)
    except: return 0

# --- 3. MOTOR DE ANÁLISIS IA (RECOMENDACIONES, TESTS Y SEGUIMIENTO) ---
def motor_clinico_ia(motivo, sintomas):
    texto = (str(motivo) + str(sintomas)).lower()
    
    # Lógica de detección de perfiles
    if any(x in texto for x in ["suicid", "morir", "matar", "vida", "solo"]):
        concl = "RIESGO CRÍTICO: El paciente presenta indicadores de ideación autolítica activa y desesperanza clínica."
        segui = "PLAN DE SEGUIMIENTO: Intervención en crisis inmediata. Contrato de vida. Sesiones de apoyo familiar. Remisión urgente a Psiquiatría."
        tests = (
            "BATERÍA DE TESTS RECOMENDADA:\n"
            "1. Beck (Depresión) [TU ENLACE]: https://bit.ly/test-beck\n"
            "2. SCL-90-R [TU ENLACE]: https://bit.ly/scl-90\n"
            "3. SUGERENCIA ADICIONAL: Inventario de Desesperanza de Beck (BHS) para cuantificar riesgo suicida.\n"
            "4. SUGERENCIA ADICIONAL: Escala de Ideación Suicida de Beck (SSI)."
        )
    elif any(x in texto for x in ["ira", "enojo", "golpe", "arma", "pelea", "violencia"]):
        concl = "PERFIL CONDUCTUAL: Dificultades graves en el control de impulsos y gestión de la agresividad."
        segui = "PLAN DE SEGUIMIENTO: Entrenamiento en control de impulsos (Stop-Think-Act). Terapia de manejo de ira. Evaluación de portación de armas."
        tests = (
            "BATERÍA DE TESTS RECOMENDADA:\n"
            "1. MMPI-2 (Personalidad) [TU ENLACE]: https://bit.ly/mmpi-2-ref\n"
            "2. IPV (Impulsividad) [TU ENLACE]: https://bit.ly/ipv-test\n"
            "3. SUGERENCIA ADICIONAL: Inventario STAXI-2 para medir estado y rasgo de ira.\n"
            "4. SUGERENCIA ADICIONAL: Test de la Figura Humana de Machover (Análisis proyectivo)."
        )
    else:
        concl = "PERFIL GENERAL: Sintomatología ansiosa o de estrés laboral dentro de rangos moderados."
        segui = "PLAN DE SEGUIMIENTO: Higiene del sueño, técnicas de relajación diafragmática y monitoreo quincenal."
        tests = (
            "BATERÍA DE TESTS RECOMENDADA:\n"
            "1. 16PF-5 [TU ENLACE]: https://bit.ly/16pf5-ref\n"
            "2. SUGERENCIA ADICIONAL: Inventario de Ansiedad de Beck (BAI).\n"
            "3. SUGERENCIA ADICIONAL: Test HTP (Casa-Árbol-Persona)."
        )
    return concl, segui, tests

# --- 4. CARGA DE DATOS EXISTENTES ---
db_actual = cargar_db()
with st.sidebar:
    st.header("🔍 BUSCADOR DE EXPEDIENTES")
    id_lista = ["--- REGISTRAR NUEVO ---"] + (db_actual["Identidad"].tolist() if not db_actual.empty else [])
    seleccion = st.selectbox("Seleccionar Identidad:", id_lista)
    datos_c = db_actual[db_actual["Identidad"] == seleccion].iloc[0].to_dict() if seleccion != "--- REGISTRAR NUEVO ---" else {}

st.title("🛡️ Protocolo Integral de Evaluación Psicológica - D.S.P.")

# --- 5. TABS: TODAS LAS PREGUNTAS SIN EXCEPCIÓN ---
t1, t2, t3, t4, t5, t6, t7, t8 = st.tabs([
    "I. Identificación", "II. Motivo/Antecedentes", "III-IV. Orgánicas", 
    "V-VI. Salud/Síntomas", "VII. Familia", "VIII-IX. Desarrollo", 
    "X-XI. Sexo/Personalidad", "XII. ANÁLISIS E IA"
])

with t1:
    st.subheader("I. DATOS DE IDENTIFICACIÓN")
    c1, c2, c3 = st.columns(3)
    id_pac = c1.text_input("1. Identidad", value=datos_c.get("Identidad", ""))
    nom_pac = c2.text_input("2. Nombre", value=datos_c.get("Nombre", ""))
    f_nac = c3.text_input("3. Fecha/Lugar Nacimiento", value=datos_c.get("F_Nac", ""))
    edad = st.text_input("4. Edad", value=datos_c.get("Edad", ""))
    sex_l = ["M", "F"]; sexo = st.selectbox("5. Sexo", sex_l, index=validar_idx(datos_c.get("Sexo"), sex_l))
    ec_l = ["Soltero", "Casado", "Divorciado", "Unión Libre", "Viudo"]; est_civil = st.selectbox("6. Estado Civil", ec_l, index=validar_idx(datos_c.get("Estado_Civil"), ec_l))
    nacionalidad = st.text_input("7. Nacionalidad", value=datos_c.get("Nacionalidad", ""))
    religion = st.text_input("8. Religión", value=datos_c.get("Religion", ""))
    celular = st.text_input("9. Celular", value=datos_c.get("Celular", ""))
    ocupacion = st.text_input("10. Ocupación", value=datos_c.get("Ocupacion", ""))
    direccion = st.text_input("11. Dirección", value=datos_c.get("Direccion", ""))
    asignacion = st.text_input("12. Asignación/Unidad", value=datos_c.get("Asignacion", ""))
    remitido = st.text_input("13. Remitido por", value=datos_c.get("Remitido", ""))

with t2:
    st.subheader("II. MOTIVO Y ANTECEDENTES")
    motivo = st.text_area("14. Motivo de Consulta (Literal)", value=datos_c.get("Motivo", ""))
    ant_sit = st.text_area("15. ¿Cuándo se sintió bien por última vez? (Antecedentes)", value=datos_c.get("Ant_Sit", ""))

with t3:
    st.subheader("III-IV. FUNCIONES ORGÁNICAS")
    c10, c11, c12, c13 = st.columns(4)
    s_l = ["Normal", "Insomnio", "Hipersomnia", "Interrumpido"]; sueño = c10.selectbox("16. Sueño", s_l, index=validar_idx(datos_c.get("Sueño", "Normal"), s_l))
    a_l = ["Normal", "Aumentado", "Disminuido"]; apetito = c11.selectbox("17. Apetito", a_l, index=validar_idx(datos_c.get("Apetito", "Normal"), a_l))
    sed = c12.text_input("18. Sed", value=datos_c.get("Sed", ""))
    defec = c13.text_input("19. Defecación", value=datos_c.get("Defec", ""))

with t4:
    st.subheader("V-VI. ESTADO DE SALUD Y SÍNTOMAS")
    alergias = st.text_input("20. Alergias", value=datos_c.get("Alergias", ""))
    meds = st.text_input("21. Medicamentos", value=datos_c.get("Meds", ""))
    hosp = st.text_input("22. Hospitalizaciones", value=datos_c.get("Hosp", ""))
    enf_inf = st.text_input("23. Enfermedades infancia", value=datos_c.get("Enf_Inf", ""))
    cirugias = st.text_input("24. Cirugías", value=datos_c.get("Cirugias", ""))
    st.write("**25. Checklist de Síntomas Neuroticos**")
    s_list = ["Pesadillas", "Terror Nocturno", "Sonambulismo", "Enuresis", "Encopresis", "Onicofagia", "Tics", "Fobias", "Drogas", "Alcohol", "Ideas Suicidas"]
    sintomas = st.multiselect("Marque presentes:", s_list, default=eval(datos_c.get("Sintomas", "[]")) if datos_c else [])

with t5:
    st.subheader("VII. INFORMACIÓN FAMILIAR")
    p_nom = st.text_input("26. Nombre Padre", value=datos_c.get("P_Nom", ""))
    p_rel = st.text_area("27. Relación Padre y Castigos", value=datos_c.get("P_Rel", ""))
    m_nom = st.text_input("28. Nombre Madre", value=datos_c.get("M_Nom", ""))
    m_rel = st.text_area("29. Relación Madre y Castigos", value=datos_c.get("M_Rel", ""))
    hermanos = st.text_input("30. Hermanos y lugar que ocupa", value=datos_c.get("Hermanos", ""))
    crianza = st.text_input("31. ¿Quién lo crió?", value=datos_c.get("Crianza", ""))
    hist_fel = st.text_area("32. Historia familiar feliz", value=datos_c.get("Hist_Fel", ""))

with t6:
    st.subheader("VIII-IX. DESARROLLO")
    embarazo = st.text_input("33. Embarazo (¿Deseado/Reacción?)", value=datos_c.get("Embarazo", ""))
    parto = st.text_input("34. Parto (Incubadora/Fórceps)", value=datos_c.get("Parto", ""))
    gateo = st.text_input("35. Edad gateó", value=datos_c.get("Gateo", ""))
    camino = st.text_input("36. Edad caminó", value=datos_c.get("Camino", ""))
    hablo = st.text_input("37. Edad habló", value=datos_c.get("Hablo", ""))
    esfinter = st.text_input("38. Edad esfínteres", value=datos_c.get("Esfinter", ""))
    esc_edad = st.text_input("39. Edad inicio escuela", value=datos_c.get("Esc_Edad", ""))
    esc_dif = st.text_input("40. Materias dificultad", value=datos_c.get("Esc_Dif", ""))
    esc_cond = st.text_area("41. Conducta y rendimiento", value=datos_c.get("Esc_Cond", ""))

with t7:
    st.subheader("X-XI. SEXUALIDAD Y PERSONALIDAD")
    menarquia = st.text_input("42. Menarquia/Eyaculación", value=datos_c.get("Menarquia", ""))
    sex_opi = st.text_area("43. Opinión Sexualidad/Matrimonio", value=datos_c.get("Sex_Opi", ""))
    sex_rel = st.text_input("44. Edad primera relación", value=datos_c.get("Sex_Rel", ""))
    noviazgo = st.text_input("45. Edad primer noviazgo", value=datos_c.get("Noviazgo", ""))
    pers_conf = st.text_input("46. ¿Confía en personas? (Rencor/Celos)", value=datos_c.get("Pers_Conf", ""))
    pers_imp = st.text_input("47. ¿Actos impulsivos? (¿Arrepentimiento?)", value=datos_c.get("Pers_Imp", ""))

with t8:
    st.subheader("XII. ANÁLISIS INTEGRAL E IA")
    if st.button("🧠 PROCESAR INFORME CLÍNICO E IA"):
        c_ia, s_ia, t_ia = motor_clinico_ia(motivo, sintomas)
        st.session_state["ia_concl"] = c_ia
        st.session_state["ia_segui"] = s_ia
        st.session_state["ia_tests"] = t_ia

    analisis_prof = st.text_area("Análisis Profesional", value=datos_c.get("Analisis", ""))
    concl_ia = st.text_area("Conclusiones Clínicas", value=st.session_state.get("ia_concl", datos_c.get("Concl", "")))
    segui_ia = st.text_area("Recomendaciones y Seguimiento", value=st.session_state.get("ia_segui", datos_c.get("Recom", "")))
    tests_ia = st.text_area("Tests Sugeridos (Base + Adicionales)", value=st.session_state.get("ia_tests", datos_c.get("Tests", "")))
    psicologo = st.text_input("Psicólogo Evaluador", value=datos_c.get("Psicologo", ""))

# --- 6. GUARDADO FINAL ---
if st.button("💾 GUARDAR Y GENERAR DOCUMENTO"):
    if id_pac and nom_pac:
        reg = {
            "Identidad": id_pac, "Nombre": nom_pac, "F_Nac": f_nac, "Edad": edad, "Sexo": sexo,
            "Estado_Civil": est_civil, "Nacionalidad": nacionalidad, "Religion": religion,
            "Celular": celular, "Ocupacion": ocupacion, "Direccion": direccion, "Asignacion": asignacion,
            "Remitido": remitido, "Motivo": motivo, "Ant_Sit": ant_sit, "Sueño": sueño, "Apetito": apetito,
            "Sed": sed, "Defec": defec, "Alergias": alergias, "Meds": meds, "Hosp": hosp, "Enf_Inf": enf_inf,
            "Cirugias": cirugias, "Sintomas": str(sintomas), "P_Nom": p_nom, "P_Rel": p_rel, "M_Nom": m_nom,
            "M_Rel": m_rel, "Hermanos": hermanos, "Crianza": crianza, "Hist_Fel": hist_fel, "Embarazo": embarazo,
            "Parto": parto, "Gateo": gateo, "Camino": camino, "Hablo": hablo, "Esfinter": esfinter,
            "Esc_Edad": esc_edad, "Esc_Dif": esc_dif, "Esc_Cond": esc_cond, "Menarquia": menarquia,
            "Sex_Opi": sex_opi, "Sex_Rel": sex_rel, "Noviazgo": noviazgo, "Pers_Conf": pers_conf,
            "Pers_Imp": pers_imp, "Analisis": analisis_prof, "Concl": concl_ia, "Recom": segui_ia,
            "Tests": tests_ia, "Psicologo": psicologo, "Fecha": str(date.today())
        }
        guardar_db(reg)
        st.success("✅ Datos guardados y expediente actualizado.")
        
        doc = Document()
        doc.add_heading('PROTOCOLO CLÍNICO D.S.P. - HONDURAS', 0)
        for k, v in reg.items():
            p = doc.add_paragraph()
            p.add_run(f"{k}: ").bold = True
            p.add_run(str(v))
        
        buf = io.BytesIO(); doc.save(buf); buf.seek(0)
        st.download_button("📥 DESCARGAR PROTOCOLO EN WORD", buf, f"Expediente_{id_pac}.docx")
    else:
        st.error("Identidad y Nombre son obligatorios.")
