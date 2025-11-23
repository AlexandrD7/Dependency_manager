#!/bin/bash
# Скрипт запуска Dependency Manager с виртуальным окружением

# Получаем директорию скрипта
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Переходим в директорию приложения
cd "$DIR" || exit 1

# Проверяем наличие виртуального окружения
if [ ! -d "$DIR/venv/bin" ]; then
    echo "Ошибка: виртуальное окружение не найдено в $DIR/program"
    read -p "Нажмите Enter для выхода..."
    exit 1
fi

# Активируем виртуальное окружение
source "$DIR/venv/bin/activate"

# Проверяем наличие файла
if [ ! -f "$DIR/dependency_manager.py" ]; then
    echo "Ошибка: dependency_manager.py не найден!"
    read -p "Нажмите Enter для выхода..."
    exit 1
fi

# Запускаем приложение
python3 "$DIR/dependency_manager.py" 2>&1

# Если произошла ошибка - ждём нажатия клавиши
if [ $? -ne 0 ]; then
    echo ""
    echo "Произошла ошибка при запуске!"
    read -p "Нажмите Enter для выхода..."
fi
