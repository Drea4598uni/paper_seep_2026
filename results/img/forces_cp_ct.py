import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scienceplots 
plt.style.use(['science', 'ieee'])
# --- SEEP2026 template: force Times New Roman to match the manuscript body ---
plt.rcParams.update({
    'text.usetex': False,
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'Nimbus Roman No9 L', 'DejaVu Serif'],
    'mathtext.fontset': 'stix',
})
plt.rcParams['figure.dpi'] = 300
plt.rcParams['figure.figsize'] = (6, 4)
plt.rcParams['font.size'] = 18
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['legend.fontsize'] = 14
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['lines.linewidth'] = 1.2
plt.rcParams['lines.markersize'] = 4
plt.rcParams['legend.loc'] = 'best'
plt.rcParams['legend.frameon'] = False
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False
plt.rcParams['xtick.top'] = False
plt.rcParams['ytick.right'] = False

alpha_df = pd.read_csv(r'dataset\risultati_solver\CSV_files\timestep_sweep\8_m_s\timestep_sweep_8_m_s_alpha_distribution.csv')
Cp_df = pd.read_csv(r'dataset\risultati_solver\CSV_files\timestep_sweep\8_m_s\timestep_sweep_8_m_s_Cp_time_series.csv')
Ct_df = pd.read_csv(r'dataset\risultati_solver\CSV_files\timestep_sweep\8_m_s\timestep_sweep_8_m_s_Ct_time_series.csv')
Energy_df = pd.read_csv(r'dataset\risultati_solver\CSV_files\timestep_sweep\8_m_s\timestep_sweep_8_m_s_Energy_spectrum.csv')
force_df = pd.read_csv(r'dataset\risultati_solver\CSV_files\timestep_sweep\8_m_s\timestep_sweep_8_m_s_force_profile.csv')
Uref=8.0

### plot Cp and Ct values against references

reference_cp = pd.read_csv(r'dataset\risultati_solver\Cp_ref.csv')
reference_ct = pd.read_csv(r'dataset\risultati_solver\c_t_new.csv') 
cp_mean = Cp_df['Cp'].mean()
ct_mean = Ct_df['Ct'].mean()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
ax1.scatter(Uref, cp_mean, label= r'$C_p$')
ax2.scatter(7, ct_mean, label=r'$C_t$', marker='s')
ax1.plot(reference_cp['wind'], reference_cp['cp'], linestyle='--')
### create two vertical axis for Cp and Ct
ax1.set_xlabel('Wind Speed (m/s)')
ax2.set_xlabel(r'$\lambda$')
ax2.plot(reference_ct['tsr'], reference_ct['ct'], label='Jonkman et Al. (2009)', linestyle='--')
ax1.set_ylabel(r'$C_p$')
ax2.set_ylabel(r'$C_t$')
ax2.spines['right'].set_visible(True)
ax2.legend()
ax1.legend()
fig.savefig(r'results\img\forces_cp_ct.png', bbox_inches='tight')
plt.close()

### plot force profile

ref_norm_force = pd.read_csv(r'dataset\risultati_solver\trold_norm.csv')
ref_tan_force = pd.read_csv(r'dataset\risultati_solver\trold_tang.csv')
fig, ax = plt.subplots(1,2, figsize=(12, 4))
ax[0].plot(force_df['normal']/(Uref**2)/(63)/1.225*(32/63), force_df['r'], label=r'$F_n$', marker='o')
ax[1].plot(force_df['tangential']/(Uref**2)/(63)/1.225*(32/63), force_df['r'], label=r'$F_t$', marker='s')
ax[0].plot(ref_norm_force['f'], ref_norm_force['r'], linestyle='--')
ax[1].plot( ref_tan_force['f'], ref_tan_force['r'], label=r'Troldborg et al. (2015)', linestyle='--')
ax[0].set_ylabel('x/R')
ax[1].set_ylabel('x/R')
ax[0].set_xlabel(r'$F_n$/$\rho U^2 R^2$')
ax[1].set_xlabel(r'$F_t$/$\rho U^2 R^2$')
ax[0].legend()
ax[1].legend()
fig.savefig(r'results\img\forces_profile.png', bbox_inches='tight')
plt.close()
