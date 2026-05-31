"""
test_engine.py — Tests unitarios del motor de filtrado.

Ejecutar con:  pytest test_engine.py -v

La separación de capas permite testear engine.py sin levantar Streamlit.
"""

import pytest
from engine import (
    _passes_consecutive_limit,
    _passes_even_odd_balance,
    _passes_spread,
    _passes_sum_range,
    _passes_zone_balance,
    is_optimal_combination,
)
from data import is_already_drawn


# ---------------------------------------------------------------------------
# Tests de filtros individuales
# Parámetros activos: sum=114-127, spread>=29, max_consecutive=0
# ---------------------------------------------------------------------------

class TestSumRange:
    def test_valid_sum(self):
        # suma 120 — dentro del rango 114-127
        assert _passes_sum_range([1, 15, 20, 25, 30, 29]) is True

    def test_sum_too_low(self):
        assert _passes_sum_range([1, 2, 3, 4, 5, 6]) is False   # suma 21

    def test_sum_too_high(self):
        assert _passes_sum_range([30, 31, 32, 33, 34, 35]) is False  # suma 195

    def test_boundary_min(self):
        # suma exacta = 114
        combo = [1, 15, 19, 24, 28, 27]
        assert _passes_sum_range(sorted(combo)) is True

    def test_boundary_max(self):
        # suma exacta = 127
        combo = [6, 11, 12, 29, 33, 36]
        assert _passes_sum_range(sorted(combo)) is True


class TestEvenOddBalance:
    def test_exactly_three_even(self):
        assert _passes_even_odd_balance([2, 4, 6, 1, 3, 5]) is True

    def test_too_many_even(self):
        assert _passes_even_odd_balance([2, 4, 6, 8, 1, 3]) is False

    def test_no_even(self):
        assert _passes_even_odd_balance([1, 3, 5, 7, 9, 11]) is False


class TestZoneBalance:
    def test_three_low_three_high(self):
        assert _passes_zone_balance([1, 10, 19, 20, 30, 39]) is True

    def test_all_low(self):
        assert _passes_zone_balance([1, 5, 9, 13, 17, 19]) is False

    def test_all_high(self):
        assert _passes_zone_balance([20, 25, 28, 32, 35, 39]) is False


class TestSpread:
    def test_sufficient_spread(self):
        # spread 35 >= 29
        assert _passes_spread([1, 10, 15, 20, 25, 36]) is True

    def test_insufficient_spread(self):
        # spread 10 < 29
        assert _passes_spread([10, 12, 14, 16, 18, 20]) is False

    def test_boundary_spread(self):
        # spread exacto = 29
        assert _passes_spread([5, 10, 15, 20, 25, 34]) is True


class TestConsecutiveLimit:
    def test_zero_consecutive(self):
        # max_consecutive=0: ningún par adyacente permitido
        assert _passes_consecutive_limit([1, 5, 10, 15, 20, 25]) is True

    def test_one_consecutive_pair_fails(self):
        # Con max_consecutive=0, incluso 1 par consecutivo falla
        assert _passes_consecutive_limit([1, 2, 10, 15, 20, 25]) is False

    def test_two_consecutive_pairs_fails(self):
        assert _passes_consecutive_limit([1, 2, 9, 10, 20, 25]) is False


# ---------------------------------------------------------------------------
# Tests de integración del pipeline completo
# Combos verificados contra los filtros activos: sum=114-127, spread>=29, consec=0
# ---------------------------------------------------------------------------

class TestOptimalCombination:
    def test_known_passing_combo(self):
        # suma=119, pares=18,20,28→3, bajos=5,11,18→3, spread=32, consecutivos=0
        combo = sorted([5, 11, 18, 20, 28, 37])
        assert is_optimal_combination(combo) is True

    def test_known_passing_combo_2(self):
        # suma=115, pares=16,22,28→3, bajos=5,13,16→3, spread=26... ajustar
        # suma=117, pares=2,18,24→3, bajos=2,17,18→3, spread=27... no
        # suma=119, pares=6,24,28→3, bajos=1,13,19→3, spread=33, consec=0
        combo = sorted([1, 13, 19, 24, 28, 34])
        assert is_optimal_combination(combo) is True

    def test_fails_sum_too_low(self):
        combo = sorted([1, 2, 3, 4, 5, 6])   # suma 21
        assert is_optimal_combination(combo) is False

    def test_fails_sum_too_high(self):
        combo = sorted([20, 22, 24, 26, 28, 30])  # suma 150
        assert is_optimal_combination(combo) is False

    def test_fails_even_odd(self):
        # 4 pares
        combo = sorted([3, 12, 17, 22, 28, 38])
        assert is_optimal_combination(combo) is False

    def test_fails_consecutive(self):
        # tiene par consecutivo (1,2) — con max_consecutive=0 debe fallar
        combo = sorted([1, 2, 15, 22, 28, 35])
        assert is_optimal_combination(combo) is False


# ---------------------------------------------------------------------------
# Tests de la verificación histórica O(1)
# ---------------------------------------------------------------------------

class TestHistoricalLookup:
    def setup_method(self):
        self.historical_set = {
            frozenset([3, 11, 15, 18, 27, 36]),
            frozenset([5, 14, 19, 24, 33, 38]),
        }

    def test_existing_combo_detected(self):
        assert is_already_drawn([3, 11, 15, 18, 27, 36], self.historical_set) is True

    def test_new_combo_not_detected(self):
        assert is_already_drawn([1, 8, 14, 22, 31, 37], self.historical_set) is False

    def test_order_independent(self):
        assert is_already_drawn([36, 27, 18, 15, 11, 3], self.historical_set) is True
