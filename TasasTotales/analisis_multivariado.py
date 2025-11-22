import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Importo IPC acumulado del archivo ipc_trimestral.py
from ipc_trimestral import ipc_acumulado

# ---------------------------
# CONFIGURACIÓN
# ---------------------------

RUTA_UNIFICADO = "TasasTotales/IndividualUnificado/individual_unificado.txt"

AGLOMERADO_CORDOBA = 13
AGLOMERADO_MENDOZA = 10
AGLOMERADOS = [AGLOMERADO_CORDOBA, AGLOMERADO_MENDOZA]

VARIABLE_NOMINAL = "P21"
VARIABLE_REAL = "P21_real"

# ---------------------------
# IPC A DATAFRAME
# ---------------------------

ipc_rows = []
for key, value in ipc_acumulado.items():
    year, trim = key.split("-")
    trim = trim.replace("Trim", "")
    ipc_rows.append({"anio": int(year), "trimestre": int(trim), "IPC": value})

df_ipc = pd.DataFrame(ipc_rows)

# ---------------------------
# CARGAR DATOS DESDE ARCHIVO UNIFICADO
# ---------------------------


def cargar_datos_unificado(ruta):
    df = pd.read_csv(ruta, sep=";", low_memory=False)

    # Convertir columnas necesarias a numérico
    cols_numeric = ["CH04", "CH06", "NIVEL_ED", "PP04B_COD", "PP04D_COD", VARIABLE_NOMINAL]
    for col in cols_numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Filtrar aglomerados
    df = df[df["AGLOMERADO"].isin(AGLOMERADOS)]

    # Quitar ingresos negativos o cero
    df = df[df[VARIABLE_NOMINAL] > 0]

    return df

# ---------------------------
# RECODIFICAR NIVEL EDUCATIVO
# ---------------------------

def agregar_categoria_educativa(df):
    df = df[df["NIVEL_ED"] != 9].copy()
    
    mapa = {
        7: "Sin estudios",
        1: "Primario",
        2: "Primario",
        3: "Secundario",
        4: "Secundario",
        5: "Universitario",
        6: "Universitario",
    }
    df["edu_cat"] = df["NIVEL_ED"].map(mapa)

    return df

# ---------------------------
# FUNCIONES AUXILIARES PARA GRÁFICOS
# ---------------------------

def remove_outliers_custom(group):
    # Para grupos pequeños (2 o 3 observaciones): eliminar el valor máximo
    if len(group) <= 3:
        max_val = group["P21_real"].max()
        return group[group["P21_real"] != max_val]

    # IQR clásico
    Q1 = group["P21_real"].quantile(0.25)
    Q3 = group["P21_real"].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    return group[(group["P21_real"] >= lower) & (group["P21_real"] <= upper)]


def config_axes(ax, titulo):
    ax.set_title(titulo)
    ax.set_ylabel("Ingreso real")
    ax.grid(axis="y")

def crear_figura_2():
    return plt.subplots(1, 2, figsize=(16,6))

# ---------------------------
# PROCESAMIENTO
# ---------------------------

df_total = cargar_datos_unificado(RUTA_UNIFICADO)

# Unir IPC
df_total = df_total.merge(df_ipc, on=["anio", "trimestre"], how="left")

# Crear ingreso real
df_total[VARIABLE_REAL] = df_total[VARIABLE_NOMINAL] / df_total["IPC"]

# Agregar categoría educativa
df_total = agregar_categoria_educativa(df_total)

# ---------------------------
# ELIMINAR OUTLIERS POR Z-SCORE
# ---------------------------
df_test = df_total[
    ~(
        (df_total["AGLOMERADO"] == 13) &
        (df_total["anio"] == 2020) &
        (df_total["edu_cat"] == "Sin estudios") &
        (df_total["P21_real"] > 7000)
    )
]

print(df_test.sort_values("P21_real", ascending=False).head(10))



# ---------------------------
# GRÁFICOS MULTIVARIADOS
# ---------------------------

def grafico_sexo_doble(df):
    fig, axes = crear_figura_2()
    etiquetas = ["Varón", "Mujer"]

    df_cba = df[df["AGLOMERADO"] == 13]
    valores_cba = df_cba.groupby("CH04")[VARIABLE_REAL].median()
    axes[0].bar(etiquetas, [valores_cba.get(1,0), valores_cba.get(2,0)], color=["blue","pink"])
    config_axes(axes[0], "Ingreso real por sexo — Gran Córdoba")

    df_mza = df[df["AGLOMERADO"] == 10]
    valores_mza = df_mza.groupby("CH04")[VARIABLE_REAL].median()
    axes[1].bar(etiquetas, [valores_mza.get(1,0), valores_mza.get(2,0)], color=["blue","pink"])
    config_axes(axes[1], "Ingreso real por sexo — Gran Mendoza")

    plt.tight_layout()
    plt.show()

