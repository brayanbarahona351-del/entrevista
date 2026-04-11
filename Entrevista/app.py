import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema Clínico D.S.P.", layout="wide")
DB_FILE = "base_datos_clinica_dsp.xlsx"

# Función para asegurar que el Excel tenga todas las columnas
def cargar_db():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()
    try:
        return pd.read_excel(DB_FILE).astype(str).replace('nan', '')
    except:
        return pd.DataFrame()

# Inicialización de memoria temporal
if 'datos' not in st.session_state:
    st.session_state.datos = {}

st.title("🛡️ Protocolo de Evaluación Psicológica D.S.P.")
st.info("Complete todas las pestañas. Al final podrá guardar en la base de datos y descargar el Word.")

# --- NAVEGACIÓN ---
t = st.tabs([
    "I. Generales", 
    "II-V. Salud y Síntomas", 
    "VI. Familia", 
    "VII-IX. Desarrollo", 
    "X-XI. Sexual y Personalidad",
    "XII. SEGUIMIENTO Y CITAS" # <--- SECCIÓN AGREGADA
])

# SECCIÓN I: GENERALES
with t[0]:
    st.subheader("I. DATOS GENERALES")
    c1, c2, c3 = st.columns(3)
    st.session_state.datos["Nombre"] = c1.text_input("Nombre Completo")
    st.session_state.datos["Identidad"] = c2.text_input("Número de Identidad / DNI")
    st.session_state.datos["Lugar_Fecha_Nac"] = c3.text_input("Lugar y Fecha de Nacimiento")
    
    c4, c5, c6 = st.columns(3)
    st.session_state.datos["Nacionalidad"] = c4.text_input("Nacionalidad")
    st.session_state.datos["Sexo"] = c5.radio("Sexo", ["M", "F"], horizontal=True)
    st.session_state.datos["Edad"] = c6.text_input("Edad")
    
    c7, c8, c9 = st.columns(3)
    st.session_state.datos["Religion"] = c7.text_input("Religión")
    st.session_state.datos["Estado_Civil"] = c8.text_input("Estado Civil")
    st.session_state.datos["Celular"] = c9.text_input("Celular")
    
    st.session_state.datos["Ocupacion"] = st.text_input("Ocupación Actual")
    st.session_state.datos["Asignacion"] = st.text_input("Asignación")
    st.session_state.datos["Militar"] = st.selectbox("¿Prestó servicio militar?", ["No", "Sí"])
    st.session_state.datos["Direccion"] = st.text_input("Dirección Actual")
    st.session_state.datos["Nivel_Edu"] = st.text_input("Nivel Educativo")
    st.session_state.datos["Remitido"] = st.text_input("Remitido por")
    
    st.session_state.datos["Motivo"] = st.text_area("MOTIVO DE CONSULTA")

# SECCIÓN II-V: SALUD
with t[1]:
    st.subheader("III-V. ANTECEDENTES Y SALUD")
    st.session_state.datos["Ant_Situacion"] = st.text_area("Antecedentes de la situación (¿Cuándo se sintió bien por última vez?)")
    
    st.write("**Funciones Orgánicas**")
    f1, f2, f3, f4 = st.columns(4)
    st.session_state.datos["Sueño"] = f1.text_input("Sueño")
    st.session_state.datos["Apetito"] = f2.text_input("Apetito")
    st.session_state.datos["Sed"] = f3.text_input("Sed")
    st.session_state.datos["Defecacion"] = f4.text_input("Defecación")
    
    st.session_state.datos["Alergias"] = st.text_input("¿Padece alergias?")
    st.session_state.datos["Meds"] = st.text_input("¿Toma algún medicamento regularmente?")
    st.session_state.datos["Enf_Infancia"] = st.text_input("Enfermedades sufridas en la infancia")
    st.session_state.datos["Cirugias"] = st.text_input("¿Intervenciones quirúrgicas?")
    st.session_state.datos["Hospitalizaciones"] = st.text_input("¿Hospitalizaciones y por qué?")

    st.write("**Checklist de Salud Física y Neurotismos**")
    sints = ["Pesadillas", "Terror nocturno", "Sonambulismo", "Berrinches", "Enuresis", "Onicofagia", "Fobias", "Tics", "Ganas de morir", "Escucha voces"]
    st.session_state.datos["Sintomas_X"] = st.multiselect("Marque lo que ha presentado:", sints)

# SECCIÓN VI: FAMILIA
with t[2]:
    st.subheader("VI. INFORMACIÓN FAMILIAR")
    st.session_state.datos["Padre_Nombre"] = st.text_input("Nombre del Padre")
    st.session_state.datos["Padre_Relacion"] = st.text_area("Tipo de relación con el padre y castigos")
    st.session_state.datos["Madre_Nombre"] = st.text_input("Nombre de la Madre")
    st.session_state.datos["Madre_Relacion"] = st.text_area("Tipo de relación con la madre y castigos")
    st.session_state.datos["Hermanos"] = st.text_input("Número de hermanos y posición que ocupa")
    st.session_state.datos["Encargado_Crianza"] = st.text_input("¿Quién fue el encargado de su crianza?")
    st.session_state.datos["Historia_Feliz"] = st.text_area("Historia feliz o divertida vivida en familia")

