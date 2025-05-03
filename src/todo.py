from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLineEdit, QListWidget, QListWidgetItem, QCheckBox, QLabel, 
                             QApplication, QMenu, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QPoint, QTimer
from PyQt6.QtGui import QIcon, QColor, QPainter, QPainterPath, QPen
import json
import os
from aqt.theme import theme_manager
from aqt import gui_hooks, mw
from datetime import datetime

class TaskItem(QWidget):
    deleted = pyqtSignal(QListWidgetItem)
    priorityChanged = pyqtSignal(QListWidgetItem, int)
    
    def __init__(self, text, priority=0, completed=False, parent=None):
        super().__init__(parent)
        self.setup_ui(text, priority, completed)
        
    def setup_ui(self, text, priority, completed):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(10)
        
        # Priority indicator
        self.priority_label = QLabel()
        self.set_priority_indicator(priority)
        layout.addWidget(self.priority_label)
        
        # Checkbox with text
        self.checkbox = QCheckBox(text)
        self.checkbox.setChecked(completed)
        self.apply_checkbox_style(completed)
        layout.addWidget(self.checkbox, 1)
        
        # Due date (if any)
        self.due_label = QLabel()
        self.due_label.setStyleSheet("color: rgba(255, 255, 255, 0.6);")
        layout.addWidget(self.due_label)
        
        # Delete button (hidden by default)
        self.delete_button = QPushButton("×")
        self.delete_button.setFixedSize(24, 24)
        self.delete_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #ff5555;
                font-size: 18px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover {
                color: #ff0000;
            }
        """)
        self.delete_button.hide()
        layout.addWidget(self.delete_button)
        
        # Setup animations
        self.setup_animations()
        
        # Connect signals
        self.checkbox.stateChanged.connect(self.on_checked_changed)
        self.delete_button.clicked.connect(self.on_delete_clicked)
        
    def setup_animations(self):
        # Fade effect for delete button
        self.delete_opacity = QGraphicsOpacityEffect(self)
        self.delete_button.setGraphicsEffect(self.delete_opacity)
        self.delete_anim = QPropertyAnimation(self.delete_opacity, b"opacity")
        self.delete_anim.setDuration(200)
        
    def set_priority_indicator(self, priority):
        colors = ["#808080", "#4CAF50", "#FFC107", "#F44336"]  # None, Low, Medium, High
        self.priority_label.setStyleSheet(f"""
            QLabel {{
                min-width: 12px;
                min-height: 12px;
                max-width: 12px;
                max-height: 12px;
                border-radius: 6px;
                background-color: {colors[priority]};
            }}
        """)
        
    def apply_checkbox_style(self, checked):
        text_color = "#ffffff" if theme_manager.night_mode else "#000000"
        dim_color = "rgba(255, 255, 255, 0.5)" if theme_manager.night_mode else "rgba(0, 0, 0, 0.5)"
        color = dim_color if checked else text_color
        
        self.checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: {color};
                font-size: 14px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 22px;
                height: 22px;
                border-radius: 11px;
                border: 2px solid #4CAF50;
            }}
            QCheckBox::indicator:checked {{
                background: #4CAF50;
                image: url(check.png);
            }}
        """)
        
    def enterEvent(self, event):
        self.delete_button.show()
        self.delete_anim.setStartValue(0)
        self.delete_anim.setEndValue(1)
        self.delete_anim.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.delete_anim.setStartValue(1)
        self.delete_anim.setEndValue(0)
        self.delete_anim.finished.connect(self.delete_button.hide)
        self.delete_anim.start()
        super().leaveEvent(event)
        
    def on_checked_changed(self, state):
        self.apply_checkbox_style(state == Qt.CheckState.Checked.value)
        
    def on_delete_clicked(self):
        parent_item = self.parent().parent()
        if isinstance(parent_item, QListWidgetItem):
            self.deleted.emit(parent_item)

