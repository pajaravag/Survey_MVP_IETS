import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box

# 🔐 Conversión segura

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def render():
    st.header("5. 💊 Insumos Mensuales del Banco de Leche Humana (Pregunta 21)")

    # ──────────────────────────────────────────────
    # Instrucciones Oficiales
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
Registre los **insumos mensuales** utilizados para el funcionamiento del Banco de Leche Humana (BLH). Para cada insumo debe indicar:

- **Unidad de medida** (ej.: unidad, litro, metro, paquete)  
- **Cantidad promedio mensual**  
- **Costo promedio por unidad (COP)**  

Si un insumo no aplica en su BLH, registre **0**.  
Si requiere registrar insumos adicionales, utilice la categoría **“Otros”**.
    """), unsafe_allow_html=True)

    # Ejemplo renderizado con st.table
    ejemplo_data = {
        "Proceso": ["Captación", "Recolección", "Control microbiológico"],
        "Insumo": ["Gorros", "Jabón quirúrgico", "Alcohol 96°"],
        "Unidad": ["Unidad", "Litro", "Litro"],
        "Cantidad mensual": ["1,000", "10", "5"],
        "Costo promedio (COP)": ["550", "6,780", "15,000"]
    }
    st.table(ejemplo_data)

    # ──────────────────────────────────────────────
    # Prefijos y Estado
    # ──────────────────────────────────────────────

    prefix = "insumos_detalle__"
    completion_flag = prefix + "completed"
    insumos_data = st.session_state.get(prefix + "data", {})

    # ──────────────────────────────────────────────
    # Definición de Procesos e Insumos
    # ──────────────────────────────────────────────

    procesos_insumos = {
        "Captación, selección y acompañamiento de usuarias": ["Gorros", "Tapabocas", "Bata desechable", "Guantes", "Polainas desechables", "Frascos de vidrio"],
        "Extracción y conservación": ["Frascos de vidrio tapa rosca (230 ml)", "Tapas plásticas (230 ml)", "Rótulos", "Jabón quirúrgico", "Alcohol al 70°", "Antibacterial", "Toallas de papel"],
        "Recepción y almacenamiento": ["Gel refrigerante", "Paños humedecidos con alcohol 70%"],
        "Selección y clasificación": ["Agua desionizada", "Fenolftaleína 1%", "Tubos capilares"],
        "Pasteurización": ["Agua desionizada", "Hidróxido de sodio (Dornic)"],
        "Control microbiológico": ["Caldo bilis-verde brillante", "Alcohol al 96°", "Desinfectante", "Tubos de ensayo", "Medio cultivo (agar sangre)"],
        "Reenvasado": ["Rótulos"],
        "Otros": ["Otro 1", "Otro 2"]
    }

    # ──────────────────────────────────────────────
    # Formulario Dinámico por Proceso
    # ──────────────────────────────────────────────

    for proceso, insumos in procesos_insumos.items():
        with st.expander(f"🔹 {proceso}"):
            proceso_data = insumos_data.get(proceso, {})

            for insumo in insumos:
                item = proceso_data.get(insumo, {})

                st.markdown(f"**🧙‍♂️ {insumo}**")

                unidad = st.text_input(f"Unidad de medida:", value=item.get("unidad", ""), key=f"{proceso}_{insumo}_unidad")
                cantidad = st.number_input(f"Cantidad promedio mensual:", min_value=0.0, value=safe_float(item.get("cantidad", 0.0)), step=1.0, key=f"{proceso}_{insumo}_cantidad")
                costo = st.number_input(f"Costo promedio por unidad (COP):", min_value=0.0, value=safe_float(item.get("costo", 0.0)), step=100.0, key=f"{proceso}_{insumo}_costo")

                if proceso not in insumos_data:
                    insumos_data[proceso] = {}

                insumos_data[proceso][insumo] = {
                    "unidad": unidad.strip(),
                    "cantidad": cantidad,
                    "costo": costo
                }

    # ──────────────────────────────────────────────
    # Validación de Completitud
    # ──────────────────────────────────────────────

    def has_data(data):
        return any(
            any(v.get("cantidad", 0) > 0 or v.get("costo", 0) > 0 for v in insumos.values())
            for insumos in data.values()
        )

    st.session_state[completion_flag] = has_data(insumos_data)

    # ──────────────────────────────────────────────
    # Guardado
    # ──────────────────────────────────────────────

    if st.button("📂 Guardar sección - Insumos Mensuales"):
        st.session_state[prefix + "data"] = insumos_data

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
