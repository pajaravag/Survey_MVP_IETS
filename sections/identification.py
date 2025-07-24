import streamlit as st
from utils.ui_styles import render_info_box, render_compact_example_box
from utils.sheet_io import safe_save_section, load_existing_data
from utils.state_manager import flatten_session_state
from utils.constants import MINIMUM_HEADERS_BY_SECTION

SECTION_PREFIX = "identificacion__"
SHEET_NAME = "Identificación"

def render():
    st.header("1. 🏥 Identificación de la IPS (Pregunta 1)")

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
"""), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo:**
- Nombre de la institución: *Hospital Básico San Gabriel*  
- Correo electrónico: *mrodriguez2@hospitalsg.co*  
- Nombre del responsable: *María Rodríguez*  
- Cargo: *Coordinadora Administrativa*  
- Teléfono: *313131313*
"""), unsafe_allow_html=True)

    # --- Precarga si aplica (solo si el valor aún no existe en session_state) ---
    data_loaded = st.session_state.get("data_loaded", False)

    def safe_get(field):
        val = st.session_state.get(f"{SECTION_PREFIX}{field}", "")
        if isinstance(val, str) or val is None:
            return val or ""
        return ""

    ips_id_in_state = safe_get("ips_id").strip().lower()

    # SOLO asigna valores a session_state si NO existen (evita conflicto widget)
    if ips_id_in_state and not data_loaded:
        loaded_data = load_existing_data(ips_id_in_state, sheet_name=SHEET_NAME)
        if loaded_data:
            for k, v in loaded_data.items():
                widget_key = f"{SECTION_PREFIX}{k}"
                if widget_key not in st.session_state:
                    st.session_state[widget_key] = v if isinstance(v, str) or v is None else str(v)
            st.session_state["data_loaded"] = True
            st.rerun()

    disable_edit = data_loaded

    with st.form("form_identificacion", clear_on_submit=False):
        ips_id = st.text_input(
            "🏥 Nombre completo de la institución",
            value=safe_get("ips_id"),
            key=f"{SECTION_PREFIX}ips_id",
            disabled=disable_edit,
            help="Este identificador será usado como clave y no podrá cambiarse luego."
        )

        correo = st.text_input(
            "📧 Correo electrónico del responsable",
            value=safe_get("correo_responsable"),
            key=f"{SECTION_PREFIX}correo_responsable"
        )

        nombre = st.text_input(
            "👤 Nombre del responsable",
            value=safe_get("nombre_responsable"),
            key=f"{SECTION_PREFIX}nombre_responsable"
        )

        cargo = st.text_input(
            "💼 Cargo del responsable",
            value=safe_get("cargo_responsable"),
            key=f"{SECTION_PREFIX}cargo_responsable"
        )

        telefono = st.text_input(
            "📞 Teléfono de contacto",
            value=safe_get("telefono_responsable"),
            key=f"{SECTION_PREFIX}telefono_responsable"
        )

        submitted = st.form_submit_button("💾 Guardar identificación")

    if submitted:
        # 1. Extrae sólo los campos SIN prefijo para guardar
        raw_data = flatten_session_state(prefix=SECTION_PREFIX)
        # 2. Valida obligatorios
        required_fields = MINIMUM_HEADERS_BY_SECTION.get(SECTION_PREFIX, [])
        missing_fields = [
            field for field in required_fields if not raw_data.get(field, "").strip()
        ]
        if missing_fields:
            st.warning(
                f"⚠️ Por favor complete los siguientes campos obligatorios: {', '.join(missing_fields)}."
            )
        else:
            success = safe_save_section(
                id_field=raw_data["ips_id"],
                sheet_name=SHEET_NAME,
                section_prefix=SECTION_PREFIX
            )
            if success:
                st.success("✅ Datos de identificación guardados correctamente.")
                # Marca la sección como completada en session_state (clave: "identificacion")
                st.session_state["identificacion"] = {
                    "ips_id": raw_data["ips_id"]
                }
                st.session_state["data_loaded"] = False
                st.session_state.section_index = 2  # Avanza a la siguiente sección
                st.rerun()
            else:
                st.error("❌ Ocurrió un error guardando los datos. Intente nuevamente.")
