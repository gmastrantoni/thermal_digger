"""
GUI for thermal edge detection.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
from datetime import datetime
from utils.config import config
from image_analysis.edge_detector import ThermalEdgeDetector, EdgeDetectionMethod

class EdgeDetectionFrame(ttk.Frame):
    """
    Frame for edge detection analysis in thermal images with optimized layout.
    """
    
    def __init__(self, parent, main_app, on_analyze=None):
        """
        Initialize the edge detection frame.
        
        Parameters:
            parent: Parent widget
            main_app: Reference to the main application
            on_analyze: Callback function when analysis is performed
        """
        super().__init__(parent, padding="5")
        self.main_app = main_app
        self.on_analyze_callback = on_analyze
        self.edge_detector = ThermalEdgeDetector()
        
        # Store last analysis results
        self.last_results = None
        
        # Setup layout
        self.setup_layout()
    
    def setup_layout(self):
        """Setup the frame layout with all controls."""
        # Configure grid for a more space-efficient layout
        self.columnconfigure(0, weight=0)  # Control column (fixed width)
        self.columnconfigure(1, weight=1)  # Image column (expandable)
        self.rowconfigure(0, weight=1)     # Make the main row expandable
        
        # Create control panel (left side)
        control_panel = ttk.Frame(self, padding="5")
        control_panel.grid(row=0, column=0, sticky="ns", padx=(0, 5))
        
        # Create results panel (right side)
        results_panel = ttk.Frame(self)
        results_panel.grid(row=0, column=1, sticky="nsew")
        results_panel.columnconfigure(0, weight=1)
        results_panel.rowconfigure(0, weight=1)
        
        # Setup control panel widgets
        self._setup_control_panel(control_panel)
        
        # Setup results panel widgets
        self._setup_results_panel(results_panel)
    
    def _setup_control_panel(self, parent):
        """Setup the control panel with parameters and options."""
        # Title
        title_label = ttk.Label(parent, text="Edge Detection Controls", font=("TkDefaultFont", 11, "bold"))
        title_label.pack(fill="x", pady=(0, 10))
        
        # Method selection frame
        method_frame = ttk.LabelFrame(parent, text="Detection Method", padding="5")
        method_frame.pack(fill="x", pady=(0, 5))
        
        # Method combobox
        self.method_var = tk.StringVar(value="Sobel")
        method_combo = ttk.Combobox(
            method_frame, 
            textvariable=self.method_var,
            values=[str(m) for m in EdgeDetectionMethod],
            state="readonly",
            width=15
        )
        method_combo.pack(fill="x", pady=3)
        
        # Method description
        self.method_description = ttk.Label(
            method_frame, 
            text="Sobel operator detects edges by calculating image gradients.",
            wraplength=220,
            justify="left",
            font=("TkDefaultFont", 9, "italic")
        )
        self.method_description.pack(fill="x", pady=3)
        
        # Method selection callback
        method_combo.bind("<<ComboboxSelected>>", self.on_method_change)
        
        # Parameters frame
        params_frame = ttk.LabelFrame(parent, text="Parameters", padding="5")
        params_frame.pack(fill="x", pady=5)
        
        # Smoothing parameter
        smoothing_frame = ttk.Frame(params_frame)
        smoothing_frame.pack(fill="x", pady=2)
        ttk.Label(smoothing_frame, text="Smoothing (σ):").pack(side="left")
        self.sigma_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(
            smoothing_frame, 
            from_=0.0, 
            to=5.0, 
            increment=0.1,
            textvariable=self.sigma_var,
            width=5
        ).pack(side="right")
        
        # Threshold parameter
        threshold_frame = ttk.Frame(params_frame)
        threshold_frame.pack(fill="x", pady=2)
        ttk.Label(threshold_frame, text="Threshold:").pack(side="left")
        self.threshold_var = tk.DoubleVar(value=1.5)
        ttk.Spinbox(
            threshold_frame, 
            from_=0.1, 
            to=10.0, 
            increment=0.1,
            textvariable=self.threshold_var,
            width=5
        ).pack(side="right")
        
        # Canny specific parameters (initially hidden)
        self.canny_frame = ttk.Frame(params_frame)
        self.canny_frame.pack(fill="x", pady=2)
        self.canny_frame.pack_forget()  # Hide initially
        
        # Low threshold
        low_frame = ttk.Frame(self.canny_frame)
        low_frame.pack(fill="x", pady=2)
        ttk.Label(low_frame, text="Low Threshold:").pack(side="left")
        self.low_threshold_var = tk.DoubleVar(value=0.5)
        ttk.Spinbox(
            low_frame, 
            from_=0.1, 
            to=5.0, 
            increment=0.1,
            textvariable=self.low_threshold_var,
            width=5
        ).pack(side="right")
        
        # High threshold
        high_frame = ttk.Frame(self.canny_frame)
        high_frame.pack(fill="x", pady=2)
        ttk.Label(high_frame, text="High Threshold:").pack(side="left")
        self.high_threshold_var = tk.DoubleVar(value=1.5)
        ttk.Spinbox(
            high_frame, 
            from_=0.1, 
            to=10.0, 
            increment=0.1,
            textvariable=self.high_threshold_var,
            width=5
        ).pack(side="right")
        
        # Visualization options frame
        visual_frame = ttk.LabelFrame(parent, text="Visualization", padding="5")
        visual_frame.pack(fill="x", pady=5)
        
        # Edge color
        color_frame = ttk.Frame(visual_frame)
        color_frame.pack(fill="x", pady=2)
        ttk.Label(color_frame, text="Edge Color:").pack(side="left")
        self.edge_color_var = tk.StringVar(value="white")
        ttk.Combobox(
            color_frame, 
            textvariable=self.edge_color_var,
            values=["white", "red", "green", "blue", "yellow", "magnitude", "direction"],
            state="readonly",
            width=10
        ).pack(side="right")
        
        # Display mode
        mode_frame = ttk.Frame(visual_frame)
        mode_frame.pack(fill="x", pady=2)
        ttk.Label(mode_frame, text="Display Mode:").pack(side="left")
        self.display_mode_var = tk.StringVar(value="overlay")
        ttk.Combobox(
            mode_frame, 
            textvariable=self.display_mode_var,
            values=["overlay", "side-by-side", "edges only"],
            state="readonly",
            width=10
        ).pack(side="right")
        
        # Show metrics checkbox
        metrics_frame = ttk.Frame(visual_frame)
        metrics_frame.pack(fill="x", pady=2)
        ttk.Label(metrics_frame, text="Show Metrics:").pack(side="left")
        self.show_metrics_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            metrics_frame, 
            variable=self.show_metrics_var
        ).pack(side="right")
        
        # Action buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", pady=10)
        
        ttk.Button(
            button_frame, 
            text="Analyze Image",
            command=self.analyze_image
        ).pack(fill="x", pady=2)
        
        ttk.Button(
            button_frame, 
            text="Save Results",
            command=self.save_results
        ).pack(fill="x", pady=2)
    
    def _setup_results_panel(self, parent):
        """Setup the results panel with the image display and metrics."""
        # Create figure for visualizing results
        self.fig = Figure(figsize=(6, 5), constrained_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Initial setup of figure
        self.setup_figure()
        
        # Metrics display (collapsed by default)
        self.metrics_frame = ttk.Frame(parent)
        self.metrics_frame.grid(row=1, column=0, sticky="ew")
        
        # Metrics header with toggle button
        metrics_header = ttk.Frame(self.metrics_frame)
        metrics_header.pack(fill="x")
        
        self.metrics_toggle = ttk.Button(
            metrics_header, 
            text="▼ Edge Metrics", 
            style="Toolbutton",
            command=self.toggle_metrics
        )
        self.metrics_toggle.pack(side="left")
        
        # Metrics content (collapsible)
        self.metrics_content = ttk.Frame(self.metrics_frame)
        self.metrics_content.pack(fill="x", expand=True)
        
        self.metrics_text = tk.Text(self.metrics_content, height=4, width=50, wrap=tk.WORD)
        self.metrics_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.metrics_content, command=self.metrics_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.metrics_text.config(yscrollcommand=scrollbar.set)
        
        # Initially collapse metrics
        self.metrics_collapsed = False
    
    def toggle_metrics(self):
        """Toggle the visibility of the metrics panel."""
        if self.metrics_collapsed:
            self.metrics_content.pack(fill="x", expand=True)
            self.metrics_toggle.config(text="▼ Edge Metrics")
            self.metrics_collapsed = False
        else:
            self.metrics_content.pack_forget()
            self.metrics_toggle.config(text="► Edge Metrics")
            self.metrics_collapsed = True
    
    def setup_figure(self):
        """Setup the initial figure."""
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Thermal Image")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.text(
            0.5, 0.5, 
            "No image analyzed yet.\nClick 'Analyze Image' to begin.",
            horizontalalignment='center',
            verticalalignment='center',
            transform=self.ax.transAxes,
            fontsize=12
        )
        self.canvas.draw()
    
    def on_method_change(self, event=None):
        """Handle change of edge detection method."""
        method = self.method_var.get().lower()
        
        # Update method description
        descriptions = {
            "sobel": "Sobel operator detects edges by calculating image gradients. Good for detecting strong edges.",
            "canny": "Canny algorithm uses multi-stage process for edge detection. Best for detecting precise edges with noise suppression.",
            "prewitt": "Prewitt operator is similar to Sobel but gives equal weight to all directions. Good for uniform edge detection.",
            "roberts": "Roberts Cross operator performs simple, quick edge detection. Good for clean images with sharp edges.",
            "scharr": "Scharr operator is an improved version of Sobel with better rotational symmetry. Better for diagonal edges."
        }
        
        self.method_description.config(text=descriptions.get(method, ""))
        
        # Show/hide Canny-specific parameters
        if method == "canny":
            self.canny_frame.pack(fill="x", pady=2)
        else:
            self.canny_frame.pack_forget()
    
    def analyze_image(self):
        """Analyze the current image for edge detection."""
        # Check if there's a current image
        if not hasattr(self.main_app, 'current_data') or self.main_app.current_data is None:
            messagebox.showwarning("No Data", "No thermal data available for analysis.")
            return
        
        try:
            # Get current thermal data
            thermal_data = self.main_app.current_data
            
            # Get parameters
            method = self.method_var.get().lower()
            sigma = self.sigma_var.get()
            threshold = self.threshold_var.get()
            
            # Additional parameters for Canny
            low_threshold = None
            high_threshold = None
            
            if method == "canny":
                low_threshold = self.low_threshold_var.get()
                high_threshold = self.high_threshold_var.get()
            
            # Perform edge detection
            edges, gradient_magnitude, edge_directions = self.edge_detector.detect_edges(
                thermal_data, 
                method=method, 
                threshold=threshold, 
                sigma=sigma,
                low_threshold=low_threshold,
                high_threshold=high_threshold
            )
            
            # Calculate edge metrics
            metrics = self.edge_detector.calculate_edge_metrics(edges, thermal_data)
            
            # Store results for later use
            self.last_results = {
                'thermal_data': thermal_data,
                'edges': edges,
                'gradient_magnitude': gradient_magnitude,
                'edge_directions': edge_directions,
                'metrics': metrics,
                'parameters': {
                    'method': method,
                    'sigma': sigma,
                    'threshold': threshold,
                    'low_threshold': low_threshold,
                    'high_threshold': high_threshold
                }
            }
            
            # Visualize results
            self.visualize_results()
            
            # Display metrics
            self.display_metrics(metrics)
            
            # Call analyze callback if provided
            if self.on_analyze_callback:
                self.on_analyze_callback(self.last_results)
                
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Error during edge detection: {str(e)}")
    
    def visualize_results(self):
        """Visualize the edge detection results."""
        if not self.last_results:
            return
            
        # Clear figure
        self.fig.clear()
        
        # Get visualization parameters
        display_mode = self.display_mode_var.get()
        edge_color = self.edge_color_var.get()
        
        # Get data from last results
        thermal_data = self.last_results['thermal_data']
        edges = self.last_results['edges']
        gradient_magnitude = self.last_results['gradient_magnitude']
        edge_directions = self.last_results['edge_directions']
        method = self.last_results['parameters']['method']
        
        # Get timestamp if available
        timestamp = None
        if hasattr(self.main_app, 'timestamps') and len(self.main_app.timestamps) > 0:
            timestamp = self.main_app.timestamps[self.main_app.current_image_index]
        
        # Create visualization based on display mode
        if display_mode == "overlay":
            # Single view with overlay
            ax = self.fig.add_subplot(111)
            
            # Create edge overlay
            overlay, legend_info = self.edge_detector.create_edge_overlay(
                thermal_data, 
                edges, 
                gradient_magnitude, 
                edge_directions, 
                edge_color
            )
            
            # Display overlay
            ax.imshow(overlay)

            # Add legend if applicable
            if legend_info and edge_color in ['magnitude', 'direction']:
                from matplotlib import cm
                from matplotlib.colors import Normalize
                import matplotlib.pyplot as plt
                
                # Create a colorbar for the legend
                if legend_info['type'] == 'direction':
                    # For direction, we need a cyclic colormap
                    norm = Normalize(vmin=legend_info['min_value'], vmax=legend_info['max_value'])
                    sm = plt.cm.ScalarMappable(cmap=legend_info['colormap'], norm=norm)
                    sm.set_array([])
                    cbar = self.fig.colorbar(sm, ax=ax, label=legend_info['label'])
                    # Add ticks for direction
                    cbar.set_ticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
                    cbar.set_ticklabels(['-π', '-π/2', '0', 'π/2', 'π'])
                else:
                    # For magnitude
                    norm = Normalize(vmin=legend_info['min_value'], vmax=legend_info['max_value'])
                    sm = plt.cm.ScalarMappable(cmap=legend_info['colormap'], norm=norm)
                    sm.set_array([])
                    cbar = self.fig.colorbar(sm, ax=ax, label=legend_info['label'])
            
            # Add title
            title = f"Edge Detection ({method.capitalize()})"
            if timestamp:
                title += f" - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            ax.set_title(title)
            
        elif display_mode == "side-by-side":
            # Two plots side by side
            ax1 = self.fig.add_subplot(121)
            ax2 = self.fig.add_subplot(122)
            
            # Original thermal image with colorbar
            im1 = ax1.imshow(thermal_data, cmap=config.COLORMAP)
            cbar1 = self.fig.colorbar(im1, ax=ax1)
            cbar1.set_label('Temperature (°C)', size=8)
            cbar1.ax.tick_params(labelsize=7)
            ax1.set_title("Original Thermal Image", fontsize=9)
            
            # Edges with colored background
            overlay, legend_info = self.edge_detector.create_edge_overlay(
                thermal_data, 
                edges, 
                gradient_magnitude, 
                edge_directions, 
                edge_color
            )
            ax2.imshow(overlay)
            ax2.set_title(f"Detected Edges ({method.capitalize()})", fontsize=9)
            
            # Add legend if applicable
            if legend_info and edge_color in ['magnitude', 'direction']:
                from matplotlib import cm
                from matplotlib.colors import Normalize
                import matplotlib.pyplot as plt
                
                # Create a colorbar for the legend
                if legend_info['type'] == 'direction':
                    norm = Normalize(vmin=legend_info['min_value'], vmax=legend_info['max_value'])
                    sm = plt.cm.ScalarMappable(cmap=legend_info['colormap'], norm=norm)
                    sm.set_array([])
                    cbar2 = self.fig.colorbar(sm, ax=ax2, label=legend_info['label'])
                    cbar2.set_ticks([-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
                    cbar2.set_ticklabels(['-π', '-π/2', '0', 'π/2', 'π'])
                else:
                    norm = Normalize(vmin=legend_info['min_value'], vmax=legend_info['max_value'])
                    sm = plt.cm.ScalarMappable(cmap=legend_info['colormap'], norm=norm)
                    sm.set_array([])
                    cbar2 = self.fig.colorbar(sm, ax=ax2, label=legend_info['label'])
            
            # Add main title if timestamp available
            if timestamp:
                self.fig.suptitle(timestamp.strftime('%Y-%m-%d %H:%M:%S'), fontsize=10)
            
        elif display_mode == "edges only":
            # Only show the edges
            ax = self.fig.add_subplot(111)
            
            if edge_color in ['magnitude', 'direction']:
                # For magnitude or direction, use the specialized overlay
                overlay, legend_info = self.edge_detector.create_edge_overlay(
                    thermal_data, 
                    edges, 
                    gradient_magnitude, 
                    edge_directions, 
                    edge_color
                )
                ax.imshow(overlay)

                # Add legend
                if legend_info:
                    from matplotlib import cm
                    from matplotlib.colors import Normalize
                    import matplotlib.pyplot as plt
                    
                    if legend_info['type'] == 'direction':
                        norm = Normalize(vmin=legend_info['min_value'], vmax=legend_info['max_value'])
                        sm = plt.cm.ScalarMappable(cmap=legend_info['colormap'], norm=norm)
                        sm.set_array([])
                        cbar = self.fig.colorbar(sm, ax=ax, label=legend_info['label'])
                        cbar.set_ticks(legend_info['ticks'])
                        cbar.set_ticklabels(legend_info['tick_labels'])
                    else:
                        norm = Normalize(vmin=legend_info['min_value'], vmax=legend_info['max_value'])
                        sm = plt.cm.ScalarMappable(cmap=legend_info['colormap'], norm=norm)
                        sm.set_array([])
                        cbar = self.fig.colorbar(sm, ax=ax, label=legend_info['label'])
                        
            else:
                # Simple edge display
                ax.imshow(edges, cmap='gray')
            
            # Add title
            title = f"Edge Detection ({method.capitalize()})"
            if timestamp:
                title += f" - {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            ax.set_title(title)
        
        # Remove axes ticks for cleaner look
        for ax in self.fig.get_axes():
            ax.set_xticks([])
            ax.set_yticks([])
        
        # Update the canvas
        self.canvas.draw()
    
    def display_metrics(self, metrics):
        """Display edge detection metrics."""
        if not self.show_metrics_var.get() or not metrics:
            self.metrics_text.delete(1.0, tk.END)
            return
            
        # Format metrics as text
        text = "Edge Detection Metrics:\n\n"
        
        text += f"Number of Edge Pixels: {metrics['num_edge_pixels']}\n"
        text += f"Edge Density: {metrics['edge_density']:.2f}%\n"
        text += f"Number of Contours: {metrics['num_contours']}\n"
        text += f"Total Edge Length: {metrics['total_edge_length']:.1f} pixels\n"
        
        # Add temperature gradient metrics if available
        if 'mean_temp_gradient' in metrics:
            text += f"Mean Temperature Gradient: {metrics['mean_temp_gradient']:.2f}°C/pixel\n"
            text += f"Max Temperature Gradient: {metrics['max_temp_gradient']:.2f}°C/pixel\n"
        
        # Add contour length statistics
        if metrics['contour_lengths']:
            mean_length = np.mean(metrics['contour_lengths'])
            max_length = np.max(metrics['contour_lengths'])
            min_length = np.min(metrics['contour_lengths'])
            text += f"Average Contour Length: {mean_length:.1f} pixels\n"
            text += f"Longest Contour: {max_length:.1f} pixels\n"
            text += f"Shortest Contour: {min_length:.1f} pixels\n"
        
        # Update text widget
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(tk.END, text)
        
        # Ensure metrics are visible
        if self.metrics_collapsed:
            self.toggle_metrics()
    
    def save_results(self):
        """Save the edge detection results."""
        if not self.last_results:
            messagebox.showwarning("No Results", "No analysis results to save.")
            return
        
        try:
            # Get default save directory
            if hasattr(self.main_app, 'get_default_save_directory'):
                default_dir = self.main_app.get_default_save_directory()
            else:
                default_dir = os.path.expanduser("~/Documents")
            
            # Create save dialog
            save_dir = filedialog.askdirectory(
                title="Select Directory to Save Results",
                initialdir=default_dir
            )
            
            if not save_dir:
                return  # User cancelled
            
            # Get timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if hasattr(self.main_app, 'timestamps') and len(self.main_app.timestamps) > 0:
                timestamp = self.main_app.timestamps[self.main_app.current_image_index].strftime("%Y%m%d_%H%M%S")
            
            # Get method name
            method = self.last_results['parameters']['method']
            
            # Create base filename
            base_filename = os.path.join(save_dir, f"edge_detection_{method}_{timestamp}")
            
            # Save figure as image
            figure_filename = f"{base_filename}.png"
            self.fig.savefig(figure_filename, dpi=300, bbox_inches='tight')
            
            # Save edge mask as CSV
            if self.last_results['edges'] is not None:
                edges_filename = f"{base_filename}_edges.csv"
                np.savetxt(edges_filename, self.last_results['edges'].astype(int), delimiter=',')
            
            # Save gradient magnitude as CSV
            if self.last_results['gradient_magnitude'] is not None:
                gradient_filename = f"{base_filename}_gradient.csv"
                np.savetxt(gradient_filename, self.last_results['gradient_magnitude'], delimiter=',')
            
            # Save metrics as text file
            if self.last_results['metrics'] is not None:
                metrics_filename = f"{base_filename}_metrics.txt"
                with open(metrics_filename, 'w') as f:
                    # Write parameters
                    f.write("Edge Detection Parameters:\n")
                    for key, value in self.last_results['parameters'].items():
                        if value is not None:
                            f.write(f"{key}: {value}\n")
                    f.write("\n")
                    
                    # Write metrics
                    f.write("Edge Detection Metrics:\n")
                    metrics = self.last_results['metrics']
                    f.write(f"Number of Edge Pixels: {metrics['num_edge_pixels']}\n")
                    f.write(f"Edge Density: {metrics['edge_density']:.2f}%\n")
                    f.write(f"Number of Contours: {metrics['num_contours']}\n")
                    f.write(f"Total Edge Length: {metrics['total_edge_length']:.1f} pixels\n")
                    
                    # Add temperature gradient metrics if available
                    if 'mean_temp_gradient' in metrics:
                        f.write(f"Mean Temperature Gradient: {metrics['mean_temp_gradient']:.2f}°C/pixel\n")
                        f.write(f"Max Temperature Gradient: {metrics['max_temp_gradient']:.2f}°C/pixel\n")
                    
                    # Add contour length statistics
                    if metrics['contour_lengths']:
                        mean_length = np.mean(metrics['contour_lengths'])
                        max_length = np.max(metrics['contour_lengths'])
                        min_length = np.min(metrics['contour_lengths'])
                        f.write(f"Average Contour Length: {mean_length:.1f} pixels\n")
                        f.write(f"Longest Contour: {max_length:.1f} pixels\n")
                        f.write(f"Shortest Contour: {min_length:.1f} pixels\n")
            
            messagebox.showinfo(
                "Results Saved", 
                f"Analysis results saved to:\n{os.path.basename(figure_filename)}"
            )
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving results: {str(e)}")