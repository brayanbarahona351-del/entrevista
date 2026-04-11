import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="D.S.P. - Protocolo Clínico Completo", layout="wide")
DB_FILE = "DB_DSP_SISTEMA_INTEGRAL.xlsx"

def cargar_db():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    try: return pd.read_excel(DB_FILE).astype(str).replace('nan', '')
    except: return pd.DataFrame()

def guardar_db(datos_dict):
    df = cargar_db()
    if not df.empty and "Identidad" in df.columns:
        df = df[df["Identidad"] != datos_dict["Identidad"]]
    df_final = pd.concat([df, pd.DataFrame([datos_dict])], ignore_index=True)
    df_final.to_excel(DB_FILE, index=False)
    return df_final

# --- BUSCADOR ---
db_actual = cargar_db()
datos_cargados = {}
with st.sidebar:
    st.header("🔍 BUSCAR EXPEDIENTE")
    if not db_actual.empty:
        lista_ids = ["--- NUEVO REGISTRO ---"] + db_actual["Identidad"].tolist()
        seleccion = st.selectbox("Seleccione Identidad:", lista_ids)
        if seleccion != "--- NUEVO REGISTRO ---":
            datos_cargados = db_actual[db_actual["Identidad"] == seleccion].iloc[0].to_dict()
            st.success(f"Cargado: {datos_cargados.get('Nombre')}")

st.title("🛡️ Protocolo Integral de Evaluación Psicológica - D.S.P.")

# --- TABS CON TODAS LAS PREGUNTAS DETALLADAS ---
t1, t2, t3, t4, t5, t6, t7 = st.tabs([
    "I-II. Generales", "III-V. Salud", "VI. Familia", 
    "VII-IX. Desarrollo", "X-XI. Sexualidad", "XII. Informe/IA", "📊 Base de Datos"
])

with t1:
    st.subheader("I. DATOS GENERALES")
    c1, c2, c3 = st.columns(3)
    identidad = c1.text_input("Identidad (Código Único)", value=datos_cargados.get("Identidad", ""))
    nombre = c2.text_input("Nombre Completo", value=datos_cargados.get("Nombre", ""))
    f_nac = c3.text_input("Lugar y Fecha de Nacimiento", value=datos_cargados.get("F_Nac", ""))
    
    c4, c5, c6 = st.columns(3)
    edad = c4.text_input("Edad", value=datos_cargados.get("Edad", ""))
    sexo = c5.selectbox("Sexo", ["M", "F"], index=0 if datos_cargados.get("Sexo")=="M" else 1)
    nacionalidad = c6.text_input("Nacionalidad", value=datos_cargados.get("Nacionalidad", ""))
    
    c7, c8, c9 = st.columns(3)
    est_civil = c7.text_input("Estado Civil", value=datos_cargados.get("Estado_Civil", ""))
    religion = c8.text_input("Religión", value=datos_cargados.get("Religion", ""))
    celular = c9.text_input("Celular", value=datos_cargados.get("Celular", ""))
    
    ocupacion = st.text_input("Ocupación Actual", value=datos_cargados.get("Ocupacion", ""))
    direccion = st.text_input("Dirección Actual", value=datos_cargados.get("Direccion", ""))
    asignacion = st.text_input("Asignación / Unidad", value=datos_cargados.get("Asignacion", ""))
    remitido = st.text_input("Remitido por", value=datos_cargados.get("Remitido", ""))
    
    st.subheader("II. MOTIVO DE CONSULTA")
    motivo = st.text_area("Describa el motivo de consulta según el paciente:", value=datos_cargados.get("Motivo", ""))

