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
