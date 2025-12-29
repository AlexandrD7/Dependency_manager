# Infrastructure Dependency Manager

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Система управления зависимостями инфраструктуры** — desktop-приложение для визуализации и управления зависимостями между компонентами IT-инфраструктуры, Docker-контейнерами и Godot-проектами.

[English version below](#english-version)

---

## 🌟 Основные возможности

### Управление объектами инфраструктуры
- **Поддержка множества типов объектов:**
  - 📄 Файлы (Files)
  - 🐳 Docker-контейнеры
  - 🌐 Роутеры (Routers)
  - ⚡ Коммутаторы (Switches)
  - 🖥️ Серверы (Servers)
  - 💾 Базы данных (Databases)
- **Поддержка объектов Godot Engine:**
  - 🎬 Сцены (Scenes)
  - 📜 Скрипты (Scripts)
  - 📦 Ресурсы (Resources)
  - ⚙️ Autoload-синглтоны

### Интерактивная визуализация
- **Графическое представление зависимостей** с использованием NetworkX и Matplotlib
- **Интерактивное управление графом:**
  - Перетаскивание узлов мышью для изменения расположения
  - Плавное масштабирование колесом мыши
  - Панорамирование с помощью средней кнопки мыши или Shift+ЛКМ
  - Выделение связей при клике на элементы
- **6 алгоритмов компоновки графа:**
  - Пружинная (Spring) — физическая симуляция
  - Круговая (Circular) — узлы по кругу
  - Kamada-Kawai — минимизация энергии
  - Спектральная (Spectral) — на основе собственных векторов
  - Оболочка (Shell) — концентрические круги
  - Иерархическая — древовидное расположение
- **Различные формы узлов** для разных типов объектов
- **4 цветовые схемы:** Default, Dark, Pastel, Vibrant
- **Экспорт графа** в PNG с высоким разрешением (300 DPI)

### Работа с данными
- **Импорт из конфигурационных файлов:**
  - Docker Compose (YAML)
  - Kubernetes (YAML)
  - Godot-проекты (с анализом зависимостей)
- **Фильтрация при импорте Godot:**
  - Исключение текстур (.png, .jpg, .webp, .svg)
  - Исключение аудио (.wav, .ogg, .mp3)
  - Исключение шрифтов (.ttf, .otf, .woff)
- **Сохранение и загрузка** проектов в JSON формате
- **Многооконный интерфейс** — работа с несколькими проектами одновременно

### Интерфейс
- **Поддержка двух языков:** Русский и English
- **Современный Material Design** интерфейс
- **Подробная информация** об объектах и связях
- **Защита от потери данных** — предупреждение о несохраненных изменениях

---

## 📋 Требования

- **Python 3.8+**
- **Linux** (Ubuntu 20.04+ или аналогичные дистрибутивы)
- **Зависимости Python**:
  - PyQt5
  - networkx
  - matplotlib
  - PyYAML

---

## 🚀 Установка

### Шаг 1: Клонирование репозитория

```bash
git clone https://github.com/AlexandrD7/Dependency_manager.git
cd Dependency-manager
```

### Шаг 2: Создание виртуального окружения

**⚠️ ВАЖНО:** Виртуальное окружение должно называться **строго `venv`**, так как это имя жёстко задано в скриптах!

```bash
python3 -m venv venv
```

### Шаг 3: Активация виртуального окружения

```bash
source venv/bin/activate
```

### Шаг 4: Установка зависимостей

```bash
pip install -r requirements.txt
```

### Шаг 5 (опционально): Удаление примеров

Example-файлы (`docker-compose-example.yml`, `kubernetes-example.yaml`, `example_infrastructure.json`) предназначены для демонстрации возможностей импорта и могут быть удалены:

```bash
rm docker-compose-example.yml kubernetes-example.yaml example_infrastructure.json
```

---

## 💻 Запуск приложения

### Способ 1: Запуск через терминал

#### Вариант A: Прямой запуск

```bash
# Активируйте виртуальное окружение, если ещё не активировано
source venv/bin/activate

# Запустите приложение
python3 dependency_manager.py
```

#### Вариант B: Использование скрипта запуска

```bash
# Сделайте скрипт исполняемым (только первый раз)
chmod +x run_dependency_manager.sh

# Запустите приложение
./run_dependency_manager.sh
```

Скрипт `run_dependency_manager.sh` автоматически:
- Проверяет наличие виртуального окружения `venv`
- Активирует окружение
- Запускает приложение
- Выводит ошибки, если что-то пошло не так

### Способ 2: Создание ярлыка в меню приложений

Для удобного запуска из меню приложений используйте скрипт `icon.sh`:

```bash
# Сделайте скрипт исполняемым
chmod +x icon.sh

# Запустите скрипт создания ярлыка
./icon.sh
```

**Что делает скрипт:**
- Создаёт desktop-файл в `~/.local/share/applications/`
- Приложение появится в меню в категории **Development → Utility**
- Название: **Dependency Manager**

**После выполнения:**
- Приложение появится в меню приложений
- Если не появилось сразу — выйдите и войдите в систему или перезагрузитесь

**Примечание:** Для работы ярлыка необходима иконка `dependency_manager_icon.svg` в директории проекта.

---

## 📖 Использование

### Создание нового проекта

1. Запустите приложение
2. **Файл → Новый проект** (или Ctrl+N)
3. Добавьте объекты через вкладку **"Объекты"**
4. Создайте связи через вкладку **"Связи"**
5. Визуализация обновится автоматически

### Добавление объекта

1. Перейдите на вкладку **"Объекты"**
2. Нажмите кнопку **"Добавить"**
3. Заполните:
   - **ID объекта** — уникальный идентификатор
   - **Тип объекта** — выберите из списка
   - **Название** — понятное имя
   - **Описание** — дополнительная информация (опционально)
4. Нажмите **"Сохранить"**

### Создание связи

1. Создайте минимум 2 объекта
2. Перейдите на вкладку **"Связи"**
3. Нажмите **"Добавить"**
4. Выберите:
   - **Исходный объект**
   - **Тип связи** (calls, depends_on, connects_to и др.)
   - **Целевой объект**
   - **Описание** (опционально)
5. Нажмите **"Сохранить"**

### Навигация по графу

- **Масштабирование:** Колесо мыши
- **Панорамирование:** Средняя кнопка мыши ИЛИ Shift + Левая кнопка мыши ИЛИ кнопка "Перемещение"
- **Перетаскивание узлов:** Левая кнопка мыши на узле
- **Просмотр информации:** Клик по узлу
- **Выделение связи:** Клик по связи в списке

### Импорт данных

#### Из Docker Compose:
1. **Файл → Импорт → Docker Compose**
2. Выберите файл `.yml` или `.yaml`
3. Приложение автоматически создаст:
   - Контейнеры как объекты типа "docker_container"
   - Зависимости между контейнерами
   - Volumes как объекты типа "database"

#### Из Kubernetes:
1. **Файл → Импорт → Kubernetes**
2. Выберите файл `.yml` или `.yaml`
3. Приложение импортирует:
   - Deployments как контейнеры
   - Services как серверы
   - PersistentVolumeClaims как базы данных
   - Связи между компонентами

#### Из Godot-проекта:
1. **Файл → Импорт → Godot Project**
2. Выберите папку с Godot-проектом (содержащую `project.godot`)
3. В диалоге фильтрации выберите, что исключить:
   - ☐ Текстуры — исключить изображения
   - ☐ Аудио — исключить звуковые файлы
   - ☐ Шрифты — исключить файлы шрифтов
4. Нажмите **"Импортировать"**
5. Приложение создаст:
   - Сцены (.tscn) как объекты типа "godot_scene"
   - Скрипты (.gd) как объекты типа "godot_script"
   - Ресурсы (.tres) как объекты типа "godot_resource"
   - Autoload-модули как объекты типа "godot_autoload"
   - Зависимости между всеми компонентами

### Выбор алгоритма компоновки

1. Нажмите кнопку **"Компоновка"** на панели визуализации
2. Выберите алгоритм из списка:
   - **Пружинная (Spring)** — хорошо для общих графов
   - **Круговая (Circular)** — узлы равномерно по кругу
   - **Kamada-Kawai** — оптимизация расстояний
   - **Спектральная (Spectral)** — хорошо для кластеров
   - **Оболочка (Shell)** — концентрические уровни
   - **Иерархическая** — для деревьев и DAG
3. Нажмите **OK** для применения

### Экспорт графа

1. Нажмите кнопку **"Экспорт PNG"**
2. Выберите место сохранения
3. Граф будет сохранён в высоком качестве (300 DPI)

### Сохранение проекта

- **Сохранить:** Файл → Сохранить (Ctrl+S)
- **Сохранить как:** Файл → Сохранить как... (Ctrl+Shift+S)
- Проект сохраняется в формате JSON со всеми объектами и связями

---

## 🎨 Цветовые схемы

Приложение поддерживает 4 цветовые схемы:

- **Default** — яркие контрастные цвета
- **Dark** — приглушённые тёмные тона
- **Pastel** — нежные пастельные оттенки
- **Vibrant** — насыщенные энергичные цвета

Смена схемы: кнопка **"Цветовая схема"** на панели визуализации.

---

## 📁 Структура проекта

```
dependency-manager/
│
├── dependency_manager.py          # Основное приложение
├── godot_analyzer.py              # Анализатор зависимостей Godot
├── requirements.txt               # Python зависимости
├── run_dependency_manager.sh      # Скрипт запуска
├── icon.sh                        # Скрипт создания ярлыка
├── dependency_manager_icon.svg    # Иконка приложения
│
├── docker-compose-example.yml     # Пример Docker Compose (можно удалить)
├── kubernetes-example.yaml        # Пример Kubernetes (можно удалить)
├── example_infrastructure.json    # Пример проекта (можно удалить)
│
└── venv/                          # Виртуальное окружение
```

---

## 🔧 Решение проблем

### Приложение не запускается

```bash
# Проверьте, что виртуальное окружение называется именно venv
ls -la | grep venv

# Убедитесь, что окружение активировано
which python3  # должен показать путь к venv/bin/python3

# Переустановите зависимости
pip install --upgrade -r requirements.txt
```

### Ошибка "виртуальное окружение не найдено"

Убедитесь, что виртуальное окружение:
1. Называется **строго `venv`** (не `env`, не `.venv`, не другое имя!)
2. Находится в корневой директории проекта
3. Содержит директорию `bin/` с исполняемыми файлами

```bash
# Пересоздайте окружение с правильным именем
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Ярлык не появляется в меню

```bash
# Обновите базу данных desktop-файлов вручную
update-desktop-database ~/.local/share/applications/

# Или выйдите и войдите в систему
# Или перезагрузите компьютер
```

### Ошибки при импорте Godot-проекта

- Убедитесь, что выбрана папка, содержащая файл `project.godot`
- Проверьте, что проект создан в Godot 4.x (поддержка 3.x ограничена)
- При больших проектах используйте фильтрацию для исключения текстур и аудио

---

## 📝 Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).

---

# English Version

## 🌟 Key Features

### Infrastructure Object Management
- **Support for multiple object types:**
  - 📄 Files
  - 🐳 Docker Containers
  - 🌐 Routers
  - ⚡ Switches
  - 🖥️ Servers
  - 💾 Databases
- **Godot Engine object support:**
  - 🎬 Scenes
  - 📜 Scripts
  - 📦 Resources
  - ⚙️ Autoload singletons

### Interactive Visualization
- **Graphical dependency representation** using NetworkX and Matplotlib
- **Interactive graph control:**
  - Drag nodes with mouse to reposition
  - Smooth zoom with mouse wheel
  - Pan with middle mouse button or Shift+LMB
  - Highlight connections on click
- **6 graph layout algorithms:**
  - Spring — force-directed layout
  - Circular — nodes arranged in circle
  - Kamada-Kawai — energy minimization
  - Spectral — eigenvector-based
  - Shell — concentric circles
  - Hierarchical — tree-like arrangement
- **Different node shapes** for different object types
- **4 color schemes:** Default, Dark, Pastel, Vibrant
- **Export graph** to high-resolution PNG (300 DPI)

### Data Operations
- **Import from configuration files:**
  - Docker Compose (YAML)
  - Kubernetes (YAML)
  - Godot projects (with dependency analysis)
- **Godot import filtering:**
  - Exclude textures (.png, .jpg, .webp, .svg)
  - Exclude audio (.wav, .ogg, .mp3)
  - Exclude fonts (.ttf, .otf, .woff)
- **Save and load** projects in JSON format
- **Multi-window interface** — work with multiple projects simultaneously

### Interface
- **Bilingual support:** Russian and English
- **Modern Material Design** interface
- **Detailed information** about objects and relationships
- **Data loss protection** — warnings about unsaved changes

---

## 📋 Requirements

- **Python 3.8+**
- **Linux** (Ubuntu 20.04+ or similar distributions)
- **Python Dependencies** (installed automatically):
  - PyQt5
  - networkx
  - matplotlib
  - PyYAML

---

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/AlexandrD7/Dependency_manager.git
cd Dependency-manager
```

### Step 2: Create Virtual Environment

**⚠️ IMPORTANT:** The virtual environment must be named **exactly `venv`**, as this name is hardcoded in scripts!

```bash
python3 -m venv venv
```

### Step 3: Activate Virtual Environment

```bash
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5 (Optional): Remove Examples

Example files (`docker-compose-example.yml`, `kubernetes-example.yaml`, `example_infrastructure.json`) are for demonstration purposes and can be removed:

```bash
rm docker-compose-example.yml kubernetes-example.yaml example_infrastructure.json
```

---

## 💻 Running the Application

### Method 1: Run via Terminal

#### Option A: Direct Launch

```bash
# Activate virtual environment if not already activated
source venv/bin/activate

# Run the application
python3 dependency_manager.py
```

#### Option B: Using Launch Script

```bash
# Make script executable (first time only)
chmod +x run_dependency_manager.sh

# Run the application
./run_dependency_manager.sh
```

The `run_dependency_manager.sh` script automatically:
- Checks for `venv` virtual environment
- Activates the environment
- Launches the application
- Shows errors if something goes wrong

### Method 2: Create Desktop Launcher

For convenient launch from application menu, use the `icon.sh` script:

```bash
# Make script executable
chmod +x icon.sh

# Run the launcher creation script
./icon.sh
```

**What the script does:**
- Creates a desktop file in `~/.local/share/applications/`
- Application appears in menu under **Development → Utility**
- Name: **Dependency Manager**

**After execution:**
- Application appears in applications menu
- If not visible immediately — log out and log in, or reboot

**Note:** The launcher requires `dependency_manager_icon.svg` icon file in the project directory.

---

## 📖 Usage

### Creating a New Project

1. Launch the application
2. **File → New Project** (or Ctrl+N)
3. Add objects via **"Objects"** tab
4. Create relationships via **"Relationships"** tab
5. Visualization updates automatically

### Adding an Object

1. Go to **"Objects"** tab
2. Click **"Add"** button
3. Fill in:
   - **Object ID** — unique identifier
   - **Object Type** — select from list
   - **Name** — readable name
   - **Description** — additional info (optional)
4. Click **"Save"**

### Creating a Relationship

1. Create at least 2 objects
2. Go to **"Relationships"** tab
3. Click **"Add"**
4. Select:
   - **Source Object**
   - **Relationship Type** (calls, depends_on, connects_to, etc.)
   - **Target Object**
   - **Description** (optional)
5. Click **"Save"**

### Graph Navigation

- **Zoom:** Mouse wheel
- **Pan:** Middle mouse button OR Shift + Left mouse button OR "Pan" button
- **Drag nodes:** Left mouse button on node
- **View information:** Click on node
- **Highlight relationship:** Click on relationship in list

### Data Import

#### From Docker Compose:
1. **File → Import → Docker Compose**
2. Select `.yml` or `.yaml` file
3. Application automatically creates:
   - Containers as "docker_container" objects
   - Dependencies between containers
   - Volumes as "database" objects

#### From Kubernetes:
1. **File → Import → Kubernetes**
2. Select `.yml` or `.yaml` file
3. Application imports:
   - Deployments as containers
   - Services as servers
   - PersistentVolumeClaims as databases
   - Relationships between components

#### From Godot Project:
1. **File → Import → Godot Project**
2. Select folder with Godot project (containing `project.godot`)
3. In filter dialog, choose what to exclude:
   - ☐ Textures — exclude images
   - ☐ Audio — exclude sound files
   - ☐ Fonts — exclude font files
4. Click **"Import"**
5. Application creates:
   - Scenes (.tscn) as "godot_scene" objects
   - Scripts (.gd) as "godot_script" objects
   - Resources (.tres) as "godot_resource" objects
   - Autoload modules as "godot_autoload" objects
   - Dependencies between all components

### Choosing Layout Algorithm

1. Click **"Layout"** button on visualization panel
2. Select algorithm from list:
   - **Spring** — good for general graphs
   - **Circular** — nodes evenly around circle
   - **Kamada-Kawai** — distance optimization
   - **Spectral** — good for clusters
   - **Shell** — concentric levels
   - **Hierarchical** — for trees and DAGs
3. Click **OK** to apply

### Graph Export

1. Click **"Export PNG"** button
2. Choose save location
3. Graph saved in high quality (300 DPI)

### Saving Project

- **Save:** File → Save (Ctrl+S)
- **Save As:** File → Save As... (Ctrl+Shift+S)
- Project saved in JSON format with all objects and relationships

---

## 🔧 Troubleshooting

### Application Won't Start

```bash
# Check that virtual environment is named venv
ls -la | grep venv

# Make sure environment is activated
which python3  # should show path to venv/bin/python3

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Error "virtual environment not found"

Ensure the virtual environment:
1. Is named **exactly `venv`** (not `env`, not `.venv`, not another name!)
2. Is in the project root directory
3. Contains `bin/` directory with executables

```bash
# Recreate environment with correct name
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Launcher Not Appearing in Menu

```bash
# Update desktop database manually
update-desktop-database ~/.local/share/applications/

# Or log out and log in
# Or reboot the computer
```

### Errors When Importing Godot Project

- Make sure to select folder containing `project.godot` file
- Check that project was created in Godot 4.x (3.x support is limited)
- For large projects, use filtering to exclude textures and audio

---

## 📁 Project Structure

```
dependency-manager/
│
├── dependency_manager.py          # Main application
├── godot_analyzer.py              # Godot dependency analyzer
├── requirements.txt               # Python dependencies
├── run_dependency_manager.sh      # Launch script
├── icon.sh                        # Desktop launcher creation script
├── dependency_manager_icon.svg    # Application icon
│
├── docker-compose-example.yml     # Docker Compose example (can be deleted)
├── kubernetes-example.yaml        # Kubernetes example (can be deleted)
├── example_infrastructure.json    # Project example (can be deleted)
│
└── venv/                          # Virtual environment
```

---

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

---
