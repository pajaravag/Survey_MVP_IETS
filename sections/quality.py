import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row

# 🔐 Safe conversion helper
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
    st.header("9. Eficiencia, Calidad y Seguridad")

    st.markdown("""
    ### 🛡️ Instrucciones:
    Por favor registre la información relacionada con la **eficiencia, seguridad y calidad** del Banco de Leche Humana (BLH):

    - Volumen promedio de leche **descartada** (**ml/mes**).
    - Tiempo promedio desde la **recolección hasta la distribución** (**días**).
    - Si se realiza **control microbiológico post-pasteurización**.
    - Número promedio de **pruebas microbiológicas** realizadas por mes.

    Si algún valor no aplica, registre **0** o seleccione **No aplica**.
    """)

    # ─────────────────────────────────
    # Keys & Prior Data
    # ─────────────────────────────────

    prefix = "calidad_seguridad__"
    completion_flag = prefix + "completed"
    prev_data = st.session_state.get(prefix + "data", {})

    # ─────────────────────────────────
    # Input Fields
    # ─────────────────────────────────

    leche_descartada_ml = st.number_input(
        "Volumen promedio de leche descartada (ml/mes)",
        min_value=0.0, step=10.0,
        value=safe_float(prev_data.get("leche_descartada_ml", 0.0)),
        key=prefix + "leche_descartada"
    )

    tiempo_distribucion_dias = st.number_input(
        "Tiempo promedio desde la recolección hasta la distribución (días)",
        min_value=0.0, step=0.1,
        value=safe_float(prev_data.get("tiempo_promedio_dias", 0.0)),
        key=prefix + "tiempo_distribucion"
    )

    control_micro = st.radio(
        "¿Se realiza control microbiológico post-pasteurización?",
        options=["Sí", "No", "No aplica"],
        index=["Sí", "No", "No aplica"].index(prev_data.get("control_microbiologico_post", "Sí")),
        horizontal=True,
        key=prefix + "control_micro"
    )

    n_pruebas_micro = st.number_input(
        "Número promedio de pruebas microbiológicas realizadas por mes",
        min_value=0, step=1,
        value=safe_int(prev_data.get("n_pruebas_micro", 0)),
        key=prefix + "n_pruebas"
    )

    # ─────────────────────────────────
    # Automatic Completion Check (✅)
    # ─────────────────────────────────

    st.session_state[completion_flag] = (
        leche_descartada_ml > 0 or
        tiempo_distribucion_dias > 0 or
        control_micro in ["Sí", "No"] or
        n_pruebas_micro > 0
    )

    # ─────────────────────────────────
    # Save Button
    # ─────────────────────────────────

    if st.button("💾 Guardar sección - Eficiencia, Calidad y Seguridad"):
        st.session_state[prefix + "data"] = {
            "leche_descartada_ml": leche_descartada_ml,
            "tiempo_promedio_dias": tiempo_distribucion_dias,
            "control_microbiologico_post": control_micro,
            "n_pruebas_micro": n_pruebas_micro
        }

        # Confirm completion
        st.session_state[completion_flag] = (
            leche_descartada_ml > 0 or
            tiempo_distribucion_dias > 0 or
            control_micro in ["Sí", "No"] or
            n_pruebas_micro > 0
        )

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Sección de calidad y seguridad guardada correctamente en Google Sheets.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Verifique su conexión e intente nuevamente.")

    # ─────────────────────────────────
    # Review Data
    # ─────────────────────────────────

    with st.expander("🔍 Ver datos guardados en esta sección"):
        st.write({
            "Leche descartada (ml/mes)": leche_descartada_ml,
            "Tiempo promedio (días)": tiempo_distribucion_dias,
            "Control microbiológico": control_micro,
            "Pruebas microbiológicas/mes": n_pruebas_micro
        })
