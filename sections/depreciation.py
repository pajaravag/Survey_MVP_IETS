import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row

def render():
    st.header("10. Depreciación e Impuestos")
    st.markdown("Ingrese los valores relacionados con la depreciación de equipos y presupuesto de mantenimiento del BLH.")

    prev_data = st.session_state.get("depreciacion", {})

    valor_mensual = st.number_input(
        "¿Cuánto es el rubro mensual asociado a la depreciación de los equipos del BLH? ($ COP)",
        min_value=0.0, step=10000.0,
        value=prev_data.get("valor_mensual_cop", 0.0),
        key="depreciacion_mensual"
    )

    porcentaje = st.slider(
        "¿Cuál es el porcentaje de depreciación promedio de los equipos del BLH?",
        min_value=0, max_value=100,
        value=prev_data.get("porcentaje_depreciacion", 20),
        step=1,
        key="depreciacion_pct"
    )

    mantenimiento_anual = st.number_input(
        "¿Cuánto dinero dispone para el mantenimiento anual de los equipos del BLH? ($ COP)",
        min_value=0.0, step=10000.0,
        value=prev_data.get("mantenimiento_anual_cop", 0.0),
        key="mantenimiento_anual"
    )

    if st.button("💾 Guardar sección y finalizar"):
        st.session_state["depreciacion"] = {
            "valor_mensual_cop": valor_mensual,
            "porcentaje_depreciacion": porcentaje,
            "mantenimiento_anual_cop": mantenimiento_anual
        }

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de depreciación registrados y guardados correctamente en Google Sheets.")
            st.balloons()  # 🎈 Optional celebratory touch
            if "section_index" in st.session_state:
                st.session_state.section_index = 9  # Stay on this section or show summary
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos.")
