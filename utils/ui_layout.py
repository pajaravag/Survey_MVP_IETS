# -*- coding: utf-8 -*-
import streamlit as st

# ──────────────────────────────────────────────
# Header: Logo Institucional (IETS)
# ──────────────────────────────────────────────

def render_header():
    """
    Renderiza la cabecera fija institucional con el logotipo del IETS.
    """
    col1, col2 = st.columns([1, 5])

    with col1:
        st.image("assets/Logo.png", width=150)

    with col2:
        st.markdown("""
            <div style="padding-top: 20px;">
                <h2 style='color:#0073E6; margin-bottom: 0;'>Formulario para Bancos de Leche Humana (BLH)</h2>
            </div>
        """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Footer: Derechos Reservados IETS
# ──────────────────────────────────────────────

def render_footer():
    """
    Renderiza un pie de página con derechos reservados institucionales.
    Debe llamarse al final de cada página.
    """
    st.markdown("""
    <hr style="margin-top: 3em;"/>
    <div style="
        width: 100%;
        background-color: #0073E6;
        color: white;
        text-align: center;
        padding: 12px;
        font-size: 13px;
        border-radius: 6px;
        margin-top: 20px;
    ">
        © 2025 Instituto de Evaluación Tecnológica en Salud (IETS) – Todos los derechos reservados.
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
# Optional Utility: Centered Section Titles
# ──────────────────────────────────────────────

def render_title(text):
    """
    Renderiza un título centrado con el color institucional azul.
    """
    st.markdown(f"""
        <h2 style='color:#0073E6; text-align:center; margin-top: 10px;'>{text}</h2>
    """, unsafe_allow_html=True)
