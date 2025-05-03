from aqt.qt import *
from aqt import mw
from aqt.utils import showInfo, showCritical
import os
import webbrowser
import json

class ChangelogWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Pomodium Updates")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # Create text browser for changelog content
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(True)
        
        # Load and display changelog content
        changelog_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "CHANGELOG.md")
        if os.path.exists(changelog_path):
            with open(changelog_path, 'r', encoding='utf-8') as f:
                changelog_content = f.read()
                self.text_browser.setMarkdown(changelog_content)
        
        # Create social buttons layout
        social_layout = QHBoxLayout()
        
        # Ko-fi button
        kofi_button = QPushButton("☕ Support on Ko-fi")
        kofi_button.setStyleSheet("""
            QPushButton {
                background-color: #13C3FF;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00B9FF;
            }
        """)
        kofi_button.clicked.connect(lambda: webbrowser.open('https://ko-fi.com/ankizium'))
        
        # Twitter button
        twitter_button = QPushButton("🐦 Follow on Twitter")
        twitter_button.setStyleSheet("""
            QPushButton {
                background-color: #1DA1F2;
                color: white;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1991DA;
            }
        """)
        twitter_button.clicked.connect(lambda: webbrowser.open('https://x.com/Anki_fy'))
        
        # Add buttons to social layout
        social_layout.addWidget(kofi_button)
        social_layout.addWidget(twitter_button)
        
        # Close button
        close_button = QPushButton("Close")
        
        # Add widgets to layout
        layout.addWidget(QLabel("<h2>What's New in Pomodium?</h2>"))
        layout.addWidget(self.text_browser)
        layout.addLayout(social_layout)
        layout.addWidget(close_button)
        
        close_button.clicked.connect(self.accept)
        self.setLayout(layout)

def get_current_version():
    version_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "version.txt")
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            return f.read().strip()
    return "0.4"  # Default version if file doesn't exist

def get_last_shown_version():
    config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_files", "changelog_config.json")
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            try:
                config = json.load(f)
                return config.get('last_shown_version', '')
            except json.JSONDecodeError:
                return ''
    return ''

def set_last_shown_version(version):
    config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_files")
    os.makedirs(config_dir, exist_ok=True)
    config_file = os.path.join(config_dir, "changelog_config.json")
    config = {'last_shown_version': version}
    with open(config_file, 'w') as f:
        json.dump(config, f)

def show_changelog():
    current_version = get_current_version()
    last_shown_version = get_last_shown_version()
    
    # Only show changelog if it hasn't been shown for the current version
    if current_version != last_shown_version:
        dialog = ChangelogWindow(mw)
        dialog.exec()
        set_last_shown_version(current_version)
