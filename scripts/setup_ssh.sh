#!/bin/bash

# Проверка на root права
if [ "$EUID" -ne 0 ]; then 
    echo "Пожалуйста, запустите скрипт с правами root (sudo)"
    exit 1
fi

# Запрос имени пользователя
read -p "Введите имя пользователя для деплоя: " DEPLOY_USER

# Создание пользователя, если его нет
if ! id "$DEPLOY_USER" &>/dev/null; then
    echo "Создание пользователя $DEPLOY_USER..."
    useradd -m -s /bin/bash $DEPLOY_USER
    echo "Пользователь $DEPLOY_USER создан"
else
    echo "Пользователь $DEPLOY_USER уже существует"
fi

# Создание директории .ssh
mkdir -p /home/$DEPLOY_USER/.ssh
chmod 700 /home/$DEPLOY_USER/.ssh

# Инструкции для пользователя
echo "=================================================="
echo "ВАЖНО: Сейчас вам нужно будет ввести ПУБЛИЧНЫЙ ключ"
echo "Публичный ключ обычно начинается с 'ssh-ed25519' или 'ssh-rsa'"
echo "и заканчивается комментарием (например, 'github-actions-deploy')"
echo "=================================================="
echo ""

# Запрос публичного ключа
echo "Введите публичный ключ (завершите ввод пустой строкой):"
PUBLIC_KEY=""
while IFS= read -r line; do
    if [ -z "$line" ]; then
        break
    fi
    PUBLIC_KEY="$PUBLIC_KEY$line\n"
done

# Проверка формата ключа
if ! echo -e "$PUBLIC_KEY" | grep -q "^ssh-"; then
    echo "ОШИБКА: Введенный ключ не похож на публичный SSH ключ!"
    echo "Публичный ключ должен начинаться с 'ssh-ed25519' или 'ssh-rsa'"
    exit 1
fi

# Добавление ключа в authorized_keys
echo -e "$PUBLIC_KEY" > /home/$DEPLOY_USER/.ssh/authorized_keys
chmod 600 /home/$DEPLOY_USER/.ssh/authorized_keys
chown -R $DEPLOY_USER:$DEPLOY_USER /home/$DEPLOY_USER/.ssh

# Настройка прав доступа к директории деплоя
BOT_DIR="/opt/deploy"
mkdir -p $BOT_DIR
chown -R $DEPLOY_USER:$DEPLOY_USER $BOT_DIR
chmod 755 $BOT_DIR

# Настройка sudo для пользователя
echo "Настройка sudo для пользователя $DEPLOY_USER..."
echo "$DEPLOY_USER ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart" > /etc/sudoers.d/discord-bot
chmod 440 /etc/sudoers.d/discord-bot

echo "=================================================="
echo "SSH настройка успешно завершена!"
echo "Пользователь: $DEPLOY_USER"
echo "Отпечаток ключа:"
echo -e "$PUBLIC_KEY" | ssh-keygen -lf -
echo "=================================================="
echo "Теперь добавьте следующие секреты в GitHub:"
echo "SSH_PRIVATE_KEY: (приватный ключ)"
echo "HOST: (IP или домен сервера)"
echo "USER: $DEPLOY_USER"
echo "DEPLOY_PATH: $BOT_DIR" 