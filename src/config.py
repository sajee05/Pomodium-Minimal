from typing import Dict
import os
from aqt import mw

def load_config() -> Dict:
    """Load configuration from Anki's addon manager"""
    config = mw.addonManager.getConfig(get_addon_name())  
    if config is None:
        config = get_default_config()
        save_config(config)
    return config

def save_config(config: Dict) -> None:
    """Save configuration using Anki's addon manager"""
    mw.addonManager.writeConfig(get_addon_name(), config)

def get_default_config() -> Dict:
    """Return default configuration values"""
    return {
        'work_duration': 25,
        'break_duration': 5,
        'long_break_duration': 15,
        'sessions_before_long_break': 4,
        'hide_during_review': False
    }

def get_addon_name() -> str:
    """Get the addon name from the directory structure"""
    return os.path.basename(os.path.dirname(os.path.dirname(__file__)))
