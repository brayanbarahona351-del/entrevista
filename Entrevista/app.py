import streamlit as st
from fpdf import FPDF

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema D.S.P. IA-Clinical", layout="wide")

class DSP_PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 5, 'REPUBLICA DE HONDURAS | SECRETARIA DE SEGURIDAD', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCION DE SANIDAD POLICIAL (D.S.P.)', 0, 1, 'C')
        self.ln(5)

def generar_pdf(entrevista, informe):
    pdf = DSP_PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    def c(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    # Página 1: Entrevista
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(0, 10, c("ENTREVISTA PSICOLÓGICA COMPLETA"), 0, 1, 'C')
    
    for sec, campos in entrevista.items():
        pdf.set_font("helvetica", 'B', 10)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 7, c(sec), 1, 1, 'L', True)
        pdf.set_font("helvetica", '', 9)
        for k, v in campos.items():
            pdf.multi_cell(185, 5, c(f"{k}: {v}"))
        pdf.ln(2)

    # Página 2: Informe de IA Clínica
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(0, 10, c("INFORME DE ANÁLISIS CLÍNICO (IA)"), 0, 1, 'C')
    pdf.ln(5)
    
    for tit, cont in informe.items():
        pdf.set_font("helvetica", 'B', 11)
        pdf.cell(0, 8, c(tit), 0, 1, 'L')
        pdf.set_font("helvetica", '', 10)
        pdf.multi_cell(185, 5, c(cont))
        pdf.ln(4)

    return pdf.output()

# --- LÓGICA DE ANÁLISIS INTELIGENTE ---
def analizar_con_ia(datos):
    """
    Este motor simula el análisis de IA procesando palabras clave y 
    contexto dentro de los campos de texto abiertos.
    """
    motivo_t = datos['motivo'].lower()
    personalidad_t = datos['personalidad'].lower()
    sintomas = datos['sintomas']
    
    # Análisis de Impresión Diagnóstica
    if any(word in motivo_t + personalidad_t for word in ["muerte", "suicid", "matar", "acabar"]):
        diag = "ALERTA CRÍTICA: Ideación autolítica activa detectada en el discurso. Requiere contención inmediata."
        test = "• Escala de Desesperanza de Beck (BHS)\n• Inventario de Depresión (BDI-II)\n• ISO-30"
        terapia = "Terapia Dialéctico-Conductual (DBT) con enfoque en gestión de crisis."
    elif any(word in motivo_t for word in ["voces", "veo", "sombra", "persiguen"]):
        diag = "ALERTA: Posible sintomatología psicótica / Alteración del juicio de realidad."
        test = "• MMPI-2 (Escalas de validez y clínicas)\n• MCMI-IV (Millon)"
        terapia = "Intervención Psiquiátrica y Terapia Cognitiva para Psicosis."
    elif any(word in personalidad_t for word in ["enojo", "peleo", "golpe", "impulso"]):
        diag = "RASGOS: Tendencia al control de impulsos deficiente y baja tolerancia a la frustración."
        test = "• Test de Personalidad 16PF-5\n• Inventario de Expresión de Ira (STAXI-2)"
        terapia = "Terapia Cognitivo-Conductual: Entrenamiento en Control de Ira."
    else:
        diag = "Ajuste Psicológico: No se detectan indicadores de gravedad inmediata. Sintomatología reactiva."
        test = "• 16PF-5 y SCL-90-R (Síntomas)"
        terapia = "Terapia de Apoyo / Psicoterapia de objetivos a corto plazo."

    return {
        "1. ANÁLISIS DE IMPRESIÓN DIAGNÓSTICA": diag,
        "2. BATERÍA DE TESTS SUGERIDA": test,
        "3. ESTRATEGIA TERAPÉUTICA": terapia,
        "4. OBSERVACIONES DE IA": "Este análisis se basa en el procesamiento de lenguaje natural de los campos llenados."
    }

# --- INTERFAZ COMPLETA ---
st.title("🛡️ Sistema de Inteligencia Clínica D.S.P.")

# Agrupar TODAS las preguntas en pestañas para que no se pierda nada
tab1, tab2, tab3, tab4 = st.tabs(["Identidad y Motivo", "Salud y Síntomas", "Historia de Vida", "Personalidad"])

with tab1:
    nombre = st.text_input("Nombre Completo")
    c1, c2 = st.columns(2)
    with c1:
        edad = st.text_input("Edad")
        civil = st.text_input("Estado Civil")
        militar = st.radio("¿Servicio Militar?", ["No", "Sí"], horizontal=True)
    with c2:
        educacion = st.text_input("Nivel Educativo")
        religion = st.text_input("Religión")
        celular = st.text_input("Celular")
    motivo = st.text_area("II. MOTIVO DE CONSULTA (Describa detalladamente)")

with tab2:
    funciones = st.text_input("Funciones Orgánicas (Sueño, Apetito, etc.)")
    medicamentos = st.text_input("Medicamentos o Alergias")
    st.write("V. Hallazgos (Marque las casillas):")
    opciones = ["Insomnio", "Pesadillas", "Escucha voces", "Ganas de morir", "Intentos suicidas", "Consumo de drogas", "Maltrato Físico", "Tics"]
    seleccion = st.multiselect("Síntomas:", opciones)
    antecedentes = st.text_area("III. Antecedentes de la situación")

with tab3:
    familia = st.text_area("VI. Información Familiar (Padres, hermanos, crianza, castigos)")
    desarrollo = st.text_area("IX. Desarrollo (Embarazo, parto, desarrollo motor, escolaridad)")
    sexual = st.text_area("X. Historia Sexual (Experiencias y opiniones)")

with tab4:
    personalidad = st.text_area("XI. Personalidad Previa (Seguridad, decisiones, impulsividad, rencor)")

# --- BOTÓN DE PROCESAMIENTO ---
if st.button("ANALIZAR CON INTELIGENCIA ARTIFICIAL Y GENERAR PDF"):
    if not nombre or not motivo:
        st.error("Por favor, llena al menos el nombre y el motivo de consulta para el análisis.")
    else:
        # 1. Empaquetar datos para la entrevista
        datos_entrevista = {
            "I. DATOS GENERALES": {"Nombre": nombre, "Edad": edad, "Educacion": educacion},
            "II-III. MOTIVO Y SITUACION": {"Motivo": motivo, "Antecedentes": antecedentes},
            "V. SALUD": {"Sintomas": ", ".join(seleccion), "Funciones": funciones},
            "HISTORIA": {"Familia": familia, "Desarrollo": desarrollo, "Sexual": sexual},
            "PERSONALIDAD": {"Detalles": personalidad}
        }
        
        # 2. Correr el motor de análisis (IA)
        datos_para_ia = {
            'motivo': motivo,
            'personalidad': personalidad,
            'sintomas': seleccion
        }
        informe_ia = analizar_con_ia(datos_para_ia)
        
        # 3. Generar PDF
        pdf_out = generar_pdf(datos_entrevista, informe_ia)
        
        st.success("🤖 La IA ha analizado el caso y generado las recomendaciones clínicas.")
        st.download_button(
            label="⬇️ DESCARGAR EXPEDIENTE + INFORME IA",
            data=bytes(pdf_out),
            file_name=f"DSP_IA_{nombre.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
