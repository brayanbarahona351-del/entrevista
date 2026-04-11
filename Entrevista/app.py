# --- FUNCIONES DE BASE DE DATOS (REPARADAS PARA PANDAS 3.x) ---
def cargar_db():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_excel(DB_FILE)
            # Forzamos a que todo el DataFrame sea tratado como texto/objeto
            # Esto evita el TypeError al intentar mezclar tipos de datos
            df = df.astype(object)
            
            # Verificar si faltan columnas y agregarlas
            for col in COLUMNAS_SISTEMA:
                if col not in df.columns:
                    df[col] = ""
            return df
        except Exception as e:
            st.error(f"Error al cargar Excel: {e}")
            return pd.DataFrame(columns=COLUMNAS_SISTEMA)
    else:
        return pd.DataFrame(columns=COLUMNAS_SISTEMA)

def guardar_en_db(datos):
    df = cargar_db()
    
    # Nos aseguramos de que el nuevo registro tenga todas las columnas
    nuevo_registro = {col: datos.get(col, "") for col in COLUMNAS_SISTEMA}
    
    if not df.empty and datos["Nombre"] in df["Nombre"].values:
        # Encontramos el índice del paciente
        idx = df.index[df["Nombre"] == datos["Nombre"]][0]
        # Actualizamos fila por fila para asegurar compatibilidad de tipos
        for key, value in nuevo_registro.items():
            df.at[idx, key] = str(value) if value is not None else ""
    else:
        # Si es nuevo, lo añadimos al final
        nuevo_df = pd.DataFrame([nuevo_registro])
        df = pd.concat([df, nuevo_df], ignore_index=True)
    
    # Guardar asegurando que no se pierdan formatos
    df.to_excel(DB_FILE, index=False)
