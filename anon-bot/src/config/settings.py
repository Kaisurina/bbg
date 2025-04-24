import json
import os
from dotenv import load_dotenv
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

# Определяем пути к файлам
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
SETTINGS_FILE = DATA_DIR / 'settings.json'
LOCALIZATION_FILE = DATA_DIR / 'ru.json'
ENV_FILE = BASE_DIR / '.env'

# Загрузка переменных окружения
load_dotenv(ENV_FILE)

# Проверка наличия файлов
if not SETTINGS_FILE.exists():
    logging.error(f"ОШИБКА: Файл настроек не найден: {SETTINGS_FILE}")
    raise FileNotFoundError(f"Файл настроек не найден: {SETTINGS_FILE}")

if not LOCALIZATION_FILE.exists():
    logging.error(f"ОШИБКА: Файл локализации не найден: {LOCALIZATION_FILE}")
    raise FileNotFoundError(f"Файл локализации не найден: {LOCALIZATION_FILE}")

# Загрузка конфигурации
with open(SETTINGS_FILE) as f:
    SETTINGS = json.load(f)

# Загрузка локализации
with open(LOCALIZATION_FILE, encoding='utf-8') as f:
    MESSAGES = json.load(f)

# Настройки бота
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not BOT_TOKEN:
    logging.error("Токен бота не найден в переменных окружения!")
    logging.error(f"Убедитесь, что файл {ENV_FILE} существует и содержит DISCORD_BOT_TOKEN=ваш_токен")
    raise ValueError("Токен бота не найден!")
else:
    # Логируем только первые 10 символов токена для безопасности
    logging.info(f"Токен бота загружен: {BOT_TOKEN[:10]}...")
    logging.info(f"Полная длина токена: {len(BOT_TOKEN)} символов")

# Экспорт настроек
COMMAND_PREFIX = SETTINGS["COMMAND_PREFIX"]
ADMIN_ROLE_NAME = SETTINGS["ADMIN_ROLE_NAME"]
CATEGORY_NAME = SETTINGS["CATEGORY_NAME"]
LOG_CHANNEL_NAME = SETTINGS["LOG_CHANNEL_NAME"]
MAX_FILE_SIZE = SETTINGS["MAX_FILE_SIZE"]

# Хранилище данных
active_chats = {}  # {user_id: {"channel_id": channel_id, "guild_id": guild_id}}
guild_settings = {}  # {guild_id: {"log_channel": channel_id, "category_id": category_id}} 