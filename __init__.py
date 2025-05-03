from aqt import mw
from aqt.qt import *
from .src import gui
from .src import changelog

# Initialize the timer when Anki starts
gui.init_timer()

# Show changelog window
changelog.show_changelog()
