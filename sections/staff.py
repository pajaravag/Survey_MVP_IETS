import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row

def render():
    st.header("6. Personal asignado al BLH")
    st.markdown("Complete la información sobre el personal exclusivo y compartido involucrado en la operación del BLH.")

    roles = [
        "Auxiliar de enfermería",
        "Profesional en Enfermería",
        "Técnico de laboratorio",
        "Profesional en Medicina",
        "Médico pediatra",
        "Nutricionista",
        "Bacteriólogo",
        "Personal de transporte y distribución",
        "Otro"
    ]

    st.subheader("👥 Personal Exclusivo")
    exclusivo_data = st.session_state.get("personal_exclusivo", {})
    personal_exclusivo = {}

    for rol in roles:
        rol_data = exclusivo_data.get(rol, {})
        with st.container():
            st.markdown(f"**{rol}**")
            cantidad = st.number_input(
                f"Número de personas ({rol})", min_value=0, step=1,
                value=rol_data.get("cantidad", 0),
                key=f"excl_{rol}_n"
            )
            salario = st.number_input(
                f"Salario mensual por persona ({rol}) ($ COP)", min_value=0.0, step=10000.0,
                value=rol_data.get("salario_mensual", 0.0),
                key=f"excl_{rol}_s"
            )
            personal_exclusivo[rol] = {
                "cantidad": cantidad,
                "salario_mensual": salario
            }

    st.subheader("🤝 Personal Compartido")
    compartido_data = st.session_state.get("personal_compartido", {})
    personal_compartido = {}

    for rol in roles:
        rol_data = compartido_data.get(rol, {})
        with st.container():
            st.markdown(f"**{rol}**")
            cantidad = st.number_input(
                f"Número de personas ({rol})", min_value=0, step=1,
                value=rol_data.get("cantidad", 0),
                key=f"comp_{rol}_n"
            )
            horas_pct = st.slider(
                f"Porcentaje de horas asignadas al BLH (%) ({rol})", 0, 100,
                value=rol_data.get("porcentaje_horas", 0),
                key=f"comp_{rol}_pct"
            )
            salario = st.number_input(
                f"Salario mensual por persona ({rol}) ($ COP)", min_value=0.0, step=10000.0,
                value=rol_data.get("salario_mensual", 0.0),
                key=f"comp_{rol}_s"
            )
            personal_compartido[rol] = {
                "cantidad": cantidad,
                "porcentaje_horas": horas_pct,
                "salario_mensual": salario
            }

    if st.button("💾 Guardar sección - Personal"):
        st.session_state["personal_exclusivo"] = personal_exclusivo
        st.session_state["personal_compartido"] = personal_compartido

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Información del personal registrada y guardada en Google Sheets.")
        else:
            st.error("❌ Error al guardar los datos.")
