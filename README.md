# Band Filling Visualization

Interactive 2D band structure visualization web app for exploring electronic band filling and dispersion.

## Features

- **Interactive 3D visualization** of electronic band structures
- **Real-time band filling** control (0 to 1)
- **Adjustable hopping strength** for tight-binding dispersion
- **Switch between dispersion types**: Free electron vs Tight-binding
- **Mathematical formulas** displayed in real-time
- **Physics explanations** and parameter metrics
- **Cross-platform** - works on any device with a web browser

## Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run band_filling_web.py

# Open http://localhost:8501 in your browser
```

### Deployment
Deploy to Streamlit Community Cloud:
1. Push this repository to GitHub
2. Connect to Streamlit Cloud
3. Deploy - get instant public URL

## Usage

1. **Band Filling Slider**: Adjust from 0 (empty) to 1 (full) to see how electrons occupy energy states
2. **Dispersion Type**: Switch between free-electron and tight-binding models
3. **Hopping Strength**: Control the bandwidth in tight-binding dispersion
4. **3D Visualization**: Rotate and zoom the 3D plot to explore the band structure

## Physics

### Free-Electron Dispersion
$$E(k) = k_x^2 + k_y^2$$

### Tight-Binding Dispersion
$$E(k) = t[2 - \cos(k_x a) - \cos(k_y a)] \cdot \frac{2}{a^2}$$

Where:
- $t$ is the hopping strength parameter
- $a$ is the lattice constant
- $k_x, k_y$ are wave vectors in the first Brillouin zone

## Technical Details

- **Framework**: Streamlit
- **Visualization**: Matplotlib 3D plots
- **Computation**: NumPy arrays for efficient calculations
- **Performance**: Cached calculations for real-time interaction

## Requirements

- Python 3.8+
- Streamlit >= 1.56.0
- NumPy >= 2.4.0
- Matplotlib >= 3.10.0

## License

Educational use for physics and materials science instruction.