import streamlit as st

def render():
    st.subheader("Identificación del diligenciante (obligatoria)")
    
    with st.form("form_identificacion"):
        ips_id = st.text_input("Código o nombre de la IPS", key="ips_id")
        correo = st.text_input("Correo del responsable", key="correo_responsable")
        responsable = st.text_input("Nombre del responsable (opcional)", key="nombre_responsable")

        submitted = st.form_submit_button("Guardar identificación")

    if submitted:
        if not ips_id or not correo:
            st.warning("⚠️ Debe ingresar al menos el nombre/código de la IPS y el correo.")
        else:
            st.success("✅ Datos de identificación guardados.")
            st.session_state["identificacion"] = {
                "ips_id": ips_id,
                "correo_responsable": correo,
                "nombre_responsable": responsable
            }
