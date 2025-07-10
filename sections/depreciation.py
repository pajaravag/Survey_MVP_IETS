import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_data_protection_box

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
    st.header("10. 💰 Depreciación e Impuestos del BLH")

    # ──────────────────────────────────────────────
    # Ayudas Visuales e Instructivas
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
    > ℹ️ **¿Qué se debe registrar en esta sección?**  
    Aquí se recopila información sobre el **valor de depreciación mensual**, el **porcentaje de depreciación** y el **presupuesto anual de mantenimiento** de los equipos e infraestructura del Banco de Leche Humana (BLH).

    📝 **Ejemplos:**  
    - Depreciación mensual: $50.000 COP  
    - Porcentaje anual de depreciación: 20%  
    - Mantenimiento anual: $300.000 COP  

    Si algún dato no aplica, por favor registre **0**.
    """), unsafe_allow_html=True)

    st.markdown(render_data_protection_box("""
    > 🔒 **Nota:** La información ingresada está protegida conforme a la **Ley 1581 de 2012 (Habeas Data)** y será usada exclusivamente para el estudio.
    """), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Claves & Valores Previos
    # ──────────────────────────────────────────────

    prefix = "depreciacion__"
    completion_flag = prefix + "completed"
    prev_data = st.session_state.get(prefix + "data", {})

    # ──────────────────────────────────────────────
    # Campos de Entrada
    # ──────────────────────────────────────────────

    valor_mensual = st.number_input(
        "💸 Valor mensual asociado a la depreciación ($ COP/mes)",
        min_value=0.0, step=10000.0,
        value=safe_float(prev_data.get("valor_mensual_cop", 0.0)),
        key=prefix + "valor_mensual"
    )

    porcentaje = st.slider(
        "📊 Porcentaje promedio anual de depreciación (%)",
        min_value=0, max_value=100, step=1,
        value=safe_int(prev_data.get("porcentaje_depreciacion", 20)),
        key=prefix + "porcentaje"
    )

    mantenimiento_anual = st.number_input(
        "🔧 Presupuesto anual estimado de mantenimiento ($ COP/año)",
        min_value=0.0, step=10000.0,
        value=safe_float(prev_data.get("mantenimiento_anual_cop", 0.0)),
        key=prefix + "mantenimiento"
    )

    # ──────────────────────────────────────────────
    # Validación Automática de Completitud
    # ──────────────────────────────────────────────

    is_complete = any([
        valor_mensual > 0,
        porcentaje > 0,
        mantenimiento_anual > 0
    ])
    st.session_state[completion_flag] = is_complete

    # ──────────────────────────────────────────────
    # Botón Guardar + Éxito/Error Visual
    # ──────────────────────────────────────────────

    if st.button("💾 Guardar sección - Depreciación e Impuestos"):
        st.session_state[prefix + "data"] = {
            "valor_mensual_cop": valor_mensual,
            "porcentaje_depreciacion": porcentaje,
            "mantenimiento_anual_cop": mantenimiento_anual
        }

        st.session_state[completion_flag] = is_complete

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de depreciación y mantenimiento guardados exitosamente.")
            st.balloons()
            st.markdown("🎯 ¡Felicitaciones! Ha completado todas las secciones del formulario.")
            if "section_index" in st.session_state:
                st.session_state.section_index = 9
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor verifique la conexión o intente nuevamente.")

    # ──────────────────────────────────────────────
    # Visualización de Datos Guardados
    # ──────────────────────────────────────────────

    with st.expander("🔍 Ver resumen de datos guardados"):
        st.write({
            "Valor mensual depreciación (COP)": valor_mensual,
            "Porcentaje anual de depreciación (%)": porcentaje,
            "Presupuesto mantenimiento anual (COP)": mantenimiento_anual
        })
