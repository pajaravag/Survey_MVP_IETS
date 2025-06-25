import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row

def render():
    st.header("7. Servicios Públicos")
    st.markdown("Ingrese el costo mensual promedio de los siguientes servicios públicos atribuibles directamente al funcionamiento del BLH.")

    servicios = {
        "Suministro de energía",
        "Suministro de agua y alcantarillado",
        "Telefonía fija e internet"
    }

    previous_data = st.session_state.get("servicios_publicos", {})
    results = {}

    for servicio in servicios:
        costo = st.number_input(
            f"{servicio} ($ COP/mes)",
            min_value=0.0,
            step=1000.0,
            value=previous_data.get(servicio, 0.0),
            key=f"util_{servicio}"
        )
        results[servicio] = costo

    if st.button("💾 Guardar sección y continuar"):
        st.session_state["servicios_publicos"] = results

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Servicios públicos registrados y guardados correctamente en Google Sheets.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos.")
