import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN DE PRIVACIDAD ---
st.set_page_config(page_title="D.S.P. - Expedientes Privados", layout="wide")
DB_FILE = "DB_DSP_PRIVADO.xlsx"

def cargar_db():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()
    try:
        return pd.read_excel(DB_FILE).astype(str).replace('nan', '')
    except:
        return pd.DataFrame()

def guardar_db(datos_dict):
    df = cargar_db()
    # La Identidad es el código único.
    if not df.empty and "Identidad" in df.columns:
        df = df[df["Identidad"] != datos_dict["Identidad"]]
    nuevo_df = pd.DataFrame([datos_dict])
    df_final = pd.concat([df, nuevo_df], ignore_index=True)
    df_final.to_excel(DB_FILE, index=False)
    return df_final

# --- 2. GESTIÓN DE BÚSQUEDA ---
db_actual = cargar_db()

with st.sidebar:
    st.header("🔐 ACCESO PRIVADO")
    modo = st.radio("Acción:", ["Nuevo Registro", "Buscar por Identidad"])
    
    datos_previa = {}
    if modo == "Buscar por Identidad" and not db_actual.empty:
        id_busqueda = st.selectbox("Seleccione Identidad:", db_actual["Identidad"].tolist())
        datos_previa = db_actual[db_actual["Identidad"] == id_busqueda].iloc[0].to_dict()
        st.success(f"Expediente cargado: {id_busqueda}")

st.title(f"🛡️ Protocolo Clínico D.S.P.")

# --- 3. TABS DETALLADOS ---
t1, t2, t3, t4, t5, t6 = st.tabs(["I-II. Generales", "III-V. Salud", "VI. Familia", "VII-IX. Desarrollo", "X-XII. Informe Final", "🔒 Base de Datos"])

with t1:
    st.subheader("I. DATOS GENERALES")
    c1, c2 = st.columns(2)
    identidad = c1.text_input("NÚMERO DE IDENTIDAD (Código Único)", value=datos_previa.get("Identidad", ""))
    nombre = c2.text_input("Nombre Completo", value=datos_previa.get("Nombre", ""))
    
    c3, c4, c5 = st.columns(3)
    f_nac = c3.text_input("Lugar y Fecha Nacimiento", value=datos_previa.get("Lugar_Fecha_Nac", ""))
    edad = c4.text_input("Edad", value=datos_previa.get("Edad", ""))
    sexo = c5.selectbox("Sexo", ["M", "F"], index=0 if datos_previa.get("Sexo") == "M" else 1)
    
    c6, c7, c8 = st.columns(3)
    celular = c6.text_input("Celular", value=datos_previa.get("Celular", ""))
    ocupacion = c7.text_input("Ocupación", value=datos_previa.get("Ocupacion", ""))
    asignacion = c8.text_input("Asignación", value=datos_previa.get("Asignacion", ""))
    
    motivo = st.text_area("MOTIVO DE CONSULTA", value=datos_previa.get("Motivo", ""))

with t2:
    st.subheader("II. SALUD Y SÍNTOMAS")
    ant_sint = st.text_area("Desarrollo de síntomas", value=datos_previa.get("Ant_Situacion", ""))
    
    st.write("**Funciones Orgánicas**")
    f1, f2, f3, f4 = st.columns(4)
    sue = f1.text_input("Sueño", value=datos_previa.get("Sueño", ""))
    ape = f2.text_input("Apetito", value=datos_previa.get("Apetito", ""))
    sed = f3.text_input("Sed", value=datos_previa.get("Sed", ""))
    # CORRECCIÓN DE LA VARIABLE 'def' A 'defec_val'
    defec_val = f4.text_input("Defecación", value=datos_previa.get("Defecacion", ""))
    
    st.write("**Historial Médico**")
    alergias = st.text_input("Alergias", value=datos_previa.get("Alergias", ""))
    meds = st.text_input("Medicamentos", value=datos_previa.get("Medicamentos", ""))
    
    # Manejo seguro del checklist para evitar errores de eval()
    try:
        lista_def = eval(datos_previa.get("Checklist", "[]"))
    except:
        lista_def = []
        
    checklist = st.multiselect("Checklist de Riesgos:", 
                               ["Pesadillas", "Ideación Suicida", "Alucinaciones", "Drogas", "Ira"],
                               default=lista_def)

