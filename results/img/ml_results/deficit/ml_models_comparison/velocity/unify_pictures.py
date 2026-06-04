import matplotlib.pyplot as plt
import PIL.Image as Image
import glob
import re
from natsort import natsorted
from matplotlib.gridspec import GridSpec
import scienceplots 
plt.style.use(['science', 'ieee'])
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

# Load the images
path = r"D:\File uni\Dottorato\NUT_regression\results\img\ml_results\deficit\ml_models_comparison\velocity"
image_files = glob.glob(path + "/*D.png")

def _extract_x_value(fname: str):
    # try pattern like _x_0.25D or _x_0,25D
    m = re.search(r'_x_([-+]?\d+[.,]?\d*)D', fname)
    if m:
        s = m.group(1).replace(',', '.')
        try:
            return float(s)
        except ValueError:
            pass
    # fallback: last numeric group before 'D'
    m2 = re.search(r'([-+]?\d+[.,]?\d*)D', fname)
    if m2:
        s = m2.group(1).replace(',', '.')
        try:
            return float(s)
        except ValueError:
            pass
    return float('inf')

# sort by numeric x value extracted from filename (ascending)
image_files = sorted(image_files, key=_extract_x_value)
images = [Image.open(f) for f in image_files]

# Create a figure to display the images with different columns per row
# Change these two variables to set different numbers of columns
top_cols = 6
bottom_cols = 6
max_cols = max(top_cols, bottom_cols)
fig = plt.figure(figsize=(15, 3), dpi=300)
gs = GridSpec(2, max_cols, figure=fig, hspace=0.005, wspace=0.02)

axes = []
# top row: create `top_cols` axes
for i in range(top_cols):
    ax = fig.add_subplot(gs[0, i])
    axes.append(ax)
# bottom row: create `bottom_cols` axes and center them if fewer than max
start = (max_cols - bottom_cols) // 2
for i in range(bottom_cols):
    ax = fig.add_subplot(gs[1, start + i])
    axes.append(ax)

# Assign images explicitly to top and bottom rows so bottom row is centered
top_images = images[:top_cols]
bottom_images = images[top_cols:top_cols + bottom_cols]

top_axes = axes[:top_cols]
bottom_axes = axes[top_cols:top_cols + bottom_cols]

for ax, img in zip(top_axes, top_images):
    ax.imshow(img)
    ax.axis('off')

for ax, img in zip(bottom_axes, bottom_images):
    ax.imshow(img)
    ax.axis('off')

plt.subplots_adjust(hspace=0.01, left=0.02, right=0.98, top=0.98, bottom=0.02)
plt.tight_layout()
plt.savefig(r"D:\File uni\Dottorato\NUT_regression\results\img\ml_results\deficit\ml_models_comparison\velocity\comparison.png", bbox_inches='tight')
plt.close()
