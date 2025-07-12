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
    st.header("11. ⚙️ Calidad, Seguridad y Eficiencia del Banco de Leche Humana (Preguntas 26 a 29)")

    # ──────────────────────────────────────────────
    # Instrucciones Visuales
    # ──────────────────────────────────────────────
    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
Esta sección busca evaluar la **calidad, seguridad y eficiencia** de su Banco de Leche Humana (BLH).  
Por favor registre:

- Volumen de leche descartada (ml/mes)  
- Tiempo promedio desde la recolección hasta la distribución (días)  
- Si se realizan controles microbiológicos post-pasteurización  
- Número promedio de pruebas microbiológicas mensuales

Estos datos permiten identificar oportunidades de mejora en la operación del BLH.
"""), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**  
- Leche descartada: 200 ml/mes  
- Tiempo promedio de distribución: 2 días  
- Control microbiológico post-pasteurización: Sí  
- Número de pruebas mensuales: 5
"""), unsafe_allow_html=True)

    st.markdown(render_data_protection_box("""
🔐 **Nota legal:**  
Los datos están protegidos por la **Ley 1581 de 2012 (Habeas Data)** y serán utilizados exclusivamente para los fines autorizados del estudio de BLH.
"""), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Estado y recuperación
    # ──────────────────────────────────────────────
    prefix = "calidad_seguridad__"
    completion_flag = prefix + "completed"
    prev_data = st.session_state.get(prefix + "data", {})

    # ──────────────────────────────────────────────
    # Pregunta 2️⃣6️⃣ Leche descartada
    # ──────────────────────────────────────────────
    leche_descartada_ml = st.number_input(
        "2️⃣6️⃣ 🍼 Volumen promedio mensual de leche descartada (mililitros):",
        min_value=0.0,
        step=10.0,
        value=safe_float(prev_data.get("leche_descartada_ml", 0.0)),
        key=f"{prefix}leche_descartada"
    )

    # ──────────────────────────────────────────────
    # Pregunta 2️⃣7️⃣ Tiempo promedio
    # ──────────────────────────────────────────────
    tiempo_distribucion_dias = st.number_input(
        "2️⃣7️⃣ ⏱️ Tiempo promedio entre recolección y distribución (días):",
        min_value=0.0,
        step=0.1,
        value=safe_float(prev_data.get("tiempo_promedio_dias", 0.0)),
        key=f"{prefix}tiempo_distribucion"
    )

    # ──────────────────────────────────────────────
    # Pregunta 2️⃣8️⃣ Control microbiológico
    # ──────────────────────────────────────────────
    control_micro = st.radio(
        "2️⃣8️⃣ 🧪 ¿Se realiza control microbiológico post-pasteurización?",
        options=["Sí", "No", "No aplica"],
        index=["Sí", "No", "No aplica"].index(prev_data.get("control_microbiologico_post", "No")),
        horizontal=True,
        key=f"{prefix}control_micro"
    )

    # ──────────────────────────────────────────────
    # Pregunta 2️⃣9️⃣ Número de pruebas
    # ──────────────────────────────────────────────
    n_pruebas_micro = 0
    if control_micro == "Sí":
        n_pruebas_micro = st.number_input(
            "2️⃣9️⃣ 🔬 Número promedio mensual de pruebas microbiológicas realizadas:",
            min_value=0,
            step=1,
            value=safe_int(prev_data.get("n_pruebas_micro", 0)),
            key=f"{prefix}n_pruebas"
        )

    # ──────────────────────────────────────────────
    # Validación y Guardado
    # ──────────────────────────────────────────────
    is_complete = (
        leche_descartada_ml >= 0 and
        tiempo_distribucion_dias >= 0 and
        control_micro in ["Sí", "No", "No aplica"]
    )
    st.session_state[completion_flag] = is_complete

    if st.button("💾 Guardar sección - Calidad, Seguridad y Eficiencia"):
        st.session_state[prefix + "data"] = {
            "leche_descartada_ml": leche_descartada_ml,
            "tiempo_promedio_dias": tiempo_distribucion_dias,
            "control_microbiologico_post": control_micro,
            "n_pruebas_micro": n_pruebas_micro if control_micro == "Sí" else "NA"
        }

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de calidad, seguridad y eficiencia guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 10:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
