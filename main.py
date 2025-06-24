import streamlit as st
from PIL import Image

# Section modules
from sections import (
    identification, general_info, processes, donors_recipients,
    infrastructure, supplies, staff, utilities,
    transport, quality, depreciation
)

from utils.state_manager import (
    compute_progress,
    is_section_completed,
    save_response_to_csv
)

# App config
st.set_page_config(page_title="Encuesta BLH", layout="wide")

# Load and display logo
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("./assets/Logo.png", width=100)
with col_title:
    st.title("Formulario para Bancos de Leche Humana (BLH)")
    st.markdown("Complete cada sección. Puede guardar su progreso y continuar más tarde.")

# Section routing definition
section_definitions = [
    {"label": "1. Datos Generales", "key": "datos_generales", "render": general_info.render},
    {"label": "2. Procesos Estandarizados", "key": "procesos_realizados", "render": processes.render},
    {"label": "3. Donantes y Receptores", "key": "donantes_receptores", "render": donors_recipients.render},
    {"label": "4. Infraestructura y Equipos", "key": "infraestructura_equipos", "render": infrastructure.render},
    {"label": "5. Insumos Mensuales", "key": "insumos_mensuales", "render": supplies.render},
    {"label": "6. Personal Asignado", "key": "personal_exclusivo", "render": staff.render},
    {"label": "7. Servicios Públicos", "key": "servicios_publicos", "render": utilities.render},
    {"label": "8. Transporte y Recolección", "key": "transporte_modalidades", "render": transport.render},
    {"label": "9. Eficiencia y Calidad", "key": "calidad_seguridad", "render": quality.render},
    {"label": "10. Depreciación e Impuestos", "key": "depreciacion", "render": depreciation.render}
]

# Enforce identification before proceeding
identification.render()
if "identificacion" not in st.session_state:
    st.warning("⚠️ Complete la identificación para continuar.")
    st.stop()

# Initialize navigation index
if "section_index" not in st.session_state:
    st.session_state.section_index = 0

current_section = section_definitions[st.session_state.section_index]

# Progress bar
tracked_keys = [s["key"] for s in section_definitions]
filled, percent = compute_progress(st.session_state, tracked_keys)
st.progress(percent, text=f"{filled} de {len(tracked_keys)} secciones completadas")

# Sidebar navigation
with st.sidebar:
    st.markdown("### Navegación rápida")
    labels_with_status = [
        f"{'✅' if is_section_completed(st.session_state, s['key']) else '🔲'} {s['label']}"
        for s in section_definitions
    ]
    selected_label = st.selectbox("Ir a sección", labels_with_status)
    selected_clean = selected_label[2:].strip()
    st.session_state.section_index = next(i for i, s in enumerate(section_definitions) if s["label"] == selected_clean)

# Render current section
st.subheader(current_section["label"])
current_section["render"]()

# Navigation buttons
col1, col2, _ = st.columns([1, 1, 6])
with col1:
    if st.session_state.section_index > 0:
        if st.button("⬅️ Sección anterior"):
            st.session_state.section_index -= 1
            st.experimental_rerun()

with col2:
    if st.session_state.section_index < len(section_definitions) - 1:
        if st.button("➡️ Siguiente sección"):
            st.session_state.section_index += 1
            st.experimental_rerun()

# Export full dataset
st.markdown("---")
st.markdown("### Guardar toda la encuesta")
if st.button("📤 Guardar encuesta completa como archivo CSV"):
    st.info("📎 Esta versión de prueba no guarda datos. Solo para revisión del flujo.")
    file_path = save_response_to_csv(st.session_state)
    st.success(f"✅ Encuesta guardada en: `{file_path}`")