#!/bin/bash

# Проверка на root права
if [ "$EUID" -ne 0 ]; then 
    echo "Пожалуйста, запустите скрипт с правами root (sudo)"
    exit 1
fi

# Создание директории для бота, если её нет
BOT_DIR="/opt/discordBot/anon-bot"
mkdir -p $BOT_DIR

# Создание символической ссылки на файл службы
echo "Установка systemd службы..."
if [ -f "/etc/systemd/system/discord-bot.service" ]; then
    echo "Удаление существующего файла службы..."
    rm /etc/systemd/system/discord-bot.service
fi
ln -s $BOT_DIR/discord-bot.service /etc/systemd/system/discord-bot.service

# Перезагрузка systemd
echo "Перезагрузка systemd..."
systemctl daemon-reload

# Включение автозапуска
echo "Включение автозапуска службы..."
systemctl enable discord-bot

# Запуск службы
echo "Запуск службы..."
systemctl start discord-bot

# Проверка статуса
echo "Проверка статуса службы..."
systemctl status discord-bot

echo "Установка завершена!"
echo "Для просмотра логов используйте: journalctl -u discord-bot -f" 