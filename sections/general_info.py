import json
import streamlit as st
from utils.ui_styles import (
    render_info_box,
    render_data_protection_box,
    render_compact_example_box,
)
from utils.sheet_io import safe_save_section, load_existing_data
from utils.constants import MINIMUM_HEADERS_BY_SECTION
from utils.state_manager import (
    flatten_session_state,
    get_current_ips_id,
    get_current_ips_nombre,
)

SECTION_PREFIX = "datos_generales__"
SHEET_NAME = "Datos_Generales"
COMPLETION_KEY = SECTION_PREFIX + "completed"

# ---- Utilidades de normalización ------------------------------------------------

def parse_checkbox_value(v) -> bool:
    # True para True, 'True', 1, '1'; False para lo demás
    return v is True or v == "True" or v == 1 or v == "1"

def _to_str(v) -> str:
    if v is None:
        return ""
    if isinstance(v, (dict, list)):
        # Evita crashear text_area si viene lista desde versiones previas
        return ", ".join(map(str, v))
    return str(v)

def _to_list(v) -> list:
    if isinstance(v, list):
        return [str(x) for x in v]
    if isinstance(v, str):
        # Intenta JSON primero
        s = v.strip()
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except Exception:
            pass
        # Fallback: separar por coma
        if s:
            return [x.strip() for x in s.split(",") if x.strip()]
        return []
    if v in (None, "", 0):
        return []
    return [str(v)]

# -----------------------------------------------------------------------------

def render():
    st.header("2. 📋 Datos Generales del Banco de Leche Humana (Preguntas 1 a 4)")

    procesos_key = "procesos_estandarizados"
    otros_key = "otros_procesos"
    data_loaded_key = SECTION_PREFIX + "data_loaded"

    # Validación de IPS
    ips_id = get_current_ips_id()
    if not ips_id:
        st.warning("⚠️ Debe identificar primero su IPS antes de continuar. Complete la sección anterior.", icon="⚠️")
        st.stop()

    # Nombre oficial (bloqueado si lo conocemos)
    nombre_inst_key = SECTION_PREFIX + "nombre_inst"
    nombre_inst_oficial = get_current_ips_nombre() or ""
    if nombre_inst_key not in st.session_state:
        st.session_state[nombre_inst_key] = nombre_inst_oficial
    disable_nombre = bool(nombre_inst_oficial)

    # Precarga segura (una sola vez) con tipos estrictos por campo
    if not st.session_state.get(data_loaded_key, False):
        loaded = load_existing_data(ips_id, sheet_name=SHEET_NAME) or {}

        # nombre_inst (texto)
        if "nombre_inst" in loaded:
            st.session_state[nombre_inst_key] = _to_str(loaded["nombre_inst"]) or nombre_inst_oficial

        # tipo_inst (multiselect -> lista)
        tipo_inst_key = SECTION_PREFIX + "tipo_inst"
        if tipo_inst_key not in st.session_state:
            st.session_state[tipo_inst_key] = []
        if "tipo_inst" in loaded:
            st.session_state[tipo_inst_key] = _to_list(loaded["tipo_inst"])

        # anio_impl (texto)
        anio_impl_key = SECTION_PREFIX + "anio_impl"
        if anio_impl_key not in st.session_state:
            st.session_state[anio_impl_key] = ""
        if "anio_impl" in loaded:
            st.session_state[anio_impl_key] = _to_str(loaded["anio_impl"])

        # otros_procesos (text_area -> string SIEMPRE)
        otros_key_full = SECTION_PREFIX + otros_key
        if otros_key_full not in st.session_state:
            st.session_state[otros_key_full] = ""
        if otros_key in loaded:
            st.session_state[otros_key_full] = _to_str(loaded[otros_key])

        # checkboxes procesos_*
        for k, v in loaded.items():
            if k.startswith("procesos_"):
                st.session_state[f"{SECTION_PREFIX}{k}"] = parse_checkbox_value(v)

        st.session_state[data_loaded_key] = True
        st.rerun()

    # Instrucciones
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

    # 1️⃣ Nombre (sin value, solo key)
    st.text_input(
        "1️⃣ 🏥 Nombre completo y oficial de la institución:",
        key=nombre_inst_key,
        help="Ejemplo: Hospital Básico San Gabriel",
        disabled=disable_nombre,
    )

    # 2️⃣ Tipo de institución (multiselect)
    tipo_inst_options = ["Hospital público", "Clínica privada", "Mixta"]
    tipo_inst_key = SECTION_PREFIX + "tipo_inst"
    if tipo_inst_key not in st.session_state:
        st.session_state[tipo_inst_key] = []
    st.multiselect(
        "2️⃣ 🏷️ Tipo de institución (marque con una “X”):",
        tipo_inst_options,
        key=tipo_inst_key,
        help="Seleccione al menos una opción que describa el tipo de institución.",
    )

    # 3️⃣ Año de implementación (texto)
    anio_impl_key = SECTION_PREFIX + "anio_impl"
    if anio_impl_key not in st.session_state:
        st.session_state[anio_impl_key] = ""
    st.text_input(
        "3️⃣ 📅 Año de implementación del BLH (formato AAAA):",
        key=anio_impl_key,
        help="Ejemplo: 2008",
    )

    # 4️⃣ Procesos estandarizados (checkboxes)
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
        "Seguimiento y Trazabilidad",
    ]

    seleccionados = []
    for proceso in procesos_disponibles:
        key = f"{SECTION_PREFIX}procesos_{proceso}"
        # El estado inicial ya fue normalizado en la precarga
        if st.checkbox(proceso, key=key):
            seleccionados.append(proceso)
    st.session_state[SECTION_PREFIX + procesos_key] = seleccionados

    # Otros procesos (text_area SIEMPRE con string en el estado)
    otros_key_full = SECTION_PREFIX + otros_key
    if otros_key_full not in st.session_state:
        st.session_state[otros_key_full] = ""
    st.text_area(
        "➕ Otros procesos realizados (si aplica):",
        key=otros_key_full,
        placeholder="Describa aquí procesos adicionales no incluidos en la lista anterior.",
    )

    # Guardado
    if st.button("📏 Guardar sección - Datos Generales"):
        errores = []

        # Año válido
        anio = (st.session_state.get(anio_impl_key, "") or "").strip()
        if anio and (not anio.isdigit() or len(anio) != 4):
            errores.append("- El año debe tener 4 dígitos (ej. 2008).")

        # Procesos u otros
        procesos_sel = st.session_state.get(SECTION_PREFIX + procesos_key, [])
        otros_txt = (st.session_state.get(otros_key_full, "") or "").strip()
        if not procesos_sel and not otros_txt:
            errores.append("- Debe registrar al menos un proceso estandarizado o describir otros.")

        # Campos mínimos
        for campo in MINIMUM_HEADERS_BY_SECTION.get(SECTION_PREFIX, []):
            valor = st.session_state.get(SECTION_PREFIX + campo)
            if valor in [None, "", [], {}]:
                errores.append(f"- `{campo}` es obligatorio.")

        if errores:
            st.warning("⚠️ Por favor corrija los siguientes errores:")
            for e in errores:
                st.markdown(e)
        else:
            ok = safe_save_section(
                id_field=ips_id,
                section_prefix=SECTION_PREFIX,
                sheet_name=SHEET_NAME,
            )
            if ok:
                st.success("✅ Datos generales guardados correctamente.")
                st.session_state[COMPLETION_KEY] = True
                st.session_state[data_loaded_key] = False
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
            else:
                st.error("❌ Error al guardar los datos. Por favor intente nuevamente.", icon="❌")
