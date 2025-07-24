import streamlit as st
from datetime import datetime

from utils.ui_styles import render_info_box, render_data_protection_box
from utils.sheet_io import save_section_to_sheet_by_prefix

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

def render_ips_identification(prefix: str) -> str:
    st.markdown("### 🏥 Identificación del IPS")
    return st.text_input(
        "Ingrese el código o nombre del IPS",
        key=f"{prefix}id_ips",
        help="Este identificador permitirá guardar sus datos de forma persistente y segura."
    ).strip()

def handle_start_button(prefix: str, sheet_name: str, id_ips: str):
    if not id_ips:
        st.error("❌ Debe completar el campo de identificación del IPS antes de continuar.")
        return

    # Guarda siempre los campos mínimos de la intro
    st.session_state[f"{prefix}form_started"] = True
    st.session_state[f"{prefix}section_started_at"] = datetime.now().isoformat()

    # Guardar la intro: siempre al menos el id, form_started y section_started_at
    success = save_section_to_sheet_by_prefix(
        section_prefix=prefix,
        id_field=id_ips,
        sheet_name=sheet_name
    )
    if success:
        st.session_state.section_index = 1  # o el índice que uses para navegación
        st.session_state.navigation_triggered = True
        st.rerun()
    else:
        st.warning("No se pudo guardar el inicio. Revise conexión o permisos.")

def render():
    st.title("📄 Formulario Nacional para Bancos de Leche Humana (BLH)")
    st.subheader("Instituto de Evaluación Tecnológica en Salud (IETS)")

    render_intro_info()
    render_instruction_link()
    render_data_protection_notice()
    render_operational_instructions()

    prefix = "intro__"
    id_ips = render_ips_identification(prefix)

    st.info("Presione el siguiente botón para iniciar la encuesta con la sección 1: **Datos Generales del BLH**.")

    if st.button("🚀 Iniciar encuesta"):
        handle_start_button(prefix=prefix, sheet_name="Intro", id_ips=id_ips)
