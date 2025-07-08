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
    ### 🚚 Instrucciones:
    Registre la información sobre el **transporte y la recolección de leche** para su Banco de Leche Humana (BLH):

    - Indique los **lugares de recolección** donde se reciben donaciones.
    - Declare si se utilizan **equipos especializados** (termos, neveras, etc.).
    - Ingrese los **costos promedio mensuales** para cada zona.

    Si un dato no aplica, deje en **0** o desmarcado.
    """)

    # ─────────────────────────────
    # Keys & State
    # ─────────────────────────────

    prefix_modal = "transporte_modalidades__"
    prefix_equipos = "transporte_equipos__"
    prefix_costos = "transporte_costos_zona__"
    completion_flag = "transporte_modalidades__completed"

    modalidades_prev = st.session_state.get(prefix_modal + "data", {})
    equipos_prev = st.session_state.get(prefix_equipos + "data", {})
    costos_prev = st.session_state.get(prefix_costos + "data", {})

    # ─────────────────────────────
    # Modalidades de recolección
    # ─────────────────────────────

    st.subheader("📍 Modalidades de recepción")
    modalidades = {
        "En la institución donde se encuentra el BLH": st.checkbox(
            "Institución", value=modalidades_prev.get("En la institución donde se encuentra el BLH", False)),
        "En las casas de las donantes": st.checkbox(
            "Domicilio", value=modalidades_prev.get("En las casas de las donantes", False)),
        "En centros de recolección": st.checkbox(
            "Centros de recolección", value=modalidades_prev.get("En centros de recolección", False))
    }

    # ─────────────────────────────
    # Equipos de transporte
    # ─────────────────────────────

    st.subheader("🚚 Equipos de transporte")
    usa_equipos = st.radio(
        "¿Utiliza equipos especializados?",
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
                f"Capacidad por contenedor (litros)", min_value=0.0, step=0.5,
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

    # ─────────────────────────────
    # Costos por zona
    # ─────────────────────────────

    st.subheader("🚗 Costos mensuales de transporte")
    costos_zona = {
        "Donación en zona urbana": st.number_input(
            "Costo zona urbana ($ COP/mes)", min_value=0.0, step=1000.0,
            value=safe_float(costos_prev.get("Donación en zona urbana", 0.0))
        ),
        "Donación en zona rural": st.number_input(
            "Costo zona rural ($ COP/mes)", min_value=0.0, step=1000.0,
            value=safe_float(costos_prev.get("Donación en zona rural", 0.0))
        ),
        "Donación en zonas rurales alejadas": st.number_input(
            "Costo zonas rurales alejadas ($ COP/mes)", min_value=0.0, step=1000.0,
            value=safe_float(costos_prev.get("Donación en zonas rurales alejadas", 0.0))
        )
    }

    # ─────────────────────────────
    # Automatic Completion Check (✅ For Progress Bar)
    # ─────────────────────────────

    modalities_filled = any(modalidades.values())
    costs_filled = any(v > 0 for v in costos_zona.values())
    equipment_filled = any(eq.get("cantidad", 0) > 0 for eq in equipos_data.values()) if usa_equipos == "Sí" else False

    st.session_state[completion_flag] = modalities_filled or costs_filled or equipment_filled

    # ─────────────────────────────
    # Save Button
    # ─────────────────────────────

    if st.button("💾 Guardar sección - Transporte y Recolección"):
        st.session_state[prefix_modal + "data"] = modalidades
        st.session_state[prefix_equipos + "data"] = equipos_data if usa_equipos == "Sí" else {}
        st.session_state[prefix_costos + "data"] = costos_zona

        # Reconfirm completion
        st.session_state[completion_flag] = modalities_filled or costs_filled or equipment_filled

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos guardados correctamente en Google Sheets.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.rerun()
        else:
            st.error("❌ Error al guardar. Verifique e intente nuevamente.")

    # ─────────────────────────────
    # Review Expanders
    # ─────────────────────────────

    with st.expander("🔍 Ver modalidades guardadas"):
        st.write(modalidades)

    with st.expander("🔍 Ver equipos guardados"):
        st.write(equipos_data if usa_equipos == "Sí" else {})

    with st.expander("🔍 Ver costos guardados"):
        st.write(costos_zona)
