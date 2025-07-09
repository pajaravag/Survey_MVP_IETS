# ──────────────────────────────────────────────
# Google Sheets Configuration
# ──────────────────────────────────────────────

GOOGLE_SHEET_ID = "1KusiBkYqlL33GmPQN2PfUripYUXVjmDtDG43H-pAmGQ"

# ──────────────────────────────────────────────
# 📁 Local Data Export Paths
# ──────────────────────────────────────────────

RESPONSES_DIR = "data/responses"
MASTER_CSV = f"{RESPONSES_DIR}/responses_master.csv"

# ──────────────────────────────────────────────
# 🔗 External Links
# ──────────────────────────────────────────────

INSTRUCTIVO_URL = "https://drive.google.com/your_instructivo_link_here"   # Optional: Link to the instruction manual

# ──────────────────────────────────────────────
# 📝 Survey Section Keys (for completion tracking)
# These must match the keys used in session_state for each section
# ──────────────────────────────────────────────

SURVEY_SECTIONS = [
    "identificacion",                # Sección de identificación inicial
    "datos_generales",               # 1. Datos Generales
    "procesos_realizados__data",     # 2. Procesos Estandarizados
    "donantes_receptores",           # 3. Donantes y Receptores
    "infraestructura_equipos",       # 4. Infraestructura y Equipos
    "insumos_mensuales",             # 5. Insumos Mensuales
    "personal_exclusivo",            # 6. Personal Asignado - exclusivo
    "personal_compartido",           # 6. Personal Asignado - compartido (si aplica)
    "servicios_publicos",            # 7. Servicios Públicos
    "transporte_modalidades",        # 8. Transporte y Recolección
    "calidad_seguridad",             # 9. Eficiencia y Calidad
    "depreciacion__data"             # 10. Depreciación e Impuestos
]
