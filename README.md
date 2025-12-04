# DSP Fiesta Power Monitoring System

A Digital Signal Processing (DSP)-based power monitoring and anomaly detection system.

## Overview
This project analyzes voltage and current waveforms using core DSP techniques to identify abnormal power usage and illegal electricity tapping.

## Setup
1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Data Generation
To generate synthetic power signal datasets (normal load and illegal tapping scenarios):
```bash
python src/generate_data.py
```
This will create the following files in the `data/` directory:
- `normal_load.csv`: Simulated normal power usage.
- `illegal_tap.csv`: Simulated illegal tapping with amplitude changes and harmonic distortion.

## Signal Visualization
To visualize electrical signal waveforms in the time domain:

### Basic Usage
```bash
python src/visualize_signal.py data/normal_load.csv
```

### Advanced Options
```bash
# Save plot to file
python src/visualize_signal.py data/normal_load.csv --save output.png

# Visualize specific time range (e.g., 0-2 seconds)
python src/visualize_signal.py data/illegal_tap.csv --time-range 0 2

# Custom title
python src/visualize_signal.py data/illegal_tap.csv --title "Illegal Tap Detection"

# Combined options
python src/visualize_signal.py data/illegal_tap.csv --time-range 2 5 --save tap_analysis.png --title "Tap Event (2-5s)"
```

### Features
- **Time-Domain Visualization**: Plots both voltage and current waveforms against time
- **Sampling Frequency Display**: Shows the sampling frequency (fs = 1000 Hz) in the plot
- **Clear Transitions**: Time-domain transitions are clearly visible (e.g., illegal tap starting at t=3s)
- **Flexible Time Range**: Zoom into specific time intervals for detailed analysis

## Digital Noise Filtering
Apply low-pass Butterworth filter to remove high-frequency noise from electrical signals while preserving the fundamental frequency and harmonics.

### Basic Usage
```bash
# Apply filter and display interactive plots
python src/apply_filter.py data/normal_load.csv

# Filter with custom cutoff frequency
python src/apply_filter.py data/normal_load.csv --cutoff 150
```

### Advanced Options
```bash
# Save filtered data to CSV
python src/apply_filter.py data/normal_load.csv --output data/normal_load_filtered.csv

# Save before/after comparison plots
python src/apply_filter.py data/illegal_tap.csv --save-plot filtered_analysis.png

# Focus on specific time range (e.g., around illegal tap transition)
python src/apply_filter.py data/illegal_tap.csv --time-range 2.5 4.5 --save-plot tap_filtered.png

# Custom filter parameters
python src/apply_filter.py data/normal_load.csv --cutoff 200 --order 6

# Choose plot type (comparison, overlay, or both)
python src/apply_filter.py data/normal_load.csv --plot overlay --save-plot overlay.png
```

### Filter Parameters
- **`--cutoff`**: Cutoff frequency in Hz (default: 200 Hz)
  - Frequencies above this are attenuated
  - For 50 Hz power signals, 200 Hz preserves fundamental + harmonics while removing noise
- **`--order`**: Filter order (default: 4)
  - Higher order = sharper cutoff but more computational cost
  - Order 4 provides good balance between smoothness and phase preservation
- **`--plot`**: Plot type - `comparison` (side-by-side), `overlay` (before/after overlaid), or `both` (default)
- **`--output`**: Save filtered signal data to CSV file
- **`--save-plot`**: Save plots to image file instead of displaying

### Features
- **Low-Pass Butterworth Filter**: Smooth frequency response with minimal passband ripple
- **Zero-Phase Filtering**: Uses `filtfilt` to avoid phase distortion in the filtered signal
- **Noise Reduction Metrics**: Displays standard deviation of removed noise
- **Before/After Visualization**: Side-by-side comparison and overlay plots
- **Preserves Signal Characteristics**: Maintains important features like illegal tap transitions while removing noise
