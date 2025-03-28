"""
Enhanced edge detection functionality for thermal image analysis.
"""

import numpy as np
from scipy import ndimage
from skimage import filters, feature, measure, color
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from enum import Enum, auto
from utils.config import config

class EdgeDetectionMethod(Enum):
    """Enumeration of supported edge detection methods."""
    SOBEL = auto()
    CANNY = auto()
    PREWITT = auto()
    ROBERTS = auto()
    SCHARR = auto()
    
    def __str__(self):
        """Return the string representation of the method."""
        return self.name.capitalize()

class ThermalEdgeDetector:
    """
    Specialized thermal edge detector with enhanced capabilities.
    """
    
    def __init__(self):
        """Initialize the ThermalEdgeDetector."""
        pass
    
    def detect_edges(self, thermal_data, method='sobel', threshold=1.5, sigma=1.0, 
                   low_threshold=None, high_threshold=None):
        """
        Detect edges in thermal data representing abrupt temperature changes.
        
        Parameters:
            thermal_data (numpy.ndarray): 2D array of temperature values
            method (str): Edge detection method ('sobel', 'canny', 'prewitt', 'roberts', 'scharr')
            threshold (float): Threshold for edge detection
            sigma (float): Gaussian smoothing sigma (for noise reduction)
            low_threshold (float, optional): Low threshold for Canny detection
            high_threshold (float, optional): High threshold for Canny detection
            
        Returns:
            tuple: (edges, gradient_magnitude, edge_directions)
                edges: Binary mask where edges are marked as True
                gradient_magnitude: Magnitude of temperature gradient
                edge_directions: Direction of temperature gradient (radians)
        """
        # Apply optional Gaussian smoothing to reduce noise
        if sigma > 0:
            smoothed_data = ndimage.gaussian_filter(thermal_data, sigma=sigma)
        else:
            smoothed_data = thermal_data
        
        # Set default thresholds for Canny if not provided
        if low_threshold is None:
            low_threshold = 0.4 * threshold
        if high_threshold is None:
            high_threshold = threshold
            
        # Apply edge detection based on selected method
        edges = None
        gradient_magnitude = None
        edge_directions = None
        
        if method.lower() == 'sobel':
            # Calculate gradients using Sobel operators
            gradient_y = ndimage.sobel(smoothed_data, axis=0, mode='reflect')
            gradient_x = ndimage.sobel(smoothed_data, axis=1, mode='reflect')
            
            # Calculate gradient magnitude and direction
            gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
            edge_directions = np.arctan2(gradient_y, gradient_x)
            
            # Apply threshold to find significant edges
            edges = gradient_magnitude > threshold
            
        elif method.lower() == 'canny':
            # Use Canny edge detector
            edges = feature.canny(
                smoothed_data, 
                sigma=sigma, 
                low_threshold=low_threshold, 
                high_threshold=high_threshold
            )
            
            # Calculate gradients for visualization
            gradient_y = ndimage.sobel(smoothed_data, axis=0, mode='reflect')
            gradient_x = ndimage.sobel(smoothed_data, axis=1, mode='reflect')
            gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
            edge_directions = np.arctan2(gradient_y, gradient_x)
            
        elif method.lower() == 'prewitt':
            # Calculate gradients using Prewitt operator
            gradient_y = filters.prewitt_v(smoothed_data)
            gradient_x = filters.prewitt_h(smoothed_data)
            
            # Calculate gradient magnitude and direction
            gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
            edge_directions = np.arctan2(gradient_y, gradient_x)
            
            # Apply threshold to find significant edges
            edges = gradient_magnitude > threshold
            
        elif method.lower() == 'roberts':
            # Calculate gradients using Roberts Cross operator
            gradient1 = filters.roberts_pos_diag(smoothed_data)
            gradient2 = filters.roberts_neg_diag(smoothed_data)
            
            # Calculate gradient magnitude
            gradient_magnitude = np.sqrt(gradient1**2 + gradient2**2)
            
            # Calculate approximate directions
            edge_directions = np.arctan2(gradient2, gradient1)
            
            # Apply threshold to find significant edges
            edges = gradient_magnitude > threshold
            
        elif method.lower() == 'scharr':
            # Calculate gradients using Scharr operator
            gradient_y = filters.scharr_v(smoothed_data)
            gradient_x = filters.scharr_h(smoothed_data)
            
            # Calculate gradient magnitude and direction
            gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
            edge_directions = np.arctan2(gradient_y, gradient_x)
            
            # Apply threshold to find significant edges
            edges = gradient_magnitude > threshold
            
        else:
            raise ValueError(f"Unsupported edge detection method: {method}")
        
        return edges, gradient_magnitude, edge_directions
    
    def calculate_edge_metrics(self, edges, thermal_data=None):
        """
        Calculate metrics for detected edges.
        
        Parameters:
            edges (numpy.ndarray): Binary edge mask
            thermal_data (numpy.ndarray, optional): Original thermal data
            
        Returns:
            dict: Dictionary of edge metrics
        """
        # Calculate basic edge properties
        num_edge_pixels = np.sum(edges)
        total_pixels = edges.size
        edge_density = (num_edge_pixels / total_pixels) * 100
        
        # Extract edge contours
        contours = measure.find_contours(edges.astype(float), 0.5)
        
        # Calculate total edge length and contour properties
        total_edge_length = 0
        contour_lengths = []
        mean_temp_gradients = []
        
        for contour in contours:
            length = len(contour)
            contour_lengths.append(length)
            total_edge_length += length
            
            # Calculate mean temperature gradient along contour if thermal data is provided
            if thermal_data is not None:
                gradient_sum = 0
                gradient_count = 0
                
                # Iterate through contour points
                for i in range(length):
                    # Get coordinates
                    y, x = int(contour[i][0]), int(contour[i][1])
                    
                    # Check if coordinates are within bounds
                    if (0 <= y < thermal_data.shape[0] - 1 and 
                        0 <= x < thermal_data.shape[1] - 1):
                        # Calculate local gradient magnitude (simple 2x2 neighborhood)
                        grad_y = thermal_data[y+1, x] - thermal_data[y, x]
                        grad_x = thermal_data[y, x+1] - thermal_data[y, x]
                        grad_mag = np.sqrt(grad_x**2 + grad_y**2)
                        
                        gradient_sum += grad_mag
                        gradient_count += 1
                
                # Calculate mean gradient for this contour
                if gradient_count > 0:
                    mean_grad = gradient_sum / gradient_count
                    mean_temp_gradients.append(mean_grad)
        
        # Create metrics dictionary
        metrics = {
            'num_edge_pixels': num_edge_pixels,
            'edge_density': edge_density,
            'num_contours': len(contours),
            'total_edge_length': total_edge_length,
            'contour_lengths': contour_lengths,
        }
        
        # Add temperature gradient metrics if available
        if thermal_data is not None and mean_temp_gradients:
            metrics.update({
                'mean_temp_gradient': np.mean(mean_temp_gradients),
                'max_temp_gradient': np.max(mean_temp_gradients),
                'contour_temp_gradients': mean_temp_gradients
            })
        
        return metrics
    
    def create_edge_overlay(self, thermal_data, edges, gradient_magnitude=None, 
                          edge_directions=None, edge_color='white', alpha=0.7):
        """
        Create an overlay of detected edges on thermal data.
        
        Parameters:
            thermal_data (numpy.ndarray): 2D array of temperature values
            edges (numpy.ndarray): Binary edge mask
            gradient_magnitude (numpy.ndarray, optional): Gradient magnitude
            edge_directions (numpy.ndarray, optional): Edge directions
            edge_color (str): Color for edges
            alpha (float): Transparency for overlay
            
        Returns:
            numpy.ndarray: RGBA image with edge overlay
        """
        # Normalize thermal data for visualization
        vmin = np.min(thermal_data)
        vmax = np.max(thermal_data)
        normalized = (thermal_data - vmin) / (vmax - vmin)
        
        # Create RGB image using inferno colormap
        rgb = plt.cm.inferno(normalized)[:, :, :3]
        # rgb = config.COLORMAP(normalized)[:, :, :3]
        
        # Create RGBA overlay
        overlay = np.zeros((*thermal_data.shape, 4))
        overlay[..., :3] = rgb
        overlay[..., 3] = alpha  # Base alpha
        
        # Prepare legend information to return
        legend_info = None
        
        # Use white for edges by default
        match edge_color:
            case 'white':
                edge_rgb = [1, 1, 1]
            case 'red':
                edge_rgb = [1, 0, 0]
            case 'green':
                edge_rgb = [0, 1, 0]
            case 'blue':
                edge_rgb = [0, 0, 1]
            case 'yellow':
                edge_rgb = [1, 1, 0]
            
            case 'direction' if edge_directions is not None:
                # Create directional coloring
                # Normalize directions from -pi to pi to 0 to 1
                norm_directions = (edge_directions + np.pi) / (2 * np.pi)
                # Apply a cyclic colormap
                dir_colors = plt.cm.hsv(norm_directions)
                
                # Create directional edge overlay
                dir_overlay = np.zeros((*thermal_data.shape, 4))
                dir_overlay[..., :3] = dir_colors[..., :3]
                dir_overlay[..., 3] = 0  # Start with transparent
                dir_overlay[edges, 3] = 1  # Make edges opaque

                # Add legend information for direction
                legend_info = {
                    'type': 'direction',
                    'min_value': -np.pi,
                    'max_value': np.pi,
                    'label': 'Edge Direction (radians)',
                    'colormap': 'hsv',
                    'ticks': [-np.pi, -np.pi/2, 0, np.pi/2, np.pi],  # Add explicit ticks
                    'ticklabels': ['-π', '-π/2', '0', 'π/2', 'π']    # Add explicit tick labels
                }
                
                return dir_overlay, legend_info
            
            case 'magnitude' if gradient_magnitude is not None:
                # Create magnitude-based coloring
                # Normalize gradient magnitude
                norm_magnitude = gradient_magnitude / np.max(gradient_magnitude)
                # Apply a sequential colormap
                mag_colors = plt.cm.viridis(norm_magnitude)
                
                # Create magnitude edge overlay
                mag_overlay = np.zeros((*thermal_data.shape, 4))
                mag_overlay[..., :3] = mag_colors[..., :3]
                mag_overlay[..., 3] = 0  # Start with transparent
                mag_overlay[edges, 3] = 1  # Make edges opaque

                # Add legend information for magnitude
                legend_info = {
                    'type': 'magnitude',
                    'min_value': 0,
                    'max_value': np.max(gradient_magnitude) if np.max(gradient_magnitude) > 0 else 1,
                    'label': 'Temperature Gradient (°C/pixel)',
                    'colormap': 'viridis',
                    'ticks': None  # Will be auto-generated based on min/max values
                }

                
                return mag_overlay, legend_info
            
            case _ if edge_color.startswith('#'):
                try:
                    # Hex color
                    r = int(edge_color[1:3], 16) / 255
                    g = int(edge_color[3:5], 16) / 255
                    b = int(edge_color[5:7], 16) / 255
                    edge_rgb = [r, g, b]
                except:
                    # Use white as fallback
                    edge_rgb = [1, 1, 1]
            
            case _:
                # Default fallback
                edge_rgb = [1, 1, 1]
        
        # Set edge pixels in overlay
        overlay[edges, :3] = edge_rgb
        overlay[edges, 3] = 1.0  # Make edges opaque
        
        return overlay, legend_info