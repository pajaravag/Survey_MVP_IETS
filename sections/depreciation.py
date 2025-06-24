import streamlit as st

def render():
    st.header("10. Depreciación e Impuestos")

    st.markdown("Ingrese los valores relacionados con la depreciación de equipos y presupuesto de mantenimiento del BLH.")

    valor_mensual = st.number_input(
        "¿Cuánto es el rubro mensual asociado a la depreciación de los equipos del BLH? ($ COP)",
        min_value=0.0, step=10000.0, key="depreciacion_mensual"
    )

    porcentaje = st.slider(
        "¿Cuál es el porcentaje de depreciación promedio de los equipos del BLH?",
        min_value=0, max_value=100, value=20, step=1, key="depreciacion_pct"
    )

    mantenimiento_anual = st.number_input(
        "¿Cuánto dinero dispone para el mantenimiento anual de los equipos del BLH? ($ COP)",
        min_value=0.0, step=10000.0, key="mantenimiento_anual"
    )

    if st.button("Guardar sección - Depreciación e Impuestos"):
        st.session_state["depreciacion"] = {
            "valor_mensual_cop": valor_mensual,
            "porcentaje_depreciacion": porcentaje,
            "mantenimiento_anual_cop": mantenimiento_anual
        }
        st.success("✅ Datos de depreciación registrados correctamente.")
