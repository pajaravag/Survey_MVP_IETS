import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box
from datetime import datetime

# 🔐 Safe conversion helpers

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

# 🔍 Validación completa de un equipo

def is_equipo_valido(equipo):
    return all([
        equipo.get("proceso"),
        equipo.get("ambiente"),
        equipo.get("equipo"),
        equipo.get("cantidad", 0) > 0,
        equipo.get("costo_unit", 0) > 0
    ])

# 🚀 Render principal

def render():
    st.header("5. 🏗️ Costos de Infraestructura y Equipos del Banco de Leche Humana (Pregunta 19)")

    # ──────────────────────────────────────────────
    # Instrucciones Oficiales Claras
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
Registre los datos de los **equipos e infraestructura** utilizados en su Banco de Leche Humana (BLH).

Para cada equipo indique:
- Proceso asociado
- Ambiente físico donde se encuentra
- Descripción del equipo
- Cantidad
- Año de compra (formato AAAA)
- Vida útil estimada (en años)
- Costo por unidad (COP)
- Costo anual de mantenimiento (COP)

Si no aplica, registre "0" o "NA" según corresponda.
    """), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**
| Proceso    | Ambiente         | Equipo          | Cantidad | Año compra | Vida útil | Costo unidad | Mantenimiento |
|-----------|------------------|-----------------|----------|------------|-----------|--------------|---------------|
| Recepción | Área de recepción | Refrigerador 90L | 2        | 2023       | 10 años   | 1.500.000 COP| 100.000 COP   |
    """), unsafe_allow_html=True)

    prefix = "infra_equipment__"
    completion_flag = prefix + "completed"

    prev_data = st.session_state.get(prefix + "data", [])

    # Permitir agregar registros dinámicamente
    if "num_filas_infra" not in st.session_state:
        st.session_state["num_filas_infra"] = len(prev_data)

    if st.button("➕ Agregar nuevo equipo"):
        st.session_state["num_filas_infra"] += 1

    num_filas = st.session_state["num_filas_infra"]
    equipos_data = []

    current_year = datetime.now().year

    for i in range(num_filas):
        with st.expander(f"🛠️ Registro de equipo #{i+1}"):
            prev = prev_data[i] if i < len(prev_data) else {}

            proceso = st.text_input("Proceso asociado:", value=prev.get("proceso", ""), key=f"proceso_{i}")
            ambiente = st.text_input("Ambiente físico (espacio):", value=prev.get("ambiente", ""), key=f"ambiente_{i}")
            equipo = st.text_input("Descripción detallada del equipo:", value=prev.get("equipo", ""), key=f"equipo_{i}")

            cantidad = st.number_input("Cantidad de equipos:", min_value=0, step=1, value=int(prev.get("cantidad", 0)), key=f"cantidad_{i}")

            anio = st.number_input("Año de compra (AAAA):", min_value=1990, max_value=current_year + 1, value=int(prev.get("anio", current_year)), key=f"anio_{i}")

            vida_util = st.number_input("Vida útil estimada (años):", min_value=0, step=1, value=int(prev.get("vida_util", 0)), key=f"vida_util_{i}")

            costo_unit = st.number_input("Costo por unidad (COP):", min_value=0.0, step=1000.0, value=safe_float(prev.get("costo_unit", 0.0)), key=f"costo_unit_{i}")

            mantenimiento = st.number_input("Costo anual de mantenimiento (COP):", min_value=0.0, step=1000.0, value=safe_float(prev.get("mantenimiento", 0.0)), key=f"mantenimiento_{i}")

            equipos_data.append({
                "proceso": proceso.strip(),
                "ambiente": ambiente.strip(),
                "equipo": equipo.strip(),
                "cantidad": cantidad,
                "anio": anio,
                "vida_util": vida_util,
                "costo_unit": costo_unit,
                "mantenimiento": mantenimiento
            })

    # Resumen visual (opcional)
    if equipos_data:
        st.markdown("#### 📊 Resumen de equipos ingresados:")
        st.dataframe(equipos_data)

    is_complete = any(is_equipo_valido(e) for e in equipos_data)
    st.session_state[completion_flag] = is_complete

    if st.button("💾 Guardar sección - Infraestructura y Equipos"):
        st.session_state[prefix + "data"] = equipos_data

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de infraestructura y equipos guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 10:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
