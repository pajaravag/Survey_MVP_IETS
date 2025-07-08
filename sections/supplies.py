import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row

# 🔐 Safe conversion helper
def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def render():
    st.header("5. Insumos Mensuales")

    st.markdown("""
    ### 🧴 Instrucciones:
    Por favor registre los **insumos mensuales** utilizados en el Banco de Leche Humana (BLH).

    - Registre unidad, cantidad y costo para cada insumo relevante.
    - Si un insumo no aplica, puede dejarlo en cero o en blanco.
    """)

    prefix = "insumos_mensuales__"
    completion_flag = prefix + "completed"
    insumos_key = prefix + "data"

    insumos_data = st.session_state.get(insumos_key, {})

    categorias = {
        "Insumos para almacenar": ["Frascos estériles"],
        "Reactivos de laboratorio": [
            "Caldo bilis-verde brillante al 2%",
            "Tubos microhematocritos fco x 100",
            "Alcohol al 95%"
        ],
        "Elementos de protección personal": [
            "Bata desechable", "Guantes", "Tapabocas",
            "Polainas desechables", "Kit desechable paquete", "Gorro desechable"
        ],
        "Etiquetas y sistemas de trazabilidad": ["Etiquetas"],
        "Productos de limpieza/desinfección": [
            "Desinfectante", "Jabón quirúrgico", "Alcohol 70%",
            "Antibacterial", "Toalla de papel"
        ],
        "Materiales de laboratorio": ["Examen de laboratorio"],
        "Otros": ["Otro 1", "Otro 2", "Otro 3"]
    }

    # 🔍 Live validate flag (ensures preloaded data is respected)
    has_data = any(
        any(item.get("cantidad", 0) > 0 or item.get("costo", 0) > 0 for item in cat.values())
        for cat in insumos_data.values()
    )
    st.session_state[completion_flag] = has_data

    # 🔹 Render inputs
    for categoria, insumos in categorias.items():
        with st.expander(f"🔹 {categoria}"):
            cat_data = insumos_data.get(categoria, {})
            for insumo in insumos:
                item_data = cat_data.get(insumo, {})

                st.markdown(f"**{insumo}**")

                unidad = st.text_input(
                    f"Unidad de medida para {insumo}",
                    value=item_data.get("unidad", ""),
                    key=f"{categoria}_{insumo}_unidad"
                )

                cantidad = st.number_input(
                    f"Cantidad mensual de {insumo}",
                    min_value=0.0, step=1.0,
                    value=safe_float(item_data.get("cantidad", 0.0)),
                    key=f"{categoria}_{insumo}_cantidad"
                )

                costo = st.number_input(
                    f"Costo promedio por unidad de {insumo} ($ COP)",
                    min_value=0.0, step=100.0,
                    value=safe_float(item_data.get("costo", 0.0)),
                    key=f"{categoria}_{insumo}_costo"
                )

                if categoria not in insumos_data:
                    insumos_data[categoria] = {}
                insumos_data[categoria][insumo] = {
                    "unidad": unidad,
                    "cantidad": cantidad,
                    "costo": costo
                }

    # 🔹 Save button
    if st.button("💾 Guardar sección - Insumos Mensuales"):
        st.session_state[insumos_key] = insumos_data

        # Recalculate completion status based on updated data
        has_data = any(
            any(item.get("cantidad", 0) > 0 or item.get("costo", 0) > 0 for item in cat.values())
            for cat in insumos_data.values()
        )
        st.session_state[completion_flag] = has_data

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de insumos guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar. Por favor intente nuevamente.")

    # 🔍 View saved data
    with st.expander("🔍 Ver resumen de datos guardados"):
        st.write(insumos_data)
