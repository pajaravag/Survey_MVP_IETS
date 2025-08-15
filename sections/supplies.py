import re
import streamlit as st
from utils.state_manager import get_current_ips_id, get_current_ips_nombre
from utils.sheet_io import batch_append_or_update_rows
from utils.ui_styles import render_info_box, render_compact_example_box
from utils.google_sheets_client import get_google_sheet_df

# ──────────────────────────────────────────────
PREFIX = "insumos_detalle__"
SHEET_NAME = "Insumos"
LOADED_FLAG = PREFIX + "loaded"
NAME_KEY = PREFIX + "nombre_inst"
COMPLETION_KEY = PREFIX + "completed"

# ──────────────────────────────────────────────
# Helpers
def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def _slug(s: str) -> str:
    # clave estable, sin espacios/acentos/símbolos raros
    return re.sub(r"[^a-zA-Z0-9]+", "_", str(s)).strip("_").lower()

def _key_for(proceso: str, insumo: str, field: str) -> str:
    return f"{PREFIX}{_slug(proceso)}__{_slug(insumo)}__{field}"

def _load_saved_insumos(ips_id: str) -> dict:
    """
    Lee todas las filas guardadas en la hoja 'Insumos' para esta IPS y
    las agrupa como: { proceso: { insumo: {unidad, cantidad, costo} } }
    """
    try:
        df = get_google_sheet_df(sheet_name=SHEET_NAME)
    except Exception:
        return {}

    if df.empty or "ips_id" not in df.columns:
        return {}

    mask = df["ips_id"].astype(str).str.strip().str.lower() == ips_id.strip().lower()
    df = df[mask]
    if df.empty:
        return {}

    # Normaliza columnas esperadas
    for col in ["proceso", "insumo", "unidad", "cantidad", "costo"]:
        if col not in df.columns:
            df[col] = ""

    nested = {}
    for _, row in df.iterrows():
        proceso = str(row.get("proceso", "")).strip()
        insumo = str(row.get("insumo", "")).strip()
        unidad = str(row.get("unidad", "")).strip()
        cantidad = safe_float(row.get("cantidad", 0))
        costo = safe_float(row.get("costo", 0))
        if proceso and insumo:
            nested.setdefault(proceso, {})[insumo] = {
                "unidad": unidad,
                "cantidad": cantidad,
                "costo": costo
            }
    return nested

# ──────────────────────────────────────────────
# Catálogo fijo
PROCESOS_INSUMOS = {
    "Captación, selección y acompañamiento de usuarias": [
        "Gorros", "Tapabocas", "Bata desechable", "Guantes",
        "Polainas desechables", "Frascos de vidrio"
    ],
    "Extracción y conservación": [
        "Frascos de vidrio tapa rosca (230 ml)", "Frascos de vidrio tapa rosca (130 ml)",
        "Tapas plásticas (230 ml)", "Tapas plásticas (130 ml)", "Rótulos", "Jabón quirúrgico",
        "Alcohol al 70°", "Antibacterial", "Toallas de papel",
        "Punteras azules (1000 μL)", "Punteras blancas (5000 μL)", "Bolsas plásticas"
    ],
    "Recepción – recolección y almacenamiento": [
        "Jabón quirúrgico", "Gel refrigerante", "Paños humedecidos con alcohol 70%"
    ],
    "Selección y clasificación": [
        "Agua desionizada", "Fenolftaleína 1%", "Tubo capilar sin heparina",
        "Tubos microhematocritos fco x 100"
    ],
    "Pasteurización": [
        "Agua desionizada", "Hidróxido de sodio (Solución Dornic)"
    ],
    "Control microbiológico": [
        "Caldo de bilis-verde brillante al 2%", "Alcohol al 96°", "Desinfectante",
        "Tubos de ensayo 13x100 mm", "Tubos de ensayo 160x16 mm", "Asa bacteriológica desechable",
        "Medio cultivo (agar sangre)", "Rejillas - portatubos", "Churruscos para lavado de tubos"
    ],
    "Reenvasado": [
        "Rótulos", "Frascos de vidrio"
    ],
    "Otros": [
        "Otro insumo 1", "Otro insumo 2", "Otro insumo 3"
    ],
}