# SECCIÓN VII-IX: DESARROLLO
with t[3]:
    st.subheader("VII-IX. DESARROLLO Y SOCIAL")
    st.session_state.datos["Embarazo"] = st.text_input("Circunstancia del embarazo / Planificado")
    st.session_state.datos["Parto"] = st.text_input("Tipo de parto (fórceps, incubadora)")
    st.session_state.datos["Hitos"] = st.text_input("Desarrollo motor (gatear, caminar)")
    st.session_state.datos["Esfinteres"] = st.text_input("Control de esfínteres")
    
    st.write("**Datos Escolares**")
    st.session_state.datos["Escuela_Edad"] = st.text_input("Edad entrada escuela")
    st.session_state.datos["Materias_Dificiles"] = st.text_input("Materias con mayor dificultad")
    st.session_state.datos["Metodo_Aprendizaje"] = st.text_input("¿Cómo aprende más fácilmente?")

# SECCIÓN X-XI: SEXUAL Y PERSONALIDAD
with t[4]:
    st.subheader("X-XI. HISTORIA SEXUAL Y PERSONALIDAD")
    st.session_state.datos["Primer_Noviazgo"] = st.text_input("Edad primer noviazgo")
    st.session_state.datos["Primera_Relacion"] = st.text_input("Edad primera relación sexual")
    st.session_state.datos["Menarquia_Eyaculacion"] = st.text_input("Periodo menstrual / Primera eyaculación")
    st.session_state.datos["Opinion_Sexualidad"] = st.text_area("Opinión sobre masturbación, matrimonio y sexualidad")
    
    st.write("**Rasgos de Personalidad**")
    st.session_state.datos["Confianza"] = st.text_input("Confianza en otros / Celos / Rencor")
    st.session_state.datos["Impulsos"] = st.text_input("Actos impulsivos / Preocupación fracaso")

# SECCIÓN XII: SEGUIMIENTO Y CITAS (ESTA ES LA QUE FALTABA)
with t[5]:
    st.subheader("XII. SEGUIMIENTO CLÍNICO Y CITAS")
    st.session_state.datos["Observaciones"] = st.text_area("OBSERVACIONES GENERALES DEL EVALUADOR", height=200)
    st.session_state.datos["Psicologo"] = st.text_input("Nombre del Psicólogo Evaluador")
    st.session_state.datos["Fecha_Aplicacion"] = st.date_input("Fecha de hoy", value=date.today())
    
    st.divider()
    st.write("**Agenda**")
    st.session_state.datos["Proxima_Cita"] = st.date_input("Programar Próxima Cita", value=date.today())
    st.session_state.datos["Hora_Cita"] = st.time_input("Hora de la cita")
    st.session_state.datos["Evolucion"] = st.text_area("Nota de evolución / Seguimiento")

# --- BOTÓN DE PROCESAMIENTO FINAL ---
st.divider()
if st.button("🚀 GUARDAR DATOS Y GENERAR EXPEDIENTE"):
    # Validación mínima
    if st.session_state.datos.get("Nombre") and st.session_state.datos.get("Identidad"):
        
        # 1. Guardar en Excel
        df_actual = cargar_db()
        df_nuevo = pd.DataFrame([st.session_state.datos])
        # Unimos y eliminamos duplicados por identidad (mantiene el más reciente)
        df_final = pd.concat([df_actual, df_nuevo], ignore_index=True).drop_duplicates(subset=['Identidad'], keep='last')
        df_final.to_excel(DB_FILE, index=False)
        
        st.success("✅ ¡Datos guardados exitosamente en la Base de Datos Excel!")
        
        # 2. Generar Word
        doc = Document()
        doc.add_heading('PROTOCOLO DE ENTREVISTA PSICOLÓGICA - D.S.P.', 0)
        
        for k, v in st.session_state.datos.items():
            p = doc.add_paragraph()
            p.add_run(f"{k.replace('_', ' ')}: ").bold = True
            p.add_run(str(v))
        
        doc.add_paragraph("\n\n__________________________\nFirma del Evaluador")
        
        # Preparar descarga
        target = io.BytesIO()
        doc.save(target)
        target.seek(0)
        
        st.download_button(
            label="📥 DESCARGAR ARCHIVO WORD",
            data=target,
            file_name=f"Expediente_{st.session_state.datos['Identidad']}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
        # Mostrar vista previa de la base de datos
        st.write("Vista previa de la Base de Datos:")
        st.dataframe(df_final.tail(3))
        
    else:
        st.error("❌ ERROR: El Nombre y la Identidad son obligatorios para generar el archivo.")
