#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Система управления зависимостями инфраструктуры.

Dependency Infrastructure Manager - приложение для визуализации
и управления зависимостями между компонентами инфраструктуры.

Поддерживает импорт из:
    - Docker Compose файлов
    - Kubernetes манифестов
    - Godot проектов

Основные возможности:
    - Визуализация графа зависимостей
    - Редактирование объектов и связей
    - Экспорт в PNG
    - Многооконный интерфейс (MDI)
    - Локализация (русский/английский)
    - Выбор алгоритма компоновки графа
"""

import sys
import json
import os
import yaml
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QDialog, QLineEdit, QComboBox,
    QTextEdit, QMessageBox, QFileDialog, QSplitter, QGroupBox,
    QListWidgetItem, QInputDialog, QTabWidget, QMdiArea, QMdiSubWindow,
    QToolBar, QAction, QMenu, QColorDialog, QFormLayout, QDialogButtonBox,
    QCheckBox, QGridLayout
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QPoint
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QCursor, QFontDatabase

import networkx as nx
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle, RegularPolygon, FancyBboxPatch
import matplotlib.patches as mpatches
import numpy as np

# Настройка matplotlib для корректного отображения шрифтов
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False


# =============================================================================
# СИСТЕМА ЛОКАЛИЗАЦИИ
# =============================================================================

TRANSLATIONS = {
    'ru': {
        # Главное окно
        'app_title': 'Менеджер зависимостей инфраструктуры',
        'ready': 'Готов к работе',
        'new_project_created': 'Создан новый проект',
        'loaded': 'Загружен',
        'saved': 'Сохранено',

        # Меню
        'menu_file': 'Файл',
        'menu_new': 'Новый проект',
        'menu_open': 'Открыть',
        'menu_import': 'Импорт',
        'menu_docker': 'Docker Compose',
        'menu_k8s': 'Kubernetes',
        'menu_godot': 'Godot Project',
        'import_godot_prefix': 'Godot:',
        'select_godot_folder': 'Выберите папку Godot проекта',
        'godot_import_stats': 'Статистика импорта Godot',
        'godot_import_options': 'Опции импорта Godot',
        'exclude_textures': 'Исключить текстуры',
        'exclude_audio': 'Исключить аудио',
        'exclude_fonts': 'Исключить шрифты',
        'menu_save': 'Сохранить',
        'menu_save_as': 'Сохранить как...',
        'menu_exit': 'Выход',
        'menu_windows': 'Окна',
        'menu_cascade': 'Каскадом',
        'menu_tile': 'Плиткой',
        'menu_language': 'Язык',
        'menu_russian': 'Русский',
        'menu_english': 'English',

        # Окно проекта
        'project': 'Проект',
        'new_project': 'Новый проект',
        'objects_title': 'Объекты инфраструктуры:',
        'relationships_title': 'Связи:',
        'visualization_title': 'Визуализация зависимостей:',
        'navigation': 'Навигация:',

        # Кнопки
        'btn_add': 'Добавить',
        'btn_edit': 'Изменить',
        'btn_remove': 'Удалить',
        'btn_view': 'Просмотр',
        'btn_refresh': 'Обновить',
        'btn_zoom_in': 'Увеличить',
        'btn_zoom_out': 'Уменьшить',
        'btn_pan': 'Перемещение',
        'btn_reset_zoom': 'Сбросить зум',
        'btn_color': 'Цветовая схема',
        'btn_export': 'Экспорт PNG',
        'btn_layout': 'Компоновка',

        # Вкладки
        'tab_objects': 'Объекты',
        'tab_relationships': 'Связи',

        # Диалоги объектов
        'dialog_add_object': 'Добавить объект',
        'dialog_edit_object': 'Редактировать объект',
        'object_id': 'ID объекта:',
        'object_type': 'Тип объекта:',
        'object_name': 'Название:',
        'object_description': 'Описание (опционально):',
        'placeholder_id': 'Уникальный идентификатор',
        'placeholder_name': 'Понятное имя объекта',
        'placeholder_desc': 'Дополнительная информация',

        # Диалоги связей
        'dialog_add_relationship': 'Добавить связь',
        'dialog_edit_relationship': 'Редактировать связь',
        'rel_source': 'Исходный объект:',
        'rel_type': 'Тип связи:',
        'rel_target': 'Целевой объект:',
        'rel_description': 'Описание (опционально):',

        # Кнопки диалогов
        'btn_save': 'Сохранить',
        'btn_cancel': 'Отмена',
        'btn_import': 'Импортировать',

        # Типы объектов
        'type_file': 'ФАЙЛ',
        'type_container': 'КОНТЕЙНЕР',
        'type_router': 'РОУТЕР',
        'type_switch': 'СВИТЧ',
        'type_server': 'СЕРВЕР',
        'type_database': 'БД',
        'type_godot_scene': 'СЦЕНА',
        'type_godot_script': 'СКРИПТ',
        'type_godot_resource': 'РЕСУРС',
        'type_godot_autoload': 'AUTOLOAD',

        # Информация об объекте
        'info_object': 'Информация об объекте',
        'info_id': 'ID:',
        'info_type': 'Тип:',
        'info_name': 'Название:',
        'info_created': 'Создан:',
        'info_properties': 'Свойства:',
        'info_depends_on': 'Зависит от',
        'info_dependents': 'От него зависят',

        # Информация о связи
        'info_relationship': 'Информация о связи',
        'info_source_obj': 'Исходный объект:',
        'info_rel_type': 'Тип связи:',
        'info_target_obj': 'Целевой объект:',
        'info_created_at': 'Создана:',
        'info_description': 'Описание:',

        # Сообщения
        'error': 'Ошибка',
        'success': 'Успех',
        'confirm': 'Подтверждение',
        'warning': 'Предупреждение',
        'select_object': 'Выберите объект',
        'select_relationship': 'Выберите связь',
        'need_2_objects': 'Нужно минимум 2 объекта',
        'confirm_delete_obj': 'Удалить',
        'confirm_delete_rel': 'Удалить связь?',
        'same_object_error': 'Исходный и целевой объект не могут совпадать',
        'no_objects': 'Нет объектов для отображения',
        'graph_title': 'Граф зависимостей',

        # Импорт
        'import_complete': 'Импорт завершён',
        'imported_objects': 'Объектов:',
        'imported_rels': 'Связей:',
        'import_error': 'Не удалось импортировать данные',
        'import_prefix': 'Импорт:',
        'import_k8s_prefix': 'Импорт K8s:',

        # Экспорт
        'export_success': 'Граф экспортирован в:',
        'export_error': 'Не удалось экспортировать граф',
        'export_dialog': 'Экспорт в PNG',

        # Файловые диалоги
        'open_project': 'Открыть проект',
        'save_project': 'Сохранить проект',
        'save_error': 'Не удалось сохранить',
        'load_error': 'Не удалось загрузить файл',

        # Несохранённые изменения
        'unsaved_title': 'Несохранённые изменения',
        'unsaved_text': 'был изменён.',
        'unsaved_question': 'Хотите сохранить изменения?',
        'btn_save_changes': 'Сохранить',
        'btn_dont_save': 'Не сохранять',

        # Подсказки
        'hint_controls': 'Колесо мыши - зум | Shift+ЛКМ / СКМ - перемещение | ЛКМ - выбор узла',
        'hint_zoom_in': 'Приблизить',
        'hint_zoom_out': 'Отдалить',
        'hint_pan': 'Режим перемещения',

        # Цветовые схемы
        'scheme_dialog': 'Цветовая схема',
        'scheme_select': 'Выберите схему:',

        # Компоновка графа
        'layout_dialog': 'Компоновка графа',
        'layout_select': 'Выберите алгоритм:',
        'layout_spring': 'Пружинная (Spring)',
        'layout_circular': 'Круговая (Circular)',
        'layout_kamada': 'Kamada-Kawai',
        'layout_spectral': 'Спектральная (Spectral)',
        'layout_shell': 'Оболочка (Shell)',
        'layout_hierarchical': 'Иерархическая',
    },
    'en': {
        # Main window
        'app_title': 'Infrastructure Dependency Manager',
        'ready': 'Ready',
        'new_project_created': 'New project created',
        'loaded': 'Loaded',
        'saved': 'Saved',

        # Menu
        'menu_file': 'File',
        'menu_new': 'New Project',
        'menu_open': 'Open',
        'menu_import': 'Import',
        'menu_docker': 'Docker Compose',
        'menu_k8s': 'Kubernetes',
        'menu_godot': 'Godot Project',
        'import_godot_prefix': 'Godot:',
        'select_godot_folder': 'Select Godot project folder',
        'godot_import_stats': 'Godot Import Statistics',
        'godot_import_options': 'Godot Import Options',
        'exclude_textures': 'Exclude textures',
        'exclude_audio': 'Exclude audio',
        'exclude_fonts': 'Exclude fonts',
        'menu_save': 'Save',
        'menu_save_as': 'Save As...',
        'menu_exit': 'Exit',
        'menu_windows': 'Windows',
        'menu_cascade': 'Cascade',
        'menu_tile': 'Tile',
        'menu_language': 'Language',
        'menu_russian': 'Русский',
        'menu_english': 'English',

        # Project window
        'project': 'Project',
        'new_project': 'New Project',
        'objects_title': 'Infrastructure Objects:',
        'relationships_title': 'Relationships:',
        'visualization_title': 'Dependencies Visualization:',
        'navigation': 'Navigation:',

        # Buttons
        'btn_add': 'Add',
        'btn_edit': 'Edit',
        'btn_remove': 'Remove',
        'btn_view': 'View',
        'btn_refresh': 'Refresh',
        'btn_zoom_in': 'Zoom In',
        'btn_zoom_out': 'Zoom Out',
        'btn_pan': 'Pan',
        'btn_reset_zoom': 'Reset Zoom',
        'btn_color': 'Color Scheme',
        'btn_export': 'Export PNG',
        'btn_layout': 'Layout',

        # Tabs
        'tab_objects': 'Objects',
        'tab_relationships': 'Relationships',

        # Object dialogs
        'dialog_add_object': 'Add Object',
        'dialog_edit_object': 'Edit Object',
        'object_id': 'Object ID:',
        'object_type': 'Object Type:',
        'object_name': 'Name:',
        'object_description': 'Description (optional):',
        'placeholder_id': 'Unique identifier',
        'placeholder_name': 'Readable object name',
        'placeholder_desc': 'Additional information',

        # Relationship dialogs
        'dialog_add_relationship': 'Add Relationship',
        'dialog_edit_relationship': 'Edit Relationship',
        'rel_source': 'Source Object:',
        'rel_type': 'Relationship Type:',
        'rel_target': 'Target Object:',
        'rel_description': 'Description (optional):',

        # Dialog buttons
        'btn_save': 'Save',
        'btn_cancel': 'Cancel',
        'btn_import': 'Import',

        # Object types
        'type_file': 'FILE',
        'type_container': 'CONTAINER',
        'type_router': 'ROUTER',
        'type_switch': 'SWITCH',
        'type_server': 'SERVER',
        'type_database': 'DATABASE',
        'type_godot_scene': 'SCENE',
        'type_godot_script': 'SCRIPT',
        'type_godot_resource': 'RESOURCE',
        'type_godot_autoload': 'AUTOLOAD',

        # Object info
        'info_object': 'Object Information',
        'info_id': 'ID:',
        'info_type': 'Type:',
        'info_name': 'Name:',
        'info_created': 'Created:',
        'info_properties': 'Properties:',
        'info_depends_on': 'Depends on',
        'info_dependents': 'Dependents',

        # Relationship info
        'info_relationship': 'Relationship Information',
        'info_source_obj': 'Source Object:',
        'info_rel_type': 'Relationship Type:',
        'info_target_obj': 'Target Object:',
        'info_created_at': 'Created:',
        'info_description': 'Description:',

        # Messages
        'error': 'Error',
        'success': 'Success',
        'confirm': 'Confirmation',
        'warning': 'Warning',
        'select_object': 'Select an object',
        'select_relationship': 'Select a relationship',
        'need_2_objects': 'Need at least 2 objects',
        'confirm_delete_obj': 'Delete',
        'confirm_delete_rel': 'Delete relationship?',
        'same_object_error': 'Source and target objects cannot be the same',
        'no_objects': 'No objects to display',
        'graph_title': 'Dependencies Graph',

        # Import
        'import_complete': 'Import Complete',
        'imported_objects': 'Objects:',
        'imported_rels': 'Relationships:',
        'import_error': 'Failed to import data',
        'import_prefix': 'Import:',
        'import_k8s_prefix': 'K8s Import:',

        # Export
        'export_success': 'Graph exported to:',
        'export_error': 'Failed to export graph',
        'export_dialog': 'Export to PNG',

        # File dialogs
        'open_project': 'Open Project',
        'save_project': 'Save Project',
        'save_error': 'Failed to save',
        'load_error': 'Failed to load file',

        # Unsaved changes
        'unsaved_title': 'Unsaved Changes',
        'unsaved_text': 'has been modified.',
        'unsaved_question': 'Do you want to save changes?',
        'btn_save_changes': 'Save',
        'btn_dont_save': "Don't Save",

        # Hints
        'hint_controls': 'Mouse wheel - zoom | Shift+LMB / MMB - pan | LMB - select node',
        'hint_zoom_in': 'Zoom In',
        'hint_zoom_out': 'Zoom Out',
        'hint_pan': 'Pan Mode',

        # Color schemes
        'scheme_dialog': 'Color Scheme',
        'scheme_select': 'Select scheme:',

        # Graph layout
        'layout_dialog': 'Graph Layout',
        'layout_select': 'Select algorithm:',
        'layout_spring': 'Spring',
        'layout_circular': 'Circular',
        'layout_kamada': 'Kamada-Kawai',
        'layout_spectral': 'Spectral',
        'layout_shell': 'Shell',
        'layout_hierarchical': 'Hierarchical',
    }
}

# Текущий язык интерфейса
CURRENT_LANGUAGE = 'ru'


def tr(key: str) -> str:
    """Получает перевод строки по ключу.

    Args:
        key: Ключ перевода из словаря TRANSLATIONS.

    Returns:
        Переведённая строка на текущем языке или ключ, если перевод не найден.
    """
    return TRANSLATIONS.get(CURRENT_LANGUAGE, {}).get(key, key)


def set_language(lang: str) -> None:
    """Устанавливает текущий язык интерфейса.

    Args:
        lang: Код языка ('ru' или 'en').
    """
    global CURRENT_LANGUAGE
    if lang in TRANSLATIONS:
        CURRENT_LANGUAGE = lang


# =============================================================================
# ЦВЕТОВЫЕ СХЕМЫ И ИКОНКИ
# =============================================================================

COLOR_SCHEMES = {
    'default': {
        'file': '#FF6B9D',
        'docker_container': '#4ECDC4',
        'router': '#95E1D3',
        'switch': '#C77DFF',
        'server': '#FFD93D',
        'database': '#FF8C42',
        'godot_scene': '#2E86AB',
        'godot_script': '#4A7C23',
        'godot_resource': '#D64933',
        'godot_autoload': '#7D3C98',
    },
    'dark': {
        'file': '#E63946',
        'docker_container': '#457B9D',
        'router': '#2A9D8F',
        'switch': '#9B59B6',
        'server': '#F4A261',
        'database': '#E76F51',
        'godot_scene': '#1A5276',
        'godot_script': '#1E5631',
        'godot_resource': '#922B21',
        'godot_autoload': '#5B2C6F',
    },
    'pastel': {
        'file': '#FFB3BA',
        'docker_container': '#BAE1FF',
        'router': '#BAFFC9',
        'switch': '#E0BBE4',
        'server': '#FFFFBA',
        'database': '#FFDFBA',
        'godot_scene': '#7EC8E3',
        'godot_script': '#98D46B',
        'godot_resource': '#FFB088',
        'godot_autoload': '#C19EE0',
    },
    'vibrant': {
        'file': '#FF006E',
        'docker_container': '#00B4D8',
        'router': '#06FFA5',
        'switch': '#9D4EDD',
        'server': '#FFBE0B',
        'database': '#FF5400',
        'godot_scene': '#0077B6',
        'godot_script': '#38B000',
        'godot_resource': '#E63946',
        'godot_autoload': '#6A0DAD',
    }
}

# Unicode-символы для обозначения типов объектов
NODE_ICONS = {
    'file': '■',
    'docker_container': '●',
    'router': '◆',
    'switch': '▲',
    'server': '◼',
    'database': '⬢',
    'godot_scene': '◉',
    'godot_script': '▰',
    'godot_resource': '◈',
    'godot_autoload': '★',
}


def get_node_label(obj_type: str) -> str:
    """Возвращает локализованную метку для типа объекта.

    Args:
        obj_type: Внутренний идентификатор типа объекта.

    Returns:
        Локализованное название типа.
    """
    labels = {
        'file': tr('type_file'),
        'docker_container': tr('type_container'),
        'router': tr('type_router'),
        'switch': tr('type_switch'),
        'server': tr('type_server'),
        'database': tr('type_database'),
        'godot_scene': tr('type_godot_scene'),
        'godot_script': tr('type_godot_script'),
        'godot_resource': tr('type_godot_resource'),
        'godot_autoload': tr('type_godot_autoload'),
    }
    return labels.get(obj_type, obj_type.upper())


# =============================================================================
# КЛАССЫ ДАННЫХ
# =============================================================================

class InfraObject:
    """Объект инфраструктуры.

    Представляет элемент инфраструктуры: файл, контейнер, сервер и т.д.

    Attributes:
        id: Уникальный идентификатор объекта.
        type: Тип объекта (file, docker_container, router, switch, server,
              database, godot_scene, godot_script, godot_resource, godot_autoload).
        name: Человекочитаемое название.
        properties: Дополнительные свойства объекта.
        created_at: Дата и время создания в формате ISO.
    """

    VALID_TYPES = [
        'file', 'docker_container', 'router', 'switch', 'server', 'database',
        'godot_scene', 'godot_script', 'godot_resource', 'godot_autoload'
    ]

    def __init__(self, obj_id: str, obj_type: str, name: str,
                 properties: Dict = None) -> None:
        """Инициализирует объект инфраструктуры.

        Args:
            obj_id: Уникальный идентификатор.
            obj_type: Тип объекта из VALID_TYPES.
            name: Название объекта.
            properties: Словарь дополнительных свойств.

        Raises:
            ValueError: Если тип объекта недопустим.
        """
        if obj_type not in self.VALID_TYPES:
            raise ValueError(f"Недопустимый тип объекта: {obj_type}")

        self.id = self._sanitize_id(obj_id)
        self.type = obj_type
        self.name = self._sanitize_string(name)
        self.properties = properties or {}
        self.created_at = datetime.now().isoformat()

    @staticmethod
    def _sanitize_string(text: str, max_length: int = 500) -> str:
        """Очищает строку от опасных символов.

        Args:
            text: Исходная строка.
            max_length: Максимальная длина результата.

        Returns:
            Очищенная строка.
        """
        if not isinstance(text, str):
            return str(text)
        text = text[:max_length]
        dangerous_chars = ['<', '>', '"', "'", '`', '\x00']
        for char in dangerous_chars:
            text = text.replace(char, '')
        return text.strip()

    @staticmethod
    def _sanitize_id(obj_id: str) -> str:
        """Очищает идентификатор от недопустимых символов.

        Args:
            obj_id: Исходный идентификатор.

        Returns:
            Очищенный идентификатор (только буквы, цифры, дефис и подчёркивание).
        """
        obj_id = str(obj_id)
        return ''.join(c for c in obj_id if c.isalnum() or c in ['-', '_'])[:100]

    def to_dict(self) -> Dict:
        """Сериализует объект в словарь.

        Returns:
            Словарь с данными объекта для сохранения в JSON.
        """
        return {
            'id': self.id,
            'type': self.type,
            'name': self.name,
            'properties': self.properties,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'InfraObject':
        """Создаёт объект из словаря.

        Args:
            data: Словарь с данными объекта.

        Returns:
            Новый экземпляр InfraObject.
        """
        obj = cls(
            obj_id=data['id'],
            obj_type=data['type'],
            name=data['name'],
            properties=data.get('properties', {})
        )
        obj.created_at = data.get('created_at', datetime.now().isoformat())
        return obj

    def __str__(self) -> str:
        """Возвращает строковое представление объекта."""
        return f"[{self.type}] {self.name} (ID: {self.id})"


class Relationship:
    """Связь между объектами инфраструктуры.

    Представляет направленную связь от одного объекта к другому.

    Attributes:
        source_id: ID исходного объекта.
        target_id: ID целевого объекта.
        type: Тип связи.
        description: Описание связи.
        created_at: Дата и время создания в формате ISO.
    """

    VALID_TYPES = [
        'calls', 'sends_to', 'depends_on', 'connects_to',
        'uses', 'provides', 'routes_through'
    ]

    def __init__(self, source_id: str, target_id: str, rel_type: str,
                 description: str = "") -> None:
        """Инициализирует связь между объектами.

        Args:
            source_id: ID исходного объекта.
            target_id: ID целевого объекта.
            rel_type: Тип связи из VALID_TYPES.
            description: Описание связи.

        Raises:
            ValueError: Если тип связи недопустим.
        """
        if rel_type not in self.VALID_TYPES:
            raise ValueError(f"Недопустимый тип связи: {rel_type}")

        self.source_id = InfraObject._sanitize_id(source_id)
        self.target_id = InfraObject._sanitize_id(target_id)
        self.type = rel_type
        self.description = InfraObject._sanitize_string(description)
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Сериализует связь в словарь.

        Returns:
            Словарь с данными связи для сохранения в JSON.
        """
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'type': self.type,
            'description': self.description,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Relationship':
        """Создаёт связь из словаря.

        Args:
            data: Словарь с данными связи.

        Returns:
            Новый экземпляр Relationship.
        """
        rel = cls(
            source_id=data['source_id'],
            target_id=data['target_id'],
            rel_type=data['type'],
            description=data.get('description', '')
        )
        rel.created_at = data.get('created_at', datetime.now().isoformat())
        return rel

    def __str__(self) -> str:
        """Возвращает строковое представление связи."""
        return f"{self.source_id} --[{self.type}]--> {self.target_id}"


