# utils/constants.py

# Encabezados esenciales para la sección de introducción
INTRO_HEADERS = [
    "intro__id_ips",
    "intro__nombre_ips",
    "intro__nit_ips",
    "intro__departamento",
    "intro__municipio",
    "intro__direccion",
    "intro__telefono",
    "intro__correo_electronico",
    "intro__nombre_encuestador",
    "intro__correo_encuestador",
    "identificacion__ips_id"  # clave obligatoria para identificar registros
]

# Claves mínimas requeridas por sección para garantizar un guardado correcto y coherente
MINIMUM_HEADERS_BY_SECTION = {
    "intro__": [
        "id_ips",
        "form_started",
        "section_started_at"
    ],
    "datos_generales__": [
        "nombre_inst",
        "tipo_inst",
        "anio_impl",
        "procesos_estandarizados",
        "otros_procesos"
    ],
    "identificacion__": [
        "ips_id",
        "correo_responsable",
        "nombre_responsable",
        "telefono_responsable"
    ],
    "costs_blh__": (
        ["ips_id"] +
        [f"costos_{proc}" for proc in [
            "Captación, selección y acompañamiento de usuarias",
            "Extracción y conservación",
            "Transporte",
            "Recepción",
            "Almacenamiento",
            "Deshielo",
            "Selección y clasificación",
            "Reenvasado",
            "Pasteurización",
            "Control microbiológico",
            "Distribución",
            "Seguimiento y trazabilidad"
        ]] +
        [f"actividades_{proc}" for proc in [
            "Captación, selección y acompañamiento de usuarias",
            "Extracción y conservación",
            "Transporte",
            "Recepción",
            "Almacenamiento",
            "Deshielo",
            "Selección y clasificación",
            "Reenvasado",
            "Pasteurización",
            "Control microbiológico",
            "Distribución",
            "Seguimiento y trazabilidad"
        ]] +
        ["costs_blh__completed"]
    )
}

