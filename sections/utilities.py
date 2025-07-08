import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row

# 🔐 Safe float conversion helper
def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def render():
    st.header("7. Servicios Públicos")

    st.markdown("""
    ### 💡 Instrucciones:
    Registre el **costo mensual promedio** de los servicios públicos asociados al funcionamiento del Banco de Leche Humana (BLH).

    - Si algún servicio no aplica, registre **0**.
    - Los datos son claves para el análisis de costos operativos del BLH.
    """)

    prefix = "servicios_publicos__"
    completion_flag = prefix + "completed"
    data_key = prefix + "data"

    stored_data = st.session_state.get(data_key, {})

    servicios = [
        "Suministro de energía",
        "Suministro de agua y alcantarillado",
        "Telefonía fija e internet"
    ]

    # Prepare dictionary to capture current inputs
    current_results = {}

    # 🔹 Render inputs
    for servicio in servicios:
        costo = st.number_input(
            f"{servicio} ($ COP/mes)",
            min_value=0.0,
            step=1000.0,
            value=safe_float(stored_data.get(servicio, 0.0)),
            key=f"util_{servicio}"
        )
        current_results[servicio] = costo

    # 🔍 Live Completion Flag: always updated on every render
    has_data = any(value > 0 for value in current_results.values())
    st.session_state[completion_flag] = has_data

    # 🔹 Save Button
    if st.button("💾 Guardar sección - Servicios Públicos"):
        st.session_state[data_key] = current_results
        st.session_state[completion_flag] = any(value > 0 for value in current_results.values())  # Recheck after save

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos guardados correctamente en Google Sheets.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")

    # 🔹 Review Data
    with st.expander("🔍 Ver datos guardados en esta sección"):
        st.write(st.session_state.get(data_key, current_results))
