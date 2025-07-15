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
# Tabla editable reutilizable
# ──────────────────────────────────────────────
def render_editor_table(df_key, title):
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

    if df_key not in st.session_state:
        st.session_state[df_key] = []

    raw_data = st.session_state[df_key]
    try:
        df = pd.DataFrame(raw_data)
        if df.empty:
            df = pd.DataFrame(columns=columnas)
        else:
            for col in columnas:
                if col not in df.columns:
                    df[col] = None
            df = df[columnas]
    except Exception:
        df = pd.DataFrame(columns=columnas)

    st.markdown(f"### 📊 {title}")
    return st.data_editor(
        df,
        column_config={
            col: (
                st.column_config.TextColumn(etiquetas[col])
                if col in ["proceso", "ambiente", "equipo"]
                else st.column_config.NumberColumn(etiquetas[col], step=1000 if "costo" in col else 1)
            ) for col in columnas
        },
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key=f"editor_{df_key}"
    )

# ──────────────────────────────────────────────
# Render principal
# ──────────────────────────────────────────────
def render():
    st.header("6. 🏛️ Costos en Infraestructura y Equipos (Preguntas 19 y 20)")
    prefix = "costos_equipos__"
    completion_flag = prefix + "completed"

    # Instrucciones principales
    st.markdown(render_info_box("""
**ℹ️ ¿Qué debe registrar?**  
Esta sección tiene dos partes:
- **Pregunta 19:** Infraestructura y equipos por proceso del BLH.  
- **Pregunta 20 (condicional):** Si realiza pasteurización, detalle los equipos usados en ese proceso.

Para cada fila indique:
- Cantidad
- Año de compra
- Vida útil (años)
- Costo por unidad (COP)
- Costo anual de mantenimiento (COP)

Si un equipo o proceso **no aplica**, registre **0** en los valores numéricos.
"""), unsafe_allow_html=True)

    # Estilo para tablas de ejemplo
    st.markdown("""
<style>
    div[data-testid="stMarkdownContainer"] table {
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

    # Ejemplo Pregunta 19
    st.markdown("### 📌 Ejemplo - Pregunta 19 (Infraestructura General)")
    st.markdown(render_compact_example_box("""
| Proceso | Ambiente | Equipo | Cant. | Año | Vida útil | Costo Unidad (COP) | Mantenimiento Anual (COP) |
|---------|----------|--------|-------|------|-------------|----------------------|-----------------------------|
| Captación | Registro donantes | Escritorio | 5 | 2024 | 15 | 50.000 | 50 |
| Captación | Registro donantes | Sillas | 3 | 2024 | 10 | 10.000 | 0 |
| Extracción | Vestier | Lavamanos | 5 | 2025 | 10 | 200.000 | 0 |
| Extracción | Vestier | Dispensador de jabón | 3 | 2025 | 3 | 80.000 | 0 |
| Valoración clínica | Área clínica | Tallímetro | 2 | 2023 | 8 | 250.000 | 0 |
| Valoración clínica | Área clínica | Balanza electrónica | 1 | 2023 | 5 | 1.200.000 | 120.000 |
| Sala extracción | Sala donantes | Extractor hospitalario | 3 | 2025 | 4 | 3.500.000 | 200.000 |
| Sala extracción | Sala donantes | Silla reclinable | 3 | 2025 | 10 | 650.000 | 50.000 |
| Almacenamiento | Punto verificación | Nevera 40L | 3 | 2025 | 5 | 650.000 | 75.000 |
| Almacenamiento | Zona fría | Estantería acero inoxidable | 2 | 2024 | 15 | 1.500.000 | 100.000 |
"""), unsafe_allow_html=True)

    # Confirmación sobre pasteurización
    realiza_pasteuriza = st.session_state.get("donantes_receptores__pasteuriza", "No") == "Sí"
    st.markdown("### 🔍 Confirmación:")
    st.markdown(f"Su institución indicó que **{'sí' if realiza_pasteuriza else 'no'} realiza pasteurización**.")

    # Ejemplo Pregunta 20
    if realiza_pasteuriza:
        st.markdown("### 📌 Ejemplo - Pregunta 20 (Pasteurización)")
        st.markdown(render_compact_example_box("""
| Proceso | Ambiente | Equipo | Cant. | Año | Vida útil | Costo Unidad (COP) | Mantenimiento Anual (COP) |
|---------|----------|--------|-------|------|-------------|----------------------|-----------------------------|
| Pasteurización | Zona pasteurización | Pasteurizador | 1 | 2024 | 15 | 36.000.000 | 785.685 |
| Pasteurización | Zona pasteurización | Timer certificado | 1 | 2022 | 5 | 5.464 | 568 |
| Reenvasado | Área lavado | Autoclave 21L | 1 | 2024 | 15 | 3.769.000 | 56.758 |
| Control microbiológico | Laboratorio | Estufa microbiológica | 3 | 2025 | 4 | 7.890.000 | 500.000 |
| Control microbiológico | Laboratorio | Incubadora | 1 | 2025 | 8 | 15.000.000 | 456.635 |
| Control microbiológico | Laboratorio | Microscopio | 1 | 2024 | 10 | 18.000.000 | 585.887 |
| Control microbiológico | Laboratorio | Campana flujo laminar | 1 | 2025 | 7 | 34.567.475 | 890.890 |
"""), unsafe_allow_html=True)
    else:
        st.info("ℹ️ Puede omitir la tabla de la Pregunta 20 ya que su institución no realiza pasteurización.")

    # Tablas editables
    df_p19 = render_editor_table(prefix + "tabla_p19", "Equipos - Pregunta 19 (Infraestructura general)")
    df_p20 = pd.DataFrame()
    if realiza_pasteuriza:
        df_p20 = render_editor_table(prefix + "tabla_p20", "Equipos - Pregunta 20 (Proceso de pasteurización)")

    # Validación de completitud
    def tabla_valida(df):
        return (
            not df.empty and
            any(safe_int(row["cantidad"], 0) > 0 and safe_float(row["costo_unidad"], 0.0) > 0.0 for _, row in df.iterrows())
        )

    is_complete = tabla_valida(df_p19)
    st.session_state[completion_flag] = is_complete

    # Botón de guardado
    if st.button("💾 Guardar sección - Costos en Infraestructura y Equipos"):
        st.session_state[prefix + "tabla_p19"] = df_p19.to_dict(orient="records")
        if realiza_pasteuriza:
            st.session_state[prefix + "tabla_p20"] = df_p20.to_dict(orient="records")

        flat_data = flatten_session_state(st.session_state)
        success = append_or_update_row(flat_data)

        if success:
            st.success("✅ Datos guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 11:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
