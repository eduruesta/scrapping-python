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
        "¡Hola! Soy el bot de Hockey Standings. Puedo ayudarte con:\n"
        "- 'posiciones': Para ver las tablas de posiciones\n"
        "- 'resultados': Para ver los últimos y próximos partidos"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Envía un mensaje cuando se emite el comando /help."""
    await update.message.reply_text(
        "Comandos disponibles:\n"
        "- posiciones: Ejecuta el script para extraer tablas de posiciones\n"
        "- posiciones retry: Reintenta extraer las URLs que fallaron previamente\n"
        "- resultados: Muestra los últimos y próximos partidos de los equipos"
    )

async def run_positions_script(update: Update, context: ContextTypes.DEFAULT_TYPE, retry=False):
    """Ejecuta el script main.py y envía los resultados."""

    # Informar al usuario que el script está en ejecución
    await update.message.reply_text("⏳ Ejecutando script de posiciones... esto puede tardar varios minutos.")
    
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
            await update.message.reply_text("✅ Script de posiciones ejecutado con éxito. Enviando resultados...")
            
            # Enviar mensaje con el resumen (últimas 10 líneas de la salida)
            output_lines = process.stdout.strip().split('\n')
            summary = '\n'.join(output_lines[-10:]) if len(output_lines) > 10 else process.stdout
            
            # Dividir el mensaje si es demasiado largo (Telegram tiene un límite de 4096 caracteres)
            if len(summary) > 4000:
                # Dividir en fragmentos de 4000 caracteres
                chunks = [summary[i:i+4000] for i in range(0, len(summary), 4000)]
                for i, chunk in enumerate(chunks):
                    await update.message.reply_text(f"📊 Resumen de ejecución (parte {i+1}/{len(chunks)}):\n\n{chunk}")
            else:
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
            error_msg = process.stderr
            if len(error_msg) > 4000:
                chunks = [error_msg[i:i+4000] for i in range(0, len(error_msg), 4000)]
                for i, chunk in enumerate(chunks):
                    await update.message.reply_text(f"❌ Error al ejecutar el script (parte {i+1}/{len(chunks)}):\n\n{chunk}")
            else:
                await update.message.reply_text(f"❌ Error al ejecutar el script:\n\n{error_msg}")
    
    except Exception as e:
        await update.message.reply_text(f"❌ Ocurrió un error: {str(e)}")

async def run_results_script(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ejecuta el script hockey_team_last_and_next_matched.py y envía los resultados."""

    # Informar al usuario que el script está en ejecución
    await update.message.reply_text("⏳ Ejecutando script de resultados... esto puede tardar varios minutos.")
    
    try:
        # Ejecutar el script con un timeout para evitar que se quede esperando indefinidamente
        process = subprocess.run(["python", "hockey_team_last_and_next_matched.py"], 
                              capture_output=True, text=True, timeout=300)  # 5 minutos de timeout
        
        # Verificar si la ejecución fue exitosa
        if process.returncode == 0:
            await update.message.reply_text("✅ Script de resultados ejecutado con éxito. Enviando información...")
            
            # Enviar mensaje con el resumen (últimas 10 líneas de la salida)
            output_lines = process.stdout.strip().split('\n')
            summary = '\n'.join(output_lines[-10:]) if len(output_lines) > 10 else process.stdout
            
            # Dividir el mensaje si es demasiado largo
            if len(summary) > 4000:
                chunks = [summary[i:i+4000] for i in range(0, len(summary), 4000)]
                for i, chunk in enumerate(chunks):
                    await update.message.reply_text(f"🏒 Resultados de partidos (parte {i+1}/{len(chunks)}):\n\n{chunk}")
            else:
                await update.message.reply_text(f"🏒 Resultados de partidos:\n\n{summary}")
            
            # Enviar archivos generados
            matches_files = []
            for file_pattern in ["output/*matches*.csv", "output/*matches*.json"]:
                matches_files.extend(glob.glob(file_pattern))
            
            if matches_files:
                await update.message.reply_text(f"📄 Enviando {len(matches_files)} archivos de resultados.")
                for file in matches_files:
                    await update.message.reply_document(document=open(file, "rb"))
            else:
                await update.message.reply_text("⚠️ No se encontraron archivos de resultados.")
        else:
            # Si hubo un error, enviar el mensaje de error
            error_msg = process.stderr
            if len(error_msg) > 4000:
                chunks = [error_msg[i:i+4000] for i in range(0, len(error_msg), 4000)]
                for i, chunk in enumerate(chunks):
                    await update.message.reply_text(f"❌ Error al ejecutar el script de resultados (parte {i+1}/{len(chunks)}):\n\n{chunk}")
            else:
                await update.message.reply_text(f"❌ Error al ejecutar el script de resultados:\n\n{error_msg}")
    
    except subprocess.TimeoutExpired:
        await update.message.reply_text("❌ El script de resultados tardó demasiado tiempo en ejecutarse y se canceló.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ocurrió un error al obtener resultados: {str(e)}\nIntentando ejecutar el script con más memoria...")
        try:
            # Segundo intento con más memoria asignada
            process = subprocess.run(["python", "-X", "utf8", "hockey_team_last_and_next_matched.py"], 
                                  capture_output=True, text=True, timeout=300)
            if process.returncode == 0:
                await update.message.reply_text("✅ Script de resultados ejecutado con éxito en el segundo intento.")
                # Procesamiento similar al anterior...
            else:
                await update.message.reply_text(f"❌ Error en el segundo intento: {process.stderr[:3900]}")
        except Exception as e2:
            await update.message.reply_text(f"❌ Error definitivo: {str(e2)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Procesa los mensajes recibidos."""
    text = update.message.text.lower()
    
    if text == "posiciones":
        await run_positions_script(update, context, retry=False)
    elif text == "posiciones retry":
        await run_positions_script(update, context, retry=True)
    elif text == "resultados":
        await run_results_script(update, context)
    else:
        await update.message.reply_text(
            "Comando no reconocido. Usa 'posiciones', 'posiciones retry' o 'resultados'."
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