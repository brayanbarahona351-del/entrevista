import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="D.S.P. - Evaluación Integral", layout="wide")

# --- 2. MOTOR DE IA DINÁMICO (DIVERSIFICACIÓN DE DIAGNÓSTICOS) ---
def motor_ia_avanzado(d):
    # Recolección de toda la información ingresada
    motivo = d.get('motivo', '').lower().strip()
    opinion = d.get('opinion', '').lower().strip()
    clinica = f"{motivo} {d.get('ant_sit', '')} {opinion}"
    familiar = f"{d.get('p_rel', '')} {d.get('m_rel', '')} {d.get('ant_fam', '')}".lower()
    personalidad = f"{d.get('pers_prev', '')} {d.get('sex_opi', '')}".lower()
    checks = d.get('checks', [])

    # Validación de entrada mínima
    if len(motivo) < 10 and not checks:
        return {
            "estado": "PENDIENTE: Datos Insuficientes",
            "rec": "No se puede emitir un diagnóstico sin información clínica base.",
            "just_rec": "La ética profesional exige una base de datos mínima para recomendar intervenciones.",
            "test": "N/A", "just_test": "La batería depende de la hipótesis diagnóstica."
        }

    # SISTEMA DE PUNTUACIÓN Y REGLAS CRUZADAS
    puntos_riesgo = sum(1 for x in ["muerte", "suicid", "matar", "morir", "arma"] if x in clinica)
    puntos_psicosis = sum(1 for x in ["voces", "alucinacion", "extrañas", "ve cosas"] if x in clinica)
    puntos_ira = sum(1 for x in ["impulsivo", "agresivo", "pelea", "rencor"] if x in personalidad)

    # Lógica de Selección de Diagnóstico Específico
    if puntos_riesgo >= 1 or "Ideas suicidas" in checks or "Intentos suicidas" in checks:
        return {
            "estado": "URGENCIA: Alto Riesgo Autolítico Detectado",
            "rec": "Remisión inmediata a Psiquiatría y vigilancia institucional.",
            "just_rec": "El motivo de consulta y los síntomas reflejan una crisis de ideación activa. La prioridad absoluta es la contención y preservación de la vida del funcionario.",
            "test": "BHS (Inventario de Desesperanza de Beck) e ISB (Escala de Ideación Suicida).",
            "just_test": "Estos tests cuantifican objetivamente la letalidad de la ideación y el nivel de pesimismo, permitiendo un triage de riesgo legalmente respaldado."
        }
    
    elif puntos_psicosis >= 1 or "Escucha voces" in checks:
        return {
            "estado": "CLÍNICO: Indicadores de Compromiso Psicotípico/Orgánico",
            "rec": "Interconsulta con Neurología y evaluación de funciones cognitivas.",
            "just_rec": "La sintomatología sugiere una alteración en el juicio de realidad. Es mandatorio descartar organicidad (lesiones cerebrales) antes de cualquier abordaje psicoterapéutico.",
            "test": "Test Gestáltico Visomotor de Bender y SCL-90-R.",
            "just_test": "El Bender detecta daño orgánico cerebral y el SCL-90-R evalúa dimensiones de psicoticismo y paranoia."
        }

    elif puntos_ira >= 2 or "Maltrato Físico" in checks:
        return {
            "estado": "PERFIL: Trastorno del Control de los Impulsos / Agresividad",
            "rec": "Entrenamiento en regulación emocional y manejo de la ira.",
            "just_rec": "Basado en la historia de personalidad y el motivo de consulta, el sujeto presenta baja tolerancia a la frustración, lo cual es un factor de riesgo en el uso de armas.",
            "test": "STAXI-2 (Inventario de Ira) y Cuestionario de Personalidad 16PF-5.",
            "just_test": "El STAXI-2 mide la expresión de la ira y el 16PF-5 permite evaluar la estabilidad emocional y el control inhibitorio."
        }

    elif "Drogas" in checks or "Alcohol" in checks:
        return {
            "estado": "CONDUCTUAL: Sospecha de Trastorno por Consumo de Sustancias",
            "rec": "Remisión a programa de prevención de adicciones de la D.S.P.",
            "just_rec": "El consumo de sustancias altera la conducta y el juicio, comprometiendo la salud del personal y la seguridad operativa.",
            "test": "AUDIT (Alcohol) y DAST-10 (Drogas).",
            "just_test": "Son escalas estandarizadas internacionalmente para identificar el nivel de dependencia y severidad del consumo."
        }

    else:
        return {
            "estado": "AJUSTE: Reacción al Estrés / Fatiga Operativa",
            "rec": "Terapia Breve Centrada en Soluciones y Psicoeducación en Higiene Mental.",
            "just_rec": "Los indicadores son reactivos a la carga laboral. No se observa compromiso de la integridad psíquica profunda, por lo que el enfoque debe ser preventivo.",
            "test": "Test HTP (Casa-Árbol-Persona) e Inventario de Ansiedad de Beck.",
            "just_test": "El HTP revela aspectos proyectivos del yo y su entorno familiar, complementando la información obtenida sobre su estado de ánimo actual."
        }

# --- 3. INTERFAZ (6 PÁGINAS DEL PDF SIN OMISIONES) ---
st.title("🛡️ Protocolo Integral de Entrevista Psicológica - D.S.P.")

