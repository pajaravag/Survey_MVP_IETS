import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_data_protection_box

# 🔐 Safe float conversion helper
def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def render():
    st.header("7. 💡 Servicios Públicos del Banco de Leche Humana (BLH)")

    # ──────────────────────────────────────────────
    # Instrucciones Visuales
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
    > ℹ️ **¿Qué información debe registrar?**  
    Por favor indique el **costo mensual promedio** (en pesos COP) de los **servicios públicos** necesarios para el funcionamiento del Banco de Leche Humana (BLH).  
    Si un servicio no aplica, registre **0**.

    > 📝 **Ejemplo práctico:**  
    - Energía eléctrica: *150,000 COP*  
    - Agua y alcantarillado: *90,000 COP*  
    - Telefonía e internet: *70,000 COP*

    > 🔑 **Importancia:**  
    Estos datos permitirán estimar los **costos operativos** del BLH y apoyar análisis de sostenibilidad.

    """), unsafe_allow_html=True)

    st.markdown(render_data_protection_box("""
    > 🔒 La información suministrada será utilizada únicamente para los fines de este estudio y protegida conforme a la **Ley 1581 de 2012 (Habeas Data)**.
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
    # Render Inputs por Servicio
    # ──────────────────────────────────────────────

    for servicio in servicios:
        costo = st.number_input(
            f"💰 {servicio} (Costo mensual en $ COP)",
            min_value=0.0,
            step=1000.0,
            value=safe_float(stored_data.get(servicio, 0.0)),
            key=f"util_{servicio}",
            help=f"Ingrese el costo mensual promedio de {servicio}. Registre 0 si no aplica."
        )
        current_results[servicio] = costo

    # ──────────────────────────────────────────────
    # Validación de Completitud para Progreso
    # ──────────────────────────────────────────────

    has_data = any(value > 0 for value in current_results.values())
    st.session_state[completion_flag] = has_data

    # ──────────────────────────────────────────────
    # Botón de Guardado con Feedback
    # ──────────────────────────────────────────────

    if st.button("💾 Guardar sección - Servicios Públicos"):
        st.session_state[data_key] = current_results
        st.session_state[completion_flag] = any(value > 0 for value in current_results.values())

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de servicios públicos guardados exitosamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor verifique la conexión e intente nuevamente.")

    # ──────────────────────────────────────────────
    # Expander: Visualización de Datos Guardados
    # ──────────────────────────────────────────────

    with st.expander("🔍 Ver resumen de datos guardados"):
        st.write(st.session_state.get(data_key, current_results))
