import streamlit as st
from utils.sheet_io import append_or_update_row
from utils.state_manager import flatten_session_state

def render():
    st.markdown("### 2️⃣ Procesos Estandarizados")

    st.info("""
    Por favor seleccione todos los **procesos estandarizados** que actualmente se realizan en su Banco de Leche Humana (BLH).
    """)

    prefix = "procesos_realizados__"
    completion_flag = prefix + "completed"
    procesos_key = prefix + "data"

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

    prev_selected = st.session_state.get(procesos_key, [])

    # ✅ Live check: ensure completion flag is always up to date
    st.session_state[completion_flag] = bool(prev_selected)

    selected = []
    with st.form("procesos_form"):
        st.markdown("#### ✅ Seleccione los procesos realizados:")

        for proceso in procesos:
            checked = proceso in prev_selected
            if st.checkbox(proceso, value=checked, key=f"chk_{proceso}"):
                selected.append(proceso)

        guardar = st.form_submit_button("💾 Guardar sección - Procesos")

    if guardar:
        st.session_state[procesos_key] = selected
        st.session_state[completion_flag] = bool(selected)

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

    with st.expander("🔍 Ver procesos seleccionados"):
        st.write(st.session_state.get(procesos_key, []))
