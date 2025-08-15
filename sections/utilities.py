import copy
import pandas as pd
import streamlit as st

from utils.state_manager import get_current_ips_id, get_current_ips_nombre
from utils.sheet_io import append_or_update_row, load_existing_data
from utils.ui_styles import render_info_box, render_compact_example_box

# ──────────────────────────────────────────────
PREFIX = "servicios_publicos__"
SHEET_NAME = "Servicios_Publicos"

NAME_KEY = PREFIX + "nombre_inst"
DF_KEY = PREFIX + "df"                 # fuente de verdad del editor
LOADED_FLAG = PREFIX + "loaded"
COMPLETION_KEY = PREFIX + "completed"
FORM_KEY = PREFIX + "form"
EDITOR_KEY = PREFIX + "editor"

DEFAULT_RUBROS = [
    {"rubro": "Energía eléctrica", "costo": 0.0},
    {"rubro": "Agua y alcantarillado", "costo": 0.0},
    {"rubro": "Telefonía fija e Internet", "costo": 0.0},
    {"rubro": "Otros", "costo": 0.0},
]

def _rows_to_df(rows):
    rows = rows or []
    if not rows:
        rows = copy.deepcopy(DEFAULT_RUBROS)
    df = pd.DataFrame([{
        "Rubro": str(r.get("rubro", "")).strip(),
        "Costo mensual (COP)": float(r.get("costo", 0.0) or 0.0),
    } for r in rows])
    if not df.empty:
        df["Rubro"] = df["Rubro"].astype(str)
        df["Costo mensual (COP)"] = pd.to_numeric(
            df["Costo mensual (COP)"], errors="coerce"
        ).fillna(0.0)
    return df

def _df_to_rows(df: pd.DataFrame):
    rows = []
    if not isinstance(df, pd.DataFrame) or df.empty:
        return rows
    for _, row in df.iterrows():
        rubro = str(row.get("Rubro", "")).strip()
        if not rubro:
            continue
        try:
            costo = float(row.get("Costo mensual (COP)", 0.0) or 0.0)
        except (TypeError, ValueError):
            costo = 0.0
        rows.append({"rubro": rubro, "costo": costo})
    return rows

def render():
    st.header("9. 💡 Servicios Públicos del Banco de Leche Humana (Pregunta 23)")

    # Nombre IPS (solo lectura, sin 'value' adicional)
    if NAME_KEY not in st.session_state:
        st.session_state[NAME_KEY] = get_current_ips_nombre() or ""
    st.text_input("🏥 Nombre completo y oficial de la institución:", key=NAME_KEY, disabled=True)

    # Instrucciones
    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
Indique los **rubros de servicios públicos** con **costo mensual atribuible al BLH** (COP).  
Registre **0** si un rubro no aplica.
"""), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**  

| Rubro                          | Costo mensual (COP) |
|--------------------------------|---------------------|
| Energía eléctrica              | 25,567,879          |
| Agua y alcantarillado          | 8,454,865           |
| Telefonía fija e Internet      | 576,868             |
| Otros                          | 0                   |
"""), unsafe_allow_html=True)

    # 1) Inicializa DF por defecto una sola vez
    if DF_KEY not in st.session_state:
        st.session_state[DF_KEY] = _rows_to_df(copy.deepcopy(DEFAULT_RUBROS))

    # 2) Precarga desde Google Sheets SOLO una vez, sin st.rerun()
    ips_id = get_current_ips_id()
    if ips_id and not st.session_state.get(LOADED_FLAG, False):
        loaded = load_existing_data(ips_id, sheet_name=SHEET_NAME) or {}
        loaded_rows = loaded.get("servicios_publicos")
        if isinstance(loaded_rows, list) and loaded_rows:
            st.session_state[DF_KEY] = _rows_to_df(loaded_rows)
        st.session_state[LOADED_FLAG] = True

    # 3) Editor dentro de un FORM → no hay reruns por celda
    with st.form(FORM_KEY, clear_on_submit=False):
        edited_df = st.data_editor(
            st.session_state[DF_KEY],
            key=EDITOR_KEY,
            column_config={
                "Rubro": st.column_config.TextColumn("Nombre del rubro"),
                "Costo mensual (COP)": st.column_config.NumberColumn(
                    "Costo mensual (COP)", min_value=0, step=10000
                ),
            },
            hide_index=True,
            num_rows="dynamic",
            use_container_width=True,
        )

        submitted = st.form_submit_button("💾 Guardar sección - Servicios Públicos")

    # 4) Si se envía el formulario, persistimos lo editado y guardamos
    if submitted:
        st.session_state[DF_KEY] = edited_df.copy()
        rows = _df_to_rows(st.session_state[DF_KEY])
        st.session_state[COMPLETION_KEY] = bool(rows)

        if not ips_id:
            st.error("❌ No se encontró el identificador único de la IPS. Complete primero la sección de Identificación.")
            return

        payload = {
            "ips_id": ips_id,
            "servicios_publicos": rows,
            COMPRETION_KEY if 'COMPRETION_KEY' in globals() else COMTECTION_KEY if 'COMTECTION_KEY' in globals() else COMPlETION_KEY if 'COMPlETION_KEY' in globals() else COMPlETION_KEY if 'COMPlETION_KEY' in globals() else COMPlETION_KEY if 'COMPlETION_KEY' in globals() else COMPlETION_KEY if 'COMPlETION_KEY' in globals() else COMPlETION_KEY if 'COMPlETION_KEY' in globals() else COMPlETION_KEY if 'COMPlETION_KEY' in globals() else COMPlETION_KEY if 'COMPlETION_KEY' in globals() else COMPlETION_KEY if 'COMPlETION_KEY' in globals() else COMPlETION_KEY if 'COMPlETION_KEY' in globals() else COMPlETION_KEY if 'COMPlETION_KEY' in globals() else COMPlETION_KEY if 'COMPlETION_KEY' in globals() else COMPlETION_KEY if 'COMPlETION_KEY' in globals() else COMPLETION_KEY: st.session_state[COMPLETION_KEY]
        }

        ok = append_or_update_row(payload, sheet_name=SHEET_NAME)
        if ok:
            st.success("✅ Costos de servicios públicos guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 13:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
    else:
        # Aunque no se guarde, mantenemos en memoria lo que está en la tabla
        # (no provoca reruns por celda)
        st.session_state[DF_KEY] = edited_df.copy()
        rows = _df_to_rows(st.session_state[DF_KEY])
        st.session_state[COMPLETION_KEY] = bool(rows)
