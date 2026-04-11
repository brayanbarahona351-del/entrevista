import streamlit as st
import pandas as pd
import os, io
from docx import Document
from datetime import datetime, date

# 1. CONFIGURACIÓN Y LISTA COMPLETA DE CAMPOS
st.set_page_config(page_title="Sistema Clínico D.S.P.", layout="wide")
DB_FILE = "expedientes_dsp_v6.xlsx"

# Lista simplificada para el Excel (Categorías principales)
CAMPOS = [
    "Nombre", "Identidad", "Fecha_Nac", "Sexo", "Edad", "Celular", "Ocupacion", 
    "Asignacion", "Servicio_Militar", "Direccion", "Nivel_Educativo", "Remitido_Por",
    "Motivo_Consulta", "Antecedentes_Situacion", "Funciones_Organicas", "Salud_General",
    "Sintomas_Checklist", "Info_Familiar", "Social_Ambiental", "Habitos_Judiciales",
    "Desarrollo_Personal", "Historia_Sexual", "Personalidad_Previa", "Observaciones",
    "Seguimiento", "Proxima_Cita"
]

# 2. FUNCIONES DE BASE DE DATOS
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

# 3. MOTOR DE IA (ANALIZA TODA LA DATA)
def motor_ia_dsp(d):
    # Analizamos el motivo, síntomas y personalidad
    texto = f"{d['Motivo_Consulta']} {d['Sintomas_Checklist']} {d['Personalidad_Previa']}".lower()
    drive = "https://drive.google.com/drive/folders/1lrH7AKPKXOVeFkcc_EdO03E0Ar5k4wbv"
    
    if any(x in texto for x in ["morir", "suicid", "voces", "extrañas"]):
        return "ALTO RIESGO / PRIORIDAD 1", "MMPI-2, SCL-90-R y Batería Proyectiva completa", "Remisión inmediata a Psiquiatría y TCC", drive
    if any(x in texto for x in ["ira", "golpe", "pelea", "drogas", "ley"]):
        return "RIESGO CONDUCTUAL / IMPULSIVIDAD", "16PF, IPV y Test de la Figura Humana", "Manejo de impulsos y desintoxicación", drive
    return "ESTABLE / SEGUIMIENTO", "16PF y Barsit", "Consejería y apoyo emocional", drive

# 4. INTERFAZ DE USUARIO
st.title("🛡️ Protocolo de Entrevista Clínica - D.S.P.")
db = cargar_db()

with st.sidebar:
    sel = st.selectbox("Expedientes:", ["NUEVO REGISTRO"] + db["Nombre"].tolist())
    p = db[db["Nombre"] == sel].iloc[0].to_dict() if sel != "NUEVO REGISTRO" else {c: "" for c in CAMPOS}

tabs = st.tabs(["I-II. Generales", "III-V. Salud y Síntomas", "VI. Familia", "VII-X. Desarrollo y Social", "XI-XII. Personalidad/IA"])

with tabs[0]:
    st.subheader("Datos Generales")
    c1, c2, c3 = st.columns(3)
    nom = c1.text_input("Nombre Completo", value=p["Nombre"])
    f_nac = c2.text_input("Lugar y Fecha Nacimiento", value=p["Fecha_Nac"])
    nac = c3.text_input("Nacionalidad", value=p.get("Nacionalidad",""))
    sex = c1.radio("Sexo", ["M", "F"], horizontal=True)
    eda = c2.text_input("Edad", value=p["Edad"])
    rel = c3.text_input("Religión", value=p.get("Religion",""))
    cel = c1.text_input("Celular", value=p["Celular"])
    ocu = c2.text_input("Ocupación", value=p["Ocupacion"])
    asi = c3.text_input("Asignación", value=p["Asignacion"])
    mil = c1.selectbox("¿Prestó Servicio Militar?", ["Sí", "No"])
    dir_a = st.text_input("Dirección Actual", value=p["Direccion"])
    rem = st.text_input("Remitido por:", value=p["Remitido_Por"])

