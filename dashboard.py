import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import os

st.set_page_config(layout="wide", page_title="Panel de Control Municipal")

st.title("🚨 Panel de Control Municipal de Incidentes")
st.markdown("Monitorización en tiempo real de reportes ciudadanos y activación de nodos IoT en Zaragoza.")

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
            # Añadimos una tercera columna para el mapa
            col_img, col_info, col_map = st.columns([1, 2, 1.5])
            
            with col_img:
                if os.path.exists(row['ruta_foto']):
                    img = Image.open(row['ruta_foto'])
                    st.image(img, use_container_width=True)
                else:
                    st.warning("Imagen no encontrada")
                    
            with col_info:
                st.subheader(f"Reporte #{row['id']} - Prioridad: {row['categoria']}")
                st.write(f"**Fecha:** {row['fecha']}")
                st.write(f"**Coordenadas:** {row['latitud']}, {row['longitud']}")
                st.write(f"**Descripción:** {row['descripcion']}")
                
                if row['categoria'] == 'Alto':
                    st.error("🔴 ACCIÓN IOT: Foco rojo intermitente activado en farola inteligente.")
                else:
                    st.warning("🟡 ACCIÓN IOT: Notificación enviada a mantenimiento.")
            
            with col_map:
                # Mostrar mapa pequeño centrado en la incidencia
                map_data = pd.DataFrame({'lat': [row['latitud']], 'lon': [row['longitud']]})
                st.map(map_data, zoom=15)
                
            st.divider()