import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import os

st.set_page_config(layout="wide", page_title="Panel de Control Municipal")

st.title("🚨 Panel de Triaje - Smart City")
st.markdown("Monitorización en tiempo real de reportes ciudadanos y activación de nodos IoT.")

# Leer datos de SQLite
conn = sqlite3.connect('reportes.db')
df = pd.read_sql_query("SELECT * FROM incidencias", conn)
conn.close()

if df.empty:
    st.info("No hay reportes en la base de datos todavía.")
else:
    # Mostrar métricas rápidas
    col1, col2 = st.columns(2)
    col1.metric("Total de Incidencias", len(df))
    col2.metric("Peligros Inminentes", len(df[df['categoria'] == 'Peligro inminente de caída']))
    
    st.divider()

    # Mostrar las tarjetas de reportes
    for index, row in df.iterrows():
        with st.container():
            col_img, col_info = st.columns([1, 3])
            
            with col_img:
                if os.path.exists(row['ruta_foto']):
                    img = Image.open(row['ruta_foto'])
                    st.image(img, use_container_width=True)
                else:
                    st.warning("Imagen no encontrada")
                    
            with col_info:
                st.subheader(f"Reporte #{row['id']} - {row['categoria']}")
                st.write(f"**Fecha:** {row['fecha']}")
                st.write(f"**Descripción:** {row['descripcion']}")
                
                # Simulación visual del IoT para la presentación
                if row['categoria'] == 'Peligro inminente de caída':
                    st.error("🔴 ACCIÓN IOT: Foco rojo intermitente activado en la farola más cercana.")
                else:
                    st.warning("🟡 ACCIÓN IOT: Notificación estándar enviada a mantenimiento.")
            st.divider()