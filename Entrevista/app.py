import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN Y BASE DE DATOS ---
st.set_page_config(page_title="D.S.P. - Sistema de Evaluación Integral", layout="wide")
DB_FILE = "DB_DSP_MAESTRO.xlsx"

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
def generar_recomendaciones_ia(motivo, sintomas):
    texto = (str(motivo) + str(sintomas)).lower()
    concl = ""
    recom_seguimiento = ""
    tests_lista = []

    # LÓGICA DE ANÁLISIS POR CATEGORÍA
    if any(x in texto for x in ["suicid", "morir", "muerte", "matar", "solo"]):
        concl = "RIESGO CRÍTICO: Indicadores de ideación autolítica y sintomatología depresiva grave."
        recom_seguimiento = "Seguimiento: Intervención en crisis inmediata, vigilancia de red de apoyo y terapia semanal."
        tests_lista = [
            "Beck (BDI-II) [DESCARGA]: https://bit.ly/test-beck",
            "SCL-90-R [REFERENCIA]: https://bit.ly/scl-90",
            "NUEVA SUGERENCIA: Escala de Desesperanza de Beck (BHS) para medir riesgo suicida a largo plazo.",
            "NUEVA SUGERENCIA: Test de Plutchik (Impulsividad) para evaluar control de actos."
        ]
    elif any(x in texto for x in ["ira", "enojo", "arma", "pelea", "agresiv"]):
        concl = "INDICADOR CONDUCTUAL: Dificultad en el control de impulsos y posible rasgo de personalidad explosiva."
        recom_seguimiento = "Seguimiento: Terapia cognitivo-conductual enfocada en manejo de la ira y asertividad."
        tests_lista = [
            "MMPI-2 [REFERENCIA]: https://bit.ly/mmpi-2-ref",
            "IPV (Vendedores/Impulsos) [REFERENCIA]: https://bit.ly/ipv-test",
            "NUEVA SUGERENCIA: Inventario de Expresión de Ira Estado-Rasgo (STAXI-2).",
            "NUEVA SUGERENCIA: Test de Bender para descartar organicidad en la conducta agresiva."
        ]
    elif any(x in texto for x in ["nervio", "ansiedad", "miedo", "temblor", "sueño"]):
        concl = "INDICADOR CLÍNICO: Trastorno de ansiedad generalizada o estrés post-traumático."
        recom_seguimiento = "Seguimiento: Técnicas de relajación progresiva y desensibilización sistemática."
        tests_lista = [
            "STAI (Ansiedad) [DESCARGA]: https://bit.ly/stai-ref",
            "NUEVA SUGERENCIA: Inventario de Ansiedad de Beck (BAI).",
            "NUEVA SUGERENCIA: Test de Zung para Ansiedad."
        ]
    else:
        concl = "EVALUACIÓN DE RUTINA: No se observan indicadores de patología grave inmediata."
        recom_seguimiento = "Seguimiento: Monitoreo trimestral de salud mental ocupacional."
        tests_lista = [
            "16PF-5 [REFERENCIA]: https://bit.ly/16pf5-ref",
            "NUEVA SUGERENCIA: Test HTP (Casa-Árbol-Persona) para análisis proyectivo de personalidad."
        ]

    return concl, recom_seguimiento, "\n".join(tests_lista)

# --- 3. INTERFAZ Y BÚSQUEDA ---
db_actual = cargar_db()
with st.sidebar:
    st.header("🔍 BUSCADOR D.S.P.")
    id_list = ["--- REGISTRAR NUEVO ---"]
    if not db_actual.empty: id_list += db_actual["Identidad"].tolist()
    seleccion = st.selectbox("Seleccionar por Identidad:", id_list)
    datos_cargados = {}
    if seleccion != "--- REGISTRAR NUEVO ---":
        datos_cargados = db_actual[db_actual["Identidad"] == seleccion].iloc[0].to_dict()

st.title("🛡️ Protocolo de Entrevista e Informe Clínico D.S.P.")

# --- 4. CUESTIONARIO COMPLETO (SIN RECORTES) ---
t1, t2, t3, t4, t5, t6, t7 = st.tabs([
    "I-II. Generales", "III-V. Salud", "VI. Familia", "VII-IX. Desarrollo", 
    "X-XI. Sexualidad", "XII. ANÁLISIS IA", "📊 Base de Datos"
])

with t1:
    st.subheader("I. DATOS GENERALES")
    c1, c2, c3 = st.columns(3)
    identidad = c1.text_input("Número de Identidad", value=datos_cargados.get("Identidad", ""))
    nombre = c2.text_input("Nombre Completo", value=datos_cargados.get("Nombre", ""))
    f_nac = c3.text_input("Fecha y Lugar Nacimiento", value=datos_cargados.get("F_Nac", ""))
    edad = st.text_input("Edad", value=datos_cargados.get("Edad", ""))
    motivo = st.text_area("II. MOTIVO DE CONSULTA (Literal)", value=datos_cargados.get("Motivo", ""))

