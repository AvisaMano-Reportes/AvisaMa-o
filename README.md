# 🦁📱 AVISAMAÑOS - Zaragoza Smart City Triage System

**Avisamaños** es un sistema integral de reporte de incidentes urbanos diseñado para la ciudad de Zaragoza. Combina la accesibilidad de Telegram con la potencia de la Inteligencia Artificial (Google Gemini) para automatizar el triaje de peligros en la vía pública y activar respuestas IoT en tiempo real.

Proyecto desarrollado durante el hackathon [THE_WAVE] por el equipo [CSV_ALPHA].

---

## ✨ Características Principales

* **🤖 Valoración Inteligente:** El sistema no requiere que el usuario sepa clasificar el peligro. Un modelo multimodal (Gemini 2.5 Flash) analiza la foto y la descripción enviada por el ciudadano para determinar la urgencia (Alto, Medio, Bajo).
* **📱 Accesibilidad Total:** Interfaz ciudadana basada en Telegram, sin necesidad de instalar nuevas aplicaciones.
* **📍 Geolocalización Precisa:** Captura de coordenadas GPS nativas para enviar a los equipos de mantenimiento al punto exacto.
* **🚨 Integración IoT (Simulada):** El sistema detecta incidentes de nivel "Alto" (ej. peligro inminente de caída) y envía señales de activación a la infraestructura urbana más cercana (ej. encender luz roja intermitente en farolas inteligentes).
* **📊 Dashboard de Control:** Panel web en tiempo real desarrollado con Streamlit para la monitorización de alertas.

---

## 🏗️ Arquitectura del Sistema

El flujo de información se divide en 4 capas:

1. **Captura (Frontend Ciudadano):** El usuario envía una foto, descripción y ubicación al bot de Telegram (`@Avisamanos_bot`).
2. **Procesamiento (Cerebro IA):** El script `bot.py` procesa los datos y consulta a la API de Google Gemini para evaluar el riesgo.
3. **Almacenamiento (Base de Datos):** Los reportes y la categorización de la IA se guardan de forma persistente en SQLite (`reportes.db`).
4. **Visualización y Acción (Dashboard):** El script `dashboard.py` lee la base de datos en tiempo real, mapea las incidencias y simula la activación de nodos IoT.

---
🛠️ Tecnologías Utilizadas
Lenguaje: Python

IA Generativa: google-genai (Modelo Gemini 2.5 Flash)

Bot API: pyTelegramBotAPI

Frontend Dashboard: Streamlit

Base de Datos: SQLite3 (Nativa en Python)

Generación de QR: qrcode
