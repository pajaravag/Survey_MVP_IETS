import copy
import pandas as pd
import streamlit as st

from utils.state_manager import get_current_ips_id, get_current_ips_nombre
from utils.sheet_io import append_or_update_row, load_existing_data
from utils.ui_styles import render_info_box, render_compact_example_box

# ──────────────────────────────────────────────
PREFIX = "personal_blh__"
SHEET_NAME = "Personal"

NAME_KEY = PREFIX + "nombre_inst"
DF_KEY = PREFIX + "df"               # fuente de verdad del editor
LOADED_FLAG = PREFIX + "loaded"
COMPLETION_KEY = PREFIX + "completed"
FORM_KEY = PREFIX + "form"
EDITOR_KEY = PREFIX + "editor"
DATA_KEY = PREFIX + "data"           # espejo opcional (lista de dicts)

ROLES_BASE = [
    "Auxiliar de enfermería",
    "Profesional en Enfermería",
    "Técnico de laboratorio",
    "Profesional en Medicina",
    "Médico pediatra",
    "Nutricionista",
    "Bacteriólogo",
    "Personal de transporte y distribución",
    "Otros 1",
    "Otros 2",
    "Otros 3",
]

def _normalize_role(s: str) -> str:
    return (s or "").strip().lower()

def _build_default_df():
    return pd.DataFrame(
        [{"Rol": r, "Personas": 0, "% Dedicación": 0, "Salario mensual (COP)": 0.0} for r in ROLES_BASE]
    )

def _merge_loaded_into_df(loaded_rows):
    """
    loaded_rows: lista de dicts con keys: rol, personas, dedicacion_pct, salario
    Mezcla con la plantilla base por nombre de rol (case-insensitive).
    Si hay roles extra en la data, se agregan al final.
    """
    df = _build_default_df()
    if not isinstance(loaded_rows, list):
        return df

    # índice por rol normalizado para la df base
    idx_by_role = {_normalize_role(r): i for i, r in enumerate(ROLES_BASE)}

    extras = []
    for item in loaded_rows:
        if not isinstance(item, dict):
            continue
        rol = str(item.get("rol", "")).strip()
        if not rol:
            continue
        personas = item.get("personas", 0)
        dedic = item.get("dedicacion_pct", 0)
        salario = item.get("salario", 0.0)

        key = _normalize_role(rol)
        if key in idx_by_role:
            i = idx_by_role[key]
            df.at[i, "Personas"] = int(personas or 0)
            df.at[i, "% Dedicación"] = int(dedic or 0)
            df.at[i, "Salario mensual (COP)"] = float(salario or 0.0)
        else:
            # rol no está en base -> agregarlo al final
            extras.append({
                "Rol": rol,
                "Personas": int(personas or 0),
                "% Dedicación": int(dedic or 0),
                "Salario mensual (COP)": float(salario or 0.0),
            })

    if extras:
        df = pd.concat([df, pd.DataFrame(extras)], ignore_index=True)

    # Tipos consistentes
    df["Rol"] = df["Rol"].astype(str)
    df["Personas"] = pd.to_numeric(df["Personas"], errors="coerce").fillna(0).astype(int)
    df["% Dedicación"] = pd.to_numeric(df["% Dedicación"], errors="coerce").fillna(0).astype(int)
    df["Salario mensual (COP)"] = pd.to_numeric(df["Salario mensual (COP)"], errors="coerce").fillna(0.0)
    return df

def _df_to_rows(df: pd.DataFrame):
    rows = []
    if not isinstance(df, pd.DataFrame) or df.empty:
        return rows
    for _, row in df.iterrows():
        rol = str(row.get("Rol", "")).strip()
        if not rol:
            continue
        personas = int(pd.to_numeric(row.get("Personas", 0), errors="coerce") or 0)
        dedic = int(pd.to_numeric(row.get("% Dedicación", 0), errors="coerce") or 0)
        salario = float(pd.to_numeric(row.get("Salario mensual (COP)", 0.0), errors="coerce") or 0.0)
        rows.append({
            "rol": rol,
            "personas": personas,
            "dedicacion_pct": dedic,
            "salario": salario,
        })
    return rows

