import streamlit as st
from utils.sheet_io import append_or_update_row
from utils.state_manager import flatten_session_state
from utils.ui_styles import render_info_box, render_data_protection_box


def render():
    st.header("2. 🔄 Procesos Estandarizados del Banco de Leche Humana (BLH)")

    # ──────────────────────────────────────────────
    # Instrucciones Visuales con ayuda del instructivo (.docx)
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
    > ℹ️ **¿Qué se debe registrar en esta sección?**  
    Aquí debe seleccionar los **procesos estandarizados** que se realizan actualmente en su Banco de Leche Humana (BLH). Esta información es fundamental para comprender el alcance operativo de su institución.

    > 📝 **Ejemplo:**  
    Si su BLH realiza actividades de **pasteurización** y **control microbiológico**, debe marcar ambas opciones.

    > ➕ **Otros procesos:**  
    Si su BLH realiza procesos adicionales no listados, por favor descríbalos en el campo "Otros procesos".

    """), unsafe_allow_html=True)

    st.markdown(render_data_protection_box("""
    > 🔐 **Nota legal:**  
    Los datos recopilados están protegidos bajo la **Ley 1581 de 2012 (Habeas Data)** y se usarán exclusivamente para fines autorizados por el **IETS**.
    """), unsafe_allow_html=True)

    prefix = "procesos_realizados__"
    completion_flag = prefix + "completed"
    procesos_key = prefix + "data"
    otros_key = prefix + "otros"

    procesos = [
        "Captación, Selección y Acompañamiento de Usuarias",
        "Extracción y Conservación",
        "Transporte",
        "Recepción",
        "Almacenamiento",
        "Deshielo",
        "Selección y Clasificación",
        "Reenvasado",
        "Pasteurización",
        "Control Microbiológico",
        "Distribución",
        "Seguimiento y Trazabilidad"
    ]

    # ──────────────────────────────────────────────
    # Cargar valores previos desde session_state
    # ──────────────────────────────────────────────

    prev_selected = st.session_state.get(procesos_key, [])
    prev_otros = st.session_state.get(otros_key, "")

    with st.form("procesos_form"):
        st.markdown("#### ✅ Seleccione los procesos actualmente realizados por su BLH:")

        selected = []
        for proceso in procesos:
            checked = proceso in prev_selected
            if st.checkbox(proceso, value=checked, key=f"chk_{proceso}"):
                selected.append(proceso)

        otros_procesos = st.text_area(
            "➕ Otros procesos realizados (si aplica)",
            value=prev_otros,
            placeholder="Describa aquí cualquier proceso adicional no incluido en la lista anterior."
        )

        st.caption("_Ejemplo de otros procesos: Educación comunitaria, talleres para madres donantes._")

        guardar = st.form_submit_button("💾 Guardar sección - Procesos Estandarizados")

    # ──────────────────────────────────────────────
    # Validación y Guardado
    # ──────────────────────────────────────────────

    if guardar:
        if not selected and not otros_procesos.strip():
            st.warning("⚠️ Debe seleccionar al menos un proceso o describir un proceso en el campo 'Otros'.")
        else:
            st.session_state[procesos_key] = selected
            st.session_state[otros_key] = otros_procesos.strip()
            st.session_state[completion_flag] = True

            flat_data = flatten_session_state(st.session_state)
            success = append_or_update_row(flat_data)

            if success:
                st.success("✅ Procesos guardados correctamente.")
                if "section_index" in st.session_state and st.session_state.section_index < 9:
                    st.session_state.section_index += 1
                    st.session_state.navigation_triggered = True
                    st.rerun()
            else:
                st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")

    # ──────────────────────────────────────────────
    # Expander: Ver resumen de datos guardados
    # ──────────────────────────────────────────────

    with st.expander("🔍 Ver resumen de procesos seleccionados"):
        st.write({
            "Procesos seleccionados": st.session_state.get(procesos_key, []),
            "Otros procesos": st.session_state.get(otros_key, "")
        })
