""" import pandas as pd

#1 Cargar el archivo (usa ; como separador)
df = pd.read_csv("usu_individual_T225.txt", sep=";", low_memory=False)

# Mostrar los aglomerados únicos
print("Listado de códigos de aglomerado:")
print(df['AGLOMERADO'].unique())
"""
import sys
import pandas as pd

# 🔧 Forzar codificación UTF-8 para imprimir correctamente acentos y símbolos
sys.stdout.reconfigure(encoding='utf-8')

# 📂 Leer el archivo de microdatos (ajustá el nombre si cambia)
df = pd.read_csv("usu_hogar_T225.txt", sep=";", low_memory=False)

codigos_presentes = sorted(df['AGLOMERADO'].unique())

# 🗺️ Diccionario oficial de aglomerados EPH (2025)
aglomerados = {
    2: "Gran La Plata",
    3: "Bahía Blanca - Cerri",
    4: "Gran Rosario",
    5: "Gran Santa Fé",
    6: "Gran Paraná",
    7: "Posadas",
    8: "Gran Resistencia",
    9: "Comodoro Rivadavia - Rada Tilly",
    10: "Gran Mendoza",
    12: "Corrientes",
    13: "Gran Córdoba",
    14: "Concordia",
    15: "Formosa",
    17: "Neuquén – Plottier",
    18: "Santiago del Estero - La Banda",
    19: "Jujuy - Palpalá",
    20: "Río Gallegos",
    22: "Gran Catamarca",
    23: "Gran Salta",
    25: "La Rioja",
    26: "Gran San Luis",
    27: "Gran San Juan",
    29: "Gran Tucumán - Tafí Viejo",
    30: "Santa Rosa – Toay",
    31: "Ushuaia - Río Grande",
    32: "Ciudad Autónoma de Buenos Aires",
    33: "Partidos del GBA",
    34: "Mar del Plata",
    36: "Río Cuarto",
    38: "San Nicolás – Villa Constitución",
    91: "Rawson – Trelew",
    93: "Viedma – Carmen de Patagones"
}

#  Mostrar resultados ordenados
print("Listado de aglomerados detectados en la base:\n")
for codigo in codigos_presentes:
    nombre = aglomerados.get(codigo, "Desconocido")
    print(f"{codigo:02d} → {nombre}")