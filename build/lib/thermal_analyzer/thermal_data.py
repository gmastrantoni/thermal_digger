import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import re
from utils.camera_types import CameraType

class ThermalDataHandler:
    @staticmethod
    def extract_datetime_from_filename(filepath):
        """
        Extract datetime from file.
        For FLIR format, extract only from metadata.
        For Mobotix format, extract from filename YYYYMMDD_HHMMSS.
        """
        filename = os.path.basename(filepath)
        
        # Check if it's a FLIR file by looking at the first few lines
        try:
            camera_type = ThermalDataHandler.detect_camera_type(filepath)
            
            # If it's a FLIR file, try to get datetime from metadata
            if camera_type == CameraType.FLIR:
                with open(filepath, 'r') as file:
                    for _ in range(2):  # Skip first two lines
                        next(file)
                    time_line = next(file).strip()  # Third line should contain time info
                    
                    # Check if the line contains time information
                    time_match = re.search(r'Time\s*=\s*(\d+):(\d+):(\d+):(\d+)\.(\d+)', time_line)
                    if time_match:
                        # Extract components - format is typically ddd:hh:mm:ss.microsec
                        days, hours, minutes, seconds, microsec = time_match.groups()
                        
                        # Get the base date as a starting point
                        year = datetime.now().year
                        # Create datetime for January 1st of the given year at 00:00:00.000
                        base_date = datetime(year, 1, 1)
                        # Add the day of year (subtract 1 because day_of_year is 1-based)
                        date_from_day = base_date + timedelta(days=int(days) - 1)
                    
                        # Set the time components
                    return date_from_day.replace(
                        hour=int(hours),
                        minute=int(minutes),
                        second=int(seconds),
                        microsecond=0
                        )
        except Exception as e:
            print(f"Error extracting datetime from FLIR metadata: {e}")
        
        # For Mobotix format (YYYYMMDD_HHMMSS)
        if re.match(r'\d{8}_\d{6}', filename):
            date_str = filename[:15]  # Get YYYYMMDD_HHMMSS part
            return datetime.strptime(date_str, '%Y%m%d_%H%M%S')
        
        # For any other format, fallback to current date
        return datetime.now()
    
    @staticmethod
    def detect_camera_type(filepath):
        """Automatically detect camera type from file format."""
        try:
            with open(filepath, 'r') as file:
                first_line = file.readline().strip()
                
                # Check if it's a Mobotix file (first line contains semicolon)
                if ";" in first_line:
                    return CameraType.MOBOTIX
                
                # Check if it's a FLIR file (contains "Filename = ")
                elif "Filename = " in first_line:
                    return CameraType.FLIR
                
                # Default to Mobotix if unknown
                return CameraType.MOBOTIX
        except Exception:
            # Default to Mobotix if detection fails
            return CameraType.MOBOTIX
        
    @staticmethod
    def get_dimensions_from_metadata(filepath, camera_type=None):
        """Extract image dimensions from CSV metadata based on camera type."""
        if camera_type is None:
            camera_type = ThermalDataHandler.detect_camera_type(filepath)
            
        if camera_type == CameraType.MOBOTIX:
            return ThermalDataHandler._get_mobotix_dimensions(filepath)
        elif camera_type == CameraType.FLIR:
            return ThermalDataHandler._get_flir_dimensions(filepath)
        else:
            raise ValueError(f"Unsupported camera type: {camera_type}")

    @staticmethod
    def _get_mobotix_dimensions(filepath):
        """Extract image dimensions from Mobotix CSV metadata."""
        with open(filepath, 'r') as file:
            metadata = [next(file).strip() for _ in range(8)]
        
        width = height = None
        for line in metadata:
            if 'width;' in line:
                width = int(line.split(';')[1])
            elif 'height;' in line:
                height = int(line.split(';')[1])
                
        if width is None or height is None:
            raise ValueError("Could not find width and height in Mobotix metadata")
            
        return width, height

    @staticmethod
    def _get_flir_dimensions(filepath):
        """Extract image dimensions from FLIR CSV by counting rows and columns."""
        with open(filepath, 'r') as file:
            # Skip metadata lines until we find a line containing commas
            line = file.readline()
            while line and ',' not in line:
                line = file.readline()
            
            # First data line - count the number of columns
            if not line:
                raise ValueError("Could not find any data rows in FLIR file")
                
            # Count columns in the first data row
            columns = len(line.strip().split(','))
            
            # Count the remaining data rows
            rows = 1  # we already read one data row
            for line in file:
                if ',' in line:
                    rows += 1
                    
        return columns, rows

    @staticmethod
    def load_csv_data(filepath, camera_type=None):
        """Load and process thermal data from CSV file based on camera type."""
        if camera_type is None:
            camera_type = ThermalDataHandler.detect_camera_type(filepath)
            
        if camera_type == CameraType.MOBOTIX:
            return ThermalDataHandler._load_mobotix_data(filepath)
        elif camera_type == CameraType.FLIR:
            return ThermalDataHandler._load_flir_data(filepath)
        else:
            raise ValueError(f"Unsupported camera type: {camera_type}")

    @staticmethod
    def _load_mobotix_data(filepath):
        """Load and process thermal data from Mobotix CSV file."""
        # Get dimensions from metadata
        width, height = ThermalDataHandler._get_mobotix_dimensions(filepath)
        
        # Skip the first 8 rows (metadata) and read the thermal data
        data = pd.read_csv(filepath, skiprows=8, sep=';', header=None, decimal='.')
        
        # Flatten all columns into a single array and reshape
        thermal_data = data.values.flatten()
        
        # Reshape the data into a 2D array using the actual dimensions
        return thermal_data.reshape(height, width)

    @staticmethod
    def _load_flir_data(filepath):
        """Load and process thermal data from FLIR CSV file."""
        # Get dimensions by counting rows and columns
        width, height = ThermalDataHandler._get_flir_dimensions(filepath)
        
        # Find the header size by counting lines until we find the first data row
        header_size = 0
        with open(filepath, 'r') as file:
            for line in file:
                if ',' in line:
                    break
                header_size += 1
        
        # Skip the header rows and read the thermal data
        # FLIR data uses comma separator and is in scientific notation
        try:
            data = pd.read_csv(filepath, skiprows=header_size, header=None, sep=',')
            
            # Convert from scientific notation and handle any potential errors
            thermal_data = data.values.astype(float)
            
            # Reshape if necessary to ensure correct dimensions
            if thermal_data.shape != (height, width):
                thermal_data = thermal_data.flatten()
                # Remove any NaN values that might be at the end of rows
                thermal_data = thermal_data[~np.isnan(thermal_data)]
                # Reshape to the expected dimensions
                thermal_data = thermal_data[:height*width].reshape(height, width)
                
            return thermal_data
            
        except Exception as e:
            # Fallback method if pandas approach fails
            print(f"Error reading FLIR data with pandas: {e}")
            print("Using alternative parsing method...")
            
            # Manual parsing as fallback
            thermal_data = np.zeros((height, width))
            with open(filepath, 'r') as file:
                # Skip header rows
                for _ in range(header_size):
                    next(file)
                
                # Read data rows
                for i, line in enumerate(file):
                    if i >= height:
                        break
                        
                    if ',' not in line:
                        continue  # Skip non-data lines
                        
                    # Split line by comma and convert values to float
                    values = line.strip().rstrip(',\r').split(',')
                    row_data = [float(val) for val in values[:width] if val.strip()]
                    
                    # Pad row with zeros if needed
                    if len(row_data) < width:
                        row_data.extend([0] * (width - len(row_data)))
                        
                    thermal_data[i, :len(row_data)] = row_data
                    
            return thermal_data