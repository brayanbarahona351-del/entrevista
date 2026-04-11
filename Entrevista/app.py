import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Expediente Clínico D.S.P.", layout="wide")
DB_FILE = "base_datos_dsp_detallada.xlsx"

# --- 2. MOTOR DE BASE DE DATOS DINÁMICA ---
def cargar_db():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    try:
        df = pd.read_excel(DB_FILE)
        return df.astype(str).replace('nan', '')
    except: return pd.DataFrame()

def guardar_db(datos_dict):
    df = cargar_db()
    # Si el paciente ya existe por Identidad, actualizamos
    if not df.empty and "Identidad" in df.columns and datos_dict["Identidad"] in df["Identidad"].values:
        df = df[df["Identidad"] != datos_dict["Identidad"]]
    
    nuevo_df = pd.DataFrame([datos_dict])
    df = pd.concat([df, nuevo_df], ignore_index=True)
    df.to_excel(DB_FILE, index=False)

# --- 3. INTERFAZ ---
st.title("📋 Protocolo de Evaluación Psicológica - D.S.P.")
st.markdown("---")

db_actual = cargar_db()
with st.sidebar:
    st.header("📂 Gestión de Expedientes")
    sel = st.selectbox("Seleccionar Registro:", ["NUEVO REGISTRO"] + (db_actual["Nombre"].tolist() if not db_actual.empty else []))
    p = db_actual[db_actual["Nombre"] == sel].iloc[0].to_dict() if sel != "NUEVO REGISTRO" else {}

# Organizado por las secciones exactas de tu solicitud
tabs = st.tabs(["I-II. Generales", "III-V. Salud y Síntomas", "VI. Familia", "VII-IX. Desarrollo", "X-XII. Sexual y Personalidad"])

# --- TAB 1: DATOS GENERALES ---
with tabs[0]:
    st.subheader("I. DATOS GENERALES")
    c1, c2, c3 = st.columns(3)
    nombre = c1.text_input("Nombre Completo", value=p.get("Nombre", ""))
    identidad = c2.text_input("Identidad", value=p.get("Identidad", ""))
    f_nac = c3.text_input("Lugar y Fecha de Nacimiento", value=p.get("Fecha_Nac", ""))
    
    c4, c5, c6 = st.columns(3)
    nacionalidad = c4.text_input("Nacionalidad", value=p.get("Nacionalidad", ""))
    sexo = c5.selectbox("Sexo", ["M", "F"], index=0 if p.get("Sexo") != "F" else 1)
    edad = c6.text_input("Edad", value=p.get("Edad", ""))
    
    c7, c8, c9 = st.columns(3)
    religion = c7.text_input("Religión", value=p.get("Religion", ""))
    estado_civil = c8.text_input("Estado Civil", value=p.get("Estado_Civil", ""))
    celular = c9.text_input("Celular", value=p.get("Celular", ""))
    
    c10, c11, c12 = st.columns(3)
    ocupacion = c10.text_input("Ocupación Actual", value=p.get("Ocupacion", ""))
    asignacion = c11.text_input("Asignación", value=p.get("Asignacion", ""))
    servicio_militar = c12.selectbox("¿Prestó servicio militar?", ["Sí", "No"], index=1 if p.get("Servicio_Militar") == "No" else 0)
    
    direccion = st.text_input("Dirección Actual", value=p.get("Direccion", ""))
    nivel_edu = st.text_input("Nivel Educativo", value=p.get("Nivel_Edu", ""))
    remitido = st.text_input("Remitido por", value=p.get("Remitido", ""))
    
    c13, c14 = st.columns(2)
    pasatiempos = c13.text_input("Pasatiempos", value=p.get("Pasatiempos", ""))
    deportes = c14.text_input("Deportes", value=p.get("Deportes", ""))

    st.subheader("II. MOTIVO DE CONSULTA")
    motivo = st.text_area("Describa el motivo", value=p.get("Motivo", ""), height=100)

