# TP Analisis de datos

- Materia: Introducción al Análsis De Datos

***
### 📌 Descripción

El informe detalla el análisis anual de las tendencias de la tasa de desocupación, la tasa de empleo, la tasa de actividad y los ingresos de la población, cubriendo el período comprendido entre 2016 y 2024.

El trabajo realiza un análisis comparativo entre dos aglomerados:

* Gran Córdoba (Código 13)

* Gran Mendoza (Código 10)

### 📈 Indicadores Analizados: 
* Los principales indicadores estudiados fueron:

* Tasa de Actividad

* Tasa de Empleo

* Tasa de Desocupación

* Ingresos laborales (P21):

    * Valores nominales

    *  Valores reales ajustados por IPC

### 🛠 Tecnologías Utilizadas

Python (Pandas, NumPy, Matplotlib, Seaborn)

QGIS o GeoPandas (para mapas)

EPH – INDEC

***
# Análisis univariado de Ingresos

## Tasas laborales aglomerado de Córdoba y Mendoza
El gráfico muestra la evolución de las tasas de actividad, empleo y desocupación (2016-2025). Las tasas de actividad y empleo se mantuvieron estables, y la desocupación en valores moderados, excepto en 2020. Ese año, la desocupación aumentó bruscamente y la actividad bajó debido al impacto del COVID-19. A partir de 2021, todas las tasas iniciaron una recuperación, volviendo a niveles prepandemia.

<img width="1600" height="600" alt="Tasas Laborales" src="https://github.com/user-attachments/assets/7a29efbf-21bc-49b0-89c3-41bbc0b73dc6" />




## Comparación del Ingreso REAL (P21 ajustado por IPC)
Ingresos de Córdoba: El sueldo promedio en Córdoba alcanzó su máximo en 2017, seguido de una caída sostenida (pérdida de poder adquisitivo) entre 2018 y 2023. Se proyecta una recuperación significativa en 2025.

Ingresos de Mendoza: Mendoza mostró una trayectoria similar, con un máximo en 2017 y un descenso constante hasta 2023. Su recuperación proyectada para 2025 es más leve que la de Córdoba, y sus ingresos reales se mantuvieron ligeramente inferiores durante todo el período.

<img width="1600" height="700" alt="Ingreso P21" src="https://github.com/user-attachments/assets/5f93d57f-2c74-47de-b523-c24254512160" />




## Regresión Lineal Múltiple

Los gráficos muestran que el modelo de regresión predice los ingresos con precisión moderada, cumple razonablemente con los supuestos estadísticos (homoscedasticidad y normalidad), y funciona de forma similar en 2017 y 2023, aunque con algo menos de precisión en 2023 debido al aumento de la desigualdad y la variabilidad salarial.

En el presente trabajo se utilizó el modelo de regresión lineal múltiple utilizando las variables.

Variable dependiente:
* P21

Variables independientes:
* Sexo: CH0
* Edad: CH06
* Años de educación: NIVEL_ED
* Sector de actividad: PP04B_COD
* Categoría ocupacional: CAT_OCUP
* Rama / tipo de empleo: PP04D_COD
* Formalidad laboral: PP07H
* Antigüedad en el puesto: PP07A
* Horas trabajadas: PP3E_TOT

<img width="1425" height="833" alt="Captura de pantalla 2025-11-28 132901" src="https://github.com/user-attachments/assets/6ebd1c62-f155-4ce0-a95a-3af16cb46753" />

***

### 2025 - UTN FRA
