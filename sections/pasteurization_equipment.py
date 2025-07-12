import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box

# 🔐 Conversión segura
def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

def render():
    st.header("8. 🔧 Equipos de Pasteurización del BLH (Pregunta 20)")

    prefix = "pasteurization_equipment__"
    completion_flag = prefix + "completed"
    prev_data = st.session_state.get(prefix + "data", [])

    # —— Instrucciones Oficiales ——
    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
Indique los **equipos utilizados para el proceso de pasteurización**, incluyendo:
- Proceso asociado
- Ambiente físico donde se encuentra
- Nombre/descripción del equipo
- Cantidad
- Año de compra
- Vida útil estimada (en años)
- Costo por unidad (COP)
- Costo anual de mantenimiento (COP)

Registre **0** si no aplica.
    """), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📋 **Ejemplo de Registro:**
- Proceso: Pasteurización  
- Ambiente: Zona de procesamiento  
- Equipo: Pasteurizador (Baño María)  
- Cantidad: 1  
- Año: 2024  
- Vida útil: 15 años  
- Costo unidad: 36,000,000 COP  
- Mantenimiento: 785,685 COP
    """), unsafe_allow_html=True)

    # —— Registro Dinámico de Equipos ——

    num_equipos = st.number_input("🔢 Número de registros de equipos de pasteurización:",
                                   min_value=0, step=1, value=len(prev_data))

    registros = []

    for i in range(num_equipos):
        with st.expander(f"🛠️ Equipo #{i+1}"):
            prev = prev_data[i] if i < len(prev_data) else {}

            proceso = st.text_input("Proceso asociado:",
                                    value=prev.get("proceso", "Pasteurización"),
                                    key=f"{prefix}proceso_{i}")

            ambiente = st.text_input("Ambiente físico:",
                                     value=prev.get("ambiente", ""),
                                     key=f"{prefix}ambiente_{i}")

            equipo = st.text_input("Descripción del equipo:",
                                   value=prev.get("equipo", ""),
                                   key=f"{prefix}equipo_{i}")

            cantidad = st.number_input("Cantidad:", min_value=0, step=1,
                                       value=safe_int(prev.get("cantidad", 0)),
                                       key=f"{prefix}cantidad_{i}")

            anio = st.number_input("Año de compra:", min_value=1900, max_value=2100,
                                   value=safe_int(prev.get("anio", 2020)),
                                   key=f"{prefix}anio_{i}")

            vida_util = st.number_input("Vida útil (años):", min_value=0, step=1,
                                        value=safe_int(prev.get("vida_util", 0)),
                                        key=f"{prefix}vida_util_{i}")

            costo_unit = st.number_input("Costo por unidad (COP):", min_value=0.0, step=1000.0,
                                         value=safe_float(prev.get("costo_unit", 0.0)),
                                         key=f"{prefix}costo_unit_{i}")

            mantenimiento = st.number_input("Costo anual de mantenimiento (COP):",
                                           min_value=0.0, step=1000.0,
                                           value=safe_float(prev.get("mantenimiento", 0.0)),
                                           key=f"{prefix}mantenimiento_{i}")

            registros.append({
                "proceso": proceso.strip(),
                "ambiente": ambiente.strip(),
                "equipo": equipo.strip(),
                "cantidad": cantidad,
                "anio": anio,
                "vida_util": vida_util,
                "costo_unit": costo_unit,
                "mantenimiento": mantenimiento
            })

    # —— Validación de Completitud ——
    is_complete = any(r.get("cantidad", 0) > 0 or r.get("costo_unit", 0) > 0 for r in registros)
    st.session_state[completion_flag] = is_complete

    # —— Botón Guardar ——
    if st.button("📂 Guardar sección - Equipos de Pasteurización"):
        st.session_state[prefix + "data"] = registros

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de equipos de pasteurización guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 10:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")

