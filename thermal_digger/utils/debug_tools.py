"""
Debug and diagnostic tools for the Thermal Analyzer application.
"""

def debug_file_sorting(files):
    """
    Debug function to help understand why files might not be sorting correctly by date.
    
    Args:
        files: List of CSV file paths
        
    Returns:
        None, prints debug information to console
    """
    from thermal_data import ThermalDataHandler
    import os
    
    print("\n===== FILE SORTING DEBUG =====")
    print(f"Number of files: {len(files)}")
    
    # Extract timestamps and store with filenames
    file_info = []
    for file_path in files:
        try:
            timestamp = ThermalDataHandler.extract_datetime_from_filename(file_path)
            camera_type = ThermalDataHandler.detect_camera_type(file_path)
            
            # Get just the filename without the full path
            filename = os.path.basename(file_path)
            
            file_info.append({
                'filename': filename,
                'timestamp': timestamp,
                'camera_type': str(camera_type)
            })
            
            print(f"File: {filename}")
            print(f"  Camera Type: {camera_type}")
            print(f"  Timestamp: {timestamp}")
            
            # If it's a FLIR file, print additional debugging info
            if str(camera_type) == "FLIR":
                with open(file_path, 'r') as f:
                    # Get the first few lines
                    header_lines = [next(f).strip() for _ in range(6) if f]
                    
                    # Print relevant header lines
                    for line in header_lines:
                        if "Time" in line:
                            print(f"  Metadata Time: {line}")
        except Exception as e:
            print(f"Error processing {os.path.basename(file_path)}: {str(e)}")
    
    # Sort by timestamp and print the sorted order
    sorted_info = sorted(file_info, key=lambda x: x['timestamp'])
    
    print("\nSorted files by timestamp:")
    for idx, info in enumerate(sorted_info):
        print(f"{idx+1}. {info['filename']} - {info['timestamp']} ({info['camera_type']})")
    
    print("\nChecking for timestamp duplicates or issues:")
    # Check for identical timestamps
    timestamps = [info['timestamp'] for info in file_info]
    for idx, timestamp in enumerate(timestamps):
        count = timestamps.count(timestamp)
        if count > 1:
            print(f"Duplicate timestamp found: {timestamp} appears {count} times")
    
    # Check for timestamps that are very close together
    sorted_timestamps = sorted(timestamps)
    for i in range(1, len(sorted_timestamps)):
        delta = sorted_timestamps[i] - sorted_timestamps[i-1]
        if delta.total_seconds() < 1:  # Less than 1 second apart
            print(f"Very close timestamps: {sorted_timestamps[i-1]} and {sorted_timestamps[i]}")
    
    print("===== END DEBUG =====\n")