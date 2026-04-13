import telebot
import sqlite3
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN = '8040777981:AAHivo5O7sgDFf00sYpoUEfZ2BIPb2lqJOs'
bot = telebot.TeleBot(TOKEN)

if not os.path.exists('fotos'):
    os.makedirs('fotos')

# --- BASE DE DATOS (Con Latitud y Longitud) ---
def init_db():
    conn = sqlite3.connect('reportes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            ruta_foto TEXT,
            categoria TEXT,
            descripcion TEXT,
            latitud REAL,
            longitud REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

user_data = {}

# --- LÓGICA DEL BOT ---
@bot.message_handler(commands=['start', 'reportar'])
def send_welcome(message):
    bot.reply_to(message, "¡Hola! Soy el bot del Ayuntamiento de Zaragoza. Por favor, envíame una FOTO del problema.")
    user_data[message.chat.id] = {}

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        foto_path = f"fotos/{message.chat.id}_{message.message_id}.jpg"
        with open(foto_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        user_data[message.chat.id]['ruta_foto'] = foto_path
        
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('Bajo', 'Medio', 'Alto')
        
        msg = bot.reply_to(message, "Foto guardada. ¿Qué nivel de peligro representa?", reply_markup=markup)
        bot.register_next_step_handler(msg, process_category_step)
    except Exception as e:
        bot.reply_to(message, "Error al procesar la foto.")

def process_category_step(message):
    user_data[message.chat.id]['categoria'] = message.text
    markup = telebot.types.ReplyKeyboardRemove()
    msg = bot.reply_to(message, "Nivel registrado. Escribe una breve DESCRIPCIÓN:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_description_step)

def process_description_step(message):
    user_data[message.chat.id]['descripcion'] = message.text
    
    # NUEVO: Pedir ubicación con botón especial
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn_gps = telebot.types.KeyboardButton("📍 Compartir Ubicación del Incidente", request_location=True)
    markup.add(btn_gps)
    
    msg = bot.reply_to(message, "¡Perfecto! Ahora pulsa el botón de abajo para enviar la ubicación exacta para los servicios municipales:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_location_step)

def process_location_step(message):
    chat_id = message.chat.id
    
    # Extraer coordenadas si el usuario pulsó el botón
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
    else:
        # Coordenadas por defecto (Plaza del Pilar) por si falla
        lat, lon = 41.6568, -0.8783

    conn = sqlite3.connect('reportes.db')
    cursor = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("INSERT INTO incidencias (fecha, ruta_foto, categoria, descripcion, latitud, longitud) VALUES (?, ?, ?, ?, ?, ?)",
                   (fecha_actual, user_data[chat_id]['ruta_foto'], user_data[chat_id]['categoria'], user_data[chat_id]['descripcion'], lat, lon))
    conn.commit()
    conn.close()
    
    bot.reply_to(message, "✅ ¡Reporte guardado con éxito! Se ha activado la alerta en el nodo IoT más cercano.", reply_markup=telebot.types.ReplyKeyboardRemove())

print("Bot en ejecución...")
bot.polling()