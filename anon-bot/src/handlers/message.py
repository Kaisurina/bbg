import discord
import logging
from ..config.settings import (
    active_chats, guild_settings, MAX_FILE_SIZE,
    ADMIN_ROLE_NAME
)
from ..utils.localization import Localization
from ..utils.logging import log_message, log_dm_message
from .guild import initialize_guild
from .utils import forward_message, create_anon_chat

async def handle_dm_message(message, bot):
    """Улучшенный обработчик ЛС"""
    try:
        user_id = message.author.id
        mutual_guilds = []
        
        # Ищем общие серверы
        for guild in bot.guilds:
            try:
                member = await guild.fetch_member(user_id)
                if member:
                    mutual_guilds.append(guild)
            except discord.NotFound:
                continue
            except Exception as e:
                logging.error(f"Ошибка при поиске пользователя {user_id} на сервере {guild.name}: {e}")
                continue

        if not mutual_guilds:
            await message.author.send(Localization.get("errors.no_mutual_guilds"))
            return
            
        # Проверяем права администратора
        admin_role = ADMIN_ROLE_NAME
        is_admin = False
        for guild in mutual_guilds:
            try:
                member = await guild.fetch_member(user_id)
                if member and any(role.name == admin_role for role in member.roles):
                    is_admin = True
                    break
            except Exception as e:
                logging.error(f"Ошибка при проверке прав администратора для {user_id} на сервере {guild.name}: {e}")
                continue
        
        if is_admin:
            await message.author.send(Localization.get("errors.admin_in_dm"))
            return

        guild = mutual_guilds[0]  # Берем первый подходящий сервер
        
        # Автоматическая инициализация сервера, если он не настроен
        if guild.id not in guild_settings:
            logging.info(f"Автоматическая инициализация сервера {guild.name}")
            try:
                await initialize_guild(guild, bot)
                logging.info(f"Сервер {guild.name} успешно инициализирован")
            except Exception as e:
                logging.error(f"Ошибка автоматической инициализации сервера {guild.name}: {e}")
                await message.author.send(Localization.get("errors.guild_not_setup"))
                return
        
        # Проверяем активный чат
        if user_id in active_chats:
            channel = guild.get_channel(active_chats[user_id]["channel_id"])
            if channel:
                try:
                    await forward_message(message, channel)
                    return
                except Exception as e:
                    logging.error(f"Ошибка пересылки сообщения от {user_id}: {e}")
                    await message.author.send(Localization.get("errors.message_forward_failed"))
                    return
        
        # Создаем новый чат
        await create_anon_chat(user_id, guild, message, bot)
        
    except Exception as e:
        logging.error(f"Ошибка обработки ЛС от пользователя {message.author.id}: {str(e)}")
        try:
            await message.author.send(Localization.get("errors.dm_processing_error"))
        except:
            logging.error("Не удалось отправить сообщение об ошибке пользователю")

async def handle_anon_chat_message(message, bot):
    """Обработка сообщений в анонимных чатах"""
    user_id = next((uid for uid, chat in active_chats.items() 
                  if chat["channel_id"] == message.channel.id), None)
    if not user_id:
        return
    
    try:
        user = await bot.fetch_user(user_id)
        await forward_message(message, user, message.content, is_admin_reply=True)
        await log_message(message.guild, Localization.get("logs.admin_replied", 
                         admin=message.author.id, channel=message.channel.name))
    except discord.Forbidden:
        await message.channel.send(Localization.get("errors.user_message_failed"))
    except Exception as e:
        logging.error(f"Ошибка отправки сообщения: {e}") 