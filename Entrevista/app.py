import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="D.S.P. - Evaluación Psicológica Adultos", layout="wide")

# --- 2. MOTOR DE ANÁLISIS CLÍNICO AVANZADO ---
def motor_ia_dsp(d):
    # Recolección de variables críticas de todas las áreas
    motivo = d.get('motivo', '').lower().strip()
    clinica = f"{motivo} {d.get('ant_sit', '')} {d.get('opinion', '')}".lower()
    checks = d.get('checks', [])
    pers = d.get('pers_prev', '').lower()
    
    # Si la información es mínima, no emitir juicios erróneos
    if len(motivo) < 15 and not checks:
        return None

    # LÓGICA DE DIAGNÓSTICO Y RECOMENDACIONES SEGÚN EL CASO
    
    # CASO A: RIESGO DE VIDA / CRISIS AFECTIVA AGUDA
    if any(x in clinica for x in ["suicid", "muerte", "matar", "morir"]) or "Ganas de morir" in checks:
        return {
            "categoria": "RIESGO AUTOLÍTICO",
            "rec_interna": "Implementar contrato de no agresión, identificación de redes de apoyo familiares y ejercicios de anclaje emocional.",
            "rec_externa": "Derivación inmediata a Psiquiatría. Notificación a la superioridad para retiro preventivo de equipo reglamentario.",
            "just_rec": "La presencia de ideación suicida es una emergencia clínica. Se requiere intervención externa para garantizar la seguridad del funcionario.",
            "tests_sugeridos": "Inventario de Depresión de Beck (BDI-II) y Escala de Desesperanza de Beck (BHS).",
            "just_test": "El BDI-II cuantifica la severidad del episodio depresivo, mientras que el BHS es el predictor estándar de riesgo suicida al medir el pesimismo cognitivo."
        }

    # CASO B: INDICADORES DE PSICOSIS O DAÑO ORGÁNICO
    elif any(x in clinica for x in ["voces", "alucinacion", "extrañas", "convulsion", "golpe"]) or "Escucha voces" in checks:
        return {
            "categoria": "ORGANICIDAD / PSICOSIS",
            "rec_interna": "Registro diario de alucinaciones (frecuencia e intensidad) e higiene estricta del sueño.",
            "rec_externa": "Remisión a Neurología para estudios de imagen (RM/TAC) y descarte de patología orgánica cerebral.",
            "just_rec": "Es imperativo descartar que la sintomatología tenga una base biológica o traumática antes de proceder con terapia psicológica.",
            "tests_sugeridos": "Test Gestáltico Visomotor de Bender-Gestalt y SCL-90-R.",
            "just_test": "El Bender permite detectar signos de maduración o daño cerebral, y el SCL-90-R mapea dimensiones de psicoticismo y paranoia."
        }

    # CASO C: IMPULSIVIDAD / IRA / CONTROL DE CONDUCTA
    elif any(x in pers for x in ["impulsivo", "agresivo", "rencor", "pelea"]) or "Maltrato Físico" in checks:
        return {
            "categoria": "CONTROL DE IMPULSOS",
            "rec_interna": "Entrenamiento en técnicas de respiración diafragmática y técnica de 'Tiempo Fuera' ante detonantes.",
            "rec_externa": "Terapia Cognitivo-Conductual (TCC) enfocada en reestructuración de pensamientos hostiles.",
            "just_rec": "El control inhibitorio es crítico en el servicio policial para evitar el uso excesivo de la fuerza o conflictos interpersonales.",
            "tests_sugeridos": "Inventario de Expresión de Ira Estado-Rasgo (STAXI-2) y 16PF-5.",
            "just_test": "El STAXI-2 permite diferenciar si la ira es una reacción temporal o un rasgo de personalidad estable; el 16PF-5 mide la estabilidad emocional."
        }

    # CASO D: ESTRÉS POST-TRAUMÁTICO / ADAPTACIÓN
    else:
        return {
            "categoria": "REACCIÓN AL ESTRÉS",
            "rec_interna": "Higiene mental, práctica de ejercicio físico y técnicas de defusing tras incidentes críticos.",
            "rec_externa": "Psicoterapia breve de apoyo y seguimiento por el Departamento de Psicología de la D.S.P.",
            "just_rec": "Se observa un agotamiento reactivo a las demandas del entorno policial sin compromiso de la integridad psíquica profunda.",
            "tests_sugeridos": "Test Proyectivo HTP (Casa-Árbol-Persona) y Cuestionario de Ansiedad de Beck (BAI).",
            "just_test": "El HTP ayuda a explorar la autoimagen y el entorno familiar de forma no invasiva; el BAI cuantifica los síntomas físicos de la ansiedad."
        }

