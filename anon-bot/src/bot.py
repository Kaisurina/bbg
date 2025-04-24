import discord
from discord.ext import commands
import sys
import traceback
import logging
from .config.settings import (
    BOT_TOKEN, COMMAND_PREFIX, ADMIN_ROLE_NAME,
    guild_settings, active_chats
)
from .handlers.message import handle_dm_message, handle_anon_chat_message
from .handlers.guild import initialize_guild
from .utils.logging import log_dm_message, log_message
from .utils.localization import Localization

class AnonChatBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.messages = True
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(command_prefix=COMMAND_PREFIX, intents=intents)
        logging.info(f"Бот инициализирован с префиксом команд: {COMMAND_PREFIX}")
        
    async def setup_hook(self):
        """Инициализация при запуске бота"""
        logging.info(f'Бот {self.user} готов к работе на {len(self.guilds)} серверах!')
        for guild in self.guilds:
            try:
                await initialize_guild(guild, self)
                logging.info(f"Сервер {guild.name} успешно инициализирован")
            except Exception as e:
                logging.error(f"Ошибка инициализации сервера {guild.name}: {e}")
            
    async def on_guild_join(self, guild):
        """Обработка добавления на новый сервер"""
        logging.info(f'Бот добавлен на новый сервер: {guild.name} (ID: {guild.id})')
        try:
            await initialize_guild(guild, self)
            logging.info(f"Сервер {guild.name} успешно инициализирован")
        except Exception as e:
            logging.error(f"Ошибка инициализации сервера {guild.name}: {e}")
        
    async def on_message(self, message):
        """Обработка всех сообщений"""
        try:
            if message.author.bot:
                return
            
            if isinstance(message.channel, discord.DMChannel):
                logging.debug(f'Получено личное сообщение от {message.author}: {message.content[:50]}...')
                await log_dm_message(message)
                await handle_dm_message(message, self)
            elif message.channel.id in [chat["channel_id"] for chat in active_chats.values()]:
                logging.debug(f'Получено сообщение в анонимном чате {message.channel.name}')
                await handle_anon_chat_message(message, self)
            
            await self.process_commands(message)
        except Exception as e:
            logging.error(f"Ошибка обработки сообщения: {e}")
            logging.error(traceback.format_exc())
            if isinstance(message.channel, discord.DMChannel):
                await message.author.send(Localization.get("errors.dm_processing_error"))

    @commands.command(name='anonclose')
    @commands.has_role(ADMIN_ROLE_NAME)
    async def close_anon_chat(self, ctx):
        """Закрытие чата"""
        user_id = next((uid for uid, chat in active_chats.items() 
                      if chat["channel_id"] == ctx.channel.id), None)
        if not user_id:
            await ctx.send(Localization.get("errors.not_anon_chat"))
            return
        
        try:
            user = await self.fetch_user(user_id)
            await user.send(Localization.get("messages.chat_closed"))
        except:
            pass
        
        try:
            await ctx.channel.delete()
        except:
            pass
        
        if user_id in active_chats:
            del active_chats[user_id]
        
        await log_message(ctx.guild, Localization.get("logs.chat_closed", 
                         channel=ctx.channel.name))

    @commands.command(name='anoninit')
    @commands.has_permissions(administrator=True)
    async def init_guild(self, ctx):
        """Инициализация сервера для анонимных чатов"""
        try:
            await ctx.send(Localization.get("messages.init_started"))
            await initialize_guild(ctx.guild, self)
            await ctx.send(Localization.get("messages.init_completed"))
        except Exception as e:
            logging.error(f"Ошибка инициализации сервера {ctx.guild.name}: {e}")
            await ctx.send(Localization.get("errors.init_failed"))

def run_bot():
    """Запуск бота"""
    try:
        logging.info("Запуск бота...")
        bot = AnonChatBot()
        bot.run(BOT_TOKEN)
    except discord.LoginFailure:
        logging.error("ОШИБКА: Не удалось войти в Discord. Проверьте токен бота.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
        logging.error(traceback.format_exc())
        sys.exit(1) 