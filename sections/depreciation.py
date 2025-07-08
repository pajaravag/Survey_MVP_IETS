import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row

# 🔐 Safe conversion helpers
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
    st.header("10. Depreciación e Impuestos")

    st.markdown("""
    ### 🏗️ Instrucciones:
    Registre la información relacionada con la **depreciación de los equipos** y el **presupuesto de mantenimiento anual** del BLH:

    - **Depreciación mensual** (en COP).
    - **Porcentaje anual de depreciación**.
    - **Presupuesto anual de mantenimiento** (en COP).

    Si algún valor no aplica, registre **0**.
    """)

    prefix = "depreciacion__"
    completion_flag = prefix + "completed"
    prev_data = st.session_state.get(prefix + "data", {})

    # ─────────────────────────────────
    # Inputs con valores previos
    # ─────────────────────────────────

    valor_mensual = st.number_input(
        "Valor mensual asociado a la depreciación ($ COP/mes)",
        min_value=0.0, step=10000.0,
        value=safe_float(prev_data.get("valor_mensual_cop", 0.0)),
        key=prefix + "valor_mensual"
    )

    porcentaje = st.slider(
        "Porcentaje de depreciación promedio (%)",
        min_value=0, max_value=100, step=1,
        value=safe_int(prev_data.get("porcentaje_depreciacion", 20)),
        key=prefix + "porcentaje"
    )

    mantenimiento_anual = st.number_input(
        "Presupuesto anual de mantenimiento ($ COP/año)",
        min_value=0.0, step=10000.0,
        value=safe_float(prev_data.get("mantenimiento_anual_cop", 0.0)),
        key=prefix + "mantenimiento"
    )

    # ─────────────────────────────────
    # Automatic Progress Flag (✅ Real-time)
    # ─────────────────────────────────

    st.session_state[completion_flag] = any([
        valor_mensual > 0,
        porcentaje > 0,
        mantenimiento_anual > 0
    ])

    # ─────────────────────────────────
    # Save Button
    # ─────────────────────────────────

    if st.button("💾 Guardar sección - Depreciación e Impuestos"):
        st.session_state[prefix + "data"] = {
            "valor_mensual_cop": valor_mensual,
            "porcentaje_depreciacion": porcentaje,
            "mantenimiento_anual_cop": mantenimiento_anual
        }

        # Confirm completion again just in case
        st.session_state[completion_flag] = any([
            valor_mensual > 0,
            porcentaje > 0,
            mantenimiento_anual > 0
        ])

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de depreciación guardados correctamente en Google Sheets.")
            st.balloons()
            st.markdown("🎯 ¡Felicidades! Ha completado todas las secciones del formulario.")
            st.markdown("Puede revisar cualquier sección usando el menú lateral o cerrar la aplicación.")

            if "section_index" in st.session_state:
                st.session_state.section_index = 9
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Verifique su conexión o intente nuevamente.")

    # ─────────────────────────────────
    # Review Block
    # ─────────────────────────────────

    with st.expander("🔍 Ver datos guardados"):
        st.write({
            "Valor mensual (COP)": valor_mensual,
            "Porcentaje depreciación (%)": porcentaje,
            "Presupuesto mantenimiento (COP)": mantenimiento_anual
        })
