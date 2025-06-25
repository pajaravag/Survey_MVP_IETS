import streamlit as st

def render():
    st.subheader("Identificación del diligenciante (obligatoria)")

    prefill = st.session_state.get("identificacion", {})

    already_loaded = st.session_state.get("data_loaded", False)
    disable_edit = already_loaded  # prevent IPS ID changes after load

    with st.form("form_identificacion"):
        ips_id = st.text_input(
            "Código o nombre de la IPS",
            value=prefill.get("ips_id", ""),
            key="ips_id_input",
            disabled=disable_edit
        )
        correo = st.text_input(
            "Correo del responsable",
            value=prefill.get("correo_responsable", ""),
            key="correo_responsable_input"
        )
        responsable = st.text_input(
            "Nombre del responsable (opcional)",
            value=prefill.get("nombre_responsable", ""),
            key="nombre_responsable_input"
        )

        submitted = st.form_submit_button("Guardar identificación")

    if submitted:
        if not ips_id or not correo:
            st.warning("⚠️ Debe ingresar al menos el nombre/código de la IPS y el correo.")
        else:
            st.session_state["identificacion"] = {
                "ips_id": ips_id,
                "correo_responsable": correo,
                "nombre_responsable": responsable
            }
            st.success("✅ Datos de identificación guardados.")