# =============================================================================
# МЕНЕДЖЕР ЗАВИСИМОСТЕЙ
# =============================================================================

class DependencyManager:
    """Менеджер зависимостей инфраструктуры.

    Центральный класс для управления объектами и связями.
    Использует NetworkX для построения и анализа графа зависимостей.

    Attributes:
        objects: Словарь объектов {id: InfraObject}.
        relationships: Список связей между объектами.
        graph: Направленный граф NetworkX.
    """

    def __init__(self) -> None:
        """Инициализирует пустой менеджер зависимостей."""
        self.objects: Dict[str, InfraObject] = {}
        self.relationships: List[Relationship] = []
        self.graph = nx.DiGraph()

    def add_object(self, obj: InfraObject) -> bool:
        """Добавляет объект в менеджер.

        Args:
            obj: Объект для добавления.

        Returns:
            True если объект добавлен, False если ID уже существует.
        """
        if obj.id in self.objects:
            return False
        self.objects[obj.id] = obj
        self.graph.add_node(obj.id, **obj.to_dict())
        return True

    def update_object(self, obj_id: str, obj: InfraObject) -> bool:
        """Обновляет существующий объект.

        При изменении ID обновляются все связанные связи.

        Args:
            obj_id: Текущий ID объекта.
            obj: Новые данные объекта.

        Returns:
            True если объект обновлён, False если исходный ID не найден.
        """
        if obj_id not in self.objects:
            return False

        # Удаляем старый объект
        del self.objects[obj_id]
        if self.graph.has_node(obj_id):
            self.graph.remove_node(obj_id)

        # Обновляем связи при изменении ID
        for rel in self.relationships:
            if rel.source_id == obj_id:
                rel.source_id = obj.id
            if rel.target_id == obj_id:
                rel.target_id = obj.id

        # Добавляем обновлённый объект
        self.objects[obj.id] = obj
        self.graph.add_node(obj.id, **obj.to_dict())

        # Перестраиваем рёбра графа
        for rel in self.relationships:
            if rel.source_id == obj.id or rel.target_id == obj.id:
                if self.graph.has_edge(rel.source_id, rel.target_id):
                    self.graph.remove_edge(rel.source_id, rel.target_id)
                self.graph.add_edge(rel.source_id, rel.target_id, **rel.to_dict())

        return True

    def remove_object(self, obj_id: str) -> bool:
        """Удаляет объект и все связанные с ним связи.

        Args:
            obj_id: ID удаляемого объекта.

        Returns:
            True если объект удалён, False если ID не найден.
        """
        if obj_id not in self.objects:
            return False

        # Удаляем связи, связанные с объектом
        self.relationships = [
            rel for rel in self.relationships
            if rel.source_id != obj_id and rel.target_id != obj_id
        ]

        # Удаляем объект
        del self.objects[obj_id]
        if self.graph.has_node(obj_id):
            self.graph.remove_node(obj_id)
        return True

    def add_relationship(self, rel: Relationship) -> bool:
        """Добавляет связь между объектами.

        Args:
            rel: Связь для добавления.

        Returns:
            True если связь добавлена, False если объекты не существуют
            или такая связь уже есть.
        """
        # Проверяем существование обоих объектов
        if rel.source_id not in self.objects or rel.target_id not in self.objects:
            return False

        # Проверяем на дубликат
        for existing_rel in self.relationships:
            if (existing_rel.source_id == rel.source_id and
                existing_rel.target_id == rel.target_id and
                existing_rel.type == rel.type):
                return False

        self.relationships.append(rel)
        self.graph.add_edge(rel.source_id, rel.target_id, **rel.to_dict())
        return True

    def update_relationship(self, old_rel: Tuple[str, str, str],
                           new_rel: Relationship) -> bool:
        """Обновляет существующую связь.

        Args:
            old_rel: Кортеж (source_id, target_id, type) старой связи.
            new_rel: Новые данные связи.

        Returns:
            True если связь обновлена.
        """
        source_id, target_id, rel_type = old_rel

        # Удаляем старую связь
        for i, rel in enumerate(self.relationships):
            if (rel.source_id == source_id and
                rel.target_id == target_id and
                rel.type == rel_type):
                del self.relationships[i]
                if self.graph.has_edge(source_id, target_id):
                    self.graph.remove_edge(source_id, target_id)
                break

        return self.add_relationship(new_rel)

    def remove_relationship(self, source_id: str, target_id: str,
                           rel_type: str) -> bool:
        """Удаляет связь между объектами.

        Args:
            source_id: ID исходного объекта.
            target_id: ID целевого объекта.
            rel_type: Тип связи.

        Returns:
            True если связь удалена, False если не найдена.
        """
        for i, rel in enumerate(self.relationships):
            if (rel.source_id == source_id and
                rel.target_id == target_id and
                rel.type == rel_type):
                del self.relationships[i]
                if self.graph.has_edge(source_id, target_id):
                    self.graph.remove_edge(source_id, target_id)
                return True
        return False

    def get_dependencies(self, obj_id: str) -> List[str]:
        """Возвращает список объектов, от которых зависит данный объект.

        Args:
            obj_id: ID объекта.

        Returns:
            Список ID объектов-зависимостей.
        """
        if obj_id not in self.objects:
            return []
        return [rel.target_id for rel in self.relationships if rel.source_id == obj_id]

    def get_dependents(self, obj_id: str) -> List[str]:
        """Возвращает список объектов, которые зависят от данного.

        Args:
            obj_id: ID объекта.

        Returns:
            Список ID зависимых объектов.
        """
        if obj_id not in self.objects:
            return []
        return [rel.source_id for rel in self.relationships if rel.target_id == obj_id]

    def import_from_docker_compose(self, filename: str) -> Tuple[int, int]:
        """Импортирует данные из файла Docker Compose.

        Создаёт объекты для сервисов, томов и сетей.
        Автоматически создаёт связи depends_on и uses.

        Args:
            filename: Путь к файлу docker-compose.yml.

        Returns:
            Кортеж (количество объектов, количество связей).
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                compose = yaml.safe_load(f)

            services = compose.get('services', {})
            networks = compose.get('networks', {})
            volumes = compose.get('volumes', {})

            added_objects = 0
            added_relationships = 0

            # Создаём объекты для сервисов
            for service_name, service_config in services.items():
                obj_id = f"docker_{service_name}"
                properties = {
                    'image': service_config.get('image', 'N/A'),
                    'ports': str(service_config.get('ports', [])),
                    'environment': str(service_config.get('environment', {}))
                }

                obj = InfraObject(obj_id, 'docker_container', service_name, properties)
                if self.add_object(obj):
                    added_objects += 1

                # Обрабатываем depends_on
                depends_on = service_config.get('depends_on', [])
                if isinstance(depends_on, dict):
                    depends_on = list(depends_on.keys())

                for dep in depends_on:
                    dep_id = f"docker_{dep}"
                    rel = Relationship(obj_id, dep_id, 'depends_on', 'Docker Compose dependency')
                    if self.add_relationship(rel):
                        added_relationships += 1

                # Обрабатываем тома
                service_volumes = service_config.get('volumes', [])
                for vol in service_volumes:
                    if isinstance(vol, str) and ':' in vol:
                        vol_name = vol.split(':')[0]
                        if vol_name in volumes:
                            vol_id = f"vol_{vol_name}"
                            if vol_id not in self.objects:
                                vol_obj = InfraObject(
                                    vol_id, 'database', f"Том: {vol_name}",
                                    {'type': 'volume'}
                                )
                                if self.add_object(vol_obj):
                                    added_objects += 1

                            rel = Relationship(obj_id, vol_id, 'uses', 'Uses volume')
                            if self.add_relationship(rel):
                                added_relationships += 1

            # Создаём объект для сети если есть
            for network_name in networks.keys():
                net_id = f"net_{network_name}"
                if net_id not in self.objects:
                    net_obj = InfraObject(
                        net_id, 'router', f"Сеть: {network_name}",
                        {'type': 'network'}
                    )
                    if self.add_object(net_obj):
                        added_objects += 1

            return added_objects, added_relationships

        except Exception as e:
            print(f"Ошибка импорта Docker Compose: {e}")
            return 0, 0

    def import_from_kubernetes(self, filename: str) -> Tuple[int, int]:
        """Импортирует данные из Kubernetes манифеста.

        Поддерживает Deployment, Service, PersistentVolumeClaim.

        Args:
            filename: Путь к YAML-файлу с манифестом.

        Returns:
            Кортеж (количество объектов, количество связей).
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                docs = list(yaml.safe_load_all(f))

            added_objects = 0
            added_relationships = 0

            for doc in docs:
                if not doc or 'kind' not in doc:
                    continue

                kind = doc['kind']
                metadata = doc.get('metadata', {})
                name = metadata.get('name', 'unnamed')

                if kind == 'Deployment':
                    spec = doc.get('spec', {})
                    template = spec.get('template', {})
                    containers = template.get('spec', {}).get('containers', [])

                    for container in containers:
                        container_name = container.get('name', 'container')
                        obj_id = f"k8s_{name}_{container_name}"

                        properties = {
                            'image': container.get('image', 'N/A'),
                            'kind': 'Deployment',
                            'namespace': metadata.get('namespace', 'default')
                        }

                        obj = InfraObject(
                            obj_id, 'docker_container',
                            f"{name}/{container_name}", properties
                        )
                        if self.add_object(obj):
                            added_objects += 1

                elif kind == 'Service':
                    obj_id = f"k8s_svc_{name}"
                    spec = doc.get('spec', {})

                    properties = {
                        'type': spec.get('type', 'ClusterIP'),
                        'ports': str(spec.get('ports', [])),
                        'kind': 'Service'
                    }

                    obj = InfraObject(obj_id, 'server', f"Service: {name}", properties)
                    if self.add_object(obj):
                        added_objects += 1

                    # Связываем с подами по селектору
                    selector = spec.get('selector', {})
                    if 'app' in selector:
                        app_name = selector['app']
                        for obj_key in self.objects.keys():
                            if app_name in obj_key and 'k8s_' in obj_key and obj_key != obj_id:
                                rel = Relationship(
                                    obj_id, obj_key, 'routes_through',
                                    'K8s Service routes to Pod'
                                )
                                if self.add_relationship(rel):
                                    added_relationships += 1

                elif kind == 'PersistentVolumeClaim':
                    obj_id = f"k8s_pvc_{name}"
                    spec = doc.get('spec', {})

                    properties = {
                        'storage': str(spec.get('resources', {}).get('requests', {}).get('storage', 'N/A')),
                        'kind': 'PersistentVolumeClaim'
                    }

                    obj = InfraObject(obj_id, 'database', f"PVC: {name}", properties)
                    if self.add_object(obj):
                        added_objects += 1

            return added_objects, added_relationships

        except Exception as e:
            print(f"Ошибка импорта Kubernetes: {e}")
            return 0, 0

    def save_to_file(self, filename: str) -> bool:
        """Сохраняет проект в JSON-файл.

        Args:
            filename: Путь к файлу для сохранения.

        Returns:
            True если сохранение успешно, False при ошибке.
        """
        try:
            if not filename.endswith('.json'):
                filename += '.json'

            data = {
                'objects': [obj.to_dict() for obj in self.objects.values()],
                'relationships': [rel.to_dict() for rel in self.relationships],
                'metadata': {
                    'version': '2.0',
                    'saved_at': datetime.now().isoformat()
                }
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False

    def load_from_file(self, filename: str) -> bool:
        """Загружает проект из JSON-файла.

        Args:
            filename: Путь к файлу проекта.

        Returns:
            True если загрузка успешна, False при ошибке.
        """
        try:
            if not os.path.exists(filename):
                return False

            # Ограничение размера файла (10 МБ)
            if os.path.getsize(filename) > 10 * 1024 * 1024:
                raise ValueError("Файл слишком большой")

            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Очищаем текущие данные
            self.objects.clear()
            self.relationships.clear()
            self.graph.clear()

            # Загружаем объекты
            for obj_data in data.get('objects', []):
                obj = InfraObject.from_dict(obj_data)
                self.add_object(obj)

            # Загружаем связи
            for rel_data in data.get('relationships', []):
                rel = Relationship.from_dict(rel_data)
                self.add_relationship(rel)

            return True
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return False


# =============================================================================
# ДИАЛОГОВЫЕ ОКНА
# =============================================================================

class GodotImportDialog(QDialog):
    """Диалог настройки импорта Godot проекта.

    Позволяет выбрать, какие типы ресурсов исключить из импорта.

    Attributes:
        exclude_textures: Флаг исключения текстур.
        exclude_audio: Флаг исключения аудио.
        exclude_fonts: Флаг исключения шрифтов.
    """

    def __init__(self, parent=None) -> None:
        """Инициализирует диалог импорта Godot.

        Args:
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self.setWindowTitle(tr('godot_import_options'))
        self.setMinimumWidth(350)
        self.setup_ui()
        self.apply_styles()

    def apply_styles(self) -> None:
        """Применяет стили к элементам диалога."""
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QCheckBox {
                color: #212529;
                font-size: 11pt;
                padding: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #DEE2E6;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #007BFF;
                border-radius: 4px;
                background-color: #007BFF;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 10pt;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton[text="Отмена"], QPushButton[text="Cancel"] {
                background-color: #6C757D;
            }
            QPushButton[text="Отмена"]:hover, QPushButton[text="Cancel"]:hover {
                background-color: #5a6268;
            }
        """)

    def setup_ui(self) -> None:
        """Настраивает элементы интерфейса диалога."""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Заголовок
        title_label = QLabel(f"<b>{tr('godot_import_options')}</b>")
        title_label.setStyleSheet("font-size: 12pt; color: #212529; padding: 10px;")
        layout.addWidget(title_label)

        # Чекбоксы фильтрации
        self.textures_cb = QCheckBox(tr('exclude_textures'))
        self.textures_cb.setChecked(True)
        layout.addWidget(self.textures_cb)

        self.audio_cb = QCheckBox(tr('exclude_audio'))
        self.audio_cb.setChecked(False)
        layout.addWidget(self.audio_cb)

        self.fonts_cb = QCheckBox(tr('exclude_fonts'))
        self.fonts_cb.setChecked(False)
        layout.addWidget(self.fonts_cb)

        layout.addSpacing(10)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.import_btn = QPushButton(tr('btn_import'))
        self.cancel_btn = QPushButton(tr('btn_cancel'))

        self.import_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_options(self) -> Dict[str, bool]:
        """Возвращает выбранные опции фильтрации.

        Returns:
            Словарь с флагами исключения типов ресурсов.
        """
        return {
            'exclude_textures': self.textures_cb.isChecked(),
            'exclude_audio': self.audio_cb.isChecked(),
            'exclude_fonts': self.fonts_cb.isChecked()
        }


