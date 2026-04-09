#!/usr/bin/env python3

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import io

# ============================================================
# Page Configuration
# ============================================================
st.set_page_config(
    page_title="Band Filling Visualization",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# Parameters
# ============================================================
a = 1.0
nk = 121

# ============================================================
# k-grid in the first Brillouin zone of a square lattice
# ============================================================
@st.cache_data
def create_k_grid():
    kmax = np.pi / a
    kx = np.linspace(-kmax, kmax, nk)
    ky = np.linspace(-kmax, kmax, nk)
    KX, KY = np.meshgrid(kx, ky, indexing="xy")
    
    qX = a * KX
    qY = a * KY
    
    # Free-electron dispersion
    E_free = qX**2 + qY**2
    
    return KX, KY, E_free

KX, KY, E_free = create_k_grid()

# ============================================================
# Tight-binding dispersion calculation
# ============================================================
@st.cache_data
def calculate_tight_binding(hopping_t):
    qX = a * KX
    qY = a * KY
    
    # Tight-binding dispersion for square lattice with adjustable hopping
    E_tb_raw = 2.0 - np.cos(qX) - np.cos(qY)
    E_tb = hopping_t * E_tb_raw * (2.0 / (a * a))
    
    return E_tb

# ============================================================
# Helper functions
# ============================================================
def occupied_mask(sorted_indices, shape, fill_fraction):
    n_occ = int(np.floor(fill_fraction * sorted_indices.size))
    occ_flat = np.zeros(sorted_indices.size, dtype=bool)
    if n_occ > 0:
        occ_flat[sorted_indices[:n_occ]] = True
    return occ_flat.reshape(shape)

def create_band_plot(dispersion_type, fill_fraction, hopping_t, elevation=28, azimuth=-55):
    # Calculate energies
    if dispersion_type == "Free":
        E_wire = E_free
        E_fill = E_free
        title_main = "2D square lattice: free-electron dispersion"
        formula = r"$E(k) = k_x^2 + k_y^2$"
    else:
        E_tb = calculate_tight_binding(hopping_t)
        E_wire = E_tb
        E_fill = E_tb
        title_main = "2D square lattice: tight-binding dispersion"
        formula = r"$E(k) = t[2 - \cos(k_x a) - \cos(k_y a)] \cdot \frac{2}{a^2}$"
    
    # Create figure
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")
    
    # Main wire mesh
    ax.plot_wireframe(
        KX, KY, E_wire,
        rstride=5,
        cstride=5,
        linewidth=0.65,
        color="0.35",
        alpha=0.95
    )
    
    # Fill states if needed
    title_extra = f"filled = {fill_fraction:.3f}"
    
    if fill_fraction > 0:
        # Sort energies for filling
        E_flat = E_fill.ravel()
        sorted_indices = np.argsort(E_flat)
        
        occ = occupied_mask(sorted_indices, E_fill.shape, fill_fraction)
        E_occ = np.where(occ, E_fill, np.nan)
        
        if np.any(occ):
            ax.plot_surface(
                KX, KY, E_occ,
                cmap="viridis",
                vmin=E_fill.min(),
                vmax=E_fill.max(),
                linewidth=0,
                antialiased=False,
                alpha=0.95
            )
            
            # Add contour projection at bottom
            ax.contourf(
                KX, KY, occ.astype(float),
                zdir="z",
                offset=-0.8,
                levels=[0.5, 1.5],
                colors=["tab:blue"],
                alpha=0.25
            )
            
            EF = E_fill[occ].max()
            title_extra += rf", $E_F \approx {EF:.2f}$"
    
    # Set labels and limits
    kmax = np.pi / a
    ax.set_xlim(-kmax, kmax)
    ax.set_ylim(-kmax, kmax)
    ax.set_zlim(-0.8, max(E_free.max(), E_fill.max()) * 1.03)
    
    ax.set_xlabel(r"$k_x$")
    ax.set_ylabel(r"$k_y$")
    ax.set_zlabel(r"$E(k)$")
    
    # Set title
    ax.set_title(f"{title_main}\n{formula}\n{title_extra}", pad=18)
    
    # Set viewing angle
    ax.view_init(elev=elevation, azim=azimuth)
    
    return fig

# ============================================================
# Main App
# ============================================================
def main():
    st.title("2D Band Structure Visualization")
    st.markdown("---")
    
    # Sidebar controls
    st.sidebar.header("Controls")
    
    # Band filling slider
    fill_fraction = st.sidebar.slider(
        "Band Filling",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.001,
        help="Fraction of electronic states filled (0 = empty, 1 = full)"
    )
    
    # Dispersion type selection
    dispersion_type = st.sidebar.radio(
        "Dispersion Type",
        ["Free", "Tight-binding"],
        help="Choose between free-electron or tight-binding dispersion"
    )
    
    # Hopping strength slider (only for tight-binding)
    if dispersion_type == "Tight-binding":
        hopping_t = st.sidebar.slider(
            "Hopping Strength t",
            min_value=0.1,
            max_value=5.0,
            value=1.0,
            step=0.1,
            help="Hopping parameter for tight-binding dispersion"
        )
    else:
        hopping_t = 1.0
    
    # Camera controls
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Camera View")
    
    elevation = st.sidebar.slider(
        "Elevation",
        min_value=-90,
        max_value=90,
        value=28,
        step=1,
        help="Vertical angle of the camera (degrees)"
    )
    
    azimuth = st.sidebar.slider(
        "Azimuth",
        min_value=0,
        max_value=360,
        value=-55,
        step=1,
        help="Horizontal rotation angle of the camera (degrees)"
    )
    
    # Debug display for camera angles
    st.sidebar.markdown("### Debug Info")
    st.sidebar.write(f"Elevation: {elevation}°")
    st.sidebar.write(f"Azimuth: {azimuth}°")
    
    # Information section
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info("""
    This interactive visualization shows:
    - **Free-electron dispersion**: $E(k) = k_x^2 + k_y^2$
    - **Tight-binding dispersion**: $E(k) = t[2 - \\cos(k_x a) - \\cos(k_y a)] \\cdot \\frac{2}{a^2}$
    
    Adjust the band filling to see how electrons occupy energy states up to the Fermi level.
    """)
    
    # Main visualization
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 3D Band Structure")
        
        # Create and display the plot
        fig = create_band_plot(dispersion_type, fill_fraction, hopping_t, elevation, azimuth)
        st.pyplot(fig, use_container_width=True, key=f"plot_{elevation}_{azimuth}_{fill_fraction}_{dispersion_type}_{hopping_t}")
    
    with col2:
        st.markdown("### Parameters")
        st.metric("Lattice Constant", f"a = {a:.1f}")
        st.metric("Grid Points", f"{nk}×{nk}")
        st.metric("Filling", f"{fill_fraction:.1%}")
        
        if dispersion_type == "Tight-binding":
            st.metric("Hopping t", f"{hopping_t:.2f}")
            
            # Calculate bandwidth
            E_tb = calculate_tight_binding(hopping_t)
            bandwidth = E_tb.max() - E_tb.min()
            st.metric("Bandwidth", f"{bandwidth:.2f}")
        
        # Add physics explanation
        st.markdown("---")
        st.markdown("### Physics")
        if fill_fraction == 0:
            st.write("No electrons in the system")
        elif fill_fraction < 0.5:
            st.write("Partially filled band - metallic behavior")
        elif fill_fraction == 0.5:
            st.write("Half-filled band - special case")
        else:
            st.write("More than half-filled - approaching full band")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Instructions:** Use the controls in the sidebar to adjust the band filling and dispersion parameters. 
    The 3D plot updates in real-time to show how electrons occupy the energy states.
    """)
    
    # Reset button
    if st.button("Reset to Defaults"):
        st.rerun()

if __name__ == "__main__":
    main()
