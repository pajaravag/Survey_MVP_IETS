import streamlit as st
from utils.state_manager import flatten_session_state, get_current_ips_id, get_current_ips_nombre
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

    # Mostrar nombre oficial de la IPS validada
    nombre_inst_oficial = get_current_ips_nombre()
    nombre_key = SECTION_PREFIX + "nombre_inst"
    if nombre_key not in st.session_state:
        st.session_state[nombre_key] = nombre_inst_oficial or ""
    st.text_input(
        "🏥 Nombre completo y oficial de la institución:",
        key=nombre_key,
        disabled=True
    )

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
    id_field = get_current_ips_id()  # Usa el getter robusto

    def safe_get(field, default=None):
        val = st.session_state.get(f"{SECTION_PREFIX}{field}", default)
        return val if isinstance(val, (str, float, int)) or val is None else default

    # Inicialización robusta de claves antes de renderizar los widgets
    initial_fields = {
        "donantes_mes": 0,
        "vol_inst": 0.0,
        "vol_dom": 0.0,
        "vol_centros": 0.0,
        "receptores_mes": 0,
        "volumen_pasteurizada": 0.0,
        "leche_distribuida": 0.0,
        "pasteuriza": "No",
    }
    for field, default in initial_fields.items():
        k = f"{SECTION_PREFIX}{field}"
        if k not in st.session_state:
            st.session_state[k] = default

    if id_field and not data_loaded:
        loaded_data = load_existing_data(id_field, sheet_name=SHEET_NAME)
        if loaded_data:
            for k, v in loaded_data.items():
                widget_key = f"{SECTION_PREFIX}{k}"
                # No sobreescribir si ya existe (preferir session_state en memoria)
                if widget_key not in st.session_state:
                    st.session_state[widget_key] = v if isinstance(v, (str, float, int)) or v is None else str(v)
            st.session_state[DATA_LOADED_KEY] = True
            st.rerun()

    # Pregunta 8 - Confirmación de pasteurización
    st.subheader("8️⃣ ¿En su institución se realiza pasteurización de la leche humana?")
    pasteuriza_key = f"{SECTION_PREFIX}pasteuriza"
    pasteuriza_val = st.session_state.get(pasteuriza_key, "No")
    pasteuriza_radio_key = f"{SECTION_PREFIX}pasteuriza_radio"
    if pasteuriza_radio_key not in st.session_state:
        st.session_state[pasteuriza_radio_key] = 0 if pasteuriza_val == "Sí" else 1

    pasteuriza = st.radio(
        "Por favor confirme si este proceso se lleva a cabo:",
        options=["Sí", "No"],
        index=0 if st.session_state[pasteuriza_radio_key] == 0 else 1,
        horizontal=True,
        key=pasteuriza_radio_key
    )
    st.session_state[pasteuriza_key] = "Sí" if pasteuriza == "Sí" else "No"

    with st.form("donantes_form"):
        # Pregunta 5
        donantes_mes_key = f"{SECTION_PREFIX}donantes_mes"
        st.subheader("5️⃣ Número promedio de donantes activas por mes:")
        st.number_input(
            "Número promedio mensual de donantes activas:",
            min_value=0,
            key=donantes_mes_key,
            help="Ejemplo: 120"
        )

        # Pregunta 6
        st.subheader("6️⃣ Volumen promedio mensual de leche recolectada (mililitros):")
        col1, col2 = st.columns(2)
        with col1:
            st.number_input(
                "Institución donde se encuentra el BLH (ml):",
                min_value=0.0,
                key=f"{SECTION_PREFIX}vol_inst",
                step=1.0
            )
        with col2:
            st.number_input(
                "Domicilio de la donante (ml):",
                min_value=0.0,
                key=f"{SECTION_PREFIX}vol_dom",
                step=1.0
            )
        st.number_input(
            "Centros externos a la institución (ml):",
            min_value=0.0,
            key=f"{SECTION_PREFIX}vol_centros",
            step=1.0
        )
        inst_ml = st.session_state[f"{SECTION_PREFIX}vol_inst"]
        dom_ml = st.session_state[f"{SECTION_PREFIX}vol_dom"]
        centros_ml = st.session_state[f"{SECTION_PREFIX}vol_centros"]
        total_volumen = inst_ml + dom_ml + centros_ml
        st.info(f"🔢 Volumen total recolectado: **{total_volumen:,.1f} ml**")

        # Pregunta 7
        st.subheader("7️⃣ Número promedio de receptores activos por mes:")
        st.number_input(
            "Número promedio mensual de receptores:",
            min_value=0,
            key=f"{SECTION_PREFIX}receptores_mes",
            help="Ejemplo: 90"
        )

        # Pregunta 9 (Condicional)
        volumen_pasteurizada_ml = 0.0
        if st.session_state[pasteuriza_key] == "Sí":
            st.subheader("9️⃣ Volumen promedio mensual de leche pasteurizada (ml):")
            st.number_input(
                "Ingrese el volumen mensual de leche pasteurizada:",
                min_value=0.0,
                key=f"{SECTION_PREFIX}volumen_pasteurizada",
                step=10.0,
                help="Ejemplo: 6.000 ml"
            )
            volumen_pasteurizada_ml = st.session_state[f"{SECTION_PREFIX}volumen_pasteurizada"]
        else:
            st.info("🧪 Su institución indicó que **no realiza pasteurización**, por lo tanto no debe completar esta pregunta.")

        # Pregunta 10
        st.subheader("🔟 Volumen promedio mensual de leche distribuida (mililitros):")
        st.number_input(
            "Volumen promedio mensual de leche distribuida (ml):",
            min_value=0.0,
            key=f"{SECTION_PREFIX}leche_distribuida",
            step=10.0,
            help="Ejemplo: 7.500 ml"
        )
        leche_distribuida_ml = st.session_state[f"{SECTION_PREFIX}leche_distribuida"]

        submitted = st.form_submit_button("💾 Guardar sección - Donantes y Receptores")

    if submitted:
        # Validaciones (puedes expandir según necesidad de la sección)
        errores = []
        donantes_mes = st.session_state[donantes_mes_key]
        receptores_mes = st.session_state[f"{SECTION_PREFIX}receptores_mes"]
        if donantes_mes < 0:
            errores.append("- El número de donantes activas debe ser 0 o mayor.")
        if total_volumen < 0:
            errores.append("- El volumen recolectado no puede ser negativo.")
        if receptores_mes < 0:
            errores.append("- El número de receptores debe ser 0 o mayor.")
        if st.session_state[pasteuriza_key] == "Sí" and volumen_pasteurizada_ml < 0:
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
