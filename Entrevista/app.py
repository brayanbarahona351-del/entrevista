import streamlit as st
import pandas as pd
import os, io
from docx import Document
from docx.shared import Pt, Inches
from datetime import datetime, date

# --- 1. CONFIGURACIÓN Y BASE DE DATOS ---
st.set_page_config(page_title="D.S.P. - Protocolo Completo", layout="wide")
DB_FILE = "DB_DSP_MASTER.xlsx"

def cargar_db():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    try: return pd.read_excel(DB_FILE).astype(str).replace('nan', '')
    except: return pd.DataFrame()

def guardar_db(datos):
    df = cargar_db()
    if not df.empty and "Identidad" in df.columns:
        df = df[df["Identidad"] != datos["Identidad"]]
    df_final = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
    df_final.to_excel(DB_FILE, index=False)

# --- 2. DICCIONARIO DE ENLACES DE TESTS ---
TEST_LINKS = {
    "MMPI-2 (Personalidad)": "https://www.teaediciones.com/mmpi-2-inventario-multifasico-de-personalidad-de-minnesota-2.html",
    "Beck (Depresión/Ansiedad)": "https://www.paho.org/es/documentos/inventario-depresion-beck-bdi-ii",
    "SCL-90-R (Síntomas)": "https://web.teaediciones.com/scl-90-r-cuestionario-de-90-sintomas-revisado.aspx",
    "16PF-5 (Rasgos)": "https://www.psicologia-online.com/test-de-personalidad-16pf-5-que-es-y-como-se-interpreta-4652.html",
    "IPV (Ventas/Impulsividad)": "https://web.teaediciones.com/ipv-inventario-de-personalidad-para-vendedores.aspx"
}

# --- 3. INTERFAZ ---
db_actual = cargar_db()
with st.sidebar:
    st.header("🔐 ARCHIVO CLÍNICO")
    modo = st.radio("Acción:", ["Nuevo Registro", "Cargar Existente"])
    datos_prev = {}
    if modo == "Cargar Existente" and not db_actual.empty:
        id_sel = st.selectbox("Identidad:", db_actual["Identidad"].tolist())
        datos_prev = db_actual[db_actual["Identidad"] == id_sel].iloc[0].to_dict()

st.title("🛡️ Protocolo de Entrevista e Informe D.S.P.")

# --- 4. CAMPOS DETALLADOS (ESTRUCTURA DE CUESTIONARIO) ---
tabs = st.tabs(["I-II. Generales y Motivo", "III-V. Salud y Biografía", "VI-IX. Desarrollo", "X-XII. Informe e IA"])

with tabs[0]:
    c1, c2 = st.columns(2)
    identidad = c1.text_input("1. Número de Identidad (ID Único)", value=datos_prev.get("Identidad", ""))
    nombre = c2.text_input("2. Nombre Completo", value=datos_prev.get("Nombre", ""))
    
    c3, c4, c5 = st.columns(3)
    f_nac = c3.text_input("3. Lugar y Fecha de Nacimiento", value=datos_prev.get("F_Nac", ""))
    edad = c4.text_input("4. Edad", value=datos_prev.get("Edad", ""))
    sexo = c5.selectbox("5. Sexo", ["M", "F"], index=0 if datos_prev.get("Sexo")=="M" else 1)
    
    motivo = st.text_area("6. ¿Cuál es el motivo de su consulta hoy? (Detalle)", value=datos_prev.get("Motivo", ""))

with tabs[1]:
    st.subheader("HISTORIA DE SALUD")
    sue = st.text_input("7. ¿Cómo es su calidad de sueño?", value=datos_prev.get("Sueño", ""))
    ape = st.text_input("8. ¿Cómo describe su apetito?", value=datos_prev.get("Apetito", ""))
    meds = st.text_input("9. ¿Toma medicamentos regularmente?", value=datos_prev.get("Meds", ""))
    
    st.subheader("HISTORIA FAMILIAR")
    padre = st.text_area("10. Describa la relación con su padre y castigos recibidos:", value=datos_prev.get("Rel_Padre", ""))
    madre = st.text_area("11. Describa la relación con su madre y castigos recibidos:", value=datos_prev.get("Rel_Madre", ""))

