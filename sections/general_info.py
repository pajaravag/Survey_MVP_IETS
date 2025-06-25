import streamlit as st
from utils.sheet_io import append_or_update_row
from utils.state_manager import flatten_session_state

def render():
    st.header("1. Datos Generales")

    # Retrieve pre-filled values if available
    prefix = "datos_generales__"
    nombre = st.text_input("Nombre del establecimiento", value=st.session_state.get(prefix + "nombre_inst", ""))
    tipo_inst = st.selectbox("Tipo de institución", ["Pública", "Privada", "Mixta"], 
                             index=["Pública", "Privada", "Mixta"].index(
                                 st.session_state.get(prefix + "tipo_inst", "Pública")
                             ))

    # Save section button
    if st.button("💾 Guardar sección - Datos Generales"):
        # Save section data to session
        st.session_state["datos_generales"] = {
            "nombre_inst": nombre,
            "tipo_inst": tipo_inst
        }

        # Flatten full session and export
        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Sección guardada en Google Sheets.")
        else:
            st.error("❌ No se pudo guardar. Verifica conexión.")
