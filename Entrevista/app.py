import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN DE PANTALLA ---
st.set_page_config(page_title="D.S.P. Honduras - Protocolo Oficial", layout="wide")

# --- 2. GESTIÓN DE BASE DE DATOS LOCAL ---
DB_FILE = "DB_DSP_ENTREVISTAS_COMPLETAS.xlsx"

def cargar_db():
    if not os.path.exists(DB_FILE): return pd.DataFrame()
    try:
        return pd.read_excel(DB_FILE).astype(str).replace('nan', '')
    except:
        return pd.DataFrame()

def guardar_db(datos_dict):
    df = cargar_db()
    if not df.empty and "Identidad" in df.columns:
        df = df[df["Identidad"] != str(datos_dict["Identidad"])]
    df_final = pd.concat([df, pd.DataFrame([datos_dict])], ignore_index=True)
    df_final.to_excel(DB_FILE, index=False)

# --- 3. MOTOR DE ANÁLISIS INTEGRAL (VALIDADO) ---
def motor_ia_dsp(datos):
    # Consolidamos texto para evitar falsos positivos
    cuerpo = f"{datos.get('motivo', '')} {datos.get('opinion', '')}".lower().strip()
    checks = datos.get('checks', [])
    
    if len(cuerpo) < 10 and not checks:
        return "PENDIENTE", "Debe completar información en el motivo o síntomas para generar análisis.", "N/A"

    if any(x in cuerpo for x in ["suicid", "muerte", "matar", "ganas de morir"]) or "Intentos suicidas" in checks or "Ganas de morir" in checks:
        return "ALERTA: Riesgo Autolítico Alto", "Remisión inmediata a Psiquiatría y vigilancia 24/7.", "Beck (Desesperanza), BDI-II, Escala de Ideación Suicida."
    elif any(x in cuerpo for x in ["voces", "alucinacion", "extrañas"]) or "Escucha voces" in checks:
        return "INDICADOR: Posible Psicosis u Organicidad", "Interconsulta con Neurología y Psiquiatría para descartar daño orgánico.", "Bender-Gestalt, SCL-90-R, MMPI-2."
    elif "Consumo de drogas" in checks or "alcohol" in cuerpo:
        return "PERFIL: Trastorno por Consumo de Sustancias", "Abordaje terapéutico en adicciones y seguimiento por bienestar policial.", "AUDIT, DAST-10."
    else:
        return "ESTADO: Reacción de Ajuste / Estrés", "Psicoterapia breve de apoyo y técnicas de higiene mental.", "16PF-5, HTP (Persona-Casa-Árbol), Inventario de Ansiedad."

# --- 4. INTERFAZ BASADA EN EL PROTOCOLO D.S.P. ---
st.title("🛡️ Protocolo de Entrevista Psicológica para Adultos - D.S.P.")
st.markdown("---")

tabs = st.tabs([
    "I-II. Identificación y Motivo", 
    "III-V. Salud y Síntomas", 
    "VI. Historia Familiar", 
    "VII-IX. Social y Hábitos", 
    "X. Desarrollo y Sexo", 
    "XI-XII. Personalidad y Cierre"
])

# SECCIÓN I Y II [cite: 7, 25]
with tabs[0]:
    st.subheader("I. DATOS GENERALES")
    c1, c2, c3 = st.columns(3)
    nombre = c1.text_input("Nombre Completo")
    f_nac = c2.text_input("Lugar y Fecha de Nacimiento")
    nacionalidad = c3.text_input("Nacionalidad", value="Hondureña")
    
    c4, c5, c6 = st.columns(3)
    identidad = c4.text_input("Número de Identidad (Sin guiones)")
    edad = c5.text_input("Edad")
    sexo = c6.selectbox("Sexo", ["M", "F"])
    
    c7, c8, c9 = st.columns(3)
    est_civil = c7.text_input("Estado Civil")
    religion = c8.text_input("Religión")
    celular = c9.text_input("Número Celular")
    
    c10, c11 = st.columns(2)
    ocupacion = c10.text_input("Ocupación actual")
    asignacion = c11.text_input("Asignación o Unidad Policial")
    
    c12, c13, c14 = st.columns(3)
    militar = c12.radio("¿Prestó servicio militar?", ["No", "Sí"])
    nivel_edu = c13.text_input("Nivel Educativo")
    pasatiempo = c14.text_input("Pasatiempos / Deportes")
    
    direccion = st.text_input("Dirección Actual")
    remitido = st.text_input("Remitido por")

    st.subheader("II. MOTIVO DE CONSULTA")
    motivo = st.text_area("Describa detalladamente el motivo de la consulta:")

