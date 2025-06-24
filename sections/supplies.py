import streamlit as st

def render():
    st.header("5. Insumos Mensuales")

    st.markdown("Indique la unidad, cantidad mensual y el costo promedio por unidad de cada insumo utilizado en el BLH.")

    categorias = {
        "Insumos para almacenar": ["Frascos estériles"],
        "Reactivos de laboratorio": ["Caldo bilis-verde brillante al 2%", "Tubos microhematocritos fco x 100", "Alcohol al 95%"],
        "Elementos de protección personal": ["Bata desechable", "Guantes", "Tapabocas", "Polainas desechables", "Kit desechable paquete", "Gorro desechable"],
        "Etiquetas y sistemas de trazabilidad": ["Etiquetas"],
        "Productos de limpieza/desinfección": ["Desinfectante", "Jabón quirúrgico", "Alcohol 70%", "Antibacterial", "Toalla de papel"],
        "Materiales de laboratorio": ["Examen de laboratorio"],
        "Otros": ["Otro 1", "Otro 2", "Otro 3"]
    }

    insumos_data = {}

    for categoria, insumos in categorias.items():
        with st.expander(f"🔹 {categoria}"):
            categoria_data = {}
            for insumo in insumos:
                with st.container():
                    st.markdown(f"**{insumo}**")
                    unidad = st.text_input(f"Unidad de medida para {insumo}", key=f"{categoria}_{insumo}_unidad")
                    cantidad = st.number_input(f"Cantidad mensual de {insumo}", min_value=0.0, step=1.0, key=f"{categoria}_{insumo}_cantidad")
                    costo = st.number_input(f"Costo promedio por unidad de {insumo} ($ COP)", min_value=0.0, step=100.0, key=f"{categoria}_{insumo}_costo")

                    categoria_data[insumo] = {
                        "unidad": unidad,
                        "cantidad": cantidad,
                        "costo": costo
                    }
            insumos_data[categoria] = categoria_data

    if st.button("Guardar sección - Insumos mensuales"):
        st.session_state["insumos_mensuales"] = insumos_data
        st.success("✅ Datos de insumos registrados correctamente.")