def grafico_educacion_doble(df):
    categorias = ["Sin estudios", "Primario", "Secundario", "Universitario"]
    colores = ["red", "orange", "gold", "green"]

    fig, axes = plt.subplots(1, 2, figsize=(18,8))

    df_cba = df[df["AGLOMERADO"] == 13]
    df_group_cba = df_cba.groupby(["anio", "edu_cat"])[VARIABLE_REAL].median().reset_index()

    for cat, color in zip(categorias, colores):
        df_cat = df_group_cba[df_group_cba["edu_cat"] == cat]
        axes[0].plot(df_cat["anio"], df_cat[VARIABLE_REAL], marker="o", color=color)

    config_axes(axes[0], "Ingreso real por nivel educativo — Gran Córdoba")
    axes[0].legend(categorias)

    df_mza = df[df["AGLOMERADO"] == 10]
    df_group_mza = df_mza.groupby(["anio", "edu_cat"])[VARIABLE_REAL].median().reset_index()

    for cat, color in zip(categorias, colores):
        df_cat = df_group_mza[df_group_mza["edu_cat"] == cat]
        axes[1].plot(df_cat["anio"], df_cat[VARIABLE_REAL], marker="o", color=color)

    config_axes(axes[1], "Ingreso real por nivel educativo — Gran Mendoza")

    plt.tight_layout()
    plt.show()

def grafico_edad_doble(df):
    df = df.copy()
    df["grupo_edad"] = pd.cut(df["CH06"], bins=[0,18,30,45,60,120],
                              labels=["<=18","19-30","31-45","46-60","60+"])

    fig, axes = crear_figura_2()

    df_cba = df[df["AGLOMERADO"] == 13]
    axes[0].bar(df_cba.groupby("grupo_edad")[VARIABLE_REAL].median().index,
                df_cba.groupby("grupo_edad")[VARIABLE_REAL].median().values)
    config_axes(axes[0], "Ingreso real por edad — Gran Córdoba")

    df_mza = df[df["AGLOMERADO"] == 10]
    axes[1].bar(df_mza.groupby("grupo_edad")[VARIABLE_REAL].median().index,
                df_mza.groupby("grupo_edad")[VARIABLE_REAL].median().values)
    config_axes(axes[1], "Ingreso real por edad — Gran Mendoza")

    plt.tight_layout()
    plt.show()

def grafico_pp04b_doble(df):
    fig, axes = crear_figura_2()

    df_cba = df[df["AGLOMERADO"] == 13]
    axes[0].bar(df_cba.groupby("PP04B_COD")[VARIABLE_REAL].median().index.astype(str),
                df_cba.groupby("PP04B_COD")[VARIABLE_REAL].median().values)
    config_axes(axes[0], "Ingreso real por categoría ocupacional — Córdoba")

    df_mza = df[df["AGLOMERADO"] == 10]
    axes[1].bar(df_mza.groupby("PP04B_COD")[VARIABLE_REAL].median().index.astype(str),
                df_mza.groupby("PP04B_COD")[VARIABLE_REAL].median().values)
    config_axes(axes[1], "Ingreso real por categoría ocupacional — Mendoza")

    plt.tight_layout()
    plt.show()

def grafico_pp04d_doble(df):
    fig, axes = crear_figura_2()

    df_cba = df[df["AGLOMERADO"] == 13]
    axes[0].bar(df_cba.groupby("PP04D_COD")[VARIABLE_REAL].median().index.astype(str),
                df_cba.groupby("PP04D_COD")[VARIABLE_REAL].median().values)
    config_axes(axes[0], "Ingreso real por tipo de empleo — Córdoba")

    df_mza = df[df["AGLOMERADO"] == 10]
    axes[1].bar(df_mza.groupby("PP04D_COD")[VARIABLE_REAL].median().index.astype(str),
                df_mza.groupby("PP04D_COD")[VARIABLE_REAL].median().values)
    config_axes(axes[1], "Ingreso real por tipo de empleo — Mendoza")

    plt.tight_layout()
    plt.show()

# ---------------------------
# EJECUCIÓN
# ---------------------------

grafico_sexo_doble(df_total)
grafico_educacion_doble(df_test)
grafico_edad_doble(df_total)
grafico_pp04b_doble(df_total)
grafico_pp04d_doble(df_total)