with t2:
    st.subheader("III-V. ORGÁNICAS Y SALUD")
    f1, f2, f3, f4 = st.columns(4)
    sue = f1.text_input("Sueño", value=datos_cargados.get("Sueño", ""))
    ape = f2.text_input("Apetito", value=datos_cargados.get("Apetito", ""))
    sed = f3.text_input("Sed", value=datos_cargados.get("Sed", ""))
    defec = f4.text_input("Defecación", value=datos_cargados.get("Defec", ""))
    hosp = st.text_input("Hospitalizaciones", value=datos_cargados.get("Hosp", ""))
    sintomas = st.multiselect("Checklist Síntomas:", ["Ideas Suicidas", "Ira", "Pesadillas", "Drogas", "Alcohol"], 
                              default=eval(datos_cargados.get("Sintomas", "[]")) if datos_cargados else [])

with t3:
    st.subheader("VI. ÁREA FAMILIAR")
    p_rel = st.text_area("Relación Padre y Castigos", value=datos_cargados.get("P_Rel", ""))
    m_rel = st.text_area("Relación Madre y Castigos", value=datos_cargados.get("M_Rel", ""))
    hist_fel = st.text_area("Historia familiar feliz", value=datos_cargados.get("Hist_Fel", ""))

with t4:
    st.subheader("VII-IX. DESARROLLO")
    parto = st.text_input("Embarazo / Parto (Incubadora/Fórceps)", value=datos_cargados.get("Parto", ""))
    hitos = st.text_input("Hitos (Edad gateó/caminó)", value=datos_cargados.get("Hitos", ""))
    esfinter = st.text_input("Control de esfínteres (Edad)", value=datos_cargados.get("Esfinter", ""))
    escuela = st.text_area("Conducta y rendimiento escolar", value=datos_cargados.get("Escuela", ""))

with t5:
    st.subheader("X-XI. SEXUALIDAD Y PERSONALIDAD")
    sex_men = st.text_input("Menarquia/Eyaculación (Edad)", value=datos_cargados.get("Sex_Men", ""))
    sex_opi = st.text_area("Opinión sobre sexualidad", value=datos_cargados.get("Sex_Opi", ""))
    pers_conf = st.text_input("¿Confía en las personas? (Celos/Rencor)", value=datos_cargados.get("Pers_Conf", ""))
    pers_imp = st.text_input("¿Actos impulsivos?", value=datos_cargados.get("Pers_Imp", ""))

with t6:
    st.subheader("XII. ANÁLISIS DE LA IA Y CIERRE PROFESIONAL")
    
    if st.button("🧠 GENERAR ANÁLISIS INTEGRAL (TESTS Y SEGUIMIENTO)"):
        c_ia, r_ia, t_ia = generar_recomendaciones_ia(motivo, sintomas)
        st.session_state["ia_concl"] = c_ia
        st.session_state["ia_recom"] = r_ia
        st.session_state["ia_tests"] = t_ia

    concl_f = st.text_area("Conclusiones Clínicas", value=st.session_state.get("ia_concl", datos_cargados.get("Concl", "")))
    recom_f = st.text_area("Recomendaciones de Seguimiento", value=st.session_state.get("ia_recom", datos_cargados.get("Recom", "")))
    tests_f = st.text_area("Tests Sugeridos (Base y Adicionales)", value=st.session_state.get("ia_tests", datos_cargados.get("Tests", "")))
    
    psicologo = st.text_input("Psicólogo Evaluador", value=datos_cargados.get("Psicologo", ""))

with t7:
    st.subheader("📊 Base de Datos General")
    st.dataframe(db_actual)

# --- 5. GUARDADO ---
if st.button("💾 GUARDAR Y GENERAR EXPEDIENTE WORD"):
    if identidad and nombre:
        dict_final = {
            "Identidad": identidad, "Nombre": nombre, "F_Nac": f_nac, "Edad": edad, "Motivo": motivo,
            "Sueño": sue, "Apetito": ape, "Sed": sed, "Defec": defec, "Hosp": hosp, "Sintomas": str(sintomas),
            "P_Rel": p_rel, "M_Rel": m_rel, "Hist_Fel": hist_fel, "Parto": parto, "Hitos": hitos,
            "Esfinter": esfinter, "Escuela": escuela, "Sex_Men": sex_men, "Sex_Opi": sex_opi,
            "Pers_Conf": pers_conf, "Pers_Imp": pers_imp, "Concl": concl_f, "Recom": recom_f,
            "Tests": tests_f, "Psicologo": psicologo, "Fecha": str(date.today())
        }
        guardar_db(dict_final)
        st.success("✅ Guardado correctamente sin duplicados.")
        
        doc = Document()
        doc.add_heading('EXPEDIENTE PSICOLÓGICO - D.S.P.', 0)
        for k, v in dict_final.items():
            p = doc.add_paragraph()
            p.add_run(f"{k}: ").bold = True
            p.add_run(str(v))
        
        buf = io.BytesIO(); doc.save(buf); buf.seek(0)
        st.download_button("📥 Descargar Word", buf, f"Expediente_{identidad}.docx")
