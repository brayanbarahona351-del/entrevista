# --- FUNCIONES DE BASE DE DATOS (CORREGIDA) ---
def cargar_db():
    # Definimos todas las columnas que el sistema NECESITA
    columnas_requeridas = [
        "Nombre", "Identidad", "Edad", "Lugar_Nac", "Religion", "Ocupacion", 
        "Militar", "Motivo", "Sintomas", "Funciones_Org", "Antecedentes_Fam", 
        "Desarrollo_Inf", "Historia_Escolar", "Historia_Sexual", 
        "Personalidad_Previa", "Seguimiento", "Proxima_Cita"
    ]
    
    if os.path.exists(DB_FILE):
        df = pd.read_excel(DB_FILE)
        # VERIFICACIÓN DE COLUMNAS FALTANTES:
        # Si el Excel es viejo y no tiene "Proxima_Cita", la creamos vacía
        for col in columnas_requeridas:
            if col not in df.columns:
                df[col] = "" 
        return df
    else:
        # Si el archivo no existe, lo creamos de cero con la estructura completa
        return pd.DataFrame(columns=columnas_requeridas)
