import streamlit as st
import pandas as pd
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box

# ──────────────────────────────────────────────
# Safe conversion helpers
# ──────────────────────────────────────────────
def safe_float(value, default=0.0):
    try:
        return float(str(value).replace(",", "."))
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default

# ──────────────────────────────────────────────
# Main render function
# ──────────────────────────────────────────────
def render():
    st.header("6. 🏗️ Costos en Infraestructura y Equipos (Preguntas 19 y 20)")

    prefix = "costos_equipos__"
    completion_flag = prefix + "completed"

    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
Esta sección tiene dos componentes:

- **Pregunta 19:** Registre infraestructura y equipos utilizados por ambiente y proceso del BLH.  
- **Pregunta 20 (condicional):** Si su institución **realiza pasteurización**, registre los equipos relacionados a ese proceso.

Por favor diligencie:

- Cantidad de equipos  
- Año de compra  
- Vida útil (años)  
- Costo por unidad (COP)  
- Costo anual de mantenimiento (COP)

Si un proceso no se realiza o el equipo no está presente, registre **cero (0)** en todos los campos.
    """), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**

| Proceso             | Ambiente                   | Equipo                             | Cantidad | Año | Vida útil | Costo Unidad | Mantenimiento Anual |
|---------------------|----------------------------|-------------------------------------|----------|-----|------------|---------------|----------------------|
| Captación           | Registro de donantes       | Escritorio                          | 5        | 2024| 15         | 50.000        | 50                   |
| Extracción          | Vestier                    | Lavamanos                           | 5        | 2025| 10         | 200.000       | 0                    |
| Pasteurización      | Sala de procesamiento      | Pasteurizador (Baño María)          | 1        | 2024| 15         | 36.000.000    | 785.685              |
| Control microbiológico | Laboratorio             | Estufa cultivo microbiológico       | 3        | 2025| 4          | 7.890.000     | 500.000              |
    """), unsafe_allow_html=True)

    # ──────────────────────────────────────────────
    # Mostrar condicionalidad
    # ──────────────────────────────────────────────
    realiza_pasteuriza = st.session_state.get("donantes_receptores__pasteuriza", "No") == "Sí"
    if not realiza_pasteuriza:
        st.warning("⚠️ Recuerde: Solo debe diligenciar datos de la **Pregunta 20** si su institución realiza pasteurización. Puede dejar esos campos en cero.")

    # ──────────────────────────────────────────────
    # Inicializar tabla editable
    # ──────────────────────────────────────────────
    columnas = [
        "proceso", "ambiente", "equipo",
        "cantidad", "anio", "vida_util",
        "costo_unidad", "costo_mantenimiento"
    ]

    etiquetas = {
        "proceso": "Proceso",
        "ambiente": "Ambiente",
        "equipo": "Equipo",
        "cantidad": "Cantidad",
        "anio": "Año de compra",
        "vida_util": "Vida útil (años)",
        "costo_unidad": "Costo por unidad (COP)",
        "costo_mantenimiento": "Costo anual mantenimiento (COP)"
    }

    if prefix + "tabla_equipos" not in st.session_state:
        st.session_state[prefix + "tabla_equipos"] = pd.DataFrame(columns=columnas)

    df = st.session_state[prefix + "tabla_equipos"]

    st.markdown("### 📊 Tabla dinámica de equipos y ambientes (P19 y P20)")
    edited_df = st.data_editor(
        df,
        column_config={
            col: st.column_config.TextColumn(etiquetas[col]) if col in ["proceso", "ambiente", "equipo"]
            else st.column_config.NumberColumn(etiquetas[col], step=1000 if "costo" in col else 1)
            for col in columnas
        },
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="editor_costos_equipos"
    )

    # ──────────────────────────────────────────────
    # Validación
    # ──────────────────────────────────────────────
    is_complete = (
        not edited_df.empty and
        any(
            safe_int(row["cantidad"], 0) > 0 and
            safe_float(row["costo_unidad"], 0.0) > 0.0
            for _, row in edited_df.iterrows()
        )
    )

    # ──────────────────────────────────────────────
    # Botón de Guardado
    # ──────────────────────────────────────────────
    if st.button("💾 Guardar sección - Costos Infraestructura y Equipos"):
        st.session_state[prefix + "tabla_equipos"] = edited_df
        st.session_state[completion_flag] = is_complete

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 10:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