class LayoutDialog(QDialog):
    """Диалог выбора алгоритма компоновки графа.

    Позволяет выбрать алгоритм расположения узлов на графе.

    Attributes:
        selected_layout: Выбранный алгоритм компоновки.
    """

    LAYOUTS = {
        'spring': 'layout_spring',
        'circular': 'layout_circular',
        'kamada_kawai': 'layout_kamada',
        'spectral': 'layout_spectral',
        'shell': 'layout_shell',
        'hierarchical': 'layout_hierarchical',
    }

    def __init__(self, parent=None, current_layout: str = 'spring') -> None:
        """Инициализирует диалог выбора компоновки.

        Args:
            parent: Родительский виджет.
            current_layout: Текущий выбранный алгоритм.
        """
        super().__init__(parent)
        self.selected_layout = current_layout
        self.setWindowTitle(tr('layout_dialog'))
        self.setMinimumWidth(300)
        self.setup_ui()
        self.apply_styles()

    def apply_styles(self) -> None:
        """Применяет стили к элементам диалога."""
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #212529;
                font-size: 11pt;
                padding: 5px;
            }
            QListWidget {
                border: 2px solid #DEE2E6;
                border-radius: 6px;
                background-color: #F8F9FA;
                padding: 5px;
                font-size: 11pt;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 4px;
                margin: 2px;
                color: #212529;
            }
            QListWidget::item:selected {
                background-color: #007BFF;
                color: white;
            }
            QListWidget::item:hover:!selected {
                background-color: #E9ECEF;
            }
            QListWidget::item:selected:hover {
                background-color: #0056b3;
                color: white;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 10pt;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)

    def setup_ui(self) -> None:
        """Настраивает элементы интерфейса диалога."""
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Заголовок
        label = QLabel(tr('layout_select'))
        layout.addWidget(label)

        # Список алгоритмов
        self.layout_list = QListWidget()
        for layout_key, label_key in self.LAYOUTS.items():
            item = QListWidgetItem(tr(label_key))
            item.setData(Qt.UserRole, layout_key)
            self.layout_list.addItem(item)
            if layout_key == self.selected_layout:
                self.layout_list.setCurrentItem(item)

        self.layout_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.layout_list)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton(tr('btn_cancel'))

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_layout(self) -> str:
        """Возвращает выбранный алгоритм компоновки.

        Returns:
            Строка-идентификатор алгоритма.
        """
        current_item = self.layout_list.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return 'spring'