# SECCIÓN III, IV Y V [cite: 28, 51, 57]
with tabs[1]:
    st.subheader("III. ANTECEDENTES CLÍNICOS Y PSICOLÓGICOS")
    ant_clinicos = st.text_area("Desarrollo de síntomas (¿Cuándo comenzó la situación actual?)")
    funciones = st.text_input("Funciones orgánicas (Sueño, apetito, sed, defecación)")
    
    c15, c16 = st.columns(2)
    alergias = c15.text_input("¿Padece alergias? Cuales?")
    meds = c16.text_input("¿Toma medicamentos? Para qué?")
    
    enf_inf = st.text_input("Enfermedades de la infancia")
    hosp = st.text_input("Hospitalizaciones e Intervenciones Quirúrgicas (Motivo)")

    st.subheader("V. SALUD FÍSICA Y SÍNTOMAS")
    # Tabla consolidada del PDF [cite: 70]
    lista_sintomas = [
        "Insomnio", "Mareos o desmayos", "Comerse las uñas", "Accidentes", "Pesadillas", 
        "Intentos suicidas", "Maltrato Físico", "Tartamudez", "Escucha voces", 
        "Caminar dormido", "Miedos o fobias", "Cólico y/o Diarrea tensional", 
        "Golpes en la cabeza", "Hablar dormido", "Ver cosas extrañas", "Convulsiones", 
        "Orinarse en las cama", "Ganas de morir", "Fiebre", "Problemas de aprendizaje", 
        "Consumo de drogas", "Repitencia Escolar", "Asma", "Tics nerviosos", 
        "Estreñimiento", "Sudoración en las manos"
    ]
    seleccionados = st.multiselect("Marque con una X lo que ha presentado en su vida:", lista_sintomas)

# SECCIÓN VI [cite: 72, 81, 95]
with tabs[2]:
    st.subheader("VI. INFORMACIÓN FAMILIAR")
    st.write("**Datos del Conyugue / Pareja**")
    cony_nom = st.text_input("Nombre del Conyugue")
    cony_det = st.text_input("Edad, Ocupación y Enfermedades", key="cony_det")
    cony_rel = st.text_area("Describa la relación de pareja:")
    
    st.write("**Datos de los Padres**")
    c17, c18 = st.columns(2)
    with c17:
        p_nom = st.text_input("Nombre del Padre")
        p_det = st.text_input("Edad, Vivo/Muerto, Ocupación, Salud", key="padre_det")
        p_rel = st.text_area("Relación con el padre e imposición de castigos:")
    with c18:
        m_nom = st.text_input("Nombre de la Madre")
        m_det = st.text_input("Edad, Vivo/Muerto, Ocupación, Salud", key="madre_det")
        m_rel = st.text_area("Relación con la madre e imposición de castigos:")
    
    st.write("**Dinámica y Antecedentes**")
    p_ec = st.text_input("Estado civil de los padres / Motivo de separación")
    hermanos = st.text_input("Número de hermanos, posición que ocupa y con quién se lleva mejor")
    crianza = st.text_input("¿Quién lo crió? (Escriba parentesco)")
    p_opinion = st.text_area("¿Qué opina de sus padres? ¿Existen antecedentes de alcoholismo o maltrato?")
    hist_feliz = st.text_area("Cuénteme una historia feliz vivida en familia:")

# SECCIÓN VII, VIII Y IX [cite: 130, 140, 149]
with tabs[3]:
    st.subheader("VII. SOCIAL / AMBIENTAL")
    social = st.text_area("Conducta en el trabajo, rendimiento, estrés y cambios laborales:")
    ley = st.text_input("¿Dificultades con la ley o catástrofes sufridas?")
    
    st.subheader("VIII Y IX. HÁBITOS Y ASPECTOS JUDICIALES")
    c19, c20 = st.columns(2)
    fuma = c19.text_input("Fuma (Cantidad al día)")
    alcohol = c20.text_input("Ingesta de alcohol (Frecuencia)")
    drogas = st.text_input("Consumo de drogas o antecedentes judiciales (Detenido/Preso)")

