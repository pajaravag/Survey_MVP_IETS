import streamlit as st
from utils.forms.validators import safe_int, safe_float

def ensure_session_dict(key: str) -> dict:
    """
    Garantiza que la clave de session_state sea un diccionario.
    Si no lo es (o no existe), la inicializa como dict vacío.
    """
    if not isinstance(st.session_state.get(key), dict):
        st.session_state[key] = {}
    return st.session_state[key]


def render_equipment_entry_section(title: str, schema: dict, state_key: str):
    """
    Renderiza una sección jerárquica de entrada de equipos por proceso y ambiente.

    Args:
        title (str): Título mostrado en la interfaz.
        schema (dict): Estructura de referencia {proceso: {ambiente: [equipos]}}.
        state_key (str): Clave en session_state donde se almacenarán los datos.
    """
    st.markdown(f"### 🧱 {title}")
    stored_data = ensure_session_dict(state_key)
    updated_data = {}

    for proceso, ambientes in schema.items():
        st.subheader(f"🔹 {proceso}")

        for ambiente, equipos in ambientes.items():
            with st.expander(f"🏗️ Ambiente: {ambiente}"):
                ambiente_data = stored_data.get(proceso, {}).get(ambiente, {})

                for equipo in equipos:
                    equipo_data = ambiente_data.get(equipo, {})

                    st.markdown(f"**🛠️ Equipo:** {equipo}")
                    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 2, 2])

                    cantidad = col1.number_input(
                        "Cantidad",
                        min_value=0,
                        step=1,
                        value=safe_int(equipo_data.get("cantidad", 0)),
                        key=f"{state_key}_{proceso}_{ambiente}_{equipo}_cantidad"
                    )

                    anio_default = safe_int(equipo_data.get("anio", 0))
                    if anio_default < 1900 or anio_default > 2100:
                        anio_default = 2024  # ✅ Valor predeterminado válido

                    anio = col2.number_input(
                        "Año de compra",
                        min_value=1900,
                        max_value=2100,
                        step=1,
                        value=anio_default,
                        key=f"{state_key}_{proceso}_{ambiente}_{equipo}_anio"
                    )


                    vida_util = col3.number_input(
                        "Vida útil (años)",
                        min_value=0,
                        max_value=100,
                        step=1,
                        value=safe_int(equipo_data.get("vida_util", 0)),
                        key=f"{state_key}_{proceso}_{ambiente}_{equipo}_vida_util"
                    )

                    costo_unidad = col4.number_input(
                        "Costo por unidad (COP)",
                        min_value=0.0,
                        step=1000.0,
                        format="%0.0f",
                        value=safe_float(equipo_data.get("costo_unidad", 0.0)),
                        key=f"{state_key}_{proceso}_{ambiente}_{equipo}_costo_unidad"
                    )

                    costo_mantenimiento = col5.number_input(
                        "Costo anual mantenimiento (COP)",
                        min_value=0.0,
                        step=1000.0,
                        format="%0.0f",
                        value=safe_float(equipo_data.get("costo_mantenimiento", 0.0)),
                        key=f"{state_key}_{proceso}_{ambiente}_{equipo}_costo_mantenimiento"
                    )

                    updated_data \
                        .setdefault(proceso, {}) \
                        .setdefault(ambiente, {})[equipo] = {
                            "cantidad": cantidad,
                            "anio": anio,
                            "vida_util": vida_util,
                            "costo_unidad": costo_unidad,
                            "costo_mantenimiento": costo_mantenimiento
                        }

    st.session_state[state_key] = updated_data


def extract_flat_equipment_data(state_key: str) -> list[dict]:
    """
    Aplana los datos estructurados de equipos (por proceso/ambiente) a una lista de dicts.

    Args:
        state_key (str): Clave en session_state con la estructura de datos.

    Returns:
        List[dict]: Lista plana con los campos 'proceso', 'ambiente', 'equipo' y datos asociados.
    """
    data = st.session_state.get(state_key, {})
    if not isinstance(data, dict):
        return []

    flat = []
    for proceso, ambientes in data.items():
        for ambiente, equipos in ambientes.items():
            for equipo, valores in equipos.items():
                flat.append({
                    "proceso": proceso,
                    "ambiente": ambiente,
                    "equipo": equipo,
                    **valores
                })
    return flat
