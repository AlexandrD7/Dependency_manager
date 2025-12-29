#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Анализатор зависимостей Godot проектов.

Модуль для анализа зависимостей в проектах Godot Engine 4.x.
Интегрируется с Dependency Infrastructure Manager.

Поддерживает:
    - Парсинг .tscn файлов (сцены)
    - Парсинг .gd файлов (GDScript)
    - Анализ project.godot
    - Определение autoload синглтонов
    - Фильтрацию по типам ресурсов

Пример использования:
    >>> analyzer = GodotDependencyAnalyzer('/path/to/godot/project')
    >>> analyzer.analyze()
    >>> stats = analyzer.get_statistics()
    >>> print(f"Найдено ресурсов: {stats['total_resources']}")
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class GodotResourceType(Enum):
    """Перечисление типов ресурсов Godot.

    Attributes:
        SCENE: Сцена (.tscn, .scn).
        SCRIPT: Скрипт (.gd, .cs).
        RESOURCE: Общий ресурс (.tres, .res).
        TEXTURE: Текстура (.png, .jpg, .webp, .svg).
        AUDIO: Аудио (.wav, .ogg, .mp3).
        SHADER: Шейдер (.gdshader, .shader).
        FONT: Шрифт (.ttf, .otf, .woff).
        AUTOLOAD: Autoload синглтон.
        UNKNOWN: Неизвестный тип.
    """
    SCENE = "scene"
    SCRIPT = "script"
    RESOURCE = "resource"
    TEXTURE = "texture"
    AUDIO = "audio"
    SHADER = "shader"
    FONT = "font"
    AUTOLOAD = "autoload"
    UNKNOWN = "unknown"


@dataclass
class GodotResource:
    """Представление ресурса Godot.

    Хранит информацию о файле ресурса в проекте.

    Attributes:
        path: Путь в формате res:// (например, res://scenes/main.tscn).
        type: Тип ресурса из GodotResourceType.
        name: Отображаемое имя ресурса.
        file_path: Абсолютный путь к файлу на диске.
        properties: Дополнительные свойства ресурса.
    """
    path: str
    type: GodotResourceType
    name: str
    file_path: str
    properties: Dict = field(default_factory=dict)

    @property
    def id(self) -> str:
        """Генерирует уникальный ID на основе пути.

        Returns:
            Строка ID без спецсимволов (для использования в DependencyManager).
        """
        return self.path.replace("res://", "").replace("/", "_").replace(".", "_").replace("-", "_")


@dataclass
class GodotDependency:
    """Зависимость между ресурсами Godot.

    Представляет направленную связь от одного ресурса к другому.

    Attributes:
        source: Путь res:// исходного ресурса.
        target: Путь res:// целевого ресурса.
        dep_type: Тип зависимости (uses_scene, extends, preloads и т.д.).
        context: Контекст зависимости (строка кода, узел сцены и т.д.).
    """
    source: str
    target: str
    dep_type: str
    context: str = ""