# --- TAB 2: SALUD Y SÍNTOMAS ---
with tabs[1]:
    st.subheader("III. ANTECEDENTES CLÍNICOS")
    ant_situacion = st.text_area("¿Cuándo se sintió bien por última vez? / Desarrollo de síntomas", value=p.get("Ant_Situacion", ""))
    
    st.write("**Funciones Orgánicas**")
    c15, c16, c17, c18 = st.columns(4)
    sueño = c15.text_input("Sueño", value=p.get("Sueño", ""))
    apetito = c16.text_input("Apetito", value=p.get("Apetito", ""))
    sed = c17.text_input("Sed", value=p.get("Sed", ""))
    defecacion = c18.text_input("Defecación", value=p.get("Defecacion", ""))
    
    c19, c20 = st.columns(2)
    alergias = c19.text_input("Alergias (Especifique)", value=p.get("Alergias", ""))
    meds = c20.text_input("Medicamentos regulares (Para qué?)", value=p.get("Medicamentos", ""))
    
    c21, c22, c23 = st.columns(3)
    enf_infancia = c21.text_input("Enfermedades infancia", value=p.get("Enf_Infancia", ""))
    cirugias = c22.text_input("Cirugías", value=p.get("Cirugias", ""))
    hospitalizado = c23.text_input("Hospitalizaciones (Por qué?)", value=p.get("Hospitalizado", ""))

    st.subheader("IV-V. SÍNTOMAS Y SALUD FÍSICA")
    st.info("Marque con una X los síntomas detectados")
    opciones_sintomas = [
        "Insomnio", "Pesadillas", "Comerse las uñas", "Mareos", "Accidentes", "Maltrato Físico", 
        "Intentos suicidas", "Tartamudez", "Escucha voces", "Fobias", "Caminar dormido", 
        "Diarrea tensional", "Golpes en cabeza", "Ver cosas extrañas", "Hablar dormido", 
        "Convulsiones", "Orinarse en la cama", "Fiebre", "Ganas de morir", "Problemas aprendizaje", 
        "Consumo drogas", "Asma", "Repitencia Escolar", "Tics nerviosos", "Estreñimiento", "Sudoración manos"
    ]
    
    # Creamos un checklist detallado
    seleccionados = st.multiselect("Checklist de síntomas", opciones_sintomas, 
                                   default=[s for s in opciones_sintomas if s in str(p.get("Checklist", ""))])

# --- TAB 3: FAMILIA ---
with tabs[2]:
    st.subheader("VI. INFORMACIÓN FAMILIAR")
    st.write("**Cónyuge e Hijos**")
    conyuge_nom = st.text_input("Nombre del Cónyuge", value=p.get("Conyuge_Nom", ""))
    c24, c25, c26 = st.columns(3)
    conyuge_edad = c24.text_input("Edad C.", value=p.get("Conyuge_Edad", ""))
    conyuge_v = c25.selectbox("Estado", ["Vivo", "Muerto"], key="cv")
    conyuge_edu = c26.text_input("Nivel Académico C.", value=p.get("Conyuge_Edu", ""))
    relacion_c = st.text_area("Describa relación cónyuge e hijos", value=p.get("Relacion_C", ""))

    st.write("**Padre**")
    padre_nom = st.text_input("Nombre del Padre", value=p.get("Padre_Nom", ""))
    c27, c28, c29 = st.columns(3)
    padre_edad = c27.text_input("Edad P.", value=p.get("Padre_Edad", ""))
    padre_v = c28.selectbox("Estado P.", ["Vivo", "Muerto"], key="pv")
    padre_edu = c29.text_input("Nivel Académico P.", value=p.get("Padre_Edu", ""))
    relacion_p = st.text_area("Relación con Padre y Castigos", value=p.get("Relacion_P", ""))

    st.write("**Madre**")
    madre_nom = st.text_input("Nombre de la Madre", value=p.get("Madre_Nom", ""))
    c30, c31, c32 = st.columns(3)
    madre_edad = c30.text_input("Edad M.", value=p.get("Madre_Edad", ""))
    madre_v = c31.selectbox("Estado M.", ["Vivo", "Muerto"], key="mv")
    madre_edu = c32.text_input("Nivel Académico M.", value=p.get("Madre_Edu", ""))
    relacion_m = st.text_area("Relación con Madre y Castigos", value=p.get("Relacion_M", ""))

