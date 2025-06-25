import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row

def render():
    st.header("3. Donantes y Receptores")

    prefix = "donantes_receptores__"
    data = st.session_state.get("donantes_receptores", {})

    with st.form("donantes_form"):
        donantes_mes = st.number_input(
            "Número promedio de donantes activas/mes", 
            min_value=0, 
            value=data.get("donantes_mes", 0)
        )

        volumen_mes = st.number_input(
            "Volumen promedio de leche recolectada/mes (litros)", 
            min_value=0.0, 
            value=data.get("volumen_mes", 0.0)
        )

        st.markdown("### Porcentaje de origen de la leche recolectada")
        pct_inst = st.slider("En institución", 0, 100, value=data.get("pct_inst", 0))
        pct_dom = st.slider("En domicilio de la donante", 0, 100, value=data.get("pct_dom", 0))
        pct_centros = st.slider("En centros de recolección", 0, 100, value=data.get("pct_centros", 0))

        receptores_mes = st.number_input(
            "Número de receptores activos /mes", 
            min_value=0, 
            value=data.get("receptores_mes", 0)
        )

        leche_distribuida = st.number_input(
            "Volumen promedio de leche distribuida/mes (litros)", 
            min_value=0.0, 
            value=data.get("leche_distribuida", 0.0)
        )

        submitted = st.form_submit_button("💾 Guardar sección y continuar")

    if submitted:
        total_pct = pct_inst + pct_dom + pct_centros
        if total_pct != 100:
            st.warning(f"⚠️ La suma de los porcentajes debe ser 100% (actual: {total_pct}%).")
        else:
            # Save to session
            st.session_state["donantes_receptores"] = {
                "donantes_mes": donantes_mes,
                "volumen_mes": volumen_mes,
                "pct_inst": pct_inst,
                "pct_dom": pct_dom,
                "pct_centros": pct_centros,
                "receptores_mes": receptores_mes,
                "leche_distribuida": leche_distribuida
            }

            # Flatten and save to Google Sheets
            flat_data = flatten_session_state(st.session_state)
            success = append_or_update_row(flat_data)

            if success:
                st.success("✅ Datos registrados y guardados en Google Sheets.")

                # Advance to next section
                if "section_index" in st.session_state and st.session_state.section_index < 9:
                    st.session_state.section_index += 1
                    st.rerun()
            else:
                st.error("❌ Hubo un error al guardar los datos.")
