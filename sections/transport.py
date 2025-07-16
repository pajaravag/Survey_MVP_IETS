import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box

# 🔐 Conversión segura
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

# 🚗 Opciones oficiales de tipos de vehículos
VEHICULOS_OPCIONES = [
    "Carro particular",
    "Motocicleta",
    "Camioneta o furgoneta",
    "Furgón refrigerado",
    "Bicicleta adaptada con caja isotérmica",
    "A pie (con termos isotérmicos)",
    "Otros"
]

def render():
    st.header("10. 🚚 Transporte y Recolección de Leche Humana (Preguntas 24 a 27)")

    prefix = "transporte__"
    completion_flag = prefix + "completed"

    modalidades_prev = st.session_state.get(prefix + "modalidades", {})
    equipos_prev = st.session_state.get(prefix + "equipos_especiales", "No")
    zonas_prev = st.session_state.get(prefix + "zonas", {})
    vehiculos_prev = st.session_state.get(prefix + "vehiculos", [])

    # ──────────────────────────────────────────────
    # Pregunta 24: Modalidades de recolección
    # ──────────────────────────────────────────────
    st.subheader("2️⃣4️⃣ Modalidades de recolección de leche humana")
    st.markdown(render_info_box("""
**¿Dónde recibe su BLH las donaciones de leche humana?**  
Marque todas las opciones que apliquen.
    """), unsafe_allow_html=True)

    modalidades = {
        "Institución donde se encuentra el BLH": st.radio("Recepción en institución", ["Sí", "No"], index=0 if modalidades_prev.get("Institución donde se encuentra el BLH", "No") == "Sí" else 1, horizontal=True),
        "En las casas de los donantes": st.radio("Recolectada en domicilio", ["Sí", "No"], index=0 if modalidades_prev.get("En las casas de los donantes", "No") == "Sí" else 1, horizontal=True),
        "Centros de recolección": st.radio("Centros de recolección", ["Sí", "No"], index=0 if modalidades_prev.get("Centros de recolección", "No") == "Sí" else 1, horizontal=True),
    }

    # ──────────────────────────────────────────────
    # Pregunta 25: Equipos especiales
    # ──────────────────────────────────────────────
    st.subheader("2️⃣5️⃣ Equipos especializados para el transporte")
    st.markdown(render_info_box("""
**¿La institución ha adquirido equipos especializados (termos, cajas isotérmicas, etc.) para el transporte de leche humana?**
    """), unsafe_allow_html=True)

    equipos_especiales = st.radio(
        "¿Ha sido necesaria la compra de equipos especializados para el transporte?",
        ["Sí", "No"],
        index=0 if equipos_prev == "Sí" else 1,
        horizontal=True
    )

    # ──────────────────────────────────────────────
    # Pregunta 26: Detalle por zona
    # ──────────────────────────────────────────────
    st.subheader("2️⃣6️⃣ Detalle operativo por zona de recolección")

    zonas_example = {
        "Zona": ["Zona urbana", "Zona rural", "Zonas rurales alejadas"],
        "Volumen (ml)": [3567, 14565, 34556],
        "Kilometraje (km)": [5, 20, 40],
        "Costo mensual (COP)": [200000, 350000, 450000]
    }

    st.markdown(render_compact_example_box("📝 **Ejemplo:**"), unsafe_allow_html=True)
    st.table(zonas_example)

    zonas = ["Zona urbana", "Zona rural", "Zonas rurales alejadas"]
    zonas_data = {}

    for zona in zonas:
        prev = zonas_prev.get(zona, {})
        st.markdown(f"**{zona}**")
        volumen = st.number_input(f"Volumen mensual recolectado (ml) - {zona}:", min_value=0.0, step=100.0, value=safe_float(prev.get("volumen_ml", 0.0)), key=f"{zona}_volumen")
        kilometros = st.number_input(f"Kilometraje mensual (km) - {zona}:", min_value=0.0, step=1.0, value=safe_float(prev.get("km", 0.0)), key=f"{zona}_km")
        costo = st.number_input(f"Costo mensual estimado (COP) - {zona}:", min_value=0.0, step=1000.0, value=safe_float(prev.get("costo", 0.0)), key=f"{zona}_costo")
        zonas_data[zona] = {
            "volumen_ml": volumen,
            "km": kilometros,
            "costo": costo
        }

    # ──────────────────────────────────────────────
    # Pregunta 27: Vehículos utilizados
    # ──────────────────────────────────────────────
    st.subheader("2️⃣7️⃣ Vehículos utilizados para recolección")
    st.markdown(render_info_box("""
**Indique los vehículos utilizados para la recolección de leche humana:**  
Para cada vehículo indique:
- Tipo de vehículo (seleccione de la lista oficial)
- Marca, modelo y año
- Volumen máximo por viaje (ml)
- Número de viajes mensuales
- Tipo de propiedad
    """), unsafe_allow_html=True)

    num_vehiculos = st.number_input("Número de vehículos utilizados:", min_value=0, step=1, value=len(vehiculos_prev))

    vehiculos_data = []
    for i in range(num_vehiculos):
        with st.expander(f"🚗 Vehículo #{i+1}"):
            prev = vehiculos_prev[i] if i < len(vehiculos_prev) else {}
            tipo = st.selectbox(
                "Tipo de vehículo (según lista oficial):",
                VEHICULOS_OPCIONES,
                index=VEHICULOS_OPCIONES.index(prev.get("tipo")) if prev.get("tipo") in VEHICULOS_OPCIONES else 0,
                key=f"vehiculo_tipo_{i}"
            )
            marca_modelo_anio = st.text_input("Marca, modelo y año:", value=prev.get("marca_modelo", ""), key=f"vehiculo_marca_{i}")
            volumen_max = st.number_input("Volumen máximo por viaje (ml):", min_value=0.0, step=100.0, value=safe_float(prev.get("volumen_viaje_ml", 0.0)), key=f"vehiculo_volumen_{i}")
            viajes_mes = st.number_input("Número de viajes al mes:", min_value=0, step=1, value=safe_int(prev.get("viajes_mes", 0)), key=f"vehiculo_viajes_{i}")
            propiedad = st.selectbox("Tipo de propiedad:", ["Propio institucional", "Alquilado", "Prestado", "Donado"], index=0, key=f"vehiculo_propiedad_{i}")

            vehiculos_data.append({
                "tipo": tipo,
                "marca_modelo": marca_modelo_anio,
                "volumen_viaje_ml": volumen_max,
                "viajes_mes": viajes_mes,
                "propiedad": propiedad
            })

    # ──────────────────────────────────────────────
    # Validación y Guardado
    # ──────────────────────────────────────────────
    is_complete = (
        any(v == "Sí" for v in modalidades.values()) or
        equipos_especiales == "Sí" or
        any(z["volumen_ml"] > 0 or z["km"] > 0 or z["costo"] > 0 for z in zonas_data.values()) or
        len(vehiculos_data) > 0
    )

    st.session_state[completion_flag] = is_complete

    if st.button("💾 Guardar sección - Transporte y Recolección"):
        st.session_state[prefix + "modalidades"] = modalidades
        st.session_state[prefix + "equipos_especiales"] = equipos_especiales
        st.session_state[prefix + "zonas"] = zonas_data
        st.session_state[prefix + "vehiculos"] = vehiculos_data

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de transporte y recolección guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 11:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
