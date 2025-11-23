#!/bin/bash

# Скрипт создания desktop файла для Dependency Manager
# Использование: ./icon.sh

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DESKTOP_FILE="$HOME/.local/share/applications/dependency_manager.desktop"
ICON_FILE="$SCRIPT_DIR/dependency_manager_icon.svg"

echo "🔧 Создание desktop файла для Dependency Manager..."

# Создаем директорию если её нет
mkdir -p "$HOME/.local/share/applications"

# Создаем .desktop файл
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Dependency Manager
Comment=Система управления зависимостями инфраструктуры
Exec=$SCRIPT_DIR/run_dependency_manager.sh
Icon=$ICON_FILE
Terminal=false
Categories=Development;Utility;
Path=$SCRIPT_DIR
StartupNotify=true
EOF

echo "✅ Desktop файл создан: $DESKTOP_FILE"

# Делаем .desktop файл исполняемым
chmod +x "$DESKTOP_FILE"
echo "✅ Установлены права на выполнение"

# Проверяем существование run скрипта
if [ ! -f "$SCRIPT_DIR/run_dependency_manager.sh" ]; then
    echo "⚠️  ВНИМАНИЕ: Не найден run_dependency_manager.sh"
    echo "   Создайте его или путь в Exec будет неверным"
else
    echo "✅ Скрипт запуска найден"
fi

# Обновляем базу данных desktop файлов
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null
    echo "✅ База данных desktop файлов обновлена"
fi

echo ""
echo "🎉 Готово! Приложение должно появиться в меню приложений"
echo "   Название: Dependency Manager"
echo "   Категория: Development → Utility"
echo ""
echo "💡 Если не появилось сразу:"
echo "   1. Выйдите и войдите в систему"
echo "   2. Возможны ошибки в наименованиях/путях"
echo "   3. Или перезагрузите систему"
