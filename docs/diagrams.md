# DSP Fiesta - System Diagrams

## 1. High-Level Block Diagram

```mermaid
graph LR
    subgraph "Data Acquisition"
        A[Power Source] --> B[Sensors (V/I)]
        B --> C[ADC / Data Gen]
    end
    
    subgraph "DSP Core"
        C --> D[Preprocessing (Filter)]
        D --> E[Feature Extraction]
        E --> F[Anomaly Detection]
    end
    
    subgraph "Visualization"
        F --> G[Real-Time Dashboard]
        G --> H[Alerts & Logs]
    end
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#9f9,stroke:#333,stroke-width:2px
    style F fill:#f99,stroke:#333,stroke-width:2px
```

## 2. Signal Processing Flowchart

```mermaid
flowchart TD
    Start([Start]) --> Input[Load/Stream Signal Data]
    Input --> Filter[Low-Pass Filter (200Hz)]
    
    subgraph "Analysis Pipeline"
        Filter --> RMS[Calculate RMS (V, I)]
        Filter --> Power[Calculate Apparent Power]
        Filter --> FFT[Compute FFT Spectrum]
        FFT --> THD[Calculate THD %]
    end
    
    THD --> Check{THD > 5%?}
    Check -- Yes --> Anomaly[🔴 Flag as Anomaly]
    Check -- No --> Normal[🟢 Flag as Normal]
    
    Anomaly --> Output[Update Dashboard / Log]
    Normal --> Output
    
    Output --> End([End / Next Frame])
```
