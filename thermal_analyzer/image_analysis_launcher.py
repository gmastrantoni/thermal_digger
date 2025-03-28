"""
Module to add a thermal change detection modal window launcher
to the existing ThermalImageGUI application.
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

def add_change_detection_launcher(app):
    """
    Add a button to launch the thermal change detection modal window
    to the existing ThermalImageGUI application.
    
    Parameters:
        app: ThermalImageGUI instance
    """
    # Add a separator after existing controls
    ttk.Separator(app.control_frame, orient='horizontal').grid(
        row=15, column=0, sticky='ew', pady=10)
    
    # Create a frame for the change detection launcher button
    launcher_frame = ttk.Frame(app.control_frame)
    launcher_frame.grid(row=16, column=0, pady=10, sticky='ew')
    launcher_frame.grid_columnconfigure(0, weight=1)
    
    # Add a button to launch the change detection window
    change_button = ttk.Button(
        launcher_frame, 
        text="Thermal Image Analysis", 
        command=lambda: launch_change_detection_window(app)
    )
    change_button.grid(row=0, column=0)
    
    return change_button

def launch_change_detection_window(app):
    """
    Launch the thermal change detection window.
    
    Parameters:
        app: ThermalImageGUI instance
    """
    # Import here to avoid circular imports
    from image_analysis_gui import ChangeDetectionWindow
    
    # Create the change detection window
    change_window = ChangeDetectionWindow(app.root, app)
    
    # Make the window modal (cannot interact with main window until this is closed)
    change_window.transient(app.root)
    change_window.grab_set()
    
    # Wait for window to close before returning control to main app
    app.root.wait_window(change_window)