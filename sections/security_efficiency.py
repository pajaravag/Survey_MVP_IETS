import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import safe_save_section, load_existing_data
from utils.ui_styles import render_info_box, render_compact_example_box
from utils.constants import MINIMUM_HEADERS_BY_SECTION

SECTION_PREFIX = "seguridad_eficiencia__"
SHEET_NAME = "Seguridad_Eficiencia"
COMPLETION_KEY = SECTION_PREFIX + "completed"
DATA_LOADED_KEY = SECTION_PREFIX + "data_loaded"

def safe_int(value, default=1, min_val=1):
    try:
        result = int(float(value))
        return max(result, min_val)
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0, min_val=0.0):
    try:
        result = float(value)
        return max(result, min_val)
    except (ValueError, TypeError):
        return default

def safe_radio_index(options, value, fallback="No"):
    clean_value = str(value).strip()
    return options.index(clean_value) if clean_value in options else options.index(fallback)

def render():
    st.header("4. 🔐 Seguridad y Eficiencia del Banco de Leche Humana (Preguntas 11 a 16)")

    # ──────────────────────────────────────────────
    # Introducción
    # ──────────────────────────────────────────────
    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
En esta sección se solicitará información cuantitativa relacionada con la **seguridad y eficiencia** de los procesos de recolección, almacenamiento y distribución de leche humana.  
Si algún ítem no aplica a su institución, deberá registrar el valor **cero (0)** y continuar con el formulario.  
Para los volúmenes con decimales, utilice una **coma** como separador decimal (por ejemplo: 250,5).
"""), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**  
- Leche descartada por estándares: **10 ml**  
- Leche descartada por vencimiento: **0 ml**  
- Tiempo promedio: **2 días**  
- Control microbiológico: **Sí**  
- Descripción: *Control antes y después de la pasteurización con pruebas de cultivo.*
"""), unsafe_allow_html=True)

    # Estado y precarga segura
    data_loaded = st.session_state.get(DATA_LOADED_KEY, False)
    id_field = st.session_state.get("identificacion", {}).get("ips_id", "")

    def safe_get(field):
        val = st.session_state.get(f"{SECTION_PREFIX}{field}", "")
        return val if isinstance(val, (str, float, int)) or val is None else ""

    # Precarga: solo si hace falta
    if id_field and not data_loaded:
        loaded_data = load_existing_data(id_field, sheet_name=SHEET_NAME)
        if loaded_data:
            for k, v in loaded_data.items():
                widget_key = f"{SECTION_PREFIX}{k}"
                if widget_key not in st.session_state:
                    st.session_state[widget_key] = v if isinstance(v, (str, float, int)) or v is None else str(v)
            st.session_state[DATA_LOADED_KEY] = True
            st.rerun()

    # Pregunta 14 - Control microbiológico
    st.subheader("1️⃣4️⃣ ¿Se realiza control microbiológico?")
    options = ["Sí", "No", "No aplica"]
    selected_option = safe_get("control_microbiologico") or "No"
    index = safe_radio_index(options, selected_option)

    control_microbiologico = st.radio(
        "Por favor indique si su institución realiza control microbiológico:",
        options,
        index=index,
        horizontal=True,
        key=SECTION_PREFIX + "control_microbiologico_radio"
    )
    st.session_state[SECTION_PREFIX + "control_microbiologico"] = control_microbiologico

    # Formulario principal
    with st.form("seguridad_eficiencia_form"):
        volumen_estandares = st.number_input(
            "1️⃣1️⃣ Volumen promedio de leche descartada por no cumplir estándares (ml):",
            min_value=0.0,
            step=1.0,
            value=safe_float(safe_get("volumen_estandares"), 0.0),
            key=SECTION_PREFIX + "volumen_estandares",
            help="Si no se descarta leche, registre 0."
        )

        volumen_vencimiento = st.number_input(
            "1️⃣2️⃣ Volumen promedio de leche descartada por vencimiento (ml):",
            min_value=0.0,
            step=1.0,
            value=safe_float(safe_get("volumen_vencimiento"), 0.0),
            key=SECTION_PREFIX + "volumen_vencimiento",
            help="Si no se descarta leche por vencimiento, registre 0."
        )

        tiempo_distribucion = st.number_input(
            "1️⃣3️⃣ Tiempo promedio desde la recolección hasta la distribución (días):",
            min_value=1,
            step=1,
            value=safe_int(safe_get("tiempo_distribucion"), 1),
            key=SECTION_PREFIX + "tiempo_distribucion",
            help="Si es menor a un día, registre 1."
        )

        descripcion_control = ""
        if control_microbiologico == "Sí":
            st.subheader("1️⃣5️⃣ Describa el proceso de control microbiológico:")
            descripcion_control = st.text_area(
                "Por favor describa el proceso: técnicas, frecuencia, tipos de análisis, estándares, etc.",
                value=safe_get("descripcion_control"),
                key=SECTION_PREFIX + "descripcion_control"
            )
        else:
            descripcion_control = "NA"

        submitted = st.form_submit_button("💾 Guardar sección - Seguridad y Eficiencia")

    # Guardado final
    if submitted:
        # Validación de campos mínimos (según constants.py)
        errores = []
        campos_requeridos = MINIMUM_HEADERS_BY_SECTION.get(SECTION_PREFIX, [])
        flat_data = flatten_session_state(prefix=SECTION_PREFIX)

        # Parche clave: si la pregunta está inactiva, forzamos "NA" sólo en flat_data
        if control_microbiologico != "Sí":
            flat_data["descripcion_control"] = "NA"

        for campo in campos_requeridos:
            valor = flat_data.get(campo)
            if valor in [None, "", [], {}]:
                errores.append(f"- `{campo}` es obligatorio.")

        if errores:
            st.warning("⚠️ Por favor corrija los siguientes errores:")
            for err in errores:
                st.markdown(err)
        else:
            success = safe_save_section(
                id_field=id_field,
                section_prefix=SECTION_PREFIX,
                sheet_name=SHEET_NAME
            )
            if success:
                st.success("✅ Sección de Seguridad y Eficiencia guardada correctamente.")
                st.session_state[COMPLETION_KEY] = True
                st.session_state[DATA_LOADED_KEY] = False
                st.session_state.section_index += 1
                st.rerun()
            else:
                st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")

