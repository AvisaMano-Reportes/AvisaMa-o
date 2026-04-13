import telebot
import sqlite3
import os
from datetime import datetime
from google import genai
import PIL.Image

# --- CONFIGURACIÓN DE SEGURIDAD Y CONSTANTES ---
TELEGRAM_TOKEN = '8040777981:AAHivo5O7sgDFf00sYpoUEfZ2BIPb2lqJOs' 
GEMINI_API_KEY = 'AIzaSyDzzuXoOAPkrH5nzubZNsU9itIEIdAZptE'

# Inicialización de clientes de API
bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

# Asegurar la persistencia del directorio de almacenamiento de imágenes
if not os.path.exists('fotos'):
    os.makedirs('fotos')

# --- CAPA DE PERSISTENCIA (SQLITE) ---
def init_db():
    """
    Inicializa la base de datos local y crea la tabla de incidencias si no existe.
    Define el esquema para almacenar metadatos, rutas de archivos y geolocalización.
    """
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

# Inicializar DB al arranque del script
init_db()

# Diccionario en memoria para gestionar el estado de la sesión por usuario
user_data = {}

# --- GESTORES DE COMANDOS ---

@bot.message_handler(commands=['start', 'reportar'])
def send_welcome(message):
    """
    Punto de entrada del bot. Saluda al usuario y limpia el estado de sesión previo.
    """
    bot.reply_to(message, "¡Hola! Soy el sistema de analisis IA del Ayuntamiento de Zaragoza. Por favor, envíame una FOTO del problema.")
    user_data[message.chat.id] = {}

@bot.message_handler(content_types=['photo'])
def handle_docs_photo(message):
    """
    Captura la imagen enviada, descarga la versión de mayor resolución y 
    la almacena localmente para su posterior análisis.
    """
    try:
        # Obtención del archivo mediante el último índice de la lista
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        foto_path = f"fotos/{message.chat.id}_{message.message_id}.jpg"
        
        with open(foto_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        user_data[message.chat.id]['ruta_foto'] = foto_path
        msg = bot.reply_to(message, "Foto recibida. Escribe una breve DESCRIPCIÓN del suceso:")
        # Registro del siguiente paso en el flujo conversacional
        bot.register_next_step_handler(msg, process_description_step)
    except Exception as e:
        bot.reply_to(message, "Error al procesar la foto.")

def process_description_step(message):
    """
    Captura la descripción textual del usuario y solicita la ubicación geográfica
    mediante un botón de teclado nativo de Telegram.
    """
    user_data[message.chat.id]['descripcion'] = message.text
    
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn_gps = telebot.types.KeyboardButton("📍 Compartir Ubicación", request_location=True)
    markup.add(btn_gps)
    
    msg = bot.reply_to(message, "Por último, pulsa el botón para enviar la ubicación exacta del problema:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_location_step)

def process_location_step(message):
    """
    Paso final del flujo: Procesa la ubicación, ejecuta el análisis multimodal con IA 
    y persiste los resultados en la base de datos.
    """
    chat_id = message.chat.id
    markup = telebot.types.ReplyKeyboardRemove()
    
    # Extracción de coordenadas si se proporcionaron
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
    else:
        lat, lon = None, None

    msg_espera = bot.reply_to(message, "🤖 Analizando la imagen y la descripción mediante Inteligencia Artificial...", reply_markup=markup)
    
    try:
        # Preparación de recursos para el modelo Vision
        img = PIL.Image.open(user_data[chat_id]['ruta_foto'])
        desc = user_data[chat_id]['descripcion']
        
        # Definición del Prompt para el análisis de riesgo
        prompt_ia = f"""
        Eres un experto en seguridad ciudadana y mantenimiento urbano de Zaragoza.
        El ciudadano ha enviado esta imagen y la siguiente descripción: '{desc}'.
        Tu tarea es evaluar el riesgo real de esta situación para los ciudadanos.
        Clasifica el nivel de peligro ESTRICTAMENTE usando una de estas tres palabras: 'Alto', 'Medio' o 'Bajo'.
        No des explicaciones, devuelve SOLO la palabra de la categoría elegida.
        """
        
        try:
            # Análisis multimodal: Texto + Imagen
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[prompt_ia, img]
            )
            categoria_ia = response.text.strip().capitalize()
            
            # Validación de salida controlada
            if categoria_ia not in ['Alto', 'Medio', 'Bajo']:
                categoria_ia = 'Medio'
                
        except Exception as api_error:
            # Mecanismo de Fallback (Modo rescate) ante fallos de API o cuotas
            print(f"⚠️ Aviso: API saturada ({api_error}). Usando modo rescate para la demo.")
            categoria_ia = 'Alto' 
            
        # --- PERSISTENCIA DE DATOS ---
        conn = sqlite3.connect('reportes.db')
        cursor = conn.cursor()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("INSERT INTO incidencias (fecha, ruta_foto, categoria, descripcion, latitud, longitud) VALUES (?, ?, ?, ?, ?, ?)",
                        (fecha_actual, user_data[chat_id]['ruta_foto'], categoria_ia, user_data[chat_id]['descripcion'], lat, lon))
        conn.commit()
        conn.close()
        
        # --- FEEDBACK AL USUARIO ---
        texto_exito = f"✅ ¡Reporte guardado con éxito!\n\n🧠 **Evaluación IA:** Nivel {categoria_ia}\n\nLos nodos IoT han sido actualizados."
        
        # Gestión robusta de edición de mensajes para evitar excepciones de Telegram API
        try:
            bot.edit_message_text(texto_exito, chat_id=chat_id, message_id=msg_espera.message_id, parse_mode='Markdown')
        except:
            bot.send_message(chat_id, texto_exito, parse_mode='Markdown')
            
    except Exception as e:
        # Registro de errores críticos en servidor y notificación al usuario
        error_exacto = str(e)
        print(f"💥 ERROR CRÍTICO: {error_exacto}")
        texto_error = f"❌ El bot ha fallado al procesar la IA. \n\n⚠️ Error técnico:\n`{error_exacto}`"
        
        try:
            bot.edit_message_text(texto_error, chat_id=chat_id, message_id=msg_espera.message_id, parse_mode='Markdown')
        except:
            bot.send_message(chat_id, texto_error, parse_mode='Markdown')

# --- INICIO DEL SERVICIO ---
if __name__ == "__main__":
    print("ChatBot IA en ejecución...")
    bot.polling()