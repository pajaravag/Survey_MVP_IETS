import streamlit as st
import json
from utils.ui_styles import render_info_box
from utils.sheet_io import safe_save_section, load_existing_data
from utils.state_manager import (
    flatten_session_state,
    validate_ips_id,
    persist_valid_ips_info,   # <--- USAR ESTA FUNCIÓN
    get_current_ips_id
)
from utils.constants import MINIMUM_HEADERS_BY_SECTION

SECTION_PREFIX = "identificacion__"
SHEET_NAME = "Identificación"
IPS_HASH_FILE = "data/ips_lookup.json"

def load_ips_lookup():
    with open(IPS_HASH_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def render():
    st.header("1. 🏥 Identificación de la IPS (Pregunta 1)")

    st.markdown(render_info_box("""
**ℹ️ Ingrese el identificador único de su IPS**  
Para comenzar, escriba el identificador único que le fue enviado por correo oficial del IETS.
"""), unsafe_allow_html=True)

    # 1. Entrada de identificador
    input_hash = st.text_input(
        "🔑 Identificador único de su IPS",
        key="input_hash"
    ).strip()

    # 2. Validación robusta contra archivo de lookup
    hashes_ips = load_ips_lookup()
    ips_name = hashes_ips.get(input_hash) if input_hash else None

    if input_hash:
        if not ips_name:
            st.warning("⚠️ El identificador ingresado **no es válido**. Por favor, verifique su código y vuelva a intentarlo.", icon="⚠️")
            st.stop()
        else:
            st.success(f"✅ Identificador válido. IPS detectada: **{ips_name}**")
            # Persistencia robusta y centralizada (ambos: id y nombre)
            persist_valid_ips_info(input_hash, ips_name)
            st.session_state[f"{SECTION_PREFIX}ips_id"] = input_hash
            st.session_state[f"{SECTION_PREFIX}nombre_ips"] = ips_name

            # Precarga de datos si aplica (una sola vez)
            if not st.session_state.get("data_loaded", False):
                loaded_data = load_existing_data(input_hash, sheet_name=SHEET_NAME)
                if loaded_data:
                    for k, v in loaded_data.items():
                        widget_key = f"{SECTION_PREFIX}{k}"
                        if widget_key not in st.session_state:
                            st.session_state[widget_key] = v if isinstance(v, str) or v is None else str(v)
                    st.session_state["data_loaded"] = True
                    st.rerun()

            # Formulario (si y solo si identificador es válido)
            with st.form("form_identificacion", clear_on_submit=False):
                st.text_input(
                    "🏥 Nombre completo de la institución",
                    key=f"{SECTION_PREFIX}nombre_ips",
                    disabled=True
                )

                correo = st.text_input(
                    "📧 Correo electrónico del responsable",
                    #value=st.session_state.get(f"{SECTION_PREFIX}correo_responsable", ""),
                    key=f"{SECTION_PREFIX}correo_responsable"
                )
                nombre = st.text_input(
                    "👤 Nombre del responsable",
                    #value=st.session_state.get(f"{SECTION_PREFIX}nombre_responsable", ""),
                    key=f"{SECTION_PREFIX}nombre_responsable"
                )
                cargo = st.text_input(
                    "💼 Cargo del responsable",
                    #value=st.session_state.get(f"{SECTION_PREFIX}cargo_responsable", ""),
                    key=f"{SECTION_PREFIX}cargo_responsable"
                )
                telefono = st.text_input(
                    "📞 Teléfono de contacto",
                    #value=st.session_state.get(f"{SECTION_PREFIX}telefono_responsable", ""),
                    key=f"{SECTION_PREFIX}telefono_responsable"
                )
                submitted = st.form_submit_button("💾 Guardar identificación")

            if submitted:
                # GARANTIZA que ips_id esté presente
                st.session_state[f"{SECTION_PREFIX}ips_id"] = input_hash
                
                raw_data = flatten_session_state(prefix=SECTION_PREFIX)

                required_fields = MINIMUM_HEADERS_BY_SECTION.get(SECTION_PREFIX, [])
                missing_fields = [
                    field for field in required_fields if not raw_data.get(field, "").strip()
                ]
                if missing_fields:
                    st.warning(
                        f"⚠️ Por favor complete los siguientes campos obligatorios: {', '.join(missing_fields)}.",
                        icon="⚠️"
                    )
                else:
                    success = safe_save_section(
                        id_field=raw_data["ips_id"],
                        sheet_name=SHEET_NAME,
                        section_prefix=SECTION_PREFIX
                    )
                    if success:
                        st.success("✅ Datos de identificación guardados correctamente.")
                        st.session_state["data_loaded"] = False
                        st.session_state.section_index = 2  # Avanza a la siguiente sección
                        st.session_state.navigation_triggered = True
                        st.rerun()
                    else:
                        st.error("❌ Ocurrió un error guardando los datos. Intente nuevamente.", icon="❌")

    else:
        st.info("Ingrese el identificador único enviado por IETS para continuar.", icon="ℹ️")
