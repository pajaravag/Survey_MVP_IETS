import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_data_protection_box, render_compact_example_box

# 🔐 Safe conversion helper
def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def render():
    st.header("5. 🧴 Insumos Mensuales del Banco de Leche Humana (BLH)")

    # ──────────────────────────────────────────────
    # Instrucciones Visuales
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
**¿Qué información debe registrar?**  
Registre los **insumos mensuales** necesarios para el funcionamiento de su Banco de Leche Humana (BLH).  
Para cada insumo debe diligenciar:
- La **unidad de medida** (ej.: frascos, litros, cajas, paquetes)
- La **cantidad promedio mensual utilizada**
- El **costo promedio por unidad** (en pesos COP)
    """), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**  
- Insumo: *Frascos estériles*  
- Unidad: *frascos*  
- Cantidad promedio: *50*  
- Costo promedio por unidad: *1,500 COP*
    """), unsafe_allow_html=True)

    st.markdown(render_data_protection_box("""
🔐 **Nota legal:**  
La información será utilizada exclusivamente para el análisis de costos operativos de manera agregada y confidencial, conforme a la **Ley 1581 de 2012 (Habeas Data)**.
    """), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Prefijos y Estado de Datos
    # ──────────────────────────────────────────────

    prefix = "insumos_mensuales__"
    completion_flag = prefix + "completed"
    insumos_key = prefix + "data"

    insumos_data = st.session_state.get(insumos_key, {})

    # ──────────────────────────────────────────────
    # Definición de Categorías e Insumos
    # ──────────────────────────────────────────────

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

    # ──────────────────────────────────────────────
    # Formulario Dinámico por Categoría
    # ──────────────────────────────────────────────

    for categoria, insumos in categorias.items():
        with st.expander(f"🔹 {categoria}"):
            cat_data = insumos_data.get(categoria, {})

            for insumo in insumos:
                item_data = cat_data.get(insumo, {})

                st.markdown(f"**{insumo}**")

                unidad = st.text_input(
                    f"Unidad de medida para {insumo}",
                    value=item_data.get("unidad", ""),
                    key=f"{categoria}_{insumo}_unidad",
                    help="Ej.: frascos, litros, cajas"
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
                    "unidad": unidad.strip(),
                    "cantidad": cantidad,
                    "costo": costo
                }

    # ──────────────────────────────────────────────
    # Validación de Completitud
    # ──────────────────────────────────────────────

    def has_valid_data(data):
        return any(
            any(item.get("cantidad", 0) > 0 or item.get("costo", 0) > 0 for item in cat.values())
            for cat in data.values()
        )

    st.session_state[completion_flag] = has_valid_data(insumos_data)

    # ──────────────────────────────────────────────
    # Botón de Guardado
    # ──────────────────────────────────────────────

    if st.button("💾 Guardar sección - Insumos Mensuales"):
        st.session_state[insumos_key] = insumos_data
        st.session_state[completion_flag] = has_valid_data(insumos_data)

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de insumos guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")

    # ──────────────────────────────────────────────
    # Resumen de Datos Guardados
    # ──────────────────────────────────────────────

    with st.expander("🔍 Ver resumen de datos guardados en esta sección"):
        st.write(insumos_data)
