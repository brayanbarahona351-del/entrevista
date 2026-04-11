import streamlit as st
from fpdf import FPDF

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="IA Clínica D.S.P. - Descarga de Tests", layout="wide")

class DSP_PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 5, 'REPUBLICA DE HONDURAS | SECRETARIA DE SEGURIDAD', 0, 1, 'C')
        self.cell(0, 5, 'DIRECCION DE SANIDAD POLICIAL (D.S.P.)', 0, 1, 'C')
        self.ln(5)

def generar_pdf_ia(entrevista, informe_ia):
    pdf = DSP_PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    def c(t): return str(t).encode('latin-1', 'replace').decode('latin-1')
    
    pdf.add_page()
    pdf.set_font("helvetica", 'B', 14)
    pdf.cell(0, 10, c("INFORME CLÍNICO Y RECOMENDACIÓN DE TESTS"), 0, 1, 'C')
    
    for sec, campos in entrevista.items():
        pdf.set_font("helvetica", 'B', 10)
        pdf.set_fill_color(235, 235, 235)
        pdf.cell(0, 8, c(sec), 1, 1, 'L', True)
        pdf.set_font("helvetica", '', 9)
        for k, v in campos.items():
            pdf.multi_cell(185, 5, c(f"{k}: {v}"))
        pdf.ln(2)

    return pdf.output()

# --- BASE DE DATOS DE IDs DE DESCARGA (Debes obtener estos IDs de tu Drive) ---
# Para obtener el ID: Clic derecho en el archivo en Drive -> Compartir -> Copiar enlace. 
# El ID es el código largo entre /d/ y /view.
TESTS_DATABASE = {
    "16PF-5": "https://drive.google.com/uc?export=download&id=ID_DE_TU_ARCHIVO_16PF",
    "MMPI-2": "https://drive.google.com/uc?export=download&id=ID_DE_TU_ARCHIVO_MMPI2",
    "BARSIT": "https://drive.google.com/uc?export=download&id=ID_DE_TU_ARCHIVO_BARSIT",
    "HTP": "https://drive.google.com/uc?export=download&id=ID_DE_TU_ARCHIVO_HTP",
    "Persona Bajo la Lluvia": "https://drive.google.com/uc?export=download&id=ID_DE_TU_ARCHIVO_PBLL"
}

def motor_ia_recomendador(motivo, sintomas):
    texto = motivo.lower()
    recomendaciones = []
    
    if any(x in texto for x in ["morir", "suicid", "triste"]):
        recomendaciones.append("MMPI-2")
    if any(x in texto for x in ["ira", "agresivo", "impulso"]):
        recomendaciones.append("16PF-5")
    if "Escucha voces" in sintomas or "Ver cosas extrañas" in sintomas:
        recomendaciones.append("HTP")
        recomendaciones.append("Persona Bajo la Lluvia")
    
    if not recomendaciones:
        recomendaciones.append("BARSIT")
        
    return recomendaciones

# --- INTERFAZ ---
st.title("🛡️ Asistente D.S.P. con Descarga de Protocolos")

with st.sidebar:
    st.header("Configuración de Archivos")
    st.info("Para que la descarga funcione, asegúrate de que los archivos en tu Drive estén configurados como 'Cualquier persona con el enlace puede leer'.")

nombre = st.text_input("Nombre del Evaluado")
motivo = st.text_area("Motivo de consulta (Análisis de IA)")
sintomas = st.multiselect("Síntomas:", ["Ganas de morir", "Escucha voces", "Ansiedad", "Agresividad"])

if st.button("ANALIZAR Y GENERAR RECOMENDACIONES"):
    if nombre and motivo:
        tests_sugeridos = motor_ia_recomendador(motivo, sintomas)
        
        st.subheader("🤖 Análisis de la IA:")
        st.write(f"Basado en el motivo de consulta, se recomienda aplicar los siguientes protocolos disponibles en tu Drive:")
        
        # Generar botones de descarga dinámicos
        cols = st.columns(len(tests_sugeridos))
        for i, test in enumerate(tests_sugeridos):
            with cols[i]:
                st.markdown(f"**{test}**")
                # Botón que redirige a la descarga directa
                st.link_button(f"Descargar {test}", TESTS_DATABASE.get(test, "#"))

        # Generar el PDF del informe
        datos_e = {"DATOS": {"Nombre": nombre}, "ANALISIS": {"Motivo": motivo}}
        informe_ia = {"RECOMENDACION": ", ".join(tests_sugeridos)}
        pdf_out = generar_pdf_ia(datos_e, informe_ia)
        
        st.divider()
        st.download_button("⬇️ Descargar Informe de Entrevista (PDF)", data=bytes(pdf_out), file_name=f"Informe_{nombre}.pdf")
    else:
        st.error("Por favor rellene los campos obligatorios.")
