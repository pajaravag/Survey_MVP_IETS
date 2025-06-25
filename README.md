# 📈 Encuesta para Bancos de Leche Humana (BLH) – IETS

Este repositorio contiene una aplicación interactiva desarrollada con [Streamlit](https://streamlit.io) para recolectar información estructurada desde IPS (Instituciones Prestadoras de Salud) sobre la operación, costos y procesos relacionados con Bancos de Leche Humana (BLH) en Colombia.

---

## 🌟 Objetivo

Recoger datos confiables y comparables para permitir:

* Estimaciones económicas de operación de BLH
* Evaluaciones de eficiencia, calidad y uso de recursos
* Generación de evidencia para toma de decisiones en salud pública

---

## 🧹 Secciones del Formulario

1. Identificación del Diligenciante
2. Datos Generales
3. Procesos Estandarizados
4. Donantes y Receptores
5. Infraestructura y Equipos
6. Insumos Mensuales
7. Personal Asignado
8. Servicios Públicos
9. Transporte y Recolección
10. Eficiencia y Calidad
11. Depreciación e Impuestos

---

## 🚀 ¿Cómo usar esta app?

### ▶️ Ejecución local

```bash
# Clona este repositorio
git clone https://github.com/iets-blh/encuesta-blh.git
cd encuesta-blh

# Crea un entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instala dependencias
pip install -r requirements.txt

# Ejecuta la app
streamlit run main.py
```

---

## 🔐 Configuración de Acceso a Google Sheets

Para permitir la conexión segura con Google Sheets:

1. Crea un proyecto en [Google Cloud Console](https://console.cloud.google.com/)
2. Habilita la API de Google Sheets
3. Crea una cuenta de servicio y descarga la credencial `.json`
4. Copia el contenido del `.json` en `.streamlit/secrets.toml` con este formato:

```toml
[gspread]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "..."
client_id = "..."
...

[sheet]
name = "BLH_Encuesta_Respuestas"
```

> ⚠️ **Nunca subas `secrets.toml` al repositorio.** Está en `.gitignore`.

5. Comparte la hoja de cálculo con `client_email` con permisos de editor.

---

## ☁️ Despliegue en Streamlit Cloud

1. Sube el repositorio a GitHub
2. En [Streamlit Cloud](https://streamlit.io/cloud), crea una app enlazada al repo
3. En el panel de configuración de la app:

   * Copia el contenido de `secrets.toml` en `Settings → Secrets`
   * Guarda y despliega
4. Comparte el enlace con las IPS

---

## 🧪 Funcionalidades clave

* ✔️ Navegación por secciones con progreso
* ✔️ Guardado parcial por IPS
* ✔️ Reanudación de sesión si el IPS vuelve a ingresar
* ✔️ Validación en campos críticos
* ✔️ Exportación directa a Google Sheets

---

## 📁 Estructura del proyecto

```bash
.
├── main.py                  # Script principal de la app
├── sections/                # Cada sección del formulario
├── utils/                   # Utilidades para estado y conexión Sheets
├── assets/                 # Logos o imágenes
├── data/                   # Carpeta para CSV locales (opcional)
├── requirements.txt         # Dependencias del entorno
├── .streamlit/secrets.toml  # Configuración segura (no se sube)
```

---

## 🧐 Créditos y contacto

Este proyecto es desarrollado por el equipo técnico de IETS en colaboración con expertos en salud pública, economía y análisis de datos. Para soporte técnico o contribuciones, contacta a:

📧 [pablo.jarava@iets.org.co](mailto:pablo.jarava@iets.org.co)

---

> Última actualización: Junio 2025
