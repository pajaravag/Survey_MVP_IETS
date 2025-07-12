import streamlit as st
from utils.sheet_io import append_or_update_row
from utils.state_manager import flatten_session_state
from utils.ui_styles import render_info_box, render_data_protection_box, render_compact_example_box


def render():
    st.header("1. 📋 Datos Generales del Banco de Leche Humana (Preguntas 1 a 5)")

    # ──────────────────────────────────────────────
    # Instrucciones Visuales
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
**ℹ️ ¿Por qué es importante esta sección?**  
Esta sección permite identificar su institución y comprender las características clave de su Banco de Leche Humana (BLH).  
La información es esencial para el análisis comparativo y la toma de decisiones.

Por favor diligencie todos los campos de forma **completa y precisa**.
"""), unsafe_allow_html=True)

    st.markdown(render_data_protection_box("""
🔐 **Nota legal:**  
La información está protegida bajo la **Ley 1581 de 2012 (Habeas Data)** y será utilizada exclusivamente con fines de análisis autorizados por el **Instituto de Evaluación Tecnológica en Salud (IETS)**.
"""), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Prefijos y Estado
    # ──────────────────────────────────────────────

    prefix = "datos_generales__"
    completion_flag = prefix + "completed"

    # ──────────────────────────────────────────────
    # Pregunta 1️⃣ Nombre de la Institución
    # ──────────────────────────────────────────────

    nombre = st.text_input(
        "1️⃣ 🏥 Nombre completo de la institución:",
        value=st.session_state.get(prefix + "nombre_inst", ""),
        help="Ejemplo: Hospital Básico San Gabriel"
    )
    st.caption("_Ejemplo: Hospital Básico San Gabriel_")

    # ──────────────────────────────────────────────
    # Pregunta 2️⃣ Tipo de Institución
    # ──────────────────────────────────────────────

    tipo_inst_options = ["Hospital público", "Clínica privada", "Mixta"]
    tipo_inst_selected = st.multiselect(
        "2️⃣ 🏷️ Tipo de institución:",
        tipo_inst_options,
        default=st.session_state.get(prefix + "tipo_inst", []),
        help="Puede seleccionar más de una opción si aplica."
    )
    st.caption("_Ejemplo: Hospital público_")

    # ──────────────────────────────────────────────
    # Pregunta 3️⃣ Año de Implementación
    # ──────────────────────────────────────────────

    anio_impl = st.text_input(
        "3️⃣ 📅 Año de implementación del BLH (formato AAAA):",
        value=st.session_state.get(prefix + "anio_impl", ""),
        help="Ejemplo: 2008"
    )
    st.caption("_Ejemplo: 2008_")

    # ──────────────────────────────────────────────
    # Pregunta 4️⃣ Persona Responsable
    # ──────────────────────────────────────────────

    st.subheader("4️⃣ 👤 Persona responsable del diligenciamiento del formulario")

    responsable_nombre = st.text_input(
        "Nombre completo:",
        value=st.session_state.get(prefix + "responsable_nombre", ""),
        help="Ejemplo: María González"
    )

    responsable_cargo = st.text_input(
        "Cargo:",
        value=st.session_state.get(prefix + "responsable_cargo", ""),
        help="Ejemplo: Coordinadora BLH"
    )

    responsable_correo = st.text_input(
        "Correo electrónico:",
        value=st.session_state.get(prefix + "responsable_correo", ""),
        help="Ejemplo: maria.gonzalez@institucion.gov.co"
    )

    responsable_telefono = st.text_input(
        "Teléfono de contacto:",
        value=st.session_state.get(prefix + "responsable_telefono", ""),
        help="Ejemplo: 3001234567"
    )

    # ──────────────────────────────────────────────
    # Pregunta 5️⃣ Procesos Estandarizados
    # ──────────────────────────────────────────────

    st.subheader("5️⃣ 🔄 Procesos estandarizados realizados por su BLH")

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
    st.caption("_Ejemplo: Educación comunitaria, talleres para madres donantes._")

    # ──────────────────────────────────────────────
    # Validación y Guardado
    # ──────────────────────────────────────────────

    if st.button("💾 Guardar sección - Datos Generales"):
        errores = []

        if not nombre.strip():
            errores.append("✅ Nombre del establecimiento")
        if not tipo_inst_selected:
            errores.append("✅ Tipo de institución")
        if not anio_impl.strip().isdigit() or len(anio_impl.strip()) != 4:
            errores.append("✅ Año de implementación (4 dígitos)")
        if not responsable_nombre.strip():
            errores.append("✅ Nombre de la persona responsable")
        if not responsable_cargo.strip():
            errores.append("✅ Cargo de la persona responsable")
        if not responsable_correo.strip():
            errores.append("✅ Correo electrónico de la persona responsable")
        if not responsable_telefono.strip():
            errores.append("✅ Teléfono de contacto de la persona responsable")
        if not seleccionados and not otros_procesos.strip():
            errores.append("✅ Debe seleccionar al menos un proceso o escribir un proceso adicional")

        if errores:
            st.warning("⚠️ Por favor corrija los siguientes campos antes de guardar:")
            for e in errores:
                st.markdown(f"- {e}")
        else:
            st.session_state[prefix + "nombre_inst"] = nombre.strip()
            st.session_state[prefix + "tipo_inst"] = tipo_inst_selected
            st.session_state[prefix + "anio_impl"] = anio_impl.strip()
            st.session_state[prefix + "responsable_nombre"] = responsable_nombre.strip()
            st.session_state[prefix + "responsable_cargo"] = responsable_cargo.strip()
            st.session_state[prefix + "responsable_correo"] = responsable_correo.strip()
            st.session_state[prefix + "responsable_telefono"] = responsable_telefono.strip()
            st.session_state[procesos_key] = seleccionados
            st.session_state[otros_key] = otros_procesos.strip()
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
