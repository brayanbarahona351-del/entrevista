import streamlit as st
import pandas as pd
import os
import io
from docx import Document
from datetime import datetime, date, time

# --- 1. CONFIGURACIÓN Y CONSTANTES ---
st.set_page_config(page_title="D.S.P. Honduras - Sistema Integral", layout="wide")
DB_FILE = "base_datos_pacientes.xlsx"

# Definimos el orden oficial de las columnas (Las 6 páginas de la D.S.P.)
COLUMNAS_SISTEMA = [
    "Nombre", "Identidad", "Edad", "Lugar_Nac", "Religion", "Ocupacion", 
    "Militar", "Motivo", "Sintomas", "Funciones_Org", "Antecedentes_Fam", 
    "Desarrollo_Inf", "Historia_Escolar", "Historia_Sexual", 
    "Personalidad_Previa", "Seguimiento", "Proxima_Cita"
]

# --- 2. FUNCIONES DE BASE DE DATOS (BLINDADAS) ---
def cargar_db():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_excel(DB_FILE)
            # Verificar si faltan columnas y agregarlas
            for col in COLUMNAS_SISTEMA:
                if col not in df.columns:
                    df[col] = ""
            return df
        except Exception:
            # Si el archivo está corrupto, crear uno nuevo
            return pd.DataFrame(columns=COLUMNAS_SISTEMA)
    else:
        return pd.DataFrame(columns=COLUMNAS_SISTEMA)

def guardar_en_db(datos):
    df = cargar_db()
    # Si el paciente ya existe, actualizar; si no, agregar
    if not df.empty and datos["Nombre"] in df["Nombre"].values:
        idx = df.index[df["Nombre"] == datos["Nombre"]][0]
        for key, value in datos.items():
            df.at[idx, key] = value
    else:
        df = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
    df.to_excel(DB_FILE, index=False)

# --- 3. LÓGICA DE CARGA DE DATOS ---
df_db = cargar_db()

# Barra lateral para selección de expediente
with st.sidebar:
    st.header("📂 Expedientes")
    # Aseguramos que el selectbox no falle si el DF está vacío
    lista_pacientes = ["NUEVO REGISTRO"]
    if not df_db.empty:
        lista_pacientes += df_db["Nombre"].dropna().tolist()
        
    sel = st.selectbox("Seleccionar paciente:", lista_pacientes)
    
    # Extraer datos del paciente seleccionado
    if sel != "NUEVO REGISTRO":
        p = df_db[df_db["Nombre"] == sel].iloc[0].to_dict()
    else:
        p = {col: "" for col in COLUMNAS_SISTEMA}

    st.divider()
    st.header("📅 Agenda de Citas")
    if not df_db.empty and "Proxima_Cita" in df_db.columns:
        citas_activas = df_db[df_db["Proxima_Cita"].astype(str).str.strip() != ""]
        if not citas_activas.empty:
            for _, row in citas_activas.iterrows():
                st.info(f"**{row['Nombre']}**\n{row['Proxima_Cita']}")
        else:
            st.write("No hay citas.")

# --- 4. INTERFAZ DE USUARIO (LAS 6 PÁGINAS) ---
st.title("🛡️ Sistema de Gestión Psicológica D.S.P.")

t1, t2, t3, t4, t5, t6 = st.tabs([
    "I. Generales", "II-V. Clínica", "VI. Familia", 
    "VII-IX. Historia", "X-XI. Personalidad", "📈 Seguimiento y Citas"
])

with t1:
    nombre = st.text_input("Nombre Completo", value=p.get("Nombre", ""))
    identidad = st.text_input("Identidad", value=p.get("Identidad", ""))
    c1, c2 = st.columns(2)
    edad = c1.text_input("Edad", value=p.get("Edad", ""))
    lugar_nac = c2.text_input("Lugar/Fecha Nacimiento", value=p.get("Lugar_Nac", ""))
    ocupacion = st.text_input("Ocupación/Asignación", value=p.get("Ocupacion", ""))

with t2:
    motivo = st.text_area("II. Motivo de Consulta", value=p.get("Motivo", ""))
    s_opciones = ["Ganas de morir", "Escucha voces", "Insomnio", "Pesadillas", "Agresividad"]
    s_previos = str(p.get("Sintomas", "")).split(", ")
    sintomas = st.multiselect("V. Hallazgos:", s_opciones, default=[s for s in s_previos if s in s_opciones])
    funciones = st.text_input("Funciones Orgánicas", value=p.get("Funciones_Org", ""))

with t3:
    familia = st.text_area("VI. Antecedentes Familiares", value=p.get("Antecedentes_Fam", ""))

with t4:
    desarrollo = st.text_area("VII-IX. Desarrollo y Escolaridad", value=p.get("Desarrollo_Inf", ""))

with t5:
    personalidad = st.text_area("X-XI. Historia Sexual y Personalidad", value=p.get("Personalidad_Previa", ""))

with t6:
    st.subheader("Seguimiento y Agenda")
    historial = str(p.get("Seguimiento", "")) if not pd.isna(p.get("Seguimiento")) else ""
    st.text_area("Historial acumulado:", value=historial, height=150, disabled=True)
    nueva_nota = st.text_area("Nueva nota de hoy:")
    
    st.divider()
    c_f, c_h = st.columns(2)
    f_cita = c_f.date_input("Próxima Cita", value=date.today())
    h_cita = c_h.time_input("Hora", value=time(8, 0))

# --- 5. BOTÓN DE PROCESAMIENTO ---
st.divider()
if st.button("💾 GUARDAR Y GENERAR DOCUMENTO WORD"):
    if nombre and motivo:
        # Actualizar seguimiento
        nota_full = historial
        if nueva_nota:
            nota_full += f"\n[{datetime.now().strftime('%d/%m/%Y')}]: {nueva_nota}"
        
        cita_str = f"{f_cita.strftime('%d/%m/%Y')} a las {h_cita.strftime('%H:%M')}"
        
        # Diccionario de datos
        datos_finales = {
            "Nombre": nombre, "Identidad": identidad, "Edad": edad, "Lugar_Nac": lugar_nac,
            "Motivo": motivo, "Sintomas": ", ".join(sintomas), "Funciones_Org": funciones,
            "Antecedentes_Fam": familia, "Desarrollo_Inf": desarrollo, 
            "Personalidad_Previa": personalidad, "Seguimiento": nota_full, 
            "Proxima_Cita": cita_str
        }
        
        guardar_en_db(datos_finales)
        
        # Generar Word
        doc = Document()
        doc.add_heading('EXPEDIENTE CLÍNICO D.S.P.', 0)
        for k, v in datos_finales.items():
            doc.add_paragraph(f"**{k}**: {v}")
        
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        
        st.success("¡Datos guardados!")
        st.download_button("📥 Descargar Word", buf, f"DSP_{nombre}.docx")
    else:
        st.error("Por favor completa Nombre y Motivo.")
