import streamlit as st

# ──────────────────────────────────────────────
# Importación de módulos locales
# ──────────────────────────────────────────────
from sections import (
    intro, identification, general_info, donors_recipients,
    security_efficiency, costs, costs_equipos, supplies, staff,
    utilities, transport
)
from utils.state_manager import compute_progress, flatten_session_state
from utils.sheet_io import load_existing_data, append_or_update_row
from utils.ui_layout import render_header, render_footer

# ──────────────────────────────────────────────
# Configuración de página
# ──────────────────────────────────────────────
st.set_page_config(page_title="Encuesta BLH - IETS", layout="wide")
render_header()

# ──────────────────────────────────────────────
# Definición de secciones
# ──────────────────────────────────────────────
section_definitions = [
    {"label": "0. Introducción", "key": None, "render": intro.render},
    {"label": "1. Identificación de la IPS", "key": None, "render": identification.render},
    {"label": "2. Datos Generales del BLH (Preguntas 1 a 4)", "key": "datos_generales__completed", "render": general_info.render},
    {"label": "3. Donantes y Receptores (Preguntas 5 a 9)", "key": "donantes_receptores__completed", "render": donors_recipients.render},
    {"label": "4. Seguridad y Eficiencia (Preguntas 10 a 14)", "key": "seguridad_eficiencia__completed", "render": security_efficiency.render},
    {"label": "5. Costos Asociados al Proceso BLH (Preguntas 15 a 16)", "key": "costos_blh__completed", "render": costs.render},
    {"label": "6. Costos en Infraestructura y Equipos (Preguntas 17 y 18)", "key": "costs_equipos__completed", "render": costs_equipos.render},
    {"label": "7. Insumos Mensuales (Pregunta 19)", "key": "insumos_mensuales__completed", "render": supplies.render},
    {"label": "8. Personal del BLH (Pregunta 20)", "key": "personal_blh__completed", "render": staff.render},
    {"label": "9. Servicios Públicos (Pregunta 21)", "key": "servicios_publicos__completed", "render": utilities.render},
    {"label": "10. Transporte y Recolección (Preguntas 22 a 25)", "key": "transporte_modalidades__completed", "render": transport.render},
]

# ──────────────────────────────────────────────
# Inicializar índice de navegación
# ──────────────────────────────────────────────
total_sections = len(section_definitions)
if "section_index" not in st.session_state or not isinstance(st.session_state.section_index, int):
    st.session_state.section_index = 0
elif st.session_state.section_index < 0:
    st.session_state.section_index = 0
elif st.session_state.section_index >= total_sections:
    st.session_state.section_index = total_sections - 1

current_section = section_definitions[st.session_state.section_index]

# ──────────────────────────────────────────────
# Validación de identificación antes de avanzar
# ──────────────────────────────────────────────
if st.session_state.section_index > 1:
    if "identificacion" not in st.session_state or not st.session_state["identificacion"].get("ips_id", "").strip():
        st.warning("⚠️ Por favor complete la sección de **Identificación de la IPS** antes de continuar.")
        st.session_state.section_index = 1
        st.rerun()

# ──────────────────────────────────────────────
# Cargar datos previos si existen (una vez)
# ──────────────────────────────────────────────
if st.session_state.get("identificacion") and not st.session_state.get("data_loaded", False):
    ips_id = st.session_state["identificacion"].get("ips_id", "").strip().lower()
    if ips_id:
        existing_data = load_existing_data(ips_id)
        if existing_data:
            excluded_keys = {
                "ips_id_input", "correo_responsable_input",
                "nombre_responsable_input", "cargo_responsable_input",
                "telefono_responsable_input"
            }
            clean_data = {k: v for k, v in existing_data.items() if k not in excluded_keys and not k.startswith("FormSubmitter:")}
            st.session_state.update(clean_data)
            st.info(f"📂 Datos restaurados para la IPS: `{ips_id}`.")
        else:
            st.info("🆕 No se encontraron datos anteriores para esta IPS.")
        st.session_state["data_loaded"] = True
        st.rerun()

# ──────────────────────────────────────────────
# Renderizar sección actual
# ──────────────────────────────────────────────
current_section["render"]()

# ──────────────────────────────────────────────
# Navegación lateral
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📑 Navegación")
    status_labels = [
        f"{'✅' if (section['key'] and st.session_state.get(section['key'], False)) else '🔲'} {section['label']}"
        for section in section_definitions
    ]
    selected = st.selectbox("Ir a sección:", status_labels, index=st.session_state.section_index)
    new_index = next(i for i, section in enumerate(section_definitions) if section['label'] in selected)
    if new_index != st.session_state.section_index:
        st.session_state.section_index = new_index
        st.rerun()

# ──────────────────────────────────────────────
# Barra de progreso
# ──────────────────────────────────────────────
tracked_flags = [s["key"] for s in section_definitions if s["key"]]
completed_count, progress_percent = compute_progress(st.session_state, tracked_flags)
st.progress(progress_percent, text=f"🔄 Progreso: {completed_count} de {len(tracked_flags)} secciones completadas")

# ──────────────────────────────────────────────
# Botones de navegación entre secciones
# ──────────────────────────────────────────────
col1, col2, _ = st.columns([1, 1, 6])
with col1:
    if st.session_state.section_index > 0:
        if st.button("⬅️ Sección anterior"):
            st.session_state.section_index -= 1
            st.rerun()
with col2:
    if st.session_state.section_index < total_sections - 1:
        if st.button("➡️ Siguiente sección"):
            st.session_state.section_index += 1
            st.rerun()

# ──────────────────────────────────────────────
# Finalización del formulario
# ──────────────────────────────────────────────
if st.session_state.section_index == total_sections - 1:
    st.success("🎉 Ha llegado al final del formulario.")
    if st.button("⬅️ Volver al inicio"):
        st.session_state.section_index = 0
        st.rerun()

# ──────────────────────────────────────────────
# Exportación final
# ──────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📤 Exportar Encuesta Completa")

if st.button("Guardar encuesta en Google Sheets y respaldo local"):
    flat_data = flatten_session_state(st.session_state)
    success = append_or_update_row(flat_data)
    ips_name = st.session_state.get("identificacion", {}).get("ips_id", "IPS desconocida")
    if success:
        st.success(f"✅ Respuestas de `{ips_name}` guardadas exitosamente.")
    else:
        st.error("❌ Error al guardar los datos. Intente nuevamente.")

# ──────────────────────────────────────────────
# Pie de página (siempre visible)
# ──────────────────────────────────────────────
render_footer()
