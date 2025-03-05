import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import numpy as np
import os
from PIL import Image, ImageTk
from thermal_data import ThermalDataHandler
from thermal_plot import ThermalPlotter, DeltaAnalysisWindow
from utils.config import config

class ThermalImageGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Thermal Image Analyzer")
        # Set initial window size (width x height)
        self.root.geometry("1200x900")
        # Set minimum window size
        self.root.minsize(900, 600)
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
        self.global_min = None
        self.global_max = None
        
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
        self.setup_delta_analysis_controls()
        
        # Connect mouse events
        self.plotter.get_click_handler().mpl_connect('button_press_event', self.on_click)

    def setup_controls(self):
        """Setup control buttons with centered layout for better visual appearance"""
        # Configure the control frame to allow centering
        self.control_frame.grid_columnconfigure(0, weight=1)
        
        # Load Files section - centered button
        files_frame = ttk.Frame(self.control_frame)
        files_frame.grid(row=0, column=0, pady=5, sticky='ew')
        files_frame.grid_columnconfigure(0, weight=1)
        
        load_button = ttk.Button(files_frame, text="Load CSV Files", command=self.load_csv_files)
        load_button.grid(row=0, column=0, pady=5)
        # Center the button by configuring the parent frame
        files_frame.grid_rowconfigure(0, weight=1)
        load_button.grid(row=0, column=0, padx=5, pady=5, sticky='n')
        
        # Add separator
        ttk.Separator(self.control_frame, orient='horizontal').grid(
            row=1, column=0, sticky='ew', pady=10)
            
        # Image Navigation section - centered navigation controls
        nav_frame = ttk.Frame(self.control_frame)
        nav_frame.grid(row=2, column=0, pady=5, sticky='ew')
        nav_frame.grid_columnconfigure(1, weight=1)
        
        # Center the navigation controls within their frame
        ttk.Button(nav_frame, text="◀ Previous", 
                  command=self.previous_image).grid(row=0, column=0, padx=2)
        self.image_label = ttk.Label(nav_frame, text="Image: 0/0")
        self.image_label.grid(row=0, column=1, padx=5)
        ttk.Button(nav_frame, text="Next ▶", 
                  command=self.next_image).grid(row=0, column=2, padx=2)
        
        # Add separator
        ttk.Separator(self.control_frame, orient='horizontal').grid(
            row=3, column=0, sticky='ew', pady=10)
        
        # Selection Mode section - centered radio buttons
        mode_frame = ttk.Frame(self.control_frame)
        mode_frame.grid(row=4, column=0, pady=5, sticky='ew')
        mode_frame.grid_columnconfigure(0, weight=1)
        mode_frame.grid_columnconfigure(3, weight=1)
        
        # Use additional columns to center the radio buttons
        self.mode_var = tk.StringVar(value="point")
        ttk.Radiobutton(mode_frame, text="Points", variable=self.mode_var, 
                       value="point", command=self.change_mode).grid(row=0, column=1, padx=5)
        ttk.Radiobutton(mode_frame, text="Polygon", variable=self.mode_var, 
                       value="polygon", command=self.change_mode).grid(row=0, column=2, padx=5)
        
        # Create mode-specific control frames - with centering
        self.control_frames_row = 5  # Row where control frames will be placed
        
        # Point controls frame - create with centered button
        self.point_frame = ttk.Frame(self.control_frame)
        self.point_frame.grid_columnconfigure(0, weight=1)
        
        self.clear_points_button = ttk.Button(self.point_frame, text="Clear All Points", 
                                           command=self.clear_selection)
        self.clear_points_button.grid(row=0, column=0, pady=5)
        
        # Polygon controls frame - create with centered buttons
        self.polygon_frame = ttk.Frame(self.control_frame)
        self.polygon_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Button(self.polygon_frame, text="Start Polygon", 
                  command=self.start_polygon).grid(row=0, column=0, pady=5)
        ttk.Button(self.polygon_frame, text="Finish Polygon", 
                  command=self.finish_polygon).grid(row=1, column=0, pady=5)
        ttk.Button(self.polygon_frame, text="Clear Selection", 
                  command=self.clear_selection).grid(row=2, column=0, pady=5)
        
        # Initially set correct visibility based on mode
        self.update_control_visibility()
        
        # Add separator
        ttk.Separator(self.control_frame, orient='horizontal').grid(
            row=6, column=0, sticky='ew', pady=10)
        
        # Save and Clear section - centered buttons
        save_frame = ttk.Frame(self.control_frame)
        save_frame.grid(row=7, column=0, pady=5, sticky='ew')
        save_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Button(save_frame, text="Save Plots", 
                  command=self.save_plots).grid(row=0, column=0, pady=5)
        
        clear_frame = ttk.Frame(self.control_frame)
        clear_frame.grid(row=8, column=0, pady=5, sticky='ew')
        clear_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Button(clear_frame, text="Clear Workspace", 
                  command=self.clear_workspace).grid(row=0, column=0, pady=5)

    def update_control_visibility(self):
        """Update visibility of controls based on selection mode"""
        # Remove both frames from grid first to avoid conflicts
        self.point_frame.grid_forget()
        self.polygon_frame.grid_forget()
        
        # Then add only the appropriate frame for the current mode
        if self.selection_mode == "polygon":
            self.polygon_frame.grid(row=self.control_frames_row, column=0, pady=5, sticky='ew')
        else:  # point mode
            self.point_frame.grid(row=self.control_frames_row, column=0, pady=5, sticky='ew')
            
        # Force update the display to ensure changes are immediately visible
        self.root.update_idletasks()


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
            filetypes=[("CSV files", "*.csv")])
        if files:
            self.csv_files = sorted(files)
            self.timestamps = [ThermalDataHandler.extract_datetime_from_filename(f) 
                               for f in self.csv_files]
            
            # Determine global min and max values across all files
            min_val = float('inf')
            max_val = float('-inf')
            
            for csv_file in self.csv_files:
                data = ThermalDataHandler.load_csv_data(csv_file)
                min_val = min(min_val, np.min(data))
                max_val = max(max_val, np.max(data))
            
            # Round min to nearest integer (floor) and max to nearest integer (ceiling)
            self.global_min = round(min_val)
            self.global_max = round(max_val)
            
            self.current_image_index = 0
            self.update_image_display()

    def change_mode(self):
        """Handle selection mode change"""
        self.selection_mode = self.mode_var.get()
        self.clear_selection()
        self.update_control_visibility()

    def update_image_display(self):
        """Update the displayed thermal image and image counter"""
        if not self.csv_files:
            return
            
        # Load and display current image
        self.current_data = ThermalDataHandler.load_csv_data(
            self.csv_files[self.current_image_index])
        self.plotter.plot_thermal_image(
            self.current_data, 
            self.timestamps[self.current_image_index],
            vmin=self.global_min,  # Pass global min
            vmax=self.global_max   # Pass global max
            )
        
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
            # Add new point and get its index
            point_idx = self.plotter.plot_point(event.xdata, event.ydata)
            self.calculate_time_series()
            
        elif self.selection_mode == "polygon" and self.collecting_points:
            # Handle polygon selection [unchanged]
            self.polygon_coords.append([event.xdata, event.ydata])
            self.plotter.plot_point(event.xdata, event.ydata)
            
            if len(self.polygon_coords) > 1:
                prev_x, prev_y = self.polygon_coords[-2]
                self.plotter.plot_line(prev_x, prev_y, event.xdata, event.ydata)

    def finish_polygon(self):
        """Complete polygon drawing and calculate statistics"""
        if len(self.polygon_coords) < 3:
            messagebox.showwarning("Warning", "A polygon needs at least 3 points.")
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
        # Disable delta analysis button
        self.delta_button.config(state=tk.DISABLED)
    
    def calculate_time_series(self):
        """Calculate and plot time series for multiple points or polygon selection"""
        if self.selection_mode == "point" and self.plotter.points:
            # Calculate time series for all points
            point_temperatures = {}
            
            for point_idx, (x, y, _) in enumerate(self.plotter.points):
                temperatures = []
                x_int, y_int = int(round(x)), int(round(y))
                
                for csv_file in self.csv_files:
                    data = ThermalDataHandler.load_csv_data(csv_file)
                    temperatures.append(data[y_int, x_int])
                
                point_temperatures[point_idx] = temperatures
            
            # Update stored data for export
            self.plotter.current_timeseries_data.update({
                'timestamps': self.timestamps,
                'values': point_temperatures,
                'selection_type': 'point'
            })
            
            # Plot all point time series
            self.plotter.plot_time_series(self.timestamps, point_temperatures)
            
            # Enable delta analysis button
            self.delta_button.config(state=tk.NORMAL)
            
        elif self.selection_mode == "polygon" and len(self.polygon_coords) >= 3:
            # Calculate polygon statistics [unchanged]
            mask = self.plotter.create_polygon_mask(self.current_data.shape, self.polygon_coords)
            means = []
            mins = []
            maxs = []
            
            for csv_file in self.csv_files:
                data = ThermalDataHandler.load_csv_data(csv_file)
                masked_data = data[mask]
                
                if len(masked_data) > 0:
                    means.append(np.mean(masked_data))
                    mins.append(np.min(masked_data))
                    maxs.append(np.max(masked_data))
                else:
                    means.append(np.nan)
                    mins.append(np.nan)
                    maxs.append(np.nan)
            
            # Update stored data for export
            self.plotter.current_timeseries_data.update({
                'timestamps': self.timestamps,
                'values': {'mean': means},
                'mins': mins,
                'maxs': maxs,
                'selection_type': 'polygon'
            })
            
            # Plot polygon statistics time series
            self.plotter.plot_time_series(self.timestamps, {'mean': means}, mins, maxs)
            
            # Enable delta analysis button
            self.delta_button.config(state=tk.NORMAL)
    

    def setup_delta_analysis_controls(self):
        """Setup controls for delta analysis"""
        # Add separator after existing controls
        ttk.Separator(self.control_frame, orient='horizontal').grid(
            row=9, column=0, sticky='ew', pady=10)
        
        # Delta Analysis section - with title label
        delta_title_frame = ttk.Frame(self.control_frame)
        delta_title_frame.grid(row=10, column=0, pady=5, sticky='ew')
        delta_title_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(delta_title_frame, text="Delta Analysis", 
                font=('Helvetica', 10, 'bold')).grid(row=0, column=0)
        
        # Window size selection
        window_size_frame = ttk.Frame(self.control_frame)
        window_size_frame.grid(row=11, column=0, pady=5, sticky='ew')
        window_size_frame.grid_columnconfigure(0, weight=1)
        window_size_frame.grid_columnconfigure(1, weight=1)
        window_size_frame.grid_columnconfigure(2, weight=1)
        
        ttk.Label(window_size_frame, text="Window Size:").grid(row=0, column=0, sticky='e')
        
        self.window_size_var = tk.IntVar(value=2)
        window_size_spinner = ttk.Spinbox(window_size_frame, from_=1, to=20, 
                                        textvariable=self.window_size_var, width=5)
        window_size_spinner.grid(row=0, column=1, sticky='w', padx=5)
        
        # Button to launch delta analysis
        delta_button_frame = ttk.Frame(self.control_frame)
        delta_button_frame.grid(row=12, column=0, pady=10, sticky='ew')
        delta_button_frame.grid_columnconfigure(0, weight=1)
        
        self.delta_button = ttk.Button(delta_button_frame, text="Show Delta Analysis", 
                                    command=self.show_delta_analysis)
        self.delta_button.grid(row=0, column=0)
        self.delta_button.config(state=tk.DISABLED)  # Initially disabled

    def show_delta_analysis(self):
        """Show delta analysis in a popup window"""
        if not self.plotter.current_timeseries_data['timestamps']:
            tk.messagebox.showwarning("Warning", "No time series data available for analysis.")
            return
        
        window_size = self.window_size_var.get()
        
        if len(self.plotter.current_timeseries_data['timestamps']) <= window_size:
            tk.messagebox.showwarning(
                "Warning", 
                f"Not enough data points for window size {window_size}. "
                f"Need at least {window_size+1} data points."
            )
            return
        
        # Create the delta analysis window
        DeltaAnalysisWindow(
            self.root,
            self.plotter.current_timeseries_data['timestamps'],
            self.plotter.current_timeseries_data['values'],
            window_size,
            self.plotter.current_timeseries_data['selection_type']
        )

    def get_default_save_directory(self):
        """
        Determines the default save directory based on input data location.
        Creates a 'results' subdirectory if it doesn't exist.
        """
        if not self.csv_files:
            return None
            
        # Get the directory of the first CSV file
        input_dir = os.path.dirname(self.csv_files[0])
        
        # Create path for results directory
        results_dir = os.path.join(input_dir, "results")
        
        # Create the results directory if it doesn't exist
        try:
            if not os.path.exists(results_dir):
                os.makedirs(results_dir)
                print(f"Created results directory: {results_dir}")
            return results_dir
        except Exception as e:
            print(f"Warning: Could not create results directory: {e}")
            return input_dir  # Fall back to input directory if we can't create results dir

    def save_plots(self):
        """Save current plots as image files and time series data as CSV with custom filename"""
        if self.current_data is None or len(self.csv_files) == 0:
            tk.messagebox.showwarning("Warning", "No data to save. Please load data first.")
            return
        
        # Get default save directory
        default_dir = self.get_default_save_directory()
        
        # Get custom filename from user
        dialog = FileNameDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if not dialog.result:
            return  # User cancelled
        
        # Get the directory to save files, starting from the default directory
        # save_dir = filedialog.askdirectory(
        #     title="Select Directory to Save Files",
        #     initialdir=default_dir
        #     )
        save_dir = default_dir
        
        if save_dir:
            try:
                # Create base filename
                base_name = dialog.result['filename']
                
                # Add timestamp if requested
                if dialog.result['include_timestamp']:
                    timestamp = self.timestamps[self.current_image_index].strftime("%Y%m%d_%H%M%S")
                    base_name = f"{base_name}_{timestamp}"
                
                base_filename = os.path.join(save_dir, base_name)
                
                # Save plots and CSV
                thermal_file, timeseries_file, csv_file = self.plotter.save_plots(base_filename)
                
                # Build success message with relative paths for cleaner display
                try:
                    common_prefix = os.path.commonpath([save_dir, thermal_file, timeseries_file])
                    rel_thermal = os.path.relpath(thermal_file, common_prefix)
                    rel_timeseries = os.path.relpath(timeseries_file, common_prefix)
                    rel_csv = os.path.relpath(csv_file, common_prefix) if csv_file else None
                    
                    message = f"Files saved successfully in {os.path.basename(save_dir)}:\n\n" \
                             f"Thermal Image: {rel_thermal}\n" \
                             f"Time Series Plot: {rel_timeseries}"
                    
                    if rel_csv:
                        message += f"\nTime Series Data: {rel_csv}"
                except:
                    # Fall back to full paths if relative path calculation fails
                    message = f"Files saved successfully:\n\n" \
                             f"Thermal Image: {os.path.basename(thermal_file)}\n" \
                             f"Time Series Plot: {os.path.basename(timeseries_file)}"
                    
                    if csv_file:
                        message += f"\nTime Series Data: {os.path.basename(csv_file)}"
                
                tk.messagebox.showinfo("Success", message)
                
            except Exception as e:
                tk.messagebox.showerror("Error", f"Error saving files: {str(e)}")
    
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
        self.global_min = None
        self.global_max = None
        # Update image counter
        self.image_label.config(text="Image: 0/0")
        # Clear plots
        self.plotter.clear_workspace()
        # Disable delta analysis button
        self.delta_button.config(state=tk.DISABLED)

class FileNameDialog:
    """Dialog for getting custom filename with optional timestamp"""
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Save Files")
        self.dialog.transient(parent)
        
        # Create and pack widgets
        frame = ttk.Frame(self.dialog, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Filename entry
        ttk.Label(frame, text="Enter base filename:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.filename = tk.StringVar(value="thermal_analysis")
        self.filename_entry = ttk.Entry(frame, textvariable=self.filename, width=40)
        self.filename_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Timestamp checkbox
        self.include_timestamp = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="Include timestamp in filename", 
                       variable=self.include_timestamp).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="OK", command=self.ok).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel).grid(row=0, column=1, padx=5)
        
        # Initialize result
        self.result = None
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                       parent.winfo_rooty() + 50))
        
        # Make dialog modal
        self.dialog.grab_set()
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        self.filename_entry.focus_set()
        
    def ok(self):
        """User clicked OK"""
        self.result = {
            'filename': self.filename.get(),
            'include_timestamp': self.include_timestamp.get()
        }
        self.dialog.destroy()
        
    def cancel(self):
        """User clicked Cancel"""
        self.dialog.destroy()


def main():
    root = tk.Tk()
    app = ThermalImageGUI(root)
    root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ThermalImageGUI(root)
    root.mainloop()