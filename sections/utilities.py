import streamlit as st
import pandas as pd
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def render():
    st.header("9. 💡 Servicios Públicos del Banco de Leche Humana (Pregunta 23)")

    prefix = "servicios_publicos__"
    completion_flag = prefix + "completed"

    prev_data = st.session_state.get(prefix + "data", [])

    # ──────────────────────────────────────────────
    # Instrucciones Oficiales
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
Por favor indique los **rubros de servicios públicos** que tienen un **costo mensual atribuible al BLH**, incluyendo:

- Energía eléctrica
- Agua y alcantarillado
- Telefonía fija e Internet
- Otros rubros si aplica

Todos los valores deben estar expresados en **pesos colombianos (COP)**. Registre **0** si un rubro no aplica.
    """), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**  

| Rubro                          | Costo mensual (COP) |
|---------------------------------|--------------------|
| Energía eléctrica               | 25,567,879         |
| Agua y alcantarillado           | 8,454,865          |
| Telefonía fija e Internet       | 576,868            |
| Otros                           | 0                  |
    """), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Tabla editable de Servicios Públicos
    # ──────────────────────────────────────────────

    default_rubros = [
        {"Rubro": "Energía eléctrica", "Costo mensual (COP)": 0.0},
        {"Rubro": "Agua y alcantarillado", "Costo mensual (COP)": 0.0},
        {"Rubro": "Telefonía fija e Internet", "Costo mensual (COP)": 0.0},
        {"Rubro": "Otros", "Costo mensual (COP)": 0.0}
    ]

    # Cargar datos previos si existen
    if prev_data:
        df = pd.DataFrame(prev_data)
    else:
        df = pd.DataFrame(default_rubros)

    edited_df = st.data_editor(
        df,
        key=f"{prefix}_editor",
        column_config={
            "Rubro": st.column_config.TextColumn("Nombre del rubro"),
            "Costo mensual (COP)": st.column_config.NumberColumn("Costo mensual (COP)", min_value=0, step=10000)
        },
        hide_index=True,
        num_rows="dynamic"
    )

    # ──────────────────────────────────────────────
    # Validación y Guardado
    # ──────────────────────────────────────────────

    services_data = []
    for _, row in edited_df.iterrows():
        services_data.append({
            "rubro": row["Rubro"].strip(),
            "costo": safe_float(row["Costo mensual (COP)"], 0.0)
        })

    is_complete = any(item["costo"] > 0 for item in services_data)
    st.session_state[completion_flag] = True  # Permisivo, puede ser todo cero

    if st.button("💾 Guardar sección - Servicios Públicos"):
        st.session_state[prefix + "data"] = services_data

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Costos de servicios públicos guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
