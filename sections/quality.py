
import streamlit as st

def render():
    st.header("9. Eficiencia, Calidad y Seguridad")

    st.markdown("Ingrese la información relacionada con la calidad y trazabilidad del proceso de leche humana.")

    descartada = st.number_input(
        "Cantidad promedio de leche descartada por no cumplir estándares (litros/mes)",
        min_value=0.0, step=0.1, key="descartada"
    )

    tiempo_recoleccion_a_distrib = st.number_input(
        "Tiempo promedio desde la recolección hasta la distribución (días)",
        min_value=0.0, step=0.1, key="tiempo_distribucion"
    )

    control_micro = st.radio(
        "¿Realiza control microbiológico post-pasteurización?",
        options=["Sí", "No", "No aplica"],
        horizontal=True,
        key="control_micro"
    )

    if st.button("Guardar sección - Eficiencia y Calidad"):
        st.session_state["calidad_seguridad"] = {
            "leche_descartada_litros": descartada,
            "tiempo_promedio_dias": tiempo_recoleccion_a_distrib,
            "control_microbiologico_post": control_micro
        }
        st.success("✅ Datos de calidad y eficiencia registrados correctamente.")
