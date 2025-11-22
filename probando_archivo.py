
import pandas as pd

df = pd.read_csv("individual_unificado.txt", sep=";")
print(df["anio"].unique())
print(df["trimestre"].unique())