class TodoList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.apply_theme()
        gui_hooks.profile_did_open.append(self.load_todos)
        gui_hooks.theme_did_change.append(self.apply_theme)
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Window styling
        self.setStyleSheet("""
            TodoList {
                background: rgba(40, 40, 40, 0.95);
                border: 2px solid #555555;
                border-radius: 25px;
            }
        """)

        # Title bar
        title_bar = self.create_title_bar()
        layout.addWidget(title_bar)
        
        # Input area
        input_widget = self.create_input_area()
        layout.addWidget(input_widget)
        
        # Todo list
        self.todo_list = QListWidget()
        self.todo_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.todo_list.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                background: rgba(60, 60, 60, 0.95);
                border: 1px solid #555555;
                border-radius: 10px;
                margin-bottom: 5px;
                min-height: 40px;
            }
            QListWidget::item:hover {
                background: rgba(80, 80, 80, 0.95);
                border: 1px solid #666666;
            }
            QListWidget::item:selected {
                background: rgba(70, 70, 70, 0.95);
                border: 1px solid #777777;
            }
        """)
        layout.addWidget(self.todo_list)
        
        # Window properties
        self.setMinimumWidth(350)
        self.setMaximumWidth(450)
        self.setMinimumHeight(500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
    def create_title_bar(self):
        title_bar = QWidget()
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(15, 8, 15, 8)
        
        # Title with icon
        title_label = QLabel("📝 Tasks")
        title_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 18px;
                font-weight: bold;
                padding: 2px 5px;
            }
        """)
        
        # Menu button
        menu_button = QPushButton("⋮")
        menu_button.setFixedSize(28, 28)
        menu_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #ffffff;
                font-size: 20px;
                font-weight: bold;
                padding: 0;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 14px;
            }
        """)
        menu_button.clicked.connect(self.show_menu)
        
        # Close button
        close_button = QPushButton("×")
        close_button.setFixedSize(28, 28)
        close_button.clicked.connect(self.hide)
        close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #ff5555;
                font-size: 20px;
                font-weight: bold;
                border-radius: 14px;
            }
            QPushButton:hover {
                background: rgba(255, 85, 85, 0.2);
                color: #ff0000;
            }
        """)
        
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(menu_button)
        title_bar_layout.addWidget(close_button)
        
        title_bar.setStyleSheet("""
            QWidget {
                background: rgba(45, 45, 45, 0.95);
                border-top-left-radius: 23px;
                border-top-right-radius: 23px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        return title_bar
        
    def create_input_area(self):
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(15, 10, 15, 10)
        input_layout.setSpacing(10)
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Add a new task...")
        self.task_input.returnPressed.connect(self.add_task)
        self.task_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.1);
                border: none;
                border-radius: 20px;
                padding: 10px 15px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                background: rgba(255, 255, 255, 0.15);
                outline: none;
            }
        """)
        
        add_button = QPushButton("+")
        add_button.setFixedSize(36, 36)
        add_button.clicked.connect(self.add_task)
        add_button.setStyleSheet("""
            QPushButton {
                background: #4CAF50;
                border: none;
                border-radius: 18px;
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #45a049;
            }
            QPushButton:pressed {
                background: #3d8b40;
            }
        """)
        
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(add_button)
        
        return input_widget
        
    def show_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2f2f31;
                border: 1px solid #555555;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 25px 8px 15px;
                border-radius: 4px;
                color: white;
            }
            QMenu::item:selected {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        
        # Add menu actions
        sort_action = menu.addAction("Sort by Priority")
        clear_completed = menu.addAction("Clear Completed")
        
        # Show menu and handle actions
        action = menu.exec(self.mapToGlobal(QPoint(self.width() - 50, 40)))
        if action == sort_action:
            self.sort_by_priority()
        elif action == clear_completed:
            self.clear_completed_tasks()
            
    def sort_by_priority(self):
        items = []
        for i in range(self.todo_list.count()):
            item = self.todo_list.item(i)
            widget = self.todo_list.itemWidget(item)
            priority = self.get_item_priority(widget)
            items.append((priority, item))
        
        items.sort(reverse=True)
        self.todo_list.clear()
        for _, item in items:
            self.todo_list.addItem(item)
            
    def clear_completed_tasks(self):
        for i in range(self.todo_list.count() - 1, -1, -1):
            item = self.todo_list.item(i)
            widget = self.todo_list.itemWidget(item)
            if widget.checkbox.isChecked():
                self.todo_list.takeItem(i)
        self.save_todos()
        
    def add_task(self):
        task_text = self.task_input.text().strip()
        if task_text:
            item = QListWidgetItem()
            task_widget = TaskItem(task_text)
            task_widget.deleted.connect(self.delete_task)
            
            item.setSizeHint(task_widget.sizeHint())
            self.todo_list.insertItem(0, item)
            self.todo_list.setItemWidget(item, task_widget)
            
            # Clear input and save
            self.task_input.clear()
            self.save_todos()
            
            # Animate new item
            self.animate_new_item(item)
            
    def animate_new_item(self, item):
        widget = self.todo_list.itemWidget(item)
        if widget:
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            
            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(300)
            anim.setStartValue(0)
            anim.setEndValue(1)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.start()
            
    def delete_task(self, item):
        row = self.todo_list.row(item)
        widget = self.todo_list.itemWidget(item)
        
        # Animate deletion
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(200)
        anim.setStartValue(1)
        anim.setEndValue(0)
        anim.finished.connect(lambda: self.finish_delete(row))
        anim.start()
        
    def finish_delete(self, row):
        self.todo_list.takeItem(row)
        self.save_todos()
        
    def save_todos(self):
        todos = []
        for i in range(self.todo_list.count()):
            item = self.todo_list.item(i)
            widget = self.todo_list.itemWidget(item)
            todos.append({
                'text': widget.checkbox.text(),
                'completed': widget.checkbox.isChecked(),
                'priority': self.get_item_priority(widget)
            })
        
        todos_path = self.get_user_data_path()
        try:
            os.makedirs(os.path.dirname(todos_path), exist_ok=True)
            with open(todos_path, 'w', encoding='utf-8') as f:
                json.dump(todos, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"Error saving todos: {str(e)}")
            
    def load_todos(self):
        self.ensure_user_files_dir()
        todos_path = self.get_user_data_path()
        
        if os.path.exists(todos_path):
            try:
                with open(todos_path, 'r', encoding='utf-8') as f:
                    todos = json.load(f)
                    self.todo_list.clear()
                    for todo in todos:
                        item = QListWidgetItem()
                        task_widget = TaskItem(
                            todo['text'],
                            todo.get('priority', 0),
                            todo.get('completed', False)
                        )
                        task_widget.deleted.connect(self.delete_task)
                        
                        item.setSizeHint(task_widget.sizeHint())
                        self.todo_list.addItem(item)
                        self.todo_list.setItemWidget(item, task_widget)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading todos: {str(e)}")
                
    def get_user_data_path(self):
        addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if not mw.col:
            return os.path.join(addon_dir, "user_files", "_pomodium_todos.json")
        return os.path.join(mw.col.media.dir(), "_pomodium_todos.json")
        
    def ensure_user_files_dir(self):
        addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        user_files_dir = os.path.join(addon_dir, "user_files")
        os.makedirs(user_files_dir, exist_ok=True)
        return user_files_dir
        
    def get_item_priority(self, widget):
        # Extract priority from the widget's priority indicator color
        style = widget.priority_label.styleSheet()
        if "#F44336" in style:  # High priority
            return 3
        elif "#FFC107" in style:  # Medium priority
            return 2
        elif "#4CAF50" in style:  # Low priority
            return 1
        return 0  # No priority
        
    def mousePressEvent(self, event):
        self.oldPos = event.globalPosition().toPoint()
        
    def mouseMoveEvent(self, event):
        delta = event.globalPosition().toPoint() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()
        
    def apply_theme(self):
        is_dark = theme_manager.night_mode
        text_color = "#ffffff" if is_dark else "#000000"
        bg_color = "#2f2f31" if is_dark else "#ffffff"
        border_color = "#3d3d3d" if is_dark else "#e0e0e0"
        
        self.setStyleSheet(f"""
            TodoList {{
                background: {bg_color};
                border: 2px solid {border_color};
                border-radius: 25px;
            }}
        """)
        
        # Update input field style
        self.task_input.setStyleSheet(f"""
            QLineEdit {{
                background: rgba({255 if is_dark else 0}, {255 if is_dark else 0}, {255 if is_dark else 0}, 0.1);
                border: none;
                border-radius: 20px;
                padding: 10px 15px;
                color: {text_color};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                background: rgba({255 if is_dark else 0}, {255 if is_dark else 0}, {255 if is_dark else 0}, 0.15);
            }}
        """)
        
        # Update list style
        self.todo_list.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                background: rgba({60 if is_dark else 245}, {60 if is_dark else 245}, {60 if is_dark else 245}, 0.95);
                border: 1px solid {border_color};
                border-radius: 10px;
                margin-bottom: 5px;
                min-height: 40px;
            }}
            QListWidget::item:hover {{
                background: rgba({80 if is_dark else 235}, {80 if is_dark else 235}, {80 if is_dark else 235}, 0.95);
            }}
            QListWidget::item:selected {{
                background: rgba({70 if is_dark else 240}, {70 if is_dark else 240}, {70 if is_dark else 240}, 0.95);
            }}
        """)
