# Discord Bots Monorepo

Монорепозиторий для Discord ботов.

## Структура проекта

```
.
├── anon-bot/           # Бот для анонимных чатов
├── scripts/            # Общие скрипты
│   └── update_service.sh  # Универсальный скрипт обновления systemd сервисов
└── README.md          # Документация
```

## Первый запуск

### 1. Подготовка сервера

1. Создайте директорию для деплоя:
```bash
sudo mkdir -p /opt/deploy
sudo chown $USER:$USER /opt/deploy
```

2. Клонируйте репозиторий:
```bash
cd /opt/deploy
git clone https://github.com/yourusername/discord-bots.git .
```

3. Создайте файл .env для каждого бота:
```bash
# Для anon-bot
echo "DISCORD_BOT_TOKEN=your_bot_token_here" > /opt/deploy/anon-bot/.env
chmod 600 /opt/deploy/anon-bot/.env
```

### 2. Настройка SSH для деплоя

1. На вашем локальном компьютере сгенерируйте SSH ключ:
```bash
ssh-keygen -t ed25519 -C "github-actions-deploy"
```

2. Скопируйте публичный ключ:
```bash
cat ~/.ssh/id_ed25519.pub
```

3. На сервере создайте пользователя для деплоя:
```bash
sudo useradd -m -s /bin/bash deploy
sudo mkdir -p /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh
echo "публичный_ключ" | sudo tee /home/deploy/.ssh/authorized_keys
sudo chmod 600 /home/deploy/.ssh/authorized_keys
sudo chown -R deploy:deploy /home/deploy/.ssh
```

4. Настройте sudo для пользователя deploy:
```bash
echo "deploy ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart discord-bot" | sudo tee /etc/sudoers.d/discord-bot
sudo chmod 440 /etc/sudoers.d/discord-bot
```

### 3. Настройка GitHub Secrets

Добавьте следующие секреты в настройках GitHub репозитория (Settings -> Secrets and variables -> Actions):
- `SSH_PRIVATE_KEY`: содержимое приватного ключа (выполните `cat ~/.ssh/id_ed25519` на локальном компьютере)
- `HOST`: IP-адрес или домен сервера
- `USER`: deploy
- `DEPLOY_PATH`: /opt/deploy

## Универсальный скрипт обновления systemd сервисов

Скрипт `scripts/update_service.sh` используется для обновления конфигурации systemd сервисов при деплое. Он автоматически обновляет пути в конфигурации сервиса и проверяет наличие необходимых файлов.

### Использование

```bash
DEPLOY_PATH=/opt/deploy SERVICE_NAME=service-name PROJECT_DIR=project-dir bash scripts/update_service.sh
```

Параметры:
- `DEPLOY_PATH` - путь к корневой директории деплоя (по умолчанию /opt/deploy)
- `SERVICE_NAME` - имя systemd сервиса (без .service)
- `PROJECT_DIR` - имя директории проекта внутри DEPLOY_PATH

### Пример использования

```bash
# Для бота анонимных чатов
DEPLOY_PATH=/opt/deploy SERVICE_NAME=discord-bot PROJECT_DIR=anon-bot bash scripts/update_service.sh
```

### Требования

1. Файл `.env` должен существовать в директории проекта
2. Systemd сервис должен быть установлен в `/etc/systemd/system/`
3. Сервис должен иметь директивы `WorkingDirectory` и `EnvironmentFile`

## Деплой

Каждый бот в монорепозитории имеет свой собственный процесс деплоя, описанный в его README.md.

Общие требования для деплоя:
1. Настроенный SSH доступ (инструкции выше)
2. Установленный systemd
3. Созданный файл .env с необходимыми переменными окружения
4. Установленный systemd сервис для бота

## Лицензия

MIT
