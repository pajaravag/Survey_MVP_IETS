import streamlit as st

def render():
    st.header("7. Servicios Públicos")

    st.markdown("Ingrese el costo mensual promedio de los siguientes servicios públicos atribuibles directamente al funcionamiento del BLH.")

    utilities = {
        "Suministro de energía": 0,
        "Suministro de agua y alcantarillado": 0,
        "Telefonía fija e internet": 0
    }

    results = {}
    for servicio in utilities:
        costo = st.number_input(
            f"{servicio} ($ COP/mes)",
            min_value=0.0,
            step=1000.0,
            key=f"util_{servicio}"
        )
        results[servicio] = costo

    if st.button("Guardar sección - Servicios Públicos"):
        st.session_state["servicios_publicos"] = results
        st.success("✅ Datos de servicios públicos registrados correctamente.")
