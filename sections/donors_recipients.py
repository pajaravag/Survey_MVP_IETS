import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import safe_save_section, load_existing_data
from utils.ui_styles import render_info_box, render_compact_example_box
from utils.constants import MINIMUM_HEADERS_BY_SECTION

SECTION_PREFIX = "donantes_receptores__"
SHEET_NAME = "Donantes_Receptores"
COMPLETION_KEY = SECTION_PREFIX + "completed"
DATA_LOADED_KEY = SECTION_PREFIX + "data_loaded"

# Helpers para valores seguros
def safe_int(value, default=0):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def render():
    st.header("3. 👩‍🍼 Donantes y Receptores del Banco de Leche Humana (Preguntas 5 a 10)")

    # Instrucciones oficiales
    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
En esta sección se solicitará información cuantitativa relacionada con los donantes y receptores de leche humana.  
En caso de que algún ítem no aplique a su institución, deberá registrar el valor **cero (0)** y continuar con el llenado del formulario.
    """), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**  
- Donantes activas: 120 donantes/mes  
- Volumen recolectado: 100,8 ml (institución), 150 ml (domicilio), 0 ml (centros externos)  
- Receptores activos: 90 receptores/mes  
- Volumen pasteurizado: 6.000 ml  
- Volumen distribuido: 7.500 ml
    """), unsafe_allow_html=True)

    # --- Pre-carga segura ---
    data_loaded = st.session_state.get(DATA_LOADED_KEY, False)
    id_field = st.session_state.get("identificacion", {}).get("ips_id", "")

    def safe_get(field):
        val = st.session_state.get(f"{SECTION_PREFIX}{field}", "")
        return val if isinstance(val, (str, float, int)) or val is None else ""

    if id_field and not data_loaded:
        loaded_data = load_existing_data(id_field, sheet_name=SHEET_NAME)
        if loaded_data:
            for k, v in loaded_data.items():
                widget_key = f"{SECTION_PREFIX}{k}"
                if widget_key not in st.session_state:
                    st.session_state[widget_key] = v if isinstance(v, (str, float, int)) or v is None else str(v)
            st.session_state[DATA_LOADED_KEY] = True
            st.rerun()

    # Pregunta 8 - Confirmación de pasteurización
    st.subheader("8️⃣ ¿En su institución se realiza pasteurización de la leche humana?")
    pasteuriza = st.radio(
        "Por favor confirme si este proceso se lleva a cabo:",
        options=["Sí", "No"],
        index=0 if safe_get("pasteuriza") == "Sí" else 1,
        horizontal=True,
        key=f"{SECTION_PREFIX}pasteuriza_radio"
    )
    st.session_state[f"{SECTION_PREFIX}pasteuriza"] = pasteuriza

    with st.form("donantes_form"):
        # Pregunta 5
        st.subheader("5️⃣ Número promedio de donantes activas por mes:")
        donantes_mes = st.number_input(
            "Número promedio mensual de donantes activas:",
            min_value=0,
            value=safe_int(safe_get("donantes_mes"), 0),
            key=f"{SECTION_PREFIX}donantes_mes",
            help="Ejemplo: 120"
        )

        # Pregunta 6
        st.subheader("6️⃣ Volumen promedio mensual de leche recolectada (mililitros):")
        col1, col2 = st.columns(2)
        with col1:
            inst_ml = st.number_input(
                "Institución donde se encuentra el BLH (ml):",
                min_value=0.0,
                value=safe_float(safe_get("vol_inst"), 0.0),
                key=f"{SECTION_PREFIX}vol_inst",
                step=1.0
            )
        with col2:
            dom_ml = st.number_input(
                "Domicilio de la donante (ml):",
                min_value=0.0,
                value=safe_float(safe_get("vol_dom"), 0.0),
                key=f"{SECTION_PREFIX}vol_dom",
                step=1.0
            )
        centros_ml = st.number_input(
            "Centros externos a la institución (ml):",
            min_value=0.0,
            value=safe_float(safe_get("vol_centros"), 0.0),
            key=f"{SECTION_PREFIX}vol_centros",
            step=1.0
        )
        total_volumen = inst_ml + dom_ml + centros_ml
        st.info(f"🔢 Volumen total recolectado: **{total_volumen:,.1f} ml**")

        # Pregunta 7
        st.subheader("7️⃣ Número promedio de receptores activos por mes:")
        receptores_mes = st.number_input(
            "Número promedio mensual de receptores:",
            min_value=0,
            value=safe_int(safe_get("receptores_mes"), 0),
            key=f"{SECTION_PREFIX}receptores_mes",
            help="Ejemplo: 90"
        )

        # Pregunta 9 (Condicional)
        volumen_pasteurizada_ml = 0.0
        if pasteuriza == "Sí":
            st.subheader("9️⃣ Volumen promedio mensual de leche pasteurizada (ml):")
            volumen_pasteurizada_ml = st.number_input(
                "Ingrese el volumen mensual de leche pasteurizada:",
                min_value=0.0,
                value=safe_float(safe_get("volumen_pasteurizada"), 0.0),
                key=f"{SECTION_PREFIX}volumen_pasteurizada",
                step=10.0,
                help="Ejemplo: 6.000 ml"
            )
        else:
            st.info("🧪 Su institución indicó que **no realiza pasteurización**, por lo tanto no debe completar esta pregunta.")

        # Pregunta 10
        st.subheader("🔟 Volumen promedio mensual de leche distribuida (mililitros):")
        leche_distribuida_ml = st.number_input(
            "Volumen promedio mensual de leche distribuida (ml):",
            min_value=0.0,
            value=safe_float(safe_get("leche_distribuida"), 0.0),
            key=f"{SECTION_PREFIX}leche_distribuida",
            step=10.0,
            help="Ejemplo: 7.500 ml"
        )

        submitted = st.form_submit_button("💾 Guardar sección - Donantes y Receptores")

    if submitted:
        # Validaciones (puedes expandir según necesidad de la sección)
        errores = []
        if donantes_mes < 0:
            errores.append("- El número de donantes activas debe ser 0 o mayor.")
        if total_volumen < 0:
            errores.append("- El volumen recolectado no puede ser negativo.")
        if receptores_mes < 0:
            errores.append("- El número de receptores debe ser 0 o mayor.")
        if pasteuriza == "Sí" and volumen_pasteurizada_ml < 0:
            errores.append("- El volumen de leche pasteurizada debe ser 0 o mayor.")
        if leche_distribuida_ml < 0:
            errores.append("- El volumen de leche distribuida debe ser 0 o mayor.")

        # Validación de campos obligatorios
        campos_requeridos = MINIMUM_HEADERS_BY_SECTION.get(SECTION_PREFIX, [])
        flat_data = flatten_session_state(prefix=SECTION_PREFIX)
        for campo in campos_requeridos:
            valor = flat_data.get(campo)
            if valor in [None, "", [], {}]:
                errores.append(f"- `{campo}` es obligatorio.")

        if errores:
            st.warning("⚠️ Por favor corrija los siguientes errores:")
            for err in errores:
                st.markdown(err)
        else:
            # Guardado seguro y modular
            success = safe_save_section(
                id_field=id_field,
                section_prefix=SECTION_PREFIX,
                sheet_name=SHEET_NAME
            )
            if success:
                st.success("✅ Datos de Donantes y Receptores guardados correctamente.")
                st.session_state[COMPLETION_KEY] = True
                st.session_state[DATA_LOADED_KEY] = False
                st.session_state.section_index += 1
                st.rerun()
            else:
                st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
