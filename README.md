# Melate Retro — Sistema Personal de IA

## Estructura del proyecto

```
melate_retro/
├── config.py        # Todos los parámetros del algoritmo (editar aquí para ajustar filtros)
├── data.py          # Ingesta de datos históricos y cálculo de números calientes
├── engine.py        # Motor de filtrado y generador de combinaciones
├── app.py           # Interfaz Streamlit (solo presentación)
├── test_engine.py   # Suite de tests unitarios
└── requirements.txt
```

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecutar la app

```bash
streamlit run app.py
```

## Ejecutar los tests

```bash
pytest test_engine.py -v
```

## Ajustar los filtros del algoritmo

Abre `config.py` y modifica `FilterConfig`:

| Parámetro         | Por defecto | Descripción                                      |
|-------------------|-------------|--------------------------------------------------|
| `sum_min`         | 105         | Suma mínima aceptable de la combinación          |
| `sum_max`         | 135         | Suma máxima aceptable de la combinación          |
| `even_count`      | 3           | Exactamente N números pares requeridos           |
| `low_threshold`   | 19          | Límite superior del rango "bajo"                 |
| `low_count`       | 3           | Exactamente N números bajos requeridos           |
| `min_spread`      | 26          | Diferencia mínima entre el mayor y menor número  |
| `max_consecutive` | 1           | Máximo de pares consecutivos permitidos          |
| `hot_numbers_top_n` | 8         | Cuántos números "calientes" considerar           |
| `recent_draws`    | 30          | Ventana de sorteos para calcular rachas          |

## Actualizar la fuente de datos

Cuando Lotería Nacional publique el endpoint CSV oficial, actualiza `DataConfig.csv_url` en `config.py`.
El formato esperado es un CSV con columnas: `R1, R2, R3, R4, R5, R6`.
