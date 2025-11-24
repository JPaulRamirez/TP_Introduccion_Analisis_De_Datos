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

RUTA_UNIFICADO = "IndividualUnificado/individual_unificado.txt"

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
    
    
mapa_pp04d = {
    1: "Directores / Gerentes",
    2: "Profesionales científicos y técnicos",
    3: "Técnicos y profesionales de apoyo",
    4: "Empleados administrativos",
    5: "Serv. personales / vendedores",
    6: "Agricultores / Operadores agro",
    7: "Oficios artesanales / Construcción",
    8: "Operadores de máquinas / Ensambladores",
    9: "Ocupaciones no calificadas"
}

def recodificar_pp04d(df):
    df = df.copy()
    # Tomamos SOLO el primer dígito del código ocupacional (familia CNO)
    df["PP04D_cat"] = df["PP04D_COD"].astype(str).str[0].astype(float)
    df["PP04D_label"] = df["PP04D_cat"].map(mapa_pp04d)
    return df
# ---------------------------
# FUNCIONES AUXILIARES PARA GRÁFICOS
# ---------------------------




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

# Normalizar la columna (a int)
df_total["PP04B_COD"] = pd.to_numeric(df_total["PP04B_COD"], errors="coerce")

# Crear la nueva columna categórica

# ---------------------------
# ELIMINAR OUTLIERS POR Z-SCORE
# ---------------------------
df_total = df_total[
    ~(
        (df_total["AGLOMERADO"] == 13) &
        (df_total["anio"] == 2020) &
        (df_total["edu_cat"] == "Sin estudios") &
        (df_total["P21_real"] > 7000)
    )
]

# Recodificar PP04D en familias CNO
df_total = recodificar_pp04d(df_total)
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
    axes[1].legend(categorias)

    plt.tight_layout()
    plt.show()

def grafico_edad_doble(df):
    df = df.copy()
    df["grupo_edad"] = pd.cut(
        df["CH06"],
        bins=[0,18,30,45,60,120],
        labels=["<=18","19-30","31-45","46-60","60+"]
    )
    fig, axes = crear_figura_2()
    # --- Córdoba ---
    df_cba = df[df["AGLOMERADO"] == 13]
    med_cba = df_cba.groupby("grupo_edad", observed=False)[VARIABLE_REAL].median()
    axes[0].bar(med_cba.index, med_cba.values)
    config_axes(axes[0], "Ingreso real por edad — Gran Córdoba")
    # --- Mendoza ---
    df_mza = df[df["AGLOMERADO"] == 10]
    med_mza = df_mza.groupby("grupo_edad", observed=False)[VARIABLE_REAL].median()

    axes[1].bar(med_mza.index, med_mza.values)
    config_axes(axes[1], "Ingreso real por edad — Gran Mendoza")

    plt.tight_layout()
    plt.show()


def grafico_pp04b_doble(df):
    fig, axes = crear_figura_2()

    # Córdoba
    df_cba = df[df["AGLOMERADO"] == 13]
    med_cba = df_cba.groupby("PP04B_COD_cat")["P21_real"].median()
    axes[0].bar(med_cba.index, med_cba.values, color="orange")
    config_axes(axes[0], "Ingreso real por categoría ocupacional — Córdoba")

    # Mendoza
    df_mza = df[df["AGLOMERADO"] == 10]
    med_mza = df_mza.groupby("PP04B_COD_cat")["P21_real"].median()
    axes[1].bar(med_mza.index, med_mza.values, color="orange")
    config_axes(axes[1], "Ingreso real por categoría ocupacional — Mendoza")

    plt.tight_layout()
    plt.show()



def grafico_pp04d_doble(df):
    fig, axes = plt.subplots(1, 2, figsize=(20, 8))

    # --- CÓRDOBA ---
    df_cba = df[df["AGLOMERADO"] == AGLOMERADO_CORDOBA]
    med_cba = df_cba.groupby("PP04D_label")[VARIABLE_REAL].median().dropna()
    
    axes[0].bar(med_cba.index, med_cba.values, color="purple")
    axes[0].set_title("Ingreso real por tipo de ocupación — CÓRDOBA")
    axes[0].set_ylabel("Ingreso real")
    
    # CORRECCIÓN AQUÍ: Agregamos ha='right' para anclar el texto
    axes[0].set_xticklabels(med_cba.index, rotation=45, ha='right', fontsize=9)

    # --- MENDOZA ---
    df_mza = df[df["AGLOMERADO"] == AGLOMERADO_MENDOZA]
    med_mza = df_mza.groupby("PP04D_label")[VARIABLE_REAL].median().dropna()
    
    axes[1].bar(med_mza.index, med_mza.values, color="purple")
    axes[1].set_title("Ingreso real por tipo de ocupación — MENDOZA")
    axes[1].set_ylabel("Ingreso real")
    
    # CORRECCIÓN AQUÍ TAMBIÉN
    axes[1].set_xticklabels(med_mza.index, rotation=45, ha='right', fontsize=9)

    # Ajustes de márgenes
    plt.tight_layout(rect=[0, 0, 1, 1]) 
    # Le damos un poco más de aire abajo si hace falta, pero tight_layout suele arreglarlo
    plt.subplots_adjust(bottom=0.25) 

    plt.show()
# ---------------------------
# EJECUCIÓN
# ---------------------------

grafico_sexo_doble(df_total)
grafico_educacion_doble(df_total)
grafico_edad_doble(df_total)
#grafico_pp04b_doble(df_total) # Dudoso
grafico_pp04d_doble(df_total)