with t3:
    st.subheader("III. ÁREA FAMILIAR")
    padre_r = st.text_area("Relación y Castigos (Padre)", value=datos_previa.get("Padre_Rel", ""))
    madre_r = st.text_area("Relación y Castigos (Madre)", value=datos_previa.get("Madre_Rel", ""))
    historia_f = st.text_area("Historia familiar relevante", value=datos_previa.get("Historia_F", ""))

with t4:
    st.subheader("IV. DESARROLLO")
    embarazo = st.text_input("Embarazo (Circunstancias)", value=datos_previa.get("Embarazo", ""))
    parto = st.text_input("Parto (Tipo/Complicaciones)", value=datos_previa.get("Parto", ""))
    escolaridad = st.text_area("Historia Escolar", value=datos_previa.get("Escuela", ""))

with t5:
    st.subheader("V. INFORME FINAL (CON CONCLUSIONES Y TEST)")
    analisis = st.text_area("Análisis Clínico / Hallazgos IA", value=datos_previa.get("Analisis", ""))
    conclusiones = st.text_area("Conclusiones Clínicas", value=datos_previa.get("Conclusiones", ""))
    recomendaciones = st.text_area("Recomendaciones y Tests Sugeridos", value=datos_previa.get("Recomendaciones", ""))
    plan_t = st.text_area("Plan Terapéutico", value=datos_previa.get("Terapia", ""))
    
    st.divider()
    psicologo = st.text_input("Psicólogo Evaluador", value=datos_previa.get("Psicologo", ""))

with t6:
    st.subheader("🔒 Base de Datos Local")
    if not db_actual.empty:
        st.dataframe(db_actual)
        buf_ex = io.BytesIO()
        db_actual.to_excel(buf_ex, index=False)
        st.download_button("📥 Exportar Base Completa", buf_ex, "DSP_PRIVADO.xlsx")

# --- 4. GUARDADO ---
if st.button("💾 GUARDAR Y GENERAR INFORME"):
    if identidad and nombre:
        dict_final = {
            "Identidad": identidad, "Nombre": nombre, "Lugar_Fecha_Nac": f_nac, "Edad": edad,
            "Sexo": sexo, "Celular": celular, "Ocupacion": ocupacion, "Asignacion": asignacion,
            "Motivo": motivo, "Ant_Situacion": ant_sint, "Sueño": sue, "Apetito": ape, 
            "Sed": sed, "Defecacion": defec_val, "Alergias": alergias, "Medicamentos": meds,
            "Checklist": str(checklist), "Padre_Rel": padre_r, "Madre_Rel": madre_r, 
            "Historia_F": historia_f, "Embarazo": embarazo, "Parto": parto, "Escuela": escolaridad,
            "Analisis": analisis, "Conclusiones": conclusiones, "Recomendaciones": recomendaciones,
            "Terapia": plan_t, "Psicologo": psicologo, "Fecha_Mod": str(date.today())
        }
        
        guardar_db(dict_final)
        st.success(f"Expediente {identidad} actualizado correctamente.")
        
        # Generar Word
        doc = Document()
        doc.add_heading('INFORME PSICOLÓGICO CLÍNICO', 0)
        doc.add_paragraph(f"Identidad: {identidad}\nPaciente: {nombre}")
        doc.add_heading('Análisis Clínico', level=1); doc.add_paragraph(analisis)
        doc.add_heading('Conclusiones', level=1); doc.add_paragraph(conclusiones)
        doc.add_heading('Recomendaciones y Tests', level=1); doc.add_paragraph(recomendaciones)
        doc.add_heading('Plan Terapéutico', level=1); doc.add_paragraph(plan_t)
        
        buf_w = io.BytesIO()
        doc.save(buf_w)
        buf_w.seek(0)
        st.download_button("📥 Descargar Informe Word", buf_w, f"Informe_{identidad}.docx")
    else:
        st.error("Identidad y Nombre son obligatorios.")
