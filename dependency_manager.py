#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система управления зависимостями инфраструктуры
Dependency Infrastructure Manager - Enhanced Edition
Новое: переключение языков, улучшенное отображение связей, перетаскивание узлов
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
    QToolBar, QAction, QMenu, QColorDialog, QFormLayout, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QPoint
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QCursor, QFontDatabase
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle, RegularPolygon, FancyBboxPatch
import matplotlib.patches as mpatches
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')

# Настройка matplotlib
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False


# ==================== СИСТЕМА ЛОКАЛИЗАЦИИ ====================

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

        # Типы объектов
        'type_file': 'ФАЙЛ',
        'type_container': 'КОНТЕЙНЕР',
        'type_router': 'РОУТЕР',
        'type_switch': 'СВИТЧ',
        'type_server': 'СЕРВЕР',
        'type_database': 'БД',

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

        # Несохраненные изменения
        'unsaved_title': 'Несохранённые изменения',
        'unsaved_text': 'был изменён.',
        'unsaved_question': 'Хотите сохранить изменения?',
        'btn_save_changes': 'Сохранить',
        'btn_dont_save': 'Не сохранять',

        # Подсказки
        'hint_controls': 'Управление: Колесо мыши - зум | Кнопка перемещения / Shift+ЛКМ / СКМ - перемещение | ЛКМ - выбор | Перетаскивание узла - переместить',
        'hint_zoom_in': 'Приблизить (Zoom In)',
        'hint_zoom_out': 'Отдалить (Zoom Out)',
        'hint_pan': 'Режим перемещения (Shift+ЛКМ или СКМ)',

        # Цветовые схемы
        'scheme_dialog': 'Цветовая схема',
        'scheme_select': 'Выберите схему:',
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

        # Object types
        'type_file': 'FILE',
        'type_container': 'CONTAINER',
        'type_router': 'ROUTER',
        'type_switch': 'SWITCH',
        'type_server': 'SERVER',
        'type_database': 'DATABASE',

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
        'hint_controls': 'Controls: Mouse wheel - zoom | Pan button / Shift+LMB / MMB - pan | LMB - select | Drag node - move',
        'hint_zoom_in': 'Zoom In',
        'hint_zoom_out': 'Zoom Out',
        'hint_pan': 'Pan Mode (Shift+LMB or MMB)',

        # Color schemes
        'scheme_dialog': 'Color Scheme',
        'scheme_select': 'Select scheme:',
    }
}

# Текущий язык
CURRENT_LANGUAGE = 'ru'

def tr(key: str) -> str:
    """Функция перевода"""
    return TRANSLATIONS.get(CURRENT_LANGUAGE, {}).get(key, key)

def set_language(lang: str):
    """Установка языка"""
    global CURRENT_LANGUAGE
    if lang in TRANSLATIONS:
        CURRENT_LANGUAGE = lang


# ==================== ЦВЕТОВЫЕ СХЕМЫ ====================

COLOR_SCHEMES = {
    'default': {
        'file': '#FF6B9D',
        'docker_container': '#4ECDC4',
        'router': '#95E1D3',
        'switch': '#C77DFF',
        'server': '#FFD93D',
        'database': '#FF8C42'
    },
    'dark': {
        'file': '#E63946',
        'docker_container': '#457B9D',
        'router': '#2A9D8F',
        'switch': '#9B59B6',
        'server': '#F4A261',
        'database': '#E76F51'
    },
    'pastel': {
        'file': '#FFB3BA',
        'docker_container': '#BAE1FF',
        'router': '#BAFFC9',
        'switch': '#E0BBE4',
        'server': '#FFFFBA',
        'database': '#FFDFBA'
    },
    'vibrant': {
        'file': '#FF006E',
        'docker_container': '#00B4D8',
        'router': '#06FFA5',
        'switch': '#9D4EDD',
        'server': '#FFBE0B',
        'database': '#FF5400'
    }
}

# Unicode символы для типов объектов
NODE_ICONS = {
    'file': '▣',
    'docker_container': '◆',
    'router': '◈',
    'switch': '⚡',
    'server': '▦',
    'database': '⬢'
}

# Метки для списков
def get_node_label(obj_type: str) -> str:
    """Получить метку типа объекта на текущем языке"""
    labels = {
        'file': tr('type_file'),
        'docker_container': tr('type_container'),
        'router': tr('type_router'),
        'switch': tr('type_switch'),
        'server': tr('type_server'),
        'database': tr('type_database')
    }
    return labels.get(obj_type, obj_type.upper())


# ==================== КЛАССЫ ДАННЫХ ====================

