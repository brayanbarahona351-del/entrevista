import streamlit as st
from fpdf import FPDF

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Sistema IA D.S.P. - Honduras", layout="wide")

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
    
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(0, 10, c("ENTREVISTA PSICOLOGICA Y RESULTADOS IA"), 0, 1, 'C')
    
    for sec, campos in entrevista.items():
        pdf.set_font("helvetica", 'B', 10)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 7, c(sec), 1, 1, 'L', True)
        pdf.set_font("helvetica", '', 9)
        for k, v in campos.items():
            pdf.multi_cell(185, 5, c(f"{k}: {v}"))
        pdf.ln(2)

    pdf.add_page()
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(0, 10, c("INFORME CLINICO DE IA Y BATERIA RECOMENDADA"), 0, 1, 'C')
    pdf.ln(5)
    for tit, cont in informe.items():
        pdf.set_font("helvetica", 'B', 11)
        pdf.cell(0, 8, c(tit), 0, 1, 'L')
        pdf.set_font("helvetica", '', 10)
        pdf.multi_cell(185, 5, c(cont))
        pdf.ln(3)
    return pdf.output()

# --- MOTOR DE IA CON TUS ENLACES ---
def motor_ia_dsp(motivo, personalidad, sintomas):
    texto_analizar = (motivo + " " + personalidad).lower()
    
    # Tus enlaces de Google Drive
    folder_psicometria = "https://drive.google.com/drive/folders/1lrH7AKPKXOVeFkcc_EdO03E0Ar5k4wbv"
    folder_proyectivos = "https://drive.google.com/drive/folders/1yji6O5YIcYOjW1IG0fIhp4MJZgrcToys"

    # Lógica de recomendación
    tests = []
    diag = "Paciente orientado en tiempo y espacio. Discurso coherente."
    
    # Análisis por palabras clave
    if any(x in texto_analizar for x in ["triste", "morir", "suicid", "lloro", "solo"]):
        diag = "INDICADORES DEPRESIVOS / RIESGO AUTOLITICO: Se observa un discurso con carga afectiva negativa y desesperanza."
        tests.append(f"Pruebas de Personalidad Profunda (MMPI-2/16PF): {folder_psicometria}")
    
    if any(x in texto_analizar for x in ["voces", "sombras", "paranoid", "persiguen"]):
        diag = "INDICADORES PSICOTICOS: El relato sugiere alteraciones en la percepcion de la realidad."
        tests.append(f"Bateria Proyectiva (HTP / Figura Humana): {folder_proyectivos}")
    
    if any(x in texto_analizar for x in ["enojo", "golpe", "ira", "peleo", "impulsivo"]):
        diag = "CONTROL DE IMPULSOS: Rasgos de personalidad con tendencia a la agresividad reactiva."
        tests.append(f"Test de Personalidad (16PF / IPV para policias): {folder_psicometria}")

    if not tests:
        diag = "AJUSTE PSICOLOGICO NORMAL: No se detectan indicadores de psicopatologia aguda."
        tests.append(f"Evaluacion de Rutina (Barsit / 16PF): {folder_psicometria}")

    return {
        "IMPRESION DIAGNOSTICA (ANALISIS IA)": diag,
        "BATERIA DE TESTS RECOMENDADA (TUS ENLACES)": "\n".join(tests),
        "PLAN TERAPEUTICO SUGERIDO": "Terapia Cognitivo-Conductual y seguimiento por el Depto. de Psicologia."
    }

# --- INTERFAZ ---
st.title("🧠 Asistente Clinico IA - Sanidad Policial")

with st.form("formulario_dsp"):
    st.subheader("I. Datos Generales")
    nombre = st.text_input("Nombre del Evaluado")
    c1, c2 = st.columns(2)
    edad = c1.text_input("Edad")
    militar = c2.selectbox("¿Servicio Militar?", ["No", "Si"])
    
    st.subheader("II. Motivo de Consulta")
    motivo_input = st.text_area("Describa el motivo detalladamente (La IA analizara este texto)")
    
    st.subheader("V. Tabla de Sintomas")
    s_lista = ["Ganas de morir", "Escucha voces", "Insomnio", "Consumo drogas", "Agresividad"]
    seleccion = st.multiselect("Sintomas detectados:", s_lista)
    
    st.subheader("XI. Rasgos de Personalidad")
    perso_input = st.text_area("Describa rasgos observados (Seguridad, impulsividad, etc.)")
    
    # El resto de campos (Familia, Desarrollo, etc.) se omiten aqui por brevedad pero deben ir
    submitted = st.form_submit_button("Analizar Caso y Generar PDF")

if submitted:
    if nombre and motivo_input:
        # Analizar con el "Cerebro"
        resultados_ia = motor_ia_dsp(motivo_input, perso_input, seleccion)
        
        # Estructura Entrevista
        entrevista = {
            "DATOS GENERALES": {"Nombre": nombre, "Edad": edad, "Militar": militar},
            "MOTIVO Y PERSONALIDAD": {"Motivo": motivo_input, "Rasgos": perso_input},
            "SINTOMAS": {"Marcados": ", ".join(seleccion)}
        }
        
        pdf_bytes = generar_pdf(entrevista, resultados_ia)
        
        st.success("✅ Analisis completado. La IA ha vinculado tus carpetas de Drive segun el caso.")
        st.download_button(
            label="⬇️ Descargar Expediente con Enlaces de Tests",
            data=bytes(pdf_bytes),
            file_name=f"Informe_IA_{nombre}.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Por favor rellena el nombre y el motivo para que la IA pueda trabajar.")
