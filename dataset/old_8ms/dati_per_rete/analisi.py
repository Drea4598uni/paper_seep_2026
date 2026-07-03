import os
import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import scienceplots
plt.style.use(['science', 'ieee'])
plt.rcParams['xtick.top'] = False
plt.rcParams['ytick.right'] = False

mesh = pv.read("dati_per_rete/rans_mesh_with_les_data.vtp")
k_sgs_les = mesh['k_sgs_les']
k_res_les = mesh['k_res_les']
k_rans = mesh['k']
k_les = mesh['k_les']

### plot tke

fig, ax = plt.subplots(1, 3, figsize=(10, 3))

sns.kdeplot(k_sgs_les, ax=ax[0], color='black', linewidth=2, label='SGS LES', linestyle='--')
sns.kdeplot(k_rans, ax=ax[0], color='blue', linewidth=2, label='RANS')
ax[0].set_xlabel(r'k [m$^2$/s$^2$]', fontsize=12)
ax[0].set_ylabel(r'PDF', fontsize=12)
ax[0].legend()
ax[0].set_xlim(0, 1.6)
# ax[0].spines['top'].set_visible(False)
# ax[0].spines['right'].set_visible(False)
ax[0].tick_params(top=False, right=False)

sns.kdeplot(k_res_les, ax=ax[1], color='black', linewidth=2, label='Resolved LES', linestyle='--')
sns.kdeplot(k_rans, ax=ax[1], color='green', linewidth=2, label='RANS')
ax[1].set_xlabel(r'k [m$^2$/s$^2$]', fontsize=12)
ax[1].set_ylabel(r'')
ax[1].legend()
ax[1].set_xlim(0, 1.6)
# ax[1].spines['top'].set_visible(False)
# ax[1].spines['right'].set_visible(False)
ax[1].tick_params(top=False, right=False)

sns.kdeplot(k_les, ax=ax[2], color='black', linewidth=2, label='Total LES', linestyle='--')
sns.kdeplot(k_rans, ax=ax[2], color='red', linewidth=2, label='RANS')
ax[2].set_xlabel(r'k [m$^2$/s$^2$]', fontsize=12)
ax[2].set_ylabel(r'')
ax[2].legend()
ax[2].set_xlim(0, 1.6)
# ax[2].spines['top'].set_visible(False)
# ax[2].spines['right'].set_visible(False)
ax[2].tick_params(top=False, right=False)

plt.tight_layout()
plt.savefig("dati_per_rete/tke_comparison_pdf.png", dpi=300)
plt.close()

### plot nut

nut_sgs_les = mesh['nutEq']
nut_rans = mesh['nut']
fig, ax = plt.subplots(1, 1, figsize=(4, 3))
sns.kdeplot(nut_sgs_les, ax=ax, color='black', linewidth=2, label='SGS LES', linestyle='--')
sns.kdeplot(nut_rans, ax=ax, color='blue', linewidth=2, label='RANS')
ax.set_xlabel(r'$\nu_t$ [m$^2$/s]', fontsize=12)
ax.set_ylabel(r'PDF', fontsize=12)
ax.legend()
plt.tight_layout()
plt.savefig("dati_per_rete/nut_comparison_pdf.png", dpi=300)
plt.close()

### plot tke and nut values on a line
d = 126
Xs = [0.5, 1, 1.5, 2, 3, 4, 5, 6, 7, 8, 9, 10]
Y = 0
Z0 = 0
Z1 = 1080

# Create directories
os.makedirs("dati_per_rete/tke_sgs_over_line_plot", exist_ok=True)
os.makedirs("dati_per_rete/tke_res_over_line_plot", exist_ok=True)
os.makedirs("dati_per_rete/tke_les_over_line_plot", exist_ok=True)
os.makedirs("dati_per_rete/nut_over_line_plot", exist_ok=True)

### k sgs plots
for X in Xs:
    sampled = mesh.sample_over_line(pointa=(X*d, Y, Z0), pointb=(X*d, Y, Z1), resolution=500)
    k_sgs_les_line = sampled['k_sgs_les']
    k_rans_line = sampled['k']
    
    plt.figure(figsize=(4, 3))
    plt.plot(k_sgs_les_line, sampled.points[:, 2]/d, label='SGS LES', color='black', linestyle='--', linewidth=2)
    plt.plot(k_rans_line, sampled.points[:, 2]/d, label='RANS', color='blue', linewidth=2)
    plt.xlabel(r'k [m$^2$/s$^2$]', fontsize=12)
    plt.ylabel(r'z/D', fontsize=12)
    plt.ylim(0, 8)
    plt.legend()
    plt.tick_params(top=False, right=False)
    plt.tight_layout()
    plt.savefig(f"dati_per_rete/tke_sgs_over_line_plot/tke_sgs_line_X_{X:.1f}_D.png", dpi=300)
    plt.close()

