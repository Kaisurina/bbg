import logging
from ..config.settings import guild_settings
from .localization import Localization

async def log_message(guild, text):
    """Отправляет сообщение в лог-канал сервера"""
    try:
        if not guild or guild.id not in guild_settings:
            return
        
        channel_id = guild_settings[guild.id].get("log_channel")
        if not channel_id:
            return
            
        channel = guild.get_channel(channel_id)
        if channel:
            await channel.send(text[:2000])
    except Exception as e:
        logging.error(f"Ошибка логирования: {e}")

async def log_dm_message(message):
    """Логирование входящих ЛС для отладки"""
    logging.info(f"Получено ЛС от {message.author}: {message.content[:50]}...")
    if message.attachments:
        logging.info(f"Вложения: {[a.filename for a in message.attachments]}") 