class InfraObject:
    """Класс для представления объекта инфраструктуры"""

    VALID_TYPES = ['file', 'docker_container', 'router', 'switch', 'server', 'database']

    def __init__(self, obj_id: str, obj_type: str, name: str, properties: Dict = None):
        if obj_type not in self.VALID_TYPES:
            raise ValueError(f"Недопустимый тип объекта: {obj_type}")

        self.id = self._sanitize_id(obj_id)
        self.type = obj_type
        self.name = self._sanitize_string(name)
        self.properties = properties or {}
        self.created_at = datetime.now().isoformat()

    @staticmethod
    def _sanitize_string(text: str, max_length: int = 500) -> str:
        if not isinstance(text, str):
            return str(text)
        text = text[:max_length]
        dangerous_chars = ['<', '>', '"', "'", '`', '\x00']
        for char in dangerous_chars:
            text = text.replace(char, '')
        return text.strip()

    @staticmethod
    def _sanitize_id(obj_id: str) -> str:
        obj_id = str(obj_id)
        return ''.join(c for c in obj_id if c.isalnum() or c in ['-', '_'])[:100]

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'type': self.type,
            'name': self.name,
            'properties': self.properties,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'InfraObject':
        obj = cls(
            obj_id=data['id'],
            obj_type=data['type'],
            name=data['name'],
            properties=data.get('properties', {})
        )
        obj.created_at = data.get('created_at', datetime.now().isoformat())
        return obj

    def __str__(self) -> str:
        return f"[{self.type}] {self.name} (ID: {self.id})"


class Relationship:
    """Класс для представления связи между объектами"""

    VALID_TYPES = [
        'calls', 'sends_to', 'depends_on', 'connects_to',
        'uses', 'provides', 'routes_through'
    ]

    def __init__(self, source_id: str, target_id: str, rel_type: str, description: str = ""):
        if rel_type not in self.VALID_TYPES:
            raise ValueError(f"Недопустимый тип связи: {rel_type}")

        self.source_id = InfraObject._sanitize_id(source_id)
        self.target_id = InfraObject._sanitize_id(target_id)
        self.type = rel_type
        self.description = InfraObject._sanitize_string(description)
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'type': self.type,
            'description': self.description,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Relationship':
        rel = cls(
            source_id=data['source_id'],
            target_id=data['target_id'],
            rel_type=data['type'],
            description=data.get('description', '')
        )
        rel.created_at = data.get('created_at', datetime.now().isoformat())
        return rel

    def __str__(self) -> str:
        return f"{self.source_id} --[{self.type}]--> {self.target_id}"