with tabs[2]:
    st.subheader("DESARROLLO Y VIDA SOCIAL")
    embarazo = st.text_input("12. Circunstancias del embarazo y parto:", value=datos_prev.get("Parto", ""))
    escuela = st.text_area("13. ¿Cómo fue su rendimiento y conducta escolar?", value=datos_prev.get("Escuela", ""))
    checklist = st.multiselect("14. Marque si ha presentado:", ["Pesadillas", "Ideas de muerte", "Drogas", "Ira"], 
                               default=eval(datos_prev.get("Sintomas", "[]")) if datos_prev else [])

with tabs[3]:
    st.subheader("ANÁLISIS PROFESIONAL E IA")
    analisis = st.text_area("Análisis Clínico", value=datos_prev.get("Analisis", ""))
    concl = st.text_area("Conclusiones", value=datos_prev.get("Conclusiones", ""))
    
    st.write("### 🧪 Recomendación de Tests")
    test_sug = st.multiselect("Seleccione los tests a recomendar:", list(TEST_LINKS.keys()))
    
    for t in test_sug:
        st.write(f"🔗 **{t}**: [Clic aquí para acceder al recurso]({TEST_LINKS[t]})")
    
    recom = st.text_area("Otras Recomendaciones", value=datos_prev.get("Recom", ""))
    psic = st.text_input("Psicólogo Evaluador", value=datos_prev.get("Psicologo", ""))

# --- 5. GENERACIÓN DEL DOCUMENTO COMPLETO ---
if st.button("💾 GUARDAR Y GENERAR PROTOCOLO COMPLETO"):
    if identidad and nombre:
        datos_finales = {
            "Identidad": identidad, "Nombre": nombre, "F_Nac": f_nac, "Edad": edad, "Sexo": sexo,
            "Motivo": motivo, "Sueño": sue, "Apetito": ape, "Meds": meds, "Rel_Padre": padre,
            "Rel_Madre": madre, "Parto": embarazo, "Escuela": escuela, "Sintomas": str(checklist),
            "Analisis": analisis, "Conclusiones": concl, "Recom": recom, "Psicologo": psic,
            "Tests_Rec": str(test_sug)
        }
        guardar_db(datos_finales)
        
        # --- CREACIÓN DEL WORD TIPO EXPEDIENTE ---
        doc = Document()
        
        # Sección 1: La Entrevista Completa
        doc.add_heading('PARTE I: PROTOCOLO DE ENTREVISTA (PREGUNTA/RESPUESTA)', 0)
        preguntas_respuestas = [
            ("Número de Identidad", identidad), ("Nombre", nombre), ("Motivo de Consulta", motivo),
            ("Calidad de Sueño", sue), ("Apetito", ape), ("Medicamentos", meds),
            ("Relación con Padre", padre), ("Relación con Madre", madre),
            ("Embarazo/Parto", embarazo), ("Historia Escolar", escuela), ("Síntomas", str(checklist))
        ]
        
        for p, r in preguntas_respuestas:
            par = doc.add_paragraph()
            par.add_run(f"P: {p}\nR: ").bold = True
            par.add_run(str(r))
            
        doc.add_page_break()
        
        # Sección 2: El Informe
        doc.add_heading('PARTE II: INFORME PSICOLÓGICO FINAL', 0)
        doc.add_heading('Análisis Clínico', level=1); doc.add_paragraph(analisis)
        doc.add_heading('Conclusiones', level=1); doc.add_paragraph(concl)
        
        doc.add_heading('Recomendaciones de Tests y Enlaces', level=1)
        for t in test_sug:
            doc.add_paragraph(f"• {t}: {TEST_LINKS[t]}")
            
        doc.add_heading('Plan de Acción', level=1); doc.add_paragraph(recom)
        
        doc.add_paragraph(f"\n\nFirma: {psic}\nFecha: {date.today()}")

        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        
        st.success("✅ Protocolo e Informe generados exitosamente.")
        st.download_button("📥 DESCARGAR EXPEDIENTE COMPLETO", buf, f"Expediente_{identidad}.docx")
    else:
        st.error("Identidad y Nombre son obligatorios.")
