import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box

# 🔐 Safe conversion helpers
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
    st.header("3. 🔐 Seguridad y Eficiencia del Banco de Leche Humana (Preguntas 12 a 16)")

    # ──────────────────────────────────────────────
    # Instrucciones Oficiales
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
Por favor registre información relacionada con la **seguridad y eficiencia de los procesos de su Banco de Leche Humana (BLH)**.  
Si algún dato no aplica, registre **0** o seleccione **No aplica**.

1️⃣2️⃣ **Volumen promedio de leche descartada por no cumplir estándares al mes (ml).**  
1️⃣3️⃣ **Volumen promedio de leche descartada por vencimiento al mes (ml).**  
1️⃣4️⃣ **Tiempo promedio desde la recolección hasta la distribución (días).**  
1️⃣5️⃣ **¿Se realiza control microbiológico?**  
1️⃣6️⃣ **Descripción del control microbiológico (si aplica).**
    """), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**  
- Leche descartada por estándares: **10 ml**  
- Leche descartada por vencimiento: **0 ml**  
- Tiempo promedio recolección → distribución: **2 días**  
- Control microbiológico: **Sí**  
- Descripción: **Realizamos control microbiológico antes y después de pasteurización.**
    """), unsafe_allow_html=True)

    prefix = "seguridad_eficiencia__"
    completion_flag = prefix + "completed"

    with st.form("seguridad_eficiencia_form"):

        # Pregunta 12
        st.subheader("1️⃣2️⃣ Volumen promedio de leche descartada por no cumplir estándares (ml):")
        volumen_descartada_estandares = st.number_input(
            "Volumen mensual de leche descartada por no cumplir estándares (ml):",
            min_value=0.0, step=1.0,
            value=safe_float(st.session_state.get(prefix + "descartada_estandares", 0.0)),
            help="Si no se descarta leche, registre 0."
        )

        # Pregunta 13
        st.subheader("1️⃣3️⃣ Volumen promedio de leche descartada por vencimiento (ml):")
        volumen_descartada_vencimiento = st.number_input(
            "Volumen mensual de leche descartada por vencimiento (ml):",
            min_value=0.0, step=1.0,
            value=safe_float(st.session_state.get(prefix + "descartada_vencimiento", 0.0)),
            help="Si no se descarta leche por vencimiento, registre 0."
        )

        # Pregunta 14
        st.subheader("1️⃣4️⃣ Tiempo promedio entre recolección y distribución (días):")
        tiempo_promedio_distribucion = st.number_input(
            "Tiempo promedio desde recolección hasta distribución (en días):",
            min_value=1, step=1,
            value=safe_int(st.session_state.get(prefix + "tiempo_distribucion_dias", 1)),
            help="Si el tiempo es menor a un día, registre 1."
        )

        # Pregunta 15
        st.subheader("1️⃣5️⃣ ¿Se realiza control microbiológico?")
        control_microbiologico = st.radio(
            "¿En su BLH se realiza control microbiológico?",
            ["Sí", "No", "No aplica"],
            index=["Sí", "No", "No aplica"].index(st.session_state.get(prefix + "control_microbiologico", "No")),
            help="Seleccione la opción correspondiente."
        )

        # Pregunta 16 (Condicional)
        descripcion_control = ""
        if control_microbiologico == "Sí":
            st.subheader("1️⃣6️⃣ Describa el proceso de control microbiológico:")
            descripcion_control = st.text_area(
                "Por favor describa el proceso de control microbiológico en su institución:",
                value=st.session_state.get(prefix + "descripcion_control", ""),
                placeholder="Ejemplo: Se realiza control microbiológico antes y después de la pasteurización para asegurar calidad."
            )

        submitted = st.form_submit_button("💾 Guardar sección - Seguridad y Eficiencia")

    if submitted:
        st.session_state[prefix + "descartada_estandares"] = volumen_descartada_estandares
        st.session_state[prefix + "descartada_vencimiento"] = volumen_descartada_vencimiento
        st.session_state[prefix + "tiempo_distribucion_dias"] = tiempo_promedio_distribucion
        st.session_state[prefix + "control_microbiologico"] = control_microbiologico
        st.session_state[prefix + "descripcion_control"] = descripcion_control.strip() if control_microbiologico == "Sí" else "NA"

        st.session_state[completion_flag] = True

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de seguridad y eficiencia guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
