#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons

# ============================================================
# Parameters
# ============================================================
a = 1.0
nk = 121

# ============================================================
# k-grid in the first Brillouin zone of a square lattice
# ============================================================
kmax = np.pi / a
kx = np.linspace(-kmax, kmax, nk)
ky = np.linspace(-kmax, kmax, nk)
KX, KY = np.meshgrid(kx, ky, indexing="xy")

qX = a * KX
qY = a * KY

# Free-electron dispersion
E_free = qX**2 + qY**2

# Tight-binding dispersion for square lattice, shifted so minimum is 0
E_tb_raw = 2.0 - np.cos(qX) - np.cos(qY)

# Scale TB to match effective mass at k=0: m*_tb = m*_free
# Free: d²E/dk² = 2, TB: d²E/dk² = a², so scale by 2/a²
tb_mass_scale = 2.0 / (a * a)
E_tb = tb_mass_scale * E_tb_raw

# Precompute sorted state orderings for filling
E_free_flat = E_free.ravel()
E_tb_flat = E_tb.ravel()
Ntot = E_free_flat.size

sorted_indices_free = np.argsort(E_free_flat)
sorted_indices_tb = np.argsort(E_tb_flat)

zmin = -0.8
zmax = max(E_free.max(), E_tb.max()) * 1.03

# ============================================================
# Figure setup
# ============================================================
fig = plt.figure(figsize=(10.2, 7.8))
ax = fig.add_subplot(111, projection="3d")
plt.subplots_adjust(bottom=0.20, left=0.15)

slider_ax = fig.add_axes([0.25, 0.075, 0.60, 0.035])
fill_slider = Slider(
    ax=slider_ax,
    label="Band Filling",
    valmin=0.0,
    valmax=1.0,
    valinit=0.0,
    valstep=0.001
)

radio_ax = fig.add_axes([0.025, 0.4, 0.12, 0.15])
radio_buttons = RadioButtons(radio_ax, ('Free', 'Tight-binding'))


ax.view_init(elev=28, azim=-55)

# ============================================================
# State
# ============================================================
state = {
    "dispersion_type": "Free",
    "fill_fraction": 0.0,
}

# ============================================================
# Helpers
# ============================================================
def occupied_mask(sorted_indices: np.ndarray, shape, fill_fraction: float) -> np.ndarray:
    n_occ = int(np.floor(fill_fraction * Ntot))
    occ_flat = np.zeros(Ntot, dtype=bool)
    if n_occ > 0:
        occ_flat[sorted_indices[:n_occ]] = True
    return occ_flat.reshape(shape)

def get_current_view(ax):
    elev = ax.elev
    azim = ax.azim
    roll = getattr(ax, "roll", 0.0)
    return elev, azim, roll

def restore_view(ax, elev, azim, roll):
    try:
        ax.view_init(elev=elev, azim=azim, roll=roll)
    except TypeError:
        ax.view_init(elev=elev, azim=azim)
      
def draw_scene():
    elev, azim, roll = get_current_view(ax)
    ax.cla()
    
    if state["dispersion_type"] == "Free":
        E_wire = E_free
        E_fill = E_free
        sorted_idx = sorted_indices_free
        title_main = "2D square lattice: free-electron dispersion"
    else:
        E_wire = E_tb
        E_fill = E_tb
        sorted_idx = sorted_indices_tb
        title_main = "2D square lattice: tight-binding dispersion"
    
    ax.plot_wireframe(
        KX, KY, E_wire,
        rstride=5,
        cstride=5,
        linewidth=0.65,
        color="0.35",
        alpha=0.95
    )
    
    fill_fraction = state["fill_fraction"]
    title_extra = f"filled = {fill_fraction:.3f}"
    
    if fill_fraction > 0:
        occ = occupied_mask(sorted_idx, E_fill.shape, fill_fraction)
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
            
            ax.contourf(
                KX, KY, occ.astype(float),
                zdir="z",
                offset=zmin,
                levels=[0.5, 1.5],
                colors=["tab:blue"],
                alpha=0.25
            )
            
            EF = E_fill[occ].max()
            title_extra += rf", $E_F \approx {EF:.2f}$"
        
    ax.set_xlim(-kmax, kmax)
    ax.set_ylim(-kmax, kmax)
    ax.set_zlim(zmin, zmax)
    
    ax.set_xlabel(r"$k_x$")
    ax.set_ylabel(r"$k_y$")
    ax.set_zlabel(r"$E(k)$")
    
    ax.set_title(title_main + "\n" + title_extra, pad=18)
    
    restore_view(ax, elev, azim, roll)

# ============================================================
# Controls
# ============================================================
def on_slider_change(val):
    state["fill_fraction"] = fill_slider.val
    draw_scene()
    fig.canvas.draw_idle()

def on_radio_change(label):
    state["dispersion_type"] = label
    draw_scene()
    fig.canvas.draw_idle()

fill_slider.on_changed(on_slider_change)
radio_buttons.on_clicked(on_radio_change)

# Initial draw
draw_scene()

plt.show()
