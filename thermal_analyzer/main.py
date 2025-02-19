import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import numpy as np
import os
from PIL import Image, ImageTk
from thermal_data import ThermalDataHandler
from thermal_plot import ThermalPlotter
from utils.config import config

class ThermalImageGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Thermal Image Analyzer")
        
        # Configure root window to expand
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Data storage
        self.csv_files = []
        self.current_data = None
        self.polygon_coords = []
        self.collecting_points = False
        self.timestamps = []
        self.current_image_index = 0
        self.selection_mode = "point"  # or "polygon"
        self.selected_point = None
        
        # Create main frames
        self.control_frame = ttk.Frame(self.root, padding="5")
        self.control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.plot_frame = ttk.Frame(self.root, padding="5")
        self.plot_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create footer frame
        self.footer_frame = ttk.Frame(self.root, padding="5", style="Footer.TFrame")
        self.footer_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Initialize plotter
        self.plotter = ThermalPlotter(self.plot_frame)
        
        # Setup GUI components
        self.setup_controls()
        self.setup_footer()
        
        # Connect mouse events
        self.plotter.get_click_handler().mpl_connect('button_press_event', self.on_click)

    def setup_controls(self):
        """Setup control buttons"""
        # Load Files section
        ttk.Button(self.control_frame, text="Load CSV Files", 
                  command=self.load_csv_files).grid(row=0, column=0, pady=5)
        
        # Add separator
        ttk.Separator(self.control_frame, orient='horizontal').grid(
            row=1, column=0, sticky='ew', pady=10)
            
        # Image Navigation section
        nav_frame = ttk.Frame(self.control_frame)
        nav_frame.grid(row=2, column=0, pady=5)
        
        ttk.Button(nav_frame, text="◀ Previous", 
                  command=self.previous_image).grid(row=0, column=0, padx=2)
        self.image_label = ttk.Label(nav_frame, text="Image: 0/0")
        self.image_label.grid(row=0, column=1, padx=5)
        ttk.Button(nav_frame, text="Next ▶", 
                  command=self.next_image).grid(row=0, column=2, padx=2)
        
        # Add separator
        ttk.Separator(self.control_frame, orient='horizontal').grid(
            row=3, column=0, sticky='ew', pady=10)
        
        # Selection Mode section
        mode_frame = ttk.Frame(self.control_frame)
        mode_frame.grid(row=4, column=0, pady=5)
        
        self.mode_var = tk.StringVar(value="point")
        ttk.Radiobutton(mode_frame, text="Point", variable=self.mode_var, 
                       value="point", command=self.change_mode).grid(row=0, column=0, padx=5)
        ttk.Radiobutton(mode_frame, text="Polygon", variable=self.mode_var, 
                       value="polygon", command=self.change_mode).grid(row=0, column=1, padx=5)
        
        # Polygon controls section
        self.polygon_frame = ttk.Frame(self.control_frame)
        self.polygon_frame.grid(row=5, column=0, pady=5)
        
        ttk.Button(self.polygon_frame, text="Start Polygon", 
                  command=self.start_polygon).grid(row=0, column=0, pady=5)
        ttk.Button(self.polygon_frame, text="Finish Polygon", 
                  command=self.finish_polygon).grid(row=1, column=0, pady=5)
        ttk.Button(self.polygon_frame, text="Clear Selection", 
                  command=self.clear_selection).grid(row=2, column=0, pady=5)
        
        # Initially hide polygon controls
        self.update_control_visibility()
        
        # Add separator
        ttk.Separator(self.control_frame, orient='horizontal').grid(
            row=6, column=0, sticky='ew', pady=10)
        
        # Save and Clear section
        ttk.Button(self.control_frame, text="Save Plots", 
                  command=self.save_plots).grid(row=7, column=0, pady=5)
        ttk.Button(self.control_frame, text="Clear Workspace", 
                  command=self.clear_workspace).grid(row=8, column=0, pady=5)

    def setup_footer(self):
        """Setup footer with development information and logo"""
        # Configure footer style
        style = ttk.Style()
        style.configure("Footer.TFrame", background='#f0f0f0')
        style.configure("Footer.TLabel", background='#f0f0f0', font=('Helvetica', 9))
        
        # Create left frame for text info
        info_frame = ttk.Frame(self.footer_frame, style="Footer.TFrame")
        info_frame.pack(side=tk.LEFT, padx=10)
        
        # Add development info
        dev_info = f"{config.APP_NAME} v{config.VERSION} | {config.ORGANIZATION}"
        ttk.Label(info_frame, text=dev_info, style="Footer.TLabel").pack(side=tk.LEFT, padx=5)
        ttk.Label(info_frame, text="|", style="Footer.TLabel").pack(side=tk.LEFT, padx=5)
        ttk.Label(info_frame, text=f"Developer: {config.DEVELOPER}", style="Footer.TLabel").pack(side=tk.LEFT, padx=5)
        ttk.Label(info_frame, text="|", style="Footer.TLabel").pack(side=tk.LEFT, padx=5)
        ttk.Label(info_frame, text=config.COPYRIGHT, style="Footer.TLabel").pack(side=tk.LEFT, padx=5)
        
        # Add logo if it exists
        if os.path.exists(config.LOGO_PATH):
            try:
                # Load and resize logo
                logo = Image.open(config.LOGO_PATH)
                # Resize logo to height of 30 pixels while maintaining aspect ratio
                logo_height = 30
                aspect_ratio = logo.width / logo.height
                logo_width = int(logo_height * aspect_ratio)
                logo = logo.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                logo_tk = ImageTk.PhotoImage(logo)
                
                # Create label for logo
                logo_label = ttk.Label(self.footer_frame, image=logo_tk, style="Footer.TLabel")
                logo_label.image = logo_tk  # Keep a reference!
                logo_label.pack(side=tk.RIGHT, padx=10)
            except Exception as e:
                print(f"Error loading logo: {e}")

    def load_csv_files(self):
        """Load and process CSV files"""
        files = filedialog.askopenfilenames(
            title="Select CSV files",
            filetypes=[("CSV files", "*.csv")]
        )
        if files:
            self.csv_files = sorted(files)
            self.timestamps = [ThermalDataHandler.extract_datetime_from_filename(f) 
                             for f in self.csv_files]
            self.current_image_index = 0
            self.update_image_display()

    def change_mode(self):
        """Handle selection mode change"""
        self.selection_mode = self.mode_var.get()
        self.clear_selection()
        self.update_control_visibility()
    
    def update_control_visibility(self):
        """Update visibility of controls based on mode"""
        if self.selection_mode == "polygon":
            for child in self.polygon_frame.winfo_children():
                child.grid()
        else:
            for child in self.polygon_frame.winfo_children():
                child.grid_remove()

    def update_image_display(self):
        """Update the displayed thermal image and image counter"""
        if not self.csv_files:
            return
            
        # Load and display current image
        self.current_data = ThermalDataHandler.load_csv_data(
            self.csv_files[self.current_image_index])
        self.plotter.plot_thermal_image(
            self.current_data, 
            self.timestamps[self.current_image_index])
        
        # Update image counter label
        self.image_label.config(
            text=f"Image: {self.current_image_index + 1}/{len(self.csv_files)}")

    def next_image(self):
        """Display next image in the sequence"""
        if not self.csv_files or self.current_image_index >= len(self.csv_files) - 1:
            return
            
        self.current_image_index += 1
        self.update_image_display()

    def previous_image(self):
        """Display previous image in the sequence"""
        if not self.csv_files or self.current_image_index <= 0:
            return
            
        self.current_image_index -= 1
        self.update_image_display()

    def start_polygon(self):
        """Start polygon drawing mode"""
        self.collecting_points = True
        self.polygon_coords = []
        self.plotter.clear_selection()

    def on_click(self, event):
        """Handle mouse click events for both point and polygon selection"""
        if not event.inaxes == self.plotter.ax_thermal:
            return
            
        if self.selection_mode == "point":
            # Handle point selection
            self.selected_point = [event.xdata, event.ydata]
            self.plotter.clear_selection()
            self.plotter.plot_point(event.xdata, event.ydata)
            self.calculate_time_series()
            
        elif self.selection_mode == "polygon" and self.collecting_points:
            # Handle polygon selection
            self.polygon_coords.append([event.xdata, event.ydata])
            self.plotter.plot_point(event.xdata, event.ydata)
            
            if len(self.polygon_coords) > 1:
                prev_x, prev_y = self.polygon_coords[-2]
                self.plotter.plot_line(prev_x, prev_y, event.xdata, event.ydata)

    def finish_polygon(self):
        """Complete polygon drawing and calculate statistics"""
        if len(self.polygon_coords) < 3:
            return
        
        self.collecting_points = False
        
        # Complete polygon
        coords = np.array(self.polygon_coords)
        self.plotter.plot_polygon(coords)
        
        # Calculate and plot time series
        self.calculate_time_series()

    def clear_selection(self):
        """Clear current selection (point or polygon)"""
        self.polygon_coords = []
        self.collecting_points = False
        self.selected_point = None
        self.plotter.clear_selection()

    def calculate_time_series(self):
        """Calculate and plot time series for point or polygon selection"""
        if self.selection_mode == "point" and self.selected_point:
            # Calculate time series for single point
            x, y = int(round(self.selected_point[0])), int(round(self.selected_point[1]))
            temperatures = []
            
            for csv_file in self.csv_files:
                data = ThermalDataHandler.load_csv_data(csv_file)
                temperatures.append(data[y, x])
            
            # Plot single point time series
            self.plotter.plot_time_series(self.timestamps, temperatures)
            
        elif self.selection_mode == "polygon" and len(self.polygon_coords) >= 3:
            # Calculate statistics for polygon region
            mask = self.plotter.create_polygon_mask(self.current_data.shape, self.polygon_coords)
            means = []
            mins = []
            maxs = []
            
            for csv_file in self.csv_files:
                data = ThermalDataHandler.load_csv_data(csv_file)
                masked_data = data[mask]
                
                means.append(np.mean(masked_data))
                mins.append(np.min(masked_data))
                maxs.append(np.max(masked_data))
            
            # Plot polygon statistics time series
            self.plotter.plot_time_series(self.timestamps, means, mins, maxs)

    def save_plots(self):
        """Save current plots as image files"""
        if self.current_data is None or len(self.csv_files) == 0:
            tk.messagebox.showwarning("Warning", "No data to save. Please load data first.")
            return
            
        # Get the directory to save files
        save_dir = filedialog.askdirectory(
            title="Select Directory to Save Plots"
        )
        
        if save_dir:
            try:
                # Create base filename from current timestamp
                timestamp = self.timestamps[self.current_image_index].strftime("%Y%m%d_%H%M%S")
                base_filename = os.path.join(save_dir, f"thermal_analysis_{timestamp}")
                
                # Save plots
                thermal_file, timeseries_file = self.plotter.save_plots(base_filename)
                
                # Show success message with saved file paths
                message = f"Plots saved successfully:\n\n" \
                         f"Thermal Image: {os.path.basename(thermal_file)}\n" \
                         f"Time Series: {os.path.basename(timeseries_file)}"
                tk.messagebox.showinfo("Success", message)
                
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error saving plots: {str(e)}")

    def clear_workspace(self):
        """Reset the entire workspace to initial state"""
        # Clear data storage
        self.csv_files = []
        self.current_data = None
        self.polygon_coords = []
        self.collecting_points = False
        self.timestamps = []
        self.current_image_index = 0
        self.selected_point = None
        
        # Update image counter
        self.image_label.config(text="Image: 0/0")
        
        # Clear plots
        self.plotter.clear_workspace()

def main():
    root = tk.Tk()
    app = ThermalImageGUI(root)
    root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ThermalImageGUI(root)
    root.mainloop()