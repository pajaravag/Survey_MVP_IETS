import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row

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
    st.header("3. Donantes y Receptores")

    st.markdown("""
    > ℹ️ **Instrucciones:**  
    Registre la información sobre donantes, volumen recolectado y receptores.  
    Si algún dato no aplica a su institución, por favor registre **0**.

    > 🔐 **Nota:** La información está protegida por el derecho fundamental de **Habeas Data** (Ley 1581 de 2012).
    """)

    prefix = "donantes_receptores__"
    completion_flag = prefix + "completed"
    data = st.session_state

    with st.form("donantes_form"):

        # ──────────────────────────────────────────────
        # Donantes activas y volumen recolectado
        # ──────────────────────────────────────────────

        donantes_mes = st.number_input(
            "👥 Número promedio de donantes activas por mes",
            min_value=0,
            value=safe_int(data.get(prefix + "donantes_mes", 0))
        )

        volumen_mes_ml = st.number_input(
            "🍼 Volumen promedio de leche recolectada por mes (ml)",
            min_value=0.0,
            value=safe_float(data.get(prefix + "volumen_mes", 0.0)),
            step=10.0
        )

        # ──────────────────────────────────────────────
        # Porcentaje de origen de la leche
        # ──────────────────────────────────────────────

        st.markdown("### 📊 Porcentaje de origen de la leche recolectada *(la suma debe ser 100%)*")

        pct_inst = st.slider("🏥 Recolectada en la institución (%)", 0, 100, value=safe_int(data.get(prefix + "pct_inst", 0)))
        pct_dom = st.slider("🏠 Recolectada en domicilio de la donante (%)", 0, 100, value=safe_int(data.get(prefix + "pct_dom", 0)))
        pct_centros = st.slider("🏬 Recolectada en centros de recolección externos (%)", 0, 100, value=safe_int(data.get(prefix + "pct_centros", 0)))

        total_pct = pct_inst + pct_dom + pct_centros
        st.info(f"🔢 **Total actual:** {total_pct} % (debe ser 100%)")

        # ──────────────────────────────────────────────
        # Pasteurización (condicional)
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
                step=10.0
            )

        # ──────────────────────────────────────────────
        # Receptores y volumen distribuido
        # ──────────────────────────────────────────────

        receptores_mes = st.number_input(
            "👶 Número promedio de receptores activos por mes",
            min_value=0,
            value=safe_int(data.get(prefix + "receptores_mes", 0))
        )

        leche_distribuida_ml = st.number_input(
            "🚚 Volumen promedio de leche distribuida por mes (ml)",
            min_value=0.0,
            value=safe_float(data.get(prefix + "leche_distribuida", 0.0)),
            step=10.0
        )

        # ──────────────────────────────────────────────
        # Submit Button
        # ──────────────────────────────────────────────

        submitted = st.form_submit_button("💾 Guardar sección - Donantes y Receptores")

    # ──────────────────────────────────────────────
    # Validación y guardado
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
                    st.rerun()
            else:
                st.error("❌ Error al guardar los datos. Intente nuevamente.")

    # ──────────────────────────────────────────────
    # Expander para datos guardados
    # ──────────────────────────────────────────────

    with st.expander("🔍 Ver datos guardados en esta sección"):
        st.write({
            "Donantes activas/mes": safe_int(data.get(prefix + "donantes_mes", 0)),
            "Volumen recolectado (ml)": safe_float(data.get(prefix + "volumen_mes", 0.0)),
            "% En institución": safe_int(data.get(prefix + "pct_inst", 0)),
            "% En domicilio": safe_int(data.get(prefix + "pct_dom", 0)),
            "% En centros": safe_int(data.get(prefix + "pct_centros", 0)),
            "¿Realiza pasteurización?": data.get(prefix + "pasteuriza", "No"),
            "Volumen pasteurizada (ml)": safe_float(data.get(prefix + "volumen_pasteurizada", 0.0)),
            "Receptores activos/mes": safe_int(data.get(prefix + "receptores_mes", 0)),
            "Volumen distribuido (ml)": safe_float(data.get(prefix + "leche_distribuida", 0.0)),
            "Total % Origen": total_pct
        })
