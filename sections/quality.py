import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row

# 🔐 Safe conversion helper
def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def render():
    st.header("9. Eficiencia, Calidad y Seguridad")

    st.markdown("""
    ### 🛡️ Instrucciones:
    Por favor registre la información relacionada con la **eficiencia, seguridad y calidad** del Banco de Leche Humana (BLH):

    - Volumen promedio de leche **descartada** (litros por mes).
    - Tiempo promedio desde la **recolección hasta la distribución** (días).
    - Si se realiza **control microbiológico post-pasteurización**.

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

    leche_descartada = st.number_input(
        "Volumen promedio de leche descartada (litros/mes)",
        min_value=0.0, step=0.1,
        value=safe_float(prev_data.get("leche_descartada_litros", 0.0)),
        key=prefix + "leche_descartada"
    )

    tiempo_distribucion = st.number_input(
        "Tiempo promedio desde recolección hasta distribución (días)",
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

    # ─────────────────────────────────
    # Automatic Completion Check (✅)
    # ─────────────────────────────────

    st.session_state[completion_flag] = (
        leche_descartada > 0 or
        tiempo_distribucion > 0 or
        control_micro in ["Sí", "No"]
    )

    # ─────────────────────────────────
    # Save Button
    # ─────────────────────────────────

    if st.button("💾 Guardar sección - Eficiencia, Calidad y Seguridad"):
        st.session_state[prefix + "data"] = {
            "leche_descartada_litros": leche_descartada,
            "tiempo_promedio_dias": tiempo_distribucion,
            "control_microbiologico_post": control_micro
        }

        # Re-confirm completion
        st.session_state[completion_flag] = (
            leche_descartada > 0 or
            tiempo_distribucion > 0 or
            control_micro in ["Sí", "No"]
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
            "Leche descartada (L/mes)": leche_descartada,
            "Tiempo promedio (días)": tiempo_distribucion,
            "Control microbiológico": control_micro
        })
