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
    st.header("3. 👩‍🍼 Donantes y Receptores del Banco de Leche Humana (Preguntas 5 a 10)")

    # ──────────────────────────────────────────────
    # Introducción oficial alineada al instructivo
    # ──────────────────────────────────────────────
    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
En esta sección se solicitará información cuantitativa relacionada con los donantes y receptores de leche humana.  
En caso de que algún ítem no aplique a su institución, deberá registrar el valor **cero (0)** y continuar con el llenado del formulario.
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
    # Prefijo y estado
    # ──────────────────────────────────────────────
    prefix = "donantes_receptores__"
    completion_flag = prefix + "completed"
    data = st.session_state

    # ──────────────────────────────────────────────
    # Pregunta 8️⃣ Pasteurización (fuera del form)
    # ──────────────────────────────────────────────
    st.subheader("8️⃣ ¿En su institución se realiza pasteurización de la leche humana?")
    pasteuriza = st.radio(
        "Por favor confirme si este proceso se lleva a cabo:",
        ["Sí", "No"],
        index=0 if data.get(prefix + "pasteuriza", "No") == "Sí" else 1,
        horizontal=True,
        key=prefix + "pasteuriza_radio"
    )
    st.session_state[prefix + "pasteuriza"] = pasteuriza

    # ──────────────────────────────────────────────
    # Formulario de ingreso de datos cuantitativos
    # ──────────────────────────────────────────────
    with st.form("donantes_form"):

        # Pregunta 5️⃣ Donantes activas
        st.subheader("5️⃣ Número promedio de donantes activas por mes:")
        donantes_mes = st.number_input(
            "Número promedio mensual de donantes activas:",
            min_value=0,
            value=safe_int(data.get(prefix + "donantes_mes", 0)),
            help="Ejemplo: 120"
        )

        # Pregunta 6️⃣ Volumen de leche recolectada
        st.subheader("6️⃣ Volumen promedio mensual de leche recolectada (mililitros):")
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

        # Pregunta 7️⃣ Receptores activos
        st.subheader("7️⃣ Número promedio de receptores activos por mes:")
        receptores_mes = st.number_input(
            "Número promedio mensual de receptores:",
            min_value=0,
            value=safe_int(data.get(prefix + "receptores_mes", 0)),
            help="Ejemplo: 90"
        )

        # Pregunta 9️⃣ Condicional - Volumen pasteurizado
        volumen_pasteurizada_ml = 0.0
        if pasteuriza == "Sí":
            st.subheader("9️⃣ Volumen promedio mensual de leche pasteurizada (ml):")
            volumen_pasteurizada_ml = st.number_input(
                "Ingrese el volumen mensual de leche pasteurizada:",
                min_value=0.0,
                value=safe_float(data.get(prefix + "volumen_pasteurizada", 0.0)),
                step=10.0,
                help="Ejemplo: 6.000 ml"
            )
        else:
            st.info("🧪 Su institución indicó que **no realiza pasteurización**, por lo tanto no debe completar esta pregunta.")

        # Pregunta 🔟 Volumen distribuido
        st.subheader("🔟 Volumen promedio mensual de leche distribuida (mililitros):")
        leche_distribuida_ml = st.number_input(
            "Volumen promedio mensual de leche distribuida (ml):",
            min_value=0.0,
            value=safe_float(data.get(prefix + "leche_distribuida", 0.0)),
            step=10.0,
            help="Ejemplo: 7.500 ml"
        )

        # Botón de guardado
        submitted = st.form_submit_button("💾 Guardar sección - Donantes y Receptores")

    # ──────────────────────────────────────────────
    # Procesamiento y guardado
    # ──────────────────────────────────────────────
    if submitted:
        st.session_state[prefix + "donantes_mes"] = donantes_mes
        st.session_state[prefix + "vol_inst"] = inst_ml
        st.session_state[prefix + "vol_dom"] = dom_ml
        st.session_state[prefix + "vol_centros"] = centros_ml
        st.session_state[prefix + "receptores_mes"] = receptores_mes
        st.session_state[prefix + "volumen_pasteurizada"] = volumen_pasteurizada_ml
        st.session_state[prefix + "leche_distribuida"] = leche_distribuida_ml
        st.session_state[completion_flag] = any([
            donantes_mes > 0,
            total_volumen > 0,
            receptores_mes > 0,
            volumen_pasteurizada_ml > 0,
            leche_distribuida_ml > 0
        ])

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de Donantes y Receptores guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 10:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
