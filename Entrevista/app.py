import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="D.S.P. Honduras - Protocolo Detallado", layout="wide")
DB_FILE = "base_datos_dsp_exhaustiva.xlsx"

def cargar_db():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    try:
        df = pd.read_excel(DB_FILE)
        return df.astype(str).replace('nan', '')
    except: return pd.DataFrame()

# Inicializamos el diccionario de datos en el estado de la sesión
if 'd' not in st.session_state:
    st.session_state.d = {}

st.title("🛡️ Protocolo de Entrevista Clínica Completo - D.S.P.")
st.markdown("---")

# --- NAVEGACIÓN POR PESTAÑAS ---
t = st.tabs(["I. Generales", "II-V. Clínica y Síntomas", "VI. Familia", "VII-IX. Social y Desarrollo", "X-XII. Sexual y Personalidad"])

# --- SECCIÓN I: DATOS GENERALES ---
with t[0]:
    st.subheader("I. DATOS GENERALES")
    c1, c2, c3 = st.columns(3)
    st.session_state.d["Nombre"] = c1.text_input("Nombre Completo")
    st.session_state.d["Lugar_Fecha_Nac"] = c2.text_input("Lugar y Fecha de Nacimiento")
    st.session_state.d["Nacionalidad"] = c3.text_input("Nacionalidad")
    
    c4, c5, c6 = st.columns(3)
    st.session_state.d["Sexo"] = c4.selectbox("Sexo", ["M", "F"])
    st.session_state.d["Edad"] = c5.text_input("Edad")
    st.session_state.d["Religion"] = c6.text_input("Religión")
    
    c7, c8, c9 = st.columns(3)
    st.session_state.d["Estado_Civil"] = c7.text_input("Estado Civil")
    st.session_state.d["Celular"] = c8.text_input("Celular")
    st.session_state.d["Ocupacion_Actual"] = c9.text_input("Ocupación Actual")
    
    c10, c11, c12 = st.columns(3)
    st.session_state.d["Asignacion"] = c10.text_input("Asignación")
    st.session_state.d["Servicio_Militar"] = c11.selectbox("¿Prestó servicio militar?", ["Sí", "No"])
    st.session_state.d["Direccion"] = c12.text_input("Dirección Actual")
    
    c13, c14, c15 = st.columns(3)
    st.session_state.d["Nivel_Educativo"] = c13.text_input("Nivel educativo")
    st.session_state.d["Remitido_Por"] = c14.text_input("Remitido por")
    st.session_state.d["Pasatiempo"] = c15.text_input("Pasatiempo")
    st.session_state.d["Deportes"] = st.text_input("Deportes")

# --- SECCIÓN II-V: CLÍNICA Y SÍNTOMAS ---
with t[1]:
    st.subheader("II. MOTIVO DE CONSULTA")
    st.session_state.d["Motivo"] = st.text_area("Motivo de la consulta (Detallado)")
    
    st.subheader("III. ANTECEDENTES")
    st.session_state.d["Ant_Bien_Ultima_Vez"] = st.text_input("¿Cuándo se sintió bien la última vez?")
    st.session_state.d["Ant_Desarrollo_Sintomas"] = st.text_area("Desarrollo de los síntomas")
    
    st.write("**Funciones Orgánicas**")
    f1, f2, f3, f4 = st.columns(4)
    st.session_state.d["Sueño"] = f1.text_input("Sueño")
    st.session_state.d["Apetito"] = f2.text_input("Apetito")
    st.session_state.d["Sed"] = f3.text_input("Sed")
    st.session_state.d["Defecacion"] = f4.text_input("Defecación")
    
    st.subheader("IV-V. SALUD FÍSICA Y SÍNTOMAS")
    st.session_state.d["Alergias"] = st.text_input("¿Padece alergias? (Especifique)")
    st.session_state.d["Meds_Regulares"] = st.text_input("Medicamentos regulares y para qué")
    st.session_state.d["Enf_Infancia"] = st.text_input("Enfermedades de la infancia")
    st.session_state.d["Cirugias"] = st.text_input("Intervenciones quirúrgicas (Especifique)")
    st.session_state.d["Hospitalizaciones"] = st.text_input("Hospitalizaciones (Especifique motivo)")
    
    st.info("Checklist de síntomas (Marque los presentes)")
    lista_x = ["Insomnio", "Uñas", "Mareos", "Accidentes", "Pesadillas", "Maltrato", "Suicidio", "Voces", "Fobias", "Convulsiones", "Drogas", "Asma"]
    st.session_state.d["Sintomas_Check"] = st.multiselect("Seleccione:", lista_x)

