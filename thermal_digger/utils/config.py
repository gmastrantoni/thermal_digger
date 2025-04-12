"""Configuration settings for the Thermal Digger application."""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class Config:
    # Application settings
    APP_NAME: str = "Thermal Digger"
    VERSION: str = "2.0.1"
    
    # Development info
    DEVELOPER: str = "Giandomenico Mastrantoni"
    ORGANIZATION: str = "" #"Sapienza University of Rome - CERI Research Centre"
    COPYRIGHT: str = "© 2025"
    WEBSITE: str = ""
    
    # Paths
    RESOURCES_DIR: str = os.path.join(os.path.dirname(__file__), "..", "resources")
    # LOGO_PATH: str = os.path.join(RESOURCES_DIR, "app_icon.png")
    ICON_PATH: str = os.path.join(RESOURCES_DIR, "thermal_digger_icon.png")  # Main icon (PNG)
    ICON_ICO_PATH: str = os.path.join(RESOURCES_DIR, "thermal_digger_icon.ico")  # Windows icon

    # File settings
    SUPPORTED_EXTENSIONS: tuple = (".csv",)
    METADATA_ROWS: int = 8
    
    # Plot settings
    COLORMAP: str = "binary_r"
    FIGURE_DPI: int = 600
    
    # Export settings
    DEFAULT_EXPORT_DIR: str = os.path.expanduser("~/Documents/ThermalAnalyzer")
    
    # Window settings
    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 800
    
    @classmethod
    def ensure_export_dir(cls) -> None:
        """Ensure the export directory exists."""
        os.makedirs(cls.DEFAULT_EXPORT_DIR, exist_ok=True)
    
    @classmethod
    def get_export_path(cls, filename: str) -> str:
        """Get full path for export file."""
        cls.ensure_export_dir()
        return os.path.join(cls.DEFAULT_EXPORT_DIR, filename)

# Default configuration
default_config = Config()

# Optional: Load custom configuration from environment or file
def load_config() -> Config:
    """Load configuration from environment variables or config file."""
    config = Config()
    
    # Example: Override from environment variables
    if "THERMAL_ANALYZER_COLORMAP" in os.environ:
        config.COLORMAP = os.environ["THERMAL_ANALYZER_COLORMAP"]
    
    return config

# Active configuration
config = load_config()