class GodotSceneParser:
    """Парсер файлов сцен Godot (.tscn).

    Извлекает внешние ресурсы, узлы со скриптами,
    инстансы сцен и сигнальные соединения.

    Поддерживает форматы Godot 3.x и 4.x.

    Attributes:
        file_path: Путь к файлу сцены.
        project_root: Корневая директория проекта.
        ext_resources: Словарь внешних ресурсов {id: (type, path)}.
        nodes: Список узлов сцены.
        connections: Список сигнальных соединений.
        dependencies: Список найденных зависимостей.
    """

    # Регулярные выражения для парсинга формата Godot 4.x
    EXT_RESOURCE_PATTERN = re.compile(
        r'\[ext_resource\s+type="([^"]+)"\s+(?:uid="[^"]+"\s+)?path="([^"]+)"\s+id="([^"]+)"\]'
    )

    # Альтернативный формат (Godot 3.x и некоторые 4.x)
    EXT_RESOURCE_ALT_PATTERN = re.compile(
        r'\[ext_resource\s+path="([^"]+)"\s+type="([^"]+)"\s+id=(\d+)\]'
    )

    # Паттерн узла с возможным инстансом сцены
    NODE_PATTERN = re.compile(
        r'\[node\s+name="([^"]+)"(?:\s+type="([^"]+)")?(?:\s+parent="([^"]+)")?(?:\s+instance=ExtResource\(["\']?([^"\')]+)["\']?\))?\]'
    )

    # Паттерн привязки скрипта к узлу
    SCRIPT_ASSIGN_PATTERN = re.compile(
        r'script\s*=\s*ExtResource\(["\']?([^"\')]+)["\']?\)'
    )

    # Паттерн сигнального соединения
    CONNECTION_PATTERN = re.compile(
        r'\[connection\s+signal="([^"]+)"\s+from="([^"]+)"\s+to="([^"]+)"\s+method="([^"]+)"\]'
    )

    def __init__(self, file_path: str, project_root: Path) -> None:
        """Инициализирует парсер сцены.

        Args:
            file_path: Путь к .tscn файлу.
            project_root: Корневая директория Godot проекта.
        """
        self.file_path = file_path
        self.project_root = project_root
        self.ext_resources: Dict[str, Tuple[str, str]] = {}
        self.nodes: List[Dict] = []
        self.connections: List[Dict] = []
        self.dependencies: List[GodotDependency] = []

    def parse(self) -> List[GodotDependency]:
        """Парсит сцену и извлекает зависимости.

        Анализирует:
            - Внешние ресурсы (ext_resource)
            - Инстансы сцен в узлах
            - Привязки скриптов
            - Сигнальные соединения

        Returns:
            Список зависимостей GodotDependency.
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Ошибка чтения {self.file_path}: {e}")
            return []

        scene_path = self._get_res_path()

        # Парсим внешние ресурсы (формат Godot 4.x)
        for match in self.EXT_RESOURCE_PATTERN.finditer(content):
            res_type, res_path, res_id = match.groups()
            self.ext_resources[res_id] = (res_type, res_path)

            dep_type = self._classify_dependency(res_type)
            self.dependencies.append(GodotDependency(
                source=scene_path,
                target=res_path,
                dep_type=dep_type,
                context=f"ext_resource: {res_type}"
            ))

        # Парсим внешние ресурсы (альтернативный формат)
        for match in self.EXT_RESOURCE_ALT_PATTERN.finditer(content):
            res_path, res_type, res_id = match.groups()
            self.ext_resources[res_id] = (res_type, res_path)

            dep_type = self._classify_dependency(res_type)
            self.dependencies.append(GodotDependency(
                source=scene_path,
                target=res_path,
                dep_type=dep_type,
                context=f"ext_resource: {res_type}"
            ))

        # Парсим узлы (для инстансов сцен)
        for match in self.NODE_PATTERN.finditer(content):
            name, node_type, parent, instance_id = match.groups()
            if instance_id:
                instance_id = instance_id.strip('"\'')
                if instance_id in self.ext_resources:
                    _, instance_path = self.ext_resources[instance_id]
                    self.dependencies.append(GodotDependency(
                        source=scene_path,
                        target=instance_path,
                        dep_type="instances",
                        context=f"node instance: {name}"
                    ))

        # Парсим привязки скриптов
        for match in self.SCRIPT_ASSIGN_PATTERN.finditer(content):
            script_id = match.group(1).strip('"\'')
            if script_id in self.ext_resources:
                _, script_path = self.ext_resources[script_id]
                self.dependencies.append(GodotDependency(
                    source=scene_path,
                    target=script_path,
                    dep_type="has_script",
                    context="attached script"
                ))

        # Парсим сигнальные соединения
        for match in self.CONNECTION_PATTERN.finditer(content):
            signal_name, from_node, to_node, method = match.groups()
            self.connections.append({
                'signal': signal_name,
                'from': from_node,
                'to': to_node,
                'method': method
            })

        return self.dependencies

    def _get_res_path(self) -> str:
        """Преобразует абсолютный путь в формат res://.

        Returns:
            Путь в формате res://.
        """
        try:
            rel_path = Path(self.file_path).relative_to(self.project_root)
            return f"res://{rel_path.as_posix()}"
        except ValueError:
            return f"res://{Path(self.file_path).name}"

    def _classify_dependency(self, godot_type: str) -> str:
        """Классифицирует тип зависимости по типу Godot ресурса.

        Args:
            godot_type: Тип ресурса из Godot (PackedScene, Script и т.д.).

        Returns:
            Строка типа зависимости для DependencyManager.
        """
        type_map = {
            'PackedScene': 'uses_scene',
            'Script': 'uses_script',
            'GDScript': 'uses_script',
            'CSharpScript': 'uses_script',
            'Texture2D': 'uses_texture',
            'CompressedTexture2D': 'uses_texture',
            'ImageTexture': 'uses_texture',
            'AtlasTexture': 'uses_texture',
            'AudioStream': 'uses_audio',
            'AudioStreamMP3': 'uses_audio',
            'AudioStreamOggVorbis': 'uses_audio',
            'AudioStreamWAV': 'uses_audio',
            'Material': 'uses_material',
            'ShaderMaterial': 'uses_shader',
            'StandardMaterial3D': 'uses_material',
            'Shader': 'uses_shader',
            'Font': 'uses_font',
            'FontFile': 'uses_font',
            'SystemFont': 'uses_font',
            'Theme': 'uses_resource',
            'Resource': 'uses_resource',
            'Animation': 'uses_resource',
            'AnimationLibrary': 'uses_resource',
            'SpriteFrames': 'uses_resource',
            'TileSet': 'uses_resource',
            'Environment': 'uses_resource',
        }
        return type_map.get(godot_type, 'uses')


class GodotScriptParser:
    """Парсер GDScript файлов.

    Извлекает зависимости из скриптов:
        - extends с путём к файлу
        - preload() вызовы
        - load() вызовы
        - Определения сигналов

    Attributes:
        file_path: Путь к .gd файлу.
        project_root: Корневая директория проекта.
        class_name: Имя класса (class_name).
        extends: Родительский класс/файл.
        signals: Список определённых сигналов.
        dependencies: Список найденных зависимостей.
    """

    # Регулярные выражения для парсинга GDScript
    EXTENDS_PATTERN = re.compile(r'^extends\s+["\']([^"\']+)["\']', re.MULTILINE)
    EXTENDS_CLASS_PATTERN = re.compile(r'^extends\s+(\w+)', re.MULTILINE)
    CLASS_NAME_PATTERN = re.compile(r'^class_name\s+(\w+)', re.MULTILINE)
    PRELOAD_PATTERN = re.compile(r'preload\s*\(\s*["\']([^"\']+)["\']\s*\)')
    LOAD_PATTERN = re.compile(r'(?<!pre)load\s*\(\s*["\']([^"\']+)["\']\s*\)')
    CONST_SCENE_PATTERN = re.compile(
        r'(?:const|var)\s+(\w+)\s*[=:]\s*preload\s*\(\s*["\']([^"\']+\.tscn)["\']\s*\)'
    )
    GET_NODE_PATTERN = re.compile(r'get_node\s*\(\s*["\']([^"\']+)["\']\s*\)')
    ONREADY_PATTERN = re.compile(r'@onready\s+var\s+(\w+)\s*[=:]\s*\$([^\s\n]+)')
    SIGNAL_PATTERN = re.compile(r'^signal\s+(\w+)', re.MULTILINE)
    CONNECT_PATTERN = re.compile(r'\.connect\s*\(\s*["\'](\w+)["\']')

    def __init__(self, file_path: str, project_root: Path) -> None:
        """Инициализирует парсер скрипта.

        Args:
            file_path: Путь к .gd файлу.
            project_root: Корневая директория Godot проекта.
        """
        self.file_path = file_path
        self.project_root = project_root
        self.class_name: Optional[str] = None
        self.extends: Optional[str] = None
        self.signals: List[str] = []
        self.dependencies: List[GodotDependency] = []

    def parse(self) -> List[GodotDependency]:
        """Парсит скрипт и извлекает зависимости.

        Анализирует:
            - extends с путём к файлу
            - preload() и load() вызовы
            - Определения сигналов

        Returns:
            Список зависимостей GodotDependency.
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Ошибка чтения {self.file_path}: {e}")
            return []

        script_path = self._get_res_path()

        # Парсим extends с путём к файлу
        extends_match = self.EXTENDS_PATTERN.search(content)
        if extends_match:
            extends_value = extends_match.group(1)
            target = extends_value if extends_value.startswith("res://") else f"res://{extends_value}"
            self.dependencies.append(GodotDependency(
                source=script_path,
                target=target,
                dep_type="extends",
                context=f"extends {extends_value}"
            ))
            self.extends = extends_value

        # Парсим class_name
        class_match = self.CLASS_NAME_PATTERN.search(content)
        if class_match:
            self.class_name = class_match.group(1)

        # Парсим preload
        for match in self.PRELOAD_PATTERN.finditer(content):
            res_path = match.group(1)
            if res_path.startswith("res://"):
                dep_type = "preloads_scene" if res_path.endswith(".tscn") else "preloads"
                self.dependencies.append(GodotDependency(
                    source=script_path,
                    target=res_path,
                    dep_type=dep_type,
                    context=f"preload({res_path})"
                ))

        # Парсим load (runtime загрузка)
        for match in self.LOAD_PATTERN.finditer(content):
            res_path = match.group(1)
            if res_path.startswith("res://"):
                dep_type = "loads_scene" if res_path.endswith(".tscn") else "loads"
                self.dependencies.append(GodotDependency(
                    source=script_path,
                    target=res_path,
                    dep_type=dep_type,
                    context=f"load({res_path})"
                ))

        # Парсим сигналы
        for match in self.SIGNAL_PATTERN.finditer(content):
            self.signals.append(match.group(1))

        return self.dependencies

    def _get_res_path(self) -> str:
        """Преобразует абсолютный путь в формат res://.

        Returns:
            Путь в формате res://.
        """
        try:
            rel_path = Path(self.file_path).relative_to(self.project_root)
            return f"res://{rel_path.as_posix()}"
        except ValueError:
            return f"res://{Path(self.file_path).name}"


