import streamlit as st
import pandas as pd
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box

def render():
    st.header("8. 👩‍⚕️ Personal del Banco de Leche Humana (Pregunta 22)")

    prefix = "personal_blh__"
    completion_flag = prefix + "completed"

    # ──────────────────────────────────────────────
    # Instrucciones oficiales
    # ──────────────────────────────────────────────
    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
Por favor, indique el número de personas asociadas a los roles priorizados en el BLH, así como el **porcentaje de dedicación mensual** y la **remuneración mensual promedio por persona** en **pesos colombianos (COP)**.

- Si no hay personal para un rol, registre **0** en todos los campos.  
- Si tiene roles adicionales, use los campos de **“Otros”**.  
"""), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**  

| Personal (rol)                  | Personas | % Dedicación | Salario mensual (COP) |
|--------------------------------|----------|--------------|------------------------|
| Auxiliar de enfermería         | 4        | 100%         | 3.500.000              |
| Profesional en Enfermería      | 2        | 80%          | 5.500.000              |
| Técnico de laboratorio         | 3        | 100%         | 3.700.000              |
| Médico pediatra                | 2        | 60%          | 9.500.000              |
| Otros (Nutricionista, etc.)    | 1        | 50%          | 5.800.000              |
    """), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Definición de estructura editable
    # ──────────────────────────────────────────────
    roles = [
        "Auxiliar de enfermería",
        "Profesional en Enfermería",
        "Técnico de laboratorio",
        "Profesional en Medicina",
        "Médico pediatra",
        "Nutricionista",
        "Bacteriólogo",
        "Personal de transporte y distribución",
        "Otros 1",
        "Otros 2",
        "Otros 3"
    ]

    default_df = pd.DataFrame([
        {
            "Rol": rol,
            "Personas": 0,
            "% Dedicación": 0,
            "Salario mensual (COP)": 0.0
        }
        for rol in roles
    ])

    # Cargar datos previos si existen
    prev_data = st.session_state.get(prefix + "data", [])
    for i, row in enumerate(prev_data):
        if i < len(default_df):
            default_df.at[i, "Personas"] = row.get("personas", 0)
            default_df.at[i, "% Dedicación"] = row.get("dedicacion_pct", 0)
            default_df.at[i, "Salario mensual (COP)"] = row.get("salario", 0.0)

    # ──────────────────────────────────────────────
    # Editor de tabla
    # ──────────────────────────────────────────────
    edited_df = st.data_editor(
        default_df,
        key=prefix + "editor",
        column_config={
            "Rol": st.column_config.TextColumn("Rol", disabled=True),
            "Personas": st.column_config.NumberColumn("Número de personas", min_value=0, step=1),
            "% Dedicación": st.column_config.NumberColumn("% de dedicación mensual", min_value=0, max_value=100, step=5),
            "Salario mensual (COP)": st.column_config.NumberColumn("Salario mensual por persona (COP)", min_value=0, step=50000)
        },
        hide_index=True,
        use_container_width=True,
        num_rows="fixed"
    )

    # ──────────────────────────────────────────────
    # Validación de completitud y estructura
    # ──────────────────────────────────────────────
    personal_data = []
    for _, row in edited_df.iterrows():
        personal_data.append({
            "rol": row["Rol"],
            "personas": int(row["Personas"]),
            "dedicacion_pct": int(row["% Dedicación"]),
            "salario": float(row["Salario mensual (COP)"])
        })

    is_complete = any(p["personas"] > 0 for p in personal_data)
    st.session_state[completion_flag] = is_complete

    # ──────────────────────────────────────────────
    # Botón de guardado
    # ──────────────────────────────────────────────
    if st.button("💾 Guardar sección - Personal BLH"):
        st.session_state[prefix + "data"] = personal_data

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos del personal guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 10:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
