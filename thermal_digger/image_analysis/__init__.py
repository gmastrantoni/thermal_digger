"""
Image analysis modules for thermal data processing.
"""

from image_analysis.edge_detector import ThermalEdgeDetector, EdgeDetectionMethod
from image_analysis.comparison_detector import ThermalComparisonDetector, ComparisonMethod
from image_analysis.edge_gui import EdgeDetectionFrame
from image_analysis.comparison_gui import ComparisonAnalysisFrame

__all__ = [
    'ThermalEdgeDetector',
    'EdgeDetectionMethod',
    'ThermalComparisonDetector',
    'ComparisonMethod',
    'EdgeDetectionFrame',
    'ComparisonAnalysisFrame'
]
