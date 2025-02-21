# Thermal Image Analyzer

A Python application for analyzing thermal image time series data. This tool allows users to analyze temperature variations over time in thermal images, with support for both point and region-based analysis.

## Features

- Load and visualize thermal image data from CSV files
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
thermal-analyzer
```

Or from Python:

```python
from thermal_analyzer.main import main
main()
```

### Basic workflow

1. Launch the application
2. Load CSV files containing thermal data
3. Choose analysis mode (point or polygon)
4. Select region of interest
5. View temperature trends over time
6. Export results as needed

## Data Format

The application expects CSV files with the following format:

- First 8 rows: metadata including image dimensions
- Remaining rows: temperature data in Celsius
- Filename format: YYYYMMDD_HHMMSS_thermal_celsius.csv

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Testing

Run the test suite:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Authors

- Giandomenico Mastrantoni - giandomenico.mastrantoni@uniroma1.it
