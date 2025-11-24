import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------
# CONFIGURACIÓN
# ---------------------------

RUTA_UNIFICADO = "TasasTotales/IndividualUnificado/individual_unificado.txt"

AGLOMERADO_CORDOBA = 13
AGLOMERADO_MENDOZA = 10
AGLOMERADOS = [AGLOMERADO_CORDOBA, AGLOMERADO_MENDOZA]

# ---------------------------
# FUNCIONES
# ---------------------------

def crear_variables_laborales(df):
    """Crea columnas binarias: actividad, empleo, desocupación"""
    df["es_activo"] = df["ESTADO"].isin([1, 2]).astype(int)
    df["es_ocupado"] = (df["ESTADO"] == 1).astype(int)
    df["es_desocupado"] = (df["ESTADO"] == 2).astype(int)
    df["peso"] = df["PONDERA"]
    return df

def media_ponderada(valores, pesos):
    return round(np.average(valores, weights=pesos) * 100, 2)

def calcular_tasas(df):
    actividad = media_ponderada(df["es_activo"], df["peso"])
    empleo = media_ponderada(df["es_ocupado"], df["peso"])

    activos = df[df["es_activo"] == 1]
    desocupacion = media_ponderada(activos["es_desocupado"], activos["peso"])

    return actividad, empleo, desocupacion

def ordenar_trimestres(nombre):
    m = re.match(r"(\d{4})-(\d)T", nombre)
    if m:
        a, t = m.groups()
        return int(a) * 10 + int(t)
    return 999999

# ---------------------------
# CARGAR UNIFICADO
# ---------------------------

df = pd.read_csv(RUTA_UNIFICADO, sep=";", low_memory=False)

# Convertir columnas clave
df["ESTADO"] = pd.to_numeric(df["ESTADO"], errors="coerce")
df["PONDERA"] = pd.to_numeric(df["PONDERA"], errors="coerce")

# Filtrar Córdoba y Mendoza
df = df[df["AGLOMERADO"].isin(AGLOMERADOS)].copy()

# Crear variables laborales
df = crear_variables_laborales(df)

# ---------------------------
# CALCULAR TASAS POR TRIMESTRE
# ---------------------------

tasas_por_trimestre = {}

for (anio, trimestre), grupo in df.groupby(["anio", "trimestre"]):

    nombre_periodo = f"{anio}-{trimestre}T"

    actividad, empleo, desocupacion = calcular_tasas(grupo)

    tasas_por_trimestre[nombre_periodo] = {
        "Actividad": actividad,
        "Empleo": empleo,
        "Desocupación": desocupacion,
    }

# ---------------------------
# CONVERTIR A DATAFRAME Y ORDENAR
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
