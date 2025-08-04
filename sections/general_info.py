import streamlit as st
from utils.ui_styles import (
    render_info_box,
    render_data_protection_box,
    render_compact_example_box
)
from utils.sheet_io import safe_save_section, load_existing_data
from utils.constants import MINIMUM_HEADERS_BY_SECTION
from utils.state_manager import flatten_session_state, get_current_ips_id, get_current_ips_nombre

SECTION_PREFIX = "datos_generales__"
SHEET_NAME = "Datos_Generales"
COMPLETION_KEY = SECTION_PREFIX + "completed"

# ---- Utilidad para checkboxes
def parse_checkbox_value(v):
    return v is True or v == 'True' or v == 1 or v == '1'

def render():
    st.header("2. 📋 Datos Generales del Banco de Leche Humana (Preguntas 1 a 4)")

    procesos_key = "procesos_estandarizados"
    otros_key = "otros_procesos"
    data_loaded_key = SECTION_PREFIX + "data_loaded"

    # Validación robusta de identificador único antes de cualquier acción
    id_field = get_current_ips_id()
    if not id_field:
        st.warning("⚠️ Debe identificar primero su IPS antes de continuar. Complete la sección anterior.", icon="⚠️")
        st.stop()

    # Obtener el nombre oficial validado
    nombre_inst_oficial = get_current_ips_nombre()
    disable_nombre = bool(nombre_inst_oficial)

    # Pre-carga segura (solo una vez por sesión) y lógica de checkboxes
    data_loaded = st.session_state.get(data_loaded_key, False)
    def safe_get(field):
        val = st.session_state.get(f"{SECTION_PREFIX}{field}", "")
        return val if isinstance(val, (str, list)) or val is None else ""

    if id_field and not data_loaded:
        loaded_data = load_existing_data(id_field, sheet_name=SHEET_NAME)
        if loaded_data:
            for k, v in loaded_data.items():
                widget_key = f"{SECTION_PREFIX}{k}"
                if k.startswith("procesos_"):
                    st.session_state[widget_key] = parse_checkbox_value(v)
                elif widget_key not in st.session_state:
                    st.session_state[widget_key] = v if isinstance(v, (str, list)) or v is None else str(v)
            st.session_state[data_loaded_key] = True
            st.rerun()

    # Inicializa nombre_inst SOLO si no existe (evita warning)
    nombre_inst_key = SECTION_PREFIX + "nombre_inst"
    if nombre_inst_key not in st.session_state:
        st.session_state[nombre_inst_key] = nombre_inst_oficial or ""

    # Instrucciones y ejemplos
    st.markdown(render_info_box("""
**ℹ️ Objetivo de la sección**  
Esta sección busca caracterizar su institución y registrar los procesos estandarizados implementados en su Banco de Leche Humana (BLH).  
Por favor diligencie todos los campos de manera completa y precisa.
"""), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo**  
- Institución: Hospital Básico San Gabriel  
- Tipo: Hospital público  
- Año de implementación: 2008  
- Procesos: Captación, Recepción, Pasteurización
"""), unsafe_allow_html=True)

    st.markdown(render_data_protection_box("""
🔐 **Confidencialidad de la información**  
Los datos serán tratados bajo la Ley 1581 de 2012 de Habeas Data y utilizados exclusivamente para los fines autorizados por el IETS.
"""), unsafe_allow_html=True)

    # 1️⃣ Nombre de institución (oficial validado, controlado por session_state)
    st.text_input(
        "1️⃣ 🏥 Nombre completo y oficial de la institución:",
        key=nombre_inst_key,
        help="Ejemplo: Hospital Básico San Gabriel",
        disabled=disable_nombre
    )

    # 2️⃣ Tipo de institución
    tipo_inst_options = ["Hospital público", "Clínica privada", "Mixta"]
    tipo_inst_key = SECTION_PREFIX + "tipo_inst"
    if tipo_inst_key not in st.session_state:
        st.session_state[tipo_inst_key] = []

    st.multiselect(
        "2️⃣ 🏷️ Tipo de institución (marque con una “X”):",
        tipo_inst_options,
        key=tipo_inst_key,
        help="Seleccione al menos una opción que describa el tipo de institución."
    )

    # 3️⃣ Año de implementación
    anio_impl_key = SECTION_PREFIX + "anio_impl"
    if anio_impl_key not in st.session_state:
        st.session_state[anio_impl_key] = ""
    st.text_input(
        "3️⃣ 📅 Año de implementación del BLH (formato AAAA):",
        key=anio_impl_key,
        help="Ejemplo: 2008"
    )

    # 4️⃣ Procesos estandarizados (checkboxes, sin warning)
    st.subheader("4️⃣ 🔄 Procesos estandarizados realizados por su BLH")
    procesos_disponibles = [
        "Captación, Selección y Acompañamiento de Usuarias",
        "Extracción y Conservación",
        "Transporte",
        "Recepción",
        "Almacenamiento",
        "Deshielo",
        "Selección y Clasificación",
        "Reenvasado",
        "Pasteurización",
        "Control Microbiológico",
        "Distribución",
        "Seguimiento y Trazabilidad"
    ]

    seleccionados = []
    for proceso in procesos_disponibles:
        key = f"{SECTION_PREFIX}procesos_{proceso}"
        checked = st.session_state.get(key, False)
        if st.checkbox(proceso, key=key):
            seleccionados.append(proceso)
    st.session_state[SECTION_PREFIX + procesos_key] = seleccionados

    # Otros procesos
    otros_key_full = SECTION_PREFIX + otros_key
    if otros_key_full not in st.session_state:
        st.session_state[otros_key_full] = ""
    st.text_area(
        "➕ Otros procesos realizados (si aplica):",
        key=otros_key_full,
        placeholder="Describa aquí procesos adicionales no incluidos en la lista anterior."
    )

    # Botón de guardado y validación robusta
    if st.button("📏 Guardar sección - Datos Generales"):
        errores = []

        # Validación de formato del año
        anio = st.session_state.get(anio_impl_key, "")
        if anio and (not anio.isdigit() or len(anio) != 4):
            errores.append("- El año debe tener 4 dígitos (ej. 2008).")

        # Validación de procesos seleccionados u otros
        procesos = st.session_state.get(SECTION_PREFIX + procesos_key, [])
        otros = st.session_state.get(otros_key_full, "").strip()
        if not procesos and not otros:
            errores.append("- Debe registrar al menos un proceso estandarizado o describir otros.")

        # Validación de campos mínimos (según constants.py)
        campos_requeridos = MINIMUM_HEADERS_BY_SECTION.get(SECTION_PREFIX, [])
        for campo in campos_requeridos:
            valor = st.session_state.get(SECTION_PREFIX + campo)
            if valor in [None, "", [], {}]:
                errores.append(f"- `{campo}` es obligatorio.")

        if errores:
            st.warning("⚠️ Por favor corrija los siguientes errores:")
            for err in errores:
                st.markdown(err)
        else:
            # Guardar en hoja y marcar como completado
            success = safe_save_section(
                id_field=id_field,
                section_prefix=SECTION_PREFIX,
                sheet_name=SHEET_NAME
            )
            if success:
                st.success("✅ Datos generales guardados correctamente.")
                st.session_state[COMPLETION_KEY] = True
                st.session_state[data_loaded_key] = False
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
            else:
                st.error("❌ Error al guardar los datos. Por favor intente nuevamente.", icon="❌")
