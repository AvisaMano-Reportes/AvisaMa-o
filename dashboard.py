import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import os
import qrcode
from io import BytesIO

st.set_page_config(layout="wide", page_title="Panel de Control Municipal")

st.title("🚨 Panel de Control Municipal de Incidentes")
st.markdown("Monitorización en tiempo real de reportes ciudadanos en Zaragoza")

# --- BARRA LATERAL CON QR ---
with st.sidebar:
    st.header("📱 ¡Pruébalo en directo!")
    st.write("Escanea este QR con la cámara de tu móvil para abrir el bot en Telegram:")
    
    # Generar el QR al vuelo
    # ¡IMPORTANTE! Cambia esto por el enlace real de tu bot
    enlace_bot = "https://t.me/AvisaManios_Reportes_Bot" 
    
    # 1. Creamos la imagen del QR
    img_qr = qrcode.make(enlace_bot)
    
    # 2. La convertimos a formato "bytes" para que Streamlit no se queje
    buffer = BytesIO()
    img_qr.save(buffer, format="PNG")
    imagen_bytes = buffer.getvalue()
    
    # 3. La mostramos usando el nuevo formato "width='stretch'" para quitar el aviso
    st.image(imagen_bytes, width="stretch")
    st.caption("1. Escanea el QR\n2. Dale a Iniciar\n3. ¡Manda una foto!")

# Conectar y leer datos
conn = sqlite3.connect('reportes.db')
try:
    df = pd.read_sql_query("SELECT * FROM incidencias", conn)
except:
    df = pd.DataFrame() # Evita error si la tabla no existe aún
conn.close()

if df.empty:
    st.info("No hay reportes en la base de datos todavía.")
else:
    col1, col2 = st.columns(2)
    col1.metric("Total de Incidencias", len(df))
    # Ajustado a tu nueva categoría 'Alto'
    col2.metric("Alertas Nivel Alto", len(df[df['categoria'] == 'Alto']))
    
    st.divider()

    for index, row in df.iterrows():
        with st.container():
            # Comprobamos si hay coordenadas (usamos pd.notnull para manejar el NULL de la DB)
            tiene_ubicacion = pd.notnull(row['latitud']) and pd.notnull(row['longitud'])

            if tiene_ubicacion:
                # Layout con mapa: 3 columnas
                col_img, col_info, col_map = st.columns([1, 2, 1.5])
            else:
                # Layout sin mapa: 2 columnas (la de info se expande)
                col_img, col_info = st.columns([1, 3.5])
            
            with col_img:
                if os.path.exists(row['ruta_foto']):
                    st.image(Image.open(row['ruta_foto']), use_container_width=True)
                    
            with col_info:
                st.subheader(f"Reporte #{row['id']} - {row['categoria']}")
                st.write(f"**Fecha:** {row['fecha']}")
                
                # Mostrar texto de ubicación solo si existe
                if tiene_ubicacion:
                    st.write(f"📍 **Coordenadas:** {row['latitud']}, {row['longitud']}")
                else:
                    st.caption("⚠️ Ubicación no proporcionada por el ciudadano.")
                
                st.write(f"**Descripción:** {row['descripcion']}")
                
                if row['categoria'] == 'Alto':
                    st.error("🔴 El reporte esta siendo analizado en estos momentos. ¡GRACIAS!")
                else:
                    st.warning("🟡 Notificación enviada. ¡GRACIAS!")

            # Solo creamos el mapa si hay datos
            if tiene_ubicacion:
                with col_map:
                    map_data = pd.DataFrame({'lat': [row['latitud']], 'lon': [row['longitud']]})
                    st.map(map_data, zoom=15)
                    
            st.divider()