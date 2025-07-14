import streamlit as st
import pandas as pd
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box

# 🔐 Conversión segura
def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

def render():
    st.header("11. 💰 Depreciación, Mantenimiento e Impuestos del BLH (Preguntas 28 a 31)")

    prefix = "depreciacion__"
    completion_flag = prefix + "completed"
    prev_data = st.session_state.get(prefix + "data", {})

    # ──────────────────────────────────────────────
    # Instrucciones Oficiales
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
Por favor registre los siguientes **costos asociados a los activos físicos** del Banco de Leche Humana (BLH).  
Si algún dato no aplica o no dispone de la información, registre **0**.

**Preguntas oficiales:**  
2️⃣8️⃣ **Valor mensual de depreciación (COP/mes)**  
2️⃣9️⃣ **Porcentaje anual promedio de depreciación de activos (%)**  
3️⃣0️⃣ **Presupuesto anual estimado de mantenimiento (COP/año)**  
3️⃣1️⃣ **Costo anual estimado de impuestos asociados (COP/año)**
    """), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**  

| Concepto                                | Valor            |
|-----------------------------------------|------------------|
| Depreciación mensual                    | 50,000 COP       |
| Porcentaje anual depreciación           | 20%              |
| Mantenimiento anual                     | 300,000 COP      |
| Impuestos anuales                       | 150,000 COP      |
    """), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Pregunta 2️⃣8️⃣ Valor mensual de depreciación
    # ──────────────────────────────────────────────

    st.subheader("2️⃣8️⃣ 💸 Valor mensual estimado de depreciación (COP/mes):")
    valor_mensual = st.number_input(
        "Valor mensual de depreciación (COP):",
        min_value=0.0, step=10000.0,
        value=safe_float(prev_data.get("valor_mensual_cop", 0.0)),
        help="Incluye depreciación mensual de infraestructura, equipos o vehículos del BLH."
    )

    # ──────────────────────────────────────────────
    # Pregunta 2️⃣9️⃣ Porcentaje anual de depreciación
    # ──────────────────────────────────────────────

    st.subheader("2️⃣9️⃣ 📊 Porcentaje anual promedio de depreciación (%):")
    porcentaje_depreciacion = st.slider(
        "Porcentaje anual promedio de depreciación:",
        min_value=0, max_value=100, step=1,
        value=safe_int(prev_data.get("porcentaje_depreciacion", 0)),
        help="Ejemplo: 20%. Si no aplica, registre 0."
    )

    # ──────────────────────────────────────────────
    # Pregunta 3️⃣0️⃣ Presupuesto anual mantenimiento
    # ──────────────────────────────────────────────

    st.subheader("3️⃣0️⃣ 🔧 Presupuesto anual estimado de mantenimiento (COP):")
    mantenimiento_anual = st.number_input(
        "Presupuesto anual de mantenimiento (COP):",
        min_value=0.0, step=10000.0,
        value=safe_float(prev_data.get("mantenimiento_anual_cop", 0.0)),
        help="Incluye mantenimiento preventivo y correctivo de equipos o infraestructura del BLH."
    )

    # ──────────────────────────────────────────────
    # Pregunta 3️⃣1️⃣ Costo anual de impuestos
    # ──────────────────────────────────────────────

    st.subheader("3️⃣1️⃣ 🏛️ Costo anual estimado de impuestos asociados (COP):")
    impuestos_anuales = st.number_input(
        "Costo anual estimado de impuestos (COP):",
        min_value=0.0, step=10000.0,
        value=safe_float(prev_data.get("impuestos_anuales_cop", 0.0)),
        help="Incluye impuestos prediales, vehículos o similares. Use 0 si no aplica."
    )

    # ──────────────────────────────────────────────
    # Validación y Compleción
    # ──────────────────────────────────────────────

    is_complete = True  # Sección siempre marcada como completada

    st.session_state[completion_flag] = is_complete

    # ──────────────────────────────────────────────
    # Guardado y Navegación
    # ──────────────────────────────────────────────

    if st.button("💾 Guardar sección - Depreciación e Impuestos"):
        st.session_state[prefix + "data"] = {
            "valor_mensual_cop": valor_mensual,
            "porcentaje_depreciacion": porcentaje_depreciacion,
            "mantenimiento_anual_cop": mantenimiento_anual,
            "impuestos_anuales_cop": impuestos_anuales
        }

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
