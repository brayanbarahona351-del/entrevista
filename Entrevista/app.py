import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="D.S.P. Honduras - Sistema Clínico", layout="wide")
DB_FILE = "base_datos_dsp_honduras.xlsx"

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_db():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()
    return pd.read_excel(DB_FILE).astype(str).replace('nan', '')

def guardar_db(datos_dict):
    df = cargar_db()
    # Si el paciente ya existe (por Identidad), lo eliminamos para actualizarlo
    if not df.empty and "Identidad" in df.columns:
        df = df[df["Identidad"] != datos_dict["Identidad"]]
    nuevo_df = pd.DataFrame([datos_dict])
    df_final = pd.concat([df, nuevo_df], ignore_index=True)
    df_final.to_excel(DB_FILE, index=False)
    return df_final

# --- BUSCADOR EN BARRA LATERAL ---
db_actual = cargar_db()

with st.sidebar:
    st.header("🔍 BUSCAR PACIENTE")
    opciones = ["NUEVO REGISTRO"]
    if not db_actual.empty:
        opciones += db_actual["Nombre"].tolist()
    
    seleccion = st.selectbox("Seleccione un paciente existente:", opciones)
    
    # Cargar datos si existe
    if seleccion != "NUEVO REGISTRO":
        datos_previa = db_actual[db_actual["Nombre"] == seleccion].iloc[0].to_dict()
        st.success(f"Cargado: {seleccion}")
    else:
        datos_previa = {}

st.title("🛡️ Protocolo de Entrevista Clínica Completa - D.S.P.")

# --- TABS CON TODAS LAS PREGUNTAS ---
t1, t2, t3, t4, t5, t6 = st.tabs(["I-II. Generales", "III-V. Salud", "VI. Familia", "VII-IX. Desarrollo", "X-XII. Informe", "📊 Ver Base de Datos"])

# SECCIÓN I: GENERALES
with t1:
    st.subheader("DATOS GENERALES")
    c1, c2, c3 = st.columns(3)
    nom = c1.text_input("Nombre Completo", value=datos_previa.get("Nombre", ""))
    ide = c2.text_input("Identidad", value=datos_previa.get("Identidad", ""))
    f_nac = c3.text_input("Lugar y Fecha Nacimiento", value=datos_previa.get("Lugar_Fecha_Nac", ""))
    
    c4, c5, c6 = st.columns(3)
    nac = c4.text_input("Nacionalidad", value=datos_previa.get("Nacionalidad", ""))
    sex = c5.selectbox("Sexo", ["M", "F"], index=0 if datos_previa.get("Sexo") == "M" else 1)
    eda = c6.text_input("Edad", value=datos_previa.get("Edad", ""))
    
    cel = c1.text_input("Celular", value=datos_previa.get("Celular", ""))
    ocu = c2.text_input("Ocupación Actual", value=datos_previa.get("Ocupacion", ""))
    asi = c3.text_input("Asignación", value=datos_previa.get("Asignacion", ""))
    dir_a = st.text_input("Dirección Actual", value=datos_previa.get("Direccion", ""))
    rem = st.text_input("Remitido por", value=datos_previa.get("Remitido", ""))
    mot = st.text_area("MOTIVO DE CONSULTA", value=datos_previa.get("Motivo", ""))

# SECCIÓN II: SALUD (DETALLE MÁXIMO)
with t2:
    st.subheader("ANTECEDENTES CLÍNICOS")
    ant_s = st.text_area("Antecedentes de la situación (Desarrollo de síntomas)", value=datos_previa.get("Ant_Situacion", ""))
    
    st.write("**Funciones Orgánicas**")
    f1, f2, f3, f4 = st.columns(4)
    sue = f1.text_input("Sueño", value=datos_previa.get("Sueño", ""))
    ape = f2.text_input("Apetito", value=datos_previa.get("Apetito", ""))
    sed = f3.text_input("Sed", value=datos_previa.get("Sed", ""))
    defec = f4.text_input("Defecación", value=datos_previa.get("Defecacion", ""))
    
    c7, c8 = st.columns(2)
    ale = c7.text_input("¿Alergias?", value=datos_previa.get("Alergias", ""))
    med = c8.text_input("¿Medicamentos?", value=datos_previa.get("Medicamentos", ""))
    
    hosp = st.text_input("¿Hospitalizado? ¿Por qué?", value=datos_previa.get("Hospitalizado", ""))
    
    st.write("**Síntomas Neuroticos**")
    checklist = st.multiselect("Marque síntomas presentes:", 
                               ["Pesadillas", "Enuresis", "Tics", "Fobias", "Drogas", "Alcohol", "Ideas Suicidas", "Voces"],
                               default=eval(datos_previa.get("Checklist", "[]")) if seleccion != "NUEVO REGISTRO" else [])

