Mesh Viewer
-----------

**Mesh Viewer** is a simple STL/OBJ CAD geometry viewer prototype
  using the Tkinter GUI framework with a Model View Controller (MVC)
  design, and either Matplotlib/mplot3d or
  [Plotly](https://www.featool.com/web-plots)/WebGL visualization
  backends.

![Mesh Viewer screenshot](https://raw.githubusercontent.com/precise-simulation/mesh-viewer/master/meshviewer-screenshot.jpg)

# Installation and Use

Simply downloading and running the corresponding Python scripts should
start both the GUI and application

    python meshviewer_mpl_tk.py

or

    python meshviewer_plotly_cef_tk.py

[Releases](https://github.com/precise-simulation/mesh-viewer/releases)
as stand-alone executables are available, and can be built using
_Pyinstaller_ and the [build/build-exe.py](https://github.com/precise-simulation/mesh-viewer/blob/master/build/build-exe.py)
script.

# Dependencies

Python with the following libraries:

- The _Tkinter_ Graphical User Interface (GUI) framework (usually installed with Python)
- [matplotlib](https://matplotlib.org) for the matplotlib version
- [cefpython](https://github.com/cztomczak/cefpython) for the plotly
  version (as well as internet connection to download the
  [plotly.js](https://github.com/plotly/plotly.js) library)

# Note

This is just a simple prototype/proof-of-concept and not intended to
be a full fledged application. If you are interested in custom CAE and
simulation tools such as this app and
[FEATool Multiphysics](https://www.featool.com) please feel free to
get in touch with [Precise Simulation](https://www.precisesimulation.com).

# License

AGPL v3, see LICENSE for more details.

Copyright (C) 2020 Precise Simulation Ltd.
