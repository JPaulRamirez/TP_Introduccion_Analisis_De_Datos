import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

from ipc_trimestral import ipc_acumulado


RUTA_UNIFICADO = "IndividualUnificado/individual_unificado.txt"
RUTA_GEOJSON   = "aglomerados_eph.json"
ANIO = 2025    # CAMBIAR A 2016, 2018, 2020, 2024, ETC.
# ======================================================
# 1) TRANSFORMAR IPC A DATAFRAME
# ======================================================
def cargar_ipc_dataframe():
    ipc_rows = []
    for key, val in ipc_acumulado.items():     # key = "2023-1Trim"
        anio_str, trim_str = key.split("-")
        trimestre = int(trim_str.replace("Trim", ""))
        ipc_rows.append({
            "anio": int(anio_str),
            "trimestre": trimestre,
            "IPC": val
        })
    return pd.DataFrame(ipc_rows)


# ======================================================
# 2) CALCULAR INGRESO REAL PROMEDIO POR AGLOMERADO
# ======================================================
def obtener_ingreso_real_promedio(ruta_unificado, aglomerado, anio_objetivo, df_ipc):

    df = pd.read_csv(ruta_unificado, sep=";", low_memory=False)

    columnas = ["AGLOMERADO", "anio", "trimestre", "P21"]
    for c in columnas:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df[
        (df["AGLOMERADO"] == aglomerado) &
        (df["anio"] == anio_objetivo)
    ].copy()

    df = df[df["P21"] > 0]

    df = df.merge(df_ipc, on=["anio", "trimestre"], how="left")

    df["P21_real"] = df["P21"] / df["IPC"]

    df_ingreso = (
        df.groupby("AGLOMERADO")["P21_real"]
          .mean()
          .reset_index()
          .rename(columns={"P21_real": "P21_real_promedio"})
    )

    return df_ingreso


# ======================================================
# 3) FUNCIÓN: GRAFICAR MAPA PARA UN AGLOMERADO
# ======================================================
def graficar_mapa_ingreso(geojson_path, df_ingresos, aglomerado, anio, titulo, cmap):

    geo = gpd.read_file(geojson_path)

    geo["AGLOMERADO"] = pd.to_numeric(geo["eph_codagl"], errors="coerce")

    gdf = geo[geo["AGLOMERADO"] == aglomerado].copy()

    gdf = gdf.merge(df_ingresos, on="AGLOMERADO", how="left")

    gdf = gdf.to_crs(epsg=3857)

    fig, ax = plt.subplots(figsize=(9, 9))

    gdf.plot(
        ax=ax,
        column="P21_real_promedio",
        cmap=cmap,
        legend=True,
        edgecolor="black",
        linewidth=0.7,
        alpha=0.75,
        legend_kwds={
            "label": "Ingreso promedio REAL P21 (deflactado por IPC)",
            "shrink": 0.7
        }
    )

    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron)

    ax.set_axis_off()
    ax.set_title(f"Ingreso promedio REAL — {titulo} ({anio})", fontsize=12)

    plt.tight_layout()
    plt.show()


# ======================================================
# 4) FUNCIÓN PRINCIPAL
# ======================================================
def mapa_ingreso_anual(ruta_unificado, ruta_geojson, aglomerado, anio_objetivo, nombre_aglomerado, color):

    df_ipc = cargar_ipc_dataframe()

    df_ingresos = obtener_ingreso_real_promedio(
        ruta_unificado,
        aglomerado,
        anio_objetivo,
        df_ipc
    )

    graficar_mapa_ingreso(
        geojson_path=ruta_geojson,
        df_ingresos=df_ingresos,
        aglomerado=aglomerado,
        anio=anio_objetivo,
        titulo=nombre_aglomerado,
        cmap=color
    )


# ======================================================
# 5) LLAMADA FINAL
# ======================================================


# --- CÓRDOBA ---
mapa_ingreso_anual(
    ruta_unificado=RUTA_UNIFICADO,
    ruta_geojson=RUTA_GEOJSON,
    aglomerado=13,
    anio_objetivo=ANIO,
    nombre_aglomerado="Gran Córdoba",
    color="Blues"
)

# --- MENDOZA ---
mapa_ingreso_anual(
    ruta_unificado=RUTA_UNIFICADO,
    ruta_geojson=RUTA_GEOJSON,
    aglomerado=10,
    anio_objetivo=ANIO,
    nombre_aglomerado="Gran Mendoza",
    color="Oranges"
)
