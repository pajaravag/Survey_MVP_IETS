import streamlit as st
from utils.sheet_io import append_or_update_row
from utils.state_manager import flatten_session_state


def render():
    st.header("2. Procesos Estandarizados del Banco de Leche Humana")

    st.markdown("""
    > ℹ️ **Instrucciones:**  
    Por favor seleccione todos los **procesos estandarizados** que actualmente se realizan en su Banco de Leche Humana (BLH).  
    Si su BLH realiza algún proceso no listado, por favor indíquelo en el campo **“Otros procesos”**.

    > 🔐 **Nota:** La información está protegida por **Habeas Data** (Ley 1581 de 2012).
    """)

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
    # Load previous values from session_state
    # ──────────────────────────────────────────────
    prev_selected = st.session_state.get(procesos_key, [])
    prev_otros = st.session_state.get(otros_key, "")

    with st.form("procesos_form"):
        st.markdown("#### ✅ Seleccione los procesos realizados:")

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

        guardar = st.form_submit_button("💾 Guardar sección - Procesos")

    # ──────────────────────────────────────────────
    # Validación y guardado
    # ──────────────────────────────────────────────

    if guardar:
        if not selected and not otros_procesos.strip():
            st.warning("⚠️ Debe seleccionar al menos un proceso o indicar un proceso en el campo 'Otros'.")
        else:
            st.session_state[procesos_key] = selected
            st.session_state[otros_key] = otros_procesos.strip()
            st.session_state[completion_flag] = True

            flat_data = flatten_session_state(st.session_state)
            success = append_or_update_row(flat_data)

            if success:
                st.success("✅ Procesos guardados correctamente en Google Sheets.")
                if "section_index" in st.session_state and st.session_state.section_index < 9:
                    st.session_state.section_index += 1
                    st.session_state.navigation_triggered = True
                    st.rerun()
            else:
                st.error("❌ Error al guardar los datos. Intente nuevamente.")

    # ──────────────────────────────────────────────
    # Expander para visualizar datos guardados
    # ──────────────────────────────────────────────

    with st.expander("🔍 Ver procesos seleccionados"):
        st.write({
            "Procesos seleccionados": st.session_state.get(procesos_key, []),
            "Otros procesos": st.session_state.get(otros_key, "")
        })
