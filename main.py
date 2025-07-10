import streamlit as st

# ──────────────────────────────────────────────
# Import Local Modules
# ──────────────────────────────────────────────

from sections import (
    identification, general_info, processes, donors_recipients,
    infrastructure, supplies, staff, utilities,
    transport, quality, depreciation
)

from utils.state_manager import compute_progress, flatten_session_state
from utils.sheet_io import load_existing_data, append_or_update_row
from utils.ui_styles import render_info_box
from utils.ui_layout import render_header, render_footer
from config import INSTRUCTIVO_URL

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────

st.set_page_config(page_title="Encuesta BLH", layout="wide")

# Header Institucional
render_header()

# Introducción
st.markdown(render_info_box(f"""
Complete cada sección. Puede guardar su progreso y continuar más tarde.<br><br>
<strong>Nota:</strong> La información está protegida por el derecho fundamental de <strong>Habeas Data</strong> (Ley 1581 de 2012). Consulte el <a href='{INSTRUCTIVO_URL}' target='_blank'>Instructivo aquí</a>.
"""), unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Secciones
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
# Identificación Inicial
# ──────────────────────────────────────────────

identification.render()

if "identificacion" not in st.session_state:
    st.warning("⚠️ Por favor complete la identificación para continuar.")
    st.stop()

ips_id = st.session_state["identificacion"].get("ips_id", "").strip().lower()
if ips_id and not st.session_state.get("data_loaded", False):
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

if "section_index" not in st.session_state:
    st.session_state.section_index = 0

# ──────────────────────────────────────────────
# Sidebar Navegación
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
# Render Sección Actual
# ──────────────────────────────────────────────

current_section = section_definitions[st.session_state.section_index]
st.subheader(current_section["label"])
current_section["render"]()

# ──────────────────────────────────────────────
# Barra de Progreso Visual
# ──────────────────────────────────────────────

completed_count, progress_percent = compute_progress(st.session_state, [s["key"] for s in section_definitions])

st.progress(progress_percent, text=f"🔄 Progreso general: {completed_count} de {len(section_definitions)} secciones completadas")

# ──────────────────────────────────────────────
# Botones Navegación
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
# Mensaje Final
# ──────────────────────────────────────────────

if st.session_state.section_index == len(section_definitions) - 1:
    st.success("🎉 Ha llegado al final del formulario. Puede revisar cualquier sección antes de finalizar.")
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

# ──────────────────────────────────────────────
# Footer Institucional
# ──────────────────────────────────────────────

st.markdown("<hr>", unsafe_allow_html=True)
render_footer()
