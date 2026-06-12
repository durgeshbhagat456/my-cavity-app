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

### 8. Cavity Linewidth ($\Delta\nu$)
The full-width at half-maximum (FWHM) of the cavity transmission peaks is:
$$\Delta\nu = \frac{\text{FSR}}{F}$$
Where $F$ is the cavity Finesse calculated above.

### 9. Photon Coherence/Lifetime ($\tau_c$)
The characteristic decay time of a photon inside the cavity is:
$$\tau_c = \frac{1}{2\pi \cdot \Delta\nu}$$

### 10. Number of Longitudinal Modes ($N_{\text{modes}}$)
The total number of cavity modes that fall within the SPDC spectrum bandwidth ($\Delta\nu_{\text{SPDC}} \sim 1 \text{ THz}$) is:
$$N_{\text{modes}} = \frac{\Delta\nu_{\text{SPDC}}}{\text{FSR}}$$

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
