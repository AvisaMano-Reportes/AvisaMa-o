import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import os
import qrcode
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
# Optimización de la interfaz para aprovechar todo el ancho de pantalla
st.set_page_config(layout="wide", page_title="AVISAMAÑOS - Panel de Control")

# --- INYECCIÓN DE CSS PARA PERSONALIZAR LA INTERFAZ ---
# Modificación del DOM de Streamlit
estilo_personalizado = """
<style>
    /* Ocultar elementos nativos de Streamlit para un acabado más profesional */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Enfatizar métricas con la identidad visual corporativa */
    [data-testid="stMetricValue"] {
        font-size: 3rem;
        color: #E3001B; /* Rojo Corporativo Zaragoza/Avisamaños */
    }
</style>
"""
st.markdown(estilo_personalizado, unsafe_allow_html=True)

# --- BARRA LATERAL ---
with st.sidebar:
    # Carga dinámica del logotipo
    ruta_logo = "logo_avisamanos.png" 
    
    if os.path.exists(ruta_logo):
        # El parámetro width="stretch" asegura adaptabilidad en el contenedor lateral
        st.image(ruta_logo, width="stretch")
    else:
        st.error(f"❌ Recurso no encontrado: {ruta_logo}")
    
    st.divider()

    # Generación dinámica de código QR para acceso al bot
    st.header("📱 ¡Pruébalo en directo!")
    st.write("Escanea este QR con tu móvil para abrir el bot:")
    
    enlace_bot = "https://t.me/AvisaManios_Reportes_Bot" # Endpoint de Telegram
    
    # Generación de QR en memoria para evitar latencia de lectura/escritura en disco
    img_qr = qrcode.make(enlace_bot)
    buffer = BytesIO()
    img_qr.save(buffer, format="PNG")
    imagen_bytes = buffer.getvalue()
    
    st.image(imagen_bytes, width="stretch")
    st.caption("1. Escanea el QR\n2. Dale a Iniciar\n3. ¡Manda una foto!")

# --- PANEL DE CONTROL PRINCIPAL ---
st.title("🚨 AVISAMAÑOS - Bot de Incidentes")
st.markdown("Monitorización en tiempo real de reportes ciudadanos y activación de nodos IoT en Zaragoza.")

# --- CAPA DE DATOS ---
# Conexión persistente a la base de datos compartida con el bot
conn = sqlite3.connect('reportes.db')
try:
    # Extracción de datos mediante Pandas para facilitar el análisis y filtrado
    df = pd.read_sql_query("SELECT * FROM incidencias ORDER BY id DESC", conn)
except Exception as e:
    df = pd.DataFrame() # Fallback en caso de tabla inexistente o error de lectura
conn.close()

# --- LÓGICA DE REPRESENTACIÓN ---
if df.empty:
    st.info("No hay reportes en la base de datos todavía.")
else:
    # KPIs Superiores: Resumen ejecutivo del estado del sistema
    col1, col2 = st.columns(2)
    col1.metric("Total de Incidencias", len(df))
    # Segmentación por prioridad crítica
    col2.metric("Alertas Prioridad Alta", len(df[df['categoria'] == 'Alto']))
    
    st.divider()

    # Renderizado iterativo de tarjetas de incidentes
    for index, row in df.iterrows():
        with st.container():
            # Evaluación de geolocalización para determinar el layout dinámico
            tiene_ubicacion = pd.notnull(row['latitud']) and pd.notnull(row['longitud'])
            
            # Si hay ubicación, se reserva espacio para el mapa (3 columnas), si no, solo 2.
            if tiene_ubicacion:
                col_img, col_info, col_map = st.columns([1, 2, 1.5])
            else:
                col_img, col_info = st.columns([1, 3.5])
            
            # Columna 1: Evidencia Visual
            with col_img:
                if os.path.exists(row['ruta_foto']):
                    st.image(Image.open(row['ruta_foto']), width="stretch")
                else:
                    st.warning("Imagen no encontrada")
                    
            # Columna 2: Detalles y Estado de Respuesta IoT
            with col_info:
                st.subheader(f"Reporte #{row['id']} - Prioridad: {row['categoria']}")
                st.write(f"**Fecha:** {row['fecha']}")
                
                if tiene_ubicacion:
                    st.write(f"📍 **Coordenadas:** {row['latitud']}, {row['longitud']}")
                else:
                    st.caption("⚠️ Ubicación no proporcionada por el ciudadano.")
                
                st.write(f"**Descripción:** {row['descripcion']}")
                
                # Feedback visual de la acción automatizada (Simulación de actuadores IoT)
                if row['categoria'] == 'Alto':
                    st.error("🔴 Notificación PRIORITARIA enviada")
                else:
                    st.warning("🟡 Notificación enviada")
            
            # Columna 3 (Opcional): Contexto Geoespacial
            if tiene_ubicacion:
                with col_map:
                    # Preparación de DataFrame específico para el componente map de Streamlit
                    map_data = pd.DataFrame({'lat': [row['latitud']], 'lon': [row['longitud']]})
                    st.map(map_data, zoom=15)
                
            st.divider()