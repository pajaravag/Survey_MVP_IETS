import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_data_protection_box, render_compact_example_box

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
    st.header("3. 👩‍🍼 Donantes y Receptores")

    # ──────────────────────────────────────────────
    # Cuadros de Instrucción Visual
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
**¿Qué información debe registrar aquí?**  
En esta sección se recopila información sobre:
- Número promedio de **donantes activas** por mes.
- Volumen promedio de **leche recolectada**.
- Porcentaje de **origen** de la leche.
- Información sobre **pasteurización**, receptores y distribución.
    """), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**  
- Donantes activas: *12 donantes/mes*  
- Volumen recolectado: *8,500 ml/mes*  
- Porcentaje origen: *Institución 40%*, *Domicilio 50%*, *Centros 10%*
    """), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
➕ **Si un dato no aplica:**  
Registre **0** o seleccione **No aplica**.
    """), unsafe_allow_html=True)

    st.markdown(render_data_protection_box("""
🔐 **Nota legal:**  
Los datos recopilados están protegidos por la **Ley 1581 de 2012 (Habeas Data)** y se usarán exclusivamente para los fines autorizados por el **IETS**.
    """), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Prefijos y Estados Previos
    # ──────────────────────────────────────────────

    prefix = "donantes_receptores__"
    completion_flag = prefix + "completed"
    data = st.session_state

    with st.form("donantes_form"):

        # ──────────────────────────────────────────────
        # Donantes y Volumen Recolectado
        # ──────────────────────────────────────────────

        donantes_mes = st.number_input(
            "👥 Número promedio de donantes activas por mes",
            min_value=0,
            value=safe_int(data.get(prefix + "donantes_mes", 0)),
            help="Ejemplo: 12"
        )
        st.caption("_Ejemplo: 12 donantes activas por mes._")

        volumen_mes_ml = st.number_input(
            "🍼 Volumen promedio de leche recolectada por mes (ml)",
            min_value=0.0,
            value=safe_float(data.get(prefix + "volumen_mes", 0.0)),
            step=10.0,
            help="Ejemplo: 8,500 ml"
        )
        st.caption("_Ejemplo: 8,500 ml recolectados mensualmente._")

        # ──────────────────────────────────────────────
        # Porcentaje de Origen de la Leche
        # ──────────────────────────────────────────────

        st.markdown("### 📊 Porcentaje de origen de la leche recolectada *(la suma debe ser 100%)*")

        pct_inst = st.slider("🏥 Recolectada en la institución (%)", 0, 100, value=safe_int(data.get(prefix + "pct_inst", 0)))
        pct_dom = st.slider("🏠 Recolectada en domicilio de la donante (%)", 0, 100, value=safe_int(data.get(prefix + "pct_dom", 0)))
        pct_centros = st.slider("🏬 Recolectada en centros externos (%)", 0, 100, value=safe_int(data.get(prefix + "pct_centros", 0)))

        total_pct = pct_inst + pct_dom + pct_centros
        st.info(f"🔢 **Total actual:** {total_pct}% (debe ser exactamente 100%)")

        # ──────────────────────────────────────────────
        # Pasteurización Condicional
        # ──────────────────────────────────────────────

        pasteuriza = st.radio(
            "🧪 ¿Se realiza pasteurización de la leche en su institución?",
            ["Sí", "No"],
            index=0 if data.get(prefix + "pasteuriza", "No") == "Sí" else 1,
            horizontal=True
        )

        volumen_pasteurizada_ml = 0.0
        if pasteuriza == "Sí":
            volumen_pasteurizada_ml = st.number_input(
                "Volumen promedio de leche pasteurizada por mes (ml)",
                min_value=0.0,
                value=safe_float(data.get(prefix + "volumen_pasteurizada", 0.0)),
                step=10.0,
                help="Ejemplo: 6,000 ml"
            )
            st.caption("_Ejemplo: 6,000 ml pasteurizados mensualmente._")

        # ──────────────────────────────────────────────
        # Receptores y Volumen Distribuido
        # ──────────────────────────────────────────────

        receptores_mes = st.number_input(
            "👶 Número promedio de receptores activos por mes",
            min_value=0,
            value=safe_int(data.get(prefix + "receptores_mes", 0)),
            help="Ejemplo: 8 receptores"
        )
        st.caption("_Ejemplo: 8 receptores mensuales._")

        leche_distribuida_ml = st.number_input(
            "🚚 Volumen promedio de leche distribuida por mes (ml)",
            min_value=0.0,
            value=safe_float(data.get(prefix + "leche_distribuida", 0.0)),
            step=10.0,
            help="Ejemplo: 7,500 ml"
        )
        st.caption("_Ejemplo: 7,500 ml distribuidos mensualmente._")

        # ──────────────────────────────────────────────
        # Botón de Guardado
        # ──────────────────────────────────────────────

        submitted = st.form_submit_button("💾 Guardar sección - Donantes y Receptores")

    # ──────────────────────────────────────────────
    # Validación y Guardado
    # ──────────────────────────────────────────────

    if submitted:
        errors = []
        if total_pct != 100:
            errors.append(f"La suma de los porcentajes debe ser 100% (actual: {total_pct}%).")

        if errors:
            for e in errors:
                st.warning(f"⚠️ {e}")
        else:
            st.session_state[prefix + "donantes_mes"] = donantes_mes
            st.session_state[prefix + "volumen_mes"] = volumen_mes_ml
            st.session_state[prefix + "pct_inst"] = pct_inst
            st.session_state[prefix + "pct_dom"] = pct_dom
            st.session_state[prefix + "pct_centros"] = pct_centros
            st.session_state[prefix + "pasteuriza"] = pasteuriza
            st.session_state[prefix + "volumen_pasteurizada"] = volumen_pasteurizada_ml
            st.session_state[prefix + "receptores_mes"] = receptores_mes
            st.session_state[prefix + "leche_distribuida"] = leche_distribuida_ml

            st.session_state[completion_flag] = True

            flat_data = flatten_session_state(st.session_state)
            success = append_or_update_row(flat_data)

            if success:
                st.success("✅ Datos de donantes y receptores guardados exitosamente.")
                if "section_index" in st.session_state and st.session_state.section_index < 9:
                    st.session_state.section_index += 1
                    st.session_state.navigation_triggered = True
                    st.rerun()
            else:
                st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")

    # ──────────────────────────────────────────────
    # Resumen de Datos Guardados
    # ──────────────────────────────────────────────

    # with st.expander("🔍 Ver resumen de datos guardados"):
    #     st.write({
    #         "Donantes activas/mes": safe_int(data.get(prefix + "donantes_mes", 0)),
    #         "Volumen recolectado (ml)": safe_float(data.get(prefix + "volumen_mes", 0.0)),
    #         "% En institución": safe_int(data.get(prefix + "pct_inst", 0)),
    #         "% En domicilio": safe_int(data.get(prefix + "pct_dom", 0)),
    #         "% En centros": safe_int(data.get(prefix + "pct_centros", 0)),
    #         "¿Realiza pasteurización?": data.get(prefix + "pasteuriza", "No"),
    #         "Volumen pasteurizada (ml)": safe_float(data.get(prefix + "volumen_pasteurizada", 0.0)),
    #         "Receptores activos/mes": safe_int(data.get(prefix + "receptores_mes", 0)),
    #         "Volumen distribuido (ml)": safe_float(data.get(prefix + "leche_distribuida", 0.0)),
    #         "Total % Origen": total_pct
    #     })