class DependencyManager:
    """Менеджер зависимостей"""

    def __init__(self):
        self.objects: Dict[str, InfraObject] = {}
        self.relationships: List[Relationship] = []
        self.graph = nx.DiGraph()

    def add_object(self, obj: InfraObject) -> bool:
        if obj.id in self.objects:
            return False
        self.objects[obj.id] = obj
        self.graph.add_node(obj.id, **obj.to_dict())
        return True

    def update_object(self, obj_id: str, obj: InfraObject) -> bool:
        if obj_id not in self.objects:
            return False

        old_obj = self.objects[obj_id]
        del self.objects[obj_id]
        if self.graph.has_node(obj_id):
            self.graph.remove_node(obj_id)

        for rel in self.relationships:
            if rel.source_id == obj_id:
                rel.source_id = obj.id
            if rel.target_id == obj_id:
                rel.target_id = obj.id

        self.objects[obj.id] = obj
        self.graph.add_node(obj.id, **obj.to_dict())

        for rel in self.relationships:
            if rel.source_id == obj.id or rel.target_id == obj.id:
                if self.graph.has_edge(rel.source_id, rel.target_id):
                    self.graph.remove_edge(rel.source_id, rel.target_id)
                self.graph.add_edge(rel.source_id, rel.target_id, **rel.to_dict())

        return True

    def remove_object(self, obj_id: str) -> bool:
        if obj_id not in self.objects:
            return False

        self.relationships = [
            rel for rel in self.relationships
            if rel.source_id != obj_id and rel.target_id != obj_id
        ]

        del self.objects[obj_id]
        if self.graph.has_node(obj_id):
            self.graph.remove_node(obj_id)
        return True

    def add_relationship(self, rel: Relationship) -> bool:
        if rel.source_id not in self.objects or rel.target_id not in self.objects:
            return False

        for existing_rel in self.relationships:
            if (existing_rel.source_id == rel.source_id and
                existing_rel.target_id == rel.target_id and
                existing_rel.type == rel.type):
                return False

        self.relationships.append(rel)
        self.graph.add_edge(rel.source_id, rel.target_id, **rel.to_dict())
        return True

    def update_relationship(self, old_rel: Tuple[str, str, str], new_rel: Relationship) -> bool:
        source_id, target_id, rel_type = old_rel

        for i, rel in enumerate(self.relationships):
            if (rel.source_id == source_id and
                rel.target_id == target_id and
                rel.type == rel_type):
                del self.relationships[i]
                if self.graph.has_edge(source_id, target_id):
                    self.graph.remove_edge(source_id, target_id)
                break

        return self.add_relationship(new_rel)

    def remove_relationship(self, source_id: str, target_id: str, rel_type: str) -> bool:
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
        if obj_id not in self.objects:
            return []
        return [rel.target_id for rel in self.relationships if rel.source_id == obj_id]

    def get_dependents(self, obj_id: str) -> List[str]:
        if obj_id not in self.objects:
            return []
        return [rel.source_id for rel in self.relationships if rel.target_id == obj_id]

    def import_from_docker_compose(self, filename: str) -> Tuple[int, int]:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                compose = yaml.safe_load(f)

            services = compose.get('services', {})
            networks = compose.get('networks', {})
            volumes = compose.get('volumes', {})

            added_objects = 0
            added_relationships = 0

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

                depends_on = service_config.get('depends_on', [])
                if isinstance(depends_on, dict):
                    depends_on = list(depends_on.keys())

                for dep in depends_on:
                    dep_id = f"docker_{dep}"
                    rel = Relationship(obj_id, dep_id, 'depends_on', 'Docker Compose dependency')
                    if self.add_relationship(rel):
                        added_relationships += 1

                service_volumes = service_config.get('volumes', [])
                for vol in service_volumes:
                    if isinstance(vol, str) and ':' in vol:
                        vol_name = vol.split(':')[0]
                        if vol_name in volumes:
                            vol_id = f"vol_{vol_name}"
                            if vol_id not in self.objects:
                                vol_obj = InfraObject(vol_id, 'database', f"Volume: {vol_name}",
                                                     {'type': 'volume'})
                                if self.add_object(vol_obj):
                                    added_objects += 1

                            rel = Relationship(obj_id, vol_id, 'uses', 'Uses volume')
                            if self.add_relationship(rel):
                                added_relationships += 1

            return added_objects, added_relationships

        except Exception as e:
            print(f"Ошибка импорта Docker Compose: {e}")
            return 0, 0

    def import_from_kubernetes(self, filename: str) -> Tuple[int, int]:
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

                        obj = InfraObject(obj_id, 'docker_container',
                                        f"{name}/{container_name}", properties)
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

                    selector = spec.get('selector', {})
                    if 'app' in selector:
                        app_name = selector['app']
                        for obj_key in self.objects.keys():
                            if app_name in obj_key and 'k8s_' in obj_key and obj_key != obj_id:
                                rel = Relationship(obj_id, obj_key, 'routes_through',
                                                 'K8s Service routes to Pod')
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
        try:
            if not filename.endswith('.json'):
                filename += '.json'

            data = {
                'objects': [obj.to_dict() for obj in self.objects.values()],
                'relationships': [rel.to_dict() for rel in self.relationships],
                'metadata': {
                    'version': '1.0',
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
        try:
            if not os.path.exists(filename):
                return False

            if os.path.getsize(filename) > 10 * 1024 * 1024:
                raise ValueError("Файл слишком большой")

            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.objects.clear()
            self.relationships.clear()
            self.graph.clear()

            for obj_data in data.get('objects', []):
                obj = InfraObject.from_dict(obj_data)
                self.add_object(obj)

            for rel_data in data.get('relationships', []):
                rel = Relationship.from_dict(rel_data)
                self.add_relationship(rel)

            return True
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return False


# ==================== ДИАЛОГОВЫЕ ОКНА ====================

class ObjectDialog(QDialog):
    """Диалог добавления/редактирования объекта"""

    def __init__(self, parent=None, edit_obj: InfraObject = None):
        super().__init__(parent)
        self.edit_obj = edit_obj
        self.setWindowTitle(tr('dialog_edit_object') if edit_obj else tr('dialog_add_object'))
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel(tr('object_id')))
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText(tr('placeholder_id'))
        if self.edit_obj:
            self.id_input.setText(self.edit_obj.id)
        layout.addWidget(self.id_input)

        layout.addWidget(QLabel(tr('object_type')))
        self.type_combo = QComboBox()
        self.type_combo.addItems(InfraObject.VALID_TYPES)
        if self.edit_obj:
            index = self.type_combo.findText(self.edit_obj.type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        layout.addWidget(self.type_combo)

        layout.addWidget(QLabel(tr('object_name')))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(tr('placeholder_name'))
        if self.edit_obj:
            self.name_input.setText(self.edit_obj.name)
        layout.addWidget(self.name_input)

        layout.addWidget(QLabel(tr('object_description')))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText(tr('placeholder_desc'))
        if self.edit_obj and 'description' in self.edit_obj.properties:
            self.description_input.setPlainText(self.edit_obj.properties['description'])
        layout.addWidget(self.description_input)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton(tr('btn_save'))
        self.cancel_button = QPushButton(tr('btn_cancel'))

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_object(self) -> Optional[InfraObject]:
        obj_id = self.id_input.text().strip()
        obj_type = self.type_combo.currentText()
        name = self.name_input.text().strip()
        description = self.description_input.toPlainText().strip()

        if not obj_id or not name:
            return None

        properties = {}
        if description:
            properties['description'] = description

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
    """Диалог добавления/редактирования связи"""

    def __init__(self, objects: Dict[str, InfraObject], parent=None, edit_rel: Relationship = None):
        super().__init__(parent)
        self.objects = objects
        self.edit_rel = edit_rel
        self.setWindowTitle(tr('dialog_edit_relationship') if edit_rel else tr('dialog_add_relationship'))
        self.setMinimumWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel(tr('rel_source')))
        self.source_combo = QComboBox()
        for obj in self.objects.values():
            self.source_combo.addItem(f"{obj.name} ({obj.id})", obj.id)
        if self.edit_rel:
            index = self.source_combo.findData(self.edit_rel.source_id)
            if index >= 0:
                self.source_combo.setCurrentIndex(index)
        layout.addWidget(self.source_combo)

        layout.addWidget(QLabel(tr('rel_type')))
        self.type_combo = QComboBox()
        self.type_combo.addItems(Relationship.VALID_TYPES)
        if self.edit_rel:
            index = self.type_combo.findText(self.edit_rel.type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        layout.addWidget(self.type_combo)

        layout.addWidget(QLabel(tr('rel_target')))
        self.target_combo = QComboBox()
        for obj in self.objects.values():
            self.target_combo.addItem(f"{obj.name} ({obj.id})", obj.id)
        if self.edit_rel:
            index = self.target_combo.findData(self.edit_rel.target_id)
            if index >= 0:
                self.target_combo.setCurrentIndex(index)
        layout.addWidget(self.target_combo)

        layout.addWidget(QLabel(tr('rel_description')))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(60)
        if self.edit_rel:
            self.description_input.setPlainText(self.edit_rel.description)
        layout.addWidget(self.description_input)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton(tr('btn_save'))
        self.cancel_button = QPushButton(tr('btn_cancel'))

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_relationship(self) -> Optional[Relationship]:
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


# ==================== ГРАФ ХОЛСТ С ПЕРЕТАСКИВАНИЕМ ====================

class GraphCanvas(FigureCanvas):
    """Холст для отрисовки графа с возможностью перетаскивания узлов"""

    node_clicked = pyqtSignal(str)
    edge_clicked = pyqtSignal(str, str, str)

    def __init__(self, parent=None):
        self.figure = Figure(figsize=(10, 7), facecolor='#F8F9FA')
        super().__init__(self.figure)
        self.setParent(parent)
        self.ax = self.figure.add_subplot(111)
        self.manager = None
        self.pos = None
        self.highlighted_edge = None
        self.color_scheme = 'default'
        self.node_positions = {}
        self.edge_positions = {}
        self.node_radius = 0.15

        # Переменные для панорамирования
        self.pan_active = False
        self.pan_mode_enabled = False
        self.pan_start_x = None
        self.pan_start_y = None
        self.pan_xlim = None
        self.pan_ylim = None

        # Переменные для перетаскивания узлов
        self.dragging_node = None
        self.drag_start_pos = None

        self.mpl_connect('button_press_event', self.on_mouse_press)
        self.mpl_connect('button_release_event', self.on_mouse_release)
        self.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.mpl_connect('scroll_event', self.on_scroll)

    def set_color_scheme(self, scheme: str):
        if scheme in COLOR_SCHEMES:
            self.color_scheme = scheme

    def on_mouse_press(self, event):
        if event.inaxes != self.ax or not self.manager:
            return

        # Проверяем, нажата ли кнопка для панорамирования
        if event.button == 2 or (event.button == 1 and event.key == 'shift') or (event.button == 1 and self.pan_mode_enabled):
            self.pan_active = True
            self.pan_start_x = event.xdata
            self.pan_start_y = event.ydata
            self.pan_xlim = self.ax.get_xlim()
            self.pan_ylim = self.ax.get_ylim()
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            return

        # Проверяем клик по узлу для перетаскивания (левая кнопка)
        if event.button == 1:
            click_x, click_y = event.xdata, event.ydata

            # Поиск узла под курсором
            for node_id, (x, y) in self.pos.items():
                distance = ((click_x - x) ** 2 + (click_y - y) ** 2) ** 0.5
                if distance < self.node_radius:
                    # Начинаем перетаскивание узла
                    self.dragging_node = node_id
                    self.drag_start_pos = (click_x, click_y)
                    self.setCursor(QCursor(Qt.ClosedHandCursor))
                    return

    def on_mouse_release(self, event):
        if self.pan_active:
            self.pan_active = False
            self.setCursor(QCursor(Qt.ArrowCursor))

        if self.dragging_node:
            # Завершаем перетаскивание
            self.dragging_node = None
            self.drag_start_pos = None
            self.setCursor(QCursor(Qt.ArrowCursor))

            # Проверяем, был ли это клик (без перемещения)
            if event.inaxes == self.ax:
                click_x, click_y = event.xdata, event.ydata
                for node_id, (x, y) in self.pos.items():
                    distance = ((click_x - x) ** 2 + (click_y - y) ** 2) ** 0.5
                    if distance < self.node_radius:
                        self.node_clicked.emit(node_id)
                        return

    def on_mouse_move(self, event):
        if event.inaxes != self.ax:
            return

        # Панорамирование
        if self.pan_active and self.pan_start_x is not None and self.pan_start_y is not None:
            dx = event.xdata - self.pan_start_x
            dy = event.ydata - self.pan_start_y

            new_xlim = [self.pan_xlim[0] - dx, self.pan_xlim[1] - dx]
            new_ylim = [self.pan_ylim[0] - dy, self.pan_ylim[1] - dy]

            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)
            self.draw()
            return

        # Перетаскивание узла
        if self.dragging_node and event.xdata and event.ydata:
            # Обновляем позицию узла
            self.pos[self.dragging_node] = (event.xdata, event.ydata)
            # Перерисовываем граф
            self.plot_graph(self.manager)

    def on_scroll(self, event):
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

        new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

        relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
        rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

        new_xlim = [xdata - new_width * (1 - relx), xdata + new_width * relx]
        new_ylim = [ydata - new_height * (1 - rely), ydata + new_height * rely]

        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)
        self.draw()

    def highlight_edge(self, source_id: str, target_id: str):
        self.highlighted_edge = (source_id, target_id)
        self.plot_graph(self.manager)

    def clear_highlight(self):
        self.highlighted_edge = None
        self.plot_graph(self.manager)

    def export_to_png(self, filename: str) -> bool:
        try:
            self.figure.savefig(filename, dpi=300, bbox_inches='tight',
                              facecolor='white', edgecolor='none')
            return True
        except Exception as e:
            print(f"Ошибка экспорта: {e}")
            return False

    def reset_view(self):
        if self.pos and len(self.pos) > 0:
            x_values = [pos[0] for pos in self.pos.values()]
            y_values = [pos[1] for pos in self.pos.values()]
            margin = 0.3
            self.ax.set_xlim(min(x_values) - margin, max(x_values) + margin)
            self.ax.set_ylim(min(y_values) - margin, max(y_values) + margin)
            self.draw()

    def zoom_by_factor(self, factor):
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
        self.draw()

    def set_pan_mode(self, enabled):
        self.pan_mode_enabled = enabled
        if enabled:
            self.setCursor(QCursor(Qt.OpenHandCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

    def plot_graph(self, manager: DependencyManager):
        self.ax.clear()
        self.manager = manager
        self.edge_positions.clear()

        if len(manager.objects) == 0:
            self.ax.text(0.5, 0.5, tr('no_objects'),
                        ha='center', va='center', fontsize=14, color='#6C757D')
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 1)
            self.ax.axis('off')
            self.ax.set_facecolor('#F8F9FA')
            self.draw()
            return

        G = manager.graph
        color_map = COLOR_SCHEMES[self.color_scheme]

        # Используем существующие позиции или создаем новые
        if self.pos is None or len(self.pos) != len(G.nodes()):
            try:
                self.pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
            except:
                self.pos = nx.circular_layout(G)

        # Рисуем стрелки
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

                    start_x = x1 + dx_norm * self.node_radius
                    start_y = y1 + dy_norm * self.node_radius
                    end_x = x2 - dx_norm * self.node_radius
                    end_y = y2 - dy_norm * self.node_radius

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

                    mid_x = (start_x + end_x) / 2
                    mid_y = (start_y + end_y) / 2
                    self.edge_positions[(rel.source_id, rel.target_id)] = (mid_x, mid_y)

        # Рисуем узлы с разными формами
        for node, (x, y) in self.pos.items():
            obj = manager.objects.get(node)
            color = color_map.get(obj.type, '#ADB5BD') if obj else '#ADB5BD'

            if obj:
                if obj.type == 'file':
                    rect = Rectangle((x - self.node_radius * 0.8, y - self.node_radius),
                                    self.node_radius * 1.6, self.node_radius * 2,
                                    color=color, ec='#212529', linewidth=2.5,
                                    alpha=0.9, zorder=3)
                    self.ax.add_patch(rect)
                elif obj.type == 'database':
                    from matplotlib.patches import Ellipse
                    ellipse = Ellipse((x, y), self.node_radius * 2, self.node_radius * 2.5,
                                    color=color, ec='#212529', linewidth=2.5,
                                    alpha=0.9, zorder=3)
                    self.ax.add_patch(ellipse)
                elif obj.type in ['router', 'switch']:
                    diamond = RegularPolygon((x, y), 4, radius=self.node_radius * 1.3,
                                           orientation=np.pi/4,
                                           color=color, ec='#212529', linewidth=2.5,
                                           alpha=0.9, zorder=3)
                    self.ax.add_patch(diamond)
                elif obj.type == 'server':
                    rect = FancyBboxPatch((x - self.node_radius, y - self.node_radius * 0.8),
                                        self.node_radius * 2, self.node_radius * 1.6,
                                        boxstyle="round,pad=0.02",
                                        color=color, ec='#212529', linewidth=2.5,
                                        alpha=0.9, zorder=3)
                    self.ax.add_patch(rect)
                else:  # docker_container
                    circle = Circle((x, y), self.node_radius,
                                  color=color, ec='#212529', linewidth=2.5,
                                  alpha=0.9, zorder=3)
                    self.ax.add_patch(circle)

        # Рисуем иконки и названия узлов
        for node, (x, y) in self.pos.items():
            obj = manager.objects.get(node)
            if obj:
                icon = NODE_ICONS.get(obj.type, '●')
                self.ax.text(x, y + 0.05, icon, fontsize=22, fontweight='bold',
                           ha='center', va='center', zorder=5, color='#FFFFFF')

                name = obj.name if len(obj.name) <= 12 else obj.name[:10] + '..'
                self.ax.text(x, y - 0.22, name, fontsize=9, fontweight='bold',
                           ha='center', va='top', zorder=4,
                           bbox=dict(boxstyle='round,pad=0.4', facecolor='white',
                                   edgecolor='#DEE2E6', alpha=0.95, linewidth=1.5))

        # Рисуем подписи связей
        for rel in manager.relationships:
            if G.has_edge(rel.source_id, rel.target_id):
                x1, y1 = self.pos[rel.source_id]
                x2, y2 = self.pos[rel.target_id]

                label_x = x1 + (x2 - x1) * 0.5
                label_y = y1 + (y2 - y1) * 0.5

                dx = x2 - x1
                dy = y2 - y1
                dist = np.sqrt(dx**2 + dy**2)

                if dist > 0:
                    perp_x = -dy / dist * 0.05
                    perp_y = dx / dist * 0.05

                    label_x += perp_x
                    label_y += perp_y

                self.ax.text(label_x, label_y, rel.type, fontsize=7,
                           bbox=dict(boxstyle='round,pad=0.25', facecolor='#FFFFEB',
                                   edgecolor='#999999', alpha=0.9, linewidth=0.8),
                           ha='center', va='center', zorder=5,
                           color='#212529', fontweight='600')

        self.ax.set_title(tr('graph_title'), fontsize=18, fontweight='bold',
                         pad=20, color='#212529')
        self.ax.axis('off')
        self.ax.set_facecolor('#F8F9FA')

        if self.pos:
            x_values = [pos[0] for pos in self.pos.values()]
            y_values = [pos[1] for pos in self.pos.values()]
            margin = 0.3
            self.ax.set_xlim(min(x_values) - margin, max(x_values) + margin)
            self.ax.set_ylim(min(y_values) - margin, max(y_values) + margin)

        self.figure.tight_layout()
        self.draw()


# ==================== ОКНО ПРОЕКТА ====================

class ProjectWindow(QWidget):
    """Окно проекта"""

    language_changed = pyqtSignal()

    def __init__(self, manager: DependencyManager = None, filename: str = None):
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

    def apply_styles(self):
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
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:disabled {
                background-color: #CED4DA;
                color: #6C757D;
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
            }
            QListWidget::item:selected {
                background-color: #007BFF;
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
        """)

    def setup_ui(self):
        main_layout = QHBoxLayout(self)

        # Левая панель
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

        # Правая панель
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.visualization_label = QLabel(f"<b>{tr('visualization_title')}</b>")
        right_layout.addWidget(self.visualization_label)

        self.graph_canvas = GraphCanvas()
        self.graph_canvas.node_clicked.connect(self.on_graph_node_clicked)
        self.graph_canvas.edge_clicked.connect(self.on_graph_edge_clicked)

        # Тулбар навигации
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

        self.nav_label = QLabel(f"{tr('navigation')}")
        nav_layout.addWidget(self.nav_label)
        nav_layout.addWidget(self.zoom_in_btn)
        nav_layout.addWidget(self.zoom_out_btn)
        nav_layout.addWidget(self.pan_btn)
        nav_layout.addStretch()

        graph_container = QWidget()
        graph_container_layout = QVBoxLayout(graph_container)
        graph_container_layout.setContentsMargins(0, 0, 0, 0)
        graph_container_layout.addWidget(nav_toolbar)
        graph_container_layout.addWidget(self.graph_canvas)

        right_layout.addWidget(graph_container)

        self.info_label = QLabel(f"<i>{tr('hint_controls')}</i>")
        self.info_label.setStyleSheet("color: #6C757D; font-size: 9px;")
        right_layout.addWidget(self.info_label)

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

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

    def retranslate_ui(self):
        """Обновление всех текстов интерфейса"""
        # Обновляем вкладки
        self.tabs.setTabText(0, tr('tab_objects'))
        self.tabs.setTabText(1, tr('tab_relationships'))

        self.objects_label.setText(f"<b>{tr('objects_title')}</b>")
        self.relationships_label.setText(f"<b>{tr('relationships_title')}</b>")
        self.visualization_label.setText(f"<b>{tr('visualization_title')}</b>")
        self.nav_label.setText(f"{tr('navigation')}")
        self.info_label.setText(f"<i>{tr('hint_controls')}</i>")

        self.add_obj_btn.setText(tr('btn_add'))
        self.edit_obj_btn.setText(tr('btn_edit'))
        self.remove_obj_btn.setText(tr('btn_remove'))
        self.view_obj_btn.setText(tr('btn_view'))

        self.add_rel_btn.setText(tr('btn_add'))
        self.edit_rel_btn.setText(tr('btn_edit'))
        self.remove_rel_btn.setText(tr('btn_remove'))
        self.view_rel_btn.setText(tr('btn_view'))

        self.zoom_in_btn.setText(tr('btn_zoom_in'))
        self.zoom_out_btn.setText(tr('btn_zoom_out'))
        self.pan_btn.setText(tr('btn_pan'))
        self.refresh_btn.setText(tr('btn_refresh'))
        self.reset_zoom_btn.setText(tr('btn_reset_zoom'))
        self.color_btn.setText(tr('btn_color'))
        self.export_btn.setText(tr('btn_export'))

        # Обновляем заголовок окна
        if self.current_file:
            self.setWindowTitle(f"{tr('project')}: {os.path.basename(self.current_file)}")
        else:
            self.setWindowTitle(tr('new_project'))

        # Обновляем списки
        self.update_ui()

    def update_ui(self):
        """Обновление интерфейса"""
        self.objects_list.clear()
        for obj in self.manager.objects.values():
            label = get_node_label(obj.type)
            icon = NODE_ICONS.get(obj.type, '●')
            item = QListWidgetItem(f"{icon} {label}: {obj.name}")
            item.setData(Qt.UserRole, obj.id)
            self.objects_list.addItem(item)

        self.relationships_list.clear()
        for rel in self.manager.relationships:
            source_name = self.manager.objects[rel.source_id].name
            target_name = self.manager.objects[rel.target_id].name
            # Улучшенное отображение с типом связи в квадратных скобках
            text = f"{source_name} → [{rel.type}] → {target_name}"
            item = QListWidgetItem(text)
            # Делаем тип связи жирным через HTML (для списка используется plaintext)
            item.setData(Qt.UserRole, (rel.source_id, rel.target_id, rel.type))
            self.relationships_list.addItem(item)

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

    def mark_modified(self):
        self.modified = True
        title = self.windowTitle()
        if not title.endswith('*'):
            self.setWindowTitle(title + ' *')

    def mark_saved(self):
        self.modified = False
        title = self.windowTitle()
        if title.endswith(' *'):
            self.setWindowTitle(title[:-2])

    def add_object(self):
        dialog = ObjectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            obj = dialog.get_object()
            if obj and self.manager.add_object(obj):
                self.mark_modified()
                self.update_ui()

    def edit_object(self):
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

    def remove_object(self):
        current_item = self.objects_list.currentItem()
        if not current_item:
            return

        obj_id = current_item.data(Qt.UserRole)
        obj = self.manager.objects.get(obj_id)

        reply = QMessageBox.question(self, tr('confirm'),
                                     f"{tr('confirm_delete_obj')} '{obj.name}'?",
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes and self.manager.remove_object(obj_id):
            self.mark_modified()
            self.update_ui()

    def view_object(self):
        current_item = self.objects_list.currentItem()
        if not current_item:
            return

        obj_id = current_item.data(Qt.UserRole)
        self.show_object_info(obj_id)

    def show_object_info(self, obj_id: str):
        obj = self.manager.objects.get(obj_id)
        if not obj:
            return

        dependencies = self.manager.get_dependencies(obj_id)
        dependents = self.manager.get_dependents(obj_id)

        label = get_node_label(obj.type)
        icon = NODE_ICONS.get(obj.type, '●')
        info = f"<h3>{icon} {label}: {tr('info_object')}</h3>"
        info += f"<b>{tr('info_id')}</b> {obj.id}<br>"
        info += f"<b>{tr('info_type')}</b> {obj.type}<br>"
        info += f"<b>{tr('info_name')}</b> {obj.name}<br>"
        info += f"<b>{tr('info_created')}</b> {obj.created_at[:19]}<br>"

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
        msg.exec_()

    def on_object_selected(self, item):
        pass

    def add_relationship(self):
        if len(self.manager.objects) < 2:
            QMessageBox.warning(self, tr('error'), tr('need_2_objects'))
            return

        dialog = RelationshipDialog(self.manager.objects, self)
        if dialog.exec_() == QDialog.Accepted:
            rel = dialog.get_relationship()
            if rel and self.manager.add_relationship(rel):
                self.mark_modified()
                self.update_ui()

    def edit_relationship(self):
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

    def remove_relationship(self):
        current_item = self.relationships_list.currentItem()
        if not current_item:
            return

        source_id, target_id, rel_type = current_item.data(Qt.UserRole)

        reply = QMessageBox.question(self, tr('confirm'),
                                     tr('confirm_delete_rel'),
                                     QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.manager.remove_relationship(source_id, target_id, rel_type):
                self.mark_modified()
                self.graph_canvas.clear_highlight()
                self.update_ui()

    def view_relationship(self):
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
        info += f"<b>{tr('info_created_at')}</b> {rel.created_at[:19]}<br>"

        if rel.description:
            info += f"<br><b>{tr('info_description')}</b><br>{rel.description}"

        msg = QMessageBox(self)
        msg.setWindowTitle(tr('info_relationship'))
        msg.setTextFormat(Qt.RichText)
        msg.setText(info)
        msg.exec_()

    def on_relationship_selected(self, item):
        source_id, target_id, _ = item.data(Qt.UserRole)
        self.graph_canvas.highlight_edge(source_id, target_id)

    def on_graph_node_clicked(self, node_id: str):
        self.show_object_info(node_id)

    def on_graph_edge_clicked(self, source_id: str, target_id: str, rel_type: str):
        for i in range(self.relationships_list.count()):
            item = self.relationships_list.item(i)
            s, t, r = item.data(Qt.UserRole)
            if s == source_id and t == target_id and r == rel_type:
                self.relationships_list.setCurrentItem(item)
                self.graph_canvas.highlight_edge(source_id, target_id)
                break

    def refresh_graph(self):
        self.graph_canvas.plot_graph(self.manager)

    def reset_zoom(self):
        self.graph_canvas.reset_view()

    def zoom_in(self):
        self.graph_canvas.zoom_by_factor(0.8)

    def zoom_out(self):
        self.graph_canvas.zoom_by_factor(1.25)

    def toggle_pan_mode(self, checked):
        self.graph_canvas.set_pan_mode(checked)
        if checked:
            self.pan_btn.setStyleSheet("background-color: #28A745; color: white;")
        else:
            self.pan_btn.setStyleSheet("")

    def change_color_scheme(self):
        schemes = list(COLOR_SCHEMES.keys())
        scheme, ok = QInputDialog.getItem(self, tr('scheme_dialog'),
                                         tr('scheme_select'),
                                         schemes, 0, False)
        if ok:
            self.graph_canvas.set_color_scheme(scheme)
            self.refresh_graph()

    def export_graph(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, tr('export_dialog'),
            "infrastructure_graph.png",
            "PNG Files (*.png)"
        )

        if filename:
            if self.graph_canvas.export_to_png(filename):
                QMessageBox.information(self, tr('success'),
                                      f"{tr('export_success')}\n{filename}")
            else:
                QMessageBox.critical(self, tr('error'),
                                    tr('export_error'))


# ==================== ГЛАВНОЕ ОКНО ====================

class MainWindow(QMainWindow):
    """Главное окно"""

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.apply_styles()
        self.new_project()

    def apply_styles(self):
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

    def setup_ui(self):
        self.setWindowTitle(tr('app_title'))
        self.setGeometry(100, 100, 1400, 800)

        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)

        # Создаем меню
        self.create_menus()

        self.statusBar().showMessage(tr('ready'))

    def create_menus(self):
        """Создание меню"""
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

        import_menu = file_menu.addMenu(tr('menu_import'))

        import_compose = QAction(tr('menu_docker'), self)
        import_compose.triggered.connect(self.import_docker_compose)
        import_menu.addAction(import_compose)

        import_k8s = QAction(tr('menu_k8s'), self)
        import_k8s.triggered.connect(self.import_kubernetes)
        import_menu.addAction(import_k8s)

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

    def change_language(self, lang: str):
        """Смена языка интерфейса"""
        set_language(lang)

        # Обновляем меню
        self.create_menus()

        # Обновляем заголовок
        self.setWindowTitle(tr('app_title'))

        # Обновляем статусную строку
        self.statusBar().showMessage(tr('ready'))

        # Обновляем все открытые окна проектов
        for window in self.mdi.subWindowList():
            project = window.widget()
            if isinstance(project, ProjectWindow):
                project.retranslate_ui()

    def closeEvent(self, event):
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
                        QMessageBox.critical(self, tr('error'),
                                           f"{tr('save_error')} '{project_name}'")
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
                            QMessageBox.critical(self, tr('error'),
                                               tr('save_error'))
                            event.ignore()
                            return
                    else:
                        event.ignore()
                        return

        event.accept()

    def new_project(self):
        project = ProjectWindow()
        sub = QMdiSubWindow()
        sub.setWidget(project)
        sub.setAttribute(Qt.WA_DeleteOnClose)
        self.mdi.addSubWindow(sub)
        sub.show()
        self.statusBar().showMessage(tr('new_project_created'), 3000)

    def open_project(self):
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

    def import_docker_compose(self):
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

    def import_kubernetes(self):
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

    def save_project(self):
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

    def save_project_as(self):
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


def main():
    """Главная функция"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    font = QFont("DejaVu Sans", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
