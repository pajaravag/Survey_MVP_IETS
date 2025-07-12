import streamlit as st
import pandas as pd
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box

def render():
    st.header("6. 👩‍⚕️ Personal del Banco de Leche Humana (Pregunta 22)")

    prefix = "personal_blh__"
    completion_flag = prefix + "completed"

    prev_data = st.session_state.get(prefix + "data", [])

    # ──────────────────────────────────────────────
    # Instrucciones Oficiales
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
Por favor registre para cada rol:
- El número de personas asignadas.
- El porcentaje promedio de dedicación al BLH.
- La remuneración mensual promedio por persona (COP).

Si un perfil no aplica, registre **0** en todos los campos.
"""), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**  

| Personal (rol)              | Personas | % Dedicación | Salario mensual (COP) |
|----------------------------|----------|--------------|-----------------------|
| Auxiliar de enfermería      | 4        | 100%         | 3,500,000             |
| Profesional en Enfermería   | 2        | 80%          | 5,500,000             |
| Médico Pediatra             | 1        | 60%          | 9,500,000             |
| Otros (Nutricionista, etc.) | 1        | 50%          | 5,800,000             |
    """), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Definición de perfiles y carga de datos previos
    # ──────────────────────────────────────────────

    perfiles = [
        "Auxiliar de enfermería",
        "Profesional en Enfermería",
        "Técnico de laboratorio",
        "Profesional en Medicina",
        "Médico Pediatra",
        "Nutricionista",
        "Bacteriólogo",
        "Personal de transporte y distribución",
        "Otros 1",
        "Otros 2",
        "Otros 3"
    ]

    default_data = pd.DataFrame([
        {
            "Rol": perfil,
            "Personas": 0,
            "% Dedicación": 0,
            "Salario mensual (COP)": 0.0
        }
        for perfil in perfiles
    ])

    if prev_data:
        for i, row in enumerate(prev_data):
            if i < len(default_data):
                default_data.at[i, "Personas"] = row.get("personas", 0)
                default_data.at[i, "% Dedicación"] = row.get("dedicacion_pct", 0)
                default_data.at[i, "Salario mensual (COP)"] = row.get("salario", 0.0)

    # ──────────────────────────────────────────────
    # Render Tabla Editable
    # ──────────────────────────────────────────────

    edited_df = st.data_editor(
        default_data,
        key=f"{prefix}_editor",
        column_config={
            "Rol": st.column_config.Column("Rol", disabled=True),
            "Personas": st.column_config.NumberColumn("Número de personas", min_value=0, step=1),
            "% Dedicación": st.column_config.NumberColumn("% de dedicación", min_value=0, max_value=100, step=5),
            "Salario mensual (COP)": st.column_config.NumberColumn("Salario mensual (COP)", min_value=0, step=50000)
        },
        hide_index=True,
        num_rows="fixed"
    )

    # ──────────────────────────────────────────────
    # Validación y Guardado
    # ──────────────────────────────────────────────

    staff_data = []
    for _, row in edited_df.iterrows():
        staff_data.append({
            "rol": row["Rol"],
            "personas": int(row["Personas"]),
            "dedicacion_pct": int(row["% Dedicación"]),
            "salario": float(row["Salario mensual (COP)"])
        })

    is_complete = any(item["personas"] > 0 for item in staff_data)
    st.session_state[completion_flag] = is_complete

    if st.button("💾 Guardar sección - Personal BLH"):
        st.session_state[prefix + "data"] = staff_data

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de personal guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
