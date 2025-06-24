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

    selected = []
    with st.form("procesos_form"):
        st.markdown("Marque los procesos que realiza su institución:")
        for p in procesos:
            if st.checkbox(p, key=p):
                selected.append(p)

        submitted = st.form_submit_button("Guardar sección")

    if submitted:
        st.success("✅ Procesos registrados.")
        st.session_state["procesos_realizados"] = selected
