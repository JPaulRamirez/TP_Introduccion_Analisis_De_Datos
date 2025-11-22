import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------
# CONFIGURACIÓN
# ---------------------------

CARPETA = "TasasTotales/individual"

AGLOMERADO_CORDOBA = 13
AGLOMERADO_MENDOZA = 10
AGLOMERADOS = [AGLOMERADO_CORDOBA, AGLOMERADO_MENDOZA]

# ---------------------------
# FUNCIONES
# ---------------------------

def listar_archivos_txt(carpeta):
    """Devuelve lista ORDENADA de archivos .txt"""
    return sorted(
        f for f in os.listdir(carpeta)
        if f.endswith(".txt")
    )

def leer_archivo_individual(ruta):
    """Lee el archivo individual con dtype seguro."""
    return pd.read_csv(ruta, sep=";", low_memory=False)

def extraer_periodo(nombre_archivo):
    """Devuelve año y trimestre desde: Individual-2016-1T.txt"""
    match = re.match(r"Individual-(\d{4})-(\d)T", nombre_archivo)
    if match:
        año, trimestre = match.groups()
        return int(año), int(trimestre)
    return None, None

def crear_variables_laborales(df):
    """Crea columnas binarias: es_activo, es_ocupado, es_desocupado"""
    df["es_activo"] = df["ESTADO"].isin([1, 2]).astype(int)
    df["es_ocupado"] = (df["ESTADO"] == 1).astype(int)
    df["es_desocupado"] = (df["ESTADO"] == 2).astype(int)
    df["peso"] = df["PONDERA"]
    return df

def media_ponderada(valores, pesos):
    """Calcula media ponderada expresada en %"""
    return round(np.average(valores, weights=pesos) * 100, 2)

def calcular_tasas(df):
    """Devuelve tasas de actividad, empleo y desocupación."""
    actividad = media_ponderada(df["es_activo"], df["peso"])
    empleo = media_ponderada(df["es_ocupado"], df["peso"])
    
    activos = df[df["es_activo"] == 1]
    desocupacion = media_ponderada(activos["es_desocupado"], activos["peso"])
    
    return actividad, empleo, desocupacion

def ordenar_trimestres(nombre):
    """Convierte '2018-3T' a número ordenable (20183)."""
    match = re.match(r"(\d{4})-(\d)T", nombre)
    if match:
        a, t = match.groups()
        return int(a) * 10 + int(t)
    return 999999

# ---------------------------
# PIPELINE PRINCIPAL
# ---------------------------

tasas_por_trimestre = {}
archivos = listar_archivos_txt(CARPETA)

for archivo in archivos:

    ruta = os.path.join(CARPETA, archivo)
    df = leer_archivo_individual(ruta)

    # Filtrar aglomerados
    df = df[df["AGLOMERADO"].isin(AGLOMERADOS)].copy()

    # Crear columnas binarias
    df = crear_variables_laborales(df)

    # Extraer período
    año, trim = extraer_periodo(archivo)
    nombre_periodo = f"{año}-{trim}T"

    # Calcular tasas
    actividad, empleo, desocupacion = calcular_tasas(df)

    tasas_por_trimestre[nombre_periodo] = {
        "Actividad": actividad,
        "Empleo": empleo,
        "Desocupación": desocupacion,
    }

# ---------------------------
# CONVERTIR A DATAFRAME
# ---------------------------

df_tasas = pd.DataFrame(tasas_por_trimestre).T

df_tasas["orden"] = df_tasas.index.map(ordenar_trimestres)
df_tasas = df_tasas.sort_values("orden").drop(columns="orden")

print(df_tasas)

# ---------------------------
# GRAFICAR
# ---------------------------

plt.figure(figsize=(16, 6))
for col in df_tasas.columns:
    plt.plot(df_tasas.index, df_tasas[col], marker="o", label=col)

plt.xticks(rotation=60)

plt.ylim(0, 100)
plt.title("Evolución de tasas de Actividad, Empleo y Desocupación (2016–2025)")
plt.xlabel("Trimestre")
plt.ylabel("Tasa (%)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