# --- TAB 4: DESARROLLO Y SOCIAL ---
with tabs[3]:
    st.subheader("VII-IX. SOCIAL, AMBIENTAL Y DESARROLLO")
    conducta_laboral = st.text_area("Conducta en escuela/trabajo, satisfacción, estrés", value=p.get("Conducta_Lab", ""))
    situacion_econ = st.selectbox("Situación Económica", ["Muy buena", "Buena", "Regular", "Mala"])
    catastrofes = st.text_input("¿Ha sufrido catástrofes o guerras?", value=p.get("Catastrofes", ""))
    
    st.write("**Hábitos y Judiciales**")
    c33, c34, c35 = st.columns(3)
    fuma = c33.selectbox("Fuma", ["No", "Sí"])
    alcohol = c34.selectbox("Alcohol", ["No", "Sí"])
    drogas = c35.text_input("Drogas", value=p.get("Drogas_Detalle", ""))
    judicial = st.text_input("Problemas con la ley (Acusado, detenido)", value=p.get("Judicial", ""))

    st.write("**Desarrollo**")
    embarazo = st.text_input("Circunstancia embarazo/planificado", value=p.get("Embarazo", ""))
    parto = st.text_input("Tipo de parto/incubadora/fórceps", value=p.get("Parto", ""))
    hitos = st.text_input("Desarrollo motor (sentarse, gatear, caminar)", value=p.get("Hitos", ""))
    esfinteres = st.text_input("Control de esfínteres", value=p.get("Esfinteres", ""))

# --- TAB 5: PERSONALIDAD Y RESULTADOS ---
with tabs[4]:
    st.subheader("X-XI. HISTORIA SEXUAL Y PERSONALIDAD")
    c36, c37 = st.columns(2)
    prim_nov = c36.text_input("Edad primer noviazgo", value=p.get("Prim_Nov", ""))
    prim_sex = c37.text_input("Edad primera relación sexual", value=p.get("Prim_Sex", ""))
    opiniones_sex = st.text_area("Opinión sobre matrimonio, masturbación, homosexualidad", value=p.get("Opiniones_Sex", ""))
    
    st.write("**Rasgos de Personalidad Previa**")
    personalidad_txt = st.text_area("Seguridad, decisiones, miedo abandono, celos, impulsividad, fracaso", value=p.get("Personalidad_Txt", ""))
    
    st.subheader("XII. OBSERVACIONES Y EVALUACIÓN IA")
    observaciones = st.text_area("Observaciones Generales del Psicólogo", value=p.get("Observaciones", ""))
    evaluador = st.text_input("Nombre del Psicólogo Evaluador", value=p.get("Evaluador", ""))

# --- 4. PROCESAMIENTO FINAL ---
st.divider()
if st.button("💾 GUARDAR EXPEDIENTE COMPLETO"):
    if nombre and identidad:
        # Construimos el diccionario con TODOS los campos individuales
        datos_finales = {
            "Nombre": nombre, "Identidad": identidad, "Fecha_Nac": f_nac, "Nacionalidad": nacionalidad,
            "Sexo": sexo, "Edad": edad, "Religion": religion, "Estado_Civil": estado_civil,
            "Celular": celular, "Ocupacion": ocupacion, "Asignacion": asignacion, "Servicio_Militar": servicio_militar,
            "Direccion": direccion, "Nivel_Edu": nivel_edu, "Remitido": remitido, "Pasatiempos": pasatiempos, "Deportes": deportes,
            "Motivo": motivo, "Ant_Situacion": ant_situacion, "Sueño": sueño, "Apetito": apetito, "Sed": sed, "Defecacion": defecacion,
            "Alergias": alergias, "Medicamentos": meds, "Enf_Infancia": enf_infancia, "Cirugias": cirug
