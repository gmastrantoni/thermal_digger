"""
Improved thermal change detection window with enhanced layout for better visualization.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from image_analysis.edge_gui import EdgeDetectionFrame
from image_analysis.comparison_gui import ComparisonAnalysisFrame


class ChangeDetectionWindow(tk.Toplevel):
    """
    Modal window for thermal change detection with improved layout.
    """
    
    def __init__(self, parent, main_app):
        """
        Initialize the change detection window.
        
        Parameters:
            parent: Parent window
            main_app: Reference to the main application (ThermalImageGUI instance)
        """
        super().__init__(parent)
        self.title("Thermal Image Analysis")
        self.geometry("1000x700")  # Larger default size
        self.minsize(900, 650)
        
        # Store reference to main app
        self.main_app = main_app
        
        # Configure root window to expand
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Create tab frames
        self.edge_tab = ttk.Frame(self.notebook)
        self.other_analysis_tab = ttk.Frame(self.notebook)
        self.image_comparison_tab = ttk.Frame(self.notebook)
        
        # Configure tab frames to expand
        for tab in [self.edge_tab, self.other_analysis_tab, self.image_comparison_tab]:
            tab.columnconfigure(0, weight=1)
            tab.rowconfigure(0, weight=1)
        
        # Add tabs to notebook
        self.notebook.add(self.edge_tab, text="Edge Detection")
        self.notebook.add(self.other_analysis_tab, text="Other Analysis Methods")
        self.notebook.add(self.image_comparison_tab, text="Image Comparison")
        
        # Setup tab contents
        self._setup_edge_tab()
        self._setup_other_analysis_tab()
        self._setup_image_comparison_tab()
        
        # Add status bar at the bottom
        status_frame = ttk.Frame(self)
        status_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 5))
        status_frame.columnconfigure(0, weight=1)
        
        # Status label (left)
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.grid(row=0, column=0, sticky="w")
        
        # Close button (right)
        ttk.Button(status_frame, text="Close", command=self.destroy).grid(row=0, column=1, sticky="e")
        
        # Check if we have valid data to work with
        if not self._check_data():
            messagebox.showwarning(
                "No Data",
                "No thermal data is currently loaded. Please load data in the main application first."
            )
            self.status_label.config(text="Warning: No thermal data loaded")
        else:
            self.status_label.config(text=f"Loaded image {self.main_app.current_image_index + 1} of {len(self.main_app.csv_files)}")
    
    def _check_data(self):
        """Check if there is valid data to work with."""
        return (hasattr(self.main_app, 'current_data') and 
                self.main_app.current_data is not None and
                len(self.main_app.csv_files) > 0)
    
    def _setup_edge_tab(self):
        """Setup the edge detection tab with the improved frame."""
        # Add EdgeDetectionFrame that fills the entire tab
        self.edge_frame = EdgeDetectionFrame(self.edge_tab, self.main_app, self.on_analysis_complete)
        self.edge_frame.grid(row=0, column=0, sticky="nsew")
    
    def _setup_other_analysis_tab(self):
        """Setup the tab for other analysis methods with placeholder."""
        # Create a more visually appealing placeholder
        placeholder_frame = ttk.Frame(self.other_analysis_tab, padding="20")
        placeholder_frame.pack(expand=True, fill="both")
        
        # Add some styling
        title_label = ttk.Label(
            placeholder_frame, 
            text="Additional Analysis Methods",
            font=("TkDefaultFont", 14, "bold")
        )
        title_label.pack(pady=(20, 10))
        
        description = ttk.Label(
            placeholder_frame,
            text="The following analysis methods will be implemented in future updates:",
            wraplength=500,
            justify="center"
        )
        description.pack(pady=(0, 20))
        
        # Create a frame for the method list
        methods_frame = ttk.Frame(placeholder_frame)
        methods_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Define methods with descriptions
        methods = [
            {
                "name": "Statistical Outlier Detection",
                "description": "Identifies thermal anomalies that statistically deviate from surrounding temperatures."
            },
            {
                "name": "Thermal Contour Analysis",
                "description": "Creates isothermal contours to define regions of similar temperature."
            },
            {
                "name": "K-means Clustering",
                "description": "Groups pixels into thermal zones based on temperature similarity."
            },
            {
                "name": "Watershed Segmentation",
                "description": "Advanced segmentation of thermal regions using gradient-based boundaries."
            }
        ]
        
        # Add each method with a visual indicator
        for i, method in enumerate(methods):
            method_frame = ttk.Frame(methods_frame)
            method_frame.pack(fill="x", pady=10)
            
            # Create a colored indicator (coming soon badge)
            indicator = tk.Canvas(method_frame, width=50, height=50, bd=0, highlightthickness=0)
            indicator.create_oval(10, 10, 40, 40, fill="#e0e0e0", outline="#cccccc")
            indicator.create_text(25, 25, text=f"{i+1}", font=("TkDefaultFont", 12, "bold"))
            indicator.pack(side="left", padx=(0, 15))
            
            # Method details
            details_frame = ttk.Frame(method_frame)
            details_frame.pack(side="left", fill="x", expand=True)
            
            ttk.Label(
                details_frame, 
                text=method["name"],
                font=("TkDefaultFont", 12, "bold")
            ).pack(anchor="w")
            
            ttk.Label(
                details_frame,
                text=method["description"],
                wraplength=500,
                justify="left"
            ).pack(anchor="w", pady=(2, 0))
            
            # Coming soon label
            ttk.Label(
                method_frame,
                text="Coming Soon",
                foreground="#888888",
                font=("TkDefaultFont", 9, "italic")
            ).pack(side="right", padx=10)
    
    def _setup_image_comparison_tab(self):
        """Setup the image comparison tab with the optimized ComparisonAnalysisFrame."""        
        # Configure the tab for proper expansion
        self.image_comparison_tab.columnconfigure(0, weight=1)
        self.image_comparison_tab.rowconfigure(0, weight=1)
        
        # Create the comparison frame
        self.comparison_frame = ComparisonAnalysisFrame(
            self.image_comparison_tab, 
            self.main_app, 
            self.on_comparison_complete
        )
        self.comparison_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    def on_comparison_complete(self, results):
        """
        Callback when comparison analysis is complete.
        
        Parameters:
            results: Comparison analysis results
        """
        # Update status bar with comparison info
        if results and 'metrics' in results:
            metrics = results['metrics']
            if 'mean_diff' in metrics:
                self.status_label.config(
                    text=f"Comparison complete: Mean diff {metrics['mean_diff']:.2f}°C, Max diff {metrics['max_diff']:.2f}°C"
                )
            elif 'mean_zscore' in metrics:
                self.status_label.config(
                    text=f"Statistical comparison complete: Mean Z-score {metrics['mean_zscore']:.2f}"
                )
            elif 'mean_correlation' in metrics:
                self.status_label.config(
                    text=f"Correlation analysis complete: Mean correlation {metrics['mean_correlation']:.2f}"
                )
    
    def on_analysis_complete(self, results):
        """
        Callback when analysis is complete.
        
        Parameters:
            results: Analysis results
        """
        # Update status bar with analysis info
        if results and 'metrics' in results:
            metrics = results['metrics']
            self.status_label.config(
                text=f"Analysis complete: {metrics['num_edge_pixels']} edge pixels, {metrics['edge_density']:.2f}% edge density"
            )