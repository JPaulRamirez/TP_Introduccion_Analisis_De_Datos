import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

from ipc_trimestral import ipc_acumulado


# ================================
# CONFIGURACIÓN
# ================================
RUTA_UNIFICADO = "IndividualUnificado/individual_unificado.txt"
RUTA_GEOJSON   = "aglomerados_eph.json"

ANIO = 2023 #2023
TRIMESTRE = 1    #1  #1


# ================================
# 1) IPC → DataFrame
# ================================
def cargar_ipc_dataframe():
    ipc_rows = []
    for key, val in ipc_acumulado.items():
        anio_str, trim_str = key.split("-")
        trimestre = int(trim_str.replace("Trim", ""))
        ipc_rows.append({"anio": int(anio_str), "trimestre": trimestre, "IPC": val})
    return pd.DataFrame(ipc_rows)


# ================================
# 2) INGRESO REAL PROMEDIO POR TRIMESTRE
# ================================
def obtener_ingreso_real_promedio(ruta_unificado, aglomerado, anio_obj, trimestre_obj, df_ipc):

    df = pd.read_csv(ruta_unificado, sep=";", low_memory=False)

    # Campos necesarios
    columnas = ["AGLOMERADO", "anio", "trimestre", "P21"]
    for c in columnas:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Filtrar aglomerado + año + trimestre
    df = df[
        (df["AGLOMERADO"] == aglomerado) &
        (df["anio"] == anio_obj) &
        (df["trimestre"] == trimestre_obj)
    ].copy()

    # Ingresos válidos
    df = df[df["P21"] > 0]

    # Unir IPC
    df = df.merge(df_ipc, on=["anio", "trimestre"], how="left")

    # Ingreso real
    df["P21_real"] = df["P21"] / df["IPC"]

    # Promedio por aglomerado
    df_final = (
        df.groupby("AGLOMERADO")["P21_real"]
          .mean()
          .reset_index()
          .rename(columns={"P21_real": "P21_real_promedio"})
    )

    return df_final


# ================================
# 3) GRAFICAR MAPA DE UN TRIMESTRE
# ================================
def graficar_mapa_ingreso(geojson_path, df_ingresos, aglomerado, anio, trimestre, titulo, cmap):

    gdf = gpd.read_file(geojson_path)
    gdf["AGLOMERADO"] = pd.to_numeric(gdf["eph_codagl"], errors="coerce")

    gdf = gdf[gdf["AGLOMERADO"] == aglomerado].copy()

    gdf = gdf.merge(df_ingresos, on="AGLOMERADO", how="left")

    # Web Mercator
    gdf = gdf.to_crs(epsg=3857)

    fig, ax = plt.subplots(figsize=(7, 7))

    gdf.plot(
        ax=ax,
        column="P21_real_promedio",
        cmap=cmap,
        legend=True,
        edgecolor="black",
        linewidth=0.7,
        alpha=0.85,
        legend_kwds={
            "label": "Ingreso real promedio P21",
            "shrink": 0.7
        }
    )

    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)

    ax.set_axis_off()
    ax.set_title(
        f"Ingreso REAL — {titulo}\nAño {anio}, Trimestre {trimestre}",
        fontsize=12
    )

    plt.tight_layout()
    plt.show()


# ================================
# 4) FUNCIÓN GENERAL
# ================================
def mapa_ingreso_trimestral(ruta_unificado, ruta_geojson,aglomerado, anio_objetivo, trimestre_objetivo, nombre_aglomerado, color):

    df_ipc = cargar_ipc_dataframe()

    df_ingresos = obtener_ingreso_real_promedio(
        ruta_unificado,
        aglomerado,
        anio_objetivo,
        trimestre_objetivo,
        df_ipc
    )

    graficar_mapa_ingreso(
        geojson_path=ruta_geojson,
        df_ingresos=df_ingresos,
        aglomerado=aglomerado,
        anio=anio_objetivo,
        trimestre=trimestre_objetivo,
        titulo=nombre_aglomerado,
        cmap=color
    )


# ================================
# 5) LLAMADAS FINALES
# ================================
mapa_ingreso_trimestral(
    ruta_unificado=RUTA_UNIFICADO,
    ruta_geojson=RUTA_GEOJSON,
    aglomerado=13,
    anio_objetivo=ANIO,
    trimestre_objetivo=TRIMESTRE,
    nombre_aglomerado="Gran Córdoba",
    color="Blues"
)

mapa_ingreso_trimestral(
    ruta_unificado=RUTA_UNIFICADO,
    ruta_geojson=RUTA_GEOJSON,
    aglomerado=10,
    anio_objetivo=ANIO,
    trimestre_objetivo=TRIMESTRE,
    nombre_aglomerado="Gran Mendoza",
    color="Oranges"
)
