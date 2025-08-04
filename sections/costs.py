import streamlit as st
from utils.state_manager import flatten_session_state, get_current_ips_id, get_current_ips_nombre
from utils.sheet_io import safe_save_section, load_existing_data
from utils.ui_styles import render_info_box, render_compact_example_box
from utils.constants import MINIMUM_HEADERS_BY_SECTION

SECTION_PREFIX = "costs_blh__"
SHEET_NAME = "Costos"
COMPLETION_KEY = SECTION_PREFIX + "completed"
DATA_LOADED_KEY = SECTION_PREFIX + "data_loaded"

PROCESOS_BLH = [
    "Captación, selección y acompañamiento de usuarias",
    "Extracción y conservación",
    "Transporte",
    "Recepción",
    "Almacenamiento",
    "Deshielo",
    "Selección y clasificación",
    "Reenvasado",
    "Pasteurización",
    "Control microbiológico",
    "Distribución",
    "Seguimiento y trazabilidad"
]

def format_cop(value):
    try:
        return f"{float(value):,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "NA"

def flat_costs_dict(costos, actividades, id_field, is_complete):
    flat = {"ips_id": id_field}
    for proceso in PROCESOS_BLH:
        flat[f"costos_{proceso}"] = costos.get(proceso, 0)
        flat[f"actividades_{proceso}"] = actividades.get(proceso, "NA")
    flat[COMPLETION_KEY] = is_complete
    return flat

def render():
    st.header("5. 💸 Costos por Proceso del Banco de Leche Humana (Preguntas 17 y 18)")

    # Nombre oficial IPS
    nombre_inst_oficial = get_current_ips_nombre()
    nombre_key = SECTION_PREFIX + "nombre_inst"
    if nombre_key not in st.session_state:
        st.session_state[nombre_key] = nombre_inst_oficial or ""
    st.text_input(
        "🏥 Nombre completo y oficial de la institución:",
        key=nombre_key,
        disabled=True
    )

    st.markdown(render_info_box("""
**ℹ️ ¿Qué debe registrar?**  
Esta sección solicita el **costo mensual estimado** y las **actividades realizadas** por cada proceso del Banco de Leche Humana (BLH).  
- Si un proceso **no se realiza**, registre el valor **cero (0)** y escriba **“NA”** en actividades.  
- Todos los valores deben expresarse en **pesos colombianos (COP)**.  
"""), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**

| Proceso                              | Costo mensual (COP) | Actividades realizadas                                           |
|--------------------------------------|---------------------|------------------------------------------------------------------|
| Captación, selección y acompañamiento de usuarias | 1.200.000           | Llamadas, visitas domiciliarias, seguimiento nutricional         |
| Extracción y conservación            | 850.000             | Preparación, extracción con extractor eléctrico, etiquetado      |
| Transporte                           | 300.000             | Traslado de leche desde IPS externas al banco                    |
| Control microbiológico               | 500.000             | Toma y siembra de muestras, lectura de resultados                |
| Distribución                         | 600.000             | Embalaje, entrega en servicios hospitalarios, registro de entrega|
"""), unsafe_allow_html=True)

    # Precarga
    data_loaded = st.session_state.get(DATA_LOADED_KEY, False)
    id_field = get_current_ips_id()

    # Inicialización previa de session_state para evitar warnings
    for i, proceso in enumerate(PROCESOS_BLH):
        costo_key = f"{SECTION_PREFIX}costo_{i}"
        actividad_key = f"{SECTION_PREFIX}actividad_{i}"
        if costo_key not in st.session_state:
            st.session_state[costo_key] = 0.0
        if actividad_key not in st.session_state:
            st.session_state[actividad_key] = ""

    # Precarga desde Google Sheets (solo una vez por sesión)
    if id_field and not data_loaded:
        loaded_data = load_existing_data(id_field, sheet_name=SHEET_NAME)
        if loaded_data:
            for i, proceso in enumerate(PROCESOS_BLH):
                k_costo = f"costos_{proceso}"
                k_act = f"actividades_{proceso}"
                costo_key = f"{SECTION_PREFIX}costo_{i}"
                actividad_key = f"{SECTION_PREFIX}actividad_{i}"
                if k_costo in loaded_data:
                    st.session_state[costo_key] = float(loaded_data[k_costo])
                if k_act in loaded_data:
                    st.session_state[actividad_key] = loaded_data[k_act]
            st.session_state[DATA_LOADED_KEY] = True
            st.rerun()

    costos_data = {}
    actividades_data = {}
    resumen_tabla = []

    with st.form("form_costos_blh"):
        for i, proceso in enumerate(PROCESOS_BLH):
            col1, col2, col3 = st.columns([3, 2, 5])
            with col1:
                st.markdown(f"**{proceso}**")
            with col2:
                costo_key = f"{SECTION_PREFIX}costo_{i}"
                costo = st.number_input(
                    f"Costo mensual (COP) - {proceso}",
                    min_value=0.0,
                    step=1000.0,
                    key=costo_key
                )
            with col3:
                actividad_key = f"{SECTION_PREFIX}actividad_{i}"
                actividad = st.text_input(
                    f"Actividades realizadas (o escriba 'NA') - {proceso}",
                    key=actividad_key
                )
            costos_data[proceso] = costo
            actividades_data[proceso] = actividad.strip() or "NA"
            resumen_tabla.append({
                "Proceso": proceso,
                "Costo mensual (COP)": format_cop(costo),
                "Actividades": actividades_data[proceso]
            })
        submitted = st.form_submit_button("💾 Guardar sección - Costos por Proceso")

    if submitted:
        id_field = get_current_ips_id()
        if not id_field:
            st.error("❌ No se encontró el identificador de la IPS. Complete primero la sección de Identificación y asegúrese de no refrescar la página.")
            return

        is_complete = any(v > 0 for v in costos_data.values())
        st.session_state[SECTION_PREFIX + "costos"] = costos_data
        st.session_state[SECTION_PREFIX + "actividades"] = actividades_data
        st.session_state[COMPLETION_KEY] = is_complete

        flat_data = flat_costs_dict(costos_data, actividades_data, id_field, is_complete)

        for field in MINIMUM_HEADERS_BY_SECTION[SECTION_PREFIX]:
            if field not in flat_data:
                flat_data[field] = ""

        for k, v in flat_data.items():
            st.session_state[f"{SECTION_PREFIX}{k}"] = v

        success = safe_save_section(
            id_field=id_field,
            section_prefix=SECTION_PREFIX,
            sheet_name=SHEET_NAME
        )

        if success:
            st.success("✅ Costos por proceso guardados correctamente.")
            st.session_state[DATA_LOADED_KEY] = False
            if "section_index" in st.session_state and st.session_state.section_index < 11:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")

    if resumen_tabla:
        st.markdown("### 📋 Resumen de Costos y Actividades")
        st.table(resumen_tabla)
