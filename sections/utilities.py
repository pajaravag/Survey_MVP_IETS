import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_data_protection_box, render_compact_example_box

# 🔐 Safe float conversion helper
def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def render():
    st.header("7. 💡 Servicios Públicos del Banco de Leche Humana (BLH)")

    # ──────────────────────────────────────────────
    # Cuadros de Instrucción Visual
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
**¿Qué información debe registrar?**  
Por favor indique el **costo mensual promedio** en pesos colombianos (**COP**) de los **servicios públicos** asociados al funcionamiento del Banco de Leche Humana (BLH).  
Si un servicio **no aplica** o **no genera costos específicos**, registre **0**.
    """), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**  
- Energía eléctrica: *150,000 COP*  
- Agua y alcantarillado: *90,000 COP*  
- Telefonía e internet: *70,000 COP*
    """), unsafe_allow_html=True)

    st.markdown(render_data_protection_box("""
🔐 **Nota legal:**  
La información será utilizada exclusivamente para fines de análisis económico de forma agregada y bajo la protección de la **Ley 1581 de 2012 (Habeas Data)**.
    """), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Variables de Estado
    # ──────────────────────────────────────────────

    prefix = "servicios_publicos__"
    completion_flag = prefix + "completed"
    data_key = prefix + "data"

    stored_data = st.session_state.get(data_key, {})

    servicios = [
        "Suministro de energía",
        "Suministro de agua y alcantarillado",
        "Telefonía fija e internet"
    ]

    current_results = {}

    # ──────────────────────────────────────────────
    # Formulario de Servicios Públicos
    # ──────────────────────────────────────────────

    for servicio in servicios:
        costo = st.number_input(
            f"💰 {servicio} (Costo mensual en $ COP)",
            min_value=0.0,
            step=1000.0,
            value=safe_float(stored_data.get(servicio, 0.0)),
            key=f"util_{servicio}",
            help=f"Ingrese el costo mensual promedio asociado a {servicio}. Use 0 si no se incurre en este gasto."
        )
        current_results[servicio] = costo

    # ──────────────────────────────────────────────
    # Validación de Completitud
    # ──────────────────────────────────────────────

    has_data = any(value > 0 for value in current_results.values())
    st.session_state[completion_flag] = has_data

    # ──────────────────────────────────────────────
    # Botón de Guardado
    # ──────────────────────────────────────────────

    if st.button("💾 Guardar sección - Servicios Públicos"):
        st.session_state[data_key] = current_results
        st.session_state[completion_flag] = has_data

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de servicios públicos guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")

    # ──────────────────────────────────────────────
    # Expander: Resumen de Datos Guardados
    # ──────────────────────────────────────────────

    with st.expander("🔍 Ver resumen de datos guardados"):
        st.write(st.session_state.get(data_key, current_results))
