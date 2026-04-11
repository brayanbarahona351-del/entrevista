import streamlit as st
import pandas as pd
import os
import io
from docx import Document
from datetime import datetime, date, time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="D.S.P. Honduras - Sistema Integral", layout="wide")
DB_FILE = "base_datos_pacientes.xlsx"

# --- FUNCIONES DE BASE DE DATOS ---
def cargar_db():
    if os.path.exists(DB_FILE):
        return pd.read_excel(DB_FILE)
    else:
        # Estructura con TODAS las columnas necesarias
        cols = ["Nombre", "Identidad", "Edad", "Lugar_Nac", "Religion", "Ocupacion", "Militar", 
                "Motivo", "Sintomas", "Funciones_Org", "Antecedentes_Fam", "Desarrollo_Inf", 
                "Historia_Escolar", "Historia_Sexual", "Personalidad_Previa", "Seguimiento", "Proxima_Cita"]
        return pd.DataFrame(columns=cols)

def guardar_en_db(datos):
    df = cargar_db()
    if datos["Nombre"] in df["Nombre"].values:
        idx = df.index[df["Nombre"] == datos["Nombre"]][0]
        for key, value in datos.items():
            df.at[idx, key] = value
    else:
        df = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
    df.to_excel(DB_FILE, index=False)

# --- INTERFAZ ---
st.title("🛡️ Expediente Clínico Digital D.S.P.")

df_db = cargar_db()
with st.sidebar:
    st.header("📂 Buscar Paciente")
    sel = st.selectbox("Expedientes:", ["NUEVO REGISTRO"] + df_db["Nombre"].tolist())
    p = df_db[df_db["Nombre"] == sel].iloc[0].to_dict() if sel != "NUEVO REGISTRO" else {}
    
    st.divider()
    st.header("📅 Agenda")
    citas = df_db[df_db["Proxima_Cita"].notna() & (df_db["Proxima_Cita"] != "")]
    for _, r in citas.iterrows():
        st.caption(f"**{r['Nombre']}**: {r['Proxima_Cita']}")

# PESTAÑAS CON TODAS LAS PREGUNTAS
t1, t2, t3, t4, t5, t6 = st.tabs(["I. Generales", "II-V. Clínica", "VI. Familia", "VII-IX. Historia", "X-XI. Personalidad", "📈 Seguimiento/Citas"])

with t1:
    st.subheader("I. DATOS GENERALES")
    nombre = st.text_input("Nombre Completo", value=p.get("Nombre", ""))
    identidad = st.text_input("Número de Identidad", value=p.get("Identidad", ""))
    c1, c2 = st.columns(2)
    edad = c1.text_input("Edad", value=p.get("Edad", ""))
    lugar_nac = c2.text_input("Lugar y Fecha de Nacimiento", value=p.get("Lugar_Nac", ""))
    religion = c1.text_input("Religión", value=p.get("Religion", ""))
    ocupacion = c2.text_input("Ocupación / Asignación", value=p.get("Ocupacion", ""))
    militar = st.radio("¿Servicio Militar?", ["No", "Sí"], index=1 if p.get("Militar") == "Sí" else 0)

with t2:
    st.subheader("II-V. MOTIVO Y SALUD")
    motivo = st.text_area("II. Motivo de Consulta", value=p.get("Motivo", ""))
    s_lista = ["Ganas de morir", "Escucha voces", "Insomnio", "Pesadillas", "Agresividad", "Tics", "Consumo drogas"]
    s_guardados = str(p.get("Sintomas", "")).split(", ")
    sintomas = st.multiselect("V. Hallazgos Síntomáticos:", s_lista, default=[s for s in s_guardados if s in s_lista])
    funciones_org = st.text_input("Funciones Orgánicas (Sueño, Apetito, etc.)", value=p.get("Funciones_Org", ""))

with t3:
    st.subheader("VI. INFORMACIÓN FAMILIAR")
    antecedentes_fam = st.text_area("Padres, Hermanos y Antecedentes (Alcoholismo, enfermedad mental)", value=p.get("Antecedentes_Fam", ""))

with t4:
    st.subheader("VII-IX. DESARROLLO")
    desarrollo_inf = st.text_area("Embarazo, Parto, Lactancia y Desarrollo Motor", value=p.get("Desarrollo_Inf", ""))
    escolar = st.text_area("Historia Escolar (Materias, conducta)", value=p.get("Historia_Escolar", ""))

with t5:
    st.subheader("X-XI. SEXUALIDAD Y PERSONALIDAD")
    sexual = st.text_area("X. Historia Sexual (Noviazgo, primera relación)", value=p.get("Historia_Sexual", ""))
    personalidad = st.text_area("XI. Personalidad Previa (Seguridad, rencor, impulsividad)", value=p.get("Personalidad_Previa", ""))

with t6:
    st.subheader("Seguimiento y Próxima Cita")
    historial = str(p.get("Seguimiento", "")) if not pd.isna(p.get("Seguimiento")) else ""
    st.text_area("Notas anteriores:", value=historial, height=150, disabled=True)
    nueva_nota = st.text_area("Nueva nota de hoy:")
    
    st.divider()
    c_f, c_h = st.columns(2)
    f_cita = c_f.date_input("Fecha próxima cita", value=date.today())
    h_cita = c_h.time_input("Hora", value=time(8, 0))

# BOTÓN DE GUARDADO GLOBAL
if st.button("💾 GUARDAR TODO Y GENERAR DOCUMENTO WORD"):
    if nombre and motivo:
        # Procesar seguimiento
        nota_final = historial
        if nueva_nota:
            nota_final += f"\n--- {datetime.now().strftime('%d/%m/%Y')}: {nueva_nota}"
            
        cita_str = f"{f_cita.strftime('%d/%m/%Y')} {h_cita.strftime('%H:%M')}"
        
        datos_full = {
            "Nombre": nombre, "Identidad": identidad, "Edad": edad, "Lugar_Nac": lugar_nac,
            "Religion": religion, "Ocupacion": ocupacion, "Militar": militar, "Motivo": motivo,
            "Sintomas": ", ".join(sintomas), "Funciones_Org": funciones_org, "Antecedentes_Fam": antecedentes_fam,
            "Desarrollo_Inf": desarrollo_inf, "Historia_Escolar": escolar, "Historia_Sexual": sexual,
            "Personalidad_Previa": personalidad, "Seguimiento": nota_final, "Proxima_Cita": cita_str
        }
        
        guardar_en_db(datos_full)
        
        # Generar Word profesional
        doc = Document()
        doc.add_heading('EXPEDIENTE PSICOLÓGICO D.S.P.', 0)
        for k, v in datos_full.items():
            if k not in ["Seguimiento", "Proxima_Cita"]:
                doc.add_paragraph(f"**{k.replace('_', ' ')}**: {v}")
        
        doc.add_page_break()
        doc.add_heading('EVOLUCIÓN Y PRÓXIMA CITA', level=1)
        doc.add_paragraph(nota_final)
        doc.add_paragraph(f"\nPRÓXIMA CITA: {cita_str}")
        
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        st.success("✅ Datos guardados en Excel y Word generado.")
        st.download_button("📥 Descargar Word", buf, f"Expediente_{nombre}.docx")
        st.rerun()
