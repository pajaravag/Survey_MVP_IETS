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
    ### 🍼 Instrucciones:
    En esta sección, por favor registre información sobre:
    
    - El número promedio de donantes activas y el volumen mensual de leche recolectada.
    - El origen de la leche recolectada (debe sumar 100%).
    - El número de receptores y el volumen promedio de leche distribuida por mes.
    """)

    prefix = "donantes_receptores__"
    completion_flag = "donantes_receptores__completed"
    data = st.session_state

    with st.form("donantes_form"):
        donantes_mes = st.number_input(
            "Número promedio de donantes activas por mes", 
            min_value=0, 
            value=safe_int(data.get(prefix + "donantes_mes", 0))
        )

        volumen_mes = st.number_input(
            "Volumen promedio de leche recolectada por mes (litros)", 
            min_value=0.0, 
            value=safe_float(data.get(prefix + "volumen_mes", 0.0))
        )

        st.markdown("### Porcentaje de origen de la leche recolectada *(Debe sumar 100%)*")
        pct_inst = st.slider("Recolectada en institución (%)", 0, 100, value=safe_int(data.get(prefix + "pct_inst", 0)))
        pct_dom = st.slider("Recolectada en domicilio de la donante (%)", 0, 100, value=safe_int(data.get(prefix + "pct_dom", 0)))
        pct_centros = st.slider("Recolectada en centros de recolección (%)", 0, 100, value=safe_int(data.get(prefix + "pct_centros", 0)))

        receptores_mes = st.number_input(
            "Número promedio de receptores activos por mes", 
            min_value=0, 
            value=safe_int(data.get(prefix + "receptores_mes", 0))
        )

        leche_distribuida = st.number_input(
            "Volumen promedio de leche distribuida por mes (litros)", 
            min_value=0.0, 
            value=safe_float(data.get(prefix + "leche_distribuida", 0.0))
        )

        submitted = st.form_submit_button("💾 Guardar sección - Donantes y Receptores")

    if submitted:
        total_pct = pct_inst + pct_dom + pct_centros
        if total_pct != 100:
            st.warning(f"⚠️ La suma de los porcentajes debe ser 100% (actual: {total_pct}%).")
        else:
            st.session_state[prefix + "donantes_mes"] = donantes_mes
            st.session_state[prefix + "volumen_mes"] = volumen_mes
            st.session_state[prefix + "pct_inst"] = pct_inst
            st.session_state[prefix + "pct_dom"] = pct_dom
            st.session_state[prefix + "pct_centros"] = pct_centros
            st.session_state[prefix + "receptores_mes"] = receptores_mes
            st.session_state[prefix + "leche_distribuida"] = leche_distribuida

            # ✅ Set completion flag
            st.session_state[completion_flag] = True

            flat_data = flatten_session_state(st.session_state)
            success = append_or_update_row(flat_data)

            if success:
                st.success("✅ Datos de donantes y receptores guardados correctamente en Google Sheets.")
                if "section_index" in st.session_state and st.session_state.section_index < 9:
                    st.session_state.section_index += 1
                    st.rerun()
            else:
                st.error("❌ Error al guardar los datos. Intente nuevamente.")

    with st.expander("🔍 Ver datos guardados en esta sección"):
        st.write({
            "Donantes activas/mes": safe_int(st.session_state.get(prefix + "donantes_mes", 0)),
            "Volumen recolectado (L)": safe_float(st.session_state.get(prefix + "volumen_mes", 0.0)),
            "% En institución": safe_int(st.session_state.get(prefix + "pct_inst", 0)),
            "% En domicilio": safe_int(st.session_state.get(prefix + "pct_dom", 0)),
            "% En centros": safe_int(st.session_state.get(prefix + "pct_centros", 0)),
            "Receptores/mes": safe_int(st.session_state.get(prefix + "receptores_mes", 0)),
            "Volumen distribuido (L)": safe_float(st.session_state.get(prefix + "leche_distribuida", 0.0)),
        })
