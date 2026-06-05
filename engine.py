"""
engine.py — Motor de filtrado y generación de combinaciones.

Responsabilidades únicas de este módulo:
  - Validar si una combinación pasa los filtros heurísticos.
  - Generar boletos candidatos usando estrategia de densidad compuesta.
  - Retornar resultados y estadísticas de ejecución.

Este módulo no importa Streamlit. Es 100% testeable con pytest.
"""

import logging
import random
from dataclasses import dataclass, field
from itertools import combinations

from config import FILTERS, GENERATOR, LOTTERY
from data import HotNumbers, is_already_drawn

logger = logging.getLogger(__name__)

# Umbral: si el universo válido es menor a este número,
# se usa selección directa en lugar de búsqueda aleatoria.
_DIRECT_SELECTION_THRESHOLD = 5_000


# ---------------------------------------------------------------------------
# Tipos de retorno
# ---------------------------------------------------------------------------

@dataclass
class GenerationResult:
    tickets: list[list[int]] = field(default_factory=list)
    total_attempts: int = 0
    requested: int = 0

    @property
    def found_count(self) -> int:
        return len(self.tickets)

    @property
    def success_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return round(self.found_count / self.total_attempts * 100, 2)


# ---------------------------------------------------------------------------
# Filtros individuales (cada uno con responsabilidad única)
# ---------------------------------------------------------------------------

def _passes_sum_range(combo: list[int]) -> bool:
    """Filtro 1 — La suma debe caer dentro del rango estadístico histórico."""
    return FILTERS.sum_min <= sum(combo) <= FILTERS.sum_max


def _passes_even_odd_balance(combo: list[int]) -> bool:
    """Filtro 2 — Balance exacto de pares e impares."""
    even_count = sum(1 for n in combo if n % 2 == 0)
    return even_count == FILTERS.even_count


def _passes_zone_balance(combo: list[int]) -> bool:
    """Filtro 3 — Balance exacto de números bajos (1-19) y altos (20-39)."""
    low_count = sum(1 for n in combo if n <= FILTERS.low_threshold)
    return low_count == FILTERS.low_count


def _passes_spread(combo: list[int]) -> bool:
    """Filtro 4 — Dispersión geométrica mínima entre extremos."""
    return (combo[-1] - combo[0]) >= FILTERS.min_spread


def _passes_consecutive_limit(combo: list[int]) -> bool:
    """Filtro 5 — Controla pares de números consecutivos adyacentes."""
    consecutive_pairs = sum(
        1 for i in range(len(combo) - 1)
        if combo[i + 1] - combo[i] == 1
    )
    return consecutive_pairs <= FILTERS.max_consecutive


# Pipeline de filtros: orden de menor a mayor costo computacional
_FILTER_PIPELINE = [
    _passes_sum_range,
    _passes_even_odd_balance,
    _passes_zone_balance,
    _passes_spread,
    _passes_consecutive_limit,
]


def is_optimal_combination(combo: list[int]) -> bool:
    """
    Aplica el pipeline completo de filtros sobre una combinación ordenada.
    Usa short-circuit: en cuanto un filtro falla, descarta la combinación.
    """
    return all(f(combo) for f in _FILTER_PIPELINE)


# ---------------------------------------------------------------------------
# Construcción del universo válido completo (para universos pequeños)
# ---------------------------------------------------------------------------

def build_valid_universe() -> list[list[int]]:
    """
    Genera todas las combinaciones válidas de forma determinista.
    Se usa cuando el universo es lo suficientemente pequeño para
    ser enumerado completo (< _DIRECT_SELECTION_THRESHOLD).
    """
    universe = []
    for combo in combinations(range(LOTTERY.min_number, LOTTERY.max_number + 1), LOTTERY.pick_count):
        if is_optimal_combination(list(combo)):
            universe.append(list(combo))
    logger.info("Universo válido construido: %d combinaciones.", len(universe))
    return universe


# ---------------------------------------------------------------------------
# Generador de candidatos (estrategia aleatoria — para universos grandes)
# ---------------------------------------------------------------------------

def _generate_candidate(hot: list[int], cold: list[int]) -> list[int]:
    """
    Estrategia de densidad compuesta:
    mitad de números calientes + mitad del resto, ordenados.
    """
    half = LOTTERY.pick_count // 2
    selected = random.sample(hot, half) + random.sample(cold, half)
    return sorted(selected)


# ---------------------------------------------------------------------------
# API pública del módulo
# ---------------------------------------------------------------------------

def generate_tickets(
    requested: int,
    hot_numbers: HotNumbers,
    historical_set: set[frozenset],
) -> GenerationResult:
    """
    Genera hasta `requested` boletos que pasen todos los filtros
    y no hayan salido antes en el histórico.

    Estrategia adaptativa:
    - Universo pequeño (< 5,000): construye el universo completo y selecciona al azar.
    - Universo grande: búsqueda aleatoria con pipeline de filtros.
    """
    capped_request = min(requested, GENERATOR.max_tickets)
    result = GenerationResult(requested=capped_request)
    seen_this_run: set[frozenset] = set()

    # --- Estrategia 1: Selección directa del universo completo ---
    universe = build_valid_universe()

    if len(universe) <= _DIRECT_SELECTION_THRESHOLD:
        # Filtrar los que ya salieron en el histórico
        candidates = [
            c for c in universe
            if not is_already_drawn(c, historical_set)
        ]
        random.shuffle(candidates)

        for candidate in candidates[:capped_request]:
            result.total_attempts += 1
            result.tickets.append(candidate)

        logger.info(
            "Selección directa: %d válidas en universo de %d, entregando %d boletos.",
            len(candidates), len(universe), result.found_count
        )
        return result

    # --- Estrategia 2: Búsqueda aleatoria (universo grande) ---
    while (
        result.found_count < capped_request
        and result.total_attempts < GENERATOR.max_attempts
    ):
        result.total_attempts += 1
        candidate = _generate_candidate(hot_numbers.hot, hot_numbers.cold)
        candidate_key = frozenset(candidate)

        if candidate_key in seen_this_run:
            continue
        if not is_optimal_combination(candidate):
            continue
        if is_already_drawn(candidate, historical_set):
            continue

        seen_this_run.add(candidate_key)
        result.tickets.append(candidate)

    if result.found_count < capped_request:
        logger.warning(
            "Solo se encontraron %d de %d boletos solicitados en %d intentos.",
            result.found_count, capped_request, result.total_attempts,
        )

    return result
