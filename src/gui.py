from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout, QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QAction
from aqt import mw, gui_hooks
from aqt.qt import *
from aqt.sound import av_player
from aqt.main import MainWindowState
from . import timer
from . import settings
from . import config
import os
import json
import webbrowser
from datetime import datetime

class TimerWidget(QWidget):
    _instance = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = timer.PomodoroTimer()
        self.setup_ui()
        self.timer.timer_updated.connect(self.update_display)
        self.timer.timer_finished.connect(self.timer_complete)
        self.apply_theme()
        gui_hooks.theme_did_change.append(self.apply_theme)
        
    def setup_ui(self):
        # Main container layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        # Create a container widget for the bubble effect
        container = QWidget()
        container.setObjectName("container")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(15, 15, 15, 15)
        container_layout.setSpacing(10)

        # Top row with timer and todo button
        top_row = QHBoxLayout()
        
        # Timer display
        self.time_label = QLabel(self.timer.get_time_string())
        self.time_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
                padding: 5px 15px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 15px;
            }
        """)
        top_row.addWidget(self.time_label)
        
        # Control buttons container
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(5)
        
        # Control buttons
        self.toggle_button = QPushButton("▶")
        self.toggle_button.setFixedSize(36, 36)
        self.toggle_button.clicked.connect(self.toggle_timer)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #555;
                border-radius: 8px;
                padding: 5px;
                min-width: 30px;
                background-color: #4CAF50;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #45a049;
                border: 1px solid #666;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
        """)

        self.reset_button = QPushButton("⟳")
        self.reset_button.setFixedSize(36, 36)
        self.reset_button.clicked.connect(self.reset_timer)
        self.reset_button.setStyleSheet("""
            QPushButton {
                border: 1px solid #555;
                border-radius: 8px;
                padding: 5px;
                min-width: 30px;
                background-color: #2196F3;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #1976D2;
                border: 1px solid #666;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)

        buttons_layout.addWidget(self.toggle_button)
        buttons_layout.addWidget(self.reset_button)
        
        top_row.addWidget(buttons_container)
        container_layout.addLayout(top_row)
        
        main_layout.addWidget(container)
        self.setLayout(main_layout)
        
        # Set styles for the main container
        self.setStyleSheet("""
            QWidget#container {
                background: rgba(40, 40, 40, 0.95);
                border-radius: 20px;
            }
            TimerWidget {
                background: transparent;
            }
        """)
        
        self.adjustSize()
        
    def apply_theme(self):
        # Get Anki's theme (dark or light)
        from aqt.theme import theme_manager
        is_dark = theme_manager.night_mode

        if is_dark:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: transparent;
                }
                QPushButton {
                    border: 1px solid #555;
                    border-radius: 8px;
                    padding: 5px;
                    min-width: 30px;
                    background-color: #3d3d3d;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                    border: 1px solid #666;
                }
                QPushButton:pressed {
                    background-color: #434343;
                }
                QProgressBar {
                    border: none;
                    background-color: transparent;
                    height: 4px;
                }
                QProgressBar::chunk {
                    background-color: #2196F3;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: transparent;
                }
                QPushButton {
                    border: 1px solid #555;
                    border-radius: 8px;
                    padding: 5px;
                    min-width: 30px;
                    background-color: #e0e0e0;
                    color: #000000;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                    border: 1px solid #666;
                }
                QPushButton:pressed {
                    background-color: #c0c0c0;
                }
                QProgressBar {
                    border: none;
                    background-color: transparent;
                    height: 4px;
                }
                QProgressBar::chunk {
                    background-color: #2196F3;
                }
            """)

    def update_display(self, time_remaining=None):
        """Update the timer display with the current time"""
        if time_remaining is None:
            time_remaining = self.timer.time_remaining
        
        minutes = time_remaining // 60
        seconds = time_remaining % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        self.time_label.setText(time_str)
        
        if self.timer.is_in_work_session():
            self.time_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #ffffff;
                    padding: 5px 15px;
                    background: rgba(0, 0, 0, 0.2);
                    border-radius: 15px;
                }
            """)
        else:
            self.time_label.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #4CAF50;
                    padding: 5px 15px;
                    background: rgba(0, 0, 0, 0.2);
                    border-radius: 15px;
                }
            """)

    def toggle_timer(self):
        if self.timer.is_running:
            self.timer.pause()
            self.toggle_button.setText("▶")
        else:
            self.timer.start()
            self.toggle_button.setText("⏸")

    def reset_timer(self):
        self.timer.reset()
        self.toggle_button.setText("▶")
            
    def timer_complete(self, is_work_session):
        sound_file = os.path.join(os.path.dirname(__file__), "complete.wav")
        if os.path.exists(sound_file):
            av_player.play_file(sound_file)
            
        if is_work_session:
            msg = QMessageBox()
            msg.setWindowTitle("Work Session Complete!")
            msg.setText("Time for a break! Click OK to start your break session.")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.buttonClicked.connect(lambda: self.start_next_session(False))
            msg.exec()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Break Complete!")
            msg.setText("Break's over! Ready to start working?")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.buttonClicked.connect(lambda: self.start_next_session(True))
            msg.exec()
            
    def start_next_session(self, is_work):
        QTimer.singleShot(0, lambda: self._do_start_next_session(is_work))
        
    def _do_start_next_session(self, is_work):
        if is_work:
            self.timer.start_work()
        else:
            self.timer.start_break()
        self.timer.start()  # Explicitly start the timer
        self.toggle_button.setText("⏸")
        self.update_display(self.timer.time_remaining)  # Update display immediately