with t2:
    st.subheader("III. ANTECEDENTES DE LA SITUACIÓN")
    ant_sit = st.text_area("¿Cuándo se sintió bien por última vez? (Desarrollo de síntomas)", value=datos_cargados.get("Ant_Sit", ""))
    
    st.subheader("IV. FUNCIONES ORGÁNICAS")
    f1, f2, f3, f4 = st.columns(4)
    sue = f1.text_input("Sueño", value=datos_cargados.get("Sueño", ""))
    ape = f2.text_input("Apetito", value=datos_cargados.get("Apetito", ""))
    sed = f3.text_input("Sed", value=datos_cargados.get("Sed", ""))
    defec = f4.text_input("Defecación", value=datos_cargados.get("Defec", ""))
    
    st.subheader("V. ESTADO DE SALUD")
    alergias = st.text_input("¿Padece de alergias?", value=datos_cargados.get("Alergias", ""))
    meds = st.text_input("¿Toma algún medicamento?", value=datos_cargados.get("Meds", ""))
    enf_inf = st.text_input("Enfermedades en la infancia", value=datos_cargados.get("Enf_Inf", ""))
    cirugias = st.text_input("Intervenciones quirúrgicas", value=datos_cargados.get("Cirugias", ""))
    hosp = st.text_input("Hospitalizaciones (Motivo y tiempo)", value=datos_cargados.get("Hosp", ""))
    
    st.write("**Síntomas Neuroticos**")
    checklist = st.multiselect("Marque lo presentado:", 
                               ["Pesadillas", "Terror Nocturno", "Sonambulismo", "Berrinches", "Enuresis", "Onicofagia", "Tics", "Fobias", "Ideas suicidas"],
                               default=eval(datos_cargados.get("Checklist", "[]")) if datos_cargados else [])

with t3:
    st.subheader("VI. INFORMACIÓN FAMILIAR")
    p_nom = st.text_input("Nombre del Padre", value=datos_cargados.get("P_Nom", ""))
    p_rel = st.text_area("Relación con el padre y tipo de castigos", value=datos_cargados.get("P_Rel", ""))
    m_nom = st.text_input("Nombre de la Madre", value=datos_cargados.get("M_Nom", ""))
    m_rel = st.text_area("Relación con la madre y tipo de castigos", value=datos_cargados.get("M_Rel", ""))
    hermanos = st.text_input("Número de hermanos y posición que ocupa", value=datos_cargados.get("Hermanos", ""))
    crianza = st.text_input("¿Quién lo crió?", value=datos_cargados.get("Crianza", ""))
    hist_fel = st.text_area("Historia feliz vivida en familia", value=datos_cargados.get("Hist_Fel", ""))

with t4:
    st.subheader("VII-IX. DESARROLLO")
    embarazo = st.text_input("Circunstancia del embarazo (¿Planificado?)", value=datos_cargados.get("Embarazo", ""))
    parto = st.text_input("Tipo de parto (Fórceps, incubadora, etc.)", value=datos_cargados.get("Parto", ""))
    hitos = st.text_input("Desarrollo motor (¿A qué edad gateó/caminó?)", value=datos_cargados.get("Hitos", ""))
    esfinteres = st.text_input("Control de esfínteres (¿A qué edad?)", value=datos_cargados.get("Esfinteres", ""))
    
    st.write("**Datos Escolares**")
    esc_edad = st.text_input("¿A qué edad inició la escuela?", value=datos_cargados.get("Esc_Edad", ""))
    esc_dif = st.text_input("Materias de mayor dificultad", value=datos_cargados.get("Esc_Dif", ""))
    esc_apren = st.text_input("¿Cómo aprende más fácilmente?", value=datos_cargados.get("Esc_Apren", ""))
    esc_cond = st.text_area("Conducta escolar y rendimiento", value=datos_cargados.get("Esc_Cond", ""))

with t5:
    st.subheader("X-XI. HISTORIA SEXUAL Y PERSONALIDAD")
    sex_nov = st.text_input("Edad primer noviazgo", value=datos_cargados.get("Sex_Nov", ""))
    sex_rel = st.text_input("Edad primera relación sexual", value=datos_cargados.get("Sex_Rel", ""))
    sex_men = st.text_input("Menarquia (Mujeres) / Primera eyaculación (Hombres)", value=datos_cargados.get("Sex_Men", ""))
    sex_opi = st.text_area("Opinión sobre sexualidad, matrimonio y masturbación", value=datos_cargados.get("Sex_Opi", ""))
    
    st.write("**Rasgos de Personalidad**")
    pers_conf = st.text_input("¿Confía en las personas? (Celos, rencor)", value=datos_cargados.get("Pers_Conf", ""))
    pers_imp = st.text_input("¿Actos impulsivos? (¿Se arrepiente?)", value=datos_cargados.get("Pers_Imp", ""))

