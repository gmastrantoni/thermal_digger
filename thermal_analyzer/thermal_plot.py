import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Polygon
from matplotlib.path import Path
import tkinter as tk
from utils.config import config

class ThermalPlotter:
    def __init__(self, plot_frame):
        self.plot_frame = plot_frame
        self.fig_thermal = None
        self.ax_thermal = None
        self.canvas_thermal = None
        self.fig_timeseries = None
        self.ax_timeseries = None
        self.canvas_timeseries = None
        self.polygon_patch = None
        self.setup_plots()

    def setup_plots(self):
        """Initialize matplotlib figures and canvases"""
        # Thermal image plot
        self.fig_thermal = Figure(figsize=(10, 8), constrained_layout=True)
        self.ax_thermal = self.fig_thermal.add_subplot(111)
        self.canvas_thermal = FigureCanvasTkAgg(self.fig_thermal, master=self.plot_frame)
        self.canvas_thermal.draw()
        canvas_widget = self.canvas_thermal.get_tk_widget()
        canvas_widget.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        # Time series plot
        self.fig_timeseries = Figure(figsize=(10, 4), constrained_layout=True)
        self.ax_timeseries = self.fig_timeseries.add_subplot(111)
        self.canvas_timeseries = FigureCanvasTkAgg(self.fig_timeseries, master=self.plot_frame)
        self.canvas_timeseries.draw()
        self.canvas_timeseries.get_tk_widget().grid(row=1, column=0, padx=5, pady=5, sticky='nsew')
        
        # Configure grid weights
        self.plot_frame.grid_columnconfigure(0, weight=1)
        self.plot_frame.grid_rowconfigure(0, weight=2)
        self.plot_frame.grid_rowconfigure(1, weight=1)
        
        # Set initial axes positions that will be maintained
        self.ax_thermal.set_position([0.1, 0.1, 0.75, 0.85])  # [left, bottom, width, height]

    def plot_thermal_image(self, data, timestamp=None):
        """Plot thermal image with optional timestamp"""
        self.ax_thermal.clear()
        
        # Maintain consistent axes position
        self.ax_thermal.set_position([0.1, 0.1, 0.75, 0.85])
        
        # Remove old colorbar if it exists
        if len(self.fig_thermal.axes) > 1:
            self.fig_thermal.delaxes(self.fig_thermal.axes[1])
        
        # Plot image with fixed aspect ratio
        im = self.ax_thermal.imshow(data, cmap=config.COLORMAP, aspect='equal', 
                           interpolation='nearest')
        
        # Add colorbar with consistent size
        cbar = self.fig_thermal.colorbar(im, ax=self.ax_thermal, 
                                       label='Temperature (°C)',
                                       pad=0.02)
        
        if timestamp:
            title = f'Thermal Image - {timestamp.strftime("%Y-%m-%d %H:%M:%S")}'
            self.ax_thermal.set_title(title, pad=10)
        
        self.canvas_thermal.draw()

    def plot_point(self, x, y):
        """Plot a point for polygon creation"""
        self.ax_thermal.plot(x, y, 'w+')
        self.canvas_thermal.draw()

    def plot_line(self, x1, y1, x2, y2):
        """Plot a line between two points"""
        self.ax_thermal.plot([x1, x2], [y1, y2], 'w-')
        self.canvas_thermal.draw()

    def plot_polygon(self, coords):
        """Plot the completed polygon"""
        if self.polygon_patch:
            self.polygon_patch.remove()
        self.polygon_patch = Polygon(coords, fill=False, color='white')
        self.ax_thermal.add_patch(self.polygon_patch)
        self.canvas_thermal.draw()

    def plot_time_series(self, timestamps, values, mins=None, maxs=None):
        """Plot time series data (single point or polygon statistics)"""
        self.ax_timeseries.clear()
        
        if mins is None and maxs is None:
            # Single point time series
            self.ax_timeseries.plot(timestamps, values, 'bo', label='Temperature')
        else:
            # Polygon statistics time series
            self.ax_timeseries.plot(timestamps, values, 'go--', label='Mean')
            self.ax_timeseries.plot(timestamps, mins, 'bo--', label='Min')
            self.ax_timeseries.plot(timestamps, maxs, 'ro--', label='Max')
        
        self.fig_timeseries.autofmt_xdate()
        
        self.ax_timeseries.set_xlabel('Time')
        self.ax_timeseries.set_ylabel('Temperature (°C)')
        self.ax_timeseries.set_title('Temperature Time Series')
        self.ax_timeseries.legend()
        self.ax_timeseries.grid(True)
        
        self.canvas_timeseries.draw()
        
    def clear_selection(self):
        """Clear current selection (point or polygon) and markers"""
        if self.polygon_patch:
            self.polygon_patch.remove()
            self.polygon_patch = None
        
        # Clear any point markers
        for artist in self.ax_thermal.lines:
            artist.remove()
        
        self.canvas_thermal.draw()
        self.ax_timeseries.clear()
        self.canvas_timeseries.draw()

    def clear_polygon(self):
        """Clear polygon and point markers"""
        if self.polygon_patch:
            self.polygon_patch.remove()
            self.polygon_patch = None
        
        # Clear any point markers
        for artist in self.ax_thermal.lines:
            artist.remove()
        
        self.canvas_thermal.draw()
        self.ax_timeseries.clear()
        self.canvas_timeseries.draw()
        
    def clear_workspace(self):
        """Clear all plots and reset to initial state"""
        # Clear thermal image plot
        self.ax_thermal.clear()
        if self.polygon_patch:
            self.polygon_patch.remove()
            self.polygon_patch = None
        
        # Maintain consistent axes position and appearance
        self.ax_thermal.set_position([0.1, 0.1, 0.75, 0.85])
        self.ax_thermal.set_title('Thermal Image')
        
        # Set initial axis limits
        self.ax_thermal.set_xlim(0, 336)  # Based on your image dimensions
        self.ax_thermal.set_ylim(252, 0)  # Inverted for image coordinates
        
        # Remove colorbar if it exists
        if len(self.fig_thermal.axes) > 1:
            self.fig_thermal.delaxes(self.fig_thermal.axes[1])
        
        # Clear time series plot
        self.ax_timeseries.clear()
        self.ax_timeseries.set_title('Temperature Statistics')
        self.ax_timeseries.set_xlabel('Time')
        self.ax_timeseries.set_ylabel('Temperature (°C)')
        self.ax_timeseries.grid(True)
        self.ax_timeseries.set_xlim(0, 1)
        self.ax_timeseries.set_ylim(0, 1)
        
        # Redraw both canvases
        self.canvas_thermal.draw()
        self.canvas_timeseries.draw()

    def create_polygon_mask(self, data_shape, polygon_coords):
        """Create boolean mask from polygon coordinates"""
        mask = np.zeros(data_shape, dtype=bool)
        
        # Convert polygon coordinates to integer indices
        polygon_coords_int = np.array(polygon_coords).astype(int)
        
        # Create vertex list for path
        path = Path(polygon_coords_int)
        
        # Create grid of points
        x, y = np.meshgrid(np.arange(data_shape[1]), np.arange(data_shape[0]))
        points = np.vstack((x.flatten(), y.flatten())).T
        
        # Test which points are inside the polygon
        mask = path.contains_points(points).reshape(data_shape)
        
        return mask

    def save_plots(self, base_filename):
        """Save both thermal and time series plots"""
        # Save thermal image plot
        thermal_filename = f"{base_filename}_thermal.png"
        self.fig_thermal.savefig(thermal_filename, bbox_inches='tight', dpi=300)
        
        # Save time series plot
        timeseries_filename = f"{base_filename}_timeseries.png"
        self.fig_timeseries.savefig(timeseries_filename, bbox_inches='tight', dpi=300)
        
        return thermal_filename, timeseries_filename
        
    def get_click_handler(self):
        """Return the canvas for click event binding"""
        return self.canvas_thermal