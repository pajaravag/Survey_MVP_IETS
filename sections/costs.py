import streamlit as st
from utils.state_manager import flatten_session_state, get_current_ips_id
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
    """
    Devuelve un dict plano alineado con los encabezados requeridos.
    """
    flat = {"ips_id": id_field}
    for proceso in PROCESOS_BLH:
        flat[f"costos_{proceso}"] = costos.get(proceso, 0)
        flat[f"actividades_{proceso}"] = actividades.get(proceso, "NA")
    flat[COMPLETION_KEY] = is_complete
    return flat

def render():
    st.header("5. 💸 Costos por Proceso del Banco de Leche Humana (Preguntas 17 y 18)")

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

    # --- Precarga de datos si aplica ---
    data_loaded = st.session_state.get(DATA_LOADED_KEY, False)
    id_field = get_current_ips_id(st.session_state)

    def safe_get_dict(key):
        val = st.session_state.get(key, {})
        return val if isinstance(val, dict) else {}

    prev_costos = safe_get_dict(SECTION_PREFIX + "costos")
    prev_actividades = safe_get_dict(SECTION_PREFIX + "actividades")

    # Si hay datos previos en Google Sheets, precarga solo 1 vez
    if id_field and not data_loaded:
        loaded_data = load_existing_data(id_field, sheet_name=SHEET_NAME)
        if loaded_data:
            costos_recuperados = {}
            actividades_recuperadas = {}
            for proceso in PROCESOS_BLH:
                k_costo = f"costos_{proceso}"
                k_act = f"actividades_{proceso}"
                if k_costo in loaded_data:
                    costos_recuperados[proceso] = loaded_data[k_costo]
                if k_act in loaded_data:
                    actividades_recuperadas[proceso] = loaded_data[k_act]
            if costos_recuperados:
                st.session_state[SECTION_PREFIX + "costos"] = costos_recuperados
            if actividades_recuperadas:
                st.session_state[SECTION_PREFIX + "actividades"] = actividades_recuperadas
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
                costo = st.number_input(
                    f"Costo mensual (COP) - {proceso}",
                    min_value=0.0,
                    step=1000.0,
                    value=float(prev_costos.get(proceso, 0.0)),
                    key=f"{SECTION_PREFIX}costo_{i}"
                )
            with col3:
                actividad = st.text_input(
                    f"Actividades realizadas (o escriba 'NA') - {proceso}",
                    value=prev_actividades.get(proceso, ""),
                    key=f"{SECTION_PREFIX}actividad_{i}"
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
        # Obtener ips_id de forma robusta
        id_field = get_current_ips_id(st.session_state)
        if not id_field:
            st.error("❌ No se encontró el identificador de la IPS. Complete primero la sección de Identificación y asegúrese de no refrescar la página.")
            return

        is_complete = any(v > 0 for v in costos_data.values())
        st.session_state[SECTION_PREFIX + "costos"] = costos_data
        st.session_state[SECTION_PREFIX + "actividades"] = actividades_data
        st.session_state[COMPLETION_KEY] = is_complete

        # --- Dict plano alineado con MINIMUM_HEADERS_BY_SECTION ---
        flat_data = flat_costs_dict(costos_data, actividades_data, id_field, is_complete)

        # DEBUG: Visualiza en pantalla la info fundamental para diagnóstico
        #st.write("DEBUG: id_field", id_field)
        #st.write("DEBUG: flat_data", flat_data)
        #st.write("DEBUG: expected headers", MINIMUM_HEADERS_BY_SECTION[SECTION_PREFIX])

        # Añade explícitamente los campos requeridos si faltan (robustez máxima)
        for field in MINIMUM_HEADERS_BY_SECTION[SECTION_PREFIX]:
            if field not in flat_data:
                flat_data[field] = ""

        # Actualiza session_state plano para integridad modular
        for k, v in flat_data.items():
            st.session_state[f"{SECTION_PREFIX}{k}"] = v

        # ----- Intento de guardado -----
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
            # Dump para análisis
            st.write("❌ ERROR al guardar")
            st.write("DICT ENVIADO:", flat_data)
            st.write("HEADERS ESPERADOS:", MINIMUM_HEADERS_BY_SECTION[SECTION_PREFIX])
            st.write("IPS_ID:", id_field)

    if resumen_tabla:
        st.markdown("### 📋 Resumen de Costos y Actividades")
        st.table(resumen_tabla)