# ──────────────────────────────────────────────
def render():
    st.header("7. 💊 Insumos del Banco de Leche Humana (Pregunta 21)")

    # Nombre IPS (sin value+key conflict)
    if NAME_KEY not in st.session_state:
        st.session_state[NAME_KEY] = get_current_ips_nombre() or ""
    st.text_input("🏥 Nombre completo y oficial de la institución:", key=NAME_KEY, disabled=True)

    st.markdown(render_info_box("""
**ℹ️ ¿Qué información debe registrar?**  
Registre los **insumos utilizados mensualmente** por el BLH. Para cada uno indique:

- Unidad de medida  
- Cantidad promedio mensual  
- Costo promedio por unidad (COP)

Si no aplica, registre **0**. Puede usar la categoría **"Otros"** para registrar insumos no listados.
"""), unsafe_allow_html=True)

    st.markdown(render_compact_example_box("""
📝 **Ejemplo práctico:**

| Proceso              | Insumo           | Unidad  | Cantidad | Costo unitario |
|----------------------|------------------|---------|----------|----------------|
| Captación            | Gorros           | Unidad  | 1,000    | 550            |
| Extracción           | Jabón quirúrgico | Litro   | 10       | 6,780          |
| Microbiológico       | Alcohol 96°      | Litro   | 5        | 15,000         |
"""), unsafe_allow_html=True)

    ips_id = get_current_ips_id()
    if not ips_id:
        st.warning("⚠️ Debe completar la **Identificación de la IPS** antes de continuar.", icon="⚠️")
        st.stop()

    # ───── Precarga desde Sheets: inicializa session_state por widget UNA SOLA VEZ
    if not st.session_state.get(LOADED_FLAG, False):
        saved_map = _load_saved_insumos(ips_id)  # {proceso: {insumo: {unidad, cantidad, costo}}}
        for proceso, insumos in PROCESOS_INSUMOS.items():
            for insumo in insumos:
                d = saved_map.get(proceso, {}).get(insumo, {})
                k_unidad = _key_for(proceso, insumo, "unidad")
                k_cantidad = _key_for(proceso, insumo, "cantidad")
                k_costo = _key_for(proceso, insumo, "costo")
                # Inicializa sólo si no existen
                if k_unidad not in st.session_state:
                    st.session_state[k_unidad] = str(d.get("unidad", "") or "")
                if k_cantidad not in st.session_state:
                    st.session_state[k_cantidad] = safe_float(d.get("cantidad", 0.0))
                if k_costo not in st.session_state:
                    st.session_state[k_costo] = safe_float(d.get("costo", 0.0))

        st.session_state[LOADED_FLAG] = True

    # ───── Form para evitar reruns al cambiar de celda
    with st.form(PREFIX + "form", clear_on_submit=False):
        for proceso, insumos in PROCESOS_INSUMOS.items():
            with st.expander(f"🔹 {proceso}"):
                for insumo in insumos:
                    k_unidad = _key_for(proceso, insumo, "unidad")
                    k_cantidad = _key_for(proceso, insumo, "cantidad")
                    k_costo = _key_for(proceso, insumo, "costo")
                    col1, col2, col3 = st.columns([2, 2, 2])
                    with col1:
                        st.text_input(f"Unidad de medida - {insumo}", key=k_unidad)
                    with col2:
                        st.number_input(f"Cantidad mensual - {insumo}", min_value=0.0, step=1.0, key=k_cantidad)
                    with col3:
                        st.number_input(f"Costo por unidad (COP) - {insumo}", min_value=0.0, step=100.0, key=k_costo)

        submitted = st.form_submit_button("💾 Guardar sección - Insumos (Pregunta 21)")

    # ───── Recolecta y guarda cuando se envía el formulario
    if submitted:
        # Construye filas planas desde session_state
        filas_insumos = []
        for proceso, insumos in PROCESOS_INSUMOS.items():
            for insumo in insumos:
                k_unidad = _key_for(proceso, insumo, "unidad")
                k_cantidad = _key_for(proceso, insumo, "cantidad")
                k_costo = _key_for(proceso, insumo, "costo")
                unidad = (st.session_state.get(k_unidad) or "").strip()
                cantidad = safe_float(st.session_state.get(k_cantidad, 0.0))
                costo = safe_float(st.session_state.get(k_costo, 0.0))
                filas_insumos.append({
                    "ips_id": ips_id,
                    "proceso": proceso,
                    "insumo": insumo,
                    "unidad": unidad,
                    "cantidad": cantidad,
                    "costo": costo,
                })

        # Completitud: al menos una cantidad o costo > 0
        st.session_state[COMPLETION_KEY] = any(
            (row["cantidad"] > 0) or (row["costo"] > 0) for row in filas_insumos
        )

        if not filas_insumos:
            st.warning("Debe ingresar al menos un insumo para guardar.")
            return

        ok = batch_append_or_update_rows(filas_insumos, sheet_name=SHEET_NAME, ips_id=ips_id)
        if ok:
            st.success("✅ Datos de insumos guardados correctamente.")
            if "section_index" in st.session_state and st.session_state.section_index < 10:
                st.session_state.section_index += 1
                st.session_state.navigation_triggered = True
                st.rerun()
        else:
            st.error("❌ Error al guardar los datos. Por favor intente nuevamente.")
