"""
GUI for thermal image comparison analysis.
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
from image_analysis.comparison_detector import ThermalComparisonDetector


class ComparisonAnalysisFrame(ttk.Frame):
    """
    Frame for thermal image comparison analysis with master-slave approach.
    Redesigned with an optimized layout.
    """
    
    def __init__(self, parent, main_app, on_analyze=None):
        """
        Initialize the comparison analysis frame.
        
        Parameters:
            parent: Parent widget
            main_app: Reference to the main application
            on_analyze: Callback function when analysis is performed
        """
        super().__init__(parent, padding="5")
        self.main_app = main_app
        self.on_analyze_callback = on_analyze
        self.comparison_detector = ThermalComparisonDetector()
        
        # Initialize image data
        self.master_data = None
        self.master_timestamp = None
        self.slave_data = None
        self.slave_timestamp = None
        
        # Store last comparison results
        self.last_results = None
        
        # Setup layout
        self.setup_layout()
    
    def setup_layout(self):
        """Setup the frame layout with controls on left, results on right."""
        # Configure grid for the main layout (left controls, right results)
        self.columnconfigure(0, weight=0)  # Control column (fixed width)
        self.columnconfigure(1, weight=1)  # Results column (expandable)
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
        """Setup the control panel with all parameters and options."""
        # Title
        title_label = ttk.Label(parent, text="Image Comparison Controls", font=("TkDefaultFont", 11, "bold"))
        title_label.pack(fill="x", pady=(0, 10))
        
        # Image selection section
        image_frame = ttk.LabelFrame(parent, text="Image Selection", padding="5")
        image_frame.pack(fill="x", pady=(0, 10))
        
        # Master image selection
        master_label = ttk.Label(image_frame, text="Master (Reference) Image:")
        master_label.pack(anchor="w", pady=(0, 5))
        
        # Create a listbox for master image selection
        master_frame = ttk.Frame(image_frame)
        master_frame.pack(fill="x", pady=(0, 10))
        
        master_scroll = ttk.Scrollbar(master_frame)
        master_scroll.pack(side="right", fill="y")
        
        self.master_listbox = tk.Listbox(master_frame, height=4, exportselection=0)
        self.master_listbox.pack(side="left", fill="x", expand=True)
        self.master_listbox.config(yscrollcommand=master_scroll.set)
        master_scroll.config(command=self.master_listbox.yview)
        
        # Slave image selection
        slave_label = ttk.Label(image_frame, text="Slave (Target) Image:")
        slave_label.pack(anchor="w", pady=(0, 5))
        
        # Create a listbox for slave image selection
        slave_frame = ttk.Frame(image_frame)
        slave_frame.pack(fill="x", pady=(0, 5))
        
        slave_scroll = ttk.Scrollbar(slave_frame)
        slave_scroll.pack(side="right", fill="y")
        
        self.slave_listbox = tk.Listbox(slave_frame, height=4, exportselection=0)
        self.slave_listbox.pack(side="left", fill="x", expand=True)
        self.slave_listbox.config(yscrollcommand=slave_scroll.set)
        slave_scroll.config(command=self.slave_listbox.yview)
        
        # Set listbox selection listeners
        self.master_listbox.bind('<<ListboxSelect>>', self.on_master_selected)
        self.slave_listbox.bind('<<ListboxSelect>>', self.on_slave_selected)
        
        # Refresh button for image lists
        refresh_button = ttk.Button(image_frame, text="Refresh Image Lists", command=self.populate_image_lists)
        refresh_button.pack(fill="x", pady=(5, 0))
        
        # Comparison method section
        method_frame = ttk.LabelFrame(parent, text="Comparison Method", padding="5")
        method_frame.pack(fill="x", pady=(0, 10))
        
        # Method selection
        method_label = ttk.Label(method_frame, text="Method:")
        method_label.pack(anchor="w", pady=(0, 5))
        
        self.compare_method_var = tk.StringVar(value="Direct Difference")
        method_combo = ttk.Combobox(
            method_frame, 
            textvariable=self.compare_method_var,
            values=["Direct Difference", "Statistical Change", "Correlation"],
            state="readonly",
            width=20
        )
        method_combo.pack(fill="x", pady=(0, 5))
        
        # Method description
        self.method_description = ttk.Label(
            method_frame,
            text="Calculates the direct temperature difference between master and slave images.",
            wraplength=250,
            justify="left",
            font=("TkDefaultFont", 9, "italic")
        )
        self.method_description.pack(fill="x", pady=(0, 5))
        
        # Method selection callback
        method_combo.bind("<<ComboboxSelected>>", self.on_comparison_method_change)
        
        # Parameter frames
        # Direct Difference parameters
        self.diff_frame = ttk.Frame(method_frame)
        self.diff_frame.pack(fill="x")
        
        # Threshold setting
        threshold_frame = ttk.Frame(self.diff_frame)
        threshold_frame.pack(fill="x", pady=2)
        ttk.Label(threshold_frame, text="Threshold (°C):").pack(side="left")
        self.diff_threshold_var = tk.DoubleVar(value=1.0)
        ttk.Spinbox(
            threshold_frame,
            from_=0.1,
            to=10.0,
            increment=0.1,
            textvariable=self.diff_threshold_var,
            width=5
        ).pack(side="right")
        
        # Relative difference setting
        relative_frame = ttk.Frame(self.diff_frame)
        relative_frame.pack(fill="x", pady=2)
        ttk.Label(relative_frame, text="Use Relative Difference:").pack(side="left")
        self.relative_diff_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            relative_frame,
            variable=self.relative_diff_var
        ).pack(side="right")
        
        # Pre-processing setting
        preproc_frame = ttk.Frame(self.diff_frame)
        preproc_frame.pack(fill="x", pady=2)
        ttk.Label(preproc_frame, text="Pre-processing:").pack(side="left")
        self.preproc_var = tk.StringVar(value="None")
        ttk.Combobox(
            preproc_frame,
            textvariable=self.preproc_var,
            values=["None", "Gradient", "Smoothing"],
            state="readonly",
            width=10
        ).pack(side="right")
        
        # Window size setting
        window_frame = ttk.Frame(self.diff_frame)
        window_frame.pack(fill="x", pady=2)
        ttk.Label(window_frame, text="Window Size:").pack(side="left")
        self.window_size_var = tk.IntVar(value=3)
        self.window_spinbox = ttk.Spinbox(
            window_frame,
            from_=3,
            to=15,
            increment=2,  # Only odd numbers for window size
            textvariable=self.window_size_var,
            width=5,
            state="disabled"
        )
        self.window_spinbox.pack(side="right")
        
        # Bind pre-processing change to update window size state
        self.preproc_var.trace("w", self.on_preproc_change)
        
        # Statistical change frame (hidden initially)
        self.stats_frame = ttk.Frame(method_frame)
        
        # Z-score threshold setting
        zscore_frame = ttk.Frame(self.stats_frame)
        zscore_frame.pack(fill="x", pady=2)
        ttk.Label(zscore_frame, text="Z-score Threshold:").pack(side="left")
        self.zscore_var = tk.DoubleVar(value=2.0)
        ttk.Spinbox(
            zscore_frame,
            from_=0.5,
            to=5.0,
            increment=0.1,
            textvariable=self.zscore_var,
            width=5
        ).pack(side="right")
        
        # Window size for statistical analysis
        stats_window_frame = ttk.Frame(self.stats_frame)
        stats_window_frame.pack(fill="x", pady=2)
        ttk.Label(stats_window_frame, text="Analysis Window:").pack(side="left")
        self.stats_window_var = tk.IntVar(value=5)
        ttk.Spinbox(
            stats_window_frame,
            from_=3,
            to=15,
            increment=2,
            textvariable=self.stats_window_var,
            width=5
        ).pack(side="right")
        
        # Correlation frame (hidden initially)
        self.corr_frame = ttk.Frame(method_frame)
        
        # Window size for correlation
        corr_window_frame = ttk.Frame(self.corr_frame)
        corr_window_frame.pack(fill="x", pady=2)
        ttk.Label(corr_window_frame, text="Correlation Window:").pack(side="left")
        self.corr_window_var = tk.IntVar(value=7)
        ttk.Spinbox(
            corr_window_frame,
            from_=3,
            to=21,
            increment=2,
            textvariable=self.corr_window_var,
            width=5
        ).pack(side="right")
        
        # Correlation threshold
        corr_threshold_frame = ttk.Frame(self.corr_frame)
        corr_threshold_frame.pack(fill="x", pady=2)
        ttk.Label(corr_threshold_frame, text="Correlation Threshold:").pack(side="left")
        self.corr_threshold_var = tk.DoubleVar(value=0.7)
        ttk.Spinbox(
            corr_threshold_frame,
            from_=0.0,
            to=1.0,
            increment=0.05,
            textvariable=self.corr_threshold_var,
            width=5
        ).pack(side="right")
        
        # Action buttons section
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill="x", pady=10)
        
        # Compare button
        self.compare_button = ttk.Button(
            action_frame, 
            text="Compare Images",
            command=self.compare_images,
            state="disabled"
        )
        self.compare_button.pack(fill="x", pady=2)
        
        # Save button
        self.save_button = ttk.Button(
            action_frame, 
            text="Save Results",
            command=self.save_results,
            state="disabled"
        )
        self.save_button.pack(fill="x", pady=2)

        # Populate listboxes with available images
        self.populate_image_lists()
    
    def _setup_results_panel(self, parent):
        """Setup panel to display comparison results."""
        # Results layout frame
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)  # For the figure
        parent.rowconfigure(1, weight=0)  # For the metrics
        
        # Create figure for visualization
        self.fig = Figure(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Initial message
        self.setup_figure()
        
        # Metrics display (collapsible)
        self.metrics_frame = ttk.Frame(parent)
        self.metrics_frame.grid(row=1, column=0, sticky="ew")
        
        # Metrics header with toggle button
        metrics_header = ttk.Frame(self.metrics_frame)
        metrics_header.pack(fill="x")
        
        self.metrics_toggle = ttk.Button(
            metrics_header, 
            text="▼ Comparison Metrics", 
            style="Toolbutton",
            command=self.toggle_metrics
        )
        self.metrics_toggle.pack(side="left")
        
        # Metrics content
        self.metrics_content = ttk.Frame(self.metrics_frame)
        self.metrics_content.pack(fill="x", expand=True)
        
        self.metrics_text = tk.Text(self.metrics_content, height=5, width=50, wrap=tk.WORD)
        self.metrics_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.metrics_content, command=self.metrics_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.metrics_text.config(yscrollcommand=scrollbar.set)
        
        # Initially collapse metrics
        self.metrics_collapsed = False
    
    def populate_image_lists(self):
        """Populate the image listboxes with available files."""
        # Clear existing items
        self.master_listbox.delete(0, tk.END)
        self.slave_listbox.delete(0, tk.END)
        
        # Check if there are files to display
        if not hasattr(self.main_app, 'csv_files') or not self.main_app.csv_files:
            return
        
        # Add files to both listboxes
        for i, file_path in enumerate(self.main_app.csv_files):
            # Get filename without path
            filename = os.path.basename(file_path)
            # Get timestamp if available
            timestamp_str = ""
            if hasattr(self.main_app, 'timestamps') and i < len(self.main_app.timestamps):
                timestamp_str = self.main_app.timestamps[i].strftime(" (%Y-%m-%d %H:%M:%S)")
            
            # Format display string with index, filename and timestamp
            display_str = f"{i+1}: {filename}{timestamp_str}"
            
            # Add to both listboxes
            self.master_listbox.insert(tk.END, display_str)
            self.slave_listbox.insert(tk.END, display_str)
        
        # Update button states
        # self._update_button_states()
    
    def on_master_selected(self, event=None):
        """Handle master image selection from listbox."""
        selection = self.master_listbox.curselection()
        if not selection:  # No selection
            self.master_data = None
            self.master_timestamp = None
            self._update_button_states()
            return
        
        # Get the selected index
        index = selection[0]
        if index < 0 or index >= len(self.main_app.csv_files):
            return
        
        try:
            # Load the selected file data
            file_path = self.main_app.csv_files[index]
            from thermal_data import ThermalDataHandler
            self.master_data = ThermalDataHandler.load_csv_data(
                file_path, self.main_app.camera_type)
            self.master_timestamp = self.main_app.timestamps[index]
            
            # Update button states
            self._update_button_states()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load master image: {str(e)}")
            self.master_data = None
            self.master_timestamp = None
            self._update_button_states()
    
    def on_slave_selected(self, event=None):
        """Handle slave image selection from listbox."""
        selection = self.slave_listbox.curselection()
        if not selection:  # No selection
            self.slave_data = None
            self.slave_timestamp = None
            self._update_button_states()
            return
        
        # Get the selected index
        index = selection[0]
        if index < 0 or index >= len(self.main_app.csv_files):
            return
        
        try:
            # Load the selected file data
            file_path = self.main_app.csv_files[index]
            from thermal_data import ThermalDataHandler
            self.slave_data = ThermalDataHandler.load_csv_data(
                file_path, self.main_app.camera_type)
            self.slave_timestamp = self.main_app.timestamps[index]
            
            # Update button states
            self._update_button_states()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load slave image: {str(e)}")
            self.slave_data = None
            self.slave_timestamp = None
            self._update_button_states()
    
    def setup_figure(self):
        """Setup the initial figure with placeholder message."""
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Thermal Image Comparison")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.text(
            0.5, 0.5, 
            "Select master and slave images to begin comparison.\nThen click 'Compare Images'.",
            horizontalalignment='center',
            verticalalignment='center',
            transform=self.ax.transAxes,
            fontsize=12
        )
        self.canvas.draw()
    
    def toggle_metrics(self):
        """Toggle the visibility of the metrics panel."""
        if self.metrics_collapsed:
            self.metrics_content.pack(fill="x", expand=True)
            self.metrics_toggle.config(text="▼ Comparison Metrics")
            self.metrics_collapsed = False
        else:
            self.metrics_content.pack_forget()
            self.metrics_toggle.config(text="► Comparison Metrics")
            self.metrics_collapsed = True
    
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
            frame.pack_forget()
        
        if method == "Direct Difference":
            self.diff_frame.pack(fill="x")
        elif method == "Statistical Change":
            self.stats_frame.pack(fill="x")
        elif method == "Correlation":
            self.corr_frame.pack(fill="x")
    
    def on_preproc_change(self, *args):
        """Handle change in pre-processing option."""
        preproc = self.preproc_var.get()
        
        if preproc == "None":
            self.window_spinbox.config(state="disabled")
        else:
            self.window_spinbox.config(state="normal")
    
    def _update_button_states(self):
        """Update states of action buttons based on available data."""
        # Check if buttons have been created
        if not hasattr(self, 'compare_button') or not hasattr(self, 'save_button'):
            return
            
        if self.master_data is not None and self.slave_data is not None:
            self.compare_button.config(state="normal")
        else:
            self.compare_button.config(state="disabled")
        
        if self.last_results is not None:
            self.save_button.config(state="normal")
        else:
            self.save_button.config(state="disabled")
    
    def compare_images(self):
        """Compare master and slave images with selected method."""
        if self.master_data is None or self.slave_data is None:
            messagebox.showwarning("Missing Data", "Both master and slave images must be selected.")
            return
        
        try:
            # Get comparison method and parameters
            method = self.compare_method_var.get()
            
            # Perform comparison based on selected method
            if method == "Direct Difference":
                # Get direct difference parameters
                threshold = self.diff_threshold_var.get()
                relative = self.relative_diff_var.get()
                preproc = self.preproc_var.get()
                window_size = self.window_size_var.get() if preproc != "None" else None
                
                # Perform comparison with selected method
                if preproc == "Gradient":
                    result = self.comparison_detector.compute_gradient_preprocessed_difference(
                        self.master_data, 
                        self.slave_data, 
                        window_size=window_size,
                        threshold=threshold, 
                        relative=relative
                    )
                elif preproc == "Smoothing":
                    # First smooth the data, then compute difference
                    result = self.comparison_detector.compute_smoothed_difference(
                        self.master_data, 
                        self.slave_data, 
                        window_size=window_size,
                        threshold=threshold, 
                        relative=relative
                    )
                else:
                    # Regular direct difference
                    result = self.comparison_detector.compute_difference(
                        self.master_data, 
                        self.slave_data, 
                        threshold=threshold, 
                        relative=relative
                    )
                
            elif method == "Statistical Change":
                # Get statistical change parameters
                zscore_threshold = self.zscore_var.get()
                window_size = self.stats_window_var.get()
                
                # Perform statistical comparison
                result = self.comparison_detector.compute_statistical_significance(
                    self.master_data, 
                    self.slave_data, 
                    window_size=window_size, 
                    zscore_threshold=zscore_threshold
                )
                
            elif method == "Correlation":
                # Get correlation parameters
                window_size = self.corr_window_var.get()
                corr_threshold = self.corr_threshold_var.get()
                
                # Perform correlation analysis
                result = self.comparison_detector.compute_spatial_correlation(
                    self.master_data, 
                    self.slave_data, 
                    window_size=window_size,
                    threshold=corr_threshold
                )
            
            # Store results for later use
            self.last_results = {
                'method': method,
                'master_data': self.master_data,
                'slave_data': self.slave_data,
                'master_timestamp': self.master_timestamp,
                'slave_timestamp': self.slave_timestamp,
                'result': result,
                'parameters': {
                    'method': method,
                    # Additional parameters will be added based on method
                }
            }
            
            # Add method-specific parameters
            if method == "Direct Difference":
                self.last_results['parameters'].update({
                    'threshold': self.diff_threshold_var.get(),
                    'relative': self.relative_diff_var.get(),
                    'preprocessing': self.preproc_var.get(),
                    'window_size': self.window_size_var.get() if self.preproc_var.get() != "None" else None
                })
            elif method == "Statistical Change":
                self.last_results['parameters'].update({
                    'zscore_threshold': self.zscore_var.get(),
                    'window_size': self.stats_window_var.get()
                })
            elif method == "Correlation":
                self.last_results['parameters'].update({
                    'window_size': self.corr_window_var.get(),
                    'correlation_threshold': self.corr_threshold_var.get()
                })
            
            # Calculate metrics
            metrics = self.comparison_detector.calculate_metrics(result)
            self.last_results['metrics'] = metrics
            
            # Visualize results
            self.visualize_results()
            
            # Display metrics
            self.display_metrics(metrics)
            
            # Enable save button
            self.save_button.config(state="normal")
            
            # Call callback if provided
            if self.on_analyze_callback:
                self.on_analyze_callback(self.last_results)
                
        except Exception as e:
            messagebox.showerror("Comparison Error", f"Error during image comparison: {str(e)}")
    
    def visualize_results(self):
        """Visualize the comparison results."""
        if not self.last_results:
            return
        
        # Clear figure
        self.fig.clear()
        
        # Get data from results
        method = self.last_results['method']
        result = self.last_results['result']
        master_timestamp = self.last_results['master_timestamp']
        slave_timestamp = self.last_results['slave_timestamp']
        
        # Create a 1x2 subplot arrangement for difference map and histogram
        gs = self.fig.add_gridspec(1, 2, wspace=0.3)
        
        # Plot result based on method
        if method == "Direct Difference":
            # For direct difference, use diverging colormap centered at zero
            ax1 = self.fig.add_subplot(gs[0, 0])  # Difference map
            ax2 = self.fig.add_subplot(gs[0, 1])  # Histogram
            
            # Get difference data
            diff_data = result['difference']
            # vmax = np.max(np.abs(diff_data))
            # vmin = -vmax
            # Percentile based vmin/vmax
            vmax = np.percentile(diff_data, 90)
            vmin = np.percentile(diff_data, 10)
            
            # Show difference map
            im_diff = ax1.imshow(
                diff_data, 
                cmap='YlOrRd',
                vmin=vmin, 
                vmax=vmax
            )
            title = "Temperature Difference"
            if self.last_results['parameters']['relative']:
                title += " (%)"
            title += f"\nMaster: {master_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            title += f"\nSlave: {slave_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            ax1.set_title(title, fontsize=9)
            self.fig.colorbar(im_diff, ax=ax1, fraction=0.046, pad=0.04)
            ax1.set_xticks([])
            ax1.set_yticks([])
            
            # Highlight significant differences if threshold was applied
            if 'significant_changes' in result and result['significant_changes'] is not None:
                # Create mask for areas exceeding threshold
                masked_data = np.ma.masked_where(~result['significant_changes'], diff_data)
                ax2.imshow(masked_data, cmap='Greens', alpha=0.3)
                ax2.set_title("Significant Changes\n(Difference > threshold)", fontsize=9)
                ax2.set_xticks([])
                ax2.set_yticks([])
            
            # Show histogram of differences
            # ax2.hist(diff_data.flatten(), bins=50, color='skyblue', edgecolor='black', alpha=0.7)
            # ax2.axvline(x=0, color='r', linestyle='--', alpha=0.3)
            # ax2.set_title("Difference Histogram", fontsize=9)
            # ax2.set_xlabel("Temperature Difference")
            # ax2.set_ylabel("Frequency")
            
        elif method == "Statistical Change":
            # For statistical change, show z-scores and significance
            ax1 = self.fig.add_subplot(gs[0, 0])  # Z-score map
            ax2 = self.fig.add_subplot(gs[0, 1])  # Significant changes or histogram
            
            # Get z-score data
            zscore_data = result['zscores']
            vmax_z = np.percentile(zscore_data, 90)
            vmin_z = np.percentile(zscore_data, 10)
            
            # Show z-score map
            im_stat = ax1.imshow(
                zscore_data, 
                cmap='coolwarm', 
                vmin=vmin_z, 
                vmax=vmax_z
            )
            title = "Statistical Significance (Z-score)"
            title += f"\nMaster: {master_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            title += f"\nSlave: {slave_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            ax1.set_title(title, fontsize=9)
            self.fig.colorbar(im_stat, ax=ax1, fraction=0.046, pad=0.04)
            ax1.set_xticks([])
            ax1.set_yticks([])
            
            # Show significant changes mask
            if 'significant_changes' in result and result['significant_changes'] is not None:
                ax2.imshow(result['significant_changes'], cmap='binary')
                ax2.set_title("Significant Changes\n(Z-score > threshold)", fontsize=9)
                ax2.set_xticks([])
                ax2.set_yticks([])
            else:
                # Fallback to histogram of z-scores
                ax2.hist(zscore_data.flatten(), bins=50, color='skyblue', edgecolor='black', alpha=0.7)
                ax2.axvline(x=0, color='r', linestyle='--', alpha=0.3)
                ax2.set_title("Z-score Histogram", fontsize=9)
                ax2.set_xlabel("Z-score")
                ax2.set_ylabel("Frequency")
            
        elif method == "Correlation":
            # For correlation, show correlation coefficient map and low correlation areas
            ax1 = self.fig.add_subplot(gs[0, 0])  # Correlation map
            ax2 = self.fig.add_subplot(gs[0, 1])  # Low correlation areas or histogram
            
            # Get correlation data
            corr_data = result['correlation_map']
            
            # Show correlation map
            im_corr = ax1.imshow(
                corr_data, 
                cmap='seismic', 
                vmin=-1, 
                vmax=1
            )
            title = "Correlation Coefficient"
            title += f"\nMaster: {master_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            title += f"\nSlave: {slave_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            ax1.set_title(title, fontsize=9)
            self.fig.colorbar(im_corr, ax=ax1, fraction=0.046, pad=0.04)
            ax1.set_xticks([])
            ax1.set_yticks([])
            
            # Show areas of low correlation
            if 'low_correlation_mask' in result and result['low_correlation_mask'] is not None:
                ax2.imshow(result['low_correlation_mask'], cmap='binary_r')
                ax2.set_title("Pattern Change Areas\n(Low Correlation)", fontsize=9)
                ax2.set_xticks([])
                ax2.set_yticks([])
            else:
                # Fallback to histogram of correlation coefficients
                ax2.hist(corr_data.flatten(), bins=50, color='skyblue', edgecolor='black', alpha=0.7)
                ax2.axvline(x=0, color='r', linestyle='--', alpha=0.3)
                ax2.set_title("Correlation Coefficient Histogram", fontsize=9)
                ax2.set_xlabel("Correlation Coefficient")
                ax2.set_ylabel("Frequency")
        
        # Add a timestamp difference note at the bottom of the figure
        time_diff = self.slave_timestamp - self.master_timestamp
        hours, remainder = divmod(time_diff.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        time_diff_str = f"Time Between Images: {int(hours)}h {int(minutes)}m {int(seconds)}s"
        
        self.fig.text(0.5, 0.01, time_diff_str, ha='center', fontsize=8)
        
        # Adjust layout
        self.fig.tight_layout(rect=[0, 0.03, 1, 0.97])  # Make room for the timestamp note
        self.canvas.draw()
    
    def display_metrics(self, metrics):
        """Display comparison metrics in the metrics panel."""
        if not metrics:
            return
            
        # Format metrics as text
        text = f"Comparison Metrics ({self.last_results['method']}):\n\n"
        
        # Common metrics for all methods
        if 'mean_diff' in metrics:
            text += f"Mean Difference: {metrics['mean_diff']:.3f}°C\n"
        if 'max_diff' in metrics:
            text += f"Maximum Difference: {metrics['max_diff']:.3f}°C\n"
        if 'min_diff' in metrics:
            text += f"Minimum Difference: {metrics['min_diff']:.3f}°C\n"
        if 'std_diff' in metrics:
            text += f"Standard Deviation: {metrics['std_diff']:.3f}°C\n"
        
        # Method-specific metrics
        method = self.last_results['method']
        
        if method == "Direct Difference":
            if 'significant_pixel_count' in metrics:
                total_pixels = self.master_data.size
                percentage = 100 * metrics['significant_pixel_count'] / total_pixels
                text += f"Significant Changes: {metrics['significant_pixel_count']} pixels "
                text += f"({percentage:.2f}% of image)\n"
                
            if 'positive_changes' in metrics:
                text += f"Warming Areas: {metrics['positive_changes']} pixels\n"
            if 'negative_changes' in metrics:
                text += f"Cooling Areas: {metrics['negative_changes']} pixels\n"
                
        elif method == "Statistical Change":
            if 'mean_zscore' in metrics:
                text += f"Mean Z-score: {metrics['mean_zscore']:.3f}\n"
            if 'significant_pixel_count' in metrics:
                total_pixels = self.master_data.size
                percentage = 100 * metrics['significant_pixel_count'] / total_pixels
                text += f"Statistically Significant Changes: {metrics['significant_pixel_count']} pixels "
                text += f"({percentage:.2f}% of image)\n"
                
        elif method == "Correlation":
            if 'mean_correlation' in metrics:
                text += f"Mean Correlation: {metrics['mean_correlation']:.3f}\n"
            if 'low_correlation_count' in metrics:
                total_pixels = self.master_data.size
                percentage = 100 * metrics['low_correlation_count'] / total_pixels
                text += f"Areas with Pattern Change: {metrics['low_correlation_count']} pixels "
                text += f"({percentage:.2f}% of image)\n"
        
        # Add image selection information
        master_idx = self.master_listbox.curselection()[0] + 1 if self.master_listbox.curselection() else 0
        slave_idx = self.slave_listbox.curselection()[0] + 1 if self.slave_listbox.curselection() else 0
        text += f"\nMaster Image: #{master_idx}\n"
        text += f"Slave Image: #{slave_idx}\n"
        
        # Add time information
        time_diff = self.slave_timestamp - self.master_timestamp
        hours, remainder = divmod(time_diff.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        text += f"Time Between Images: {int(hours)}h {int(minutes)}m {int(seconds)}s\n"
        
        # Update text widget
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(tk.END, text)
        
        # Ensure metrics are visible
        if self.metrics_collapsed:
            self.toggle_metrics()
    
    def save_results(self):
        """Save the comparison results."""
        if not self.last_results:
            messagebox.showwarning("No Results", "No comparison results to save.")
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
            
            # Get timestamps for filename
            m_timestamp = self.last_results['master_timestamp'].strftime("%Y%m%d_%H%M%S")
            s_timestamp = self.last_results['slave_timestamp'].strftime("%Y%m%d_%H%M%S")
            
            # Get method name
            method = self.last_results['method'].lower().replace(" ", "_")
            
            # Create base filename
            base_filename = os.path.join(save_dir, f"{method}_comparison_{m_timestamp}_vs_{s_timestamp}")
            
            # Save figure as image
            figure_filename = f"{base_filename}.png"
            self.fig.savefig(figure_filename, dpi=300, bbox_inches='tight')
            
            # Save difference/result data as CSV
            result = self.last_results['result']
            if 'difference' in result:
                diff_filename = f"{base_filename}_difference.csv"
                np.savetxt(diff_filename, result['difference'], delimiter=',')
            elif 'zscores' in result:
                zscores_filename = f"{base_filename}_zscores.csv"
                np.savetxt(zscores_filename, result['zscores'], delimiter=',')
            elif 'correlation_map' in result:
                corr_filename = f"{base_filename}_correlation.csv"
                np.savetxt(corr_filename, result['correlation_map'], delimiter=',')
            
            # Save metrics as text file
            if self.last_results['metrics']:
                metrics_filename = f"{base_filename}_metrics.txt"
                with open(metrics_filename, 'w') as f:
                    # Write comparison information
                    f.write(f"Thermal Image Comparison Results\n")
                    f.write(f"==============================\n\n")
                    f.write(f"Method: {self.last_results['method']}\n")
                    f.write(f"Master Image: {m_timestamp}\n")
                    f.write(f"Slave Image: {s_timestamp}\n")
                    f.write(f"Time Between Images: {(self.last_results['slave_timestamp'] - self.last_results['master_timestamp'])}\n\n")
                    
                    # Write parameters
                    f.write("Parameters:\n")
                    for key, value in self.last_results['parameters'].items():
                        f.write(f"  {key}: {value}\n")
                    f.write("\n")
                    
                    # Write metrics
                    f.write("Metrics:\n")
                    metrics = self.last_results['metrics']
                    for key, value in metrics.items():
                        if isinstance(value, (int, float)):
                            f.write(f"  {key}: {value:.4f}\n")
                        else:
                            f.write(f"  {key}: {value}\n")
            
            messagebox.showinfo(
                "Results Saved", 
                f"Comparison results saved to:\n{os.path.basename(figure_filename)}"
            )
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving results: {str(e)}")