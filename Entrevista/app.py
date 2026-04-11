import streamlit as st
import pandas as pd
import os
import io
from docx import Document
from datetime import datetime, date, time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema Integral D.S.P. Honduras", layout="wide")
DB_FILE = "base_datos_dsp_final.xlsx"

# Definición de la estructura completa (Columnas del Excel)
COLUMNAS = [
    "Nombre", "Identidad", "Edad", "Lugar_Nacimiento", "Estado_Civil", "Religion",
    "Grado_Militar", "Antigüedad", "Asignacion_Actual", "Procedencia",
    "Motivo_Consulta", "Sintomas_Detallados", "Frecuencia_Intensidad",
    "Enfermedades_Cronicas", "Operaciones_Previas", "Medicamentos_Actuales",
    "Sueno", "Apetito", "Libido", "Habitos_Toxicos",
    "Historia_Familiar_Padres", "Historia_Hermanos", "Relacion_Familiar",
    "Embarazo_Parto", "Desarrollo_Motor", "Conducta_Infantil",
    "Rendimiento_Escolar", "Conducta_Escolar", "Nivel_Academico",
    "Primera_Relacion_Sexual", "Noviazgos", "Vida_Sexual_Actual",
    "Apariencia_Actitud", "Estado_Animo", "Proceso_Pensamiento", "Memoria_Atencion",
    "Rasgos_Personalidad", "Manejo_Estres", "Mecanismos_Defensa",
    "Seguimiento_Clinico", "Proxima_Cita"
]

# --- 2. FUNCIONES DE DATOS ---
def cargar_db():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame(columns=COLUMNAS)
    try:
        df = pd.read_excel(DB_FILE)
        df
