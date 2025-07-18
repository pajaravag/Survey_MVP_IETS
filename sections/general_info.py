import streamlit as st
import ast

from utils.sheet_io import append_or_update_row
from utils.state_manager import flatten_session_state
from utils.ui_styles import render_info_box, render_data_protection_box, render_compact_example_box


def render():
    st.header("2. 📋 Datos Generales del Banco de Leche Humana (Preguntas 1 a 4)")

    # ──────────────────────────────────────────────
    # 🔄 Limpiar claves corruptas (checklist no booleanas)
    # ──────────────────────────────────────────────
    for k in list(st.session_state.keys()):
        if "datos_generales__procesos_" in k and not isinstance(st.session_state[k], bool):
            del st.session_state[k]

    # ──────────────────────────────────────────────
    # ℹ️ Instrucciones, ejemplos y protección de datos
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
    # 📌 Estado y claves
    # ──────────────────────────────────────────────
    prefix = "datos_generales__"
    completion_flag = prefix + "completed"
    procesos_key = prefix + "procesos"
    otros_key = prefix + "otros_procesos"

    # ──────────────────────────────────────────────
    # Pregunta 1️⃣ - Nombre institución
    # ──────────────────────────────────────────────
    nombre = st.text_input(
        "1️⃣ 🏥 Nombre completo y oficial de la institución:",
        value=st.session_state.get(prefix + "nombre_inst", ""),
        help="Ejemplo: Hospital Básico San Gabriel"
    )

    # ──────────────────────────────────────────────
    # Pregunta 2️⃣ - Tipo de institución
    # ──────────────────────────────────────────────
    tipo_inst_options = ["Hospital público", "Clínica privada", "Mixta"]
    tipo_inst_selected = st.multiselect(
        "2️⃣ 🏷️ Tipo de institución (marque con una “X”):",
        tipo_inst_options,
        default=st.session_state.get(prefix + "tipo_inst", []),
        help="Seleccione al menos una opción que describa el tipo de institución."
    )

    # ──────────────────────────────────────────────
    # Pregunta 3️⃣ - Año de implementación
    # ──────────────────────────────────────────────
    anio_impl = st.text_input(
        "3️⃣ 📅 Año de implementación del BLH (formato AAAA):",
        value=st.session_state.get(prefix + "anio_impl", ""),
        help="Ejemplo: 2008"
    )

    # ──────────────────────────────────────────────
    # Pregunta 4️⃣ - Procesos estandarizados
    # ──────────────────────────────────────────────
    st.subheader("4️⃣ 🔄 Procesos estandarizados realizados por su BLH")

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

    # Cargar estado anterior
    procesos_previos = st.session_state.get(procesos_key, [])
    if isinstance(procesos_previos, str):
        try:
            procesos_previos = ast.literal_eval(procesos_previos)
        except Exception:
            procesos_previos = []

    otros_previos = st.session_state.get(otros_key, "")

    # Mostrar checkboxes (no pasar `value=...` para evitar conflicto con `key`)
    seleccionados = []
    for proceso in procesos_disponibles:
        key = f"{procesos_key}_{proceso}"
        # Solo definimos el valor inicial si la clave aún no existe
        if key not in st.session_state:
            st.session_state[key] = proceso in procesos_previos
        if st.checkbox(proceso, key=key):
            seleccionados.append(proceso)

    otros_procesos = st.text_area(
        "➕ Otros procesos realizados (si aplica):",
        value=otros_previos,
        placeholder="Describa aquí procesos adicionales no incluidos en la lista anterior."
    )

    # ──────────────────────────────────────────────
    # Botón de guardado y validación
    # ──────────────────────────────────────────────
    if st.button("📏 Guardar sección - Datos Generales"):
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
            # Guardar en session_state
            st.session_state[prefix + "nombre_inst"] = nombre.strip()
            st.session_state[prefix + "tipo_inst"] = tipo_inst_selected
            st.session_state[prefix + "anio_impl"] = anio_impl.strip()
            st.session_state[procesos_key] = seleccionados
            st.session_state[otros_key] = otros_procesos.strip()
            st.session_state[completion_flag] = True

            # Guardar en Sheets / CSV
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
