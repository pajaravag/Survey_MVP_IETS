import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box

# 🔐 Safe conversion helpers
def safe_int(value, default=0):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def render():
    st.header("2. 👩‍🍼 Donantes y Receptores del Banco de Leche Humana (Preguntas 6 a 11)")

    # ──────────────────────────────────────────────
    # Instrucciones Visuales
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
Por favor ingrese los datos relacionados con:
- El número de donantes activas mensuales,
- Los volúmenes de leche recolectada,
- Los receptores mensuales,
- La existencia de procesos de pasteurización,
- El volumen mensual de leche distribuida.

Si algún dato no aplica, registre **0** y continúe.
    """), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**  
- Donantes activas: 120 donantes/mes  
- Volumen recolectado: 100,8 ml (institución), 150 ml (domicilio), 0 ml (centros externos)  
- Receptores activos: 90 receptores/mes  
- Volumen pasteurizado: 6.000 ml  
- Volumen distribuido: 7.500 ml
    """), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Variables de sesión y prefijos
    # ──────────────────────────────────────────────

    prefix = "donantes_receptores__"
    completion_flag = prefix + "completed"
    data = st.session_state

    with st.form("donantes_form"):

        # Pregunta 6️⃣ Donantes activas
        st.subheader("6️⃣ Número promedio de donantes activas por mes:")

        donantes_mes = st.number_input(
            "Número promedio mensual de donantes activas:",
            min_value=0,
            value=safe_int(data.get(prefix + "donantes_mes", 0)),
            help="Ejemplo: 120"
        )

        # Pregunta 7️⃣ Volumen de leche recolectada
        st.subheader("7️⃣ Volumen promedio mensual de leche recolectada (mililitros):")

        col1, col2 = st.columns(2)
        with col1:
            inst_ml = st.number_input(
                "Institución donde se encuentra el BLH (ml):",
                min_value=0.0,
                value=safe_float(data.get(prefix + "vol_inst", 0.0)),
                step=1.0
            )
        with col2:
            dom_ml = st.number_input(
                "Domicilio de la donante (ml):",
                min_value=0.0,
                value=safe_float(data.get(prefix + "vol_dom", 0.0)),
                step=1.0
            )

        centros_ml = st.number_input(
            "Centros externos a la institución (ml):",
            min_value=0.0,
            value=safe_float(data.get(prefix + "vol_centros", 0.0)),
            step=1.0
        )

        total_volumen = inst_ml + dom_ml + centros_ml
        st.info(f"🔢 Volumen total recolectado: **{total_volumen:,.1f} ml**")

        # Pregunta 8️⃣ Receptores activos
        st.subheader("8️⃣ Número promedio de receptores activos por mes:")

        receptores_mes = st.number_input(
            "Número promedio mensual de receptores:",
            min_value=0,
            value=safe_int(data.get(prefix + "receptores_mes", 0)),
            help="Ejemplo: 90"
        )

        # Pregunta 9️⃣ Pasteurización
        st.subheader("9️⃣ Pasteurización de leche humana:")

        pasteuriza = st.radio(
            "¿Se realiza pasteurización en su institución?",
            ["Sí", "No"],
            index=0 if data.get(prefix + "pasteuriza", "No") == "Sí" else 1,
            horizontal=True
        )

        volumen_pasteurizada_ml = 0.0
        if pasteuriza == "Sí":
            volumen_pasteurizada_ml = st.number_input(
                "Volumen promedio mensual de leche pasteurizada (ml):",
                min_value=0.0,
                value=safe_float(data.get(prefix + "volumen_pasteurizada", 0.0)),
                step=10.0,
                help="Ejemplo: 6.000 ml"
            )

        # Pregunta 🔟 Volumen distribuido
        st.subheader("🔟 Volumen promedio mensual de leche distribuida (mililitros):")

        leche_distribuida_ml = st.number_input(
            "Volumen promedio mensual de leche distribuida (ml):",
            min_value=0.0,
            value=safe_float(data.get(prefix + "leche_distribuida", 0.0)),
            step=10.0,
            help="Ejemplo: 7.500 ml"
        )

        # Pregunta 1️⃣1️⃣ (Nueva) Confirmación de volumen distribuido
        st.subheader("1️⃣1️⃣ Confirme el volumen promedio mensual de leche distribuida (mililitros):")

        confirmacion_distribuido_ml = st.number_input(
            "Confirme el volumen promedio mensual de leche distribuida (ml):",
            min_value=0.0,
            value=safe_float(data.get(prefix + "confirmacion_distribuida", leche_distribuida_ml)),
            step=10.0,
            help="Este valor debe coincidir con el volumen efectivamente distribuido. Use 0 si no aplica."
        )

        # ──────────────────────────────────────────────
        # Botón de Guardado con Validación
        # ──────────────────────────────────────────────

        submitted = st.form_submit_button("💾 Guardar sección - Donantes y Receptores")

    if submitted:
        st.session_state[prefix + "donantes_mes"] = donantes_mes
        st.session_state[prefix + "vol_inst"] = inst_ml
        st.session_state[prefix + "vol_dom"] = dom_ml
        st.session_state[prefix + "vol_centros"] = centros_ml
        st.session_state[prefix + "receptores_mes"] = receptores_mes
        st.session_state[prefix + "pasteuriza"] = pasteuriza
        st.session_state[prefix + "volumen_pasteurizada"] = volumen_pasteurizada_ml
        st.session_state[prefix + "leche_distribuida"] = leche_distribuida_ml
        st.session_state[prefix + "confirmacion_distribuida"] = confirmacion_distribuido_ml

        st.session_state[completion_flag] = True

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de Donantes y Receptores guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
