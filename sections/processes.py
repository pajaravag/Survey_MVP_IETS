import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row

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

    # Retrieve previous selection if exists
    preselected = st.session_state.get("procesos_realizados", [])

    selected = []
    with st.form("procesos_form"):
        st.markdown("Marque los procesos que realiza su institución:")
        for p in procesos:
            if st.checkbox(p, value=(p in preselected), key=f"procesos_realizados__{p}"):
                selected.append(p)

        submitted = st.form_submit_button("💾 Guardar sección")

    if submitted:
        # Save as list in session
        st.session_state["procesos_realizados"] = selected

        # Flatten session state and export
        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Procesos registrados y guardados en Google Sheets.")
        else:
            st.error("❌ Hubo un error al guardar los datos.")
