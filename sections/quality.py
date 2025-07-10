import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_data_protection_box, render_compact_example_box

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
    st.header("9. ⚙️ Eficiencia, Calidad y Seguridad del Banco de Leche Humana")

    # ──────────────────────────────────────────────
    # Instrucciones Visuales
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
**¿Qué información debe registrar?**  
Esta sección busca evaluar la **eficiencia, calidad y seguridad** en el funcionamiento del Banco de Leche Humana (BLH).  
Por favor diligencie los siguientes indicadores:

- Volumen promedio de **leche descartada**.
- Tiempo promedio desde la **recolección hasta la distribución**.
- Si se realizan **controles microbiológicos post-pasteurización**.

Recuerde que estos datos ayudan a identificar oportunidades de mejora en los procesos del BLH.
    """), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**  
- Leche descartada: *200 mL/mes*  
- Tiempo promedio de distribución: *2 días*  
- Control microbiológico: *Sí, con 5 pruebas mensuales*
    """), unsafe_allow_html=True)

    st.markdown(render_data_protection_box("""
🔐 **Nota legal:**  
Los datos están protegidos por la **Ley 1581 de 2012 (Habeas Data)** y serán utilizados exclusivamente para los fines autorizados del estudio de BLH.
    """), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Variables y Datos Previos
    # ──────────────────────────────────────────────

    prefix = "calidad_seguridad__"
    completion_flag = prefix + "completed"
    prev_data = st.session_state.get(prefix + "data", {})

    # ──────────────────────────────────────────────
    # Inputs de Calidad y Seguridad
    # ──────────────────────────────────────────────

    leche_descartada_ml = st.number_input(
        "🍼 Volumen promedio de leche descartada (mL/mes)",
        min_value=0.0, step=10.0,
        value=safe_float(prev_data.get("leche_descartada_ml", 0.0)),
        key=prefix + "leche_descartada"
    )

    tiempo_distribucion_dias = st.number_input(
        "⏱️ Tiempo promedio desde recolección hasta distribución (días)",
        min_value=0.0, step=0.1,
        value=safe_float(prev_data.get("tiempo_promedio_dias", 0.0)),
        key=prefix + "tiempo_distribucion"
    )

    control_micro = st.radio(
        "🧪 ¿Se realiza control microbiológico post-pasteurización?",
        options=["Sí", "No", "No aplica"],
        index=["Sí", "No", "No aplica"].index(prev_data.get("control_microbiologico_post", "Sí")),
        horizontal=True,
        key=prefix + "control_micro"
    )

    n_pruebas_micro = 0
    if control_micro == "Sí":
        n_pruebas_micro = st.number_input(
            "🔬 Número promedio de pruebas microbiológicas realizadas por mes",
            min_value=0, step=1,
            value=safe_int(prev_data.get("n_pruebas_micro", 0)),
            key=prefix + "n_pruebas"
        )

    # ──────────────────────────────────────────────
    # Validación de Completitud
    # ──────────────────────────────────────────────

    is_complete = (
        leche_descartada_ml >= 0 and
        tiempo_distribucion_dias >= 0 and
        control_micro in ["Sí", "No", "No aplica"]
    )

    st.session_state[completion_flag] = is_complete

    # ──────────────────────────────────────────────
    # Botón de Guardado con Feedback
    # ──────────────────────────────────────────────

    if st.button("💾 Guardar sección - Eficiencia, Calidad y Seguridad"):
        st.session_state[prefix + "data"] = {
            "leche_descartada_ml": leche_descartada_ml,
            "tiempo_promedio_dias": tiempo_distribucion_dias,
            "control_microbiologico_post": control_micro,
            "n_pruebas_micro": n_pruebas_micro
        }

        st.session_state[completion_flag] = is_complete

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de eficiencia, calidad y seguridad guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")

    # ──────────────────────────────────────────────
    # Visualización de Datos Guardados
    # ──────────────────────────────────────────────

    # with st.expander("🔍 Ver resumen de datos guardados"):
    #     st.write({
    #         "Volumen leche descartada (mL/mes)": leche_descartada_ml,
    #         "Tiempo promedio recolección → distribución (días)": tiempo_distribucion_dias,
    #         "Control microbiológico post-pasteurización": control_micro,
    #         "Número de pruebas microbiológicas/mes": n_pruebas_micro
    #     })
