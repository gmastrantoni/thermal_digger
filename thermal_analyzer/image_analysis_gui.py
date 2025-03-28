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
        """Setup the image comparison tab with an improved layout."""
        # Main container with padding
        container = ttk.Frame(self.image_comparison_tab, padding=10)
        container.grid(row=0, column=0, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)  # Make the results area expandable
        
        # Image selection section in a single frame with two columns
        selection_frame = ttk.LabelFrame(container, text="Image Selection", padding=10)
        selection_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        selection_frame.columnconfigure(0, weight=1)
        selection_frame.columnconfigure(1, weight=1)
        
        # Master image column
        master_frame = ttk.Frame(selection_frame)
        master_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        ttk.Label(
            master_frame, 
            text="Master (Reference) Image",
            font=("TkDefaultFont", 10, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        ttk.Button(
            master_frame, 
            text="Use Current Image as Master",
            command=self.set_master_image
        ).pack(fill="x")
        
        self.master_label = ttk.Label(
            master_frame, 
            text="No master image selected",
            background="#f0f0f0",
            padding=5
        )
        self.master_label.pack(fill="x", pady=(5, 0))
        
        # Slave image column
        slave_frame = ttk.Frame(selection_frame)
        slave_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        ttk.Label(
            slave_frame, 
            text="Slave (Target) Image",
            font=("TkDefaultFont", 10, "bold")
        ).pack(anchor="w", pady=(0, 5))
        
        ttk.Button(
            slave_frame, 
            text="Use Current Image as Slave",
            command=self.set_slave_image
        ).pack(fill="x")
        
        self.slave_label = ttk.Label(
            slave_frame, 
            text="No slave image selected",
            background="#f0f0f0",
            padding=5
        )
        self.slave_label.pack(fill="x", pady=(5, 0))
        
        # Comparison method selection
        method_frame = ttk.LabelFrame(container, text="Comparison Method", padding=10)
        method_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        method_frame.columnconfigure(1, weight=1)
        
        # Method selection with icon
        method_row = ttk.Frame(method_frame)
        method_row.pack(fill="x", pady=(0, 5))
        
        ttk.Label(method_row, text="Method:").pack(side="left", padx=(0, 10))
        
        self.compare_method_var = tk.StringVar(value="Direct Difference")
        method_combo = ttk.Combobox(
            method_row, 
            textvariable=self.compare_method_var,
            values=["Direct Difference", "Statistical Change", "Correlation"],
            state="readonly",
            width=20
        )
        method_combo.pack(side="left")
        
        # Description for the selected method
        self.method_description = ttk.Label(
            method_frame,
            text="Calculates the direct temperature difference between master and slave images.",
            wraplength=700,
            justify="left",
            font=("TkDefaultFont", 9, "italic")
        )
        self.method_description.pack(anchor="w", pady=(0, 5))
        
        # Method selection callback
        method_combo.bind("<<ComboboxSelected>>", self.on_comparison_method_change)
        
        # Parameter frames (initially only showing direct difference)
        self.diff_frame = ttk.Frame(method_frame)
        self.diff_frame.pack(fill="x")
        
        threshold_row = ttk.Frame(self.diff_frame)
        threshold_row.pack(fill="x", pady=2)
        ttk.Label(threshold_row, text="Threshold (°C):").pack(side="left", padx=(0, 10))
        self.diff_threshold_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(
            threshold_row,
            from_=0.1,
            to=10.0,
            increment=0.1,
            textvariable=self.diff_threshold_var,
            width=10
        ).pack(side="left")
        
        relative_row = ttk.Frame(self.diff_frame)
        relative_row.pack(fill="x", pady=2)
        ttk.Label(relative_row, text="Use Relative Difference:").pack(side="left", padx=(0, 10))
        self.relative_diff_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            relative_row,
            variable=self.relative_diff_var
        ).pack(side="left")
        
        # Stats frame (hidden initially)
        self.stats_frame = ttk.Frame(method_frame)
        
        # Correlation frame (hidden initially)
        self.corr_frame = ttk.Frame(method_frame)
        
        # Results area with placeholder
        results_frame = ttk.LabelFrame(container, text="Comparison Results", padding=10)
        results_frame.grid(row=2, column=0, sticky="nsew")
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # Create a placeholder for results
        placeholder = ttk.Frame(results_frame)
        placeholder.pack(expand=True, fill="both")
        
        ttk.Label(
            placeholder,
            text="Select master and slave images to compare",
            font=("TkDefaultFont", 12)
        ).pack(expand=True)
        
        # Create figure for results (not shown initially)
        self.comparison_fig = Figure(figsize=(8, 6), constrained_layout=True)
        self.comparison_canvas = FigureCanvasTkAgg(self.comparison_fig, master=results_frame)
        
        # Action buttons at the bottom
        button_frame = ttk.Frame(container)
        button_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Compare button (disabled initially)
        self.compare_button = ttk.Button(
            button_frame, 
            text="Compare Images",
            command=self.compare_images,
            state="disabled"
        )
        self.compare_button.grid(row=0, column=0, sticky="e", padx=(0, 5))
        
        # Save button (disabled initially)
        self.save_compare_button = ttk.Button(
            button_frame, 
            text="Save Results",
            command=self.save_comparison_results,
            state="disabled"
        )
        self.save_compare_button.grid(row=0, column=1, sticky="w", padx=(5, 0))
    
    def on_comparison_method_change(self, event=None):
        """Handle change of comparison method."""
        method = self.compare_method_var.get()
        
        # Update method description
        descriptions = {
            "Direct Difference": "Calculates the direct temperature difference between master and slave images.",
            "Statistical Change": "Uses statistical methods to identify significant temperature changes relative to local variability.",
            "Correlation": "Measures the spatial correlation between temperature patterns in the two images."
        }
        
        self.method_description.config(text=descriptions.get(method, ""))
        
        # Show/hide parameter frames based on selected method
        frames = [self.diff_frame, self.stats_frame, self.corr_frame]
        for frame in frames:
            try:
                frame.pack_forget()
            except:
                pass
        
        if method == "Direct Difference":
            self.diff_frame.pack(fill="x")
        elif method == "Statistical Change":
            self.stats_frame.pack(fill="x")
        elif method == "Correlation":
            self.corr_frame.pack(fill="x")
    
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
    
    def set_master_image(self):
        """Set current image as master reference."""
        if not self._check_data():
            messagebox.showwarning("No Data", "No thermal data available.")
            return
        
        # Store reference to current data
        self.master_data = self.main_app.current_data.copy()
        self.master_timestamp = self.main_app.timestamps[self.main_app.current_image_index]
        
        # Update label with more detail
        self.master_label.config(
            text=f"Image {self.main_app.current_image_index + 1} - " + 
                 f"{self.master_timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            background="#e6f3ff"  # Light blue background to indicate selection
        )
        
        # Update status
        self.status_label.config(text="Master image set")
        
        # Enable compare button if both master and slave are set
        if hasattr(self, 'slave_data') and self.slave_data is not None:
            self.compare_button.config(state="normal")
    
    def set_slave_image(self):
        """Set current image as slave target."""
        if not self._check_data():
            messagebox.showwarning("No Data", "No thermal data available.")
            return
        
        # Store reference to current data
        self.slave_data = self.main_app.current_data.copy()
        self.slave_timestamp = self.main_app.timestamps[self.main_app.current_image_index]
        
        # Update label with more detail
        self.slave_label.config(
            text=f"Image {self.main_app.current_image_index + 1} - " + 
                 f"{self.slave_timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            background="#fff2e6"  # Light orange background to indicate selection
        )
        
        # Update status
        self.status_label.config(text="Slave image set")
        
        # Enable compare button if both master and slave are set
        if hasattr(self, 'master_data') and self.master_data is not None:
            self.compare_button.config(state="normal")
    
    def compare_images(self):
        """Compare master and slave images."""
        if not hasattr(self, 'master_data') or not hasattr(self, 'slave_data'):
            messagebox.showwarning("Missing Data", "Both master and slave images must be selected.")
            return
        
        # For now, just show a placeholder message
        messagebox.showinfo(
            "Compare Images", 
            "Image comparison functionality will be implemented in future updates."
        )
        
    def save_comparison_results(self):
        """Save comparison results."""
        messagebox.showinfo(
            "Save Results", 
            "Saving comparison results will be implemented in future updates."
        )