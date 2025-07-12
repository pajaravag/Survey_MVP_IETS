import streamlit as st
from utils.sheet_io import load_existing_data
from utils.ui_styles import render_info_box, render_compact_example_box

def render():
    st.header("1. 🏥 Identificación de la IPS (Pregunta 1)")

    # ──────────────────────────────────────────────
    # Instrucciones del formulario oficial
    # ──────────────────────────────────────────────
    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
Ingrese los **datos generales de la institución** que opera el Banco de Leche Humana (BLH).

Campos obligatorios:
- Nombre oficial de la IPS
- Correo electrónico del responsable

Campos opcionales (recomendados):
- Nombre del responsable
- Cargo del responsable
- Teléfono de contacto

Esta información permite rastrear el origen del formulario y facilitar el acompañamiento posterior.
    """), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo:**

- Nombre de la institución: *Hospital Básico San Gabriel*  
- Correo electrónico: *mrodriguez2@hospitalsg.co*  
- Nombre del responsable: *María Rodríguez*  
- Cargo: *Coordinadora Administrativa*  
- Teléfono: *313131313*
    """), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Recuperar estado y verificar si ya está cargado
    # ──────────────────────────────────────────────
    already_loaded = st.session_state.get("data_loaded", False)
    identificacion_data = st.session_state.get("identificacion", {})

    ips_id_in_state = identificacion_data.get("ips_id", "").strip().lower()

    if ips_id_in_state and not already_loaded:
        loaded_data = load_existing_data(ips_id_in_state)
        if loaded_data:
            widget_keys_to_skip = {
                "ips_id_input", "correo_responsable_input", "nombre_responsable_input",
                "cargo_responsable_input", "telefono_responsable_input"
            }
            safe_loaded_data = {
                k: v for k, v in loaded_data.items()
                if k not in widget_keys_to_skip and not k.startswith("FormSubmitter:")
            }
            st.session_state.update(safe_loaded_data)
            st.session_state["data_loaded"] = True
            st.rerun()

    # Valores por defecto si están en memoria
    default_values = {
        "ips_id": identificacion_data.get("ips_id", ""),
        "correo": identificacion_data.get("correo_responsable", ""),
        "nombre": identificacion_data.get("nombre_responsable", ""),
        "cargo": identificacion_data.get("cargo_responsable", ""),
        "telefono": identificacion_data.get("telefono_responsable", "")
    }
    disable_edit = already_loaded

    # ──────────────────────────────────────────────
    # Formulario
    # ──────────────────────────────────────────────
    with st.form("form_identificacion", clear_on_submit=False):
        ips_id = st.text_input(
            "🏥 Nombre completo de la institución (obligatorio)",
            value=default_values["ips_id"],
            key="ips_id_input",
            disabled=disable_edit,
            help="Ingrese el nombre oficial completo. Este identificador será usado como clave y no podrá cambiarse luego."
        )

        correo = st.text_input(
            "📧 Correo electrónico del responsable (obligatorio)",
            value=default_values["correo"],
            key="correo_responsable_input",
            help="Correo válido para contacto."
        )

        nombre = st.text_input(
            "👤 Nombre del responsable (opcional)",
            value=default_values["nombre"],
            key="nombre_responsable_input",
            help="Nombre completo del responsable del formulario, si desea registrarlo."
        )

        cargo = st.text_input(
            "💼 Cargo del responsable (opcional)",
            value=default_values["cargo"],
            key="cargo_responsable_input",
            help="Ejemplo: Coordinador(a) BLH, Médico(a) Pediatra, etc."
        )

        telefono = st.text_input(
            "📞 Teléfono de contacto (opcional)",
            value=default_values["telefono"],
            key="telefono_responsable_input",
            help="Incluya un número celular o fijo que permita contacto posterior."
        )

        submitted = st.form_submit_button("💾 Guardar identificación")

    # ──────────────────────────────────────────────
    # Validación y almacenamiento
    # ──────────────────────────────────────────────
    if submitted:
        missing_fields = []
        if not ips_id.strip():
            missing_fields.append("nombre oficial de la IPS")
        if not correo.strip():
            missing_fields.append("correo electrónico")

        if missing_fields:
            st.warning(f"⚠️ Por favor complete los siguientes campos obligatorios: {', '.join(missing_fields)}.")
        else:
            st.session_state["identificacion"] = {
                "ips_id": ips_id.strip(),
                "correo_responsable": correo.strip(),
                "nombre_responsable": nombre.strip(),
                "cargo_responsable": cargo.strip(),
                "telefono_responsable": telefono.strip()
            }
            st.success("✅ Datos de identificación guardados correctamente.")
