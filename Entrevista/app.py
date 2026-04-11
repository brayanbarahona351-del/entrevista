import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# --- 1. CONFIGURACIÓN DE SEGURIDAD Y ARCHIVO ---
st.set_page_config(page_title="D.S.P. Honduras - Gestión de Datos", layout="wide")
DB_FILE = "DB_DSP_SISTEMA.xlsx"

def cargar_db():
    if not os.path.exists(DB_FILE):
        return pd.DataFrame()
    try:
        df = pd.read_excel(DB_FILE)
        return df.astype(str).replace('nan', '')
    except:
        return pd.DataFrame()

def guardar_db(datos_dict):
    df = cargar_db()
    if not df.empty and "Identidad" in df.columns:
        # Elimina la versión vieja si existe para actualizar con la nueva
        df = df[df["Identidad"] != datos_dict["Identidad"]]
    df_final = pd.concat([df, pd.DataFrame([datos_dict])], ignore_index=True)
    df_final.to_excel(DB_FILE, index=False)
    return df_final

# --- 2. BIBLIOTECA DE TESTS Y ENLACES ---
TEST_LINKS = {
    "MMPI-2 (Personalidad profunda)": "https://www.teaediciones.com/mmpi-2-inventario-multifasico-de-personalidad-de-minnesota-2.html",
    "Beck BDI-II (Depresión)": "https://www.paho.org/es/documentos/inventario-depresion-beck-bdi-ii",
    "STAI (Ansiedad Estado/Rasgo)": "https://web.teaediciones.com/stai-cuestionario-de-ansiedad-estado-rasgo.aspx",
    "16PF-5 (Factores de personalidad)": "https://www.psicologia-online.com/test-de-personalidad-16pf-5-que-es-y-como-se-interpreta-4652.html",
    "IPV (Inventario de Personalidad)": "https://web.teaediciones.com/ipv-inventario-de-personalidad-para-vendedores.aspx"
}

# --- 3. ÁREA DE BÚSQUEDA (SIEMPRE ARRIBA) ---
db_actual = cargar_db()
st.sidebar.header("🔍 BUSCADOR DE EXPEDIENTES")

datos_cargados = {}
if not db_actual.empty:
    lista_ids = ["--- SELECCIONAR NUEVO ---"] + db_actual["Identidad"].tolist()
    seleccion_id = st.sidebar.selectbox("Buscar por Número de Identidad:", lista_ids)
    
    if seleccion_id != "--- SELECCIONAR NUEVO ---":
        datos_cargados = db_actual[db_actual["Identidad"] == seleccion_id].iloc[0].to_dict()
        st.sidebar.success(f"Cargado: {datos_cargados.get('Nombre')}")
else:
    st.sidebar.info("La base de datos está vacía.")

st.title("🛡️ Sistema de Protocolo e Informe Clínico - D.S.P.")

# --- 4. ESTRUCTURA DE PESTAÑAS ---
t1, t2, t3, t4, t5 = st.tabs([
    "📝 Entrevista (Preguntas)", 
    "🧠 Análisis e Informe", 
    "🧪 Tests y Recomendaciones", 
    "📊 BASE DE DATOS COMPLETA", # Aquí verás todos tus datos
    "📥 Generar Archivos"
])

# PESTAÑA 1: TODA LA ENTREVISTA
with t1:
    st.subheader("PROTOCOLO DE ENTREVISTA DETALLADO")
    c1, c2 = st.columns(2)
    id_paciente = c1.text_input("Identidad (Código Único)", value=datos_cargados.get("Identidad", ""))
    nom_paciente = c2.text_input("Nombre Completo del Paciente", value=datos_cargados.get("Nombre", ""))
    
    col_a, col_b, col_c = st.columns(3)
    eda = col_a.text_input("Edad", value=datos_cargados.get("Edad", ""))
    sex = col_b.selectbox("Sexo", ["M", "F"], index=0 if datos_cargados.get("Sexo") == "M" else 1)
    f_nac = col_c.text_input("Fecha/Lugar Nacimiento", value=datos_cargados.get("F_Nac", ""))
    
    motivo = st.text_area("Motivo de consulta (Respuesta del paciente)", value=datos_cargados.get("Motivo", ""))
    
    st.write("**Área de Salud y Familia**")
    sue = st.text_input("¿Cómo duerme?", value=datos_cargados.get("Sueño", ""))
    padre_rel = st.text_area("Relación con el padre y castigos", value=datos_cargados.get("Rel_Padre", ""))
    madre_rel = st.text_area("Relación con la madre y castigos", value=datos_cargados.get("Rel_Madre", ""))
    
    st.write("**Desarrollo**")
    parto = st.text_input("Tipo de parto / Embarazo", value=datos_cargados.get("Parto", ""))
    escuela = st.text_area("Historia escolar y conducta", value=datos_cargados.get("Escuela", ""))

