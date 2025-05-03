from PyQt6.QtCore import QTimer, QObject, pyqtSignal, pyqtSlot
import logging
from . import config

logging.basicConfig(level=logging.DEBUG)

class PomodoroTimer(QObject):
    timer_updated = pyqtSignal(int)
    timer_finished = pyqtSignal(bool)  # True if work session, False if break

    def __init__(self):
        super().__init__()
        self.load_config()
        self.is_work_session = True
        self.session_count = 0
        self.time_remaining = self.work_duration * 60
        self.is_running = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.setInterval(1000)  # Ensure 1-second intervals
        
    def load_config(self):
        conf = config.load_config()
        self.work_duration = conf.get('work_duration', 25)
        self.break_duration = conf.get('break_duration', 5)
        self.long_break_duration = conf.get('long_break_duration', 15)
        self.sessions_before_long_break = conf.get('sessions_before_long_break', 4)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.timer.start()

    def pause(self):
        if self.is_running:
            self.is_running = False
            self.timer.stop()

    def reset(self):
        """Reset the timer to initial state"""
        self.load_config()
        self.is_work_session = True
        self.session_count = 0
        self.time_remaining = self.work_duration * 60
        self.is_running = False
        self.timer.stop()
        self.timer_updated.emit(self.time_remaining)  # Emit signal to update display

    def start_break(self):
        """Start a break session"""
        logging.debug(f"Starting break session. Current session count: {self.session_count}")
        self.is_work_session = False
        if self.session_count >= self.sessions_before_long_break:
            logging.debug("Initiating long break.")
            self.time_remaining = self.long_break_duration * 60
            # session_count will be reset after the long break completes
        else:
            logging.debug("Initiating regular break.")
            self.time_remaining = self.break_duration * 60
        self.timer_updated.emit(self.time_remaining)
        self.is_running = False  # Reset running state
        self.start()  # Automatically start the break timer

    def start_work(self):
        """Start a work session"""
        self.is_work_session = True
        self.time_remaining = self.work_duration * 60
        self.timer_updated.emit(self.time_remaining)
        self.is_running = False  # Reset running state
        self.start()  # Automatically start the work timer

    @pyqtSlot()
    def update(self):
        """Update timer state"""
        logging.debug(f"Timer update called. Time remaining: {self.time_remaining}")
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.timer_updated.emit(self.time_remaining)
        else:
            if self.is_work_session:
                self.session_count += 1
                logging.debug(f"Work session complete. Incremented session count: {self.session_count}")
                self.timer_finished.emit(True)
                self.start_break()  # Automatically transition to break
            else:
                logging.debug("Break session complete. Transitioning to work session.")
                # Reset session count after long break completes
                if self.session_count >= self.sessions_before_long_break:
                    logging.debug("Long break complete. Resetting session count.")
                    self.session_count = 0
                self.timer_finished.emit(False)
                self.start_work()  # Automatically transition to work

    def get_time_string(self):
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        return f"{minutes:02d}:{seconds:02d}"

    def get_progress_percentage(self):
        if self.is_work_session:
            total_seconds = self.work_duration * 60
        else:
            if self.session_count >= self.sessions_before_long_break:
                total_seconds = self.long_break_duration * 60
            else:
                total_seconds = self.break_duration * 60
        
        if total_seconds == 0:
            return 0
        return int((total_seconds - self.time_remaining) / total_seconds * 100)

    def is_in_work_session(self):
        return self.is_work_session
