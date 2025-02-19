import pandas as pd
from datetime import datetime
import os

class ThermalDataHandler:
    @staticmethod
    def extract_datetime_from_filename(filename):
        """Extract datetime from filename format: YYYYMMDD_HHMMSS"""
        basename = os.path.basename(filename)
        date_str = basename[:15]  # Get YYYYMMDD_HHMMSS part
        return datetime.strptime(date_str, '%Y%m%d_%H%M%S')

    @staticmethod
    def get_dimensions_from_metadata(filepath):
        """Extract image dimensions from CSV metadata"""
        with open(filepath, 'r') as file:
            metadata = [next(file).strip() for _ in range(8)]
        
        width = height = None
        for line in metadata:
            if 'width;' in line:
                width = int(line.split(';')[1])
            elif 'height;' in line:
                height = int(line.split(';')[1])
                
        if width is None or height is None:
            raise ValueError("Could not find width and height in metadata")
            
        return width, height

    @staticmethod
    def load_csv_data(filepath):
        """Load and process thermal data from CSV file"""
        # Get dimensions from metadata
        width, height = ThermalDataHandler.get_dimensions_from_metadata(filepath)
        
        # Skip the first 8 rows (metadata) and read the thermal data
        data = pd.read_csv(filepath, skiprows=8, sep=';', header=None, decimal='.')
        
        # Flatten all columns into a single array and reshape
        thermal_data = data.values.flatten()
        
        # Reshape the data into a 2D array using the actual dimensions
        return thermal_data.reshape(height, width)