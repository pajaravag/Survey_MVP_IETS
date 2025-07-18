import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box

# 🔐 Conversión segura
def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def render():
    st.header("7. 💊 Insumos del Banco de Leche Humana (Pregunta 21)")

    # ──────────────────────────────────────────────
    # Instrucciones Oficiales
    # ──────────────────────────────────────────────
    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
Registre los **insumos utilizados mensualmente** por el BLH. Para cada uno indique:

- Unidad de medida  
- Cantidad promedio mensual  
- Costo promedio por unidad (COP)

Si no aplica, registre **0**. Puede usar la categoría **"Otros"** para registrar insumos no listados.
"""), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**

| Proceso              | Insumo           | Unidad  | Cantidad | Costo unitario |
|----------------------|------------------|---------|----------|----------------|
| Captación            | Gorros           | Unidad  | 1,000    | 550            |
| Extracción           | Jabón quirúrgico | Litro   | 10       | 6,780          |
| Microbiológico       | Alcohol 96°      | Litro   | 5        | 15,000         |
"""), unsafe_allow_html=True)

    prefix = "insumos_detalle__"
    completion_flag = prefix + "completed"
    prev_data = st.session_state.get(prefix + "data", {})

    procesos_insumos = {
        "Captación, selección y acompañamiento de usuarias": [
            "Gorros", "Tapabocas", "Bata desechable", "Guantes", "Polainas desechables", "Frascos de vidrio"
        ],
        "Extracción y conservación": [
            "Frascos de vidrio tapa rosca (230 ml)", "Frascos de vidrio tapa rosca (130 ml)", "Tapas plásticas (230 ml)",
            "Tapas plásticas (130 ml)", "Rótulos", "Jabón quirúrgico", "Alcohol al 70°", "Antibacterial", "Toallas de papel",
            "Punteras azules (1000 μL)", "Punteras blancas (5000 μL)", "Bolsas plásticas"
        ],
        "Recepción – recolección y almacenamiento": [
            "Jabón quirúrgico", "Gel refrigerante", "Paños humedecidos con alcohol 70%"
        ],
        "Selección y clasificación": [
            "Agua desionizada", "Fenolftaleína 1%", "Tubo capilar sin heparina", "Tubos microhematocritos fco x 100"
        ],
        "Pasteurización": [
            "Agua desionizada", "Hidróxido de sodio (Solución Dornic)"
        ],
        "Control microbiológico": [
            "Caldo de bilis-verde brillante al 2%", "Alcohol al 96°", "Desinfectante", "Tubos de ensayo 13x100 mm",
            "Tubos de ensayo 160x16 mm", "Asa bacteriológica desechable", "Medio cultivo (agar sangre)", "Rejillas - portatubos",
            "Churruscos para lavado de tubos"
        ],
        "Reenvasado": [
            "Rótulos", "Frascos de vidrio"
        ],
        "Otros": [
            "Otro insumo 1", "Otro insumo 2", "Otro insumo 3"
        ]
    }

    insumos_data = {}

    for proceso, insumos in procesos_insumos.items():
        with st.expander(f"🔹 {proceso}"):
            proceso_data = prev_data.get(proceso, {})

            for insumo in insumos:
                prev = proceso_data.get(insumo, {})
                col1, col2, col3 = st.columns([2, 2, 2])

                with col1:
                    unidad = st.text_input(
                        f"Unidad de medida - {insumo}",
                        value=prev.get("unidad", ""),
                        key=f"{prefix}_{proceso}_{insumo}_unidad"
                    )

                with col2:
                    cantidad = st.number_input(
                        f"Cantidad mensual - {insumo}",
                        min_value=0.0,
                        step=1.0,
                        value=safe_float(prev.get("cantidad", 0.0)),
                        key=f"{prefix}_{proceso}_{insumo}_cantidad"
                    )

                with col3:
                    costo = st.number_input(
                        f"Costo por unidad (COP) - {insumo}",
                        min_value=0.0,
                        step=100.0,
                        value=safe_float(prev.get("costo", 0.0)),
                        key=f"{prefix}_{proceso}_{insumo}_costo"
                    )

                insumos_data.setdefault(proceso, {})[insumo] = {
                    "unidad": unidad.strip(),
                    "cantidad": cantidad,
                    "costo": costo
                }

    # ──────────────────────────────────────────────
    # Validación de Completitud segura
    # ──────────────────────────────────────────────

    def is_positive(value):
        try:
            return float(value) > 0
        except (ValueError, TypeError):
            return False

    is_complete = any(
        any(is_positive(v.get("cantidad", 0)) or is_positive(v.get("costo", 0)) for v in insumos.values())
        for insumos in insumos_data.values()
    )
    st.session_state[completion_flag] = is_complete

    # ──────────────────────────────────────────────
    # Guardado
    # ──────────────────────────────────────────────

    if st.button("💾 Guardar sección - Insumos (Pregunta 21)"):
        st.session_state[prefix + "data"] = insumos_data

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de insumos guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 10:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
