import streamlit as st
from fpdf import FPDF

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IA Clínica - D.S.P. Honduras", layout="wide")

class DSP_PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 5, 'REPUBLICA DE HONDURAS | SECRETARIA DE SEGURIDAD', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCION DE SANIDAD POLICIAL (D.S.P.)', 0, 1, 'C')
        self.ln(5)

def generar_pdf(datos_entrevista, informe_ia):
    pdf = DSP_PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    def c(t):
        return str(t).encode('latin-1', 'replace').decode('latin-1')

    pdf.add_page()
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, c("ENTREVISTA PSICOLÓGICA COMPLETA"), 0, 1, 'C')

    for seccion, campos in datos_entrevista.items():
        pdf.set_font("helvetica", 'B', 10)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 7, c(seccion), 1, 1, 'L', True)
        pdf.set_font("helvetica", '', 9)
        for k, v in campos.items():
            pdf.multi_cell(185, 5, c(f"{k}: {v}"))
        pdf.ln(2)

    return pdf.output()

# --- INTERFAZ ---
st.title("📋 Expediente Oficial D.S.P. - Honduras")

t1, t2, t3, t4, t5 = st.tabs(["I. Generales", "II-V. Motivo y Salud", "VI. Familia", "VII-IX. Desarrollo", "X-XI. Personalidad"])

with t1:
    nombre = st.text_input("Nombre Completo")
    edad = st.text_input("Edad")
    militar = st.radio("¿Servicio Militar?", ["No", "Sí"], horizontal=True)
    educacion = st.text_input("Nivel Educativo")
    ocupacion = st.text_input("Ocupación/Asignación")

with t2:
    motivo = st.text_area("II. Motivo de consulta")
    sintomas = st.multiselect("V. Hallazgos:", ["Insomnio", "Ganas de morir", "Escucha voces", "Agresividad", "Tics"])
    antecedentes = st.text_area("III. Antecedentes de la situación")
    funciones = st.text_input("Funciones Orgánicas (Sueño, Apetito, etc.)")

with t3:
    hermanos = st.text_input("Número de hermanos y posición")
    padres = st.text_area("Relación con padres y castigos")
    conyugue = st.text_input("Cónyuge (Nombre, salud, relación)")
    familia_ant = st.text_area("Antecedentes familiares (Alcoholismo, enfermedad mental)")

with t4:
    embarazo = st.text_input("Embarazo y Parto")
    desarrollo_motor = st.text_input("Desarrollo motor y lenguaje")
    escolar = st.text_area("Historia escolar")
    social = st.text_area("Situación social y legal")

with t5:
    sexual = st.text_area("X. Historia Sexual")
    personalidad = st.text_area("XI. Personalidad Previa (Impulsividad, rencor, celos)")

# --- BOTÓN DE PROCESAMIENTO ---
if st.button("ANALIZAR Y GENERAR PDF"):
    if not nombre or not motivo:
        st.error("Por favor rellene Nombre y Motivo de Consulta.")
    else:
        # 1. Simulación de Análisis IA
        info_ia = {
            "ANÁLISIS": "Análisis clínico automatizado finalizado.",
            "RECOMENDACIÓN": "Aplicar pruebas según perfiles detectados en el discurso."
        }
        
        # 2. Estructura para el PDF
        datos = {
            "I. DATOS GENERALES": {"Nombre": nombre, "Edad": edad, "Militar": militar, "Educación": educacion},
            "II-V. MOTIVO Y SALUD": {"Motivo": motivo, "Síntomas": ", ".join(sintomas), "Funciones": funciones},
            "VI. FAMILIA": {"Hermanos": hermanos, "Padres": padres, "Cónyuge": conyugue, "Antecedentes": familia_ant},
            "VII-IX. DESARROLLO": {"Embarazo": embarazo, "Motor": desarrollo_motor, "Escolar": escolar, "Social": social},
            "X-XI. SEXUALIDAD Y PERSONALIDAD": {"Sexual": sexual, "Personalidad": personalidad}
        }
        
        # 3. Generar PDF y convertir a Bytes
        pdf_out = generar_pdf(datos, info_ia)
        pdf_bytes = bytes(pdf_out)
        
        st.success("✅ Documento generado correctamente.")
        
        # 4. Botón de descarga corregido
        st.download_button(
            label="⬇️ Descargar PDF Completo",
            data=pdf_bytes,
            file_name=f"DSP_{nombre.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
