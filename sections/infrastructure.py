import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_data_protection_box

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
    # Instrucciones claras alineadas al documento
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
    > ℹ️ **¿Qué información debe registrar?**  
    Por favor registre los **equipos e infraestructura** disponibles en cada área funcional del Banco de Leche Humana (BLH).  
    - Si un equipo **no existe o no aplica**, registre **0** en cantidad.  
    - Registre el **costo promedio por unidad**, o coloque **0** si no aplica o no se conoce el valor.

    > 📝 **Ejemplo práctico:**  
    - Área: *Sala de extracción*  
    - Equipo: *Extractor eléctrico*  
    - Cantidad: *2* unidades  
    - Costo promedio por unidad: *450,000 COP*

    > 🔐 **Nota:** La información está protegida por la **Ley 1581 de 2012 (Habeas Data)** y se utilizará exclusivamente para los fines autorizados del estudio.
    """), unsafe_allow_html=True)

    st.markdown(render_data_protection_box("""
    > 🔒 Sus respuestas son confidenciales y serán analizadas de forma agregada y anónima.
    """), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Prefix & Completion Flag
    # ──────────────────────────────────────────────

    prefix = "infraestructura_equipos__"
    completion_flag = prefix + "completed"
    resultados = st.session_state.get(prefix + "data", {})

    # ──────────────────────────────────────────────
    # Áreas funcionales y equipos por área
    # ──────────────────────────────────────────────

    secciones = {
        "Recepción y registro de donantes": ["Escritorio", "Sillas", "Computador"],
        "Vestier": ["Lockers", "Lavamanos", "Dispensadores de jabón"],
        "Sala de extracción": ["Extractores manuales", "Extractores eléctricos", "Cortinas de privacidad"],
        "Punto de recepción y verificación inicial": ["Balanza", "Termómetro", "Neveras portátiles"]
    }

    # ──────────────────────────────────────────────
    # Inputs por área funcional y equipo
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
                    help="Ingrese el valor estimado o 0 si no aplica."
                )

                # Guardar en la estructura interna
                if area not in resultados:
                    resultados[area] = {}
                resultados[area][eq] = {
                    "cantidad": cantidad,
                    "costo": costo
                }

    # ──────────────────────────────────────────────
    # Botón de Guardado y Validación
    # ──────────────────────────────────────────────

    if st.button("💾 Guardar sección - Infraestructura y Equipos"):
        st.session_state[prefix + "data"] = resultados

        # Validación mínima: al menos un equipo con cantidad > 0
        has_any_data = any(
            any(item.get("cantidad", 0) > 0 for item in area_data.values())
            for area_data in resultados.values()
        )

        st.session_state[completion_flag] = has_any_data

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de infraestructura guardados exitosamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Verifique su conexión o intente nuevamente.")

    # ──────────────────────────────────────────────
    # Expander: Ver resumen de datos guardados
    # ──────────────────────────────────────────────

    with st.expander("🔍 Ver resumen de datos guardados en esta sección"):
        st.write(resultados)
