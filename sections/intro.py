import streamlit as st
from utils.ui_styles import render_info_box, render_data_protection_box


def render():
    st.title("📄 Formulario Nacional para Bancos de Leche Humana (BLH)")
    st.subheader("Instituto de Evaluación Tecnológica en Salud (IETS)")

    # ──────────────────────────────────────────────
    # Propósito y contexto legal
    # ──────────────────────────────────────────────
    st.markdown(render_info_box("""
**🎯 Objetivo del estudio:**  
El Instituto de Evaluación Tecnológica en Salud (IETS) adelanta esta encuesta con el fin de **estimar los costos asociados al suministro de leche humana en Colombia**, incluyendo infraestructura, equipos, insumos, personal y transporte.

Esta recolección de información se enmarca en la **Ley 2361 de 2024** y en los **Lineamientos Técnicos de la Estrategia de Bancos de Leche Humana** del Ministerio de Salud y Protección Social.
    
Su participación es fundamental para **fortalecer esta estrategia nacional de salud pública**.
"""), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Nota legal de confidencialidad
    # ──────────────────────────────────────────────
    st.markdown(render_data_protection_box("""
🔐 **Nota legal sobre protección de datos personales:**  
Toda la información será tratada con **estricta confidencialidad** y los resultados se presentarán de forma **agregada y anonimizada**.

La información está protegida por el **derecho fundamental de Habeas Data** (Constitución Política de Colombia) y la **Ley 1581 de 2012**, por lo cual su uso será exclusivamente para los fines autorizados en este estudio.
"""), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Instrucciones operativas
    # ──────────────────────────────────────────────
    st.markdown("""
### 🧭 ¿Cómo diligenciar el formulario?

- Complete cada sección de forma **precisa, completa y veraz**.
- Si un dato **no aplica**, registre el valor **0** o seleccione **“No aplica”**.
- Las secciones pueden ser completadas en distintos momentos (progreso guardado por sesión/IP).
- Al final de cada sección, presione **💾 Guardar sección** para registrar sus respuestas.

📌 Puede navegar entre secciones desde el menú lateral izquierdo o usando los botones de avance.

---
""")

    # ──────────────────────────────────────────────
    # Acción para iniciar
    # ──────────────────────────────────────────────
    st.info("Presione el siguiente botón para iniciar la encuesta con la sección 1: **Datos Generales del BLH**.")

    if st.button("🚀 Iniciar encuesta"):
        st.session_state.section_index = 1
        st.session_state.navigation_triggered = True
        st.rerun()

