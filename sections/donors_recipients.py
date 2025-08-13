import streamlit as st
from utils.state_manager import (
    flatten_session_state,
    get_current_ips_id,
    get_current_ips_nombre,
)
from utils.sheet_io import safe_save_section, load_existing_data
from utils.ui_styles import render_info_box, render_compact_example_box
from utils.constants import MINIMUM_HEADERS_BY_SECTION

SECTION_PREFIX = "donantes_receptores__"
SHEET_NAME = "Donantes_Receptores"
COMPLETION_KEY = SECTION_PREFIX + "completed"
DATA_LOADED_KEY = SECTION_PREFIX + "data_loaded"

RADIO_OPTIONS = ["Sí", "No"]

# --------------------------- Helpers ---------------------------

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

def _normalize_pasteuriza(val) -> str:
    if isinstance(val, str):
        v = val.strip().lower()
        if v in {"sí", "si", "true", "1"}: return "Sí"
        if v in {"no", "false", "0"}:       return "No"
    if isinstance(val, (int, float)):        return "Sí" if int(val) == 1 else "No"
    if isinstance(val, bool)):               return "Sí" if val else "No"
    return "No"

# ----------------------------- UI ------------------------------

def render():
    st.header("3. 👩‍🍼 Donantes y Receptores del Banco de Leche Humana (Preguntas 5 a 10)")

    ips_id = get_current_ips_id()
    if not ips_id:
        st.warning("⚠️ Debe completar la **Identificación de la IPS** antes de continuar.", icon="⚠️")
        st.stop()

    # Nombre oficial (solo lectura, sin conflicto value+key)
    nombre_key = SECTION_PREFIX + "nombre_inst"
    if nombre_key not in st.session_state:
        st.session_state[nombre_key] = get_current_ips_nombre() or ""
    st.text_input("🏥 Nombre completo y oficial de la institución:", key=nombre_key, disabled=True)

    # Instrucciones
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

    # ----------- HIDRATACIÓN (primero) desde Google Sheets -----------
    PASTEURIZA_VAL_KEY = SECTION_PREFIX + "pasteuriza"  # guardamos "Sí"/"No" aquí

    if not st.session_state.get(DATA_LOADED_KEY, False):
        loaded = load_existing_data(ips_id, sheet_name=SHEET_NAME) or {}

        # Sobreescribe SIEMPRE en la primera hidratación (tras refresh)
        st.session_state[f"{SECTION_PREFIX}donantes_mes"]        = safe_int(loaded.get("donantes_mes",        st.session_state.get(f"{SECTION_PREFIX}donantes_mes",        0)))
        st.session_state[f"{SECTION_PREFIX}vol_inst"]            = safe_float(loaded.get("vol_inst",          st.session_state.get(f"{SECTION_PREFIX}vol_inst",            0.0)))
        st.session_state[f"{SECTION_PREFIX}vol_dom"]             = safe_float(loaded.get("vol_dom",           st.session_state.get(f"{SECTION_PREFIX}vol_dom",             0.0)))
        st.session_state[f"{SECTION_PREFIX}vol_centros"]         = safe_float(loaded.get("vol_centros",       st.session_state.get(f"{SECTION_PREFIX}vol_centros",         0.0)))
        st.session_state[f"{SECTION_PREFIX}receptores_mes"]      = safe_int(  loaded.get("receptores_mes",    st.session_state.get(f"{SECTION_PREFIX}receptores_mes",      0)))
        st.session_state[f"{SECTION_PREFIX}volumen_pasteurizada"]= safe_float(loaded.get("volumen_pasteurizada", st.session_state.get(f"{SECTION_PREFIX}volumen_pasteurizada", 0.0)))
        st.session_state[f"{SECTION_PREFIX}leche_distribuida"]   = safe_float(loaded.get("leche_distribuida", st.session_state.get(f"{SECTION_PREFIX}leche_distribuida",   0.0)))
        st.session_state[PASTEURIZA_VAL_KEY] = _normalize_pasteuriza(loaded.get("pasteuriza", st.session_state.get(PASTEURIZA_VAL_KEY, "No")))

        st.session_state[DATA_LOADED_KEY] = True
        st.rerun()

    # ----------- Defaults de respaldo (solo si faltara algo) ----------
    for key, default in {
        f"{SECTION_PREFIX}donantes_mes": 0,
        f"{SECTION_PREFIX}vol_inst": 0.0,
        f"{SECTION_PREFIX}vol_dom": 0.0,
        f"{SECTION_PREFIX}vol_centros": 0.0,
        f"{SECTION_PREFIX}receptores_mes": 0,
        f"{SECTION_PREFIX}volumen_pasteurizada": 0.0,
        f"{SECTION_PREFIX}leche_distribuida": 0.0,
    }.items():
        st.session_state.setdefault(key, default)
    st.session_state.setdefault(PASTEURIZA_VAL_KEY, "No")

    # ----------- Radio SIN key (evita conflictos) ---------------------
    st.subheader("8️⃣ ¿En su institución se realiza pasteurización de la leche humana?")
    idx = RADIO_OPTIONS.index(st.session_state[PASTEURIZA_VAL_KEY]) \
        if st.session_state[PASTEURIZA_VAL_KEY] in RADIO_OPTIONS else 1
    sel = st.radio(
        "Por favor confirme si este proceso se lleva a cabo:",
        options=RADIO_OPTIONS,
        index=idx,
        horizontal=True,
    )
    st.session_state[PASTEURIZA_VAL_KEY] = sel  # persistir "Sí"/"No"

    # ------------------------- Formulario ------------------------------
    with st.form("donantes_form"):
        st.subheader("5️⃣ Número promedio de donantes activas por mes:")
        st.number_input("Número promedio mensual de donantes activas:", min_value=0,
                        key=f"{SECTION_PREFIX}donantes_mes", help="Ejemplo: 120")

        st.subheader("6️⃣ Volumen promedio mensual de leche recolectada (mililitros):")
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Institución donde se encuentra el BLH (ml):", min_value=0.0,
                            key=f"{SECTION_PREFIX}vol_inst", step=1.0)
        with col2:
            st.number_input("Domicilio de la donante (ml):", min_value=0.0,
                            key=f"{SECTION_PREFIX}vol_dom", step=1.0)
        st.number_input("Centros externos a la institución (ml):", min_value=0.0,
                        key=f"{SECTION_PREFIX}vol_centros", step=1.0)

        inst_ml    = float(st.session_state[f"{SECTION_PREFIX}vol_inst"])
        dom_ml     = float(st.session_state[f"{SECTION_PREFIX}vol_dom"])
        centros_ml = float(st.session_state[f"{SECTION_PREFIX}vol_centros"])
        total_volumen = inst_ml + dom_ml + centros_ml
        st.info(f"🔢 Volumen total recolectado: **{total_volumen:,.1f} ml**")

        st.subheader("7️⃣ Número promedio de receptores activos por mes:")
        st.number_input("Número promedio mensual de receptores:", min_value=0,
                        key=f"{SECTION_PREFIX}receptores_mes", help="Ejemplo: 90")

        volumen_pasteurizada_ml = 0.0
        if st.session_state[PASTEURIZA_VAL_KEY] == "Sí":
            st.subheader("9️⃣ Volumen promedio mensual de leche pasteurizada (ml):")
            st.number_input("Ingrese el volumen mensual de leche pasteurizada:", min_value=0.0,
                            key=f"{SECTION_PREFIX}volumen_pasteurizada", step=10.0,
                            help="Ejemplo: 6.000 ml")
            volumen_pasteurizada_ml = float(st.session_state[f"{SECTION_PREFIX}volumen_pasteurizada"])
        else:
            st.info("🧪 Su institución indicó que **no realiza pasteurización**, por lo tanto no debe completar esta pregunta.")

        st.subheader("🔟 Volumen promedio mensual de leche distribuida (mililitros):")
        st.number_input("Volumen promedio mensual de leche distribuida (ml):", min_value=0.0,
                        key=f"{SECTION_PREFIX}leche_distribuida", step=10.0,
                        help="Ejemplo: 7.500 ml")
        leche_distribuida_ml = float(st.session_state[f"{SECTION_PREFIX}leche_distribuida"])

        submitted = st.form_submit_button("💾 Guardar sección - Donantes y Receptores")

    # --------------------------- Guardado ------------------------------
    if submitted:
        errores = []
        donantes_mes   = safe_int(st.session_state[f"{SECTION_PREFIX}donantes_mes"])
        receptores_mes = safe_int(st.session_state[f"{SECTION_PREFIX}receptores_mes"])
        if donantes_mes < 0: errores.append("- El número de donantes activas debe ser 0 o mayor.")
        if total_volumen < 0: errores.append("- El volumen recolectado no puede ser negativo.")
        if receptores_mes < 0: errores.append("- El número de receptores debe ser 0 o mayor.")
        if st.session_state[PASTEURIZA_VAL_KEY] == "Sí" and volumen_pasteurizada_ml < 0:
            errores.append("- El volumen de leche pasteurizada debe ser 0 o mayor.")
        if leche_distribuida_ml < 0:
            errores.append("- El volumen de leche distribuida debe ser 0 o mayor.")

        campos_requeridos = MINIMUM_HEADERS_BY_SECTION.get(SECTION_PREFIX, [])
        flat_data = flatten_session_state(prefix=SECTION_PREFIX)
        for c in campos_requeridos:
            if flat_data.get(c) in [None, "", [], {}]:
                errores.append(f"- `{c}` es obligatorio.")

        if errores:
            st.warning("⚠️ Por favor corrija los siguientes errores:")
            for e in errores: st.markdown(e)
        else:
            ok = safe_save_section(id_field=ips_id, section_prefix=SECTION_PREFIX, sheet_name=SHEET_NAME)
            if ok:
                st.success("✅ Datos de Donantes y Receptores guardados correctamente.")
                st.session_state[COMPLETION_KEY] = True
                # Forzamos re-hidratación la próxima vez que entres a la sección
                st.session_state[DATA_LOADED_KEY] = False
                st.session_state.section_index += 1
                st.rerun()
            else:
                st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