# Create k sgs gif
images = []
for X in Xs:
    img_path = f"dati_per_rete/tke_sgs_over_line_plot/tke_sgs_line_X_{X:.1f}_D.png"
    images.append(Image.open(img_path))
gif_path = "dati_per_rete/tke_sgs_over_line_plot/tke_sgs_over_line_plot.gif"
images[0].save(gif_path, save_all=True, append_images=images[1:], duration=300, loop=0)

### k res plots
for X in Xs:
    sampled = mesh.sample_over_line(pointa=(X*d, Y, Z0), pointb=(X*d, Y, Z1), resolution=500)
    k_res_les_line = sampled['k_res_les']
    k_rans_line = sampled['k']

    plt.figure(figsize=(4, 3))
    plt.plot(k_res_les_line, sampled.points[:, 2]/d, label='Resolved LES', color='black', linestyle='--', linewidth=2)
    plt.plot(k_rans_line, sampled.points[:, 2]/d, label='RANS', color='green', linewidth=2)
    plt.xlabel(r'k [m$^2$/s$^2$]', fontsize=12)
    plt.ylabel(r'z/D', fontsize=12)
    plt.ylim(0, 8)
    plt.legend()
    plt.tick_params(top=False, right=False)
    plt.tight_layout()
    plt.savefig(f"dati_per_rete/tke_res_over_line_plot/tke_res_line_X_{X:.1f}_D.png", dpi=300)
    plt.close()

# Create k res gif
images = []
for X in Xs:
    img_path = f"dati_per_rete/tke_res_over_line_plot/tke_res_line_X_{X:.1f}_D.png"
    images.append(Image.open(img_path))
gif_path = "dati_per_rete/tke_res_over_line_plot/tke_res_over_line_plot.gif"
images[0].save(gif_path, save_all=True, append_images=images[1:], duration=300, loop=0)

### k les plots
for X in Xs:
    sampled = mesh.sample_over_line(pointa=(X*d, Y, Z0), pointb=(X*d, Y, Z1), resolution=500)
    k_les_line = sampled['k_les']
    k_rans_line = sampled['k']
    
    plt.figure(figsize=(4, 3))
    plt.plot(k_les_line, sampled.points[:, 2]/d, label='Total LES', color='black', linestyle='--', linewidth=2)
    plt.plot(k_rans_line, sampled.points[:, 2]/d, label='RANS', color='red', linewidth=2)
    plt.xlabel(r'k [m$^2$/s$^2$]', fontsize=12)
    plt.ylabel(r'z/D', fontsize=12)
    plt.ylim(0, 8)
    plt.legend()
    plt.tick_params(top=False, right=False)
    plt.tight_layout()
    plt.savefig(f"dati_per_rete/tke_les_over_line_plot/tke_les_line_X_{X:.1f}_D.png", dpi=300)
    plt.close()

# Create k les gif
images = []
for X in Xs:
    img_path = f"dati_per_rete/tke_les_over_line_plot/tke_les_line_X_{X:.1f}_D.png"
    images.append(Image.open(img_path))
gif_path = "dati_per_rete/tke_les_over_line_plot/tke_les_over_line_plot.gif"
images[0].save(gif_path, save_all=True, append_images=images[1:], duration=300, loop=0)

### nut plots
for X in Xs:
    sampled = mesh.sample_over_line(pointa=(X*d, Y, Z0), pointb=(X*d, Y, Z1), resolution=500)
    nut_sgs_les_line = sampled['nutEq']
    nut_rans_line = sampled['nut']
    
    plt.figure(figsize=(4, 3))
    plt.plot(nut_sgs_les_line, sampled.points[:, 2]/d, label='SGS LES', color='black', linestyle='--', linewidth=2)
    plt.plot(nut_rans_line, sampled.points[:, 2]/d, label='RANS', color='blue', linewidth=2)
    plt.xlabel(r'$\nu_t$ [m$^2$/s]', fontsize=12)
    plt.ylabel(r'z/D', fontsize=12)
    plt.ylim(0, 8)
    plt.legend()
    plt.tick_params(top=False, right=False)
    plt.tight_layout()
    plt.savefig(f"dati_per_rete/nut_over_line_plot/nut_line_X_{X:.1f}_D.png", dpi=300)
    plt.close()

# Create nut gif
images = []
for X in Xs:
    img_path = f"dati_per_rete/nut_over_line_plot/nut_line_X_{X:.1f}_D.png"
    images.append(Image.open(img_path))
gif_path = "dati_per_rete/nut_over_line_plot/nut_over_line_plot.gif"
images[0].save(gif_path, save_all=True, append_images=images[1:], duration=300, loop=0)