# SECCIÓN III: FAMILIA
with t3:
    st.subheader("INFORMACIÓN FAMILIAR")
    pad_n = st.text_input("Nombre del Padre", value=datos_previa.get("Padre_Nom", ""))
    pad_r = st.text_area("Relación y castigos con el Padre", value=datos_previa.get("Padre_Rel", ""))
    mad_n = st.text_input("Nombre de la Madre", value=datos_previa.get("Madre_Nom", ""))
    mad_r = st.text_area("Relación y castigos con la Madre", value=datos_previa.get("Madre_Rel", ""))
    herm = st.text_input("Hermanos y posición", value=datos_previa.get("Hermanos", ""))
    hist_f = st.text_area("Historia familiar feliz", value=datos_previa.get("Historia_Feliz", ""))

# SECCIÓN IV: DESARROLLO
with t4:
    st.subheader("DESARROLLO Y SOCIAL")
    c9, c10 = st.columns(2)
    emb = c9.text_input("Embarazo (Planificado/Reacción)", value=datos_previa.get("Embarazo", ""))
    par = c10.text_input("Parto (Fórceps/Incubadora)", value=datos_previa.get("Parto", ""))
    hitos = st.text_input("Hitos (Sentarse, gatear, caminar)", value=datos_previa.get("Hitos", ""))
    esc = st.text_area("Historia Escolar (Materias, problemas, repitencia)", value=datos_previa.get("Escuela", ""))

# SECCIÓN V: INFORME E IA
with t5:
    st.subheader("INFORME FINAL, CONCLUSIONES Y RECOMENDACIONES")
    
    # Análisis IA simplificado
    ia_analisis = f"Paciente {nom}, con motivo de consulta: {mot}. Presenta síntomas de {checklist}."
    
    ana = st.text_area("Análisis del Psicólogo", value=datos_previa.get("Analisis", ia_analisis))
    concl = st.text_area("Conclusiones", value=datos_previa.get("Conclusiones", ""))
    recom = st.text_area("Recomendaciones y Test sugeridos", value=datos_previa.get("Recomendaciones", ""))
    tera = st.text_area("Plan Terapéutico", value=datos_previa.get("Terapia", ""))
    
    st.divider()
    psic = st.text_input("Nombre del Psicólogo Evaluador", value=datos_previa.get("Psicologo", ""))
    prox = st.date_input("Próxima Cita")

# SECCIÓN VI: VER BASE DE DATOS
with t6:
    st.subheader("📊 Explorador de Base de Datos")
    if not db_actual.empty:
        st.dataframe(db_actual)
        # Botón para descargar toda la base de datos en Excel
        buf_ex = io.BytesIO()
        db_actual.to_excel(buf_ex, index=False)
        st.download_button("📥 Descargar Excel Completo", buf_ex, "base_datos_dsp.xlsx")
    else:
        st.info("La base de datos está vacía actualmente.")

# --- GUARDADO ---
if st.button("💾 GUARDAR Y GENERAR INFORME"):
    if nom and ide:
        # Recopilamos absolutamente todo
        datos_completos = {
            "Nombre": nom, "Identidad": ide, "Lugar_Fecha_Nac": f_nac, "Nacionalidad": nac,
            "Sexo": sex, "Edad": eda, "Celular": cel, "Ocupacion": ocu, "Asignacion": asi,
            "Direccion": dir_a, "Remitido": rem, "Motivo": mot, "Ant_Situacion": ant_s,
            "Sueño": sue, "Apetito": ape, "Sed": sed, "Defecacion": defec,
            "Alergias": ale, "Medicamentos": med, "Hospitalizado": hosp,
            "Checklist": str(checklist), "Padre_Nom": pad_n, "Padre_Rel": pad_r,
            "Madre_Nom": mad_n, "Madre_Rel": mad_r, "Hermanos": herm, "Historia_Feliz": hist_f,
            "Embarazo": emb, "Parto": par, "Hitos": hitos, "Escuela": esc,
            "Analisis": ana, "Conclusiones": concl, "Recomendaciones": recom,
            "Terapia": tera, "Psicologo": psic, "Proxima_Cita": str(prox), "Fecha_Registro": str(date.today())
        }
        
        # 1. Guardar en Excel
        db_final = guardar_db(datos_completos)
        st.success("✅ Datos guardados y actualizados en el Excel.")
        
        # 2. Generar Word con Conclusiones y Recomendaciones
        doc = Document()
        doc.add_heading(f'INFORME PSICOLÓGICO: {nom}', 0)
        
        # Estructura del Informe
        secciones = {
            "MOTIVO DE CONSULTA": mot,
            "ANÁLISIS CLÍNICO": ana,
            "CONCLUSIONES": concl,
            "RECOMENDACIONES Y TEST": recom,
            "PLAN TERAPÉUTICO": tera
        }
        
        for titulo, contenido in secciones.items():
            doc.add_heading(titulo, level=1)
            doc.add_paragraph(contenido)
            
        doc.add_paragraph(f"\n\nPsicólogo Evaluador: {psic}")
        doc.add_paragraph(f"Fecha: {date.today()}")
        
        buf_word = io.BytesIO()
        doc.save(buf_word)
        buf_word.seek(0)
        
        st.download_button("📥 Descargar Informe Word Final", buf_word, f"Informe_{ide}.docx")
    else:
        st.error("Nombre e Identidad son obligatorios.")