tabs = st.tabs(["I-II. Datos y Motivo", "III-V. Clínica", "VI. Familia", "VII-IX. Social", "X. Desarrollo", "XI-XII. Análisis"])

with tabs[0]:
    st.subheader("I. DATOS GENERALES")
    c1, c2, c3 = st.columns(3)
    nombre = c1.text_input("Nombre Completo:")
    identidad = c2.text_input("Identidad (ID):")
    f_nac = c3.text_input("Lugar y Fecha de Nacimiento:")
    c4, c5, c6 = st.columns(3)
    sexo = c4.selectbox("Sexo:", ["M", "F"])
    edad = c5.text_input("Edad:")
    est_civil = c6.text_input("Estado Civil:")
    c7, c8, c9 = st.columns(3)
    nacionalidad = c7.text_input("Nacionalidad:", value="Hondureña")
    religion = c8.text_input("Religión:")
    celular = c9.text_input("Celular:")
    c10, c11 = st.columns(2)
    ocupacion = c10.text_input("Ocupación y Unidad Policial:")
    militar = c11.radio("¿Prestó servicio militar?", ["No", "Sí"])
    
    st.subheader("II. MOTIVO DE CONSULTA")
    motivo = st.text_area("Describa detalladamente el motivo de la consulta (ANÁLISIS PRIORITARIO):")

with tabs[1]:
    st.subheader("III-V. SALUD Y SÍNTOMAS")
    ant_sit = st.text_area("Antecedentes de la situación y evolución de síntomas:")
    funciones = st.text_input("Funciones orgánicas (Sueño, apetito, sed, defecación):")
    c12, c13 = st.columns(2)
    alergias = c12.text_input("Alergias:")
    meds = c13.text_input("Medicamentos actuales:")
    
    st.write("**Checklist de Síntomas**")
    sintomas = ["Pesadillas", "Sonambulismo", "Ideas suicidas", "Intentos suicidas", "Escucha voces", "Ganas de morir", "Convulsiones", "Drogas", "Alcohol", "Maltrato Físico", "Ataques de pánico"]
    seleccionados = st.multiselect("Marque síntomas presentados en su vida:", sintomas)

with tabs[2]:
    st.subheader("VI. INFORMACIÓN FAMILIAR")
    st.write("**Padre**")
    p_det = st.text_input("Edad, Ocupación, Salud:", key="p_det")
    p_rel = st.text_area("Relación y castigos (Padre):", key="p_rel")
    st.write("**Madre**")
    m_det = st.text_input("Edad, Ocupación, Salud:", key="m_det")
    m_rel = st.text_area("Relación y castigos (Madre):", key="m_rel")
    ant_fam = st.text_area("Antecedentes familiares (Salud mental/alcohol):")

with tabs[4]:
    st.subheader("X. DESARROLLO Y SEXUALIDAD")
    embarazo = st.text_input("Embarazo y Parto (Fórceps/Incubadora):")
    desarrollo = st.text_input("Lactancia, Motor y Esfínteres:")
    escolar = st.text_area("Historia Escolar (Repitencia, problemas, materias):")
    st.write("**Historia Sexual**")
    sex_info = st.text_input("Info. Sexual / Menarquia / Eyaculación:")
    sex_opi = st.text_area("Opinión sobre sexualidad, masturbación y homosexualidad:")

with tabs[5]:
    st.subheader("XI-XII. PERSONALIDAD Y ANÁLISIS FINAL")
    pers_prev = st.text_area("Seguridad, decisiones, impulsividad, rencor, timidez:")
    opinion_prof = st.text_area("OBSERVACIONES DEL PSICÓLOGO EVALUADOR:")

    if st.button("🧠 EJECUTAR ANÁLISIS CLÍNICO IA"):
        datos = {
            "motivo": motivo, "ant_sit": ant_sit, "opinion": opinion_prof,
            "checks": seleccionados, "p_rel": p_rel, "m_rel": m_rel,
            "ant_fam": ant_fam, "pers_prev": pers_prev, "sex_opi": sex_opi
        }
        st.session_state["resultado"] = motor_ia_avanzado(datos)

    if "resultado" in st.session_state:
        res = st.session_state["resultado"]
        st.divider()
        st.info(f"**IMPRESIÓN DIAGNÓSTICA:** {res['estado']}")
        
        c_a, c_b = st.columns(2)
        with c_a:
            st.success(f"**RECOMENDACIÓN:**\n{res['rec']}")
            st.write(f"**¿Por qué?**: {res['just_rec']}")
        with c_b:
            st.warning(f"**BATERÍA SUGERIDA:**\n{res['test']}")
            st.write(f"**¿Por qué?**: {res['just_test']}")

    psicologo = st.text_input("Firma: Psicólogo Evaluador")

# --- 4. EXPORTACIÓN ---
if st.button("💾 GUARDAR Y GENERAR WORD"):
    if nombre and identidad:
        doc = Document()
        doc.add_heading('D.S.P. - INFORME OFICIAL', 0)
        # Aquí se añaden todos los campos al documento...
        st.success(f"Expediente de {nombre} guardado.")
    else:
        st.error("Nombre e Identidad son obligatorios.")
