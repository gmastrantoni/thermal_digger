"""
Thermal Analyzer
--------------

A tool for analyzing thermal images and time series data.
"""

from thermal_analyzer.utils.config import config
from thermal_analyzer.thermal_data import ThermalDataHandler
from thermal_analyzer.thermal_plot import ThermalPlotter
from thermal_analyzer.utils.camera_types import CameraType
from image_analysis.edge_detector import EdgeDetector

__version__ = config.VERSION
__author__ = "Giandomenico Mastrantoni"
__email__ = "giandomenico.mastrantoni@uniroma1.it"

__all__ = ['ThermalDataHandler', 'ThermalPlotter', 'config', "CameraType", "EdgeDetector"]
