import streamlit as st
from utils.sheet_io import append_or_update_row
from utils.state_manager import flatten_session_state

def render():
    st.header("1. Datos Generales")

    st.markdown("""
    ### 📄 Instrucciones:
    Complete los datos generales de su establecimiento. Recuerde que esta información es necesaria para continuar.
    """)

    prefix = "datos_generales__"
    completion_flag = prefix + "completed"

    # Load previous values
    nombre = st.text_input(
        "Nombre del establecimiento",
        value=st.session_state.get(prefix + "nombre_inst", "")
    )

    tipo_inst_options = ["Pública", "Privada", "Mixta"]
    tipo_inst = st.selectbox(
        "Tipo de institución",
        tipo_inst_options,
        index=tipo_inst_options.index(st.session_state.get(prefix + "tipo_inst", "Pública"))
    )

    # Save button
    if st.button("💾 Guardar sección - Datos Generales"):
        st.session_state[prefix + "nombre_inst"] = nombre
        st.session_state[prefix + "tipo_inst"] = tipo_inst

        # ✅ Live completion check
        is_complete = bool(nombre.strip()) and bool(tipo_inst.strip())
        st.session_state[completion_flag] = is_complete

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Sección guardada en Google Sheets.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar en Google Sheets.")

    # ✅ Fallback: Display current status for debugging
    with st.expander("🔍 Ver datos guardados en esta sección"):
        st.write({
            "Nombre del establecimiento": st.session_state.get(prefix + "nombre_inst", ""),
            "Tipo de institución": st.session_state.get(prefix + "tipo_inst", ""),
            "Sección completada": st.session_state.get(completion_flag, False)
        })
