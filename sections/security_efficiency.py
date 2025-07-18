import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box

# 🔐 Safe conversion helpers
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

    # ──────────────────────────────────────────────
    # Estado
    # ──────────────────────────────────────────────
    prefix = "seguridad_eficiencia__"
    completion_flag = prefix + "completed"
    data = st.session_state

    # ──────────────────────────────────────────────
    # Pregunta 14 - Control microbiológico
    # ──────────────────────────────────────────────
    st.subheader("1️⃣4️⃣ ¿Se realiza control microbiológico?")
    options = ["Sí", "No", "No aplica"]
    selected_option = data.get(prefix + "control_microbiologico", "No")
    index = safe_radio_index(options, selected_option)

    control_microbiologico = st.radio(
        "Por favor indique si su institución realiza control microbiológico:",
        options,
        index=index,
        horizontal=True,
        key=prefix + "control_microbiologico_radio"
    )
    st.session_state[prefix + "control_microbiologico"] = control_microbiologico

    # ──────────────────────────────────────────────
    # Formulario principal
    # ──────────────────────────────────────────────
    with st.form("seguridad_eficiencia_form"):
        volumen_estandares = st.number_input(
            "1️⃣1️⃣ Volumen promedio de leche descartada por no cumplir estándares (ml):",
            min_value=0.0,
            step=1.0,
            value=safe_float(data.get(prefix + "volumen_estandares", 0.0), min_val=0.0),
            help="Si no se descarta leche, registre 0."
        )

        volumen_vencimiento = st.number_input(
            "1️⃣2️⃣ Volumen promedio de leche descartada por vencimiento (ml):",
            min_value=0.0,
            step=1.0,
            value=safe_float(data.get(prefix + "volumen_vencimiento", 0.0), min_val=0.0),
            help="Si no se descarta leche por vencimiento, registre 0."
        )

        tiempo_distribucion = st.number_input(
            "1️⃣3️⃣ Tiempo promedio desde la recolección hasta la distribución (días):",
            min_value=1,
            step=1,
            value=safe_int(data.get(prefix + "tiempo_distribucion", 1), min_val=1),
            help="Si es menor a un día, registre 1."
        )

        descripcion_control = ""
        if control_microbiologico == "Sí":
            st.subheader("1️⃣5️⃣ Describa el proceso de control microbiológico:")
            descripcion_control = st.text_area(
                "Por favor describa el proceso: técnicas, frecuencia, tipos de análisis, estándares, etc.",
                value=data.get(prefix + "descripcion_control", ""),
                key=prefix + "descripcion_control_textarea"
            )
        else:
            descripcion_control = "NA"

        # ✅ Botón de envío debe ir dentro del form
        submitted = st.form_submit_button("💾 Guardar sección - Seguridad y Eficiencia")

    # ──────────────────────────────────────────────
    # Guardado final
    # ──────────────────────────────────────────────
    if submitted:
        st.session_state[prefix + "volumen_estandares"] = volumen_estandares
        st.session_state[prefix + "volumen_vencimiento"] = volumen_vencimiento
        st.session_state[prefix + "tiempo_distribucion"] = tiempo_distribucion
        st.session_state[prefix + "descripcion_control"] = descripcion_control
        st.session_state[completion_flag] = True

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Sección de Seguridad y Eficiencia guardada correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 10:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
