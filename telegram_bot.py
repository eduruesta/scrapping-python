#!/usr/bin/env python
import os
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import subprocess
import glob

# Configuración de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()  # Cargará variables del archivo .env si existe

# Intentar obtener el token primero de las variables de entorno del sistema (Render)
# y si no está disponible, del archivo .env
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envía un mensaje cuando se emite el comando /start."""
    await update.message.reply_text(
        "¡Hola! Soy el bot de Hockey Standings. Usa 'resultados' para ejecutar el script o 'resultados retry' para reintentar URLs fallidas."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envía un mensaje cuando se emite el comando /help."""
    await update.message.reply_text(
        "Comandos disponibles:\n"
        "- resultados: Ejecuta el script para extraer todas las tablas\n"
        "- resultados retry: Reintenta extraer las URLs que fallaron previamente"
    )

async def run_script(update: Update, context: ContextTypes.DEFAULT_TYPE, retry=False):
    """Ejecuta el script main.py y envía los resultados."""

    # Informar al usuario que el script está en ejecución
    await update.message.reply_text("⏳ Ejecutando script... esto puede tardar varios minutos.")
    
    try:
        # Obtener la lista de archivos CSV antes de ejecutar el script
        existing_csv_files = set(glob.glob("output/*.csv"))
        
        # Construir el comando para ejecutar el script
        cmd = ["python", "main.py"]
        if retry:
            cmd.append("--retry")
        
        # Ejecutar el script
        process = subprocess.run(cmd, capture_output=True, text=True)
        
        # Verificar si la ejecución fue exitosa
        if process.returncode == 0:
            await update.message.reply_text("✅ Script ejecutado con éxito. Enviando resultados...")
            
            # Enviar mensaje con el resumen (últimas 10 líneas de la salida)
            output_lines = process.stdout.strip().split('\n')
            summary = '\n'.join(output_lines[-10:]) if len(output_lines) > 10 else process.stdout
            await update.message.reply_text(f"📊 Resumen de ejecución:\n\n{summary}")
            
            # Obtener la lista de archivos CSV después de ejecutar el script
            new_csv_files = set(glob.glob("output/*.csv"))
            
            # Determinar qué archivos CSV son nuevos (solo los generados en esta ejecución)
            csv_files_to_send = list(new_csv_files - existing_csv_files)
            
            if csv_files_to_send:
                await update.message.reply_text(f"📄 Enviando {len(csv_files_to_send)} archivos generados en esta ejecución.")
                for csv_file in csv_files_to_send:
                    await update.message.reply_document(document=open(csv_file, "rb"))
            else:
                await update.message.reply_text("⚠️ No se generaron nuevos archivos CSV en esta ejecución.")
            
            # Enviar archivo failed_urls.json si existe
            failed_urls_file = "output/failed_urls.json"
            if os.path.exists(failed_urls_file):
                await update.message.reply_document(document=open(failed_urls_file, "rb"))
                await update.message.reply_text("ℹ️ Se adjunta el archivo con URLs fallidas.")
        else:
            # Si hubo un error, enviar el mensaje de error
            await update.message.reply_text(f"❌ Error al ejecutar el script:\n\n{process.stderr}")
    
    except Exception as e:
        await update.message.reply_text(f"❌ Ocurrió un error: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa los mensajes recibidos."""
    text = update.message.text.lower()
    
    if text == "resultados":
        await run_script(update, context, retry=False)
    elif text == "resultados retry":
        await run_script(update, context, retry=True)
    else:
        await update.message.reply_text(
            "Comando no reconocido. Usa 'resultados' o 'resultados retry'."
        )

def main():
    """Inicia el bot."""
    if not TOKEN:
        logger.error("No se ha configurado TELEGRAM_BOT_TOKEN en las variables de entorno o en el archivo .env")
        return
    
    # Crear la aplicación
    application = Application.builder().token(TOKEN).build()

    # Registrar manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Iniciar el bot
    logger.info("Bot iniciado")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main() 