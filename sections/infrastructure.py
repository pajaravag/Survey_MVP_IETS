import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_data_protection_box, render_compact_example_box

# 🔐 Safe conversion helpers
def safe_int(value, default=0):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def render():
    st.header("4. 🏗️ Infraestructura y Equipos del Banco de Leche Humana")

    # ──────────────────────────────────────────────
    # Instrucciones Visuales y Ayuda
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
**¿Qué información debe registrar?**  
Registre los **equipos e infraestructura** disponibles en cada área funcional del Banco de Leche Humana (BLH).  
- Si un equipo **no existe o no aplica**, registre **0** en cantidad.  
- Indique el **costo promedio por unidad** o escriba **0** si no se conoce el valor.
    """), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo:**  
- Área: *Sala de extracción*  
- Equipo: *Extractor eléctrico*  
- Cantidad: *2* unidades  
- Costo promedio: *450,000 COP por unidad*
    """), unsafe_allow_html=True)

    st.markdown(render_data_protection_box("""
🔐 **Nota legal:**  
La información proporcionada está protegida bajo la **Ley 1581 de 2012 (Habeas Data)** y será utilizada exclusivamente para fines autorizados por el **IETS**.
    """), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Variables de Estado
    # ──────────────────────────────────────────────

    prefix = "infraestructura_equipos__"
    completion_flag = prefix + "completed"
    resultados = st.session_state.get(prefix + "data", {})

    # ──────────────────────────────────────────────
    # Definición de Áreas y Equipos
    # ──────────────────────────────────────────────

    secciones = {
        "Recepción y registro de donantes": ["Escritorio", "Sillas", "Computador"],
        "Vestier": ["Lockers", "Lavamanos", "Dispensadores de jabón"],
        "Sala de extracción": ["Extractores manuales", "Extractores eléctricos", "Cortinas de privacidad"],
        "Punto de recepción y verificación inicial": ["Balanza", "Termómetro", "Neveras portátiles"]
    }

    # ──────────────────────────────────────────────
    # Formulario por Área y Equipo
    # ──────────────────────────────────────────────

    for area, equipos in secciones.items():
        with st.expander(f"🔹 {area}"):
            area_result = resultados.get(area, {})

            for eq in equipos:
                eq_data = area_result.get(eq, {})

                st.markdown(f"**{eq}**")

                cantidad = st.number_input(
                    f"Cantidad disponible de {eq}",
                    min_value=0, step=1,
                    value=safe_int(eq_data.get("cantidad", 0)),
                    key=f"{area}_{eq}_cantidad",
                    help="Ingrese 0 si este equipo no existe en su institución."
                )

                costo = st.number_input(
                    f"Costo promedio por unidad de {eq} ($ COP)",
                    min_value=0, step=1000,
                    value=safe_int(eq_data.get("costo", 0)),
                    key=f"{area}_{eq}_costo",
                    help="Ingrese el valor estimado o 0 si no se conoce."
                )

                if area not in resultados:
                    resultados[area] = {}
                resultados[area][eq] = {
                    "cantidad": cantidad,
                    "costo": costo
                }

    # ──────────────────────────────────────────────
    # Guardado y Validación de Completitud
    # ──────────────────────────────────────────────

    if st.button("💾 Guardar sección - Infraestructura y Equipos"):
        st.session_state[prefix + "data"] = resultados

        has_any_data = any(
            any(item.get("cantidad", 0) > 0 for item in area_data.values())
            for area_data in resultados.values()
        )

        st.session_state[completion_flag] = has_any_data

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de infraestructura guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")

    # ──────────────────────────────────────────────
    # Expander: Ver resumen
    # ──────────────────────────────────────────────

    # with st.expander("🔍 Ver resumen de datos guardados en esta sección"):
    #     st.write(resultados)
