import streamlit as st
import pandas as pd
from utils.state_manager import flatten_session_state, get_current_ips_id
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box

def render():
    st.header("8. 👩‍⚕️ Personal del Banco de Leche Humana (Pregunta 22)")

    prefix = "personal_blh__"
    completion_flag = prefix + "completed"
    SHEET_NAME = "Personal"

    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
Indique el número de personas asociadas a los roles priorizados en el BLH, el **porcentaje de dedicación mensual** y la **remuneración mensual promedio por persona** en **pesos colombianos (COP)**.

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

    # Carga de datos previos (si existen)
    prev_data = st.session_state.get(prefix + "data", [])
    for i, row in enumerate(prev_data):
        if i < len(default_df):
            default_df.at[i, "Personas"] = row.get("personas", 0)
            default_df.at[i, "% Dedicación"] = row.get("dedicacion_pct", 0)
            default_df.at[i, "Salario mensual (COP)"] = row.get("salario", 0.0)

    # Editor interactivo
    edited_df = st.data_editor(
        default_df,
        key=prefix + "editor",
        column_config={
            "Rol": st.column_config.TextColumn("Rol", disabled=True),
            "Personas": st.column_config.NumberColumn("Número de personas", min_value=0, step=1),
            "% Dedicación": st.column_config.NumberColumn("% dedicación mensual", min_value=0, max_value=100, step=5),
            "Salario mensual (COP)": st.column_config.NumberColumn("Salario mensual (COP)", min_value=0, step=50000)
        },
        hide_index=True,
        use_container_width=True,
        num_rows="fixed"
    )

    # Transforma y valida
    personal_data = []
    for _, row in edited_df.iterrows():
        personal_data.append({
            "rol": row["Rol"],
            "personas": int(row["Personas"]),
            "dedicacion_pct": int(row["% Dedicación"]),
            "salario": float(row["Salario mensual (COP)"])
        })

    st.session_state[prefix + "data"] = personal_data
    st.session_state[completion_flag] = any(p["personas"] > 0 for p in personal_data)

    # Guardado robusto: una fila por IPS con datos estructurados (en un campo dict)
    if st.button("💾 Guardar sección - Personal BLH"):
        id_ips = get_current_ips_id(st.session_state)
        if not id_ips:
            st.error("❌ No se encontró el identificador único de la IPS. Complete primero la sección de Identificación.")
            return

        # Estructura plana: cada rol se guarda como columna, o toda la tabla serializada como json.
        # Aquí optamos por guardar toda la tabla serializada (más simple y flexible)
        flat_data = {
            "ips_id": id_ips,
            "personal_data": personal_data,
            completion_flag: st.session_state[completion_flag]
        }

        success = append_or_update_row(flat_data, sheet_name=SHEET_NAME)

        if success:
            st.success("✅ Datos de personal guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 12:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")

