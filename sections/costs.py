import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box

# 🔐 Safe conversion helper
def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def render():
    st.header("5. 💸 Costos Asociados al Proceso del Banco de Leche Humana (Preguntas 17 y 18)")

    prefix = "costos_blh__"
    completion_flag = prefix + "completed"

    prev_costos = st.session_state.get(prefix + "costos", {})
    prev_actividades = st.session_state.get(prefix + "actividades", {})

    # ──────────────────────────────────────────────
    # Introducción oficial
    # ──────────────────────────────────────────────
    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
En esta sección se solicita información relacionada con los **costos mensuales estimados** y las **actividades desarrolladas** por cada proceso del Banco de Leche Humana (BLH).  
Si algún proceso no se realiza en su institución, registre el valor **cero (0)** y escriba **NA** en actividades.

Los valores deben expresarse en **pesos colombianos (COP)**.
"""), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**

| Proceso                           | Costo mensual (COP) | Actividades                                                   |
|----------------------------------|----------------------|---------------------------------------------------------------|
| Transporte                       | 2.000.000            | Recolección en domicilios, uso de vehículo institucional      |
| Reenvasado                       | 0                    | NA                                                            |
"""), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Lista de procesos definidos por el instructivo
    # ──────────────────────────────────────────────
    procesos = [
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

    # ──────────────────────────────────────────────
    # Captura de datos
    # ──────────────────────────────────────────────
    costos_data = {}
    actividades_data = {}
    resumen_tabla = []

    for i, proceso in enumerate(procesos):
        col1, col2, col3 = st.columns([3, 2, 5])

        with col1:
            st.markdown(f"**{proceso}**")

        with col2:
            costo = st.number_input(
                f"Costo mensual (COP) - {proceso}",
                min_value=0.0,
                step=1000.0,
                value=safe_float(prev_costos.get(proceso, 0.0)),
                key=f"{prefix}costo_{i}"
            )

        with col3:
            actividad = st.text_input(
                f"Actividades o NA - {proceso}",
                value=prev_actividades.get(proceso, ""),
                key=f"{prefix}actividad_{i}"
            )

        costos_data[proceso] = costo
        actividades_data[proceso] = actividad.strip() or "NA"

        resumen_tabla.append({
            "Proceso": proceso,
            "Costo mensual (COP)": f"{costo:,.0f}".replace(",", "."),
            "Actividades": actividad.strip() or "NA"
        })

    # ──────────────────────────────────────────────
    # Tabla resumen
    # ──────────────────────────────────────────────
    st.markdown("### 📋 Resumen de Costos y Actividades")
    st.table(resumen_tabla)

    # ──────────────────────────────────────────────
    # Validación de completitud
    # ──────────────────────────────────────────────
    is_complete = any(v > 0 for v in costos_data.values())
    st.session_state[completion_flag] = is_complete

    # ──────────────────────────────────────────────
    # Botón de guardado
    # ──────────────────────────────────────────────
    if st.button("💾 Guardar sección - Costos por Proceso"):
        st.session_state[prefix + "costos"] = costos_data
        st.session_state[prefix + "actividades"] = actividades_data
        st.session_state[completion_flag] = is_complete

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Costos y actividades guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 10:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
