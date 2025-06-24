import streamlit as st

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

    personal_exclusivo = {}
    for rol in roles:
        with st.container():
            st.markdown(f"**{rol}**")
            cantidad = st.number_input(f"Número de personas ({rol})", min_value=0, step=1, key=f"excl_{rol}_n")
            salario = st.number_input(f"Salario mensual por persona ({rol}) ($ COP)", min_value=0.0, step=10000.0, key=f"excl_{rol}_s")
            personal_exclusivo[rol] = {
                "cantidad": cantidad,
                "salario_mensual": salario
            }

    st.subheader("🤝 Personal Compartido")

    personal_compartido = {}
    for rol in roles:
        with st.container():
            st.markdown(f"**{rol}**")
            cantidad = st.number_input(f"Número de personas ({rol})", min_value=0, step=1, key=f"comp_{rol}_n")
            horas_pct = st.slider(f"Porcentaje de horas asignadas al BLH (%) ({rol})", 0, 100, key=f"comp_{rol}_pct")
            salario = st.number_input(f"Salario mensual por persona ({rol}) ($ COP)", min_value=0.0, step=10000.0, key=f"comp_{rol}_s")
            personal_compartido[rol] = {
                "cantidad": cantidad,
                "porcentaje_horas": horas_pct,
                "salario_mensual": salario
            }

    if st.button("Guardar sección - Personal"):
        st.session_state["personal_exclusivo"] = personal_exclusivo
        st.session_state["personal_compartido"] = personal_compartido
        st.success("✅ Información del personal registrada correctamente.")