class GodotProjectParser:
    """Парсер файла project.godot.

    Извлекает информацию о проекте:
        - Имя проекта
        - Autoload синглтоны

    Attributes:
        project_path: Путь к файлу project.godot.
        project_root: Корневая директория проекта.
        autoloads: Словарь autoload {имя: путь res://}.
        project_name: Название проекта.
    """

    AUTOLOAD_PATTERN = re.compile(r'^(\w+)="?\*?res://([^"\n]+)"?$', re.MULTILINE)

    def __init__(self, project_path: str) -> None:
        """Инициализирует парсер проекта.

        Args:
            project_path: Путь к файлу project.godot.
        """
        self.project_path = project_path
        self.project_root = Path(project_path).parent
        self.autoloads: Dict[str, str] = {}
        self.project_name: str = "Godot Project"

    def parse(self) -> Dict[str, str]:
        """Парсит project.godot и извлекает настройки.

        Returns:
            Словарь autoload {имя: путь res://}.
        """
        try:
            with open(self.project_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Ошибка чтения project.godot: {e}")
            return {}

        # Ищем секцию autoload
        in_autoload = False
        for line in content.split('\n'):
            line = line.strip()
            if line == '[autoload]':
                in_autoload = True
                continue
            elif line.startswith('[') and in_autoload:
                in_autoload = False
                continue

            if in_autoload and '=' in line:
                match = self.AUTOLOAD_PATTERN.match(line)
                if match:
                    name, path = match.groups()
                    self.autoloads[name] = f"res://{path}"

        # Ищем имя проекта
        name_match = re.search(r'config/name="([^"]+)"', content)
        if name_match:
            self.project_name = name_match.group(1)

        return self.autoloads


class GodotDependencyAnalyzer:
    """Главный класс анализатора зависимостей Godot проекта.

    Выполняет полный анализ проекта:
        - Сканирование всех файлов
        - Парсинг сцен и скриптов
        - Определение autoload
        - Построение графа зависимостей

    Интегрируется с DependencyManager из основного приложения.

    Attributes:
        project_root: Корневая директория проекта.
        project_godot: Путь к файлу project.godot.
        resources: Словарь ресурсов {путь res://: GodotResource}.
        dependencies: Список зависимостей.
        autoloads: Словарь autoload синглтонов.
        project_name: Название проекта.
        exclude_textures: Флаг исключения текстур.
        exclude_audio: Флаг исключения аудио.
        exclude_fonts: Флаг исключения шрифтов.

    Example:
        >>> analyzer = GodotDependencyAnalyzer('/path/to/project')
        >>> analyzer.analyze()
        >>> stats = analyzer.get_statistics()
        >>> print(stats['total_resources'])
    """

    # Маппинг расширений файлов на типы ресурсов
    SUPPORTED_EXTENSIONS = {
        '.tscn': GodotResourceType.SCENE,
        '.scn': GodotResourceType.SCENE,
        '.gd': GodotResourceType.SCRIPT,
        '.cs': GodotResourceType.SCRIPT,
        '.tres': GodotResourceType.RESOURCE,
        '.res': GodotResourceType.RESOURCE,
        '.png': GodotResourceType.TEXTURE,
        '.jpg': GodotResourceType.TEXTURE,
        '.jpeg': GodotResourceType.TEXTURE,
        '.webp': GodotResourceType.TEXTURE,
        '.svg': GodotResourceType.TEXTURE,
        '.wav': GodotResourceType.AUDIO,
        '.ogg': GodotResourceType.AUDIO,
        '.mp3': GodotResourceType.AUDIO,
        '.gdshader': GodotResourceType.SHADER,
        '.shader': GodotResourceType.SHADER,
        '.ttf': GodotResourceType.FONT,
        '.otf': GodotResourceType.FONT,
        '.woff': GodotResourceType.FONT,
        '.woff2': GodotResourceType.FONT,
    }

    def __init__(self, project_root: str, exclude_textures: bool = True,
                 exclude_audio: bool = False, exclude_fonts: bool = False) -> None:
        """Инициализирует анализатор проекта.

        Args:
            project_root: Путь к корню Godot проекта (где лежит project.godot).
            exclude_textures: Исключить текстуры из анализа (по умолчанию True).
            exclude_audio: Исключить аудио файлы из анализа.
            exclude_fonts: Исключить шрифты из анализа.

        Raises:
            ValueError: Если project.godot не найден в указанной директории.
        """
        self.project_root = Path(project_root)
        self.project_godot = self.project_root / "project.godot"

        if not self.project_godot.exists():
            raise ValueError(f"Не найден project.godot в {project_root}")

        self.resources: Dict[str, GodotResource] = {}
        self.dependencies: List[GodotDependency] = []
        self.autoloads: Dict[str, str] = {}
        self.project_name: str = "Godot Project"

        # Настройки фильтрации
        self.exclude_textures = exclude_textures
        self.exclude_audio = exclude_audio
        self.exclude_fonts = exclude_fonts

        # Формируем множество исключённых типов
        self._excluded_types: set = set()
        if exclude_textures:
            self._excluded_types.add(GodotResourceType.TEXTURE)
        if exclude_audio:
            self._excluded_types.add(GodotResourceType.AUDIO)
        if exclude_fonts:
            self._excluded_types.add(GodotResourceType.FONT)

    def analyze(self) -> Tuple[int, int]:
        """Выполняет полный анализ проекта.

        Этапы анализа:
            1. Парсинг project.godot
            2. Сканирование файлов проекта
            3. Добавление autoload как особых ресурсов
            4. Парсинг зависимостей из сцен и скриптов
            5. Удаление дубликатов

        Returns:
            Кортеж (количество ресурсов, количество зависимостей).
        """
        # 1. Парсим project.godot
        project_parser = GodotProjectParser(str(self.project_godot))
        self.autoloads = project_parser.parse()
        self.project_name = project_parser.project_name

        # 2. Сканируем все файлы проекта
        self._scan_project_files()

        # 3. Добавляем autoload как особые ресурсы
        for name, path in self.autoloads.items():
            if path not in self.resources:
                file_path = self.project_root / path.replace("res://", "")
                self.resources[path] = GodotResource(
                    path=path,
                    type=GodotResourceType.AUTOLOAD,
                    name=f"[Autoload] {name}",
                    file_path=str(file_path),
                    properties={'autoload_name': name, 'singleton': True}
                )
            else:
                # Помечаем существующий ресурс как autoload
                self.resources[path].properties['autoload_name'] = name
                self.resources[path].properties['singleton'] = True
                self.resources[path].name = f"[Autoload] {name}"

        # 4. Парсим зависимости из сцен и скриптов
        self._parse_dependencies()

        # 5. Удаляем дубликаты зависимостей
        self._deduplicate_dependencies()

        return len(self.resources), len(self.dependencies)

    def _scan_project_files(self) -> None:
        """Сканирует все файлы проекта и создаёт ресурсы.

        Обходит директорию проекта рекурсивно, пропуская:
            - Служебные директории (.godot, .import)
            - Скрытые файлы
            - Исключённые типы ресурсов
        """
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file():
                # Пропускаем служебные директории
                parts_str = str(file_path)
                if '.godot' in parts_str or '.import' in parts_str or '__pycache__' in parts_str:
                    continue
                if file_path.name.startswith('.'):
                    continue

                ext = file_path.suffix.lower()
                if ext in self.SUPPORTED_EXTENSIONS:
                    res_type = self.SUPPORTED_EXTENSIONS[ext]

                    # Пропускаем исключённые типы
                    if res_type in self._excluded_types:
                        continue

                    rel_path = file_path.relative_to(self.project_root)
                    res_path = f"res://{rel_path.as_posix()}"

                    # Формируем отображаемое имя с префиксом типа
                    name = file_path.stem
                    type_prefix = {
                        GodotResourceType.SCENE: '[Scene]',
                        GodotResourceType.SCRIPT: '[Script]',
                        GodotResourceType.RESOURCE: '[Resource]',
                        GodotResourceType.TEXTURE: '[Texture]',
                        GodotResourceType.AUDIO: '[Audio]',
                        GodotResourceType.SHADER: '[Shader]',
                        GodotResourceType.FONT: '[Font]',
                    }
                    display_name = f"{type_prefix.get(res_type, '')} {name}"

                    self.resources[res_path] = GodotResource(
                        path=res_path,
                        type=res_type,
                        name=display_name,
                        file_path=str(file_path),
                        properties={
                            'extension': ext,
                            'size': file_path.stat().st_size,
                            'relative_path': str(rel_path)
                        }
                    )

    def _parse_dependencies(self) -> None:
        """Парсит зависимости из всех ресурсов.

        Для каждого ресурса вызывает соответствующий парсер:
            - GodotSceneParser для сцен
            - GodotScriptParser для GDScript

        Также анализирует использование autoload синглтонов.
        """
        for res_path, resource in self.resources.items():
            if resource.type == GodotResourceType.SCENE:
                parser = GodotSceneParser(resource.file_path, self.project_root)
                self.dependencies.extend(parser.parse())

            elif resource.type == GodotResourceType.SCRIPT:
                if resource.file_path.endswith('.gd'):
                    parser = GodotScriptParser(resource.file_path, self.project_root)
                    self.dependencies.extend(parser.parse())

        # Анализируем использование autoload
        self._analyze_autoload_usage()

    def _analyze_autoload_usage(self) -> None:
        """Анализирует использование autoload синглтонов в скриптах.

        Ищет обращения к autoload по имени (например, Global.method())
        и создаёт зависимости типа uses_autoload.
        """
        for name, autoload_path in self.autoloads.items():
            for res_path, resource in self.resources.items():
                if resource.type == GodotResourceType.SCRIPT and res_path != autoload_path:
                    try:
                        with open(resource.file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        # Ищем использование autoload по имени
                        pattern = rf'\b{name}\s*\.'
                        if re.search(pattern, content):
                            self.dependencies.append(GodotDependency(
                                source=res_path,
                                target=autoload_path,
                                dep_type="uses_autoload",
                                context=f"Uses singleton: {name}"
                            ))
                    except Exception:
                        pass

    def _deduplicate_dependencies(self) -> None:
        """Удаляет дубликаты зависимостей и фильтрует исключённые типы.

        Зависимость считается дубликатом, если совпадают:
            - source (исходный ресурс)
            - target (целевой ресурс)
            - dep_type (тип зависимости)
        """
        seen = set()
        unique_deps = []

        # Определяем расширения исключённых типов
        excluded_extensions = set()
        for ext, res_type in self.SUPPORTED_EXTENSIONS.items():
            if res_type in self._excluded_types:
                excluded_extensions.add(ext)

        for dep in self.dependencies:
            # Проверяем, не ссылается ли зависимость на исключённый тип
            target_ext = Path(dep.target).suffix.lower()
            if target_ext in excluded_extensions:
                continue

            key = (dep.source, dep.target, dep.dep_type)
            if key not in seen:
                seen.add(key)
                unique_deps.append(dep)

        self.dependencies = unique_deps

    def get_statistics(self) -> Dict:
        """Возвращает статистику по проекту.

        Returns:
            Словарь со статистикой:
                - project_name: Название проекта
                - total_resources: Количество ресурсов
                - total_dependencies: Количество зависимостей
                - by_type: Словарь {тип: количество}
                - autoloads: Список имён autoload
                - dependency_types: Словарь {тип_зависимости: количество}
                - filters: Настройки фильтрации
        """
        stats = {
            'project_name': self.project_name,
            'total_resources': len(self.resources),
            'total_dependencies': len(self.dependencies),
            'by_type': {},
            'autoloads': list(self.autoloads.keys()),
            'dependency_types': {},
            'filters': {
                'exclude_textures': self.exclude_textures,
                'exclude_audio': self.exclude_audio,
                'exclude_fonts': self.exclude_fonts,
            }
        }

        # Подсчёт по типам ресурсов
        for resource in self.resources.values():
            type_name = resource.type.value
            stats['by_type'][type_name] = stats['by_type'].get(type_name, 0) + 1

        # Подсчёт по типам зависимостей
        for dep in self.dependencies:
            stats['dependency_types'][dep.dep_type] = stats['dependency_types'].get(dep.dep_type, 0) + 1

        return stats

    def export_to_dependency_manager(self, manager) -> Tuple[int, int]:
        """Экспортирует результаты анализа в DependencyManager.

        Преобразует ресурсы Godot в объекты InfraObject,
        а зависимости - в связи Relationship.

        Args:
            manager: Экземпляр DependencyManager из основного приложения.

        Returns:
            Кортеж (добавлено объектов, добавлено связей).
        """
        from dependency_manager import InfraObject, Relationship

        added_objects = 0
        added_relationships = 0

        # Маппинг типов Godot на типы визуализации
        type_mapping = {
            GodotResourceType.SCENE: 'godot_scene',
            GodotResourceType.SCRIPT: 'godot_script',
            GodotResourceType.RESOURCE: 'godot_resource',
            GodotResourceType.TEXTURE: 'godot_resource',
            GodotResourceType.AUDIO: 'godot_resource',
            GodotResourceType.SHADER: 'godot_script',
            GodotResourceType.FONT: 'godot_resource',
            GodotResourceType.AUTOLOAD: 'godot_autoload',
            GodotResourceType.UNKNOWN: 'godot_resource',
        }

        # Добавляем ресурсы как объекты
        for res_path, resource in self.resources.items():
            obj_type = type_mapping.get(resource.type, 'file')

            properties = {
                'godot_type': resource.type.value,
                'res_path': resource.path,
                **resource.properties
            }

            try:
                obj = InfraObject(
                    obj_id=f"godot_{resource.id}",
                    obj_type=obj_type,
                    name=resource.name,
                    properties=properties
                )

                if manager.add_object(obj):
                    added_objects += 1
            except Exception as e:
                print(f"Ошибка добавления объекта {resource.path}: {e}")

        # Маппинг типов зависимостей
        rel_type_map = {
            'uses_scene': 'uses',
            'uses_script': 'uses',
            'uses_texture': 'uses',
            'uses_audio': 'uses',
            'uses_shader': 'uses',
            'uses_material': 'uses',
            'uses_font': 'uses',
            'uses_resource': 'uses',
            'instances': 'depends_on',
            'extends': 'depends_on',
            'preloads': 'uses',
            'preloads_scene': 'uses',
            'loads': 'uses',
            'loads_scene': 'uses',
            'has_script': 'uses',
            'uses_autoload': 'connects_to',
            'uses': 'uses',
        }

        # Добавляем зависимости как связи
        for dep in self.dependencies:
            source_id = f"godot_{dep.source.replace('res://', '').replace('/', '_').replace('.', '_').replace('-', '_')}"
            target_id = f"godot_{dep.target.replace('res://', '').replace('/', '_').replace('.', '_').replace('-', '_')}"

            rel_type = rel_type_map.get(dep.dep_type, 'uses')

            # Проверяем, существуют ли оба объекта
            if source_id not in [f"godot_{r.id}" for r in self.resources.values()]:
                continue
            if target_id not in [f"godot_{r.id}" for r in self.resources.values()]:
                continue

            try:
                rel = Relationship(
                    source_id=source_id,
                    target_id=target_id,
                    rel_type=rel_type,
                    description=f"[{dep.dep_type}] {dep.context}"
                )

                if manager.add_relationship(rel):
                    added_relationships += 1
            except Exception:
                pass

        return added_objects, added_relationships


# =============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================================================

def analyze_godot_project(project_path: str, exclude_textures: bool = True,
                          exclude_audio: bool = False,
                          exclude_fonts: bool = False) -> Tuple[Dict, 'DependencyManager']:
    """Анализирует Godot проект и возвращает заполненный DependencyManager.

    Удобная функция для быстрого анализа без создания анализатора вручную.

    Args:
        project_path: Путь к папке с project.godot.
        exclude_textures: Исключить текстуры (по умолчанию True).
        exclude_audio: Исключить аудио файлы.
        exclude_fonts: Исключить шрифты.

    Returns:
        Кортеж (статистика, заполненный DependencyManager).

    Example:
        >>> stats, manager = analyze_godot_project('/path/to/project')
        >>> print(f"Найдено: {stats['total_resources']} ресурсов")
    """
    from dependency_manager import DependencyManager

    analyzer = GodotDependencyAnalyzer(
        project_path,
        exclude_textures=exclude_textures,
        exclude_audio=exclude_audio,
        exclude_fonts=exclude_fonts
    )
    analyzer.analyze()

    manager = DependencyManager()
    analyzer.export_to_dependency_manager(manager)

    return analyzer.get_statistics(), manager


# =============================================================================
# ТОЧКА ВХОДА (CLI)
# =============================================================================

if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description='Анализатор зависимостей Godot проекта',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python godot_analyzer.py /path/to/project
  python godot_analyzer.py /path/to/project --include-textures
  python godot_analyzer.py /path/to/project --exclude-audio --exclude-fonts
        """
    )
    parser.add_argument('project_path', help='Путь к папке Godot проекта')
    parser.add_argument('--include-textures', action='store_true',
                        help='Включить текстуры в анализ (по умолчанию исключены)')
    parser.add_argument('--exclude-audio', action='store_true',
                        help='Исключить аудио файлы')
    parser.add_argument('--exclude-fonts', action='store_true',
                        help='Исключить шрифты')

    args = parser.parse_args()

    try:
        analyzer = GodotDependencyAnalyzer(
            args.project_path,
            exclude_textures=not args.include_textures,
            exclude_audio=args.exclude_audio,
            exclude_fonts=args.exclude_fonts
        )
        resources, deps = analyzer.analyze()
        stats = analyzer.get_statistics()

        print(f"\n{'='*50}")
        print(f"Проект: {stats['project_name']}")
        print(f"{'='*50}")

        # Показываем активные фильтры
        filters = []
        if stats['filters']['exclude_textures']:
            filters.append('текстуры')
        if stats['filters']['exclude_audio']:
            filters.append('аудио')
        if stats['filters']['exclude_fonts']:
            filters.append('шрифты')
        if filters:
            print(f"Исключены: {', '.join(filters)}")

        print(f"\nВсего ресурсов: {stats['total_resources']}")
        print(f"Всего зависимостей: {stats['total_dependencies']}")

        print(f"\nПо типам ресурсов:")
        for type_name, count in sorted(stats['by_type'].items()):
            print(f"  {type_name}: {count}")

        if stats['autoloads']:
            print(f"\nAutoload синглтоны: {', '.join(stats['autoloads'])}")

        print(f"\nТипы зависимостей:")
        for dep_type, count in sorted(stats['dependency_types'].items()):
            print(f"  {dep_type}: {count}")

        # Показываем несколько примеров зависимостей
        print(f"\nПримеры зависимостей (первые 10):")
        for dep in analyzer.dependencies[:10]:
            print(f"  {dep.source} --[{dep.dep_type}]--> {dep.target}")

    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
