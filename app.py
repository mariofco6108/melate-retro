"""
app.py — Interfaz Streamlit de Melate Retro.

Este módulo SOLO se ocupa de presentación y orquestación.
Toda la lógica de negocio vive en engine.py y data.py.

Para ejecutar:
    streamlit run app.py
"""

import logging
from datetime import datetime

import streamlit as st

from config import GENERATOR
from data import get_hot_numbers, load_historical_data
from engine import generate_tickets

# ---------------------------------------------------------------------------
# Configuración global de logging (Streamlit no lo hace por defecto)
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

# ---------------------------------------------------------------------------
# Página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Predicciones Élite - Melate Retro",
    page_icon="🎰",
    layout="centered",
)

st.title("🎰 Melate Retro — Sistema Personal de IA")
st.markdown(
    "Descarga el histórico oficial, analiza rachas de la tómbola y aplica "
    "un **Embudo Extremo del 99.2% de descarte**."
)

# ---------------------------------------------------------------------------
# Carga de datos (cacheada automáticamente por @st.cache_data en data.py)
# ---------------------------------------------------------------------------
historical = load_historical_data()

if historical.is_live:
    st.success("✅ Conectado con éxito a la base de datos en tiempo real de la Lotería Nacional.")
else:
    st.warning(
        "⚠️ Servidor de Lotería Nacional fuera de línea temporalmente. "
        "Usando base de datos de respaldo."
    )

hot_numbers = get_hot_numbers(historical)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.header("🎛️ Panel de Control")
ticket_count = st.sidebar.slider(
    "¿Cuántos boletos deseas generar?",
    min_value=1,
    max_value=GENERATOR.max_tickets,
    value=3,
)

st.sidebar.subheader("🔥 Números Calientes en Racha")
st.sidebar.write(hot_numbers.hot)

# ---------------------------------------------------------------------------
# Inicializar session_state para persistir resultados entre re-renders
# ---------------------------------------------------------------------------
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ---------------------------------------------------------------------------
# Botón principal
# ---------------------------------------------------------------------------
if st.button("🚀 Ejecutar Algoritmo Élite"):
    with st.spinner("Procesando combinaciones y aplicando filtros..."):
        result = generate_tickets(
            requested=ticket_count,
            hot_numbers=hot_numbers,
            historical_set=historical.historical_set,
        )
    st.session_state.last_result = result

# ---------------------------------------------------------------------------
# Presentación de resultados (persiste en session_state)
# ---------------------------------------------------------------------------
result = st.session_state.last_result

if result is not None:
    st.markdown("---")
    st.subheader(f"🎯 Tus {result.found_count} Jugadas Sugeridas")
    st.info(
        f"🔬 El sistema analizó {result.total_attempts:,} combinaciones candidatas "
        f"para encontrar las que mejor se ajustan al patrón ganador histórico."
    )

    for idx, ticket in enumerate(result.tickets, start=1):
        st.markdown(f"### 🎫 Boleto #{idx:02d}")
        balls = " ".join(f"` {n:02d} `" for n in ticket)
        even = sum(1 for n in ticket if n % 2 == 0)
        low  = sum(1 for n in ticket if n <= 19)
        st.markdown(
            f"{balls} | **Suma:** {sum(ticket)} "
            f"| **Par/Impar:** {even}:{6 - even} "
            f"| **Zonas:** {low}:{6 - low}"
        )
        st.markdown("---")

    # Bloque de texto para copiar
    today = datetime.now().strftime("%d/%m/%Y")
    copy_text = f"--- MIS JUGADAS MELATE RETRO ({today}) ---\n"
    for idx, ticket in enumerate(result.tickets, start=1):
        copy_text += f"Boleto #{idx}: {ticket} (Suma: {sum(ticket)})\n"

    st.text_area("📋 Copiar combinaciones listas:", value=copy_text, height=120)