# PESTAÑA 2: ANÁLISIS E INFORME
with t2:
    st.subheader("ANÁLISIS CLÍNICO Y CONCLUSIONES")
    hallazgos = st.text_area("Análisis de Hallazgos (IA y Profesional)", value=datos_cargados.get("Analisis", ""))
    concl = st.text_area("Conclusiones Finales", value=datos_cargados.get("Conclusiones", ""))
    terapia = st.text_area("Plan de Terapia Sugerido", value=datos_cargados.get("Terapia", ""))

# PESTAÑA 3: TESTS CON ENLACES
with t3:
    st.subheader("RECOMENDACIÓN DE PRUEBAS PSICOMÉTRICAS")
    # Cargar selección previa si existe
    try:
        prev_tests = eval(datos_cargados.get("Tests_Rec", "[]"))
    except:
        prev_tests = []
        
    seleccion_tests = st.multiselect("Seleccione los tests para este paciente:", list(TEST_LINKS.keys()), default=prev_tests)
    
    st.info("Enlaces a los recursos:")
    for t in seleccion_tests:
        st.write(f"🔗 **{t}**: [Abrir enlace]({TEST_LINKS[t]})")

# PESTAÑA 4: LA BASE DE DATOS (PARA VER TODOS LOS DATOS)
with t4:
    st.subheader("📊 Base de Datos General (Privada)")
    db_vista = cargar_db()
    if not db_vista.empty:
        st.dataframe(db_vista) # AQUÍ PUEDES VER TODOS LOS DATOS YA EXISTENTES
        
        # Botón para descargar todo el Excel
        buf_ex = io.BytesIO()
        db_vista.to_excel(buf_ex, index=False)
        st.download_button("📥 Descargar Base de Datos Completa (Excel)", buf_ex, "Base_Datos_DSP.xlsx")
    else:
        st.warning("No hay datos guardados aún.")

# PESTAÑA 5: GENERAR ARCHIVOS
with t5:
    st.subheader("FINALIZAR EXPEDIENTE")
    psicologo_firma = st.text_input("Nombre del Psicólogo Evaluador", value=datos_cargados.get("Psicologo", ""))
    
    if st.button("💾 GUARDAR TODO Y GENERAR WORD"):
        if id_paciente and nom_paciente:
            # Diccionario de guardado
            datos_finales = {
                "Identidad": id_paciente, "Nombre": nom_paciente, "Edad": eda, "Sexo": sex,
                "F_Nac": f_nac, "Motivo": motivo, "Sueño": sue, "Rel_Padre": padre_rel,
                "Rel_Madre": madre_rel, "Parto": parto, "Escuela": escuela,
                "Analisis": hallazgos, "Conclusiones": concl, "Terapia": terapia,
                "Tests_Rec": str(seleccion_tests), "Psicologo": psicologo_firma,
                "Fecha_Registro": str(date.today())
            }
            
            guardar_db(datos_finales)
            st.success(f"✅ Los datos de {nom_paciente} se han guardado/actualizado.")
            
            # --- GENERAR EL WORD DETALLADO ---
            doc = Document()
            doc.add_heading('EXPEDIENTE PSICOLÓGICO INTEGRAL - D.S.P.', 0)
            
            # PARTE 1: ENTREVISTA
            doc.add_heading('I. PROTOCOLO DE ENTREVISTA (VACIADO)', level=1)
            items = [
                ("Identidad", id_paciente), ("Nombre", nom_paciente), ("Motivo", motivo),
                ("Relación Padre", padre_rel), ("Relación Madre", madre_rel), 
                ("Historia Escolar", escuela)
            ]
