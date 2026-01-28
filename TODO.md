# TODO list
### General
* GUIDE NOTEBOOKS
* Add draw_map class for drawing geometries

### Ruben
* Make it easier to add entries to guidelines, currently lot of repetition for different plot types. Can this be abstracted?
* Add keyword inheritance to guidelines
* Consider dataset name and unit in kwargs hierarchy: User kwargs > dataset kwargs > project kwargs > default kwargs
* rename keyword arguments from 'data_style', 'map_style', etc to just 'style' for simplicity

### Zeta
* Interactive plotting: Zoom, limits, tooltips, etc.
* Curved quiver
* plot .grid file
* Add notebook guidelines to better understand arguments
* Automatic conversion of extent type based on provided crs (!)

### Helena
* Highlighting banks and other bedform features
* See email.

### Nice to have
* Annotations/descriptions
* PyPi installation

### Naming
* Reference: import matplotlib.pyplot as plt
* Equivalent: import resplotlib.guideplot as gplt.
* gplt.read_guidelines()
* gplt.imshow()
