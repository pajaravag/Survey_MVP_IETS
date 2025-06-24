import streamlit as st

def render():
    st.header("1. Datos Generales del BLH")

    with st.form("datos_generales_form"):
        nombre_inst = st.text_input("Nombre de la institución")
        anio_impl = st.number_input("Año de implementación del BLH", min_value=1990, max_value=2100, step=1)
        
        tipo_inst = st.radio(
            "Tipo de institución",
            options=["Hospital público", "Clínica privada", "Mixta"]
        )

        submit = st.form_submit_button("Guardar sección")

    if submit:
        st.success("✅ Datos guardados correctamente (aún no se persisten en disco).")
        st.session_state["datos_generales"] = {
            "nombre_inst": nombre_inst,
            "anio_impl": anio_impl,
            "tipo_inst": tipo_inst
        }
