import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row

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
    st.header("8. Transporte y Recolección de Leche Humana")

    st.markdown("""
    > ℹ️ **Instrucciones:**  
    Registre la información relacionada con el **transporte y la recolección de leche humana** en su Banco de Leche Humana (BLH).  
    - Indique los **lugares de recolección** utilizados.
    - Informe si se usan **equipos especializados** para transporte.
    - Registre los **costos promedio mensuales y distancias recorridas** en cada zona.

    Si un dato no aplica, puede dejarlo en **0** o desmarcado.

    > 🔐 **Nota:** La información está protegida conforme a la Ley 1581 de 2012 (**Habeas Data**).
    """)

    # ──────────────────────────────────────────────
    # Prefixes & Stored Data
    # ──────────────────────────────────────────────

    prefix_modal = "transporte_modalidades__"
    prefix_equipos = "transporte_equipos__"
    prefix_costos = "transporte_costos_zona__"
    prefix_detalle_zonas = "transporte_detalle_zonas__"
    completion_flag = "transporte_modalidades__completed"

    modalidades_prev = st.session_state.get(prefix_modal + "data", {})
    equipos_prev = st.session_state.get(prefix_equipos + "data", {})
    detalle_prev = st.session_state.get(prefix_detalle_zonas + "data", {})

    # ──────────────────────────────────────────────
    # Modalidades de Recepción
    # ──────────────────────────────────────────────

    st.subheader("📍 Modalidades de recepción de leche")

    modalidades = {
        "En la institución donde se encuentra el BLH": st.checkbox(
            "Institución", value=modalidades_prev.get("En la institución donde se encuentra el BLH", False)),
        "En las casas de las donantes": st.checkbox(
            "Domicilio", value=modalidades_prev.get("En las casas de las donantes", False)),
        "En centros de recolección": st.checkbox(
            "Centros de recolección", value=modalidades_prev.get("En centros de recolección", False))
    }

    # ──────────────────────────────────────────────
    # Equipos de Transporte
    # ──────────────────────────────────────────────

    st.subheader("🚚 Equipos de transporte utilizados")

    usa_equipos = st.radio(
        "¿Utiliza equipos especializados para el transporte de leche?",
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
                f"Cantidad de {eq}", min_value=0, step=1,
                value=safe_int(eq_data.get("cantidad", 0)),
                key=f"{eq}_cantidad"
            )
            capacidad = st.number_input(
                f"Capacidad promedio por unidad (litros)", min_value=0.0, step=0.5,
                value=safe_float(eq_data.get("capacidad_litros", 0.0)),
                key=f"{eq}_capacidad"
            )
            costo = st.number_input(
                f"Costo promedio por unidad ($ COP)", min_value=0.0, step=1000.0,
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

    st.subheader("📊 Detalle por zona de recolección")

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
            f"Volumen mensual recolectado en {zona} (mL)",
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
    # Validación de Completitud
    # ──────────────────────────────────────────────

    modalities_filled = any(modalidades.values())
    details_filled = any(v.get("volumen_ml", 0) > 0 or v.get("km", 0) > 0 or v.get("costo", 0) > 0 for v in detalle_zonas.values())
    equipment_filled = any(eq.get("cantidad", 0) > 0 for eq in equipos_data.values()) if usa_equipos == "Sí" else False

    st.session_state[completion_flag] = modalities_filled or details_filled or equipment_filled

    # ──────────────────────────────────────────────
    # Guardado y Progreso
    # ──────────────────────────────────────────────

    if st.button("💾 Guardar sección - Transporte y Recolección"):
        st.session_state[prefix_modal + "data"] = modalidades
        st.session_state[prefix_equipos + "data"] = equipos_data if usa_equipos == "Sí" else {}
        st.session_state[prefix_detalle_zonas + "data"] = detalle_zonas

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de transporte y recolección guardados correctamente.")
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
