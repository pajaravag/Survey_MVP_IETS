import streamlit as st
from utils.ui_styles import (
    render_info_box,
    render_data_protection_box,
    render_compact_example_box
)
from utils.sheet_io import safe_save_section, load_existing_data
from utils.constants import MINIMUM_HEADERS_BY_SECTION
from utils.state_manager import flatten_session_state

SECTION_PREFIX = "datos_generales__"
SHEET_NAME = "Datos_Generales"
COMPLETION_KEY = SECTION_PREFIX + "completed"

def render():
    st.header("2. 📋 Datos Generales del Banco de Leche Humana (Preguntas 1 a 4)")

    procesos_key = "procesos_estandarizados"
    otros_key = "otros_procesos"

    # Pre-carga segura (sólo una vez por sesión)
    data_loaded_key = SECTION_PREFIX + "data_loaded"
    data_loaded = st.session_state.get(data_loaded_key, False)
    id_field = st.session_state.get("identificacion", {}).get("ips_id", "")

    def safe_get(field):
        val = st.session_state.get(f"{SECTION_PREFIX}{field}", "")
        return val if isinstance(val, str) or isinstance(val, list) or val is None else ""

    # PRELOAD de datos si existen y aún no se ha hecho
    if id_field and not data_loaded:
        loaded_data = load_existing_data(id_field, sheet_name=SHEET_NAME)
        if loaded_data:
            for k, v in loaded_data.items():
                widget_key = f"{SECTION_PREFIX}{k}"
                if widget_key not in st.session_state:
                    st.session_state[widget_key] = v if isinstance(v, (str, list)) or v is None else str(v)
            st.session_state[data_loaded_key] = True
            st.rerun()

    # ℹ️ Instrucciones
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

    # 1️⃣ Nombre de institución
    st.text_input(
        "1️⃣ 🏥 Nombre completo y oficial de la institución:",
        key=SECTION_PREFIX + "nombre_inst",
        value=safe_get("nombre_inst"),
        help="Ejemplo: Hospital Básico San Gabriel"
    )

    # 2️⃣ Tipo de institución
    tipo_inst_options = ["Hospital público", "Clínica privada", "Mixta"]
    st.multiselect(
        "2️⃣ 🏷️ Tipo de institución (marque con una “X”):",
        tipo_inst_options,
        key=SECTION_PREFIX + "tipo_inst",
        default=safe_get("tipo_inst") if safe_get("tipo_inst") else [],
        help="Seleccione al menos una opción que describa el tipo de institución."
    )

    # 3️⃣ Año de implementación
    st.text_input(
        "3️⃣ 📅 Año de implementación del BLH (formato AAAA):",
        key=SECTION_PREFIX + "anio_impl",
        value=safe_get("anio_impl"),
        help="Ejemplo: 2008"
    )

    # 4️⃣ Procesos estandarizados
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
        if st.checkbox(proceso, key=key, value=st.session_state.get(key, False)):
            seleccionados.append(proceso)
    st.session_state[SECTION_PREFIX + procesos_key] = seleccionados

    st.text_area(
        "➕ Otros procesos realizados (si aplica):",
        key=SECTION_PREFIX + otros_key,
        value=safe_get(otros_key),
        placeholder="Describa aquí procesos adicionales no incluidos en la lista anterior."
    )

    # Botón de guardado
    if st.button("📏 Guardar sección - Datos Generales"):
        errores = []

        # Validación de formato del año
        anio = st.session_state.get(SECTION_PREFIX + "anio_impl", "")
        if anio and (not anio.isdigit() or len(anio) != 4):
            errores.append("- El año debe tener 4 dígitos (ej. 2008).")

        # Validación de procesos seleccionados u otros
        procesos = st.session_state.get(SECTION_PREFIX + procesos_key, [])
        otros = st.session_state.get(SECTION_PREFIX + otros_key, "").strip()
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
                st.rerun()
            else:
                st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
