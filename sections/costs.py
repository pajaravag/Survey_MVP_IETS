import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box, render_box

# ──────────────────────────────────────────────
# 🔐 Safe helpers
# ──────────────────────────────────────────────
def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def format_cop(value):
    try:
        return f"{float(value):,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return "NA"

# ──────────────────────────────────────────────
# Render function
# ──────────────────────────────────────────────
def render():
    st.header("5. 💸 Costos por Proceso del Banco de Leche Humana (Preguntas 17 y 18)")

    prefix = "costos_blh__"
    completion_flag = prefix + "completed"

    prev_costos = st.session_state.get(prefix + "costos", {})
    prev_actividades = st.session_state.get(prefix + "actividades", {})

    # Instrucciones
    st.markdown(render_info_box("""
**ℹ️ ¿Qué debe registrar?**  
Esta sección solicita el **costo mensual estimado** y las **actividades realizadas** por cada proceso del Banco de Leche Humana (BLH).  

- Si un proceso **no se realiza**, registre el valor **cero (0)** y escriba **“NA”** en actividades.  
- Todos los valores deben expresarse en **pesos colombianos (COP)**.  
"""), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**

| Proceso                              | Costo mensual (COP) | Actividades realizadas                                           |
|--------------------------------------|----------------------|------------------------------------------------------------------|
| Captación, selección y acompañamiento de usuarias | 1.200.000            | Llamadas, visitas domiciliarias, seguimiento nutricional         |
| Extracción y conservación            | 850.000              | Preparación, extracción con extractor eléctrico, etiquetado      |
| Transporte                           | 300.000              | Traslado de leche desde IPS externas al banco                    |
| Control microbiológico               | 500.000              | Toma y siembra de muestras, lectura de resultados                |
| Distribución                         | 600.000              | Embalaje, entrega en servicios hospitalarios, registro de entrega|
"""), unsafe_allow_html=True)

    # Procesos estándar
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

    # Inicializar contenedores
    costos_data = {}
    actividades_data = {}
    resumen_tabla = []

    with st.form("form_costos_blh"):
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
                    f"Actividades realizadas (o escriba 'NA') - {proceso}",
                    value=prev_actividades.get(proceso, ""),
                    key=f"{prefix}actividad_{i}"
                )

            # Guardar internamente
            costos_data[proceso] = costo
            actividades_data[proceso] = actividad.strip() if actividad.strip() else "NA"

            resumen_tabla.append({
                "Proceso": proceso,
                "Costo mensual (COP)": format_cop(costo),
                "Actividades": actividades_data[proceso]
            })

        submitted = st.form_submit_button("💾 Guardar sección - Costos por Proceso")

    # Guardar estado y exportar si se envió el formulario
    if submitted:
        is_complete = any(v > 0 for v in costos_data.values())
        st.session_state[prefix + "costos"] = costos_data
        st.session_state[prefix + "actividades"] = actividades_data
        st.session_state[completion_flag] = is_complete

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Costos por proceso guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 11:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")

    # Tabla resumen siempre visible
    if resumen_tabla:
        st.markdown("### 📋 Resumen de Costos y Actividades")
        st.table(resumen_tabla)
