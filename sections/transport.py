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
    st.header("8. 🚚 Transporte y Recolección de Leche Humana")

    # ──────────────────────────────────────────────
    # Instrucciones Visuales
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
    > ℹ️ **¿Qué información se solicita en esta sección?**  
    Aquí debe registrar la información relacionada con la **recolección y transporte** de la leche humana para su Banco de Leche Humana (BLH).  

    📝 **Incluya información sobre:**  
    - Modalidades de recolección empleadas.  
    - Uso de equipos especializados.  
    - Costos mensuales y distancias recorridas según zona.

    > 💡 **Ejemplo práctico:**  
    - **Modalidades:** Recolección en casa de donantes.  
    - **Equipos:** Termos rígidos - 2 unidades.  
    - **Zonas:** 100 km mensuales en zona rural.

    """), unsafe_allow_html=True)

    st.markdown(render_data_protection_box("""
    > 🔒 Esta información será utilizada únicamente para los fines del estudio y está protegida por la **Ley 1581 de 2012 (Habeas Data)**.
    """), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Variables & Estado
    # ──────────────────────────────────────────────

    prefix_modal = "transporte_modalidades__"
    prefix_equipos = "transporte_equipos__"
    prefix_detalle_zonas = "transporte_detalle_zonas__"
    completion_flag = prefix_modal + "completed"

    modalidades_prev = st.session_state.get(prefix_modal + "data", {})
    equipos_prev = st.session_state.get(prefix_equipos + "data", {})
    detalle_prev = st.session_state.get(prefix_detalle_zonas + "data", {})

    # ──────────────────────────────────────────────
    # Modalidades de Recolección
    # ──────────────────────────────────────────────

    st.subheader("📍 Modalidades de recepción de leche")

    modalidades = {
        "En la institución donde se encuentra el BLH": st.checkbox(
            "Recepción en la institución", value=modalidades_prev.get("En la institución donde se encuentra el BLH", False)),
        "En las casas de las donantes": st.checkbox(
            "Recolectada en domicilio", value=modalidades_prev.get("En las casas de las donantes", False)),
        "En centros de recolección": st.checkbox(
            "Centros de recolección", value=modalidades_prev.get("En centros de recolección", False))
    }

    # ──────────────────────────────────────────────
    # Equipos de Transporte
    # ──────────────────────────────────────────────

    st.subheader("🚚 Equipos de transporte utilizados")

    usa_equipos = st.radio(
        "¿Utiliza equipos especializados para el transporte de la leche?",
        ["Sí", "No"],
        index=0 if equipos_prev else 1,
        horizontal=True
    )

    equipos_data = {}
    if usa_equipos == "Sí":
        equipos = [
            "Termos rígidos",
            "Cajas térmicas de poliestireno",
            "Neveras portátiles con acumuladores de frío"
        ]
        for eq in equipos:
            eq_data = equipos_prev.get(eq, {})

            st.markdown(f"**{eq}**")

            cantidad = st.number_input(
                f"Cantidad de {eq}",
                min_value=0, step=1,
                value=safe_int(eq_data.get("cantidad", 0)),
                key=f"{eq}_cantidad"
            )

            capacidad = st.number_input(
                f"Capacidad promedio por unidad (litros)",
                min_value=0.0, step=0.5,
                value=safe_float(eq_data.get("capacidad_litros", 0.0)),
                key=f"{eq}_capacidad"
            )

            costo = st.number_input(
                f"Costo promedio por unidad ($ COP)",
                min_value=0.0, step=1000.0,
                value=safe_float(eq_data.get("costo_unitario", 0.0)),
                key=f"{eq}_costo"
            )

            equipos_data[eq] = {
                "cantidad": cantidad,
                "capacidad_litros": capacidad,
                "costo_unitario": costo
            }

    # ──────────────────────────────────────────────
    # Detalle por Zona
    # ──────────────────────────────────────────────

    st.subheader("📊 Detalle de recolección por zona")

    zonas = [
        "Donación en zona urbana",
        "Donación en zona rural",
        "Donación en zonas rurales alejadas"
    ]

    detalle_zonas = {}
    for zona in zonas:
        prev = detalle_prev.get(zona, {})

        st.markdown(f"**{zona}**")

        volumen_ml = st.number_input(
            f"Volumen mensual recolectado ({zona}) (mL)",
            min_value=0.0, step=100.0,
            value=safe_float(prev.get("volumen_ml", 0.0)),
            key=f"{zona}_volumen"
        )

        kilometros = st.number_input(
            f"Kilometraje mensual en {zona} (km)",
            min_value=0.0, step=1.0,
            value=safe_float(prev.get("km", 0.0)),
            key=f"{zona}_km"
        )

        costo_zona = st.number_input(
            f"Costo promedio mensual en {zona} ($ COP)",
            min_value=0.0, step=1000.0,
            value=safe_float(prev.get("costo", 0.0)),
            key=f"{zona}_costo"
        )

        detalle_zonas[zona] = {
            "volumen_ml": volumen_ml,
            "km": kilometros,
            "costo": costo_zona
        }

    # ──────────────────────────────────────────────
    # Completitud para Navegación
    # ──────────────────────────────────────────────

    modalities_filled = any(modalidades.values())
    details_filled = any(v.get("volumen_ml", 0) > 0 or v.get("km", 0) > 0 or v.get("costo", 0) > 0 for v in detalle_zonas.values())
    equipment_filled = any(eq.get("cantidad", 0) > 0 for eq in equipos_data.values()) if usa_equipos == "Sí" else False

    st.session_state[completion_flag] = modalities_filled or details_filled or equipment_filled

    # ──────────────────────────────────────────────
    # Guardado con Feedback
    # ──────────────────────────────────────────────

    if st.button("💾 Guardar sección - Transporte y Recolección"):
        st.session_state[prefix_modal + "data"] = modalidades
        st.session_state[prefix_equipos + "data"] = equipos_data if usa_equipos == "Sí" else {}
        st.session_state[prefix_detalle_zonas + "data"] = detalle_zonas

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de transporte guardados exitosamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")

    # ──────────────────────────────────────────────
    # Visualización de Datos Guardados
    # ──────────────────────────────────────────────

    with st.expander("🔍 Ver modalidades de recolección guardadas"):
        st.write(modalidades)

    with st.expander("🔍 Ver equipos de transporte guardados"):
        st.write(equipos_data if usa_equipos == "Sí" else {})

    with st.expander("🔍 Ver detalle de zonas guardado"):
        st.write(detalle_zonas)
