import streamlit as st
from constants.infrastructure_schemma import EQUIPOS_INFRAESTRUCTURA, EQUIPOS_PASTEURIZACION
from utils.state_manager import flatten_session_state
from utils.sheet_io import append_or_update_row
from utils.ui_styles import render_info_box, render_compact_example_box
from utils.forms.render_equipment_entry import render_equipment_entry_section, extract_flat_equipment_data


def render():
    st.header("6. 🏩️ Costos en Infraestructura y Equipos (Preguntas 19 y 20)")
    prefix = "costos_equipos__"
    completion_flag = prefix + "completed"

    st.markdown(render_info_box("""
**ℹ️ ¿Qué debe registrar?**  
Esta sección tiene dos partes:

- **Pregunta 19:** Infraestructura y equipos por proceso del BLH.  
- **Pregunta 20 (condicional):** Si realiza pasteurización, detalle los equipos usados en ese proceso.

Para cada equipo ingrese:
- **Cantidad**
- **Año de compra**
- **Vida útil (años)**
- **Costo por unidad (COP)**
- **Costo anual de mantenimiento (COP)**

Si un equipo o proceso **no aplica**, registre **0** en los valores numéricos.
"""), unsafe_allow_html=True)

    realiza_pasteuriza = st.session_state.get("donantes_receptores__pasteuriza", "No") == "Sí"
    st.info(f"📌 Confirmación: La institución {'sí' if realiza_pasteuriza else 'no'} realiza pasteurización.")

    # ─────────────────────────────
    # 🧱 Ejemplo Pregunta 19
    # ─────────────────────────────
    st.markdown(render_compact_example_box("""
📝 **Ejemplo - Pregunta 19: Infraestructura General**

| Proceso     | Ambiente  | Equipo      | Cant. | Año | Vida útil | Costo Unidad | Mantenimiento |
|-------------|-----------|-------------|-------|-----|-----------|---------------|----------------|
| Captación   | Registro  | Escritorio  | 5     | 2024 | 15       | 50.000        | 50.000         |
| Extracción  | Vestier   | Lavamanos   | 5     | 2025 | 10       | 200.000       | 0              |
"""), unsafe_allow_html=True)

    # Pregunta 19
    render_equipment_entry_section(
        title="Pregunta 19: Infraestructura General",
        schema=EQUIPOS_INFRAESTRUCTURA,
        state_key=prefix + "tabla_p19"
    )

    # ─────────────────────────────
    # 🧪 Ejemplo Pregunta 20
    # ─────────────────────────────
    if realiza_pasteuriza:
        st.markdown(render_compact_example_box("""
🧪 **Ejemplo - Pregunta 20: Equipos del Proceso de Pasteurización**

| Proceso        | Ambiente            | Equipo              | Cant. | Año | Vida útil | Costo Unidad | Mantenimiento |
|----------------|---------------------|----------------------|-------|-----|-----------|---------------|----------------|
| Pasteurización | Área de pasteurizado| Pasteurizador        | 2     | 2023 | 8         | 25.000.000    | 1.000.000      |
| Pasteurización | Área de reenvasado  | Campana de flujo laminar | 1 | 2022 | 6         | 15.000.000    | 500.000        |
"""), unsafe_allow_html=True)

        render_equipment_entry_section(
            title="Pregunta 20: Equipos del proceso de pasteurización",
            schema=EQUIPOS_PASTEURIZACION,
            state_key=prefix + "tabla_p20"
        )

    # ─────────────────────────────
    # Validación y guardado
    # ─────────────────────────────
    def alguna_fila_valida(lista):
        return any(item.get("cantidad", 0) > 0 and item.get("costo_unidad", 0) > 0 for item in lista)

    resultados_p19 = extract_flat_equipment_data(prefix + "tabla_p19")
    resultados_p20 = extract_flat_equipment_data(prefix + "tabla_p20") if realiza_pasteuriza else []

    st.session_state[completion_flag] = alguna_fila_valida(resultados_p19)

    if st.button("📂 Guardar sección - Costos en Infraestructura y Equipos"):
        st.session_state[prefix + "tabla_p19_result"] = resultados_p19
        if realiza_pasteuriza:
            st.session_state[prefix + "tabla_p20_result"] = resultados_p20

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
