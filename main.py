import streamlit as st

# ──────────────────────────────────────────────
# Import Local Modules (actualizados y corregidos)
# ──────────────────────────────────────────────

from sections import (
    identification, general_info, donors_recipients,
    security_efficiency, costs, supplies,
    staff, utilities, transport, depreciation
)

from utils.state_manager import compute_progress, flatten_session_state
from utils.sheet_io import load_existing_data, append_or_update_row
from utils.ui_styles import render_info_box
from utils.ui_layout import render_header, render_footer

# ──────────────────────────────────────────────
# Page Configuration
# ──────────────────────────────────────────────

st.set_page_config(page_title="Encuesta BLH", layout="wide")
render_header()

# ──────────────────────────────────────────────
# Introducción Oficial IETS
# ──────────────────────────────────────────────

intro_markdown = """
**El Instituto de Evaluación Tecnológica en Salud (IETS)** adelanta esta encuesta para estimar los costos asociados al suministro de leche humana en Colombia, incluyendo infraestructura, equipos, insumos, personal y transporte.  
Este estudio se desarrolla en el marco de la **Ley 2361 de 2024** y los **Lineamientos Técnicos de la Estrategia de Bancos de Leche Humana**.

Toda la información será tratada con **estricta confidencialidad** y los resultados se presentarán de forma **agregada y anonimizada**.

*Agradecemos su participación, fundamental para fortalecer esta estrategia nacional de salud pública.*

*Nota: La información compartida se encuentra protegida por el derecho fundamental de **Habeas Data** (Ley 1581 de 2012). Su uso debe hacerse en cumplimiento de la garantía de dicho derecho y para los fines estrictamente autorizados.*
"""
st.markdown(render_info_box(intro_markdown), unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Definición de Secciones (Preguntas 1 a 22)
# ──────────────────────────────────────────────

section_definitions = [
    {"label": "1. Datos Generales del Banco de Leche Humana (Preguntas 1 a 5)", "key": "datos_generales__completed", "render": general_info.render},
    {"label": "2. Donantes y Receptores (Preguntas 6 a 10)", "key": "donantes_receptores__completed", "render": donors_recipients.render},
    {"label": "3. Seguridad y Eficiencia (Preguntas 11 a 15)", "key": "seguridad_eficiencia__completed", "render": security_efficiency.render},
    {"label": "4. Costos Asociados al Proceso BLH (Preguntas 16 a 17)", "key": "costos_blh__completed", "render": costs.render},
    {"label": "5. Insumos Mensuales (Pregunta 18)", "key": "insumos_mensuales__completed", "render": supplies.render},
    {"label": "6. Personal del Banco de Leche Humana (Pregunta 19)", "key": "personal_blh__completed", "render": staff.render},
    {"label": "7. Servicios Públicos (Pregunta 20)", "key": "servicios_publicos__completed", "render": utilities.render},
    {"label": "8. Transporte y Recolección (Pregunta 21)", "key": "transporte_modalidades__completed", "render": transport.render},
    {"label": "9. Depreciación e Impuestos (Pregunta 22)", "key": "depreciacion__completed", "render": depreciation.render},
]

# ──────────────────────────────────────────────
# Render Identification
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
# Sidebar Navigation
# ──────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 📑 Navegación rápida")

    labels_with_status = [
        f"{'✅' if st.session_state.get(section['key'], False) else '🔲'} {section['label']}"
        for section in section_definitions
    ]

    selected_label = st.selectbox("Ir a sección:", labels_with_status, index=st.session_state.section_index)
    selected_index = next(i for i, s in enumerate(section_definitions) if s["label"] in selected_label)

    if selected_index != st.session_state.section_index:
        st.session_state.section_index = selected_index
        st.rerun()

# ──────────────────────────────────────────────
# Render Current Section
# ──────────────────────────────────────────────

current_section = section_definitions[st.session_state.section_index]
current_section["render"]()

# ──────────────────────────────────────────────
# Progress Bar
# ──────────────────────────────────────────────

completed_count, progress_percent = compute_progress(st.session_state, [s["key"] for s in section_definitions])

st.progress(progress_percent, text=f"🔄 Progreso: {completed_count} de {len(section_definitions)} secciones completadas")

# ──────────────────────────────────────────────
# Navigation Buttons
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
# Final Confirmation and Save
# ──────────────────────────────────────────────

if st.session_state.section_index == len(section_definitions) - 1:
    st.success("🎉 Ha llegado al final del formulario. Puede revisar cualquier sección si lo desea.")
    if st.button("⬅️ Volver al inicio"):
        st.session_state.section_index = 0
        st.rerun()

st.markdown("---")
st.markdown("### 📤 Exportar Encuesta Completa")

if st.button("Guardar encuesta como CSV y Google Sheets"):
    flat_data = flatten_session_state(st.session_state)
    success = append_or_update_row(flat_data)
    ips_name = st.session_state.get("identificacion", {}).get("ips_id", "IPS desconocida")

    if success:
        st.success(f"✅ Encuesta de `{ips_name}` guardada exitosamente en respaldo.")
    else:
        st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")

st.markdown("<hr>", unsafe_allow_html=True)
render_footer()
