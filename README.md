# Cavity-Enhanced SPDC Parameter Explorer

This Streamlit dashboard is designed to analyze and explore parameter ranges for a **Cavity-Enhanced Spontaneous Parametric Down-Conversion (SPDC)** source of correlated photon pairs, optimized for coupling to the Zero Phonon Line (ZPL) of Nitrogen-Vacancy (NV) centers in diamond (Signal wavelength $\lambda = 637\text{ nm}$).

Developed for the **Quantum Information and Computing (QuIC) Lab, Raman Research Institute**.

---

## 🔬 Cavity Physics & Equations Used

Below are the exact equations and physical relations modeled in the application:

### 1. Crystal Optical Correction ($d_{\text{corr}}$)
The presence of a nonlinear crystal of length $L_c$ and refractive index $n_s$ modifies the optical path length compared to the physical mirror separation. The correction factor is given by:
$$d_{\text{corr}} = L_c \left(1 - \frac{1}{n_s}\right)$$

### 2. Physical Distance Limits
For a symmetric cavity with mirror Radius of Curvature (ROC) $R$:
* **Minimum Stable Physical Separation ($d_{\text{phys, min}}$)**:
  $$d_{\text{phys, min}} = d_{\text{corr}}$$
* **Confocal Cavity Separation ($d_{\text{phys, conf}}$)**:
  $$d_{\text{phys, conf}} = R + d_{\text{corr}}$$
* **Concentric Cavity Separation ($d_{\text{phys, max}}$)**:
  $$d_{\text{phys, max}} = 2R + d_{\text{corr}}$$

### 3. Stability Parameter ($U$)
The cavity stability parameter $U$ is defined using the normalized position coordinate $x$:
$$x = \frac{d_{\text{phys}} - d_{\text{corr}}}{R}$$
$$U = (1 - x)^2$$
The cavity is stable when $0 < U < 1$.

### 4. Cavity Mode Beam Waist ($w_0$)
The spot size of the cavity mode at the waist position (inside the crystal) is:
$$w_0 = \sqrt{\frac{\lambda R}{2\pi}} \left[ x (2 - x) \right]^{0.25}$$
Where:
* $\lambda = 637 \text{ nm}$ (NV-centre ZPL wavelength)
* $w_0$ goes to zero at the stability boundaries ($x = 0$ and $x = 2$).

### 5. Cavity Round-Trip Length ($L_{\text{rt}}$)
The total optical path length of a single round trip through the cavity, accounting for the crystal's physical length $L_c$ and refractive index $n_s$, is:
$$L_{\text{rt}} = 2 \left( d_{\text{phys}} + L_c (n_s - 1) \right)$$

### 6. Free Spectral Range (FSR)
The frequency spacing between adjacent longitudinal cavity modes is:
$$\text{FSR} = \frac{c}{L_{\text{rt}}}$$
Where $c = 3 \times 10^8 \text{ m/s}$ is the speed of light.

### 7. Cavity Finesse ($F$) from Reflectivity ($R_{\text{eff}}$)
The cavity Finesse is calculated dynamically from the effective round-trip reflectivity $R_{\text{eff}}$ using the relation:
$$F = \frac{\pi \sqrt[4]{R_{\text{eff}}}}{1 - \sqrt{R_{\text{eff}}}}$$

### 8. Cavity Linewidth ($\Delta\nu$) and Photon Lifetime ($\tau_c$)
The full-width at half-maximum (FWHM) of the cavity transmission peaks is:
$$\Delta\nu = \frac{\text{FSR}}{F}$$
Where $F$ is the cavity Finesse calculated above.

The photon lifetime (coherence time) inside the cavity is directly related to the linewidth by:
$$\tau_c = \frac{1}{2\pi \cdot \Delta\nu}$$
This represents the characteristic time a photon spends inside the resonator before escaping or being lost.

### 9. Escape Efficiency ($\eta_{\text{esc}}$)
The escape efficiency (the probability that a generated photon successfully exits the cavity through the output coupler rather than being lost) is given by:
$$\eta_{\text{esc}} = \frac{T_{\text{op}}}{T_{\text{ip}} + T_{\text{op}} + L_{\text{int}}}$$
Where:
* $T_{\text{ip}} = 0.001$ (0.1% transmission of the input coupler mirror)
* $L_{\text{int}} = 0.011$ (1.1% round-trip internal loss inside the cavity)
* $T_{\text{op}}$ is the transmission of the output coupler, related to the selected effective reflectivity $R_{\text{eff}}$ by:
  $$T_{\text{op}} = 1 - \frac{R_{\text{eff}}}{1 - T_{\text{ip}}}$$

### 10. Number of Longitudinal Modes ($N_{\text{modes}}$)
The total number of cavity modes that fall within the SPDC phase-matching spectrum bandwidth ($\Delta\nu_{\text{SPDC}}$) is:
$$N_{\text{modes}} = \frac{\Delta\nu_{\text{SPDC}}}{\text{FSR}}$$
Where $\Delta\nu_{\text{SPDC}}$ is determined by the group-velocity mismatch (GVM) inside the nonlinear crystal:
$$\Delta\nu_{\text{SPDC}} = \frac{0.44 \cdot c}{L_c \cdot |n_s - n_i|}$$
Here $n_i = 1.745$ is the extraordinary index of KTP, and $n_s$ is the signal refractive index. For typical values, this yields a bandwidth $\Delta\nu_{\text{SPDC}} \approx 163\text{ GHz}$.

### 11. Achievable Tuning Ranges (for fixed mirror/crystal)
For a set configuration of mirror ROC ($R$), reflectivity ($R_{\text{eff}}$), crystal length ($L_c$), and index ($n_s$), the only parameter tuned in the lab is the physical mirror separation $d_{\text{phys}}$. 

To avoid the mathematically unstable boundaries (where FSR, linewidth, and lifetime would blow up and the waist goes to zero), the dashboard evaluates these ranges across the user-adjustable slider limits:
$$d_{\text{phys}} \in \left[ 1.002 \cdot d_{\text{phys, min}}, \, 0.998 \cdot d_{\text{phys, max}} \right]$$

The dashboard calculates the exact minimum and maximum value of each parameter across this range and displays them as a grey subtext (`Range: Min – Max`) below each metric card. This shows you the practical boundaries you can tune within the stable regime.

### 12. Design Optimization Search Score
In the **Design Optimizer** tab, a grid search is performed over standard available mirror ROCs ($25, 50, 75, 100, 150\text{ mm}$) and reflectivity values ($90\%\text{ to }99\%$). For each configuration, it sweeps the physical distance to find the subset of distances where all user-defined constraints (linewidth target, waist target, and stability) are simultaneously satisfied. If a valid tuning window is found, it calculates a design score:
$$\text{Score} = w \cdot \eta_{\text{esc}} + (1 - w) \cdot \frac{100}{N_{\text{modes, mid}}} + \frac{\Delta d_{\text{phys, valid}}}{2}$$
Where:
* $w$ is the user's priority weight between escape efficiency and mode reduction.
* $N_{\text{modes, mid}}$ is the longitudinal mode count at the center of the valid tuning window.
* $\Delta d_{\text{phys, valid}}$ is the width of the valid tuning window (in mm). A higher score represents a more stable, efficient, and easier-to-align cavity.

---

## 🛠️ Installation & Local Run

To run this dashboard locally, ensure you have Python installed, then follow these steps:

1. Clone or download this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit application:
   ```bash
   streamlit run cavity_app.py
   ```
