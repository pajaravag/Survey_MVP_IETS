import streamlit as st
from utils.sheet_io import load_existing_data


def render():
    st.subheader("📄 Identificación de la IPS (obligatoria)")

    # ──────────────────────────────────────────────
    # Step 1: Verificar si los datos ya están cargados en sesión
    # ──────────────────────────────────────────────
    already_loaded = st.session_state.get("data_loaded", False)
    identificacion_data = st.session_state.get("identificacion", {})

    # Normalizar IPS ID para búsqueda segura
    ips_id_in_state = identificacion_data.get("ips_id", "").strip().lower()

    # ──────────────────────────────────────────────
    # Step 2: Cargar datos previos si aplica
    # ──────────────────────────────────────────────
    if ips_id_in_state and not already_loaded:
        loaded_data = load_existing_data(ips_id_in_state)
        if loaded_data:
            widget_keys_to_skip = {
                "ips_id_input",
                "correo_responsable_input",
                "nombre_responsable_input"
            }
            safe_loaded_data = {k: v for k, v in loaded_data.items() if k not in widget_keys_to_skip and not k.startswith("FormSubmitter:")}
            st.session_state.update(safe_loaded_data)
            st.session_state["data_loaded"] = True
            st.rerun()

    # ──────────────────────────────────────────────
    # Step 3: Establecer valores por defecto
    # ──────────────────────────────────────────────
    default_ips_id = identificacion_data.get("ips_id", "")
    default_correo = identificacion_data.get("correo_responsable", "")
    default_responsable = identificacion_data.get("nombre_responsable", "")
    disable_edit = already_loaded  # Deshabilitar edición si los datos ya fueron cargados

    # ──────────────────────────────────────────────
    # Step 4: Dibujar formulario
    # ──────────────────────────────────────────────
    with st.form("form_identificacion", clear_on_submit=False):
        ips_id = st.text_input(
            "🏥 Nombre de la IPS (obligatorio)",
            value=default_ips_id,
            key="ips_id_input",
            disabled=disable_edit,
            help="Ingrese un identificador único para la IPS. No se podrá modificar después de guardar."
        )

        correo = st.text_input(
            "📧 Correo electrónico del responsable (obligatorio)",
            value=default_correo,
            key="correo_responsable_input",
            help="Ingrese un correo válido para contacto."
        )

        responsable = st.text_input(
            "👤 Nombre del responsable (opcional)",
            value=default_responsable,
            key="nombre_responsable_input",
            help="Ingrese el nombre completo si desea dejar un responsable identificado."
        )

        submitted = st.form_submit_button("💾 Guardar identificación")

    # ──────────────────────────────────────────────
    # Step 5: Validación y guardado en session_state
    # ──────────────────────────────────────────────
    if submitted:
        missing_fields = []
        if not ips_id:
            missing_fields.append("código/nombre de la IPS")
        if not correo:
            missing_fields.append("correo electrónico")

        if missing_fields:
            st.warning(f"⚠️ Por favor complete los siguientes campos obligatorios: {', '.join(missing_fields)}.")
        else:
            st.session_state["identificacion"] = {
                "ips_id": ips_id.strip(),
                "correo_responsable": correo.strip(),
                "nombre_responsable": responsable.strip()
            }
            st.success("✅ Datos de identificación guardados correctamente.")

