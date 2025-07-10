import streamlit as st
from utils.sheet_io import append_or_update_row
from utils.state_manager import flatten_session_state
from utils.ui_styles import render_info_box, render_data_protection_box


def render():
    st.header("1. 📋 Datos Generales del Banco de Leche Humana (BLH)")

    # ──────────────────────────────────────────────
    # Instrucciones Visuales (con ayudas del .docx)
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
    > ℹ️ **¿Por qué es importante esta sección?**  
    Esta sección permite identificar su institución y comprender las características clave de su Banco de Leche Humana (BLH). La información es esencial para el análisis comparativo entre establecimientos.

    > 📝 **Recuerde:**  
    Por favor diligencie todos los campos de forma completa y precisa.
    """), unsafe_allow_html=True)

    st.markdown(render_data_protection_box("""
    > 🔐 **Nota legal:**  
    La información está protegida bajo la **Ley 1581 de 2012 (Habeas Data)** y será utilizada exclusivamente con fines de análisis autorizados por el **Instituto de Evaluación Tecnológica en Salud (IETS)**.
    """), unsafe_allow_html=True)

    prefix = "datos_generales__"
    completion_flag = prefix + "completed"

    # ──────────────────────────────────────────────
    # Campo 1: Nombre del Establecimiento
    # ──────────────────────────────────────────────

    nombre = st.text_input(
        "🏥 Nombre completo del establecimiento (obligatorio)",
        value=st.session_state.get(prefix + "nombre_inst", ""),
        help="Ejemplo: Hospital Básico San Gabriel"
    )
    st.caption("_Ejemplo: Hospital Básico San Gabriel_")

    # ──────────────────────────────────────────────
    # Campo 2: Tipo de Institución
    # ──────────────────────────────────────────────

    tipo_inst_options = ["Hospital público", "Clínica privada", "Mixta"]
    tipo_inst_selected = st.multiselect(
        "🏷️ Tipo de institución (obligatorio)",
        tipo_inst_options,
        default=st.session_state.get(prefix + "tipo_inst", []),
        help="Puede seleccionar más de una opción si aplica."
    )
    st.caption("_Ejemplo: Hospital público_")

    # ──────────────────────────────────────────────
    # Campo 3: Año de Implementación
    # ──────────────────────────────────────────────

    anio_impl = st.text_input(
        "📅 Año de implementación del BLH (obligatorio, formato AAAA)",
        value=st.session_state.get(prefix + "anio_impl", ""),
        help="Indique el año en que su institución inició formalmente el funcionamiento del BLH."
    )
    st.caption("_Ejemplo: 2008_")

    # ──────────────────────────────────────────────
    # Botón de Guardado con Validación
    # ──────────────────────────────────────────────

    if st.button("💾 Guardar sección - Datos Generales"):
        errores = []

        if not nombre.strip():
            errores.append("✅ Nombre del establecimiento")
        if not tipo_inst_selected:
            errores.append("✅ Tipo de institución")
        if not anio_impl.strip().isdigit() or len(anio_impl.strip()) != 4:
            errores.append("✅ Año de implementación (formato correcto: 4 dígitos)")

        if errores:
            st.warning("⚠️ Por favor corrija los siguientes campos antes de guardar:")
            for e in errores:
                st.markdown(f"- {e}")
        else:
            st.session_state[prefix + "nombre_inst"] = nombre.strip()
            st.session_state[prefix + "tipo_inst"] = tipo_inst_selected
            st.session_state[prefix + "anio_impl"] = anio_impl.strip()
            st.session_state[completion_flag] = True

            flat_data = flatten_session_state(st.session_state)
            success = append_or_update_row(flat_data)

            if success:
                st.success("✅ Datos generales guardados correctamente.")
                if "section_index" in st.session_state and st.session_state.section_index < 9:
                    st.session_state.section_index += 1
                    st.session_state.navigation_triggered = True
                    st.rerun()
            else:
                st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")

    # ──────────────────────────────────────────────
    # Expander: Ver Resumen de Datos
    # ──────────────────────────────────────────────

    with st.expander("🔍 Ver resumen de datos guardados"):
        st.write({
            "Nombre del establecimiento": st.session_state.get(prefix + "nombre_inst", ""),
            "Tipo de institución": st.session_state.get(prefix + "tipo_inst", []),
            "Año de implementación": st.session_state.get(prefix + "anio_impl", ""),
            "Sección completada": st.session_state.get(completion_flag, False)
        })
