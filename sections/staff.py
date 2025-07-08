import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row

# 🔐 Safe conversion helpers
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

def render():
    st.header("6. Personal Asignado al BLH")

    st.markdown("""
    ### 👥 Instrucciones:
    Por favor registre la información relacionada con el personal que participa en el funcionamiento del Banco de Leche Humana (BLH):

    - **Personal Exclusivo:** Dedicación 100% al BLH.
    - **Personal Compartido:** Dedicación parcial (indique porcentaje estimado).
    - Registre el número de personas y el salario mensual promedio para cada perfil.

    Si un rol no aplica, registre **0**.
    """)

    # ─────────────────────────────
    # Definición de Roles
    # ─────────────────────────────

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

    prefix_excl = "personal_exclusivo__"
    prefix_comp = "personal_compartido__"
    completion_flag = "personal_asignado__completed"

    exclusivo_data = st.session_state.get(prefix_excl + "data", {})
    compartido_data = st.session_state.get(prefix_comp + "data", {})

    personal_exclusivo = {}
    personal_compartido = {}

    # ─────────────────────────────
    # Sección: Personal Exclusivo
    # ─────────────────────────────

    st.subheader("👥 Personal Exclusivo (100% dedicado)")

    for rol in roles:
        rol_data = exclusivo_data.get(rol, {})
        with st.container():
            st.markdown(f"**{rol}**")
            cantidad = st.number_input(
                f"Número de personas ({rol})",
                min_value=0, step=1,
                value=safe_int(rol_data.get("cantidad", 0)),
                key=f"excl_{rol}_n"
            )
            salario = st.number_input(
                f"Salario mensual promedio ({rol}) ($ COP)",
                min_value=0.0, step=10000.0,
                value=safe_float(rol_data.get("salario_mensual", 0.0)),
                key=f"excl_{rol}_s"
            )
            personal_exclusivo[rol] = {
                "cantidad": cantidad,
                "salario_mensual": salario
            }

    # ─────────────────────────────
    # Sección: Personal Compartido
    # ─────────────────────────────

    st.subheader("🤝 Personal Compartido (dedicación parcial)")

    for rol in roles:
        rol_data = compartido_data.get(rol, {})
        with st.container():
            st.markdown(f"**{rol}**")
            cantidad = st.number_input(
                f"Número de personas ({rol})",
                min_value=0, step=1,
                value=safe_int(rol_data.get("cantidad", 0)),
                key=f"comp_{rol}_n"
            )
            horas_pct = st.slider(
                f"% de horas dedicadas al BLH ({rol})",
                min_value=0, max_value=100, step=1,
                value=safe_int(rol_data.get("porcentaje_horas", 0)),
                key=f"comp_{rol}_pct"
            )
            salario = st.number_input(
                f"Salario mensual promedio ({rol}) ($ COP)",
                min_value=0.0, step=10000.0,
                value=safe_float(rol_data.get("salario_mensual", 0.0)),
                key=f"comp_{rol}_s"
            )
            personal_compartido[rol] = {
                "cantidad": cantidad,
                "porcentaje_horas": horas_pct,
                "salario_mensual": salario
            }

    # ─────────────────────────────
    # Validación para barra de progreso
    # ─────────────────────────────

    any_exclusive = any(p.get("cantidad", 0) > 0 for p in personal_exclusivo.values())
    any_shared = any(p.get("cantidad", 0) > 0 for p in personal_compartido.values())
    st.session_state[completion_flag] = any_exclusive or any_shared

    # ─────────────────────────────
    # Botón de Guardado
    # ─────────────────────────────

    if st.button("💾 Guardar sección - Personal BLH"):
        st.session_state[prefix_excl + "data"] = personal_exclusivo
        st.session_state[prefix_comp + "data"] = personal_compartido

        st.session_state[completion_flag] = any_exclusive or any_shared

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de personal guardados correctamente en Google Sheets.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Verifique conexión e intente nuevamente.")

    # ─────────────────────────────
    # Ver datos guardados
    # ─────────────────────────────

    with st.expander("🔍 Ver Personal Exclusivo guardado"):
        st.write(st.session_state.get(prefix_excl + "data", {}))

    with st.expander("🔍 Ver Personal Compartido guardado"):
        st.write(st.session_state.get(prefix_comp + "data", {}))
