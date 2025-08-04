import streamlit as st
from utils.ui_styles import render_info_box, render_data_protection_box

def render_intro_info():
    st.markdown(render_info_box("""
**🎯 Objetivo del estudio:**  
El Instituto de Evaluación Tecnológica en Salud (IETS) adelanta esta encuesta con el fin de **estimar los costos asociados al suministro de leche humana en Colombia**, incluyendo infraestructura, equipos, insumos, personal y transporte.

Esta recolección de información se enmarca en la **Ley 2361 de 2024** y en los **Lineamientos Técnicos de la Estrategia de Bancos de Leche Humana** del Ministerio de Salud y Protección Social.
    
Su participación es fundamental para **fortalecer esta estrategia nacional de salud pública**.
"""), unsafe_allow_html=True)

def render_instruction_link():
    st.markdown("""
### 📘 ¿Necesita orientación detallada?

Para conocer en profundidad el propósito, contenido y estructura de este formulario, puede consultar el instructivo oficial en formato PDF:

👉 [**Descargar Instructivo BLH (PDF)**](https://drive.google.com/file/d/1gjoWON6hhYTMQrSvF95yQ04nG5Nc0YfL/view?usp=share_link)

> *Este documento contiene definiciones clave, ejemplos ilustrativos y lineamientos técnicos del IETS.*
""")

def render_data_protection_notice():
    st.markdown(render_data_protection_box("""
🔐 **Nota legal sobre protección de datos personales:**  
Toda la información será tratada con **estricta confidencialidad** y los resultados se presentarán de forma **agregada y anonimizada**.

La información está protegida por el **derecho fundamental de Habeas Data** (Constitución Política de Colombia) y la **Ley 1581 de 2012**, por lo cual su uso será exclusivamente para los fines autorizados en este estudio.
"""), unsafe_allow_html=True)

def render_operational_instructions():
    st.markdown("""
### 🧭 ¿Cómo diligenciar el formulario?

- Complete cada sección de forma **precisa, completa y veraz**.
- Si un dato **no aplica**, registre el valor **0** o seleccione **“No aplica”**.
- Las secciones pueden ser completadas en distintos momentos (progreso guardado por sesión/IP).
- Al final de cada sección, presione **💾 Guardar sección** para registrar sus respuestas.

📌 Puede navegar entre secciones desde el menú lateral izquierdo o usando los botones de avance.

---
""")

def render():
    st.title("📄 Formulario Nacional para Bancos de Leche Humana (BLH)")
    st.subheader("Instituto de Evaluación Tecnológica en Salud (IETS)")

    render_intro_info()
    render_instruction_link()
    render_data_protection_notice()
    render_operational_instructions()

    st.info("Presione el siguiente botón para iniciar la encuesta con la sección 1: **Identificación del IPS**.")

    if st.button("🚀 Iniciar encuesta"):
        # Simplemente avanza a la siguiente sección (índice 1 o nombre, según tu sistema)
        st.session_state.section_index = 1  # O el índice/nombre correspondiente a identification.py
        st.session_state.navigation_triggered = True
        st.rerun()
