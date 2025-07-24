import streamlit as st

from utils.state_manager import flatten_session_state, get_current_ips_id
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box

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

VEHICULOS_OPCIONES = [
    "Carro particular", "Motocicleta", "Camioneta o furgoneta", "Furgón refrigerado",
    "Bicicleta adaptada con caja isotérmica", "A pie (con termos isotérmicos)", "Otro"
]

def render():
    st.header("10. 🚚 Transporte y Recolección de Leche Humana (Preguntas 24 a 27)")

    prefix = "transporte__"
    sheet_name = "Transporte"
    completion_flag = prefix + "completed"

    # Datos previos
    modalidades_prev = st.session_state.get(prefix + "modalidades", {})
    equipos_prev = st.session_state.get(prefix + "equipos_especiales", "No")
    zonas_prev = st.session_state.get(prefix + "zonas", {})
    vehiculos_prev = st.session_state.get(prefix + "vehiculos", [])

    # P24: Modalidades
    st.subheader("24. Modalidades de recolección de leche humana")
    st.markdown(render_info_box("""
**¿Dónde recibe su BLH las donaciones de leche humana?**  
Marque todas las opciones que apliquen.
"""), unsafe_allow_html=True)
    modalidades = {
        label: st.radio(
            label,
            ["Sí", "No"],
            index=0 if modalidades_prev.get(label, "No") == "Sí" else 1,
            horizontal=True
        )
        for label in [
            "Institución donde se encuentra el BLH",
            "En las casas de los donantes",
            "Centros de recolección"
        ]
    }

    # P25: Equipos
    st.subheader("25. Equipos especializados para el transporte")
    st.markdown(render_info_box("""
**¿La institución ha adquirido equipos especializados (termos, cajas isotérmicas, etc.) para el transporte de leche humana?**
"""), unsafe_allow_html=True)
    equipos_especiales = st.radio(
        "¿Ha sido necesaria la compra de equipos especializados?",
        ["Sí", "No"],
        index=0 if equipos_prev == "Sí" else 1,
        horizontal=True
    )

    # P26: Detalle zonas
    st.subheader("26. Detalle operativo por zona de recolección")
    st.markdown(render_compact_example_box("📜 **Ejemplo:**"), unsafe_allow_html=True)
    st.table({
        "Zona": ["Zona urbana", "Zona rural", "Zonas rurales alejadas"],
        "Volumen (ml)": [3567, 14565, 34556],
        "Kilometraje (km)": [5, 20, 40],
        "Costo mensual (COP)": [200000, 350000, 450000]
    })
    zonas = ["Zona urbana", "Zona rural", "Zonas rurales alejadas"]
    zonas_data = {}
    for zona in zonas:
        prev = zonas_prev.get(zona, {})
        st.markdown(f"**{zona}**")
        zonas_data[zona] = {
            "volumen_ml": st.number_input(
                f"Volumen mensual recolectado (ml) - {zona}:", min_value=0.0, step=100.0,
                value=safe_float(prev.get("volumen_ml", 0.0)), key=f"{zona}_volumen"
            ),
            "km": st.number_input(
                f"Kilometraje mensual (km) - {zona}:", min_value=0.0, step=1.0,
                value=safe_float(prev.get("km", 0.0)), key=f"{zona}_km"
            ),
            "costo": st.number_input(
                f"Costo mensual estimado (COP) - {zona}:", min_value=0.0, step=1000.0,
                value=safe_float(prev.get("costo", 0.0)), key=f"{zona}_costo"
            )
        }

    # P27: Vehículos
    st.subheader("27. Vehículos utilizados para recolección")
    st.markdown(render_info_box("""
**Indique los vehículos utilizados para la recolección de leche humana:**  
Para cada vehículo indique:
- Tipo de vehículo (seleccione de la lista oficial)
- Marca, modelo y año
- Volumen máximo por viaje (ml)
- Número de viajes mensuales
- Tipo de propiedad
"""), unsafe_allow_html=True)

    num_vehiculos = st.number_input(
        "Número de vehículos utilizados:", min_value=0, step=1, value=len(vehiculos_prev)
    )

    vehiculos_data = []
    for i in range(num_vehiculos):
        with st.expander(f"🚗 Vehículo #{i + 1}"):
            prev = vehiculos_prev[i] if i < len(vehiculos_prev) else {}
            tipo = st.selectbox(
                "Tipo de vehículo:", VEHICULOS_OPCIONES,
                index=VEHICULOS_OPCIONES.index(prev.get("tipo", VEHICULOS_OPCIONES[0])),
                key=f"vehiculo_tipo_{i}"
            )
            otro_tipo = ""
            if tipo == "Otro":
                otro_tipo = st.text_input(
                    "Otro - describa el tipo de vehículo:",
                    value=prev.get("otro_tipo", ""), key=f"vehiculo_otro_tipo_{i}"
                )

            vehiculo = {
                "tipo": tipo,
                "marca_modelo": st.text_input("Marca, modelo y año:", value=prev.get("marca_modelo", ""), key=f"vehiculo_marca_{i}"),
                "volumen_viaje_ml": st.number_input("Volumen máximo por viaje (ml):", min_value=0.0, step=100.0, value=safe_float(prev.get("volumen_viaje_ml", 0.0)), key=f"vehiculo_volumen_{i}"),
                "viajes_mes": st.number_input("Número de viajes al mes:", min_value=0, step=1, value=safe_int(prev.get("viajes_mes", 0)), key=f"vehiculo_viajes_{i}"),
                "propiedad": st.selectbox("Tipo de propiedad:", ["Propio institucional", "Alquilado", "Prestado", "Donado"], index=0, key=f"vehiculo_propiedad_{i}")
            }
            if tipo == "Otro":
                vehiculo["otro_tipo"] = otro_tipo.strip()
            vehiculos_data.append(vehiculo)

    # Completitud
    is_complete = (
        any(v == "Sí" for v in modalidades.values()) or
        equipos_especiales == "Sí" or
        any(
            safe_float(z.get("volumen_ml", 0)) > 0 or
            safe_float(z.get("km", 0)) > 0 or
            safe_float(z.get("costo", 0)) > 0
            for z in zonas_data.values()
        ) or
        len(vehiculos_data) > 0
    )
    st.session_state[completion_flag] = is_complete

    if st.button("📂 Guardar sección - Transporte y Recolección"):
        id_ips = get_current_ips_id(st.session_state)
        if not id_ips:
            st.error("❌ No se encontró el identificador único de la IPS. Complete primero la sección de Identificación.")
            return

        st.session_state[prefix + "modalidades"] = modalidades
        st.session_state[prefix + "equipos_especiales"] = equipos_especiales
        st.session_state[prefix + "zonas"] = zonas_data
        st.session_state[prefix + "vehiculos"] = vehiculos_data

        flat_data = {
            "ips_id": id_ips,
            "modalidades": modalidades,
            "equipos_especiales": equipos_especiales,
            "zonas": zonas_data,
            "vehiculos": vehiculos_data,
            completion_flag: is_complete
        }

        success = append_or_update_row(flat_data, sheet_name=sheet_name)

        if success:
            st.success("✅ Datos de transporte y recolección guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 14:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
