# Hockey Standings Scraper Bot

Este proyecto permite extraer tablas de posiciones de hockey desde la página web de la AHBA y guardarlas en archivos CSV y en MongoDB. Incluye un bot de Telegram para ejecutar remotamente el script y recibir los resultados.

## Requisitos

- Python 3.8 o superior
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clona este repositorio
2. Crea un entorno virtual:
   ```
   python -m venv .venv
   ```
3. Activa el entorno virtual:
   - En Windows: `.venv\Scripts\activate`
   - En macOS/Linux: `source .venv/bin/activate`
4. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

## Configuración del Bot de Telegram

1. Crea un nuevo bot en Telegram hablando con [@BotFather](https://t.me/BotFather)
2. Ejecuta el comando `/newbot` y sigue las instrucciones
3. BotFather te proporcionará un token. Cópialo y agrégualo al archivo `.env`:
   ```
   TELEGRAM_BOT_TOKEN=tu_token_aqui
   ```
4. (Opcional) Para restringir el uso del bot a ciertos usuarios, obtén tu ID de Telegram usando [@userinfobot](https://t.me/userinfobot) y agrégalo al archivo `.env`:
   ```
   AUTHORIZED_USERS=123456789
   ```
   Puedes agregar varios IDs separados por comas.

## Uso

### Ejecución manual

Para ejecutar el script manualmente:

```
python main.py
```

Para reintentar URLs fallidas:

```
python main.py --retry
```

### Bot de Telegram

1. Inicia el bot:

   ```
   python telegram_bot.py
   ```

2. Abre Telegram y busca tu bot por su nombre de usuario
3. Inicia una conversación y usa los siguientes comandos:
   - `/start` - Iniciar el bot
   - `/help` - Mostrar ayuda
   - `resultados` - Ejecutar el script para extraer todas las tablas
   - `resultados retry` - Reintentar URLs fallidas

El bot ejecutará el script y te enviará los archivos CSV generados y el archivo `failed_urls.json` si existen URLs fallidas.

## Ejecución automática (opcional)

Para mantener el bot en ejecución de manera continua, puedes usar herramientas como `systemd` (Linux), `pm2` o `supervisor`.

Ejemplo con `systemd`:

1. Crea un archivo de servicio:

   ```
   sudo nano /etc/systemd/system/hockey-bot.service
   ```

2. Añade el siguiente contenido (ajusta las rutas según tu configuración):

   ```
   [Unit]
   Description=Hockey Standings Telegram Bot
   After=network.target

   [Service]
   User=tu_usuario
   WorkingDirectory=/ruta/al/proyecto
   ExecStart=/ruta/al/proyecto/.venv/bin/python /ruta/al/proyecto/telegram_bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. Habilita e inicia el servicio:
   ```
   sudo systemctl enable hockey-bot
   sudo systemctl start hockey-bot
   ```
