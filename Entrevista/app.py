import streamlit as st
import pandas as pd
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io
import os

# --- FUNCIÓN PARA GENERAR EL WORD ---
def generar_word(datos_entrevista, informe_ia):
    doc = Document()
    
    # Encabezado Oficial
    header = doc.sections[0].header
    p = header.paragraphs[0]
    p.text = "REPÚBLICA DE HONDURAS | SECRETARÍA DE SEGURIDAD\nDIRECCIÓN DE SANIDAD POLICIAL (D.S.P.)"
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_heading('EXPEDIENTE PSICOLÓGICO CLÍNICO', 0)

    # Llenado de secciones
    for seccion, campos in datos_entrevista.items():
        doc.add_heading(seccion, level=1)
        table = doc.add_table(rows=0, cols=2)
        table.style = 'Table Grid'
        for clave, valor in campos.items():
            row_cells = table.add_row().cells
            row_cells[0].text = str(clave)
            row_cells[1].text = str(valor)
            # Formato de fuente
            for cell in row_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(10)

    # Sección de IA
    doc.add_page_break()
    doc.add_heading('INFORME DE ANÁLISIS E INTERPRETACIÓN (IA)', level=1)
    for k, v in informe_ia.items():
        doc.add_heading(k, level=2)
        doc.add_paragraph(v)

    # Espacio para firmas
    doc.add_paragraph("\n\n\n__________________________\nFirma y Sello del Psicólogo")

    # Guardar en memoria para descarga
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- INTERFAZ DE STREAMLIT (Lógica de Base de Datos Excel) ---
st.title("🛡️ Sistema D.S.P. - Formato Word (.docx)")

# (Aquí va el resto de tu código de pestañas y base de datos Excel...)

# --- BOTÓN DE FINALIZACIÓN ---
if st.button("📝 FINALIZAR Y GENERAR EXPEDIENTE EN WORD"):
    if nombre and motivo:
        # 1. Simular análisis de IA
        res_ia = {
            "Diagnóstico Sugerido": "Análisis preliminar de rasgos detectados.",
            "Batería Recomendada": "Aplicar pruebas según manuales en Drive."
        }
        
        # 2. Organizar datos
        datos_completos = {
            "DATOS GENERALES": {"Nombre": nombre, "Edad": edad, "Identidad": identidad},
            "MOTIVO Y SALUD": {"Motivo": motivo, "Síntomas": ", ".join(sintomas)},
            "HISTORIA": {"Familia": familia, "Desarrollo": desarrollo},
            "PERSONALIDAD": {"Rasgos": personalidad}
        }
        
        # 3. Generar Word
        word_file = generar_word(datos_completos, res_ia)
        
        st.success("✅ Documento de Word generado correctamente.")
        
        st.download_button(
            label="⬇️ Descargar Expediente en Word",
            data=word_file,
            file_name=f"Expediente_{nombre.replace(' ', '_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