# --- SECCIÓN VI: INFORMACIÓN FAMILIAR ---
with t[2]:
    st.subheader("VI. INFORMACIÓN FAMILIAR")
    st.session_state.d["Conyuge_Info"] = st.text_input("Nombre, Edad y Salud del Cónyuge")
    st.session_state.d["Relacion_Conyuge"] = st.text_area("Descripción de la relación e hijos")
    
    st.write("**Padres**")
    st.session_state.d["Padre_Info"] = st.text_input("Padre: Nombre, Edad, Vivo/Muerto, Educación")
    st.session_state.d["Relacion_Padre"] = st.text_area("Relación con el padre y castigos")
    
    st.session_state.d["Madre_Info"] = st.text_input("Madre: Nombre, Edad, Vivo/Muerto, Educación")
    st.session_state.d["Relacion_Madre"] = st.text_area("Relación con la madre y castigos")
    
    st.session_state.d["Estado_Civil_Padres"] = st.text_input("Estado civil de los padres / Motivo separación")
    st.session_state.d["Hermanos_Posicion"] = st.text_input("Número de hermanos y posición que ocupa")
    st.session_state.d["Historia_Feliz"] = st.text_area("Cuénteme una historia feliz vivida en familia")

# --- SECCIÓN VII-IX: SOCIAL Y DESARROLLO ---
with t[3]:
    st.subheader("VII-IX. SOCIAL Y DESARROLLO")
    st.session_state.d["Conducta_Escuela_Trabajo"] = st.text_area("Conducta y relaciones escuela/trabajo")
    st.session_state.d["Situacion_Economica"] = st.selectbox("Economía", ["Muy buena", "Buena", "Regular", "Mala"])
    st.session_state.d["Problemas_Ley"] = st.text_input("Dificultades con la ley")
    
    st.write("**Desarrollo Personal**")
    st.session_state.d["Circunstancia_Embarazo"] = st.text_input("Embarazo: Planificado/Reacción")
    st.session_state.d["Tipo_Parto"] = st.text_input("Parto: Tipo, Fórceps, Incubadora")
    st.session_state.d["Hitos_Motor"] = st.text_input("Desarrollo motor (sentarse, gatear, caminar)")
    st.session_state.d["Escolaridad_Detalle"] = st.text_area("Edad entrada, materias difíciles, repitencia")

# --- SECCIÓN X-XII: SEXUAL Y PERSONALIDAD ---
with t[4]:
    st.subheader("X-XII. HISTORIA SEXUAL Y PERSONALIDAD")
    st.session_state.d["H_Sexual_Noviazgo"] = st.text_input("Edad primer noviazgo / Opinión matrimonio")
    st.session_state.d["H_Sexual_Relacion"] = st.text_input("Edad primera relación / Opinión masturbación")
    st.session_state.d["H_Sexual_Opiniones"] = st.text_area("Opinión sobre homosexualidad y relaciones")
    
    st.write("**Personalidad Previa**")
    st.session_state.d["Perso_Seguridad"] = st.text_input("Seguridad en sí mismo / Toma de decisiones")
    st.session_state.d["Perso_Miedos"] = st.text_input("Miedo al abandono / Celos / Rencor")
    st.session_state.d["Perso_Impulsividad"] = st.text_input("Actos impulsivos / Preocupación fracaso")
    
    st.session_state.d["Observaciones"] = st.text_area("OBSERVACIONES GENERALES")
    st.session_state.d["Psicologo"] = st.text_input("Nombre del Psicólogo Evaluador")

# --- GUARDADO Y GENERACIÓN DE ARCHIVOS ---
st.divider()
if st.button("💾 FINALIZAR: GUARDAR EN EXCEL Y GENERAR WORD"):
    if st.session_state.d.get("Nombre") and st.session_state.d.get("Motivo"):
        # Guardar en Excel
        df_nuevo = pd.DataFrame([st.session_state.d])
        db = cargar_db()
        df_final = pd.concat([db, df_nuevo], ignore_index=True)
        df_final.to_excel(DB_FILE, index=False)
        
        # Crear Word
        doc = Document()
        doc.add_heading('EXPEDIENTE CLÍNICO D.S.P. HONDURAS', 0)
        for k, v in st.session_state.d.items():
            doc.add_paragraph(f"{k.replace('_', ' ')}: {v}")
