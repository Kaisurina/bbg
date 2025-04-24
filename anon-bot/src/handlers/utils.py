import discord
import logging
from ..config.settings import (
    active_chats, guild_settings, MAX_FILE_SIZE,
    ADMIN_ROLE_NAME
)
from ..utils.localization import Localization
from ..utils.logging import log_message

async def forward_message(source, target, content=None, is_admin_reply=False):
    """Улучшенная пересылка сообщений с обработкой ошибок"""
    try:
        # Отправка текста
        if content or source.content:
            text = content if content else source.content
            embed = discord.Embed(
                description=text,
                color=discord.Color.green() if is_admin_reply else discord.Color.blurple()
            )
            embed.set_footer(text=Localization.get("messages.admin_reply" if is_admin_reply else "messages.anon_message"))
            await target.send(embed=embed)
        
        # Отправка вложений
        for attachment in source.attachments:
            try:
                if attachment.size > MAX_FILE_SIZE:
                    await target.send(Localization.get("errors.attachment_too_large", filename=attachment.filename))
                    continue
                
                file = await attachment.to_file()
                prefix = Localization.get("messages.attachment_admin" if is_admin_reply else "messages.attachment_anon")
                await target.send(prefix, file=file)
            except Exception as e:
                logging.error(f"Ошибка вложения: {e}")
                await target.send(Localization.get("errors.attachment_send_error", filename=attachment.filename))
                
    except discord.Forbidden:
        logging.error("Нет прав для отправки сообщения")
        raise
    except Exception as e:
        logging.error(f"Ошибка пересылки: {e}")
        raise

async def create_anon_chat(user_id, guild, initial_message, bot):
    """Создание нового анонимного чата"""
    try:
        logging.info(f"Начало создания анонимного чата для пользователя {user_id} на сервере {guild.name}")
        
        if guild.id not in guild_settings:
            logging.error(f"Сервер {guild.name} не настроен")
            await initial_message.author.send(Localization.get("errors.guild_not_setup"))
            return
            
        category_id = guild_settings[guild.id].get("category_id")
        if not category_id:
            logging.error(f"Категория не настроена для сервера {guild.name}")
            await initial_message.author.send(Localization.get("errors.category_not_setup"))
            return
        
        category = guild.get_channel(category_id)
        if not category:
            logging.error(f"Категория {category_id} не найдена на сервере {guild.name}")
            await initial_message.author.send(Localization.get("errors.category_not_found"))
            return
        
        chat_number = 1
        while discord.utils.get(category.channels, name=f"anon-chat-{chat_number}"):
            chat_number += 1
        
        admin_role = discord.utils.get(guild.roles, name=ADMIN_ROLE_NAME)
        if not admin_role:
            logging.error(f"Роль администратора {ADMIN_ROLE_NAME} не найдена на сервере {guild.name}")
            await initial_message.author.send(Localization.get("errors.admin_role_not_found"))
            return
        
        try:
            channel = await category.create_text_channel(
                name=f"anon-chat-{chat_number}",
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    admin_role: discord.PermissionOverwrite(read_messages=True),
                    guild.me: discord.PermissionOverwrite(read_messages=True)
                }
            )
            logging.info(f"Создан канал {channel.name} для пользователя {user_id}")
            
            active_chats[user_id] = {"channel_id": channel.id, "guild_id": guild.id}
            
            embed = discord.Embed(
                title=Localization.get("messages.chat_created_title", number=chat_number),
                description=Localization.get("messages.chat_created_desc"),
                color=discord.Color.blurple()
            )
            await channel.send(embed=embed)
            
            if initial_message:
                await forward_message(initial_message, channel)
            
            await log_message(guild, Localization.get("logs.chat_created", 
                             channel=channel.mention, user=user_id))
            
            await initial_message.author.send(Localization.get("messages.welcome_dm"))
            logging.info(f"Анонимный чат успешно создан для пользователя {user_id}")
        
        except discord.Forbidden as e:
            logging.error(f"Недостаточно прав для создания канала на сервере {guild.name}: {e}")
            await initial_message.author.send(Localization.get("errors.insufficient_permissions"))
        except Exception as e:
            logging.error(f"Ошибка при создании канала на сервере {guild.name}: {e}")
            await initial_message.author.send(Localization.get("errors.chat_creation_error"))
    
    except Exception as e:
        logging.error(f"Критическая ошибка при создании анонимного чата для пользователя {user_id}: {str(e)}")
        try:
            await initial_message.author.send(Localization.get("errors.chat_creation_error"))
        except:
            logging.error("Не удалось отправить сообщение об ошибке пользователю") 