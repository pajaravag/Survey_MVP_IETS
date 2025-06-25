import streamlit as st
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row

def render():
    st.header("9. Eficiencia, Calidad y Seguridad")
    st.markdown("Ingrese la información relacionada con la calidad y trazabilidad del proceso de leche humana.")

    prev_data = st.session_state.get("calidad_seguridad", {})

    descartada = st.number_input(
        "Cantidad promedio de leche descartada por no cumplir estándares (litros/mes)",
        min_value=0.0, step=0.1,
        value=prev_data.get("leche_descartada_litros", 0.0),
        key="descartada"
    )

    tiempo_recoleccion_a_distrib = st.number_input(
        "Tiempo promedio desde la recolección hasta la distribución (días)",
        min_value=0.0, step=0.1,
        value=prev_data.get("tiempo_promedio_dias", 0.0),
        key="tiempo_distribucion"
    )

    control_micro = st.radio(
        "¿Realiza control microbiológico post-pasteurización?",
        options=["Sí", "No", "No aplica"],
        index=["Sí", "No", "No aplica"].index(prev_data.get("control_microbiologico_post", "Sí")),
        horizontal=True,
        key="control_micro"
    )

    if st.button("💾 Guardar sección y continuar"):
        st.session_state["calidad_seguridad"] = {
            "leche_descartada_litros": descartada,
            "tiempo_promedio_dias": tiempo_recoleccion_a_distrib,
            "control_microbiologico_post": control_micro
        }

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos de calidad y eficiencia registrados y guardados en Google Sheets.")
            if "section_index" in st.session_state and st.session_state.section_index < 9:
                st.session_state.section_index += 1
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos.")
