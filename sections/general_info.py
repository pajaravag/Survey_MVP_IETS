import streamlit as st
from utils.sheet_io import append_or_update_row
from utils.state_manager import flatten_session_state


def render():
    st.header("1. Datos Generales del Banco de Leche Humana")

    st.markdown("""
    > ℹ️ **Instrucciones:**  
    Por favor complete los siguientes datos generales de su institución. Estos datos son esenciales para el análisis de los Bancos de Leche Humana en Colombia.

    > 🔐 **Nota:** La información aquí consignada está protegida por el derecho fundamental de **Habeas Data** (Ley 1581 de 2012) y será utilizada únicamente para los fines autorizados del estudio.
    """)

    prefix = "datos_generales__"
    completion_flag = prefix + "completed"

    # ──────────────────────────────────────────────
    # Load previous values from session_state
    # ──────────────────────────────────────────────
    nombre = st.text_input(
        "🏥 Nombre completo del establecimiento",
        value=st.session_state.get(prefix + "nombre_inst", ""),
        help="Ejemplo: Hospital Básico San Gabriel"
    )

    # Tipo de institución (checkbox múltiple como en el instructivo)
    tipo_inst_options = ["Hospital público", "Clínica privada", "Mixta"]
    tipo_inst_selected = st.multiselect(
        "🏷️ Tipo de institución (puede seleccionar más de una si aplica)",
        tipo_inst_options,
        default=st.session_state.get(prefix + "tipo_inst", [])
    )

    # Año de implementación BLH
    anio_impl = st.text_input(
        "📅 Año de implementación del Banco de Leche Humana (formato AAAA)",
        value=st.session_state.get(prefix + "anio_impl", ""),
        help="Ejemplo: 2008"
    )

    # ──────────────────────────────────────────────
    # Save button with validation
    # ──────────────────────────────────────────────
    if st.button("💾 Guardar sección - Datos Generales"):
        errors = []
        if not nombre.strip():
            errors.append("nombre del establecimiento")
        if not tipo_inst_selected:
            errors.append("tipo de institución")
        if not anio_impl.strip() or not anio_impl.strip().isdigit() or len(anio_impl.strip()) != 4:
            errors.append("año de implementación (formato correcto: 4 dígitos)")

        if errors:
            st.warning(f"⚠️ Por favor complete o corrija los siguientes campos obligatorios: {', '.join(errors)}.")
        else:
            # Save values in session
            st.session_state[prefix + "nombre_inst"] = nombre.strip()
            st.session_state[prefix + "tipo_inst"] = tipo_inst_selected
            st.session_state[prefix + "anio_impl"] = anio_impl.strip()

            # Flag de completado solo si todo está correcto
            st.session_state[completion_flag] = True

            # Save to Google Sheets and local
            flat_data = flatten_session_state(st.session_state)
            success = append_or_update_row(flat_data)

            if success:
                st.success("✅ Datos generales guardados exitosamente.")
                if "section_index" in st.session_state and st.session_state.section_index < 9:
                    st.session_state.section_index += 1
                    st.session_state.navigation_triggered = True
                    st.rerun()
            else:
                st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")

    # ──────────────────────────────────────────────
    # Expander Debug
    # ──────────────────────────────────────────────
    with st.expander("🔍 Ver datos guardados en esta sección"):
        st.write({
            "Nombre del establecimiento": st.session_state.get(prefix + "nombre_inst", ""),
            "Tipo de institución": st.session_state.get(prefix + "tipo_inst", []),
            "Año implementación": st.session_state.get(prefix + "anio_impl", ""),
            "Sección completada": st.session_state.get(completion_flag, False)
        })