# SECCIÓN X [cite: 169, 183]
with tabs[4]:
    st.subheader("X. ANTECEDENTES DEL DESARROLLO E HISTORIA SEXUAL")
    st.write("**Primeros Años y Educación**")
    embarazo = st.text_input("Circunstancia del embarazo y tipo de parto")
    motor = st.text_input("Desarrollo motor (Gatear, caminar) y control de esfínteres")
    escuela = st.text_area("Historia escolar (Edad de inicio, materias difíciles, repitencia):")
    
    st.write("**Historia Sexual**")
    sex_info = st.text_input("Información sexual adquirida / Menarquia o Primera eyaculación")
    noviazgo = st.text_input("Edad primer noviazgo y opinión del matrimonio")
    rel_sex = st.text_area("Edad primera relación y opinión de masturbación/sexualidad:")

# SECCIÓN XI Y XII [cite: 191, 200]
with tabs[5]:
    st.subheader("XI. PERSONALIDAD PREVIA")
    c21, c22 = st.columns(2)
    pers_a = c21.text_input("Seguridad en sí mismo / Toma de decisiones")
    pers_b = c22.text_input("Miedo al abandono / Confianza en otros")
    pers_c = c21.text_input("Rencor / Celos / Timidez")
    pers_d = c22.text_input("Actos impulsivos / Preocupación por el fracaso")
    
    st.subheader("XII. OBSERVACIONES GENERALES Y ANÁLISIS")
    opinion_prof = st.text_area("OPINIÓN PROFESIONAL (Basado en la entrevista y observación):")
    
    if st.button("🧠 GENERAR ANÁLISIS CLÍNICO"):
        datos_ia = {"motivo": motivo, "opinion": opinion_prof, "checks": seleccionados}
        res, rec, tst = motor_ia_dsp(datos_ia)
        st.session_state["ia_res"] = res
        st.session_state["ia_rec"] = rec
        st.session_state["ia_tst"] = tst

    if "ia_res" in st.session_state:
        st.divider()
        st.info(f"**Conclusión IA:** {st.session_state['ia_res']}")
        st.success(f"**Recomendación:** {st.session_state['ia_rec']}")
        st.warning(f"**Batería Sugerida:** {st.session_state['ia_tst']}")

    psicologo = st.text_input("Nombre del Psicólogo Evaluador [cite: 201]")
    fecha = st.date_input("Fecha de Aplicación", value=date.today())

# --- 5. GUARDADO Y EXPORTACIÓN ---
if st.button("💾 GUARDAR REGISTRO Y GENERAR INFORME WORD"):
    if identidad and nombre:
        # Diccionario consolidado
        registro = {
            "Identidad": identidad, "Nombre": nombre, "Motivo": motivo,
            "Sintomas": str(seleccionados), "Opinion_Prof": opinion_prof,
            "Conclusion_IA": st.session_state.get("ia_res", "N/A"),
            "Recomendacion": st.session_state.get("ia_rec", "N/A"),
            "Psicologo": psicologo, "Fecha": str(fecha)
        }
        guardar_db(registro)
        
        # Generar Word profesional
        doc = Document()
        doc.add_heading('POLICÍA NACIONAL - D.S.P.', 0)
        doc.add_heading('ENTREVISTA PSICOLÓGICA PARA ADULTOS', level=1)
        doc.add_paragraph(f"Paciente: {nombre} | ID: {identidad}")
        doc.add_paragraph(f"Motivo de Consulta: {motivo}")
        doc.add_heading('Análisis y Recomendaciones', level=2)
        doc.add_paragraph(f"Impresión: {st.session_state.get('ia_res', 'Pendiente')}")
        doc.add_paragraph(f"Sugerencias: {st.session_state.get('ia_rec', 'Pendiente')}")
        doc.add_paragraph(f"\nFirma: {psicologo}")
        
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        st.success("✅ Datos guardados en Excel.")
        st.download_button("📥 DESCARGAR INFORME EN WORD", buf, f"Entrevista_{identidad}.docx")
    else:
        st.error("Faltan campos obligatorios (Identidad y Nombre).")
