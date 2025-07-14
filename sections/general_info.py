import streamlit as st
from utils.sheet_io import append_or_update_row
from utils.state_manager import flatten_session_state
from utils.ui_styles import render_info_box, render_data_protection_box, render_compact_example_box


def render():
    st.header("2. 📋 Datos Generales del Banco de Leche Humana (Preguntas 1 a 4)")

    # ──────────────────────────────────────────────
    # Instrucciones de contexto técnico
    # ──────────────────────────────────────────────
    st.markdown(render_info_box("""
**ℹ️ Objetivo de la sección**  
Esta sección busca caracterizar su institución y registrar los procesos estandarizados implementados en su Banco de Leche Humana (BLH).  
Por favor diligencie todos los campos de manera completa y precisa.
"""), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo**  
- Institución: Hospital Básico San Gabriel  
- Tipo: Hospital público  
- Año de implementación: 2008  
- Procesos: Captación, Recepción, Pasteurización
"""), unsafe_allow_html=True)

    st.markdown(render_data_protection_box("""
🔐 **Confidencialidad de la información**  
Los datos serán tratados bajo la Ley 1581 de 2012 de Habeas Data y utilizados exclusivamente para los fines autorizados por el IETS.
"""), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Prefijos y estado de sesión
    # ──────────────────────────────────────────────
    prefix = "datos_generales__"
    completion_flag = prefix + "completed"

    # ──────────────────────────────────────────────
    # Pregunta 1️⃣ Nombre de la institución
    # ──────────────────────────────────────────────
    nombre = st.text_input(
        "1️⃣ 🏥 Nombre completo y oficial de la institución:",
        value=st.session_state.get(prefix + "nombre_inst", ""),
        help="Ejemplo: Hospital Básico San Gabriel"
    )

    # ──────────────────────────────────────────────
    # Pregunta 2️⃣ Tipo de institución
    # ──────────────────────────────────────────────
    tipo_inst_options = ["Hospital público", "Clínica privada", "Mixta"]
    tipo_inst_selected = st.multiselect(
        "2️⃣ 🏷️ Tipo de institución (marque con una “X”):",
        tipo_inst_options,
        default=st.session_state.get(prefix + "tipo_inst", []),
        help="Seleccione al menos una opción que describa el tipo de institución."
    )

    # ──────────────────────────────────────────────
    # Pregunta 3️⃣ Año de implementación del BLH
    # ──────────────────────────────────────────────
    anio_impl = st.text_input(
        "3️⃣ 📅 Año de implementación del BLH (formato AAAA):",
        value=st.session_state.get(prefix + "anio_impl", ""),
        help="Ejemplo: 2008"
    )

    # ──────────────────────────────────────────────
    # Pregunta 4️⃣ Procesos estandarizados implementados
    # ──────────────────────────────────────────────
    st.subheader("4️⃣ 🔄 Procesos estandarizados realizados por su BLH")

    procesos_key = prefix + "procesos"
    otros_key = prefix + "otros_procesos"

    procesos_disponibles = [
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

    procesos_previos = st.session_state.get(procesos_key, [])
    otros_previos = st.session_state.get(otros_key, "")

    seleccionados = []
    for proceso in procesos_disponibles:
        if st.checkbox(proceso, value=(proceso in procesos_previos), key=f"{procesos_key}_{proceso}"):
            seleccionados.append(proceso)

    otros_procesos = st.text_area(
        "➕ Otros procesos realizados (si aplica):",
        value=otros_previos,
        placeholder="Describa aquí procesos adicionales no incluidos en la lista anterior."
    )

    # ──────────────────────────────────────────────
    # Validación de completitud
    # ──────────────────────────────────────────────
    if st.button("💾 Guardar sección - Datos Generales"):
        errores = []

        if not nombre.strip():
            errores.append("✅ Nombre de la institución")
        if not tipo_inst_selected:
            errores.append("✅ Tipo de institución")
        if not anio_impl.strip().isdigit() or len(anio_impl.strip()) != 4:
            errores.append("✅ Año de implementación válido (formato AAAA)")
        if not seleccionados and not otros_procesos.strip():
            errores.append("✅ Al menos un proceso estandarizado o proceso adicional")

        if errores:
            st.warning("⚠️ Por favor revise los siguientes campos:")
            for e in errores:
                st.markdown(f"- {e}")
        else:
            st.session_state[prefix + "nombre_inst"] = nombre.strip()
            st.session_state[prefix + "tipo_inst"] = tipo_inst_selected
            st.session_state[prefix + "anio_impl"] = anio_impl.strip()
            st.session_state[procesos_key] = seleccionados
            st.session_state[otros_key] = otros_procesos.strip()
            st.session_state[completion_flag] = True

            flat_data = flatten_session_state(st.session_state)
            success = append_or_update_row(flat_data)

            if success:
                st.success("✅ Datos generales guardados correctamente.")
                if "section_index" in st.session_state and st.session_state.section_index < 10:
                    st.session_state.section_index += 1
                    st.session_state.navigation_triggered = True
                    st.rerun()
            else:
                st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
