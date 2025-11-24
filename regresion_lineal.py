import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

from ipc_trimestral import ipc_acumulado


# ============================================================
# 1) Cargar y preparar base completa
# ============================================================
def cargar_datos(ruta):
    df = pd.read_csv(ruta, sep=";", low_memory=False)

    # Convertir columnas numéricas
    cols_num = [
        "CH04", "CH06", "NIVEL_ED", "PP04B_COD",
        "PP04D_COD", "REGION", "P21", "PONDERA"
    ]
    for c in cols_num:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Eliminar ingresos inválidos
    df = df[df["P21"] > 0]

    return df


# ============================================================
# 2) Crear DataFrame de IPC acumulado
# ============================================================
def crear_df_ipc(ipc_acumulado):
    ipc_rows = []
    for key, val in ipc_acumulado.items():
        y, t = key.split("-")
        ipc_rows.append({
            "anio": int(y),
            "trimestre": int(t.replace("Trim", "")),
            "IPC": val
        })
    return pd.DataFrame(ipc_rows)


# ============================================================
# 3) Unir IPC + calcular ingreso real
# ============================================================
def aplicar_ipc(df, df_ipc):
    df = df.merge(df_ipc, on=["anio", "trimestre"], how="left")
    df["P21_real"] = df["P21"] / df["IPC"]
    return df


# ============================================================
# 4) Preparar variables predictoras  (MEJORADO)
# ============================================================
def preparar_X_y(df):
    y = df["P21_real"]

    #  Nuevas variables agregadas:
    variables_numericas = ["CH06"]
    variables_categoricas = [
        "CH04",        # sexo
        "NIVEL_ED",    # educación
        "PP04B_COD",   # categoría ocupacional
        "PP04D_COD",   # rama / tipo de empleo
        "REGION"       # región INDEC
    ]

    X_num = df[variables_numericas]

    # OneHot para variables categóricas
    enc = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    X_cat = enc.fit_transform(df[variables_categoricas])

    X = np.hstack([X_num, X_cat])

    feature_names = variables_numericas + list(
        enc.get_feature_names_out(variables_categoricas)
    )

    return X, y, feature_names, enc


# ============================================================
# 5) Entrenar modelo lineal
# ============================================================
def entrenar_modelo(X, y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    modelo = LinearRegression()
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)

    return modelo, X_test, y_test, y_pred


# ============================================================
# 6) Mostrar métricas
# ============================================================
def mostrar_metricas(y_test, y_pred):
    print("\n================ METRICAS DEL MODELO ================")
    print("R2 :", round(r2_score(y_test, y_pred), 4))
    print("RMSE:", round(np.sqrt(mean_squared_error(y_test, y_pred)), 2))
    print("MAE:", round(mean_absolute_error(y_test, y_pred), 2))


# ============================================================
# 7) Gráfico
# ============================================================
def graficar_predicciones(y_test, y_pred, nombre_aglo):
    ESCALA = 10_000

    y_test_m = y_test / ESCALA
    y_pred_m = y_pred / ESCALA

    plt.figure(figsize=(9,7))
    plt.scatter(y_test_m, y_pred_m, alpha=0.3)

    min_v = min(min(y_test_m), min(y_pred_m))
    max_v = max(max(y_test_m), max(y_pred_m))

    plt.plot([min_v, max_v], [min_v, max_v], 'r--', label="Predicción perfecta")

    plt.xlabel("Ingreso real observado (miles de $)")
    plt.ylabel("Ingreso predicho (miles de $)")
    plt.title(f"Predicción de ingresos — {nombre_aglo}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# ============================================================
# 8) Coeficientes
# ============================================================
def mostrar_coeficientes(modelo, feature_names):
    print("\n=========== COEFICIENTES DEL MODELO ===========")
    for name, coef in zip(feature_names, modelo.coef_):
        print(f"{name:20s} --> {coef:.4f}")


# ============================================================
# 9) Correr modelo por trimestre
# ============================================================
def correr_modelo_trimestre(df_base, df_ipc, aglo, nombre_aglo, anio, trimestre):
    print(f"\n=========== {nombre_aglo}  {anio}-{trimestre}T ===========")

    df = df_base.copy()
    df = df[
        (df["AGLOMERADO"] == aglo) &
        (df["anio"] == anio) &
        (df["trimestre"] == trimestre)
    ]

    df = aplicar_ipc(df, df_ipc)

    X, y, feature_names, enc = preparar_X_y(df)

    modelo, X_test, y_test, y_pred = entrenar_modelo(X, y)

    mostrar_metricas(y_test, y_pred)
    graficar_predicciones(y_test, y_pred, f"{nombre_aglo} {anio} T{trimestre}")
    #mostrar_coeficientes(modelo, feature_names)


# ============================================================
# 10) EJECUCIÓN FINAL
# ============================================================

df_base = cargar_datos("IndividualUnificado/individual_unificado.txt")
df_ipc = crear_df_ipc(ipc_acumulado)

# Córdoba
correr_modelo_trimestre(df_base, df_ipc, 13, "Gran Córdoba", 2024, 4)

# Mendoza
correr_modelo_trimestre(df_base, df_ipc, 10, "Gran Mendoza", 2024, 4)
