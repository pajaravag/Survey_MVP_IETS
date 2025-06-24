import streamlit as st

def render():
    st.header("3. Donantes y Receptores")

    with st.form("donantes_form"):
        donantes_mes = st.number_input("Número promedio de donantes activas/mes", min_value=0)
        volumen_mes = st.number_input("Volumen promedio de leche recolectada/mes (litros)", min_value=0.0)
        
        st.markdown("### Porcentaje de origen de la leche recolectada")
        pct_inst = st.slider("En institución", 0, 100)
        pct_dom = st.slider("En domicilio de la donante", 0, 100)
        pct_centros = st.slider("En centros de recolección", 0, 100)
        
        receptores_mes = st.number_input("Número de receptores activos /mes", min_value=0)
        leche_distribuida = st.number_input("Volumen promedio de leche distribuida/mes (litros)", min_value=0.0)
        
        submitted = st.form_submit_button("Guardar sección")

    if submitted:
        total_pct = pct_inst + pct_dom + pct_centros
        if total_pct != 100:
            st.warning(f"⚠️ La suma de los porcentajes debe ser 100% (actual: {total_pct}%).")
        else:
            st.success("✅ Datos registrados.")
            st.session_state["donantes_receptores"] = {
                "donantes_mes": donantes_mes,
                "volumen_mes": volumen_mes,
                "pct_inst": pct_inst,
                "pct_dom": pct_dom,
                "pct_centros": pct_centros,
                "receptores_mes": receptores_mes,
                "leche_distribuida": leche_distribuida
            }
