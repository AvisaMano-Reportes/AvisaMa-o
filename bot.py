import telebot
import sqlite3
import os
from datetime import datetime

# --- CONFIGURACIÓN ---
TOKEN = '8040777981:AAHivo5O7sgDFf00sYpoUEfZ2BIPb2lqJOs'
bot = telebot.TeleBot(TOKEN)

# Crear carpeta para fotos si no existe
if not os.path.exists('fotos'):
    os.makedirs('fotos')

# --- BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect('reportes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS incidencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            ruta_foto TEXT,
            categoria TEXT,
            descripcion TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- DICCIONARIO TEMPORAL PARA GUARDAR DATOS DEL USUARIO ---
user_data = {}

# --- LÓGICA DEL BOT ---
@bot.message_handler(commands=['start', 'reportar'])
def send_welcome(message):
    bot.reply_to(message, "¡Hola! Soy el bot del Ayuntamiento de Zaragoza. Por favor, envíame una FOTO del problema que quieres reportar.")
    user_data[message.chat.id] = {}

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    try:
        # Descargar y guardar la foto
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        foto_path = f"fotos/{message.chat.id}_{message.message_id}.jpg"
        with open(foto_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        user_data[message.chat.id]['ruta_foto'] = foto_path
        
        # Pedir categoría con botones (teclado personalizado)
        markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('Bajo', 'Medio', 'Alto')
        
        msg = bot.reply_to(message, "Foto guardada. ¿Qué nivel peligro representa?", reply_markup=markup)
        bot.register_next_step_handler(msg, process_category_step)
        
    except Exception as e:
        bot.reply_to(message, "Hubo un error al procesar la foto.")

def process_category_step(message):
    user_data[message.chat.id]['categoria'] = message.text
    # Quitar el teclado
    markup = telebot.types.ReplyKeyboardRemove()
    msg = bot.reply_to(message, "Nivel de peligro registrado. Por último, escribe una breve DESCRIPCIÓN del lugar y del problema:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_description_step)

def process_description_step(message):
    chat_id = message.chat.id
    descripcion = message.text
    
    # Guardar todo en la Base de Datos
    conn = sqlite3.connect('reportes.db')
    cursor = conn.cursor()
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("INSERT INTO incidencias (fecha, ruta_foto, categoria, descripcion) VALUES (?, ?, ?, ?)",
                   (fecha_actual, user_data[chat_id]['ruta_foto'], user_data[chat_id]['categoria'], descripcion))
    conn.commit()
    conn.close()
    
    bot.reply_to(message, "✅ ¡Reporte guardado con éxito! Los servicios municipales han sido notificados y se atenderá lo antes posible. ¡Gracias!")

# Iniciar el bot
print("Bot en ejecución...")
bot.polling()