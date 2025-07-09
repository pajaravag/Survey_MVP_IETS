import streamlit as st
from PIL import Image

# ──────────────────────────────────────────────
# Import Local Modules
# ──────────────────────────────────────────────

from sections import (
    identification, general_info, processes, donors_recipients,
    infrastructure, supplies, staff, utilities,
    transport, quality, depreciation
)

from utils.state_manager import (
    compute_progress,
    flatten_session_state
)

from utils.sheet_io import (
    load_existing_data,
    append_or_update_row
)

from config import SURVEY_SECTIONS, INSTRUCTIVO_URL

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────

st.set_page_config(page_title="Encuesta BLH", layout="wide")

col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("assets/Logo.png", width=100)

with col_title:
    st.title("Formulario para Bancos de Leche Humana (BLH)")
    st.markdown("Complete cada sección. Puede guardar su progreso y continuar más tarde.")
    st.markdown(
        f"> **Nota:** La información recopilada está protegida por el derecho fundamental de **Habeas Data** según la Constitución Política de Colombia y la Ley 1581 de 2012. El uso de estos datos debe ceñirse estrictamente a los fines autorizados. Consulte el [Instructivo aquí]({INSTRUCTIVO_URL})."
    )

# ──────────────────────────────────────────────
# Section Definitions (Navigation & Rendering)
# ──────────────────────────────────────────────

section_definitions = [
    {"label": "1. Datos Generales", "key": "datos_generales__completed", "render": general_info.render},
    {"label": "2. Procesos Estandarizados", "key": "procesos_realizados__completed", "render": processes.render},
    {"label": "3. Donantes y Receptores", "key": "donantes_receptores__completed", "render": donors_recipients.render},
    {"label": "4. Infraestructura y Equipos", "key": "infraestructura_equipos__completed", "render": infrastructure.render},
    {"label": "5. Insumos Mensuales", "key": "insumos_mensuales__completed", "render": supplies.render},
    {"label": "6. Personal Asignado", "key": "personal_exclusivo__completed", "render": staff.render},
    {"label": "7. Servicios Públicos", "key": "servicios_publicos__completed", "render": utilities.render},
    {"label": "8. Transporte y Recolección", "key": "transporte_modalidades__completed", "render": transport.render},
    {"label": "9. Eficiencia y Calidad", "key": "calidad_seguridad__completed", "render": quality.render},
    {"label": "10. Depreciación e Impuestos", "key": "depreciacion__completed", "render": depreciation.render},
]

# ──────────────────────────────────────────────
# Identification Section (Required First Step)
# ──────────────────────────────────────────────

identification.render()

if "identificacion" not in st.session_state:
    st.warning("⚠️ Por favor complete la identificación para continuar.")
    st.stop()

ips_id = st.session_state["identificacion"].get("ips_id", "").strip().lower()
already_loaded = st.session_state.get("data_loaded", False)

if ips_id and not already_loaded:
    existing_data = load_existing_data(ips_id)
    if existing_data:
        widget_keys_to_skip = {"ips_id_input", "correo_responsable_input", "nombre_responsable_input"}
        safe_data = {k: v for k, v in existing_data.items() if k not in widget_keys_to_skip and not k.startswith("FormSubmitter:")}
        st.session_state.update(safe_data)
        st.info(f"📂 Datos previos restaurados para IPS: `{ips_id}`.")
    else:
        st.info("📝 No se encontraron datos previos para esta IPS.")

    st.session_state["data_loaded"] = True
    st.rerun()

# ──────────────────────────────────────────────
# Navigation State Initialization
# ──────────────────────────────────────────────

if "section_index" not in st.session_state:
    st.session_state.section_index = 0

# ──────────────────────────────────────────────
# Sidebar Navigation Menu
# ──────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 📑 Navegación rápida")

    labels_with_status = [
        f"{'✅' if st.session_state.get(section['key'], False) else '🔲'} {section['label']}"
        for section in section_definitions
    ]

    selected_label = st.selectbox("Ir a sección", labels_with_status, index=st.session_state.section_index)
    selected_index = next(i for i, s in enumerate(section_definitions) if s["label"] in selected_label)

    if selected_index != st.session_state.section_index:
        st.session_state.section_index = selected_index
        st.rerun()

# ──────────────────────────────────────────────
# Render Current Section
# ──────────────────────────────────────────────

current_section = section_definitions[st.session_state.section_index]
st.subheader(current_section["label"])
current_section["render"]()

# ──────────────────────────────────────────────
# Progress Bar (Global Progress)
# ──────────────────────────────────────────────

completion_flags = [s["key"] for s in section_definitions]
completed_count, progress_percent = compute_progress(st.session_state, completion_flags)

st.progress(progress_percent, text=f"{completed_count} de {len(completion_flags)} secciones completadas")

# ──────────────────────────────────────────────
# Navigation Buttons (Previous / Next)
# ──────────────────────────────────────────────

col1, col2, _ = st.columns([1, 1, 6])

with col1:
    if st.session_state.section_index > 0:
        if st.button("⬅️ Sección anterior"):
            st.session_state.section_index -= 1
            st.rerun()

with col2:
    if st.session_state.section_index < len(section_definitions) - 1:
        if st.button("➡️ Siguiente sección"):
            st.session_state.section_index += 1
            st.rerun()

# ──────────────────────────────────────────────
# Final Section Message & Global Save
# ──────────────────────────────────────────────

if st.session_state.section_index == len(section_definitions) - 1:
    st.success("🎉 Ha llegado al final del formulario.")
    st.markdown("Puede revisar cualquier sección usando el menú lateral o los botones de navegación.")
    if st.button("⬅️ Volver al inicio"):
        st.session_state.section_index = 0
        st.rerun()

st.markdown("---")
st.markdown("### 📤 Guardar encuesta completa")

if st.button("Guardar encuesta como CSV y Google Sheets"):
    flat_data = flatten_session_state(st.session_state)
    success = append_or_update_row(flat_data)
    ips_name = st.session_state.get("identificacion", {}).get("ips_id", "IPS desconocida")
    if success:
        st.success(f"✅ Encuesta de `{ips_name}` guardada exitosamente.")
    else:
        st.error("❌ Error al guardar la encuesta. Por favor intente nuevamente.")
