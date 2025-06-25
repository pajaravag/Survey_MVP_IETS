import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row

def render():
    st.header("8. Transporte y Recolección de Leche Humana")

    # Load previous data
    modalidades_prev = st.session_state.get("transporte_modalidades", {})
    equipos_prev = st.session_state.get("transporte_equipos", {})
    costos_prev = st.session_state.get("transporte_costos_zona", {})

    st.subheader("📍 Modalidades de recepción de leche humana")
    modalidades = {
        "En la institución donde se encuentra el BLH": st.checkbox(
            "Institución", value=modalidades_prev.get("En la institución donde se encuentra el BLH", False)),
        "En las casas de las donantes": st.checkbox(
            "Domicilio", value=modalidades_prev.get("En las casas de las donantes", False)),
        "En centros de recolección": st.checkbox(
            "Centros de recolección", value=modalidades_prev.get("En centros de recolección", False))
    }

    st.subheader("🚚 Equipos de transporte utilizados")
    usa_equipos = st.radio(
        "¿La institución adquirió equipos especializados como termos o cajas isotérmicas?",
        ["Sí", "No"],
        index=0 if equipos_prev else 1,
        horizontal=True
    )

    equipos_data = {}
    if usa_equipos == "Sí":
        equipos = [
            "Termos rígidos",
            "Cajas térmicas de poliestireno",
            "Neveras portátiles con acumuladores de frío"
        ]
        for eq in equipos:
            eq_data = equipos_prev.get(eq, {})
            st.markdown(f"**{eq}**")
            cantidad = st.number_input(
                f"Cantidad de contenedores ({eq})",
                min_value=0, step=1,
                value=eq_data.get("cantidad", 0),
                key=f"{eq}_cantidad"
            )
            capacidad = st.number_input(
                f"Capacidad por contenedor en litros ({eq})",
                min_value=0.0, step=0.5,
                value=eq_data.get("capacidad_litros", 0.0),
                key=f"{eq}_capacidad"
            )
            costo = st.number_input(
                f"Costo promedio por unidad ({eq}) ($ COP)",
                min_value=0.0, step=1000.0,
                value=eq_data.get("costo_unitario", 0.0),
                key=f"{eq}_costo"
            )
            equipos_data[eq] = {
                "cantidad": cantidad,
                "capacidad_litros": capacidad,
                "costo_unitario": costo
            }

    st.subheader("🚗 Costo promedio de transporte según zona")
    costos_zona = {
        "Donación en zona urbana": st.number_input(
            "Costo promedio por recolección en zona urbana ($ COP)",
            min_value=0.0, step=1000.0,
            value=costos_prev.get("Donación en zona urbana", 0.0)
        ),
        "Donación en zona rural": st.number_input(
            "Costo promedio por recolección en zona rural ($ COP)",
            min_value=0.0, step=1000.0,
            value=costos_prev.get("Donación en zona rural", 0.0)
        ),
        "Donación en zonas rurales alejadas": st.number_input(
            "Costo promedio en zonas rurales alejadas ($ COP)",
            min_value=0.0, step=1000.0,
            value=costos_prev.get("Donación en zonas rurales alejadas", 0.0)
        )
    }

    if st.button("💾 Guardar sección y continuar"):
        st.session_state["transporte_modalidades"] = modalidades
        st.session_state["transporte_equipos"] = equipos_data if usa_equipos == "Sí" else {}
        st.session_state["transporte_costos_zona"] = costos_zona

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de transporte registrados y guardados en Google Sheets.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos.")
