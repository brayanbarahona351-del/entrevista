import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# 1. CONFIGURACIÓN Y COLUMNAS
st.set_page_config(page_title="D.S.P. Honduras - Protocolo Completo", layout="wide")
DB_FILE = "expedientes_dsp_v7.xlsx"

CAMPOS = [
    "Nombre", "Identidad", "Fecha_Nac", "Sexo", "Edad", "Celular", "Ocupacion", 
    "Asignacion", "Servicio_Militar", "Direccion", "Nivel_Educativo", "Remitido_Por",
    "Motivo_Consulta", "Antecedentes_Situacion", "Funciones_Organicas", "Salud_General",
    "Sintomas_Checklist", "Info_Familiar", "Social_Ambiental", "Habitos_Judiciales",
    "Desarrollo_Personal", "Historia_Sexual", "Personalidad_Previa", "Observaciones",
    "Seguimiento", "Proxima_Cita"
]

# 2. FUNCIONES DE DATOS
def cargar_db():
    if not os.path.exists(DB_FILE): return pd.DataFrame(columns=CAMPOS)
    try:
        df = pd.read_excel(DB_FILE)
        return df.astype(str).replace('nan', '')
    except: return pd.DataFrame(columns=CAMPOS)

def guardar_db(datos):
    df = cargar_db()
    if not df.empty and datos["Nombre"] in df["Nombre"].values:
        df = df[df["Nombre"] != datos["Nombre"]]
    pd.concat([df, pd.DataFrame([datos])], ignore_index=True).to_excel(DB_FILE, index=False)

# 3. MOTOR DE IA
def motor_ia_dsp(d):
    texto = f"{d['Motivo_Consulta']} {d['Sintomas_Checklist']} {d['Personalidad_Previa']}".lower()
    drive = "https://drive.google.com/drive/folders/1lrH7AKPKXOVeFkcc_EdO03E0Ar5k4wbv"
    if any(x in texto for x in ["morir", "suicid", "voces", "extrañas"]):
        return "ALTO RIESGO", "MMPI-2, SCL-90-R", "Remisión a Psiquiatría", drive
    if any(x in texto for x in ["ira", "golpe", "pelea", "drogas"]):
        return "RIESGO CONDUCTUAL", "16PF, IPV", "Manejo de impulsos", drive
    return "ESTABLE", "16PF y Barsit", "Apoyo emocional", drive

# 4. INTERFAZ
st.title("🛡️ Protocolo de Entrevista Clínica - D.S.P.")
db = cargar_db()

with st.sidebar:
    sel = st.selectbox("Expedientes:", ["NUEVO REGISTRO"] + db["Nombre"].tolist())
    p = db[db["Nombre"] == sel].iloc[0].to_dict() if sel != "NUEVO REGISTRO" else {c: "" for c in CAMPOS}

tabs = st.tabs(["I-II. Generales", "III-V. Salud y Síntomas", "VI. Familia", "VII-X. Desarrollo", "XI-XII. IA/Word"])

with tabs[0]:
    st.subheader("Datos Generales")
    c1, c2, c3 = st.columns(3)
    nom = c1.text_input("Nombre Completo", value=p["Nombre"])
    ide = c2.text_input("Identidad", value=p["Identidad"]) # <--- AQUÍ ESTÁ LA CORRECCIÓN
    eda = c3.text_input("Edad", value=p["Edad"])
    f_nac = c1.text_input("Lugar y Fecha Nacimiento", value=p["Fecha_Nac"])
    sex = c2.radio("Sexo", ["M", "F"], index=0 if p["Sexo"] != "F" else 1, horizontal=True)
    cel = c3.text_input("Celular", value=p["Celular"])
    ocu = c1.text_input("Ocupación", value=p["Ocupacion"])
    asi = c2.text_input("Asignación", value=p["Asignacion"])
    mil = c3.selectbox("¿Servicio Militar?", ["No", "Sí"], index=1 if p["Servicio_Militar"] == "Sí" else 0)
    dir_a = st.text_input("Dirección Actual", value=p["Direccion"])
    rem = st.text_input("Remitido por", value=p["Remitido_By"] if "Remitido_By" in p else "")

with tabs[1]:
    st.subheader("Motivo y Salud")
    mot = st.text_area("Motivo de Consulta", value=p["Motivo_Consulta"])
    ant_s = st.text_area("Antecedentes Situación", value=p["Antecedentes_Situacion"])
    fun = st.text_input("Sueño, apetito, sed, defecación", value=p["Funciones_Organicas"])
    sal_g = st.text_area("Alergias, medicamentos, cirugías", value=p["Salud_General"])
    lista_s = ["Insomnio", "Pesadillas", "Ganas de morir", "Escucha voces", "Consumo drogas", "Ira"]
    sintomas_selec = st.multiselect("Checklist:", lista_s, default=[s for s in lista_s if s in p["Sintomas_Checklist"]])

with tabs[2]:
    st.subheader("Información Familiar")
    f_inf = st.text_area("Relación padres, castigos, hermanos, antecedentes alcoholismo", value=p["Info_Familiar"])

with tabs[3]:
    st.subheader("Desarrollo y Social")
    soc = st.text_area("Relación trabajo, economía, judicial", value=p["Social_Ambiental"])
    des = st.text_area("Embarazo, parto, motor, esfínteres", value=p["Desarrollo_Personal"])
    sex_h = st.text_area("Historia Sexual (Noviazgo, primera relación, opiniones)", value=p["Historia_Sexual"])

with tabs[4]:
    st.subheader("Personalidad y Cierre")
    per = st.text_area("Rasgos (Seguridad, timidez, impulsividad)", value=p["Personalidad_Previa"])
    obs = st.text_area("Observaciones Generales", value=p["Observaciones"])
    st.divider()
    nota = st.text_area("Nota de hoy:")
    cita = st.date_input("Próxima Cita")

# 5. GUARDADO
if st.button("💾 GUARDAR Y ANALIZAR"):
    if nom and mot:
        d_f = {
            "Nombre": nom, "Identidad": ide, "Fecha_Nac": f_nac, "Sexo": sex, "Edad": eda, 
            "Celular": cel, "Ocupacion": ocu, "Asignacion": asi, "Servicio_Militar": mil,
            "Direccion": dir_a, "Remitido_Por": rem, "Motivo_Consulta": mot, 
            "Antecedentes_Situacion": ant_s, "Funciones_Organicas": fun,
            "Salud_General": sal_g, "Sintomas_Checklist": ", ".join(sintomas_selec),
            "Info_Familiar": f_inf, "Social_Ambiental": soc, "Desarrollo_Personal": des,
            "Historia_Sexual": sex_h, "Personalidad_Previa": per, "Observaciones": obs,
            "Seguimiento": p["Seguimiento"] + f"\n[{date.today()}]: {nota}", "Proxima_Cita": str(cita)
        }
        
        diag, tests, plan, link = motor_ia_dsp(d_f)
        guardar_db(d_f)
        
        st.error(f"**Diagnóstico:** {diag}"); st.info(f"**Pruebas:** {tests}"); st.success(f"**Plan:** {plan}")
        
        doc = Document()
        doc.add_heading(f'EXPEDIENTE D.S.P. - {nom}', 0)
        for k, v in d_f.items(): doc.add_paragraph(f"**{k}**: {v}")
        buf = io.BytesIO(); doc.save(buf); buf.seek(0)
