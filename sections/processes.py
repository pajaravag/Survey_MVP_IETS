import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box


def render():
    st.header("2. 🔄 Procesos Estandarizados del Banco de Leche Humana (Pregunta 5)")

    # ──────────────────────────────────────────────
    # Instrucciones
    # ──────────────────────────────────────────────
    st.markdown(render_info_box("""
**ℹ️ ¿Qué debe registrar?**  
Seleccione todos los **procesos estandarizados** que actualmente se realizan en su Banco de Leche Humana (BLH).  
Si un proceso **no se realiza**, marque "NA".
"""), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**  
- Captación: ✅  
- Deshielo: ✅  
- Distribución: NA
"""), unsafe_allow_html=True)

    prefix = "procesos_estandarizados__"
    completion_flag = prefix + "completed"

    # ──────────────────────────────────────────────
    # Lista oficial de procesos
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
        "Seguimiento y trazabilidad",
        "Otros"
    ]

    estado_procesos = st.session_state.get(prefix + "data", {})
    updated_data = {}

    for proceso in procesos:
        col1, col2 = st.columns([0.6, 0.4])
        with col1:
            st.markdown(f"**{proceso}**")
        with col2:
            seleccion = st.radio(
                label="¿Se realiza este proceso?",
                options=["Sí", "No", "NA"],
                index=["Sí", "No", "NA"].index(
                    estado_procesos.get(proceso, "No")
                ),
                horizontal=True,
                key=f"{prefix}_{proceso}"
            )
            updated_data[proceso] = seleccion

    st.session_state[completion_flag] = True  # Siempre completado (no se fuerza valor positivo)

    # ──────────────────────────────────────────────
    # Botón de guardado
    # ──────────────────────────────────────────────
    if st.button("📂 Guardar sección - Procesos Estandarizados"):
        st.session_state[prefix + "data"] = updated_data

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Procesos estandarizados guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
