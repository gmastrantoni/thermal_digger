"""
Thermal image comparison techniques for identifying changes between thermal images.
Based on the approaches outlined in technical documentation.
"""

import numpy as np
from scipy import ndimage
from enum import Enum, auto


class ComparisonMethod(Enum):
    """Enumeration of supported thermal image comparison methods."""
    DIRECT_DIFFERENCE = auto()
    STATISTICAL_CHANGE = auto()
    CORRELATION = auto()
    
    def __str__(self):
        """Return the string representation of the method."""
        return self.name.replace('_', ' ').capitalize()


class ThermalComparisonDetector:
    """
    Detector for comparing master and slave thermal images using various techniques.
    Implements Master-Slave Image Comparison Techniques from technical documentation.
    """
    
    def __init__(self):
        """Initialize the ThermalComparisonDetector."""
        pass
    
    def compute_difference(self, master_data, slave_data, threshold=1.0, relative=False):
        """
        Calculate direct difference between master and slave thermal images.
        
        Parameters:
            master_data (numpy.ndarray): Master (reference) thermal data
            slave_data (numpy.ndarray): Slave (target) thermal data
            threshold (float): Minimum temperature difference to consider significant (in °C or % based on relative)
            relative (bool): If True, calculate relative (percentage) difference
        
        Returns:
            dict: Dictionary containing difference data and analysis results
                'difference': Difference matrix (slave - master)
                'significant_changes': Boolean mask of changes exceeding threshold
                'threshold_value': Threshold value used
        """
        # Verify that both images have the same dimensions
        if master_data.shape != slave_data.shape:
            raise ValueError(f"Image dimensions don't match: master {master_data.shape} vs slave {slave_data.shape}")
        
        # Calculate the raw difference (slave - master)
        difference = slave_data - master_data
        
        # For relative difference, calculate percentage change relative to master
        if relative:
            # Avoid division by zero and handle small values
            epsilon = 0.00001  # Small value to prevent division by zero
            safe_master = np.where(np.abs(master_data) > epsilon, master_data, epsilon)
            difference = (difference / np.abs(safe_master)) * 100.0
        
        # Identify areas where the difference exceeds the threshold
        if relative:
            significant_changes = np.abs(difference) > threshold  # Threshold is percentage
        else:
            significant_changes = np.abs(difference) > threshold  # Threshold is absolute temperature
        
        return {
            'difference': difference,
            'significant_changes': significant_changes,
            'threshold_value': threshold,
            'is_relative': relative
        }
    
    def compute_gradient_preprocessed_difference(self, master_data, slave_data, window_size=3, 
                                               threshold=1.0, relative=False):
        """
        Calculate difference after gradient pre-processing.
        This can highlight areas where the thermal gradient changes, rather than just the absolute temperature.
        
        Parameters:
            master_data (numpy.ndarray): Master (reference) thermal data
            slave_data (numpy.ndarray): Slave (target) thermal data
            window_size (int): Size of window for gradient calculation
            threshold (float): Minimum gradient difference to consider significant
            relative (bool): If True, calculate relative (percentage) difference
        
        Returns:
            dict: Dictionary containing difference data and analysis results
                'difference': Difference matrix (slave gradient - master gradient)
                'significant_changes': Boolean mask of changes exceeding threshold
                'master_gradient': Gradient magnitude of master image
                'slave_gradient': Gradient magnitude of slave image
                'threshold_value': Threshold value used
        """
        # Calculate gradient magnitude for both images
        master_gradient = self._calculate_gradient_magnitude(master_data, window_size)
        slave_gradient = self._calculate_gradient_magnitude(slave_data, window_size)
        
        # Compute difference between gradients
        gradient_diff = slave_gradient - master_gradient
        
        # For relative difference, calculate percentage change relative to master
        if relative:
            # Avoid division by zero and handle small values
            epsilon = 0.00001
            safe_master_gradient = np.where(np.abs(master_gradient) > epsilon, master_gradient, epsilon)
            gradient_diff = (gradient_diff / np.abs(safe_master_gradient)) * 100.0
        
        # Identify areas where the gradient difference exceeds the threshold
        if relative:
            significant_changes = np.abs(gradient_diff) > threshold  # Threshold is percentage
        else:
            significant_changes = np.abs(gradient_diff) > threshold  # Threshold is absolute temperature
        
        return {
            'difference': gradient_diff,
            'significant_changes': significant_changes,
            'master_gradient': master_gradient,
            'slave_gradient': slave_gradient,
            'threshold_value': threshold,
            'is_relative': relative,
            'window_size': window_size
        }
    
    def compute_smoothed_difference(self, master_data, slave_data, window_size=3, 
                                  threshold=1.0, relative=False):
        """
        Calculate difference after smoothing pre-processing.
        Smoothing reduces noise and helps identify more significant trends.
        
        Parameters:
            master_data (numpy.ndarray): Master (reference) thermal data
            slave_data (numpy.ndarray): Slave (target) thermal data
            window_size (int): Size of window for smoothing
            threshold (float): Minimum temperature difference to consider significant
            relative (bool): If True, calculate relative (percentage) difference
        
        Returns:
            dict: Dictionary containing difference data and analysis results
                'difference': Difference matrix (smoothed slave - smoothed master)
                'significant_changes': Boolean mask of changes exceeding threshold
                'threshold_value': Threshold value used
        """
        # Apply Gaussian smoothing to both images
        sigma = window_size / 6.0  # Convert window size to appropriate sigma
        smoothed_master = ndimage.gaussian_filter(master_data, sigma=sigma)
        smoothed_slave = ndimage.gaussian_filter(slave_data, sigma=sigma)
        
        # Calculate the smoothed difference
        smoothed_diff = smoothed_slave - smoothed_master
        
        # For relative difference, calculate percentage change relative to master
        if relative:
            # Avoid division by zero and handle small values
            epsilon = 0.00001
            safe_smoothed_master = np.where(np.abs(smoothed_master) > epsilon, smoothed_master, epsilon)
            smoothed_diff = (smoothed_diff / np.abs(safe_smoothed_master)) * 100.0
        
        # Identify areas where the smoothed difference exceeds the threshold
        if relative:
            significant_changes = np.abs(smoothed_diff) > threshold  # Threshold is percentage
        else:
            significant_changes = np.abs(smoothed_diff) > threshold  # Threshold is absolute temperature
        
        return {
            'difference': smoothed_diff,
            'significant_changes': significant_changes,
            'smoothed_master': smoothed_master,
            'smoothed_slave': smoothed_slave,
            'threshold_value': threshold,
            'is_relative': relative,
            'window_size': window_size
        }
    
    def compute_statistical_significance(self, master_data, slave_data, window_size=5, zscore_threshold=2.0):
        """
        Calculate statistical significance of changes between images.
        Uses local statistics from master image to determine if changes are significant.
        
        Parameters:
            master_data (numpy.ndarray): Master (reference) thermal data
            slave_data (numpy.ndarray): Slave (target) thermal data
            window_size (int): Size of window for local statistics calculation
            zscore_threshold (float): Z-score threshold for significant changes
        
        Returns:
            dict: Dictionary containing statistical comparison data
                'zscores': Z-score matrix
                'significant_changes': Boolean mask of significant changes
                'local_means': Local mean values from master image
                'local_stds': Local standard deviations from master image
        """
        # Verify that both images have the same dimensions
        if master_data.shape != slave_data.shape:
            raise ValueError(f"Image dimensions don't match: master {master_data.shape} vs slave {slave_data.shape}")
        
        # Calculate local statistics for master image (mean and standard deviation)
        local_means = ndimage.uniform_filter(master_data, size=window_size)
        
        # Calculate squared deviations
        squared_deviations = (master_data - local_means) ** 2
        
        # Calculate local variance and standard deviation
        local_variance = ndimage.uniform_filter(squared_deviations, size=window_size)
        local_stds = np.sqrt(local_variance)
        
        # Add a small epsilon to avoid division by zero
        epsilon = 0.001
        safe_stds = np.where(local_stds > epsilon, local_stds, epsilon)
        
        # Calculate z-scores for slave image based on master statistics
        zscores = (slave_data - local_means) / safe_stds
        
        # Identify statistically significant changes
        significant_changes = np.abs(zscores) > zscore_threshold
        
        return {
            'zscores': zscores,
            'significant_changes': significant_changes,
            'local_means': local_means,
            'local_stds': local_stds,
            'zscore_threshold': zscore_threshold,
            'window_size': window_size
        }
    
    def compute_spatial_correlation(self, master_data, slave_data, window_size=7, threshold=0.7):
        """
        Calculate spatial correlation between master and slave images.
        Uses moving window correlation to identify areas where patterns have changed.
        
        Parameters:
            master_data (numpy.ndarray): Master (reference) thermal data
            slave_data (numpy.ndarray): Slave (target) thermal data
            window_size (int): Size of window for correlation calculation
            threshold (float): Correlation threshold below which changes are considered significant
        
        Returns:
            dict: Dictionary containing correlation analysis results
                'correlation_map': Spatial correlation map
                'low_correlation_mask': Boolean mask of areas with low correlation
        """
        # Verify that both images have the same dimensions
        if master_data.shape != slave_data.shape:
            raise ValueError(f"Image dimensions don't match: master {master_data.shape} vs slave {slave_data.shape}")
        
        # Initialize correlation map
        correlation_map = np.zeros_like(master_data, dtype=float)
        
        # Calculate correlation coefficient for each pixel's neighborhood
        half_window = window_size // 2
        
        # Pad the arrays to handle edge cases
        master_padded = np.pad(master_data, half_window, mode='reflect')
        slave_padded = np.pad(slave_data, half_window, mode='reflect')
        
        # Calculate local correlation coefficients
        for i in range(master_data.shape[0]):
            for j in range(master_data.shape[1]):
                # Extract local regions
                master_region = master_padded[i:i+window_size, j:j+window_size]
                slave_region = slave_padded[i:i+window_size, j:j+window_size]
                
                # Flatten regions for correlation calculation
                master_flat = master_region.flatten()
                slave_flat = slave_region.flatten()
                
                # Calculate correlation coefficient
                try:
                    # Calculate means
                    master_mean = np.mean(master_flat)
                    slave_mean = np.mean(slave_flat)
                    
                    # Calculate deviations from means
                    master_dev = master_flat - master_mean
                    slave_dev = slave_flat - slave_mean
                    
                    # Calculate correlation coefficient
                    numerator = np.sum(master_dev * slave_dev)
                    denominator = np.sqrt(np.sum(master_dev**2) * np.sum(slave_dev**2))
                    
                    # Avoid division by zero
                    if denominator < 1e-10:
                        correlation_map[i, j] = 0
                    else:
                        correlation_map[i, j] = numerator / denominator
                        
                except Exception:
                    correlation_map[i, j] = 0
        
        # Identify areas with low correlation
        low_correlation_mask = correlation_map < threshold
        
        return {
            'correlation_map': correlation_map,
            'low_correlation_mask': low_correlation_mask,
            'correlation_threshold': threshold,
            'window_size': window_size
        }
    
    def calculate_metrics(self, result):
        """
        Calculate metrics for the comparison result.
        
        Parameters:
            result (dict): Comparison result from one of the compute methods
        
        Returns:
            dict: Dictionary of metrics
        """
        metrics = {}
        
        # Direct Difference metrics
        if 'difference' in result:
            diff_data = result['difference']
            metrics['mean_diff'] = np.mean(diff_data)
            metrics['std_diff'] = np.std(diff_data)
            metrics['max_diff'] = np.max(diff_data)
            metrics['min_diff'] = np.min(diff_data)
            
            # Count of significant changes if available
            if 'significant_changes' in result and result['significant_changes'] is not None:
                metrics['significant_pixel_count'] = np.sum(result['significant_changes'])
                metrics['positive_changes'] = np.sum((diff_data > 0) & result['significant_changes'])
                metrics['negative_changes'] = np.sum((diff_data < 0) & result['significant_changes'])
        
        # Statistical Change metrics
        if 'zscores' in result:
            zscore_data = result['zscores']
            metrics['mean_zscore'] = np.mean(zscore_data)
            metrics['std_zscore'] = np.std(zscore_data)
            metrics['max_zscore'] = np.max(zscore_data)
            metrics['min_zscore'] = np.min(zscore_data)
            
            # Count of statistically significant pixels
            if 'significant_changes' in result and result['significant_changes'] is not None:
                metrics['significant_pixel_count'] = np.sum(result['significant_changes'])
                metrics['positive_significant'] = np.sum((zscore_data > 0) & result['significant_changes'])
                metrics['negative_significant'] = np.sum((zscore_data < 0) & result['significant_changes'])
        
        # Correlation metrics
        if 'correlation_map' in result:
            corr_data = result['correlation_map']
            metrics['mean_correlation'] = np.mean(corr_data)
            metrics['min_correlation'] = np.min(corr_data)
            
            # Count of low correlation areas
            if 'low_correlation_mask' in result and result['low_correlation_mask'] is not None:
                metrics['low_correlation_count'] = np.sum(result['low_correlation_mask'])
        
        return metrics
    
    def _calculate_gradient_magnitude(self, data, window_size=3):
        """
        Calculate gradient magnitude using Sobel operators with custom window size.
        
        Parameters:
            data (numpy.ndarray): Thermal data
            window_size (int): Size of window for gradient calculation
        
        Returns:
            numpy.ndarray: Gradient magnitude
        """
        # For larger windows, use separable filters
        if window_size > 3:
            # Create 1D filters for x and y gradients
            # Central finite difference with larger window
            half_size = window_size // 2
            weights = np.arange(-half_size, half_size + 1)
            
            # Create normalized gradient filters
            gradient_filter = np.zeros(window_size)
            for i in range(window_size):
                if i < half_size:
                    gradient_filter[i] = -1 / (half_size * (half_size + 1) / 2) * (half_size - i)
                elif i > half_size:
                    gradient_filter[i] = 1 / (half_size * (half_size + 1) / 2) * (i - half_size)
            
            # Apply separable gradient filters
            gradient_x = ndimage.convolve1d(data, gradient_filter, axis=1, mode='reflect')
            gradient_y = ndimage.convolve1d(data, gradient_filter, axis=0, mode='reflect')
            
        else:
            # For small windows, use standard Sobel operator
            gradient_x = ndimage.sobel(data, axis=1, mode='reflect')
            gradient_y = ndimage.sobel(data, axis=0, mode='reflect')
        
        # Calculate gradient magnitude
        gradient_magnitude = np.sqrt(gradient_x**2 + gradient_y**2)
        
        return gradient_magnitude
