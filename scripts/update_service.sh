#!/bin/bash

# Проверяем обязательные параметры
if [ -z "$DEPLOY_PATH" ] || [ -z "$SERVICE_NAME" ] || [ -z "$PROJECT_DIR" ]; then
    echo "ОШИБКА: Необходимо указать следующие переменные окружения:"
    echo "DEPLOY_PATH - путь к директории деплоя"
    echo "SERVICE_NAME - имя systemd сервиса"
    echo "PROJECT_DIR - имя директории проекта"
    exit 1
fi

# Формируем полный путь к проекту
PROJECT_PATH="$DEPLOY_PATH/$PROJECT_DIR"

# Проверяем наличие .env файла
if [ ! -f "$PROJECT_PATH/.env" ]; then
    echo "ОШИБКА: Файл .env не найден в $PROJECT_PATH!"
    exit 1
fi

# Проверяем наличие systemd сервиса
if [ ! -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
    echo "ОШИБКА: Systemd сервис $SERVICE_NAME.service не найден!"
    exit 1
fi

# Обновляем пути в systemd сервисе
echo "Обновление конфигурации сервиса $SERVICE_NAME..."
sudo sed -i "s|WorkingDirectory=.*|WorkingDirectory=$PROJECT_PATH|" "/etc/systemd/system/$SERVICE_NAME.service"
sudo sed -i "s|EnvironmentFile=.*|EnvironmentFile=$PROJECT_PATH/.env|" "/etc/systemd/system/$SERVICE_NAME.service"

# Перезагружаем systemd
echo "Перезагрузка systemd..."
sudo systemctl daemon-reload

echo "Конфигурация systemd сервиса $SERVICE_NAME успешно обновлена"
echo "Путь к проекту: $PROJECT_PATH"
echo "Файл окружения: $PROJECT_PATH/.env" 