import glob
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os

# Get colormaps
def _get_colormaps():
    """Get colormaps.

    :return: Colormaps.
    :rtype:  list[matplotlib.colors.LinearSegmentedColormap]

    See also: `matplotlib.colors.LinearSegmentedColormap <https://matplotlib.org/stable/api/_as_gen/matplotlib.colors.LinearSegmentedColormap.html>`_.
    """
    
    # Function to scale colors
    def scale_colors(colors, rgba_scales=(1, 1, 1, 1)):
        if isinstance(rgba_scales, (int, float)):
            rgba_scales = (rgba_scales, rgba_scales, rgba_scales, rgba_scales)
        colors_new = []
        for r, g, b, a in colors:
            colors_new.append((r*rgba_scales[0], g*rgba_scales[1], b*rgba_scales[2], a*rgba_scales[3]))
        return colors_new
    
    # Function to get colors from a colormap
    def get_colors_from_cmap(cmap_name):
        cmap = plt.get_cmap(cmap_name)
        colors = [cmap(i) for i in range(cmap.N)]
        return colors
    
    # Function to get colors from a file
    def get_colors_from_file(file_path):
        colors = []
        with open(file_path, 'r') as file:
            for line in file:
                colors.append(tuple(float(color) for color in line.split()))
        colors = scale_colors(colors, rgba_scales=1/255)
        return colors

    # Function to get a colormap from colors
    def get_cmap_from_colors(colors, cmap_name):
        cmap = plt.cm.colors.LinearSegmentedColormap.from_list(cmap_name, colors)
        return cmap
    
    # Initialise colormaps
    cmaps = []
    cmaps_contours = []
    
    # Add colormaps from matplotlib colormaps
    cmaps.append(get_cmap_from_colors(get_colors_from_cmap('Spectral_r'), 'bathymetry'))
    cmaps_contours.append(get_cmap_from_colors(scale_colors(get_colors_from_cmap('Spectral_r'), rgba_scales=(0.75, 0.75, 0.75, 1)), 'bathymetry_contour'))
    cmaps.append(get_cmap_from_colors(get_colors_from_cmap('RdBu_r'), 'bedforms'))
    cmaps_contours.append(get_cmap_from_colors(scale_colors(get_colors_from_cmap('RdBu_r'), rgba_scales=(0.75, 0.75, 0.75, 1)), 'bedforms_contour'))
    cmaps.append(get_cmap_from_colors(get_colors_from_cmap('RdBu_r'), 'morphology'))
    cmaps_contours.append(get_cmap_from_colors(scale_colors(get_colors_from_cmap('RdBu_r'), rgba_scales=(0.75, 0.75, 0.75, 1)), 'morphology_contour'))
    cmaps.append(get_cmap_from_colors(get_colors_from_cmap('RdBu_r'), 'diverging'))
    cmaps_contours.append(get_cmap_from_colors(scale_colors(get_colors_from_cmap('RdBu_r'), rgba_scales=(0.75, 0.75, 0.75, 1)), 'diverging_contour'))
    
    # Add colormaps from text files
    file_path_cmaps = glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cmaps', '*.txt'))
    for file_path in file_path_cmaps:
        cmap_name = os.path.basename(file_path).split('.')[0]
        colors = get_colors_from_file(file_path)
        cmaps.append(get_cmap_from_colors(colors, cmap_name))
        cmaps_contours.append(get_cmap_from_colors(scale_colors(colors, rgba_scales=(0.75, 0.75, 0.75, 1)), cmap_name+'_contour'))

    # Combine colormaps
    cmaps = cmaps + cmaps_contours
    
    # Return colormaps
    return cmaps

# Register colormaps
def register_colormaps():
    """Register colormaps.

    returns: None.
    rtype:   None

    See also: `Creating Colormaps in Matplotlib <https://matplotlib.org/stable/users/explain/colors/colormap-manipulation.html>`_.
    """

    # Get colormaps
    cmaps = _get_colormaps()

    # Register colormaps
    for cmap in cmaps:
        if not cmap.name in plt.colormaps():
            mpl.colormaps.register(cmap=cmap)
            mpl.colormaps.register(cmap=cmap.reversed())

# Plot colormaps
def plot_colormaps():
    """Plot colormaps.

    returns: None.
    rtype:   None

    See also: `Plotting Colormaps in Matplotlib <https://matplotlib.org/stable/users/explain/colors/colormaps.html>`_.
    """

    # Get colormaps
    cmaps = _get_colormaps()

    # Create figure and axes
    nrows = len(cmaps)
    figh = 0.35 + 0.15 + (nrows + (nrows - 1) * 0.1) * 0.22
    fig, axs = plt.subplots(nrows=nrows + 3, figsize=(6.4, figh))
    fig.subplots_adjust(top=1 - 0.35 / figh, bottom=0.15 / figh,
                        left=0.2, right=0.99)
    axs_ = [ax for idx, ax in enumerate(axs) if idx not in [int(nrows/2), int(nrows/2)+1]]
    
    # Create gradient
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    # Plot colormaps
    for ax, cmap in zip(axs_, cmaps):
        ax.imshow(gradient, aspect='auto', cmap=cmap)
        ax.text(-0.01, 0.5,cmap.name, va='center', ha='right', fontsize=10,
                transform=ax.transAxes)
        
    # Add titles
    axs_[0].set_title('Colormaps', fontsize=10)
    axs_[int(nrows/2)].set_title('Contour Colormaps', fontsize=10)

    # Turn off all ticks & spines
    for ax in axs:
        ax.set_axis_off()