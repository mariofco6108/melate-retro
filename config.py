
FILT"""
config.py — Parámetros centralizados del sistema.

Todos los valores ajustables del algoritmo viven aquí.
Modificar este archivo no requiere tocar la lógica de negocio.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LotteryConfig:
    """Parámetros del sorteo Melate Retro."""
    min_number: int = 1
    max_number: int = 39
    pick_count: int = 6


@dataclass(frozen=True)
class FilterConfig:
    """
    Umbrales del Embudo de Filtrado.

    sum_min / sum_max   — Rango de suma aceptable (Campana de Gauss histórica).
    even_count          — Cantidad exacta de números pares requerida.
    low_threshold       — Límite superior del rango "bajo" (inclusive).
    low_count           — Cantidad exacta de números bajos requerida.
    min_spread          — Diferencia mínima entre el mayor y el menor número.
    max_consecutive     — Máximo de pares consecutivos permitidos.
    hot_numbers_top_n   — Cuántos números "calientes" tomar del histórico reciente.
    recent_draws        — Ventana de sorteos recientes para calcular rachas.

    Universo válido con estos parámetros: ~624 combinaciones de 3,262,623 posibles.
    Probabilidad de acertar: 1 en 624 (vs 1 en 3,262,623 sin filtros).
    """
    sum_min: int = 119
    sum_max: int = 122
    even_count: int = 3
    low_threshold: int = 19
    low_count: int = 3
    min_spread: int = 38
    max_consecutive: int = 0
    hot_numbers_top_n: int = 8
    recent_draws: int = 30


@dataclass(frozen=True)
class GeneratorConfig:
    """Parámetros del generador de combinaciones."""
    max_attempts: int = 50_000
    max_tickets: int = 10


@dataclass(frozen=True)
class DataConfig:
    """Configuración de la fuente de datos."""
    # URL del CSV oficial. Actualizar cuando Lotería Nacional publique el endpoint.
    csv_url: str = "https://loterianacional.gob.mx/archivos/melate_retro.csv"
    cache_ttl_seconds: int = 3600
    result_columns: tuple = ("R1", "R2", "R3", "R4", "R5", "R6")


# Instancias listas para importar
LOTTERY = LotteryConfig()
FILTERS = FilterConfig()
GENERATOR = GeneratorConfig()
DATA = DataConfig()
ERS = FilterConfig()
GENERATOR = GeneratorConfig()
DATA = DataConfig()
