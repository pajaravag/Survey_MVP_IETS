import streamlit as st

def render():
    st.header("2. Procesos Estandarizados realizados en el BLH")

    procesos = [
        "Captación, Selección y Acompañamiento de Usuarias",
        "Extracción y Conservación",
        "Transporte",
        "Recepción",
        "Almacenamiento",
        "Deshielo",
        "Selección y Clasificación",
        "Reenvasado",
        "Pasteurización",
        "Control Microbiológico",
        "Distribución",
        "Seguimiento y Trazabilidad"
    ]

    # Load previous selections if any
    prev_selected = st.session_state.get("procesos_realizados", [])

    selected = []
    with st.form("procesos_form"):
        st.markdown("Marque los procesos que realiza su institución:")

        for p in procesos:
            checked = p in prev_selected
            if st.checkbox(p, value=checked, key=f"chk_{p}"):
                selected.append(p)

        guardar = st.form_submit_button("💾 Guardar sección y continuar")

    if guardar:
        st.session_state["procesos_realizados"] = selected
        st.success("✅ Procesos registrados correctamente.")

        if "section_index" in st.session_state and st.session_state.section_index < 9:
            st.session_state.section_index += 1
            st.rerun()