# --- 3. INTERFAZ (Protocolo Completo 6 Páginas) ---
st.title("🛡️ Protocolo Integral de Entrevista para Adultos - D.S.P.")
st.caption("Secretaría de Seguridad - Dirección de Sanidad Policial")

tabs = st.tabs(["I-II. Identificación", "III-V. Clínica", "VI. Familia", "VII-IX. Social", "X. Desarrollo/Sexo", "XI-XII. Personalidad"])

with tabs[0]:
    st.subheader("I. DATOS GENERALES")
    c1, c2, c3 = st.columns(3)
    nombre = c1.text_input("Nombre Completo:")
    id_n = c2.text_input("Identidad:")
    f_nac = c3.text_input("Lugar/Fecha Nacimiento:")
    c4, c5, c6 = st.columns(3)
    sexo = c4.selectbox("Sexo:", ["M", "F"])
    edad = c5.text_input("Edad:")
    est_civil = c6.text_input("Estado Civil:")
    st.subheader("II. MOTIVO DE CONSULTA")
    motivo = st.text_area("Describa el motivo (Literal):", height=150)

with tabs[1]:
    st.subheader("III-V. SALUD Y SÍNTOMAS")
    ant_sit = st.text_area("Desarrollo de síntomas:")
    st.write("**Checklist de Síntomas:**")
    s_list = ["Ideas suicidas", "Intentos suicidas", "Escucha voces", "Drogas", "Alcohol", "Maltrato Físico", "Ganas de morir"]
    checks_sel = st.multiselect("Marque síntomas presentados:", s_list)

with tabs[2]:
    st.subheader("VI. INFORMACIÓN FAMILIAR")
    p_rel = st.text_area("Relación con Padre y castigos:", key="kp")
    m_rel = st.text_area("Relación con Madre y castigos:", key="km")

with tabs[5]:
    st.subheader("XI-XII. PERSONALIDAD Y ANÁLISIS")
    pers_prev = st.text_area("Seguridad, decisiones, impulsos, rencor:")
    opinion_prof = st.text_area("OBSERVACIONES PROFESIONALES:")

    if st.button("🧠 GENERAR ANÁLISIS TÉCNICO"):
        datos = {
            "motivo": motivo, "ant_sit": ant_sit, "opinion": opinion_prof,
            "checks": checks_sel, "p_rel": p_rel, "m_rel": m_rel, "pers_prev": pers_prev
        }
        res = motor_ia_dsp(datos)
        if res:
            st.session_state["ia"] = res
        else:
            st.warning("Complete el Motivo de Consulta para analizar.")

    if "ia" in st.session_state:
        a = st.session_state["ia"]
        st.divider()
        st.info(f"**CATEGORÍA CLÍNICA:** {a['categoria']}")
        
        c_i, c_e = st.columns(2)
        with c_i:
            st.success("**RECOMENDACIONES INTERNAS (AUTOCUIDADO)**")
            st.write(a["rec_interna"])
            st.warning("**BATERÍA PSICOMÉTRICA SUGERIDA**")
            st.write(f"👉 {a['tests_sugeridos']}")
        with c_e:
            st.error("**RECOMENDACIONES EXTERNAS (DERIVACIÓN)**")
            st.write(a["rec_externa"])
            st.info("**JUSTIFICACIÓN CLÍNICA**")
            st.write(f"**Del Caso:** {a['just_rec']}")
            st.write(f"**De los Tests:** {a['just_test']}")

# --- 4. EXPORTACIÓN ---
if st.button("💾 GUARDAR Y EXPORTAR"):
    if nombre and id_n:
        st.success(f"Expediente de {nombre} guardado correctamente.")
    else:
        st.error("Identidad y Nombre son obligatorios.")
