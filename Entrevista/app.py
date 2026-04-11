import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión D.S.P. Privada", layout="wide")

# Nombre del archivo Excel que actuará como Base de Datos
DB_FILE = "base_datos_pacientes.xlsx"

# --- FUNCIONES DE PERSISTENCIA ---
def cargar_db():
    if os.path.exists(DB_FILE):
        return pd.read_excel(DB_FILE)
    else:
        # Estructura inicial si el archivo no existe
        return pd.DataFrame(columns=["Nombre", "Edad", "Identidad", "Motivo", "Sintomas", "Familia", "Desarrollo", "Personalidad"])

def guardar_progreso(datos):
    df = cargar_db()
    # Si el paciente ya existe (por Nombre o Identidad), lo actualizamos
    if datos["Nombre"] in df["Nombre"].values:
        df.loc[df["Nombre"] == datos["Nombre"]] = datos
    else:
        df = pd.concat([df, pd.DataFrame([datos])], ignore_index=True)
    df.to_excel(DB_FILE, index=False)

# --- CLASE PDF ---
class DSP_PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 5, 'REPUBLICA DE HONDURAS | D.S.P.', 0, 1, 'C')
        self.ln(5)

# --- INTERFAZ DE USUARIO ---
st.title("🛡️ Sistema de Expedientes Psicológicos D.S.P.")

# 1. BUSCADOR EN BARRA LATERAL
df_actual = cargar_db()
with st.sidebar:
    st.header("📂 Expedientes Guardados")
    busqueda = st.selectbox("Seleccionar para continuar:", ["NUEVO REGISTRO"] + df_actual["Nombre"].tolist())
    
    prellenado = {}
    if busqueda != "NUEVO REGISTRO":
        prellenado = df_actual[df_actual["Nombre"] == busqueda].iloc[0].to_dict()
        st.success(f"Cargado: {busqueda}")

# 2. FORMULARIO CON AUTORELLENADO
tabs = st.tabs(["I. Generales", "II-V. Salud", "VI-IX. Historia", "X-XI. Personalidad"])

with tabs[0]:
    nombre = st.text_input("Nombre Completo", value=prellenado.get("Nombre", ""))
    identidad = st.text_input("Número de Identidad", value=prellenado.get("Identidad", ""))
    edad = st.text_input("Edad", value=prellenado.get("Edad", ""))

with tabs[1]:
    motivo = st.text_area("Motivo de consulta", value=prellenado.get("Motivo", ""))
    st.write("Síntomas detectados:")
    s_guardados = str(prellenado.get("Sintomas", "")).split(", ")
    sintomas = st.multiselect("Hallazgos:", ["Ganas de morir", "Escucha voces", "Insomnio", "Agresividad"], default=[s for s in s_guardados if s])

with tabs[2]:
    familia = st.text_area("Historia Familiar", value=prellenado.get("Familia", ""))
    desarrollo = st.text_area("Desarrollo Infantil y Escolar", value=prellenado.get("Desarrollo", ""))

with tabs[3]:
    personalidad = st.text_area("Rasgos de Personalidad", value=prellenado.get("Personalidad", ""))

# 3. BOTONES DE CONTROL
st.divider()
c1, c2 = st.columns(2)

with c1:
    if st.button("💾 GUARDAR AVANCE (Excel)"):
        if nombre:
            datos_paciente = {
                "Nombre": nombre, "Edad": edad, "Identidad": identidad,
                "Motivo": motivo, "Sintomas": ", ".join(sintomas),
                "Familia": familia, "Desarrollo": desarrollo, "Personalidad": personalidad
            }
            guardar_progreso(datos_paciente)
            st.success("Progreso guardado en la base de datos.")
            st.rerun()
        else:
            st.error("Se requiere el nombre para guardar.")

with c2:
    if st.button("📄 GENERAR PDF FINAL"):
        # Lógica de PDF (usando la función que ya teníamos)
        st.info("Generando archivo...")
        # Aquí iría tu función generar_pdf(...) enviando los datos actuales

# --- ÁREA DE ADMINISTRACIÓN PRIVADA ---
st.divider()
with st.expander("🔐 PANEL DE ADMINISTRACIÓN (PRIVADO)"):
    clave = st.text_input("Ingrese Clave Maestra", type="password")
    if clave == "DSP2024":  # <--- CAMBIA ESTA CLAVE
        st.dataframe(cargar_db())
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "rb") as f:
                st.download_button("📥 Descargar Base de Datos Completa", f, file_name="DB_Pacientes_DSP.xlsx")