def render():
    st.header("8. 👩‍⚕️ Personal del Banco de Leche Humana (Pregunta 22)")

    # Nombre IPS (solo lectura, sin value+key conflict)
    if NAME_KEY not in st.session_state:
        st.session_state[NAME_KEY] = get_current_ips_nombre() or ""
    st.text_input("🏥 Nombre completo y oficial de la institución:", key=NAME_KEY, disabled=True)

    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
Indique el número de personas asociadas a los roles priorizados en el BLH, el **porcentaje de dedicación mensual** y la **remuneración mensual promedio por persona** en **COP**.

- Si no hay personal para un rol, registre **0** en todos los campos.  
- Si tiene roles adicionales, use los campos de **“Otros”**.
"""), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**  

| Personal (rol)                  | Personas | % Dedicación | Salario mensual (COP) |
|--------------------------------|----------|--------------|------------------------|
| Auxiliar de enfermería         | 4        | 100%         | 3.500.000              |
| Profesional en Enfermería      | 2        | 80%          | 5.500.000              |
| Técnico de laboratorio         | 3        | 100%         | 3.700.000              |
| Médico pediatra                | 2        | 60%          | 9.500.000              |
| Otros (Nutricionista, etc.)    | 1        | 50%          | 5.800.000              |
"""), unsafe_allow_html=True)

    # 1) Inicializa DF base una vez
    if DF_KEY not in st.session_state:
        st.session_state[DF_KEY] = _build_default_df()

    # 2) Precarga desde Google Sheets SOLO una vez, sin st.rerun()
    ips_id = get_current_ips_id()
    if ips_id and not st.session_state.get(LOADED_FLAG, False):
        loaded = load_existing_data(ips_id, sheet_name=SHEET_NAME) or {}
        loaded_rows = loaded.get("personal_data")
        if isinstance(loaded_rows, list) and loaded_rows:
            st.session_state[DF_KEY] = _merge_loaded_into_df(loaded_rows)
        st.session_state[LOADED_FLAG] = True
        # Marca completitud inicial según data cargada
        st.session_state[COMPLETION_KEY] = any(r.get("personas", 0) > 0 for r in _df_to_rows(st.session_state[DF_KEY]))

    # 3) Editor dentro de FORM para evitar reruns por cada celda
    with st.form(PREFIX + "form", clear_on_submit=False):
        edited_df = st.data_editor(
            st.session_state[DF_KEY],
            key=EDITOR_KEY,
            column_config={
                "Rol": st.column_config.TextColumn("Rol", disabled=True),
                "Personas": st.column_config.NumberColumn("Número de personas", min_value=0, step=1),
                "% Dedicación": st.column_config.NumberColumn("% dedicación mensual", min_value=0, max_value=100, step=5),
                "Salario mensual (COP)": st.column_config.NumberColumn("Salario mensual (COP)", min_value=0, step=50000),
            },
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",  # roles predefinidos
        )

        submitted = st.form_submit_button("💾 Guardar sección - Personal BLH")

    # 4) Si se envía el formulario, persistimos el DF y guardamos
    if submitted:
        st.session_state[DF_KEY] = edited_df.copy()
        rows = _df_to_rows(st.session_state[DF_KEY])
        st.session_state[DATA_KEY] = rows
        st.session_state[COMPLETION_KEY] = any(p.get("personas", 0) > 0 for p in rows)

        if not ips_id:
            st.error("❌ No se encontró el identificador único de la IPS. Complete primero la sección de Identificación.")
            return

        flat_data = {
            "ips_id": ips_id,
            "personal_data": rows,                 # guardamos toda la tabla como lista de dicts
            COMPLETION_KEY: st.session_state[COMPLETION_KEY],
        }

        ok = append_or_update_row(flat_data, sheet_name=SHEET_NAME)
        if ok:
            st.success("✅ Datos de personal guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 12:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
    else:
        # Aunque no se envíe, conservamos el último DF en memoria
        st.session_state[DF_KEY] = edited_df.copy()
        st.session_state[DATA_KEY] = _df_to_rows(st.session_state[DF_KEY])
        st.session_state[COMPLETION_KEY] = any(p.get("personas", 0) > 0 for p in st.session_state[DATA_KEY])