with tabs[1]:
    st.subheader("Motivo y Antecedentes Clínicos")
    mot = st.text_area("Motivo de Consulta", value=p["Motivo_Consulta"])
    ant_s = st.text_area("Antecedentes de la situación (¿Cuándo se sintió bien por última vez?)", value=p["Antecedentes_Situacion"])
    fun = st.text_input("Funciones Orgánicas (Sueño, apetito, sed, defecación)", value=p["Funciones_Organicas"])
    sal_g = st.text_area("Salud (Alergias, medicamentos, cirugías, hospitalizaciones)", value=p["Salud_General"])
    
    st.divider()
    st.subheader("Checklist de Síntomas (Marque los presentes)")
    lista_s = ["Insomnio", "Pesadillas", "Ganas de morir", "Escucha voces", "Ver cosas extrañas", "Intentos suicidas", "Consumo de drogas", "Maltrato Físico", "Fobias", "Convulsiones", "Ataques de ira", "Obsesiones"]
    sintomas_selec = st.multiselect("Síntomas detectados:", lista_s, default=[s for s in lista_s if s in p["Sintomas_Checklist"]])

with tabs[2]:
    st.subheader("Información Familiar")
    con = st.text_input("Nombre del Cónyuge e hijos", value=p.get("Conyuge",""))
    pad = st.text_area("Datos del Padre (Nombre, edad, relación, castigos)", value=p.get("Padre",""))
    mad = st.text_area("Datos de la Madre (Nombre, edad, relación, castigos)", value=p.get("Madre",""))
    her = st.text_input("Hermanos (Cantidad, posición, favorito)", value=p.get("Hermanos",""))
    hist_f = st.text_area("Historia familiar feliz / Antecedentes alcoholismo o maltrato", value=p["Info_Familiar"])

with tabs[3]:
    st.subheader("Social, Ambiental y Desarrollo")
    soc = st.text_area("Relaciones laborales/escuela, economía, problemas legales", value=p["Social_Ambiental"])
    hab = st.text_input("Hábitos (Fuma, alcohol, drogas)", value=p["Habitos_Judiciales"])
    des = st.text_area("Desarrollo (Embarazo, parto, motor, esfínteres, educación)", value=p["Desarrollo_Personal"])
    sex_h = st.text_area("Historia Sexual (Primer noviazgo, primera relación, opiniones)", value=p["Historia_Sexual"])

with tabs[4]:
    st.subheader("Personalidad Previa y Resultados")
    per = st.text_area("Personalidad (Seguridad, decisiones, timidez, impulsividad, miedos)", value=p["Personalidad_Previa"])
    obs = st.text_area("Observaciones Generales", value=p["Observaciones"])
    st.divider()
    nota = st.text_area("Nota de evolución de hoy:")
    cita = st.date_input("Próxima Cita", value=date.today())

# 5. BOTÓN DE PROCESAMIENTO
if st.button("💾 GUARDAR EXPEDIENTE Y EJECUTAR IA"):
    if nom and mot:
        d_f = {
            "Nombre": nom, "Identidad": ide, "Fecha_Nac": f_nac, "Sexo": sex, "Edad": eda, 
            "Celular": cel, "Ocupacion": ocu, "Asignacion": asi, "Servicio_Militar": mil,
            "Direccion": dir_a, "Nivel_Educativo": p.get("Nivel_Educativo",""), "Remitido_Por": rem,
            "Motivo_Consulta": mot, "Antecedentes_Situacion": ant_s, "Funciones_Organicas": fun,
            "Salud_General": sal_g, "Sintomas_Checklist": ", ".join(sintomas_selec),
            "Info_Familiar": f"Padre: {pad} | Madre: {mad} | Hist: {hist_f}",
            "Social_Ambiental": soc, "Habitos_Judiciales": hab, "Desarrollo_Personal": des,
            "Historia_Sexual": sex_h, "Personalidad_Previa": per, "Observaciones": obs,
            "Seguimiento": p["Seguimiento"] + f"\n[{date.today()}]: {nota}",
            "Proxima_Cita": str(cita)
        }
        
        diag, tests, plan, link = motor_ia_dsp(d_f)
        guardar_db(d_f)
        
        st.error(f"**Diagnóstico IA:** {diag}")
        st.info(f"**Pruebas Sugeridas:** {tests} [Carpeta Drive]({link})")
        st.success(f"**Plan Terapéutico:** {plan}")
        
        # Generación de Word
        doc = Document()
        doc.add_heading('EXPEDIENTE CLÍNICO D.S.P.', 0)
        for k, v in d_f.items(): doc.add_paragraph(f"**{k}**: {v}")
        buf = io.BytesIO(); doc.save(buf); buf.seek(0)
        st.download_button("📥 Descargar Word", buf, f"Expediente_{nom}.docx")
    else: st.warning("Nombre y Motivo son obligatorios.")
