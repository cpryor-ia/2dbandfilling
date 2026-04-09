#!/usr/bin/env python3

import streamlit as st
import numpy as np
import matplotlib
# Force Agg backend and configure for headless environment
matplotlib.use('Agg')
matplotlib.rcParams['figure.max_open_warning'] = 0
matplotlib.rcParams['agg.path.chunksize'] = 10000
import matplotlib.pyplot as plt
import io
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

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

def create_band_plot_2d(dispersion_type, fill_fraction, hopping_t):
    """Create 2D contour plot as fallback for 3D issues"""
    try:
        # Clear any existing figures
        plt.close('all')
        
        # Calculate energies
        if dispersion_type == "Free":
            E_fill = E_free
            title_main = "2D square lattice: free-electron dispersion"
            formula = r"$E(k) = k_x^2 + k_y^2$"
        else:
            E_tb = calculate_tight_binding(hopping_t)
            E_fill = E_tb
            title_main = "2D square lattice: tight-binding dispersion"
            formula = r"$E(k) = t[2 - \cos(k_x a) - \cos(k_y a)] \cdot \frac{2}{a^2}$"
        
        # Create 2D figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=100)
        fig.patch.set_facecolor('white')
        fig.set_constrained_layout(True)
        
        # Left plot: Energy contour
        levels = 20
        contour = ax1.contourf(KX, KY, E_fill, levels=levels, cmap='viridis')
        ax1.contour(KX, KY, E_fill, levels=levels, colors='black', alpha=0.3, linewidths=0.5)
        fig.colorbar(contour, ax=ax1, label=r'$E(k)$')
        
        # Fill states if needed
        title_extra = f"filled = {fill_fraction:.3f}"
        
        if fill_fraction > 0:
            # Sort energies for filling
            E_flat = E_fill.ravel()
            sorted_indices = np.argsort(E_flat)
            
            occ = occupied_mask(sorted_indices, E_fill.shape, fill_fraction)
            
            if np.any(occ):
                # Overlay occupied states
                ax1.contour(KX, KY, occ.astype(float), levels=[0.5], colors='red', linewidths=2)
                EF = E_fill[occ].max()
                title_extra += rf", $E_F \approx {EF:.2f}$"
        
        # Right plot: Cross-section
        mid_idx = nk // 2
        ax2.plot(KX[mid_idx, :], E_fill[mid_idx, :], 'b-', linewidth=2)
        
        if fill_fraction > 0:
            E_flat = E_fill.ravel()
            sorted_indices = np.argsort(E_flat)
            occ = occupied_mask(sorted_indices, E_fill.shape, fill_fraction)
            
            if np.any(occ):
                E_cross = E_fill[mid_idx, :]
                occ_cross = occ[mid_idx, :]
                ax2.fill_between(KX[mid_idx, :], E_cross, 
                                where=occ_cross, alpha=0.3, color='blue', label='Occupied')
                ax2.legend()
        
        # Set labels and limits
        kmax = np.pi / a
        ax1.set_xlim(-kmax, kmax)
        ax1.set_ylim(-kmax, kmax)
        ax1.set_xlabel(r"$k_x$")
        ax1.set_ylabel(r"$k_y$")
        ax1.set_title("Energy Contour")
        
        ax2.set_xlim(-kmax, kmax)
        ax2.set_ylim(E_fill.min() * 0.9, E_fill.max() * 1.1)
        ax2.set_xlabel(r"$k_x$ (at $k_y=0$)")
        ax2.set_ylabel(r"$E(k)$")
        ax2.set_title("Energy Cross-section")
        ax2.grid(True, alpha=0.3)
        
        # Set title
        fig.suptitle(f"{title_main}\n{formula}\n{title_extra}", fontsize=14)
        
        # Force draw the figure
        fig.canvas.draw()
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating 2D plot: {str(e)}")
        plt.close('all')
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, f"2D plot generation failed\nError: {str(e)}", 
                ha='center', va='center', transform=ax.transAxes)
        fig.canvas.draw()
        return fig

def create_band_plot(dispersion_type, fill_fraction, hopping_t, elevation=28, azimuth=-55):
    """Create 3D plot with fallback to 2D"""
    try:
        # Clear any existing figures
        plt.close('all')
        
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
        
        # Create figure with explicit backend and DPI
        fig = plt.figure(figsize=(12, 8), dpi=100)
        ax = fig.add_subplot(111, projection="3d")
        
        # Set figure properties to avoid buffer issues
        fig.patch.set_facecolor('white')
        fig.set_constrained_layout(True)
        
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
        ax.set_zlabel(r"E(k)$")
        
        # Set title
        ax.set_title(f"{title_main}\n{formula}\n{title_extra}", pad=18)
        
        # Set viewing angle
        ax.view_init(elev=elevation, azim=azimuth)
        
        # Force draw the figure to ensure it's rendered
        fig.canvas.draw()
        
        return fig
        
    except Exception as e:
        st.error(f"Error creating plot: {str(e)}")
        # Return a simple figure as fallback
        plt.close('all')
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, f"Plot generation failed\nError: {str(e)}", 
                ha='center', va='center', transform=ax.transAxes)
        fig.canvas.draw()
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
        st.markdown("### Band Structure Visualization")
        
        # Try 3D plot first, fallback to 2D if it fails
        try:
            fig = create_band_plot(dispersion_type, fill_fraction, hopping_t, elevation, azimuth)
            plot_type = "3D"
        except Exception as e:
            st.warning(f"3D plot failed, using 2D fallback: {str(e)}")
            fig = create_band_plot_2d(dispersion_type, fill_fraction, hopping_t)
            plot_type = "2D"
        
        st.pyplot(fig, use_container_width=True)
        
        # Clean up the figure to prevent memory issues
        plt.close(fig)
    
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
