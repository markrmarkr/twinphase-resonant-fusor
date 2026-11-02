#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""
TwinPhase Resonant Fusor — reproducible kinematics & order-of-magnitude calcs.
Masses: CODATA 2018 / AME2020 atomic masses (neutral atoms); ion masses =
atomic mass − Z·m_e (+ binding neglected at our sig-fig level).
"""
from __future__ import annotations
import math
from dataclasses import dataclass

# ---- constants (SI + nuclear convenience) ----
u = 1.66053906660e-27          # kg (CODATA 2018)
m_e = 9.1093837015e-31         # kg
e = 1.602176634e-19            # C
c = 2.99792458e8               # m/s
MeV = 1e6 * e                  # J
amu_MeV = 931.49410242         # MeV/u (CODATA)

# AME2020 atomic masses (u) — Wang et al., Chin. Phys. C 45, 030003 (2021)
M_H1_u  = 1.00782503224
M_Li7_u = 7.0160034366
M_He4_u = 4.00260325413
M_Be7_u = 7.01692871
M_n_u   = 1.00866491595

def ion_mass_u(atomic_u: float, Z: int) -> float:
    """Nuclear+electrons removed: atomic − Z m_e (u). Binding neglected."""
    return atomic_u - Z * (m_e / u)

m_p_u   = ion_mass_u(M_H1_u, 1)      # H+
m_Li_u  = ion_mass_u(M_Li7_u, 3)     # 7Li3+
m_a_u   = ion_mass_u(M_He4_u, 2)     # 4He2+
m_p     = m_p_u * u
m_Li    = m_Li_u * u
m_a     = m_a_u * u

# Approximate integer ratios used in pedagogical text
m_p_approx = 1.0
m_Li_approx = 7.0

def q_over_m_norm(q_e: float, m_u: float) -> float:
    """q/m relative to proton (q=1, m=m_p)."""
    return (q_e / m_u) / (1.0 / m_p_u)

@dataclass
class Result:
    name: str
    value: float
    unit: str
    note: str = ""

def section(title: str):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)

# ---- A1: energy gain, velocity, TOF scaling ----
section("A1. Energy gain, velocity, TOF ~ L sqrt(m/q)")
V = 1.8e6  # V illustrative Reflector/anode class
for name, q_e, mass in [("p", 1, m_p), ("7Li3+", 3, m_Li), ("4He2+", 2, m_a)]:
    E = q_e * e * V
    v = math.sqrt(2 * E / mass)
    print(f"  {name:8s}: E={E/MeV:.4f} MeV, v={v/1e6:.3f}e6 m/s, "
          f"sqrt(m/q)={math.sqrt(mass/(q_e*e)):.4e}")

# Bounce period scaling
print("\n  Bounce period T ∝ L √(m/q); resonant f = 1/T depends only on q/m "
      "(and L, potential shape).")
print(f"  q/m relative to proton:")
for name, q_e, mu in [("p", 1, m_p_u), ("7Li3+", 3, m_Li_u),
                      ("4He2+", 2, m_a_u), ("3He2+", 2, ion_mass_u(3.01602932265, 2)),
                      ("6Li3+", 3, ion_mass_u(6.0151228874, 3)),
                      ("D+", 1, ion_mass_u(2.01410177811, 1))]:
    print(f"    {name:8s}: q/m_norm = {q_over_m_norm(q_e, mu):.4f}  "
          f"(integer group ≈ {q_e}/{round(mu)})")

# ---- A2: relative / CM energy ----
section("A2. Relative/CM energy: head-on vs co-streaming shared-V")

mu_red = m_p * m_Li / (m_p + m_Li)
mu_red_u = m_p_u * m_Li_u / (m_p_u + m_Li_u)
print(f"  Reduced mass μ = {mu_red_u:.6f} u = {mu_red_u/m_p_u:.4f} m_p")

def E_rel_shared_V(V_volt: float, head_on: bool) -> float:
    """Both species accelerated from rest through potential V (volts).
    Energies: E_p = eV, E_Li = 3 eV. Head-on: v_rel = v_p+v_Li; else |v_p-v_Li|."""
    Ep = e * V_volt
    ELi = 3 * e * V_volt
    vp = math.sqrt(2 * Ep / m_p)
    vLi = math.sqrt(2 * ELi / m_Li)
    vrel = (vp + vLi) if head_on else abs(vp - vLi)
    return 0.5 * mu_red * vrel**2 / MeV  # MeV

# Factor: E_rel = k * eV  (E_rel in eV if V in volts, so E_rel/MeV = k * V/1e6)
# Using approx m_Li=7 m_p, q_Li=3:
# head-on: E_rel/e = (7/8)*V*(1+sqrt(3/7))^2
# co-stream: E_rel/e = (7/8)*V*(1-sqrt(3/7))^2
a = math.sqrt(3 * m_p / m_Li)  # = v_Li/v_p at shared V = sqrt(3 m_p/m_Li)
# more precisely v_Li/vp = sqrt( (3eV/m_Li) / (eV/m_p) ) = sqrt(3 m_p/m_Li)
r = math.sqrt(3 * m_p / m_Li)
k_head = (mu_red / m_p) * (1 + r) ** 2   # E_rel / (eV) dimensionless
k_co   = (mu_red / m_p) * (1 - r) ** 2
print(f"  v_Li/v_p at shared V: {r:.6f}")
print(f"  Head-on:   E_rel = {k_head:.4f} × eV   => E_rel/MeV = {k_head:.4f} × (V/MV)")
print(f"  Co-stream: E_rel = {k_co:.4f} × eV   => E_rel/MeV = {k_co:.4f} × (V/MV)")

E_design = 1.80  # MeV relative (paper design point)
V_head = E_design / k_head * 1e6  # volts
V_co   = E_design / k_co * 1e6
print(f"\n  For E_rel = {E_design} MeV:")
print(f"    shared-V head-on:   V = {V_head/1e6:.3f} MV  "
      f"(E_p={V_head/1e6:.3f} MeV, E_Li={3*V_head/1e6:.3f} MeV)")
print(f"    shared-V co-stream: V = {V_co/1e6:.3f} MV  "
      f"(E_p lab = {V_co/1e6:.2f} MeV)  <-- '~15 MeV-class' check")

# Verify numerically
print(f"    check head-on E_rel @ that V: {E_rel_shared_V(V_head, True):.4f} MeV")
print(f"    check co-stream E_rel @ that V: {E_rel_shared_V(V_co, False):.4f} MeV")

# Equal-momentum head-on split (classic)
# E_p = (m_Li/(m_p+m_Li)) E_rel, E_Li = (m_p/(m_p+m_Li)) E_rel
Ep_eq = m_Li / (m_p + m_Li) * E_design
ELi_eq = m_p / (m_p + m_Li) * E_design
Vp_eq = Ep_eq / 1.0   # MV for proton (q=1)
VLi_eq = ELi_eq / 3.0  # MV for Li3+
print(f"\n  Equal-momentum head-on at E_rel={E_design} MeV:")
print(f"    E_p = {Ep_eq:.4f} MeV  => V_p = {Vp_eq:.3f} MV")
print(f"    E_Li = {ELi_eq:.4f} MeV => V_Li = {VLi_eq*1e3:.1f} kV")

# Architecture-consistent: proton from ~1.8 MV Reflector, choose Li reflection
# so E_rel = 1.80 MeV head-on.
# E_p = 1.8 MeV (from 1.8 MV), need E_Li such that
# E_rel = 1/2 μ (v_p + v_Li)^2 = 1.80
Ep_arch = 1.80  # MeV
vp = math.sqrt(2 * Ep_arch * MeV / m_p)
# 1/2 μ (vp + vLi)^2 = E_design * MeV
# vp + vLi = sqrt(2 E_design MeV / μ)
vrel_needed = math.sqrt(2 * E_design * MeV / mu_red)
vLi_needed = vrel_needed - vp
if vLi_needed > 0:
    ELi_arch = 0.5 * m_Li * vLi_needed**2 / MeV
    VLi_arch = ELi_arch / 3.0
    print(f"\n  Architecture-illustrative: E_p = {Ep_arch} MeV (V_p≈1.80 MV), "
          f"head-on to E_rel={E_design} MeV:")
    print(f"    required E_Li = {ELi_arch:.4f} MeV  => V_Li(refl) = {VLi_arch*1e3:.1f} kV")
else:
    print("  Proton alone already exceeds design E_rel at 1.8 MeV head-on vs rest Li")
    # vs stationary Li: E_rel = Ep * m_Li/(m_p+m_Li)
    print(f"    E_rel vs stationary Li at Ep=1.8: "
          f"{Ep_arch * m_Li/(m_p+m_Li):.4f} MeV")

# Also compute for SUB-THRESHOLD design point
E_sub = 1.55  # MeV relative — below CM threshold
Ep_eq_s = m_Li / (m_p + m_Li) * E_sub
ELi_eq_s = m_p / (m_p + m_Li) * E_sub
print(f"\n  Equal-momentum head-on at E_rel={E_sub} MeV (sub-threshold illustrative):")
print(f"    E_p = {Ep_eq_s:.4f} MeV => V_p = {Ep_eq_s:.3f} MV")
print(f"    E_Li = {ELi_eq_s:.4f} MeV => V_Li = {ELi_eq_s/3*1e3:.1f} kV")

# Shared V for E_rel=1.55
V_head_s = E_sub / k_head * 1e6
print(f"    shared-V head-on: V = {V_head_s/1e6:.3f} MV")

# ---- A3: Q-value and alpha energies ----
section("A3. Reaction Q-value and alpha lab energies")
# Q from mass excess: p + 7Li -> 2 4He
# Using atomic masses carefully:
# Atomic: H + 7Li -> 2 4He  (electrons: 1+3 = 4 on left as neutral? 
# Actually: ion reaction p + 7Li3+ -> 2 4He2+ ; electron count: left 0+0 (fully stripped), right 0.
# Better: nuclear masses = atomic - Z m_e + binding≈0
# Q = [m_p + m_Li7_nucleus - 2 m_alpha_nucleus] c^2
# Nuclear mass ≈ atomic - Z m_e
m_p_nuc = (M_H1_u - 1*m_e/u) * amu_MeV  # MeV
m_Li_nuc = (M_Li7_u - 3*m_e/u) * amu_MeV
m_a_nuc = (M_He4_u - 2*m_e/u) * amu_MeV
# Wait — for Q-value the standard is atomic masses for p+7Li→2α:
# Because: 1H + 7Li → 2 4He (neutral atoms): electrons balance (1+3=4).
Q_atomic = (M_H1_u + M_Li7_u - 2*M_He4_u) * amu_MeV
print(f"  Q (atomic mass difference H+7Li−2·4He) = {Q_atomic:.4f} MeV")

# In CM at rest: each alpha gets Q/2
E_a_cm_rest = Q_atomic / 2
print(f"  Alpha energy in CM if reactants at rest: {E_a_cm_rest:.3f} MeV each")

# With finite E_rel: total CM energy available to products = Q + E_rel
# (non-relativistic; for E_rel << Q this is fine)
# Two identical alphas: each gets (Q+E_rel)/2 in CM frame
def alpha_lab_energies(E_rel_MeV, Ep_MeV, ELi_MeV):
    """Head-on along z. CM velocity of system, then alpha ±v_cm in CM."""
    # momenta before (1D head-on, opposite directions)
    # take +z for proton, -z for Li
    pp = math.sqrt(2 * m_p * Ep_MeV * MeV)
    pLi = math.sqrt(2 * m_Li * ELi_MeV * MeV)
    P_tot = pp - pLi  # net lab momentum
    M_tot = m_p + m_Li
    Vcm = P_tot / M_tot
    E_cm_kin = E_rel_MeV  # by construction for head-on definition
    E_a_cm = (Q_atomic + E_rel_MeV) / 2.0  # each alpha in CM
    p_a_cm = math.sqrt(2 * m_a * E_a_cm * MeV)
    # lab: alphas emitted at CM angle 0 and 180 for extreme collinear
    # E_lab = 1/2 m (Vcm ± v_a_cm)^2
    va_cm = p_a_cm / m_a
    E_fwd = 0.5 * m_a * (Vcm + va_cm)**2 / MeV
    E_bwd = 0.5 * m_a * (Vcm - va_cm)**2 / MeV
    # Also isotropic average: E_lab = E_cm + 1/2 m Vcm^2
    E_avg = E_a_cm + 0.5 * m_a * Vcm**2 / MeV
    return E_fwd, E_bwd, E_avg, E_a_cm, Vcm

# Equal-momentum case: Vcm=0, no spread from CM motion of system
E_f, E_b, E_avg, E_acm, Vcm = alpha_lab_energies(E_design, Ep_eq, ELi_eq)
print(f"\n  Equal-momentum head-on (Vcm≈0) at E_rel={E_design}:")
print(f"    E_α,CM = {E_acm:.3f} MeV; lab collinear extremes {E_b:.3f}–{E_f:.3f} MeV")

# Architecture case: Ep=1.8, ELi as computed
if vLi_needed > 0:
    E_f2, E_b2, E_avg2, E_acm2, Vcm2 = alpha_lab_energies(E_design, Ep_arch, ELi_arch)
    print(f"  Arch-illustrative Ep={Ep_arch}, ELi={ELi_arch:.3f}:")
    print(f"    E_α,CM = {E_acm2:.3f} MeV")
    print(f"    lab collinear extremes: {E_b2:.3f} – {E_f2:.3f} MeV")
    print(f"    isotropic mean lab: {E_avg2:.3f} MeV")
    print(f"    half-range spread about mean: ±{(E_f2-E_b2)/2:.3f} MeV")
    print(f"    Vcm = {Vcm2/1e5:.3f}e5 m/s")

# Stopping voltage for α2+: V_stop = E/(2e)
print(f"\n  Electrostatic stopping voltage for α²⁺: V_stop = E_α / (2e)")
print(f"    ~{E_a_cm_rest/2:.2f} MV for {E_a_cm_rest:.2f} MeV alphas (order {E_acm/2:.2f} MV at design)")

# ---- A4: (p,n) threshold ----
section("A4. 7Li(p,n)7Be threshold: lab vs CM")
# Q_pn from masses: 7Li + p -> 7Be + n
Q_pn = (M_Li7_u + M_H1_u - M_Be7_u - M_n_u) * amu_MeV
print(f"  Q(p,n) = {Q_pn:.4f} MeV (endothermic)")
# Lab threshold for stationary target: E_thr_lab = -Q * (m_p+m_Li)/m_Li
# More precisely with atomic/nuclear consistency:
E_thr_lab = -Q_pn * (M_H1_u + M_Li7_u) / M_Li7_u
# Standard measured ≈ 1.880 MeV
E_thr_lab_meas = 1.8804  # MeV (White et al. / commonly quoted)
E_thr_cm = E_thr_lab_meas * M_Li7_u / (M_H1_u + M_Li7_u)
# Also E_thr_cm = -Q for the relative energy at threshold (approx)
print(f"  From masses: E_thr^lab ≈ {E_thr_lab:.4f} MeV")
print(f"  Adopted measured E_thr^lab ≈ {E_thr_lab_meas} MeV (proton on stationary 7Li)")
print(f"  => E_thr^CM = E_rel,thr = {E_thr_cm:.4f} MeV")
print(f"  Design E_rel=1.80 MeV is {E_design - E_thr_cm:+.3f} MeV relative to CM threshold")
print(f"  *** FLAG: 1.80 MeV relative is ABOVE (p,n) CM threshold ***")
margin_lab_equiv = E_thr_lab_meas - E_design  # if someone confused frames
print(f"  If design meant 1.80 MeV LAB-equivalent on stationary target: "
      f"margin {margin_lab_equiv*1e3:.0f} keV below lab threshold;")
print(f"    corresponding E_rel = {E_design * M_Li7_u/(M_H1_u+M_Li7_u):.4f} MeV")

# ---- B5: bounce periods ----
section("B5. Illustrative bounce periods / RF frequency")
# Triangular or square-well-ish: T ≈ 4 L / <v> with <v> ~ v_max/something
# For harmonic: T = 2π sqrt(m/(q k)); for flat well + hard wall: T = 4L/v
# Use hard-wall half-length L: round-trip 4L at speed v=sqrt(2qV/m)
for L in [0.5, 1.0]:  # m half-path reflection-to-midplane approx
    print(f"  Illustrative half-length L = {L} m (reflection→midplane), V=1.8 MV class:")
    for name, q_e, mass in [("p", 1, m_p), ("7Li3+", 3, m_Li)]:
        # For Li, reflection potential is lower — use V_Li from equal-momentum for design
        V_use = V if name == "p" else VLi_eq * 1e6
        # Actually for frequency comparison at THEIR reflection voltages:
        E = q_e * e * V_use
        v = math.sqrt(2 * E / mass)
        T = 4 * L / v  # full bounce
        f = 1 / T
        print(f"    {name}: V={V_use/1e3:.1f} kV, v={v/1e6:.2f}e6 m/s, "
              f"T={T*1e6:.2f} μs, f={f/1e6:.2f} MHz")
    # Nested bucket: same RF frequency — Li cavity length scales
    # f_p = f_Li => L_Li / L_p = sqrt( (m_Li/q_Li) / (m_p/q_p) ) * (v factors from V)
    # With different V: T=4L/sqrt(2qV/m) = 4L sqrt(m/(2qV))
    # Same f: L_Li/L_p = sqrt( (m_p/(q_p V_p)) / (m_Li/(q_Li V_Li)) ) wait inverse:
    # L ∝ T * sqrt(qV/m) ∝ sqrt(qV/m) at fixed T
    Lp = L
    Vp = V
    VLi = VLi_eq * 1e6
    LLi = Lp * math.sqrt((m_Li / (3 * e * VLi)) / (m_p / (1 * e * Vp)))
    # From T_p=T_Li: 4 Lp / vp = 4 LLi / vLi => LLi = Lp * vLi/vp
    vp = math.sqrt(2 * e * Vp / m_p)
    vLi = math.sqrt(2 * 3 * e * VLi / m_Li)
    LLi2 = Lp * vLi / vp
    print(f"    For same bounce period as proton @ L_p={Lp}m: L_Li ≈ {LLi2:.3f} m "
          f"(at V_Li={VLi/1e3:.1f} kV)")

# Scaling only with q/m at SAME V and SAME L:
print("\n  Same L, same V: f ∝ sqrt(q/m); f_Li/f_p = sqrt( (3/m_Li)/(1/m_p) ) = "
      f"{math.sqrt(3 * m_p / m_Li):.4f}")
print("  Nested buckets share one RF frequency ⇒ different cavity lengths "
      "(or different potentials) must satisfy T_p = T_Li.")

# ---- B6: Bremsstrahlung ----
section("B6. Bremsstrahlung scaling")
# P_br ∝ n_e Σ n_i Z_i^2 sqrt(T_e)
print("  P_br ∝ n_e Σ_i n_i Z_i² √T_e")
print("  Electron depletion (small n_e) linearly suppresses Brems.")
print(f"  Z²(Li)=9, Z²(B)=25; ratio B/Li = {25/9:.3f} at equal n_i, n_e, T_e")
print("  Per-fusion: radiation tax scales with the Z²-weighted ion mix "
      "and residual n_e; p–7Li is kinder than p–11B by Z² alone (~2.8×).")

# ---- B7: cross section & rate ----
section("B7. Cross-section and illustrative rate")
# Taskaev et al. NIMB 2022: σ(1.853 MeV lab) = 30.57 mb
# Abramovich eval: σ(1.8 MeV lab) = 32.73 mb
# Convert lab to CM: E_cm = E_lab * M_Li/(M_p+M_Li)
sig_taskaev_1853 = 30.57  # mb at 1.853 MeV lab
Ecm_1853 = 1.853 * M_Li7_u / (M_H1_u + M_Li7_u)
sig_abram_18 = 32.73  # mb at 1.8 MeV lab
Ecm_18 = 1.8 * M_Li7_u / (M_H1_u + M_Li7_u)
print(f"  Taskaev et al. (NIMB 2022): σ = {sig_taskaev_1853} mb at E_lab=1.853 MeV "
      f"(E_CM≈{Ecm_1853:.3f} MeV)")
print(f"  Abramovich evaluation (EXFOR): σ = {sig_abram_18} mb at E_lab=1.8 MeV "
      f"(E_CM≈{Ecm_18:.3f} MeV)")
print(f"  Note: ENDF/B-VIII.0 is ~½ of Taskaev/Abramovich/JENDL near 1.8 MeV (literature discrepant).")
print(f"  For E_rel=1.80 MeV (above CM threshold): interpolate roughly — "
      f"E_lab,equiv = 1.80 * (M_p+M_Li)/M_Li = "
      f"{1.80*(M_H1_u+M_Li7_u)/M_Li7_u:.3f} MeV lab-stationary")
# At ~2.06 MeV lab, Taskaev has 36.62 mb at 2.008 MeV
sig_approx_180_rel = 35.0  # mb rough near 2.0 MeV lab
print(f"  Approximate σ ~ 30–37 mb near E_CM~1.6–1.75 MeV; ~35 mb class near "
      f"E_rel=1.80 MeV (order-of-magnitude only).")

# Rate per pair: R = n1 n2 <σv>
# Illustrative densities
n = 1e18  # m^-3 = 1e12 cm^-3 illustrative dilute
sig = 30e-31  # 30 mb = 30e-31 m^2 (1 mb = 1e-31 m^2)
# v_rel at E_rel=1.8 MeV
v_rel = math.sqrt(2 * E_design * MeV / mu_red)
rate_vol = n * n * sig * v_rel  # reactions m^-3 s^-1
print(f"  Illustrative: n_p = n_Li = {n:.0e} m^-3, σ=30 mb, E_rel=1.8 MeV:")
print(f"    v_rel = {v_rel/1e6:.2f}e6 m/s")
print(f"    n n σ v ≈ {rate_vol:.3e} m^-3 s^-1")
print(f"    Power density ≈ rate × Q ≈ {rate_vol * Q_atomic * MeV:.3e} W/m^3 "
      f"(tiny at this density — densification is OMR)")

# ---- B8: nested bucket math ----
section("B8. Nested-bucket frequency/phase matching")
print("  Requirement: f_RF common, Δφ = 180°.")
print("  Bounce: T_s = ∮ dz / v_s(z; V(z), q_s/m_s) = 1/f_RF  for each locked species s.")
print("  Scaling in similar potential wells: T ∝ L √(m/q) / √V_eff")
print("  Architecture constraint:")
print("    T_p(L_p, V_Reflector, q/m=1) = T_Li(L_Li, V_Li-cavity, q/m=3/7) = 1/f_RF")
print("    φ_Li(t) = φ_p(t) + π   (anti-phase meetings at interaction plateau)")

print("\nDone.")

# =====================================================================
# C. Operating-point control: T(E) in power-law wells  (added 2026-09-25)
# U(z) = qV (|z|/d)^n ;  T = 4 d I_n sqrt(m/2) E^(1/n - 1/2) (qV)^(-1/n)
# Synchronous energy E_s from T(E_s; V) = 1/f:
#   dlnE/dlnf = -2n/(2-n),   dlnE/dlnV = 2/(2-n)
# n=1 linear ramp; n=2 harmonic (isochronous); n->inf flat well, hard walls
# =====================================================================
section("C. Power-law well: T(E), dE/df and DC-trim authority")
from math import gamma, sqrt, pi, inf
def I_n(n):
    if n == inf:
        return 1.0
    return sqrt(pi) * gamma(1 + 1/n) / gamma(0.5 + 1/n)
for n in [1, 1.5, 2, 3, 4, inf]:
    if n == 2:
        print(f"  n=2 (harmonic): T independent of E -> f cannot select E; dlnE/dlnV undefined")
        continue
    expT = (0 if n == inf else 1/n) - 0.5
    dlnE_dlnf = 2.0 if n == inf else -2*n/(2-n)
    dlnE_dlnV = 0.0 if n == inf else 2/(2-n)
    print(f"  n={n}: T ∝ E^{expT:+.3f}, I_n={I_n(n):.4f}, dlnE/dlnf={dlnE_dlnf:+.2f}, dlnE/dlnV={dlnE_dlnV:+.2f}")

# Numerical check of the T(E) exponent by direct quadrature (n=1, n=inf, n=4)
import numpy as np
def T_numeric(E, n, m=m_p, qV=1.8*MeV, d=0.5):
    zmax = d * (E/qV)**(1/n)
    s = np.linspace(0, 1, 200001)[:-1]
    integrand = 1/np.sqrt(1 - s**n)
    I = np.trapezoid(integrand, s) if hasattr(np, 'trapezoid') else np.trapz(integrand, s)
    return 4 * zmax * sqrt(m/(2*E)) * I
for n in [1, 4]:
    E1, E2 = 1.0*MeV, 1.1*MeV
    slope = math.log(T_numeric(E2, n)/T_numeric(E1, n)) / math.log(1.1)
    print(f"  quadrature check n={n}: dlnT/dlnE = {slope:+.3f} (theory {1/n-0.5:+.3f})")

# Equal-momentum sensitivity dE_rel/dE_p = dE_rel/dE_Li = 1
def Erel(Ep, ELi):
    vp = math.sqrt(2*Ep*MeV/m_p); vL = math.sqrt(2*ELi*MeV/m_Li)
    return 0.5*mu_red*(vp+vL)**2/MeV
Ep0, EL0 = Ep_eq_s, ELi_eq_s   # sub-threshold equal-momentum point (1.55 MeV)
h = 1e-6
print(f"\n  At equal-momentum E_rel={E_sub} MeV: dErel/dEp = {(Erel(Ep0+h,EL0)-Erel(Ep0-h,EL0))/(2*h):.4f}, "
      f"dErel/dELi = {(Erel(Ep0,EL0+h)-Erel(Ep0,EL0-h))/(2*h):.4f}")

# Example loop: lower E_rel by 50 keV using proton energy only
dE = -0.050
frac = dE / Ep0
print(f"  Lower E_rel by 50 keV via proton: dlnE_p = {frac*100:.2f}%")
print(f"    linear-ramp proton well (n=1): dlnf = dlnE/(-2) = {frac/-2*100:+.2f}%  (raise f)")
print(f"    flat hard-wall well (n->inf):  dlnf = dlnE/(+2) = {frac/2*100:+.2f}%  (lower f)")

# Neutron-channel sensitivity (Lee & Zhou 1999: sigma(p,n) ~270 mb within 50 keV lab of threshold)
dlab = 0.050
dcm = dlab * M_Li7_u/(M_H1_u+M_Li7_u)
print(f"\n  (p,n) rises to ~270 mb within 50 keV lab = {dcm*1e3:.1f} keV CM of threshold;")
print(f"    ratio to sigma(p,alpha)~30 mb: ~{270/30:.0f}x")

# =====================================================================
# D. 6Li: abundance, q/m, p+6Li Q-value, enrichment effect
# =====================================================================
section("D. 6Li content and enrichment")
M_Li6_u = 6.0151228874; M_He3_u = 3.01602932265
Q_p6 = (M_H1_u + M_Li6_u - M_He3_u - M_He4_u) * amu_MeV
print(f"  Q(p + 6Li -> 3He + 4He) = {Q_p6:.3f} MeV")
print(f"  q/m (norm): 6Li3+ {q_over_m_norm(3, ion_mass_u(M_Li6_u,3)):.4f}, "
      f"4He2+ {q_over_m_norm(2, m_a_u):.4f}, D+ {q_over_m_norm(1, ion_mass_u(2.01410177811,1)):.4f}, "
      f"3He2+ {q_over_m_norm(2, ion_mass_u(M_He3_u,2)):.4f}")
for x6 in [0.0759, 0.001, 0.0001]:
    print(f"  6Li fraction {x6*100:.2f}%: 6Li per 7Li fed = {x6/(1-x6)*100:.3f}%  "
          f"(reduction vs natural: {(0.0759/0.9241)/(x6/(1-x6)):.0f}x)")
