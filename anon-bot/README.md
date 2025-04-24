# Discord Анонимный Чат Бот

Бот для создания анонимных чатов в Discord серверах. Позволяет пользователям общаться с администраторами сервера анонимно.

## Возможности

- Создание анонимных чатов для пользователей
- Автоматическая настройка сервера при добавлении бота
- Система ролей для администраторов
- Логирование всех действий
- Поддержка вложений
- Команда закрытия чата
- Автоматический деплой через GitHub Actions

## Установка

### Локальная установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/discord-bots.git
cd discord-bots/anon-bot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` в корневой директории и добавьте токен бота:
```
DISCORD_BOT_TOKEN=your_bot_token_here
```

4. Настройте конфигурацию в `data/settings.json`:
```json
{
    "COMMAND_PREFIX": "!",
    "ADMIN_ROLE_NAME": "AnonChat Admin",
    "CATEGORY_NAME": "Анонимные чаты",
    "LOG_CHANNEL_NAME": "логи-чатов",
    "MAX_FILE_SIZE": 8388608
}
```

### Установка на сервер

#### Настройка SSH для деплоя

1. На вашем локальном компьютере сгенерируйте SSH ключ для деплоя:
```bash
ssh-keygen -t ed25519 -C "github-actions-deploy"
```
При запросе пути для сохранения ключа, нажмите Enter для использования пути по умолчанию.
При запросе пароля, можете оставить его пустым, нажав Enter дважды.

2. Скопируйте публичный ключ:
```bash
cat ~/.ssh/id_ed25519.pub
```
Вывод будет выглядеть примерно так:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAI... github-actions-deploy
```

3. На сервере запустите скрипт настройки SSH:
```bash
sudo ./setup_ssh.sh
```

4. Когда скрипт запросит имя пользователя, введите желаемое имя (например, `deploy`).
5. Когда скрипт запросит публичный ключ, вставьте скопированный публичный ключ и нажмите Enter дважды.

6. Добавьте следующие секреты в настройках GitHub репозитория (Settings -> Secrets and variables -> Actions):
   - `SSH_PRIVATE_KEY`: содержимое приватного ключа (выполните `cat ~/.ssh/id_ed25519` на локальном компьютере)
   - `HOST`: IP-адрес или домен сервера
   - `USER`: имя пользователя, которое вы ввели в шаге 4
   - `DEPLOY_PATH`: путь для деплоя (например, /opt/deploy)
   - `DISCORD_BOT_TOKEN`: токен вашего Discord бота

#### Автоматическая установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/discord-bots.git
cd discord-bots/anon-bot
```

2. Запустите скрипт установки:
```bash
sudo ./setup.sh
```

Скрипт автоматически:
- Создаст необходимые директории
- Установит systemd службу
- Включит автозапуск
- Запустит бота
- Покажет статус установки

#### Ручная установка

Если вы предпочитаете установить вручную:

1. Установите systemd службу:
```bash
# Копируем файл службы
sudo cp discord-bot.service /etc/systemd/system/

# Перезагружаем systemd
sudo systemctl daemon-reload

# Включаем автозапуск
sudo systemctl enable discord-bot

# Запускаем службу
sudo systemctl start discord-bot
```

2. Проверьте статус службы:
```bash
sudo systemctl status discord-bot
```

## Запуск

### Локальный запуск
```bash
python main.py
```

### Управление службой
```bash
# Запуск
sudo systemctl start discord-bot

# Остановка
sudo systemctl stop discord-bot

# Перезапуск
sudo systemctl restart discord-bot

# Просмотр логов
sudo journalctl -u discord-bot -f
```

## Структура проекта

```
anon-bot/
├── src/                    # Исходный код
│   ├── bot.py             # Основной класс бота
│   ├── handlers/          # Обработчики событий
│   ├── utils/             # Вспомогательные функции
│   └── config/            # Конфигурация
├── data/                  # Данные и локализация
│   ├── settings.json     # Настройки
│   └── ru.json           # Локализация
├── tests/                 # Тесты
│   ├── __init__.py       # Инициализация пакета тестов
│   └── test_basic.py     # Базовые тесты
├── requirements.txt       # Зависимости
├── discord-bot.service   # Systemd служба
├── setup.sh              # Скрипт установки
├── setup_ssh.sh          # Скрипт настройки SSH
└── README.md             # Документация
```

## Использование

1. Добавьте бота на сервер с правами администратора
2. Бот автоматически создаст необходимые каналы и роли
3. Пользователи могут начать анонимный чат, написав боту в личные сообщения
4. Администраторы могут отвечать в созданных каналах
5. Для закрытия чата используйте команду `!anonclose`

## Требования

- Python 3.8+
- discord.py
- python-dotenv
- systemd (для серверной установки)

## Лицензия

MIT 