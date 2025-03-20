# Thermal Image Analyzer

A Python application for analyzing thermal image time series data. This tool allows users to analyze temperature variations over time in thermal images, with support for both point and region-based analysis.

## Features

- Load and visualize thermal image data from CSV files
- Support for multiple thermal camera formats (Mobotix and FLIR)
- Navigate through time series of thermal images
- Select individual points or define polygon regions for analysis
- Calculate and plot temperature time series over time
- Export plots and analysis results
- User-friendly GUI interface

## Installation

### From source

```bash
git clone https://github.com/gmastrantoni/thermal_analyzer.git
cd thermal_analyzer
pip install -e .
```

## Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## Usage

### Running the application

```bash
python ./thermal_analyzer/main.py
```


### Basic workflow

1. Launch the application
2. Select the appropriate camera type (Mobotix or FLIR)
3. Load CSV files containing thermal data
4. Choose analysis mode (point or polygon)
5. Select region of interest
6. View temperature trends over time
7. Export results as needed

## Data Formats

The application supports the following thermal camera formats:

### Mobotix Format
- First 8 rows: metadata including image dimensions (width; height)
- Semicolon (;) separated values
- Filename format: YYYYMMDD_HHMMSS_thermal_celsius.csv

### FLIR Format
- First 6 rows: metadata with "Key = Value" format
- Comma-separated values in scientific notation (e.g., 6.69e+00)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Authors

- Giandomenico Mastrantoni - giandomenico.mastrantoni@uniroma1.it