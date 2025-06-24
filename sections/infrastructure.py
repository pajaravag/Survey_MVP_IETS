
import streamlit as st

def render():
    st.header("4. Infraestructura y Equipos")

    st.markdown("Ingrese la cantidad de equipos, si son exclusivos para el BLH y su costo estimado.")

    secciones = {
        "Recepción y registro de donantes": [
            "Escritorio", "Sillas", "Computador"
        ],
        "Vestier": [
            "Lockers", "Lavamanos", "Dispensadores de jabón"
        ],
        "Sala de extracción": [
            "Extractores manuales", "Extractores eléctricos", "Cortinas de privacidad"
        ],
        "Punto de recepción y verificación inicial": [
            "Balanza", "Termómetro", "Neveras portátiles"
        ]
    }

    resultados = {}

    for area, equipos in secciones.items():
        with st.expander(f"🔹 {area}"):
            area_result = {}
            for eq in equipos:
                with st.container():
                    st.markdown(f"**{eq}**")

                    cantidad = st.number_input(f"Cantidad de {eq}", min_value=0, step=1, key=f"{area}_{eq}_cantidad")
                    exclusivo = st.radio(
                        f"¿Es exclusivo del BLH?", ["Sí", "No"],
                        key=f"{area}_{eq}_exclusivo",
                        horizontal=True
                    )
                    uso_pct = 100 if exclusivo == "Sí" else st.slider(
                        "¿Qué porcentaje del uso es para BLH?",
                        min_value=0, max_value=100, step=1,
                        key=f"{area}_{eq}_porcentaje"
                    )
                    costo = st.number_input(f"Costo promedio por unidad de {eq} ($ COP)", min_value=0, step=1000, key=f"{area}_{eq}_costo")

                    area_result[eq] = {
                        "cantidad": cantidad,
                        "exclusivo": exclusivo,
                        "porcentaje_uso": uso_pct,
                        "costo": costo
                    }
            resultados[area] = area_result

    if st.button("Guardar sección - Infraestructura"):
        st.session_state["infraestructura_equipos"] = resultados
        st.success("✅ Datos de infraestructura registrados correctamente.")
