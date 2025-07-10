import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_data_protection_box

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
    st.header("6. 👥 Personal Asignado al Banco de Leche Humana (BLH)")

    # ──────────────────────────────────────────────
    # Instrucciones Visuales
    # ──────────────────────────────────────────────

    st.markdown(render_info_box("""
    > ℹ️ **¿Qué información debe registrar?**  
    Por favor registre el **personal que participa en el funcionamiento del Banco de Leche Humana (BLH)**. Para cada perfil indique:
    - El **número de personas** que cumplen ese rol
    - El **salario mensual promedio** en pesos COP
    - Si el personal es **compartido**, indique el **% de horas dedicadas al BLH**.

    > 📝 **Ejemplo práctico:**  
    - Perfil: *Nutricionista*  
    - Personal exclusivo: *1 persona* — Salario: *2,500,000 COP*  
    - Personal compartido: *1 persona* — 40% de dedicación — Salario: *2,800,000 COP*

    > 🔐 **Nota:** La información será tratada conforme a la **Ley 1581 de 2012 (Habeas Data)** y se utilizará exclusivamente para los fines autorizados.
    """), unsafe_allow_html=True)

    st.markdown(render_data_protection_box("""
    > 🔒 Los datos recopilados serán utilizados únicamente con fines estadísticos y de análisis, respetando la confidencialidad de cada IPS.
    """), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Definición de Roles
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
        "Otro"
    ]

    prefix_excl = "personal_exclusivo__"
    prefix_comp = "personal_compartido__"
    completion_flag = "personal_asignado__completed"

    exclusivo_data = st.session_state.get(prefix_excl + "data", {})
    compartido_data = st.session_state.get(prefix_comp + "data", {})

    personal_exclusivo = {}
    personal_compartido = {}

    # ──────────────────────────────────────────────
    # Personal Exclusivo (100% dedicado)
    # ──────────────────────────────────────────────

    st.subheader("👥 Personal Exclusivo (dedicación total al BLH)")

    for rol in roles:
        rol_data = exclusivo_data.get(rol, {})
        with st.container():
            st.markdown(f"**{rol}**")
            cantidad = st.number_input(
                f"Número de personas ({rol})",
                min_value=0, step=1,
                value=safe_int(rol_data.get("cantidad", 0)),
                key=f"excl_{rol}_n",
                help="Ingrese 0 si no aplica este perfil en su BLH."
            )

            salario = st.number_input(
                f"Salario mensual promedio ({rol}) ($ COP)",
                min_value=0.0, step=10000.0,
                value=safe_float(rol_data.get("salario_mensual", 0.0)),
                key=f"excl_{rol}_s",
                help="Ingrese el valor promedio mensual, o 0 si no aplica."
            )

            personal_exclusivo[rol] = {
                "cantidad": cantidad,
                "salario_mensual": salario
            }

    # ──────────────────────────────────────────────
    # Personal Compartido (dedicación parcial)
    # ──────────────────────────────────────────────

    st.subheader("🤝 Personal Compartido (dedicación parcial al BLH)")

    for rol in roles:
        rol_data = compartido_data.get(rol, {})
        with st.container():
            st.markdown(f"**{rol}**")

            cantidad = st.number_input(
                f"Número de personas ({rol})",
                min_value=0, step=1,
                value=safe_int(rol_data.get("cantidad", 0)),
                key=f"comp_{rol}_n",
                help="Ingrese 0 si no aplica este perfil en su BLH."
            )

            porcentaje_horas = st.slider(
                f"% estimado de horas dedicadas al BLH ({rol})",
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
                "porcentaje_horas": porcentaje_horas,
                "salario_mensual": salario
            }

    # ──────────────────────────────────────────────
    # Validación de Completitud para Progreso
    # ──────────────────────────────────────────────

    any_exclusive = any(p.get("cantidad", 0) > 0 for p in personal_exclusivo.values())
    any_shared = any(p.get("cantidad", 0) > 0 for p in personal_compartido.values())
    st.session_state[completion_flag] = any_exclusive or any_shared

    # ──────────────────────────────────────────────
    # Botón de Guardado y Navegación
    # ──────────────────────────────────────────────

    if st.button("💾 Guardar sección - Personal BLH"):
        st.session_state[prefix_excl + "data"] = personal_exclusivo
        st.session_state[prefix_comp + "data"] = personal_compartido
        st.session_state[completion_flag] = any_exclusive or any_shared

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de personal guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar. Por favor verifique e intente nuevamente.")

    # ──────────────────────────────────────────────
    # Resumen Visual de Datos Guardados
    # ──────────────────────────────────────────────

    with st.expander("🔍 Ver Personal Exclusivo guardado"):
        st.write(st.session_state.get(prefix_excl + "data", {}))

    with st.expander("🔍 Ver Personal Compartido guardado"):
        st.write(st.session_state.get(prefix_comp + "data", {}))
