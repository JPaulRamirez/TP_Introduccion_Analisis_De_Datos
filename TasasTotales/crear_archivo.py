import os
import re
import pandas as pd

# ---------------------------
# CONFIGURACIÓN
# ---------------------------

CARPETA = "TasasTotales/individual"
AGLOMERADOS = [13, 10]   # Córdoba y Mendoza

ARCHIVO_SALIDA = "individual_unificado.txt"

# ---------------------------
# FUNCIONES
# ---------------------------

def listar_archivos_txt(carpeta):
    return sorted([f for f in os.listdir(carpeta) if f.endswith(".txt")])


def leer_individual(ruta):
    return pd.read_csv(ruta, sep=";", low_memory=False)


def extraer_periodo(nombre_archivo):
    match = re.match(r"Individual-(\d{4})-(\d)T", nombre_archivo)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

# ---------------------------
# UNIFICAR TODO
# ---------------------------

dfs = []

for archivo in listar_archivos_txt(CARPETA):
    ruta = os.path.join(CARPETA, archivo)
    df = leer_individual(ruta)

    anio, trimestre = extraer_periodo(archivo)
    df["anio"] = anio
    df["trimestre"] = trimestre

    # Filtrar Córdoba y Mendoza
    df = df[df["AGLOMERADO"].isin(AGLOMERADOS)]

    dfs.append(df)

# Unir todo en un solo DF
df_unificado = pd.concat(dfs, ignore_index=True)

# Guardar como TXT igual formato INDEC
df_unificado.to_csv(ARCHIVO_SALIDA, sep=";", index=False)

print(f"Archivo creado: {ARCHIVO_SALIDA}")
