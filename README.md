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
