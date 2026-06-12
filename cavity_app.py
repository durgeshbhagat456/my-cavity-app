"""
cavity_app.py
=============
Streamlit dashboard — Cavity-Enhanced SPDC Parameter Explorer
Run locally:  streamlit run cavity_app.py
Deploy free:  push to GitHub → connect to share.streamlit.io
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title  = "SPDC Cavity Explorer",
    page_icon   = "🔬",
    layout      = "wide",
)

st.title("🔬 Cavity-Enhanced SPDC — Parameter Range Explorer")
st.markdown(
    "**QuIC Lab, Raman Research Institute** &nbsp;|&nbsp; "
    "PPKTP Type-II, Signal λ = 637 nm (NV-centre ZPL)"
)

# ─────────────────────────────────────────────────────────────────────────────
# DOCUMENTATION / HOW TO USE
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("📖 Quick Guide: How to Use & Theory", expanded=False):
    st.write("### ⚙️ How to Interact with this Tool")
    
    st.write("1. Set Cavity parameters in the sidebar: Mirror ROC (R), Crystal length (L_c), Refractive index (n_s), and Effective round-trip reflectivity (R_eff).")
    
    st.write("Finesse Calculation: The cavity Finesse (F) is calculated dynamically from the selected reflectivity (R_eff) using the formula: F = (pi * R_eff^0.25) / (1 - sqrt(R_eff)).")
    
    st.write("Dynamic Distance Range: Depending on the parameters you choose, the physical mirror separation (d_phys) slider automatically updates its range to match the theoretically allowed stable cavity bounds. The plots will automatically rescale to match this range.")
    
    st.write("Live Readouts: As you adjust any parameter, the metric cards at the top and all six plots will update instantly to show the corresponding cavity outputs.")
    
    st.write("2. Adjust the physical distance (d_phys) using the last slider. This updates the live values on the metric cards at the top and moves the red vertical line on all plots to show where your current physical configuration lies.")
    
    st.write("Achievable Tuning Ranges: The grey range at the bottom of each metric card displays the minimum and maximum values you can achieve for that parameter by physically tuning the mirror separation (d_phys) from the minimum to the maximum stable limits in the lab, keeping all other parameters (ROC, reflectivity, crystal length, index) fixed.")
    
    st.write("### 🔬 Target Windows & Design Constraints")
    
    st.write("NV-Centre Linewidth Target (10 to 40 MHz): For efficient coupling of the generated signal photons to the Nitrogen-Vacancy (NV) center Zero Phonon Line (ZPL), the cavity linewidth should match the NV lifetime profile (taken as 10 to 40 MHz). The Linewidth card shows a checkmark (✅) when your selection is inside this window, and the cavity linewidth plot highlights it with a green horizontal band.")
    
    st.write("Stability Parameter (U): A cavity is stable when U is between 0 and 1. For optimal performance, a good stability range is 0.60 to 0.95. The Stability card shows a checkmark (✅) if the cavity is stable, and the stability plot highlights this zone with a blue horizontal band.")
    
    st.write("Confocal Cavity Condition: The white dashed vertical line marked 'confocal' shows the point where the mirror separation equals the mirror ROC plus the crystal correction factor: d_phys = R + L_c(1 - 1/n_s).")
    
    st.write("Concentric Cavity Condition: The orange dotted vertical line marked 'concentric' shows the point where the cavity becomes concentric: d_phys = 2R + L_c(1 - 1/n_s). At this limit, the beam waist goes to zero and U reaches 1.")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
c        = 3e8
lam      = 637e-9

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR — all sliders
# ─────────────────────────────────────────────────────────────────────────────
st.sidebar.header("⚙️  Cavity Parameters")

R_mm   = st.sidebar.slider("Mirror ROC  R  [mm]",         10.0, 150.0, 50.0,  step=1.0)
Lc_mm  = st.sidebar.slider("Crystal length  L_c  [mm]",    5.0,  50.0, 30.0,  step=1.0)
n_val  = st.sidebar.slider("Signal refractive index  n_s", 1.50,  2.20,  1.77, step=0.01)
Reff_val = st.sidebar.slider("Effective reflectivity  R_eff", 0.500, 0.999, 0.940, step=0.001)
F_val  = (np.pi * (Reff_val ** 0.25)) / (1 - np.sqrt(Reff_val))
st.sidebar.caption(f"Calculated Finesse $F$: {F_val:.1f}")

st.sidebar.divider()
st.sidebar.header("📍  Point of Interest")

R_v   = R_mm  * 1e-3
Lc_v  = Lc_mm * 1e-3
n_i   = 1.745
dnu_SPDC = 0.44 * c / (Lc_v * max(abs(n_i - n_val), 1e-4))

# ─────────────────────────────────────────────────────────────────────────────
# PHYSICS FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def d_corr(Lc, n):         return Lc * (1 - 1/n)
def d_phys_min(Lc, n):     return d_corr(Lc, n)
def d_phys_max(R, Lc, n):  return 2*R + d_corr(Lc, n)
def d_phys_conf(R, Lc, n): return R  + d_corr(Lc, n)

def w0(dp, R, Lc, n):
    x   = (dp - d_corr(Lc, n)) / R
    fac = x * (2 - x)
    fac = np.where(fac > 0, fac, np.nan)
    return np.sqrt(lam * R / (2*np.pi)) * fac**0.25

def U(dp, R, Lc, n):
    x = (dp - d_corr(Lc, n)) / R
    return (1 - x)**2

def L_rt(dp, Lc, n):       return 2 * (dp + Lc*(n - 1))
def FSR(dp, Lc, n):        return c / L_rt(dp, Lc, n)
def linewidth(dp, Lc, n, F): return FSR(dp, Lc, n) / F
def tau(dp, Lc, n, F):     return 1 / (2*np.pi * linewidth(dp, Lc, n, F))
def N_modes(dp, Lc, n):    return dnu_SPDC / FSR(dp, Lc, n)

def escape_efficiency(Reff):
    T_ip = 0.001     # 0.1% transmission input mirror
    L_int = 0.011    # 1.1% round-trip loss
    if isinstance(Reff, np.ndarray):
        T_op = np.maximum(1.0 - Reff / (1.0 - T_ip), 0.0)
        denom = T_ip + T_op + L_int
        return np.where(denom > 0, T_op / denom, 0.0)
    else:
        T_op = max(1.0 - Reff / (1.0 - T_ip), 0.0)
        denom = T_ip + T_op + L_int
        return (T_op / denom) if denom > 0 else 0.0

# ─────────────────────────────────────────────────────────────────────────────
# d_phys slider — range updates dynamically with R and Lc
# ─────────────────────────────────────────────────────────────────────────────
dp_min_mm = d_phys_min(Lc_v, n_val) * 1e3 * 1.002
dp_max_mm = d_phys_max(R_v, Lc_v, n_val) * 1e3 * 0.998
dp_conf_mm = d_phys_conf(R_v, Lc_v, n_val) * 1e3
dp_init   = float(np.clip(dp_conf_mm, dp_min_mm, dp_max_mm))

dp_mm = st.sidebar.slider(
    "d_phys  [mm]  (mirror separation)",
    min_value = round(dp_min_mm, 1),
    max_value = round(dp_max_mm, 1),
    value     = round(dp_init, 1),
    step      = 0.5,
)

dp_v = dp_mm * 1e-3

# ─────────────────────────────────────────────────────────────────────────────
# LIVE READOUT & TUNING RANGES — metric cards at top
# ─────────────────────────────────────────────────────────────────────────────
w0_pt  = w0(dp_v,  R_v, Lc_v, n_val) * 1e6
fsr_pt = FSR(dp_v, Lc_v, n_val) / 1e9
lw_pt  = linewidth(dp_v, Lc_v, n_val, F_val) / 1e6
tau_pt = tau(dp_v, Lc_v, n_val, F_val) * 1e9
N_pt   = N_modes(dp_v, Lc_v, n_val)
U_pt   = U(dp_v, R_v, Lc_v, n_val)

nv_ok  = "✅" if 10 <= lw_pt <= 40 else "❌"
stab_ok = "✅" if 0 < U_pt < 1 else "❌"

# Calculate achievable ranges over the stable tuning region
dp_min_stable = d_phys_min(Lc_v, n_val)
dp_max_stable = d_phys_max(R_v, Lc_v, n_val)

w0_max_val = w0(d_phys_conf(R_v, Lc_v, n_val), R_v, Lc_v, n_val) * 1e6
fsr_min_val = FSR(dp_max_stable, Lc_v, n_val) / 1e9
fsr_max_val = FSR(dp_min_stable, Lc_v, n_val) / 1e9
lw_min_val = linewidth(dp_max_stable, Lc_v, n_val, F_val) / 1e6
lw_max_val = linewidth(dp_min_stable, Lc_v, n_val, F_val) / 1e6
N_min_val = N_modes(dp_min_stable, Lc_v, n_val)
N_max_val = N_modes(dp_max_stable, Lc_v, n_val)
eta_esc_pt = escape_efficiency(Reff_val) * 100

c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Beam Waist  w₀",    f"{w0_pt:.2f} µm", delta=f"Range: 0.00 – {w0_max_val:.2f} µm", delta_color="off")
c2.metric("FSR",               f"{fsr_pt:.3f} GHz", delta=f"Range: {fsr_min_val:.3f} – {fsr_max_val:.3f} GHz", delta_color="off")
c3.metric(f"Linewidth {nv_ok}", f"{lw_pt:.2f} MHz", delta=f"Range: {lw_min_val:.2f} – {lw_max_val:.2f} MHz", delta_color="off")
c4.metric("Escape Efficiency η_esc", f"{eta_esc_pt:.1f}%", delta="Independent of d_phys", delta_color="off")
c5.metric("Longitudinal modes", f"{N_pt:.0f}", delta=f"Range: {N_min_val:.0f} – {N_max_val:.0f}", delta_color="off")
c6.metric(f"Stability U {stab_ok}", f"{U_pt:.4f}", delta="Range: 0.0000 – 1.0000", delta_color="off")

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# RANGE TABLE
# ─────────────────────────────────────────────────────────────────────────────
with st.expander("📋  Full Parameter Range Table", expanded=False):
    dp_arr = np.linspace(dp_min_mm*1e-3*1.002, dp_max_mm*1e-3*0.998, 5)
    rows   = []
    for dp_i in dp_arr:
        rows.append({
            "d_phys [mm]"  : f"{dp_i*1e3:.1f}",
            "w0 [µm]"      : f"{w0(dp_i, R_v, Lc_v, n_val)*1e6:.2f}",
            "FSR [GHz]"    : f"{FSR(dp_i, Lc_v, n_val)/1e9:.3f}",
            "Δν [MHz]"     : f"{linewidth(dp_i, Lc_v, n_val, F_val)/1e6:.2f}",
            "η_esc [%]"    : f"{escape_efficiency(Reff_val)*100:.1f}",
            "N_modes"      : f"{N_modes(dp_i, Lc_v, n_val):.0f}",
            "U"            : f"{U(dp_i, R_v, Lc_v, n_val):.4f}",
        })
    import pandas as pd
    st.dataframe(pd.DataFrame(rows), width='stretch')

# ─────────────────────────────────────────────────────────────────────────────
# MAIN PLOTS
# ─────────────────────────────────────────────────────────────────────────────
dp_arr  = np.linspace(dp_min_mm*1e-3*1.002, d_phys_max(R_v, Lc_v, n_val), 800)
conf_mm = dp_conf_mm
conc_mm = d_phys_max(R_v, Lc_v, n_val) * 1e3
Reff_arr = np.linspace(0.50, 0.999, 800)

panels = [
    # (x_data, y_data, title, xlabel, ylabel, color)
    (dp_arr*1e3, w0(dp_arr, R_v, Lc_v, n_val)*1e6,
     'Beam waist  w₀',         'd_phys  [mm]', 'w₀  [µm]',   '#4fc3f7'),
    (dp_arr*1e3, FSR(dp_arr, Lc_v, n_val)/1e9,
     'Free spectral range',    'd_phys  [mm]', 'FSR  [GHz]',  '#81c995'),
    (dp_arr*1e3, linewidth(dp_arr, Lc_v, n_val, F_val)/1e6,
     'Cavity linewidth  Δν',   'd_phys  [mm]', 'Δν  [MHz]',   '#ffb74d'),
    (Reff_arr, escape_efficiency(Reff_arr)*100,
     'Escape Efficiency  η_esc', 'R_eff',      'η_esc  [%]',  '#ce93d8'),
    (dp_arr*1e3, N_modes(dp_arr, Lc_v, n_val),
     'Longitudinal modes  N',  'd_phys  [mm]', 'N_modes',      '#ef9a9a'),
    (dp_arr*1e3, U(dp_arr, R_v, Lc_v, n_val),
     'Stability  U = (1−x)²',  'd_phys  [mm]', 'U',            '#80cbc4'),
]

fig = plt.figure(figsize=(14, 9))
fig.patch.set_facecolor('#0d1117')
gs  = gridspec.GridSpec(3, 2, figure=fig, hspace=0.55, wspace=0.38)

for idx, (xd, yd, title, xlabel, ylabel, col) in enumerate(panels):
    ax = fig.add_subplot(gs[idx//2, idx%2])
    ax.set_facecolor('#161b22')
    ax.plot(xd, yd, color=col, lw=2.0)

    if xlabel == 'd_phys  [mm]':
        # confocal line
        ax.axvline(conf_mm, color='#ffffff', lw=0.9, ls='--',
                   alpha=0.5, label='confocal')

        # concentric line
        ax.axvline(conc_mm, color='#ffa726', lw=0.9, ls=':',
                   alpha=0.6, label='concentric')

        # current d_phys marker
        ax.axvline(dp_mm, color='#ef9a9a', lw=1.8, ls='-',
                   alpha=0.95, label=f'd={dp_mm:.1f} mm')
    elif xlabel == 'R_eff':
        # current R_eff marker
        ax.axvline(Reff_val, color='#ef9a9a', lw=1.8, ls='-',
                   alpha=0.95, label=f'R_eff={Reff_val:.3f}')

    # NV linewidth band on linewidth plot
    if 'Δν' in title:
        ax.axhspan(10, 40, color='#81c995', alpha=0.12, label='NV 10–40 MHz')

    # stability band on U plot
    if 'Stability' in title:
        ax.axhspan(0.60, 0.95, color='#4fc3f7', alpha=0.12, label='good range')

    ax.set_title(title,           color='#e6edf3', fontsize=10, pad=6)
    ax.set_xlabel(xlabel,         color='#8b949e', fontsize=8)
    ax.set_ylabel(ylabel,         color='#8b949e', fontsize=8)
    ax.tick_params(colors='#8b949e', labelsize=7)
    for sp in ax.spines.values():
        sp.set_edgecolor('#30363d')
    ax.legend(fontsize=7, labelcolor='#8b949e',
              facecolor='#161b22', edgecolor='#30363d')

fig.suptitle(
    f'R = {R_mm:.0f} mm  |  L_c = {Lc_mm:.0f} mm  |  n_s = {n_val:.2f}  |  '
    f'R_eff = {Reff_val:.3f} (F = {F_val:.1f})  |  λ = {lam*1e9:.0f} nm',
    color='#e6edf3', fontsize=11, y=0.99
)

st.pyplot(fig)
plt.close(fig)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "QuIC Lab · Raman Research Institute · Durgesh Kumar  |  "
    "Supervisor: Prof. Urbasi Sinha  |  SRO-637 Cavity Design Tool"
)
