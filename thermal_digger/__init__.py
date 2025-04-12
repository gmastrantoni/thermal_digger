"""
Thermal Analyzer
--------------

A tool for analyzing thermal images and time series data.
"""

from thermal_digger.utils.config import config
from thermal_digger.thermal_data import ThermalDataHandler
from thermal_digger.thermal_plot import ThermalPlotter
from thermal_digger.utils.camera_types import CameraType
from image_analysis.edge_detector import ThermalEdgeDetector, EdgeDetectionMethod
from image_analysis.comparison_detector import ThermalComparisonDetector, ComparisonMethod


__version__ = config.VERSION
__author__ = "Giandomenico Mastrantoni"
__email__ = "giandomenico.mastrantoni@uniroma1.it"

__all__ = [
    'ThermalDataHandler', 
    'ThermalPlotter', 
    'config', 
    'CameraType', 
    'ThermalEdgeDetector', 
    'EdgeDetectionMethod',
    'ThermalComparisonDetector',
    'ComparisonMethod'
]