import os
import re
import pandas as pd
import matplotlib.pyplot as plt

from ipc_trimestral import *

# ---------------------------
# CONFIGURACIÓN
# ---------------------------
RUTA_UNIFICADO = "IndividualUnificado/individual_unificado.txt"
AGLOMERADO_CORDOBA = 13
AGLOMERADO_MENDOZA = 10
AGLOMERADOS = [AGLOMERADO_CORDOBA, AGLOMERADO_MENDOZA]

VARIABLE_NOMINAL = "P21"
VARIABLE_REAL = "P21_real"

# ---------------------------
# TRANSFORMAR IPC A DATAFRAME
# ---------------------------

ipc_rows = []
for key, value in ipc_acumulado.items():
    year, trim = key.split("-")
    trim = trim.replace("Trim", "")
    ipc_rows.append({"anio": int(year), "trimestre": int(trim), "IPC": value})

df_ipc = pd.DataFrame(ipc_rows)

# ---------------------------
# CARGAR ARCHIVO UNIFICADO
# ---------------------------

df_total = pd.read_csv(RUTA_UNIFICADO, sep=";")

# Convertir P21 a numérico si no viene así
df_total[VARIABLE_NOMINAL] = pd.to_numeric(df_total[VARIABLE_NOMINAL], errors="coerce")

# Eliminar ingresos negativos o nulos
df_total = df_total[df_total[VARIABLE_NOMINAL] > 0]

# ---------------------------
# UNIR CON IPC
# ---------------------------

df_total = df_total.merge(df_ipc, on=["anio", "trimestre"], how="left")

# Crear ingreso real
df_total[VARIABLE_REAL] = df_total[VARIABLE_NOMINAL] / df_total["IPC"]

# ---------------------------
# ESTADÍSTICOS
# ---------------------------

def calcular_estadisticos(df, columna):
    return df.groupby(["anio", "AGLOMERADO"])[columna].agg(
        media="mean",
        mediana="median",
        p25=lambda x: x.quantile(0.25),
        p75=lambda x: x.quantile(0.75),
        p10=lambda x: x.quantile(0.10),
        p90=lambda x: x.quantile(0.90),
        std="std",
        count="count"
    ).reset_index()



df_nominal = calcular_estadisticos(df_total, VARIABLE_NOMINAL)
df_real = calcular_estadisticos(df_total, VARIABLE_REAL)

print("\n--- ESTADÍSTICOS NOMINALES ---")
#print(df_nominal)

print("\n--- ESTADÍSTICOS REALES ---")
#print(df_real)

# ---------------------------
# GRAFICOS
# ---------------------------

def graficar_comparacion_dos_aglomerados(df_real, aglo1, aglo2, nombre1, nombre2):
    plt.figure(figsize=(16,7))

    # Filtrar
    df1 = df_real[df_real["AGLOMERADO"] == aglo1]
    df2 = df_real[df_real["AGLOMERADO"] == aglo2]

    # --- MEDIA ---
    plt.plot(df1["anio"], df1["media"], marker="o",
             label=f"{nombre1} — media real", linestyle="-")
    plt.plot(df2["anio"], df2["media"], marker="o",
             label=f"{nombre2} — media real", linestyle="-")

    # --- MEDIANA ---
    plt.plot(df1["anio"], df1["mediana"], marker="x",
             label=f"{nombre1} — mediana real", linestyle="--")
    plt.plot(df2["anio"], df2["mediana"], marker="x",
             label=f"{nombre2} — mediana real", linestyle="--")

    # Eje X
    años = sorted(df_real["anio"].unique())
    plt.xticks(años)

    # Títulos
    plt.title("Ingreso REAL (P21 ajustado por IPC) — Media y Mediana\nComparación Gran Córdoba vs Gran Mendoza (2016–2025)")
    plt.xlabel("Año")
    plt.ylabel("Ingreso real (P21 ajustado)")
    
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


# --------- EJECUTAR LA FUNCIÓN ---------
graficar_comparacion_dos_aglomerados(
    df_real,
    AGLOMERADO_CORDOBA,
    AGLOMERADO_MENDOZA,
    "Gran Córdoba",
    "Gran Mendoza"
)




"""def graficar_nominal_vs_real(df_nom, df_real, aglomerado, nombre_aglo):
    plt.figure(figsize=(15,6))

    df_nom_aglo = df_nom[df_nom["AGLOMERADO"] == aglomerado]
    df_real_aglo = df_real[df_real["AGLOMERADO"] == aglomerado]

    plt.plot(df_nom_aglo["anio"], df_nom_aglo["mediana"], marker="o", label="Nominal")
    plt.plot(df_real_aglo["anio"], df_real_aglo["mediana"], marker="o", label="Ajustado por IPC")

    años = df_nom_aglo["anio"].unique()
    plt.xticks(años)

    plt.title(f"Evolución ingreso P21 — {nombre_aglo} (Nominal vs Real 2016–2025)")
    plt.xlabel("Año")
    plt.ylabel("Mediana del ingreso P21")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

# --------- GRAFICAR CÓRDOBA Y MENDOZA ---------

graficar_nominal_vs_real(df_nominal, df_real, 13, "Gran Córdoba")
graficar_nominal_vs_real(df_nominal, df_real, 10, "Gran Mendoza")"""
