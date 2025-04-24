import discord
import logging
from ..config.settings import (
    ADMIN_ROLE_NAME, CATEGORY_NAME, LOG_CHANNEL_NAME,
    guild_settings
)
from ..utils.localization import Localization
from ..utils.logging import log_message
from .utils import forward_message, create_anon_chat

async def initialize_guild(guild, bot):
    """Инициализация сервера с автоматической настройкой"""
    try:
        # Проверка прав бота
        bot_member = guild.me
        required_perms = discord.Permissions(
            manage_channels=True,
            manage_roles=True,
            read_messages=True,
            send_messages=True
        )
        
        if not bot_member.guild_permissions >= required_perms:
            logging.warning(f"Недостаточно прав на сервере {guild.name}")
            return

        # Создание/проверка роли администратора
        admin_role = discord.utils.get(guild.roles, name=ADMIN_ROLE_NAME)
        if not admin_role:
            try:
                admin_role = await guild.create_role(
                    name=ADMIN_ROLE_NAME,
                    permissions=discord.Permissions.none(),
                    reason="Создание роли для анонимных чатов"
                )
                logging.info(f"Создана роль администратора на сервере {guild.name}")
            except Exception as e:
                logging.error(f"Ошибка создания роли на сервере {guild.name}: {e}")
                return

        # Назначение роли администраторам сервера
        admins = [member for member in guild.members 
                 if member.guild_permissions.administrator and admin_role not in member.roles]
        
        for admin in admins:
            try:
                await admin.add_roles(admin_role, reason="Назначение роли администратора анонимных чатов")
            except Exception as e:
                logging.error(f"Ошибка назначения роли администратору {admin} на сервере {guild.name}: {e}")

        # Удаление старой категории, если она существует
        old_category = discord.utils.get(guild.categories, name=CATEGORY_NAME)
        if old_category:
            try:
                for channel in old_category.channels:
                    try:
                        await channel.delete()
                        logging.info(f"Удален канал {channel.name} в категории {old_category.name}")
                    except Exception as e:
                        logging.error(f"Ошибка удаления канала {channel.name}: {e}")
                
                await old_category.delete()
                logging.info(f"Удалена старая категория {old_category.name}")
            except Exception as e:
                logging.error(f"Ошибка удаления категории: {e}")

        # Создание новой категории
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            admin_role: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_messages=True
            ),
            bot_member: discord.PermissionOverwrite(
                read_messages=True,
                send_messages=True,
                manage_channels=True
            )
        }
        
        try:
            category = await guild.create_category(
                name=CATEGORY_NAME,
                overwrites=overwrites,
                reason="Создание категории для анонимных чатов"
            )
            logging.info(f"Создана новая категория {category.name} на сервере {guild.name}")
        except Exception as e:
            logging.error(f"Ошибка создания категории на сервере {guild.name}: {e}")
            return

        # Создание лог-канала
        try:
            log_channel = await category.create_text_channel(
                name=LOG_CHANNEL_NAME,
                overwrites=category.overwrites,
                reason="Создание лог-канала для анонимных чатов"
            )
            logging.info(f"Создан лог-канал {log_channel.name} на сервере {guild.name}")
        except Exception as e:
            logging.error(f"Ошибка создания лог-канала на сервере {guild.name}: {e}")
            return

        # Сохранение настроек
        guild_settings[guild.id] = {
            "category_id": category.id,
            "log_channel": log_channel.id
        }

        # Отправка сообщения в лог-канал
        await log_message(guild, Localization.get("logs.bot_initialized", guild=guild.name))
        
    except Exception as e:
        logging.error(f"Ошибка инициализации сервера {guild.name}: {e}") 