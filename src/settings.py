from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QGroupBox, QFormLayout, QDialogButtonBox, QCheckBox, QWidget)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon, QDesktopServices
from aqt import mw, gui_hooks
from aqt.theme import theme_manager
from aqt.utils import showInfo, showCritical
import webbrowser
from . import config
from datetime import datetime

class PomodiumSettings(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = config.load_config()
        self.setup_ui()
        self.apply_theme()
        gui_hooks.theme_did_change.append(self.apply_theme)
        
    def setup_ui(self):
        self.setWindowTitle("Pomodium Settings")
        layout = QVBoxLayout(self)
        
        # Create title label with larger, bold blue text
        title_label = QLabel("Pomodium")
        title_label.setStyleSheet("""
            QLabel {
                color: #2196F3;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 20px;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Add spacing after title
        layout.addSpacing(20)
        
        # Timer Settings Group
        timer_group = QGroupBox("Timer Settings")
        timer_layout = QFormLayout()
        
        # Work Duration
        self.work_duration = QComboBox()
        for i in range(1, 61):
            self.work_duration.addItem(f"{i} minutes")
        work_duration = self.config.get('work_duration', 25)
        self.work_duration.setCurrentText(f"{work_duration} minutes")
        timer_layout.addRow("Work Duration:", self.work_duration)
        
        # Break Duration
        self.break_duration = QComboBox()
        for i in range(1, 31):
            self.break_duration.addItem(f"{i} minutes")
        break_duration = self.config.get('break_duration', 5)
        self.break_duration.setCurrentText(f"{break_duration} minutes")
        timer_layout.addRow("Break Duration:", self.break_duration)
        
        # Long Break Duration
        self.long_break_duration = QComboBox()
        for i in range(5, 61, 5):
            self.long_break_duration.addItem(f"{i} minutes")
        long_break_duration = self.config.get('long_break_duration', 15)
        self.long_break_duration.setCurrentText(f"{long_break_duration} minutes")
        timer_layout.addRow("Long Break Duration:", self.long_break_duration)
        
        # Sessions before Long Break
        self.sessions_before_long_break = QComboBox()
        for i in range(2, 9):
            self.sessions_before_long_break.addItem(f"{i} sessions")
        sessions = self.config.get('sessions_before_long_break', 4)
        self.sessions_before_long_break.setCurrentText(f"{sessions} sessions")
        timer_layout.addRow("Sessions before Long Break:", self.sessions_before_long_break)
        
        timer_group.setLayout(timer_layout)
        layout.addWidget(timer_group)
        
        # UI Settings Group
        ui_group = QGroupBox("UI Settings")
        ui_layout = QFormLayout()
        
        # Hide During Review Checkbox
        self.hide_during_review = QCheckBox()
        self.hide_during_review.setChecked(self.config.get('hide_during_review', False))
        ui_layout.addRow("Hide Timer During Review:", self.hide_during_review)
        
        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)
        
        # Add buttons container
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 10, 0, 10)
        buttons_layout.setSpacing(10)

        # Pro button with golden gradient
        pro_button = QPushButton("⭐ Upgrade to Pro")
        pro_button.setStyleSheet("""
            QPushButton {
                border: 2px solid #FFD700;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
                background-color: rgba(218, 165, 32, 0.2);
                color: #FFD700;
            }
            QPushButton:hover {
                background-color: rgba(218, 165, 32, 0.3);
                border: 2px solid #DAA520;
            }
            QPushButton:pressed {
                background-color: rgba(184, 134, 11, 0.4);
                border: 2px solid #B8860B;
            }
        """)
        pro_button.clicked.connect(lambda: webbrowser.open('https://ahmedbenarab.github.io/Pomodium-pro'))

        # Support Button with fixed style
        support_button = QPushButton("Support on Ko-fi")
        support_button.setStyleSheet("""
            QPushButton {
                background-color: #FF424D;
                color: white !important;
                border: none;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF1F2D;
            }
        """)
        support_button.clicked.connect(self.open_kofi)

        # Add buttons to layout
        buttons_layout.addWidget(pro_button)
        buttons_layout.addWidget(support_button)
        layout.addWidget(buttons_container)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def apply_theme(self):
        is_dark = theme_manager.night_mode

        if is_dark:
            self.setStyleSheet("""
                QDialog {
                    background-color: #2f2f31;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QGroupBox {
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    margin-top: 1em;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px;
                }
                QComboBox {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    padding: 5px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border: none;
                }
                QPushButton {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border: none;
                    padding: 8px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QLabel {
                    color: #000000;
                }
                QGroupBox {
                    border: 1px solid #d0d0d0;
                    border-radius: 5px;
                    margin-top: 1em;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 3px;
                }
                QComboBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #d0d0d0;
                    border-radius: 3px;
                    padding: 5px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border: none;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    color: #000000;
                    border: none;
                    padding: 8px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
            """)
        
    def save_settings(self):
        """Save settings to config file and reset timer"""
        new_config = {
            'work_duration': int(self.work_duration.currentText().split()[0]),
            'break_duration': int(self.break_duration.currentText().split()[0]),
            'long_break_duration': int(self.long_break_duration.currentText().split()[0]),
            'sessions_before_long_break': int(self.sessions_before_long_break.currentText().split()[0]),
            'hide_during_review': self.hide_during_review.isChecked()
        }
        
        config.save_config(new_config)
        
        # Reset the timer to apply new settings
        if hasattr(mw, 'pomodoro_container'):
            timer_widget = mw.pomodoro_container.timer_widget
            timer_widget.timer.reset()
            # Update display with the new work duration
            timer_widget.update_display(timer_widget.timer.time_remaining)
        
        self.accept()
        
    def open_kofi(self):
        """Open Ko-fi support page"""
        url = QUrl("https://ko-fi.com/ankizium")
        QDesktopServices.openUrl(url)
