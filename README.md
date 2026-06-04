# Análisis de frecuencias en resultados históricos de loterías

Proyecto personal de análisis exploratorio de datos con Python. El objetivo es integrar resultados históricos de distintas loterías, limpiar formatos diferentes y calcular métricas de frecuencia para identificar patrones históricos de aparición.

> **Nota importante:** este proyecto no intenta predecir resultados futuros ni recomendar apuestas. Las loterías son juegos de azar; el análisis se usa como práctica de carga, limpieza, transformación, exploración, visualización y exportación de datos.

## Juegos analizados

- **Melate**: resultados históricos descargados y actualizados manualmente.
- **Mega Millions**: dataset histórico de NY Open Data.
- **Powerball**: dataset histórico de NY Open Data.

## Fuentes de datos

- **Lotería Nacional**: resultados oficiales de Melate y últimos sorteos publicados.
- **NY Open Data**: datasets públicos históricos de Mega Millions y Powerball.
- **Pakin/GitHub**: fuente alternativa utilizada como referencia para histórico de Melate en CSV.

## Herramientas utilizadas

- Python
- pandas
- NumPy
- Matplotlib
- Jupyter Notebook
- CSV
- Análisis exploratorio de datos
- Limpieza y transformación de datos
- Automatización de funciones reutilizables

## Estructura del proyecto

```text
lottery_frequency_analysis/
├── data/
│   ├── raw/              # Archivos originales descargados
│   └── processed/        # Tablas generadas por el análisis
├── notebooks/
│   └── 01_lottery_frequency_analysis.ipynb
├── requirements.txt
└── README.md
```

## Qué hace el análisis

1. Carga datos históricos con formatos distintos.
2. Normaliza fechas y columnas numéricas.
3. Estandariza las columnas de números principales y números especiales.
4. Calcula frecuencia de aparición de números principales y bolas especiales.
5. Calcula última fecha registrada y brechas promedio, mínimas y máximas entre apariciones.
6. Genera un resumen comparativo de los juegos analizados.
7. Crea visualizaciones con los números principales más frecuentes.
8. Exporta archivos CSV con resultados procesados.

## Principales salidas

Los resultados se guardan en `data/processed/`:

- `*_freq_main.csv`: frecuencia por número principal.
- `*_metrics_main.csv`: métricas completas por número principal.
- `*_top_main.csv`: números principales con más apariciones.
- `*_freq_special.csv`: frecuencia de bola especial/adicional.
- `*_metrics_special.csv`: métricas de bola especial/adicional.
- `*_top_special.csv`: ranking de bola especial/adicional.
- `resumen_general.csv`: resumen comparativo de juegos analizados.

## Cómo ejecutar

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Abrir el notebook:

```bash
jupyter notebook notebooks/01_lottery_frequency_analysis.ipynb
```

3. Ejecutar todas las celdas desde Jupyter Notebook.

El proyecto espera encontrar los archivos CSV originales dentro de la carpeta `data/raw/`. Los resultados procesados se generan automáticamente en `data/processed/`.

## Resultados principales

El análisis genera una tabla resumen con:

- Juego analizado.
- Número de sorteos analizados.
- Fecha inicial y fecha final del periodo histórico.
- Número principal más frecuente.
- Número de apariciones.
- Proporción sobre sorteos.
- Última fecha de aparición.

Además, incluye visualizaciones de los 10 números principales más frecuentes para Melate, Mega Millions y Powerball.

## Nota metodológica

Los resultados representan únicamente patrones históricos descriptivos. Una mayor frecuencia pasada no implica mayor probabilidad futura. El propósito del proyecto es demostrar un flujo completo de análisis de datos con información real, no generar predicciones.