class PomodoroContainer:
    _instance = None
    
    def __init__(self):
        self.timer_widget = TimerWidget(mw)
        self.setup_position_timer()
        self.init_menu()
        gui_hooks.state_did_change.append(self.on_state_change)
        
    def on_state_change(self, new_state, old_state):
        # Load config to check if we should hide during review
        conf = config.load_config()
        hide_during_review = conf.get('hide_during_review', False)
        
        if new_state == "review" and hide_during_review:
            self.timer_widget.hide()
        else:
            self.timer_widget.show()
            
    def setup_position_timer(self):
        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.update_position)
        self.position_timer.start(100)  # Update every 100ms
        
    def update_position(self):
        if mw and mw.windowHandle():
            window_width = mw.width()
            self.timer_widget.move(window_width - self.timer_widget.width() - 10, 5)
            
    def init_menu(self):
        # Create action for settings
        self.settings_action = QAction("Pomodium", mw)
        self.settings_action.triggered.connect(self.show_settings)
        
        # Add to Tools menu
        mw.form.menuTools.addAction(self.settings_action)
        
    def show_settings(self):
        dialog = settings.PomodiumSettings(mw)
        dialog.exec()
        
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = PomodoroContainer()
        return cls._instance

class ProgressBar(QProgressBar):
    _instance = None
    
    @classmethod
    def get_instance(cls, parent=None):
        if cls._instance is None:
            cls._instance = cls(parent)
        return cls._instance
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setFixedHeight(3)
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: transparent;
                height: 4px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
        """)

def init_timer():
    # Create timer container if it doesn't exist
    if not hasattr(mw, 'pomodoro_container'):
        mw.pomodoro_container = PomodoroContainer.get_instance()
        
        # Ensure the container stays on top
        mw.pomodoro_container.timer_widget.raise_()
        mw.pomodoro_container.timer_widget.show()
    
    # Create and add progress bar
    progress_bar = ProgressBar.get_instance()
    if not hasattr(mw, 'pomodoro_progress'):
        mw.pomodoro_progress = progress_bar
        mw.mainLayout.addWidget(progress_bar)
    
    # Update progress bar when timer updates
    mw.pomodoro_container.timer_widget.timer.timer_updated.connect(
        lambda _: progress_bar.setValue(mw.pomodoro_container.timer_widget.timer.get_progress_percentage())
    )

def on_toolbar_did_init(links, toolbar):
    """Called when the toolbar is initialized."""
    init_timer()

# Register the toolbar initialization hook
gui_hooks.top_toolbar_did_init_links.append(on_toolbar_did_init)
