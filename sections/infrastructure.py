import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row

def render():
    st.header("4. Infraestructura y Equipos")
    st.markdown("Ingrese la cantidad de equipos, si son exclusivos para el BLH y su costo estimado.")

    secciones = {
        "Recepción y registro de donantes": ["Escritorio", "Sillas", "Computador"],
        "Vestier": ["Lockers", "Lavamanos", "Dispensadores de jabón"],
        "Sala de extracción": ["Extractores manuales", "Extractores eléctricos", "Cortinas de privacidad"],
        "Punto de recepción y verificación inicial": ["Balanza", "Termómetro", "Neveras portátiles"]
    }

    resultados = st.session_state.get("infraestructura_equipos", {})

    for area, equipos in secciones.items():
        with st.expander(f"🔹 {area}"):
            area_result = resultados.get(area, {})
            for eq in equipos:
                eq_data = area_result.get(eq, {})
                st.markdown(f"**{eq}**")

                cantidad = st.number_input(
                    f"Cantidad de {eq}", min_value=0, step=1,
                    value=eq_data.get("cantidad", 0),
                    key=f"{area}_{eq}_cantidad"
                )

                exclusivo = st.radio(
                    f"¿Es exclusivo del BLH?", ["Sí", "No"],
                    index=0 if eq_data.get("exclusivo", "Sí") == "Sí" else 1,
                    key=f"{area}_{eq}_exclusivo",
                    horizontal=True
                )

                uso_pct = 100 if exclusivo == "Sí" else st.slider(
                    "¿Qué porcentaje del uso es para BLH?",
                    min_value=0, max_value=100, step=1,
                    value=eq_data.get("porcentaje_uso", 0),
                    key=f"{area}_{eq}_porcentaje"
                )

                costo = st.number_input(
                    f"Costo promedio por unidad de {eq} ($ COP)",
                    min_value=0, step=1000,
                    value=eq_data.get("costo", 0),
                    key=f"{area}_{eq}_costo"
                )

                # Save values live into session (nested)
                if area not in resultados:
                    resultados[area] = {}
                resultados[area][eq] = {
                    "cantidad": cantidad,
                    "exclusivo": exclusivo,
                    "porcentaje_uso": uso_pct,
                    "costo": costo
                }

    if st.button("💾 Guardar sección y continuar"):
        st.session_state["infraestructura_equipos"] = resultados

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de infraestructura registrados y guardados en Google Sheets.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos.")
