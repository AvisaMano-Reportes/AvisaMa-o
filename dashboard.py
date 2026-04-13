import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import os
import qrcode
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(layout="wide", page_title="AVISAMAÑOS - Panel de Control")

# --- INYECCIÓN DE CSS PARA PERSONALIZAR LA INTERFAZ ---
# Ocultamos menús por defecto para que parezca una app nativa.
estilo_personalizado = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Personalizamos las métricas para que destaquen con el color principal */
    [data-testid="stMetricValue"] {
        font-size: 3rem;
        color: #E3001B; /* Rojo Carmesí Avisamaños */
    }
</style>
"""
st.markdown(estilo_personalizado, unsafe_allow_html=True)

# --- BARRA LATERAL (Sidebar) CON LOGO Y QR ---
with st.sidebar:
    # 1. MOSTRAR EL LOGO
    # Asegúrate de que el nombre del archivo coincida con el tuyo real
    ruta_logo = "logo_avisamanos.png" 
    
    if os.path.exists(ruta_logo):
        # width='stretch' elimina el aviso de use_container_width
        st.image(ruta_logo, width="stretch")
    else:
        st.error(f"❌ No se encontró el logo: {ruta_logo}")
    
    st.divider()

    # 2. GENERAR Y MOSTRAR EL QR
    st.header("📱 ¡Pruébalo en directo!")
    st.write("Escanea este QR con tu móvil para abrir el bot:")
    
    # ¡IMPORTANTE! Cambia esto por el enlace real de tu bot
    enlace_bot = "https://t.me/pon_tu_bot_aqui" 
    
    img_qr = qrcode.make(enlace_bot)
    
    # Lo convertimos a bytes para Streamlit
    buffer = BytesIO()
    img_qr.save(buffer, format="PNG")
    imagen_bytes = buffer.getvalue()
    
    st.image(imagen_bytes, width="stretch")
    st.caption("1. Escanea el QR\n2. Dale a Iniciar\n3. ¡Manda una foto!")

# --- PANEL PRINCIPAL ---
st.title("🚨 AVISAMAÑOS - Bot de Incidentes")
st.markdown("Monitorización en tiempo real de reportes ciudadanos y activación de nodos IoT en Zaragoza.")

# Conectar y leer datos
conn = sqlite3.connect('reportes.db')
try:
    df = pd.read_sql_query("SELECT * FROM incidencias", conn)
except:
    df = pd.DataFrame()
conn.close()

if df.empty:
    st.info("No hay reportes en la base de datos todavía.")
else:
    col1, col2 = st.columns(2)
    col1.metric("Total de Incidencias", len(df))
    # Ajustado a tu nueva categoría 'Alto'
    col2.metric("Alertas Prioridad Alta", len(df[df['categoria'] == 'Alto']))
    
    st.divider()

    for index, row in df.iterrows():
        with st.container():
            # Layout dinámico: con o sin mapa
            tiene_ubicacion = pd.notnull(row['latitud']) and pd.notnull(row['longitud'])
            
            if tiene_ubicacion:
                col_img, col_info, col_map = st.columns([1, 2, 1.5])
            else:
                col_img, col_info = st.columns([1, 3.5])
            
            with col_img:
                if os.path.exists(row['ruta_foto']):
                    st.image(Image.open(row['ruta_foto']), width="stretch")
                else:
                    st.warning("Imagen no encontrada")
                    
            with col_info:
                st.subheader(f"Reporte #{row['id']} - Prioridad: {row['categoria']}")
                st.write(f"**Fecha:** {row['fecha']}")
                
                if tiene_ubicacion:
                    st.write(f"📍 **Coordenadas:** {row['latitud']}, {row['longitud']}")
                else:
                    st.caption("⚠️ Ubicación no proporcionada por el ciudadano.")
                
                st.write(f"**Descripción:** {row['descripcion']}")
                
                if row['categoria'] == 'Alto':
                    st.error("🔴 ACCIÓN IOT: Foco rojo intermitente activado en farola inteligente.")
                else:
                    st.warning("🟡 ACCIÓN IOT: Notificación enviada a mantenimiento.")
            
            if tiene_ubicacion:
                with col_map:
                    map_data = pd.DataFrame({'lat': [row['latitud']], 'lon': [row['longitud']]})
                    st.map(map_data, zoom=15)
                
            st.divider()