class ObjectDialog(QDialog):
    """Диалог создания и редактирования объекта.

    Позволяет задать ID, тип, название и описание объекта.

    Attributes:
        edit_obj: Редактируемый объект или None для создания нового.
    """

    def __init__(self, parent=None, edit_obj: InfraObject = None) -> None:
        """Инициализирует диалог объекта.

        Args:
            parent: Родительский виджет.
            edit_obj: Объект для редактирования или None для создания.
        """
        super().__init__(parent)
        self.edit_obj = edit_obj
        self.setWindowTitle(tr('dialog_edit_object') if edit_obj else tr('dialog_add_object'))
        self.setMinimumWidth(400)
        self.setup_ui()
        self.apply_styles()

    def apply_styles(self) -> None:
        """Применяет стили к элементам диалога."""
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #212529;
                font-size: 10pt;
            }
            QLineEdit, QTextEdit, QComboBox {
                border: 2px solid #DEE2E6;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
                font-size: 10pt;
                color: #212529;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #007BFF;
            }
            QComboBox {
                padding-right: 20px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #DEE2E6;
                border-radius: 6px;
                selection-background-color: #007BFF;
                selection-color: white;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)

    def setup_ui(self) -> None:
        """Настраивает элементы интерфейса диалога."""
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Поле ID
        layout.addWidget(QLabel(tr('object_id')))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText(tr('placeholder_id'))
        if self.edit_obj:
            self.id_input.setText(self.edit_obj.id)
        layout.addWidget(self.id_input)

        # Выбор типа
        layout.addWidget(QLabel(tr('object_type')))
        self.type_combo = QComboBox()
        self.type_combo.addItems(InfraObject.VALID_TYPES)
        if self.edit_obj:
            index = self.type_combo.findText(self.edit_obj.type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        layout.addWidget(self.type_combo)

        # Поле названия
        layout.addWidget(QLabel(tr('object_name')))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(tr('placeholder_name'))
        if self.edit_obj:
            self.name_input.setText(self.edit_obj.name)
        layout.addWidget(self.name_input)

        # Поле описания
        layout.addWidget(QLabel(tr('object_description')))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText(tr('placeholder_desc'))
        if self.edit_obj and 'description' in self.edit_obj.properties:
            self.description_input.setPlainText(self.edit_obj.properties['description'])
        layout.addWidget(self.description_input)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = QPushButton(tr('btn_save'))
        self.cancel_button = QPushButton(tr('btn_cancel'))

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_object(self) -> Optional[InfraObject]:
        """Создаёт объект из введённых данных.

        Returns:
            Новый InfraObject или None при ошибке валидации.
        """
        obj_id = self.id_input.text().strip()
        obj_type = self.type_combo.currentText()
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()

        if not obj_id or not name:
            return None

        properties = {}
        if description:
            properties['description'] = description

        # Сохраняем старые свойства при редактировании
        if self.edit_obj:
            for key, value in self.edit_obj.properties.items():
                if key != 'description':
                    properties[key] = value

        try:
            return InfraObject(obj_id, obj_type, name, properties)
        except ValueError as e:
            QMessageBox.warning(self, tr('error'), str(e))
            return None


class RelationshipDialog(QDialog):
    """Диалог создания и редактирования связи.

    Позволяет выбрать исходный и целевой объекты, тип связи и описание.

    Attributes:
        objects: Словарь доступных объектов.
        edit_rel: Редактируемая связь или None для создания новой.
    """

    def __init__(self, objects: Dict[str, InfraObject], parent=None,
                 edit_rel: Relationship = None) -> None:
        """Инициализирует диалог связи.

        Args:
            objects: Словарь объектов для выбора.
            parent: Родительский виджет.
            edit_rel: Связь для редактирования или None.
        """
        super().__init__(parent)
        self.objects = objects
        self.edit_rel = edit_rel
        self.setWindowTitle(tr('dialog_edit_relationship') if edit_rel else tr('dialog_add_relationship'))
        self.setMinimumWidth(400)
        self.setup_ui()
        self.apply_styles()

    def apply_styles(self) -> None:
        """Применяет стили к элементам диалога."""
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #212529;
                font-size: 10pt;
            }
            QComboBox, QTextEdit {
                border: 2px solid #DEE2E6;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
                font-size: 10pt;
                color: #212529;
            }
            QComboBox:focus, QTextEdit:focus {
                border-color: #007BFF;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 2px solid #DEE2E6;
                border-radius: 6px;
                selection-background-color: #007BFF;
                selection-color: white;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)

    def setup_ui(self) -> None:
        """Настраивает элементы интерфейса диалога."""
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Выбор исходного объекта
        layout.addWidget(QLabel(tr('rel_source')))
        self.source_combo = QComboBox()
        for obj in self.objects.values():
            self.source_combo.addItem(f"{obj.name} ({obj.id})", obj.id)
        if self.edit_rel:
            index = self.source_combo.findData(self.edit_rel.source_id)
            if index >= 0:
                self.source_combo.setCurrentIndex(index)
        layout.addWidget(self.source_combo)

        # Выбор типа связи
        layout.addWidget(QLabel(tr('rel_type')))
        self.type_combo = QComboBox()
        self.type_combo.addItems(Relationship.VALID_TYPES)
        if self.edit_rel:
            index = self.type_combo.findText(self.edit_rel.type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        layout.addWidget(self.type_combo)

        # Выбор целевого объекта
        layout.addWidget(QLabel(tr('rel_target')))
        self.target_combo = QComboBox()
        for obj in self.objects.values():
            self.target_combo.addItem(f"{obj.name} ({obj.id})", obj.id)
        if self.edit_rel:
            index = self.target_combo.findData(self.edit_rel.target_id)
            if index >= 0:
                self.target_combo.setCurrentIndex(index)
        layout.addWidget(self.target_combo)

        # Поле описания
        layout.addWidget(QLabel(tr('rel_description')))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(60)
        if self.edit_rel:
            self.description_input.setPlainText(self.edit_rel.description)
        layout.addWidget(self.description_input)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = QPushButton(tr('btn_save'))
        self.cancel_button = QPushButton(tr('btn_cancel'))

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_relationship(self) -> Optional[Relationship]:
        """Создаёт связь из введённых данных.

        Returns:
            Новый Relationship или None при ошибке валидации.
        """
        source_id = self.source_combo.currentData()
        target_id = self.target_combo.currentData()
        rel_type = self.type_combo.currentText()
        description = self.description_input.toPlainText().strip()

        if source_id == target_id:
            QMessageBox.warning(self, tr('error'), tr('same_object_error'))
            return None

        try:
            return Relationship(source_id, target_id, rel_type, description)
        except ValueError as e:
            QMessageBox.warning(self, tr('error'), str(e))
            return None


# =============================================================================
# ХОЛСТ ГРАФА
# =============================================================================

class GraphCanvas(FigureCanvas):
    """Холст для отрисовки графа зависимостей.

    Поддерживает:
        - Масштабирование колесом мыши
        - Панорамирование (Shift+ЛКМ или СКМ)
        - Перетаскивание узлов
        - Подсветку связей
        - Экспорт в PNG
        - Различные алгоритмы компоновки

    Signals:
        node_clicked: Сигнал при клике на узел (передаёт ID узла).
        edge_clicked: Сигнал при клике на ребро (source_id, target_id, type).
    """

    node_clicked = pyqtSignal(str)
    edge_clicked = pyqtSignal(str, str, str)

    # Минимальное расстояние для различия клика и перетаскивания
    DRAG_THRESHOLD = 5

    def __init__(self, parent=None) -> None:
        """Инициализирует холст графа.

        Args:
            parent: Родительский виджет.
        """
        self.figure = Figure(figsize=(10, 7), facecolor='#F8F9FA')
        super().__init__(self.figure)
        self.setParent(parent)
        self.ax = self.figure.add_subplot(111)

        # Данные графа
        self.manager = None
        self.pos = None
        self.highlighted_edge = None
        self.color_scheme = 'default'
        self.layout_algorithm = 'spring'
        self.node_positions = {}
        self.edge_positions = {}
        self.node_radius = 0.15

        # Хранение графических элементов для инкрементального обновления
        self.node_patches = {}      # {node_id: [list of patches]}
        self.node_texts = {}        # {node_id: [list of text objects]}
        self.edge_patches = {}      # {(src, tgt): arrow_patch}
        self.edge_labels = {}       # {(src, tgt): text object}

        # Состояние панорамирования
        self.pan_active = False
        self.pan_mode_enabled = False
        self.pan_start_x = None
        self.pan_start_y = None
        self.pan_start_xlim = None
        self.pan_start_ylim = None

        # Состояние перетаскивания узлов
        self.dragging_node = None
        self.drag_start_pos = None
        self.mouse_press_pos = None
        self.is_dragging = False

        # Подключаем обработчики событий
        self.mpl_connect('button_press_event', self.on_mouse_press)
        self.mpl_connect('button_release_event', self.on_mouse_release)
        self.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.mpl_connect('scroll_event', self.on_scroll)

    def set_color_scheme(self, scheme: str) -> None:
        """Устанавливает цветовую схему графа.

        Args:
            scheme: Название схемы из COLOR_SCHEMES.
        """
        if scheme in COLOR_SCHEMES:
            self.color_scheme = scheme

    def set_layout_algorithm(self, algorithm: str) -> None:
        """Устанавливает алгоритм компоновки графа.

        Args:
            algorithm: Идентификатор алгоритма (spring, circular и т.д.).
        """
        self.layout_algorithm = algorithm
        self.pos = None  # Сбрасываем позиции для пересчёта

    def on_mouse_press(self, event) -> None:
        """Обработчик нажатия кнопки мыши.

        Определяет режим: панорамирование или выбор узла.

        Args:
            event: Событие matplotlib.
        """
        if event.inaxes != self.ax or not self.manager:
            return

        # Сохраняем начальную позицию для определения клика/перетаскивания
        self.mouse_press_pos = (event.x, event.y)
        self.is_dragging = False

        # Панорамирование: СКМ или Shift+ЛКМ или режим Pan
        if (event.button == 2 or
            (event.button == 1 and event.key == 'shift') or
            (event.button == 1 and self.pan_mode_enabled)):
            self.pan_active = True
            self.pan_start_x = event.xdata
            self.pan_start_y = event.ydata
            self.pan_start_xlim = self.ax.get_xlim()
            self.pan_start_ylim = self.ax.get_ylim()
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            return

        # Проверяем клик по узлу (ЛКМ без модификаторов)
        if event.button == 1 and not self.pan_mode_enabled and self.pos:
            click_x, click_y = event.xdata, event.ydata

            for node_id, (x, y) in self.pos.items():
                distance = ((click_x - x) ** 2 + (click_y - y) ** 2) ** 0.5
                if distance < self.node_radius:
                    self.dragging_node = node_id
                    self.drag_start_pos = (click_x, click_y)
                    return

    def on_mouse_release(self, event) -> None:
        """Обработчик отпускания кнопки мыши.

        Завершает панорамирование или перетаскивание.
        Генерирует сигнал node_clicked при клике без перемещения.

        Args:
            event: Событие matplotlib.
        """
        # Завершаем панорамирование
        if self.pan_active:
            self.pan_active = False
            self.pan_start_x = None
            self.pan_start_y = None
            if self.pan_mode_enabled:
                self.setCursor(QCursor(Qt.OpenHandCursor))
            else:
                self.setCursor(QCursor(Qt.ArrowCursor))
            return

        # Завершаем работу с узлом
        if self.dragging_node:
            # Проверяем, был ли это клик (без существенного перемещения)
            if not self.is_dragging and self.mouse_press_pos:
                # Это был клик - показываем информацию
                self.node_clicked.emit(self.dragging_node)

            self.dragging_node = None
            self.drag_start_pos = None
            self.mouse_press_pos = None
            self.is_dragging = False
            self.setCursor(QCursor(Qt.ArrowCursor))

    def on_mouse_move(self, event) -> None:
        """Обработчик движения мыши.

        Выполняет панорамирование или перетаскивание узла.

        Args:
            event: Событие matplotlib.
        """
        if event.inaxes != self.ax:
            return

        # Панорамирование (плавное)
        if self.pan_active and self.pan_start_x is not None and event.xdata is not None:
            # Вычисляем смещение
            dx = event.xdata - self.pan_start_x
            dy = event.ydata - self.pan_start_y

            # Применяем смещение к исходным границам
            new_xlim = [self.pan_start_xlim[0] - dx, self.pan_start_xlim[1] - dx]
            new_ylim = [self.pan_start_ylim[0] - dy, self.pan_start_ylim[1] - dy]

            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            self.draw_idle()  # Используем draw_idle для плавности
            return

        # Перетаскивание узла
        if self.dragging_node and event.xdata and event.ydata:
            # Проверяем порог перетаскивания
            if self.mouse_press_pos and not self.is_dragging:
                dx = abs(event.x - self.mouse_press_pos[0])
                dy = abs(event.y - self.mouse_press_pos[1])
                if dx > self.DRAG_THRESHOLD or dy > self.DRAG_THRESHOLD:
                    self.is_dragging = True
                    self.setCursor(QCursor(Qt.ClosedHandCursor))

            # Если перетаскивание активно, обновляем позицию (оптимизировано)
            if self.is_dragging:
                self._update_dragged_node_fast(
                    self.dragging_node, event.xdata, event.ydata
                )

    def on_scroll(self, event) -> None:
        """Обработчик прокрутки колеса мыши.

        Масштабирует граф относительно позиции курсора.

        Args:
            event: Событие matplotlib.
        """
        if event.inaxes != self.ax:
            return

        base_scale = 1.2

        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()

        xdata = event.xdata
        ydata = event.ydata

        if event.button == 'up':
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            scale_factor = base_scale
        else:
            return

        # Вычисляем новые границы с учётом позиции курсора
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

        new_xlim = [xdata - new_width * (1 - relx), xdata + new_width * relx]
        new_ylim = [ydata - new_height * (1 - rely), ydata + new_height * rely]

        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        self.draw_idle()

    def highlight_edge(self, source_id: str, target_id: str) -> None:
        """Подсвечивает указанное ребро графа.

        Args:
            source_id: ID исходного узла.
            target_id: ID целевого узла.
        """
        self.highlighted_edge = (source_id, target_id)
        self.plot_graph(self.manager)

    def clear_highlight(self) -> None:
        """Снимает подсветку с ребра."""
        self.highlighted_edge = None
        self.plot_graph(self.manager)

    def export_to_png(self, filename: str) -> bool:
        """Экспортирует граф в PNG-файл.

        Args:
            filename: Путь к файлу для сохранения.

        Returns:
            True если экспорт успешен, False при ошибке.
        """
        try:
            self.figure.savefig(filename, dpi=300, bbox_inches='tight',
                              facecolor='white', edgecolor='none')
            return True
        except Exception as e:
            print(f"Ошибка экспорта: {e}")
            return False

    def reset_view(self) -> None:
        """Сбрасывает масштаб и центрирует граф."""
        if self.pos and len(self.pos) > 0:
            x_values = [pos[0] for pos in self.pos.values()]
            y_values = [pos[1] for pos in self.pos.values()]
            margin = 0.3
            self.ax.set_xlim(min(x_values) - margin, max(x_values) + margin)
            self.ax.set_ylim(min(y_values) - margin, max(y_values) + margin)
            self.draw_idle()

    def zoom_by_factor(self, factor: float) -> None:
        """Изменяет масштаб на указанный коэффициент.

        Args:
            factor: Коэффициент масштабирования (< 1 - приближение, > 1 - отдаление).
        """
        cur_xlim = self.ax.get_xlim()
        cur_ylim = self.ax.get_ylim()

        center_x = (cur_xlim[0] + cur_xlim[1]) / 2
        center_y = (cur_ylim[0] + cur_ylim[1]) / 2

        new_width = (cur_xlim[1] - cur_xlim[0]) * factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * factor

        new_xlim = [center_x - new_width / 2, center_x + new_width / 2]
        new_ylim = [center_y - new_height / 2, center_y + new_height / 2]

        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        self.draw_idle()

    def set_pan_mode(self, enabled: bool) -> None:
        """Включает или отключает режим панорамирования.

        Args:
            enabled: True для включения режима.
        """
        self.pan_mode_enabled = enabled
        if enabled:
            self.setCursor(QCursor(Qt.OpenHandCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

    def _update_dragged_node_fast(self, node_id: str, new_x: float, new_y: float) -> None:
        """Быстрое обновление позиции перетаскиваемого узла.

        Вместо полной перерисовки графа обновляет только позиции
        элементов, связанных с перемещаемым узлом.

        Args:
            node_id: ID перетаскиваемого узла.
            new_x: Новая X-координата.
            new_y: Новая Y-координата.
        """
        if not self.manager or node_id not in self.pos:
            return

        old_x, old_y = self.pos[node_id]
        dx = new_x - old_x
        dy = new_y - old_y

        # Обновляем позицию в словаре
        self.pos[node_id] = (new_x, new_y)

        # Обновляем патчи узла
        if node_id in self.node_patches:
            for patch in self.node_patches[node_id]:
                if hasattr(patch, 'center'):
                    # Circle, Ellipse
                    patch.center = (new_x, new_y)
                elif hasattr(patch, 'set_xy'):
                    # Rectangle, FancyBboxPatch
                    old_xy = patch.get_xy()
                    patch.set_xy((old_xy[0] + dx, old_xy[1] + dy))
                elif hasattr(patch, 'xy'):
                    # RegularPolygon
                    patch.xy = (new_x, new_y)

        # Обновляем текстовые метки узла
        if node_id in self.node_texts:
            for text_obj in self.node_texts[node_id]:
                pos = text_obj.get_position()
                text_obj.set_position((pos[0] + dx, pos[1] + dy))

        # Обновляем связанные рёбра
        G = self.manager.graph
        for rel in self.manager.relationships:
            edge_key = (rel.source_id, rel.target_id)

            # Проверяем, связано ли ребро с перемещаемым узлом
            if rel.source_id == node_id or rel.target_id == node_id:
                if edge_key in self.edge_patches and G.has_edge(*edge_key):
                    # Пересчитываем позиции ребра
                    x1, y1 = self.pos[rel.source_id]
                    x2, y2 = self.pos[rel.target_id]

                    ddx = x2 - x1
                    ddy = y2 - y1
                    dist = (ddx**2 + ddy**2) ** 0.5

                    if dist > 0:
                        dx_norm = ddx / dist
                        dy_norm = ddy / dist

                        start_x = x1 + dx_norm * self.node_radius
                        start_y = y1 + dy_norm * self.node_radius
                        end_x = x2 - dx_norm * self.node_radius
                        end_y = y2 - dy_norm * self.node_radius

                        # Обновляем позицию стрелки
                        arrow = self.edge_patches[edge_key]
                        arrow.set_positions((start_x, start_y), (end_x, end_y))

                        # Обновляем позицию метки ребра
                        if edge_key in self.edge_labels:
                            mid_x = (start_x + end_x) / 2
                            mid_y = (start_y + end_y) / 2

                            # Смещение перпендикулярно линии
                            perp_x = -ddy / dist * 0.05
                            perp_y = ddx / dist * 0.05

                            self.edge_labels[edge_key].set_position(
                                (mid_x + perp_x, mid_y + perp_y)
                            )

        # Обновляем отображение без полной перерисовки
        self.draw_idle()


    def _calculate_layout(self, G: nx.Graph) -> Dict:
        """Вычисляет позиции узлов по выбранному алгоритму.

        Args:
            G: Граф NetworkX.

        Returns:
            Словарь позиций {node_id: (x, y)}.
        """
        if len(G.nodes()) == 0:
            return {}

        try:
            if self.layout_algorithm == 'spring':
                return nx.spring_layout(G, k=3, iterations=50, seed=42)
            elif self.layout_algorithm == 'circular':
                return nx.circular_layout(G)
            elif self.layout_algorithm == 'kamada_kawai':
                return nx.kamada_kawai_layout(G)
            elif self.layout_algorithm == 'spectral':
                if len(G.nodes()) > 2:
                    return nx.spectral_layout(G)
                else:
                    return nx.spring_layout(G, k=3, iterations=50, seed=42)
            elif self.layout_algorithm == 'shell':
                return nx.shell_layout(G)
            elif self.layout_algorithm == 'hierarchical':
                # Иерархическая компоновка на основе топологической сортировки
                try:
                    # Пытаемся получить слои по топологической сортировке
                    layers = list(nx.topological_generations(G))
                    pos = {}
                    for layer_idx, layer in enumerate(layers):
                        layer_size = len(layer)
                        for node_idx, node in enumerate(layer):
                            x = (node_idx - (layer_size - 1) / 2) * 2
                            y = -layer_idx * 2
                            pos[node] = (x, y)
                    return pos
                except nx.NetworkXError:
                    # Если граф циклический, используем spring layout
                    return nx.spring_layout(G, k=3, iterations=50, seed=42)
            else:
                return nx.spring_layout(G, k=3, iterations=50, seed=42)
        except Exception:
            return nx.circular_layout(G)

    def plot_graph(self, manager: DependencyManager) -> None:
        """Отрисовывает граф зависимостей.

        Рисует узлы разных форм в зависимости от типа объекта,
        направленные стрелки связей и подписи.

        Args:
            manager: DependencyManager с данными для отображения.
        """
        self.ax.clear()
        self.manager = manager
        self.edge_positions.clear()

        # Очищаем хранилища графических элементов
        self.node_patches.clear()
        self.node_texts.clear()
        self.edge_patches.clear()
        self.edge_labels.clear()

        # Проверяем наличие объектов
        if len(manager.objects) == 0:
            self.ax.text(0.5, 0.5, tr('no_objects'),
                        ha='center', va='center', fontsize=14, color='#6C757D')
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
            self.ax.axis('off')
            self.ax.set_facecolor('#F8F9FA')
            self.draw_idle()
            return

        G = manager.graph
        color_map = COLOR_SCHEMES[self.color_scheme]

        # Вычисляем позиции узлов (сохраняем при перетаскивании)
        if self.pos is None or len(self.pos) != len(G.nodes()):
            self.pos = self._calculate_layout(G)

        # === Рисуем стрелки связей ===
        for rel in manager.relationships:
            edge = (rel.source_id, rel.target_id)
            if G.has_edge(*edge):
                x1, y1 = self.pos[rel.source_id]
                x2, y2 = self.pos[rel.target_id]

                dx = x2 - x1
                dy = y2 - y1
                dist = np.sqrt(dx**2 + dy**2)

                if dist > 0:
                    dx_norm = dx / dist
                    dy_norm = dy / dist

                    # Смещаем начало и конец от центров узлов
                    start_x = x1 + dx_norm * self.node_radius
                    start_y = y1 + dy_norm * self.node_radius
                    end_x = x2 - dx_norm * self.node_radius
                    end_y = y2 - dy_norm * self.node_radius

                    # Настройки подсвеченного/обычного ребра
                    color = '#E63946' if self.highlighted_edge == edge else '#495057'
                    width = 3.0 if self.highlighted_edge == edge else 1.8
                    alpha = 1.0 if self.highlighted_edge == edge else 0.6

                    arrow = FancyArrowPatch(
                        (start_x, start_y), (end_x, end_y),
                        arrowstyle='->', mutation_scale=25,
                        color=color, linewidth=width, alpha=alpha,
                        connectionstyle="arc3,rad=0.1", zorder=1
                    )
                    self.ax.add_patch(arrow)

                    # Сохраняем ссылку на стрелку для быстрого обновления
                    self.edge_patches[(rel.source_id, rel.target_id)] = arrow

                    # Сохраняем позицию для подписи
                    mid_x = (start_x + end_x) / 2
                    mid_y = (start_y + end_y) / 2
                    self.edge_positions[(rel.source_id, rel.target_id)] = (mid_x, mid_y)

        # === Рисуем узлы с разными формами ===
        for node, (x, y) in self.pos.items():
            obj = manager.objects.get(node)
            color = color_map.get(obj.type, '#ADB5BD') if obj else '#ADB5BD'

            if obj:
                if obj.type in ['file', 'godot_script']:
                    # Прямоугольник для файлов и скриптов
                    rect = Rectangle(
                        (x - self.node_radius * 0.8, y - self.node_radius),
                        self.node_radius * 1.6, self.node_radius * 2,
                        color=color, ec='#212529', linewidth=2.5,
                        alpha=0.9, zorder=3
                    )
                    self.ax.add_patch(rect)
                    self.node_patches[node] = [rect]
                elif obj.type in ['database', 'godot_resource']:
                    # Эллипс для баз данных и ресурсов
                    from matplotlib.patches import Ellipse
                    ellipse = Ellipse(
                        (x, y), self.node_radius * 2, self.node_radius * 2.5,
                        color=color, ec='#212529', linewidth=2.5,
                        alpha=0.9, zorder=3
                    )
                    self.ax.add_patch(ellipse)
                    self.node_patches[node] = [ellipse]
                elif obj.type in ['router', 'switch']:
                    # Ромб для сетевого оборудования
                    diamond = RegularPolygon(
                        (x, y), 4, radius=self.node_radius * 1.3,
                        orientation=np.pi/4,
                        color=color, ec='#212529', linewidth=2.5,
                        alpha=0.9, zorder=3
                    )
                    self.ax.add_patch(diamond)
                    self.node_patches[node] = [diamond]
                elif obj.type in ['server', 'godot_autoload']:
                    # Скруглённый прямоугольник для серверов и autoload
                    rect = FancyBboxPatch(
                        (x - self.node_radius, y - self.node_radius * 0.8),
                        self.node_radius * 2, self.node_radius * 1.6,
                        boxstyle="round,pad=0.02",
                        color=color, ec='#212529', linewidth=2.5,
                        alpha=0.9, zorder=3
                    )
                    self.ax.add_patch(rect)
                    self.node_patches[node] = [rect]
                elif obj.type == 'godot_scene':
                    # Круг с внутренним кругом для сцен
                    circle_outer = Circle(
                        (x, y), self.node_radius * 1.1,
                        color=color, ec='#212529', linewidth=2.5,
                        alpha=0.9, zorder=3
                    )
                    self.ax.add_patch(circle_outer)
                    circle_inner = Circle(
                        (x, y), self.node_radius * 0.5,
                        color='white', ec='#212529', linewidth=1.5,
                        alpha=0.9, zorder=4
                    )
                    self.ax.add_patch(circle_inner)
                    self.node_patches[node] = [circle_outer, circle_inner]
                else:
                    # Круг по умолчанию (контейнеры)
                    circle = Circle(
                        (x, y), self.node_radius,
                        color=color, ec='#212529', linewidth=2.5,
                        alpha=0.9, zorder=3
                    )
                    self.ax.add_patch(circle)
                    self.node_patches[node] = [circle]

        # === Рисуем иконки и названия узлов ===
        for node, (x, y) in self.pos.items():
            obj = manager.objects.get(node)
            if obj:
                # Иконка типа
                icon = NODE_ICONS.get(obj.type, '◉')
                icon_text = self.ax.text(x, y + 0.02, icon, fontsize=18, fontweight='bold',
                           ha='center', va='center', zorder=5, color='#1a1a2e')

                # Название (обрезаем длинные)
                name = obj.name if len(obj.name) <= 15 else obj.name[:13] + '..'
                name_text = self.ax.text(x, y - 0.22, name, fontsize=8, fontweight='bold',
                           ha='center', va='top', zorder=4,
                           bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                                   edgecolor='#DEE2E6', alpha=0.95, linewidth=1.5))

                # Сохраняем ссылки на текстовые объекты
                self.node_texts[node] = [icon_text, name_text]

        # === Рисуем подписи связей ===
        for rel in manager.relationships:
            if G.has_edge(rel.source_id, rel.target_id):
                x1, y1 = self.pos[rel.source_id]
                x2, y2 = self.pos[rel.target_id]

                # Позиция подписи на середине ребра со смещением
                label_x = x1 + (x2 - x1) * 0.5
                label_y = y1 + (y2 - y1) * 0.5

                dx = x2 - x1
                dy = y2 - y1
                dist = np.sqrt(dx**2 + dy**2)

                if dist > 0:
                    # Смещение перпендикулярно линии связи
                    perp_x = -dy / dist * 0.05
                    perp_y = dx / dist * 0.05

                    label_x += perp_x
                    label_y += perp_y

                edge_label = self.ax.text(label_x, label_y, rel.type, fontsize=7,
                           bbox=dict(boxstyle='round,pad=0.25', facecolor='#FFFFEB',
                                   edgecolor='#999999', alpha=0.9, linewidth=0.8),
                           ha='center', va='center', zorder=5,
                           color='#212529', fontweight='600')

                # Сохраняем ссылку на метку ребра
                self.edge_labels[(rel.source_id, rel.target_id)] = edge_label

        # Настройки осей
        self.ax.set_title(tr('graph_title'), fontsize=18, fontweight='bold',
                         pad=20, color='#212529')
        self.ax.axis('off')
        self.ax.set_facecolor('#F8F9FA')

        # Устанавливаем границы с отступом
        if self.pos:
            x_values = [pos[0] for pos in self.pos.values()]
            y_values = [pos[1] for pos in self.pos.values()]
            margin = 0.5
            self.ax.set_xlim(min(x_values) - margin, max(x_values) + margin)
            self.ax.set_ylim(min(y_values) - margin, max(y_values) + margin)

        self.figure.tight_layout()
        self.draw_idle()


# =============================================================================
# ОКНО ПРОЕКТА
# =============================================================================

class ProjectWindow(QWidget):
    """Окно проекта с редактированием объектов и визуализацией графа.

    Содержит:
        - Вкладки со списками объектов и связей
        - Холст с интерактивным графом
        - Панель навигации и инструментов

    Attributes:
        manager: DependencyManager с данными проекта.
        current_file: Путь к файлу проекта или None.
        modified: Флаг наличия несохранённых изменений.

    Signals:
        language_changed: Сигнал при смене языка интерфейса.
    """

    language_changed = pyqtSignal()

    def __init__(self, manager: DependencyManager = None,
                 filename: str = None) -> None:
        """Инициализирует окно проекта.

        Args:
            manager: Менеджер зависимостей или None для создания нового.
            filename: Путь к файлу проекта.
        """
        super().__init__()
        self.manager = manager or DependencyManager()
        self.current_file = filename
        self.modified = False
        self.setup_ui()
        self.apply_styles()
        self.update_ui()

        if filename:
            self.setWindowTitle(f"{tr('project')}: {os.path.basename(filename)}")
        else:
            self.setWindowTitle(tr('new_project'))

    def apply_styles(self) -> None:
        """Применяет стили к элементам интерфейса."""
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:disabled {
                background-color: #CED4DA;
                color: #6C757D;
            }
            QPushButton:checked {
                background-color: #28A745;
            }
            QListWidget {
                border: 2px solid #DEE2E6;
                border-radius: 6px;
                background-color: #F8F9FA;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                margin: 2px;
                color: #212529;
            }
            QListWidget::item:selected {
                background-color: #007BFF;
                color: white;
            }
            QListWidget::item:hover:!selected {
                background-color: #E9ECEF;
            }
            QListWidget::item:selected:hover {
                background-color: #0056b3;
                color: white;
            }
            QLabel {
                color: #212529;
                font-size: 10pt;
            }
            QLineEdit, QTextEdit, QComboBox {
                border: 2px solid #DEE2E6;
                border-radius: 6px;
                padding: 6px;
                background-color: white;
                color: #212529;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border-color: #007BFF;
            }
            QTabWidget::pane {
                border: 2px solid #DEE2E6;
                border-radius: 6px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #E9ECEF;
                color: #495057;
                padding: 10px 20px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background-color: #007BFF;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #DEE2E6;
            }
        """)

    def setup_ui(self) -> None:
        """Настраивает элементы интерфейса окна."""
        main_layout = QHBoxLayout(self)

        # === Левая панель со списками ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self.tabs = QTabWidget()

        # Вкладка объектов
        objects_tab = QWidget()
        objects_layout = QVBoxLayout(objects_tab)

        self.objects_label = QLabel(f"<b>{tr('objects_title')}</b>")
        objects_layout.addWidget(self.objects_label)

        self.objects_list = QListWidget()
        self.objects_list.itemClicked.connect(self.on_object_selected)
        self.objects_list.itemDoubleClicked.connect(self.view_object)
        objects_layout.addWidget(self.objects_list)

        # Кнопки управления объектами
        obj_buttons = QHBoxLayout()
        self.add_obj_btn = QPushButton(tr('btn_add'))
        self.edit_obj_btn = QPushButton(tr('btn_edit'))
        self.remove_obj_btn = QPushButton(tr('btn_remove'))
        self.view_obj_btn = QPushButton(tr('btn_view'))

        self.add_obj_btn.clicked.connect(self.add_object)
        self.edit_obj_btn.clicked.connect(self.edit_object)
        self.remove_obj_btn.clicked.connect(self.remove_object)
        self.view_obj_btn.clicked.connect(self.view_object)

        obj_buttons.addWidget(self.add_obj_btn)
        obj_buttons.addWidget(self.edit_obj_btn)
        obj_buttons.addWidget(self.remove_obj_btn)
        obj_buttons.addWidget(self.view_obj_btn)
        objects_layout.addLayout(obj_buttons)

        self.tabs.addTab(objects_tab, tr('tab_objects'))

        # Вкладка связей
        relations_tab = QWidget()
        relations_layout = QVBoxLayout(relations_tab)

        self.relationships_label = QLabel(f"<b>{tr('relationships_title')}</b>")
        relations_layout.addWidget(self.relationships_label)

        self.relationships_list = QListWidget()
        self.relationships_list.itemClicked.connect(self.on_relationship_selected)
        self.relationships_list.itemDoubleClicked.connect(self.view_relationship)
        relations_layout.addWidget(self.relationships_list)

        # Кнопки управления связями
        rel_buttons = QHBoxLayout()
        self.add_rel_btn = QPushButton(tr('btn_add'))
        self.edit_rel_btn = QPushButton(tr('btn_edit'))
        self.remove_rel_btn = QPushButton(tr('btn_remove'))
        self.view_rel_btn = QPushButton(tr('btn_view'))

        self.add_rel_btn.clicked.connect(self.add_relationship)
        self.edit_rel_btn.clicked.connect(self.edit_relationship)
        self.remove_rel_btn.clicked.connect(self.remove_relationship)
        self.view_rel_btn.clicked.connect(self.view_relationship)

        rel_buttons.addWidget(self.add_rel_btn)
        rel_buttons.addWidget(self.edit_rel_btn)
        rel_buttons.addWidget(self.remove_rel_btn)
        rel_buttons.addWidget(self.view_rel_btn)
        relations_layout.addLayout(rel_buttons)

        self.tabs.addTab(relations_tab, tr('tab_relationships'))

        left_layout.addWidget(self.tabs)
        left_panel.setMaximumWidth(400)

        # === Правая панель с графом ===
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.visualization_label = QLabel(f"<b>{tr('visualization_title')}</b>")
        right_layout.addWidget(self.visualization_label)

        # Холст графа
        self.graph_canvas = GraphCanvas()
        self.graph_canvas.node_clicked.connect(self.on_graph_node_clicked)
        self.graph_canvas.edge_clicked.connect(self.on_graph_edge_clicked)

        # Панель навигации
        nav_toolbar = QWidget()
        nav_layout = QHBoxLayout(nav_toolbar)
        nav_layout.setContentsMargins(5, 5, 5, 5)

        self.zoom_in_btn = QPushButton(tr('btn_zoom_in'))
        self.zoom_in_btn.setFixedHeight(35)
        self.zoom_in_btn.setToolTip(tr('hint_zoom_in'))
        self.zoom_in_btn.clicked.connect(self.zoom_in)

        self.zoom_out_btn = QPushButton(tr('btn_zoom_out'))
        self.zoom_out_btn.setFixedHeight(35)
        self.zoom_out_btn.setToolTip(tr('hint_zoom_out'))
        self.zoom_out_btn.clicked.connect(self.zoom_out)

        self.pan_btn = QPushButton(tr('btn_pan'))
        self.pan_btn.setFixedHeight(35)
        self.pan_btn.setToolTip(tr('hint_pan'))
        self.pan_btn.setCheckable(True)
        self.pan_btn.toggled.connect(self.toggle_pan_mode)

        self.layout_btn = QPushButton(tr('btn_layout'))
        self.layout_btn.setFixedHeight(35)
        self.layout_btn.clicked.connect(self.change_layout)

        self.nav_label = QLabel(f"{tr('navigation')}")
        nav_layout.addWidget(self.nav_label)
        nav_layout.addWidget(self.zoom_in_btn)
        nav_layout.addWidget(self.zoom_out_btn)
        nav_layout.addWidget(self.pan_btn)
        nav_layout.addWidget(self.layout_btn)
        nav_layout.addStretch()

        # Контейнер для графа
        graph_container = QWidget()
        graph_container_layout = QVBoxLayout(graph_container)
        graph_container_layout.setContentsMargins(0, 0, 0, 0)
        graph_container_layout.addWidget(nav_toolbar)
        graph_container_layout.addWidget(self.graph_canvas)

        right_layout.addWidget(graph_container)

        # Подсказка по управлению
        self.info_label = QLabel(f"<i>{tr('hint_controls')}</i>")
        self.info_label.setStyleSheet("color: #6C757D; font-size: 9px;")
        right_layout.addWidget(self.info_label)

        # Кнопки управления графом
        graph_buttons = QHBoxLayout()
        self.refresh_btn = QPushButton(tr('btn_refresh'))
        self.reset_zoom_btn = QPushButton(tr('btn_reset_zoom'))
        self.color_btn = QPushButton(tr('btn_color'))
        self.export_btn = QPushButton(tr('btn_export'))

        self.refresh_btn.clicked.connect(self.refresh_graph)
        self.reset_zoom_btn.clicked.connect(self.reset_zoom)
        self.color_btn.clicked.connect(self.change_color_scheme)
        self.export_btn.clicked.connect(self.export_graph)

        graph_buttons.addWidget(self.refresh_btn)
        graph_buttons.addWidget(self.reset_zoom_btn)
        graph_buttons.addWidget(self.color_btn)
        graph_buttons.addWidget(self.export_btn)
        right_layout.addLayout(graph_buttons)

        # Сплиттер для изменения размеров панелей
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

    def retranslate_ui(self) -> None:
        """Обновляет тексты интерфейса при смене языка."""
        # Вкладки
        self.tabs.setTabText(0, tr('tab_objects'))
        self.tabs.setTabText(1, tr('tab_relationships'))

        # Заголовки
        self.objects_label.setText(f"<b>{tr('objects_title')}</b>")
        self.relationships_label.setText(f"<b>{tr('relationships_title')}</b>")
        self.visualization_label.setText(f"<b>{tr('visualization_title')}</b>")
        self.nav_label.setText(f"{tr('navigation')}")
        self.info_label.setText(f"<i>{tr('hint_controls')}</i>")

        # Кнопки объектов
        self.add_obj_btn.setText(tr('btn_add'))
        self.edit_obj_btn.setText(tr('btn_edit'))
        self.remove_obj_btn.setText(tr('btn_remove'))
        self.view_obj_btn.setText(tr('btn_view'))

        # Кнопки связей
        self.add_rel_btn.setText(tr('btn_add'))
        self.edit_rel_btn.setText(tr('btn_edit'))
        self.remove_rel_btn.setText(tr('btn_remove'))
        self.view_rel_btn.setText(tr('btn_view'))

        # Кнопки навигации и графа
        self.zoom_in_btn.setText(tr('btn_zoom_in'))
        self.zoom_out_btn.setText(tr('btn_zoom_out'))
        self.pan_btn.setText(tr('btn_pan'))
        self.layout_btn.setText(tr('btn_layout'))
        self.refresh_btn.setText(tr('btn_refresh'))
        self.reset_zoom_btn.setText(tr('btn_reset_zoom'))
        self.color_btn.setText(tr('btn_color'))
        self.export_btn.setText(tr('btn_export'))

        # Заголовок окна
        if self.current_file:
            self.setWindowTitle(f"{tr('project')}: {os.path.basename(self.current_file)}")
        else:
            self.setWindowTitle(tr('new_project'))

        # Обновляем списки
        self.update_ui()

    def update_ui(self) -> None:
        """Обновляет списки объектов и связей."""
        # Список объектов
        self.objects_list.clear()
        for obj in self.manager.objects.values():
            label = get_node_label(obj.type)
            icon = NODE_ICONS.get(obj.type, '◉')
            item = QListWidgetItem(f"{icon} {label}: {obj.name}")
            item.setData(Qt.UserRole, obj.id)
            self.objects_list.addItem(item)

        # Список связей
        self.relationships_list.clear()
        for rel in self.manager.relationships:
            source_name = self.manager.objects[rel.source_id].name
            target_name = self.manager.objects[rel.target_id].name
            text = f"{source_name} → [{rel.type}] → {target_name}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, (rel.source_id, rel.target_id, rel.type))
            self.relationships_list.addItem(item)

        # Доступность кнопок
        has_objects = len(self.manager.objects) > 0
        self.edit_obj_btn.setEnabled(has_objects)
        self.remove_obj_btn.setEnabled(has_objects)
        self.view_obj_btn.setEnabled(has_objects)
        self.add_rel_btn.setEnabled(len(self.manager.objects) >= 2)
        self.edit_rel_btn.setEnabled(len(self.manager.relationships) > 0)
        self.remove_rel_btn.setEnabled(len(self.manager.relationships) > 0)
        self.view_rel_btn.setEnabled(len(self.manager.relationships) > 0)
        self.export_btn.setEnabled(has_objects)

        self.refresh_graph()

    def mark_modified(self) -> None:
        """Отмечает проект как изменённый."""
        self.modified = True
        title = self.windowTitle()
        if not title.endswith('*'):
            self.setWindowTitle(title + ' *')

    def mark_saved(self) -> None:
        """Отмечает проект как сохранённый."""
        self.modified = False
        title = self.windowTitle()
        if title.endswith(' *'):
            self.setWindowTitle(title[:-2])

    # === Методы работы с объектами ===

    def add_object(self) -> None:
        """Открывает диалог добавления нового объекта."""
        dialog = ObjectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            obj = dialog.get_object()
            if obj and self.manager.add_object(obj):
                self.mark_modified()
                self.update_ui()

    def edit_object(self) -> None:
        """Открывает диалог редактирования выбранного объекта."""
        current_item = self.objects_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, tr('error'), tr('select_object'))
            return

        obj_id = current_item.data(Qt.UserRole)
        obj = self.manager.objects.get(obj_id)

        dialog = ObjectDialog(self, edit_obj=obj)
        if dialog.exec_() == QDialog.Accepted:
            new_obj = dialog.get_object()
            if new_obj and self.manager.update_object(obj_id, new_obj):
                self.mark_modified()
                self.update_ui()

    def remove_object(self) -> None:
        """Удаляет выбранный объект после подтверждения."""
        current_item = self.objects_list.currentItem()
        if not current_item:
            return

        obj_id = current_item.data(Qt.UserRole)
        obj = self.manager.objects.get(obj_id)

        reply = QMessageBox.question(
            self, tr('confirm'),
            f"{tr('confirm_delete_obj')} '{obj.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes and self.manager.remove_object(obj_id):
            self.mark_modified()
            self.update_ui()

    def view_object(self) -> None:
        """Показывает информацию о выбранном объекте."""
        current_item = self.objects_list.currentItem()
        if not current_item:
            return

        obj_id = current_item.data(Qt.UserRole)
        self.show_object_info(obj_id)

    def show_object_info(self, obj_id: str) -> None:
        """Показывает диалог с информацией об объекте.

        Args:
            obj_id: ID объекта для отображения.
        """
        obj = self.manager.objects.get(obj_id)
        if not obj:
            return

        dependencies = self.manager.get_dependencies(obj_id)
        dependents = self.manager.get_dependents(obj_id)

        label = get_node_label(obj.type)
        icon = NODE_ICONS.get(obj.type, '◉')

        info = f"<h3>{icon} {label}: {tr('info_object')}</h3>"
        info += f"<b>{tr('info_id')}</b> {obj.id}<br>"
        info += f"<b>{tr('info_type')}</b> {obj.type}<br>"
        info += f"<b>{tr('info_name')}</b> {obj.name}<br>"
        info += f"<b>{tr('info_created')}</b> {obj.created_at[:19].replace('T', '  ')}<br>"

        if obj.properties:
            info += f"<br><b>{tr('info_properties')}</b><br>"
            for key, value in obj.properties.items():
                info += f"&nbsp;&nbsp;• {key}: {value}<br>"

        if dependencies:
            info += f"<br><b>{tr('info_depends_on')} ({len(dependencies)}):</b><br>"
            for dep_id in dependencies:
                dep = self.manager.objects[dep_id]
                info += f"&nbsp;&nbsp;• {dep.name}<br>"

        if dependents:
            info += f"<br><b>{tr('info_dependents')} ({len(dependents)}):</b><br>"
            for dep_id in dependents:
                dep = self.manager.objects[dep_id]
                info += f"&nbsp;&nbsp;• {dep.name}<br>"

        msg = QMessageBox(self)
        msg.setWindowTitle(tr('info_object'))
        msg.setTextFormat(Qt.RichText)
        msg.setText(info)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #212529;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        msg.exec_()

    def on_object_selected(self, item) -> None:
        """Обработчик выбора объекта в списке."""
        pass

    # === Методы работы со связями ===

    def add_relationship(self) -> None:
        """Открывает диалог добавления новой связи."""
        if len(self.manager.objects) < 2:
            QMessageBox.warning(self, tr('error'), tr('need_2_objects'))
            return

        dialog = RelationshipDialog(self.manager.objects, self)
        if dialog.exec_() == QDialog.Accepted:
            rel = dialog.get_relationship()
            if rel and self.manager.add_relationship(rel):
                self.mark_modified()
                self.update_ui()

    def edit_relationship(self) -> None:
        """Открывает диалог редактирования выбранной связи."""
        current_item = self.relationships_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, tr('error'), tr('select_relationship'))
            return

        source_id, target_id, rel_type = current_item.data(Qt.UserRole)

        rel = None
        for r in self.manager.relationships:
            if (r.source_id == source_id and r.target_id == target_id and
                r.type == rel_type):
                rel = r
                break

        if not rel:
            return

        dialog = RelationshipDialog(self.manager.objects, self, edit_rel=rel)
        if dialog.exec_() == QDialog.Accepted:
            new_rel = dialog.get_relationship()
            if new_rel:
                old_rel = (source_id, target_id, rel_type)
                if self.manager.update_relationship(old_rel, new_rel):
                    self.mark_modified()
                    self.update_ui()

    def remove_relationship(self) -> None:
        """Удаляет выбранную связь после подтверждения."""
        current_item = self.relationships_list.currentItem()
        if not current_item:
            return

        source_id, target_id, rel_type = current_item.data(Qt.UserRole)

        reply = QMessageBox.question(
            self, tr('confirm'),
            tr('confirm_delete_rel'),
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            if self.manager.remove_relationship(source_id, target_id, rel_type):
                self.mark_modified()
                self.graph_canvas.clear_highlight()
                self.update_ui()

    def view_relationship(self) -> None:
        """Показывает информацию о выбранной связи."""
        current_item = self.relationships_list.currentItem()
        if not current_item:
            return

        source_id, target_id, rel_type = current_item.data(Qt.UserRole)

        rel = None
        for r in self.manager.relationships:
            if (r.source_id == source_id and r.target_id == target_id and
                r.type == rel_type):
                rel = r
                break

        if not rel:
            return

        source = self.manager.objects[rel.source_id]
        target = self.manager.objects[rel.target_id]

        info = f"<h3>{tr('info_relationship')}</h3>"
        info += f"<b>{tr('info_source_obj')}</b> {source.name} ({source.id})<br>"
        info += f"<b>{tr('info_rel_type')}</b> {rel.type}<br>"
        info += f"<b>{tr('info_target_obj')}</b> {target.name} ({target.id})<br>"
        info += f"<b>{tr('info_created_at')}</b> {rel.created_at[:19].replace('T', '  ')}<br>"

        if rel.description:
            info += f"<br><b>{tr('info_description')}</b><br>{rel.description}"

        msg = QMessageBox(self)
        msg.setWindowTitle(tr('info_relationship'))
        msg.setTextFormat(Qt.RichText)
        msg.setText(info)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #212529;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        msg.exec_()

    def on_relationship_selected(self, item) -> None:
        """Обработчик выбора связи в списке."""
        source_id, target_id, _ = item.data(Qt.UserRole)
        self.graph_canvas.highlight_edge(source_id, target_id)

    # === Обработчики событий графа ===

    def on_graph_node_clicked(self, node_id: str) -> None:
        """Обработчик клика на узел графа."""
        self.show_object_info(node_id)

    def on_graph_edge_clicked(self, source_id: str, target_id: str,
                              rel_type: str) -> None:
        """Обработчик клика на ребро графа."""
        for i in range(self.relationships_list.count()):
            item = self.relationships_list.item(i)
            s, t, r = item.data(Qt.UserRole)
            if s == source_id and t == target_id and r == rel_type:
                self.relationships_list.setCurrentItem(item)
                self.graph_canvas.highlight_edge(source_id, target_id)
                break

    # === Методы управления графом ===

    def refresh_graph(self) -> None:
        """Перерисовывает граф."""
        self.graph_canvas.plot_graph(self.manager)

    def reset_zoom(self) -> None:
        """Сбрасывает масштаб графа."""
        self.graph_canvas.reset_view()

    def zoom_in(self) -> None:
        """Приближает граф."""
        self.graph_canvas.zoom_by_factor(0.8)

    def zoom_out(self) -> None:
        """Отдаляет граф."""
        self.graph_canvas.zoom_by_factor(1.25)

    def toggle_pan_mode(self, checked: bool) -> None:
        """Переключает режим панорамирования.

        Args:
            checked: Состояние кнопки.
        """
        self.graph_canvas.set_pan_mode(checked)

    def change_layout(self) -> None:
        """Открывает диалог выбора алгоритма компоновки."""
        dialog = LayoutDialog(self, self.graph_canvas.layout_algorithm)
        if dialog.exec_() == QDialog.Accepted:
            new_layout = dialog.get_layout()
            self.graph_canvas.set_layout_algorithm(new_layout)
            self.refresh_graph()

    def change_color_scheme(self) -> None:
        """Открывает диалог выбора цветовой схемы."""
        schemes = list(COLOR_SCHEMES.keys())

        # Создаём кастомный диалог вместо QInputDialog
        dialog = QDialog(self)
        dialog.setWindowTitle(tr('scheme_dialog'))
        dialog.setMinimumWidth(300)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #212529;
                font-size: 11pt;
                padding: 5px;
            }
            QListWidget {
                border: 2px solid #DEE2E6;
                border-radius: 6px;
                background-color: #F8F9FA;
                padding: 5px;
                font-size: 11pt;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 4px;
                margin: 2px;
                color: #212529;
            }
            QListWidget::item:selected {
                background-color: #007BFF;
                color: white;
            }
            QListWidget::item:hover:!selected {
                background-color: #E9ECEF;
            }
            QListWidget::item:selected:hover {
                background-color: #0056b3;
                color: white;
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: 600;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(tr('scheme_select')))

        scheme_list = QListWidget()
        for scheme in schemes:
            scheme_list.addItem(scheme)

        current_idx = schemes.index(self.graph_canvas.color_scheme) if self.graph_canvas.color_scheme in schemes else 0
        scheme_list.setCurrentRow(current_idx)
        scheme_list.itemDoubleClicked.connect(dialog.accept)
        layout.addWidget(scheme_list)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton(tr('btn_cancel'))
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        if dialog.exec_() == QDialog.Accepted and scheme_list.currentItem():
            scheme = scheme_list.currentItem().text()
            self.graph_canvas.set_color_scheme(scheme)
            self.refresh_graph()

    def export_graph(self) -> None:
        """Экспортирует граф в PNG-файл."""
        filename, _ = QFileDialog.getSaveFileName(
            self, tr('export_dialog'),
            "infrastructure_graph.png",
            "PNG Files (*.png)"
        )

        if filename:
            if self.graph_canvas.export_to_png(filename):
                QMessageBox.information(
                    self, tr('success'),
                    f"{tr('export_success')}\n{filename}"
                )
            else:
                QMessageBox.critical(self, tr('error'), tr('export_error'))


# =============================================================================
# ГЛАВНОЕ ОКНО
# =============================================================================

class MainWindow(QMainWindow):
    """Главное окно приложения.

    Содержит:
        - MDI-область для нескольких открытых проектов
        - Меню: Файл, Окна, Язык
        - Строку состояния
    """

    def __init__(self) -> None:
        """Инициализирует главное окно."""
        super().__init__()
        self.setup_ui()
        self.apply_styles()
        self.new_project()

    def apply_styles(self) -> None:
        """Применяет стили к элементам интерфейса."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8F9FA;
            }
            QMenuBar {
                background-color: #FFFFFF;
                color: #212529;
                border-bottom: 2px solid #DEE2E6;
                padding: 5px;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: #007BFF;
                color: white;
            }
            QMenu {
                background-color: #FFFFFF;
                border: 2px solid #DEE2E6;
                border-radius: 6px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px;
                border-radius: 4px;
                color: #212529;
            }
            QMenu::item:selected {
                background-color: #007BFF;
                color: white;
            }
            QStatusBar {
                background-color: #F8F9FA;
                color: #495057;
                border-top: 2px solid #DEE2E6;
            }
            QMdiArea {
                background-color: #E9ECEF;
            }
        """)

    def setup_ui(self) -> None:
        """Настраивает элементы интерфейса."""
        self.setWindowTitle(tr('app_title'))
        self.setGeometry(100, 100, 1400, 800)

        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)

        self.create_menus()

        self.statusBar().showMessage(tr('ready'))

    def create_menus(self) -> None:
        """Создаёт меню приложения."""
        menubar = self.menuBar()
        menubar.clear()

        # Меню Файл
        file_menu = menubar.addMenu(tr('menu_file'))

        new_action = QAction(tr('menu_new'), self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)

        open_action = QAction(tr('menu_open'), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        # Подменю Импорт
        import_menu = file_menu.addMenu(tr('menu_import'))

        import_compose = QAction(tr('menu_docker'), self)
        import_compose.triggered.connect(self.import_docker_compose)
        import_menu.addAction(import_compose)

        import_k8s = QAction(tr('menu_k8s'), self)
        import_k8s.triggered.connect(self.import_kubernetes)
        import_menu.addAction(import_k8s)

        import_godot = QAction(tr('menu_godot'), self)
        import_godot.triggered.connect(self.import_godot_project)
        import_menu.addAction(import_godot)

        file_menu.addSeparator()

        save_action = QAction(tr('menu_save'), self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)

        save_as_action = QAction(tr('menu_save_as'), self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction(tr('menu_exit'), self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню Окна
        window_menu = menubar.addMenu(tr('menu_windows'))

        cascade_action = QAction(tr('menu_cascade'), self)
        cascade_action.triggered.connect(self.mdi.cascadeSubWindows)
        window_menu.addAction(cascade_action)

        tile_action = QAction(tr('menu_tile'), self)
        tile_action.triggered.connect(self.mdi.tileSubWindows)
        window_menu.addAction(tile_action)

        # Меню Язык
        language_menu = menubar.addMenu(tr('menu_language'))

        russian_action = QAction(tr('menu_russian'), self)
        russian_action.triggered.connect(lambda: self.change_language('ru'))
        language_menu.addAction(russian_action)

        english_action = QAction(tr('menu_english'), self)
        english_action.triggered.connect(lambda: self.change_language('en'))
        language_menu.addAction(english_action)

    def change_language(self, lang: str) -> None:
        """Меняет язык интерфейса.

        Args:
            lang: Код языка ('ru' или 'en').
        """
        set_language(lang)

        self.create_menus()
        self.setWindowTitle(tr('app_title'))
        self.statusBar().showMessage(tr('ready'))

        # Обновляем все открытые окна проектов
        for window in self.mdi.subWindowList():
            project = window.widget()
            if isinstance(project, ProjectWindow):
                project.retranslate_ui()

    def closeEvent(self, event) -> None:
        """Обработчик закрытия приложения.

        Проверяет несохранённые изменения во всех проектах.

        Args:
            event: Событие закрытия.
        """
        unsaved_projects = []

        for window in self.mdi.subWindowList():
            project = window.widget()
            if isinstance(project, ProjectWindow) and project.modified:
                unsaved_projects.append((window, project))

        if not unsaved_projects:
            event.accept()
            return

        for window, project in unsaved_projects:
            self.mdi.setActiveSubWindow(window)

            project_name = project.current_file if project.current_file else tr('new_project')
            if project.current_file:
                project_name = os.path.basename(project_name)

            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle(tr('unsaved_title'))
            msg.setText(f"{tr('project')} '{project_name}' {tr('unsaved_text')}")
            msg.setInformativeText(tr('unsaved_question'))
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #FFFFFF;
                }
                QLabel {
                    color: #212529;
                }
                QPushButton {
                    background-color: #007BFF;
                    color: white;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 6px;
                    font-weight: 600;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)

            save_btn = msg.addButton(tr('btn_save_changes'), QMessageBox.AcceptRole)
            dont_save_btn = msg.addButton(tr('btn_dont_save'), QMessageBox.DestructiveRole)
            cancel_btn = msg.addButton(tr('btn_cancel'), QMessageBox.RejectRole)

            msg.setDefaultButton(save_btn)
            msg.exec_()

            clicked = msg.clickedButton()

            if clicked == cancel_btn:
                event.ignore()
                return
            elif clicked == save_btn:
                if project.current_file:
                    if not project.manager.save_to_file(project.current_file):
                        QMessageBox.critical(
                            self, tr('error'),
                            f"{tr('save_error')} '{project_name}'"
                        )
                        event.ignore()
                        return
                else:
                    filename, _ = QFileDialog.getSaveFileName(
                        self, tr('save_project'),
                        "infrastructure.json",
                        "JSON Files (*.json)"
                    )

                    if filename:
                        if not project.manager.save_to_file(filename):
                            QMessageBox.critical(self, tr('error'), tr('save_error'))
                            event.ignore()
                            return
                    else:
                        event.ignore()
                        return

        event.accept()

    def new_project(self) -> None:
        """Создаёт новый пустой проект."""
        project = ProjectWindow()
        sub = QMdiSubWindow()
        sub.setWidget(project)
        sub.setAttribute(Qt.WA_DeleteOnClose)
        self.mdi.addSubWindow(sub)
        sub.show()
        self.statusBar().showMessage(tr('new_project_created'), 3000)

    def open_project(self) -> None:
        """Открывает проект из файла."""
        filename, _ = QFileDialog.getOpenFileName(
            self, tr('open_project'), "",
            "JSON Files (*.json)"
        )

        if filename:
            manager = DependencyManager()
            if manager.load_from_file(filename):
                project = ProjectWindow(manager, filename)
                sub = QMdiSubWindow()
                sub.setWidget(project)
                sub.setAttribute(Qt.WA_DeleteOnClose)
                self.mdi.addSubWindow(sub)
                sub.show()
                self.statusBar().showMessage(f"{tr('loaded')}: {filename}", 3000)
            else:
                QMessageBox.critical(self, tr('error'), tr('load_error'))

    def import_docker_compose(self) -> None:
        """Импортирует Docker Compose файл."""
        filename, _ = QFileDialog.getOpenFileName(
            self, tr('menu_docker'), "",
            "YAML Files (*.yml *.yaml)"
        )

        if filename:
            manager = DependencyManager()
            added_obj, added_rel = manager.import_from_docker_compose(filename)

            if added_obj > 0:
                project = ProjectWindow(manager, None)
                project.setWindowTitle(f"{tr('import_prefix')} {os.path.basename(filename)}")
                sub = QMdiSubWindow()
                sub.setWidget(project)
                sub.setAttribute(Qt.WA_DeleteOnClose)
                self.mdi.addSubWindow(sub)
                sub.show()

                QMessageBox.information(
                    self, tr('import_complete'),
                    f"{tr('import_complete')}:\n"
                    f"{tr('imported_objects')} {added_obj}\n"
                    f"{tr('imported_rels')} {added_rel}"
                )
            else:
                QMessageBox.warning(self, tr('error'), tr('import_error'))

    def import_kubernetes(self) -> None:
        """Импортирует Kubernetes манифест."""
        filename, _ = QFileDialog.getOpenFileName(
            self, tr('menu_k8s'), "",
            "YAML Files (*.yml *.yaml)"
        )

        if filename:
            manager = DependencyManager()
            added_obj, added_rel = manager.import_from_kubernetes(filename)

            if added_obj > 0:
                project = ProjectWindow(manager, None)
                project.setWindowTitle(f"{tr('import_k8s_prefix')} {os.path.basename(filename)}")
                sub = QMdiSubWindow()
                sub.setWidget(project)
                sub.setAttribute(Qt.WA_DeleteOnClose)
                self.mdi.addSubWindow(sub)
                sub.show()

                QMessageBox.information(
                    self, tr('import_complete'),
                    f"{tr('import_complete')}:\n"
                    f"{tr('imported_objects')} {added_obj}\n"
                    f"{tr('imported_rels')} {added_rel}"
                )
            else:
                QMessageBox.warning(self, tr('error'), tr('import_error'))

    def import_godot_project(self) -> None:
        """Импортирует Godot проект с диалогом настройки фильтров."""
        # Сначала показываем диалог настройки импорта
        options_dialog = GodotImportDialog(self)
        if options_dialog.exec_() != QDialog.Accepted:
            return

        options = options_dialog.get_options()

        # Затем выбираем папку проекта
        folder = QFileDialog.getExistingDirectory(
            self,
            tr('select_godot_folder'),
            "",
            QFileDialog.ShowDirsOnly
        )

        if folder:
            try:
                from godot_analyzer import GodotDependencyAnalyzer

                analyzer = GodotDependencyAnalyzer(
                    folder,
                    exclude_textures=options['exclude_textures'],
                    exclude_audio=options['exclude_audio'],
                    exclude_fonts=options['exclude_fonts']
                )
                analyzer.analyze()

                manager = DependencyManager()
                added_obj, added_rel = analyzer.export_to_dependency_manager(manager)

                if added_obj > 0:
                    stats = analyzer.get_statistics()

                    project = ProjectWindow(manager, None)
                    project.setWindowTitle(f"{tr('import_godot_prefix')} {stats['project_name']}")
                    sub = QMdiSubWindow()
                    sub.setWidget(project)
                    sub.setAttribute(Qt.WA_DeleteOnClose)
                    self.mdi.addSubWindow(sub)
                    sub.show()

                    # Формируем статистику
                    stats_text = f"Проект: {stats['project_name']}\n\n"
                    stats_text += f"Ресурсов: {added_obj}\n"
                    stats_text += f"Зависимостей: {added_rel}\n\n"
                    stats_text += "По типам:\n"
                    for type_name, count in sorted(stats['by_type'].items()):
                        stats_text += f"  • {type_name}: {count}\n"

                    if stats['autoloads']:
                        stats_text += f"\nAutoload: {', '.join(stats['autoloads'])}"

                    # Показываем активные фильтры
                    filters = []
                    if stats['filters']['exclude_textures']:
                        filters.append('текстуры')
                    if stats['filters']['exclude_audio']:
                        filters.append('аудио')
                    if stats['filters']['exclude_fonts']:
                        filters.append('шрифты')
                    if filters:
                        stats_text += f"\n\n(Исключены: {', '.join(filters)})"

                    QMessageBox.information(self, tr('godot_import_stats'), stats_text)
                else:
                    QMessageBox.warning(self, tr('error'), tr('import_error'))

            except FileNotFoundError:
                QMessageBox.critical(
                    self, tr('error'),
                    "Файл godot_analyzer.py не найден!\n"
                    "Убедитесь, что он находится в той же папке."
                )
            except ValueError as e:
                QMessageBox.critical(self, tr('error'), str(e))
            except Exception as e:
                QMessageBox.critical(self, tr('error'), f"Ошибка импорта: {str(e)}")

    def save_project(self) -> None:
        """Сохраняет текущий проект."""
        window = self.mdi.activeSubWindow()
        if not window:
            return

        project = window.widget()

        if project.current_file:
            if project.manager.save_to_file(project.current_file):
                project.mark_saved()
                self.statusBar().showMessage(tr('saved'), 3000)
            else:
                QMessageBox.critical(self, tr('error'), tr('save_error'))
        else:
            self.save_project_as()

    def save_project_as(self) -> None:
        """Сохраняет текущий проект в новый файл."""
        window = self.mdi.activeSubWindow()
        if not window:
            return

        project = window.widget()

        filename, _ = QFileDialog.getSaveFileName(
            self, tr('save_project'),
            project.current_file or "infrastructure.json",
            "JSON Files (*.json)"
        )

        if filename:
            if project.manager.save_to_file(filename):
                project.current_file = filename
                project.mark_saved()
                window.setWindowTitle(f"{tr('project')}: {os.path.basename(filename)}")
                self.statusBar().showMessage(f"{tr('saved')}: {filename}", 3000)
            else:
                QMessageBox.critical(self, tr('error'), tr('save_error'))


# =============================================================================
# ТОЧКА ВХОДА
# =============================================================================

def main() -> None:
    """Главная функция запуска приложения."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    font = QFont("DejaVu Sans", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
