import streamlit as st
from utils.sheet_io import load_existing_data

def render():
    st.subheader("Identificación del diligenciante (obligatoria)")

    # Step 1: Check if we need to preload data
    already_loaded = st.session_state.get("data_loaded", False)
    identificacion_data = st.session_state.get("identificacion", {})

    # Normalize IPS ID for lookup
    ips_id_in_state = identificacion_data.get("ips_id", "").strip().lower()

    # If IPS is present but data not yet loaded → load safely before drawing widgets
    if ips_id_in_state and not already_loaded:
        loaded_data = load_existing_data(ips_id_in_state)
        if loaded_data:
            widget_keys_to_skip = {
                "ips_id_input",
                "correo_responsable_input",
                "nombre_responsable_input"
            }
            safe_loaded_data = {k: v for k, v in loaded_data.items() if k not in widget_keys_to_skip}
            st.session_state.update(safe_loaded_data)
            st.session_state["data_loaded"] = True
            st.rerun()  # ⬅️ Critical: force rerun before drawing the form

    # Step 2: Prepare default values
    default_ips_id = identificacion_data.get("ips_id", "")
    default_correo = identificacion_data.get("correo_responsable", "")
    default_responsable = identificacion_data.get("nombre_responsable", "")
    disable_edit = already_loaded

    # Step 3: Draw the form (only after session is safe)
    with st.form("form_identificacion"):
        ips_id = st.text_input(
            "Código o nombre de la IPS (obligatorio)",
            value=default_ips_id,
            key="ips_id_input",
            disabled=disable_edit
        )

        correo = st.text_input(
            "Correo electrónico del responsable (obligatorio)",
            value=default_correo,
            key="correo_responsable_input"
        )

        responsable = st.text_input(
            "Nombre del responsable (opcional)",
            value=default_responsable,
            key="nombre_responsable_input"
        )

        submitted = st.form_submit_button("💾 Guardar identificación")

    # Step 4: On submit → save logical state only
    if submitted:
        if not ips_id or not correo:
            st.warning("⚠️ Debe ingresar al menos el nombre/código de la IPS y el correo.")
        else:
            st.session_state["identificacion"] = {
                "ips_id": ips_id,
                "correo_responsable": correo,
                "nombre_responsable": responsable
            }
            st.success("✅ Datos de identificación guardados correctamente.")
            # No need to load again → data_loaded flag will prevent it
