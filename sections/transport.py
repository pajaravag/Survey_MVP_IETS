import streamlit as st

def render():
    st.header("8. Transporte y Recolección de Leche Humana")

    st.subheader("📍 Modalidades de recepción de leche humana")
    modalidades = {
        "En la institución donde se encuentra el BLH": st.checkbox("Institución"),
        "En las casas de las donantes": st.checkbox("Domicilio"),
        "En centros de recolección": st.checkbox("Centros de recolección")
    }

    st.subheader("🚚 Equipos de transporte utilizados")
    usa_equipos = st.radio(
        "¿La institución adquirió equipos especializados como termos o cajas isotérmicas?",
        ["Sí", "No"], horizontal=True
    )

    equipos_data = {}
    if usa_equipos == "Sí":
        equipos = ["Termos rígidos", "Cajas térmicas de poliestireno", "Neveras portátiles con acumuladores de frío"]
        for eq in equipos:
            st.markdown(f"**{eq}**")
            cantidad = st.number_input(f"Cantidad de contenedores ({eq})", min_value=0, step=1, key=f"{eq}_cantidad")
            capacidad = st.number_input(f"Capacidad por contenedor en litros ({eq})", min_value=0.0, step=0.5, key=f"{eq}_capacidad")
            costo = st.number_input(f"Costo promedio por unidad ({eq}) ($ COP)", min_value=0.0, step=1000.0, key=f"{eq}_costo")
            equipos_data[eq] = {
                "cantidad": cantidad,
                "capacidad_litros": capacidad,
                "costo_unitario": costo
            }

    st.subheader("🚗 Costo promedio de transporte según zona")
    costos_zona = {
        "Donación en zona urbana": st.number_input("Costo promedio por recolección en zona urbana ($ COP)", min_value=0.0, step=1000.0),
        "Donación en zona rural": st.number_input("Costo promedio por recolección en zona rural ($ COP)", min_value=0.0, step=1000.0),
        "Donación en zonas rurales alejadas": st.number_input("Costo promedio en zonas rurales alejadas ($ COP)", min_value=0.0, step=1000.0)
    }

    if st.button("Guardar sección - Transporte"):
        st.session_state["transporte_modalidades"] = modalidades
        st.session_state["transporte_equipos"] = equipos_data
        st.session_state["transporte_costos_zona"] = costos_zona
        st.success("✅ Datos de transporte registrados correctamente.")