with t6:
    st.subheader("XII. INFORME FINAL Y RECOMENDACIONES")
    ana_ia = st.text_area("Análisis Clínico / Hallazgos IA", value=datos_cargados.get("Ana_IA", ""))
    conclusiones = st.text_area("Conclusiones Clínicas", value=datos_cargados.get("Conclusiones", ""))
    
    st.write("**Tests Recomendados**")
    test_sug = st.multiselect("Seleccione pruebas:", 
                               ["MMPI-2", "Beck (BDI-II)", "16PF-5", "SCL-90-R", "IPV"],
                               default=eval(datos_cargados.get("Tests", "[]")) if datos_cargados else [])
    
    recom = st.text_area("Recomendaciones Terapéuticas", value=datos_cargados.get("Recom", ""))
    psicologo = st.text_input("Psicólogo Evaluador", value=datos_cargados.get("Psicologo", ""))

with t7:
    st.subheader("📊 Base de Datos General")
    st.dataframe(db_actual)
    if not db_actual.empty:
        buf_ex = io.BytesIO()
        db_actual.to_excel(buf_ex, index=False)
        st.download_button("📥 Descargar Base Completa (Excel)", buf_ex, "DSP_DB_MASTER.xlsx")

# --- GUARDADO E IMPRESIÓN ---
if st.button("💾 GUARDAR Y GENERAR EXPEDIENTE"):
    if identidad and nombre:
        dict_guardar = {
            "Identidad": identidad, "Nombre": nombre, "F_Nac": f_nac, "Edad": edad, "Sexo": sexo,
            "Nacionalidad": nacionalidad, "Estado_Civil": est_civil, "Religion": religion,
            "Celular": celular, "Ocupacion": ocupacion, "Direccion": direccion, "Asignacion": asignacion,
            "Remitido": remitido, "Motivo": motivo, "Ant_Sit": ant_sit, "Sueño": sue, "Apetito": ape,
            "Sed": sed, "Defec": defec, "Alergias": alergias, "Meds": meds, "Enf_Inf": enf_inf,
            "Cirugias": cirugias, "Hosp": hosp, "Checklist": str(checklist), "P_Nom": p_nom,
            "P_Rel": p_rel, "M_Nom": m_nom, "M_Rel": m_rel, "Hermanos": hermanos, "Crianza": crianza,
            "Hist_Fel": hist_fel, "Embarazo": embarazo, "Parto": parto, "Hitos": hitos,
            "Esfinteres": esfinteres, "Esc_Edad": esc_edad, "Esc_Dif": esc_dif, "Esc_Apren": esc_apren,
            "Esc_Cond": esc_cond, "Sex_Nov": sex_nov, "Sex_Rel": sex_rel, "Sex_Men": sex_men,
            "Sex_Opi": sex_opi, "Pers_Conf": pers_conf, "Pers_Imp": pers_imp, "Ana_IA": ana_ia,
            "Conclusiones": conclusiones, "Tests": str(test_sug), "Recom": recom, "Psicologo": psicologo
        }
        guardar_db(dict_guardar)
        st.success("✅ Datos guardados en la Base de Datos.")

        # WORD: PROTOCOLO COMPLETO PREGUNTA/RESPUESTA
        doc = Document()
        doc.add_heading('PROTOCOLO CLÍNICO Y EVALUACIÓN - D.S.P.', 0)
        
        for k, v in dict_guardar.items():
            p = doc.add_paragraph()
            p.add_run(f"{k.replace('_', ' ')}: ").bold = True
            p.add_run(str(v))
            
        buf_w = io.BytesIO()
        doc.save(buf_w)
        buf_w.seek(0)
        st.download_button("📥 Descargar Word Completo", buf_w, f"Protocolo_{identidad}.docx")
    else:
        st.error("Identidad y Nombre obligatorios.")
