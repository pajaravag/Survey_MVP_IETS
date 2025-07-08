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
    st.header("4. Infraestructura y Equipos")

    st.markdown("""
    ### 🏥 Instrucciones:
    Registre los equipos e infraestructura disponibles en las diferentes áreas del Banco de Leche Humana (BLH).

    Para cada equipo indique:
    - La **cantidad** disponible.
    - Si el equipo es **exclusivo para el BLH** o compartido.
    - El **porcentaje de uso** para el BLH (si aplica).
    - El **costo promedio por unidad** en pesos colombianos (COP).
    """)

    prefix = "infraestructura_equipos__"
    completion_flag = prefix + "completed"

    # Load existing session data if available
    resultados = st.session_state.get(prefix + "data", {})

    # 🔹 Define areas and equipment
    secciones = {
        "Recepción y registro de donantes": ["Escritorio", "Sillas", "Computador"],
        "Vestier": ["Lockers", "Lavamanos", "Dispensadores de jabón"],
        "Sala de extracción": ["Extractores manuales", "Extractores eléctricos", "Cortinas de privacidad"],
        "Punto de recepción y verificación inicial": ["Balanza", "Termómetro", "Neveras portátiles"]
    }

    # 🔹 Inputs for each area
    for area, equipos in secciones.items():
        with st.expander(f"🔹 {area}"):
            area_result = resultados.get(area, {})
            for eq in equipos:
                eq_data = area_result.get(eq, {})
                st.markdown(f"**{eq}**")

                cantidad = st.number_input(
                    f"Cantidad de {eq}", min_value=0, step=1,
                    value=safe_int(eq_data.get("cantidad", 0)),
                    key=f"{area}_{eq}_cantidad"
                )

                exclusivo = st.radio(
                    f"¿Es exclusivo del BLH?", ["Sí", "No"],
                    index=0 if eq_data.get("exclusivo", "Sí") == "Sí" else 1,
                    key=f"{area}_{eq}_exclusivo",
                    horizontal=True
                )

                uso_pct = 100 if exclusivo == "Sí" else st.slider(
                    "Porcentaje de uso para BLH",
                    min_value=0, max_value=100, step=1,
                    value=safe_int(eq_data.get("porcentaje_uso", 0)),
                    key=f"{area}_{eq}_porcentaje"
                )

                costo = st.number_input(
                    f"Costo promedio por unidad de {eq} ($ COP)",
                    min_value=0, step=1000,
                    value=safe_int(eq_data.get("costo", 0)),
                    key=f"{area}_{eq}_costo"
                )

                if area not in resultados:
                    resultados[area] = {}
                resultados[area][eq] = {
                    "cantidad": cantidad,
                    "exclusivo": exclusivo,
                    "porcentaje_uso": uso_pct,
                    "costo": costo
                }

    # 🔹 Save button and logic
    if st.button("💾 Guardar sección - Infraestructura"):
        st.session_state[prefix + "data"] = resultados

        # Validate: at least one non-zero quantity anywhere
        has_data = any(
            any(equipo.get("cantidad", 0) > 0 for equipo in area.values())
            for area in resultados.values()
        )

        st.session_state[completion_flag] = has_data

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de infraestructura guardados correctamente en Google Sheets.")
            # Optional: auto-advance to next section
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Verifique la conexión.")

    # 🔹 Show saved data for review
    with st.expander("🔍 Ver resumen de datos guardados"):
        st.write(resultados)
