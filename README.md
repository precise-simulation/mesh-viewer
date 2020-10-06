Mesh Viewer
-----------

**Mesh Viewer** is a simple STL/OBJ CAD geometry and surface mesh
viewer prototype with a _Model View Controller_ (MVC) type
design. Three different visualization backends are compared and
embedded within the same
[Python](https://www.python.org)/[tkinter](https://wiki.python.org/moin/TkInter)
GUI framework.

- [matplotlib](https://matplotlib.org)
- [plotly](https://www.featool.com/web-plots) _(WebGL with embedded webview)_
- [vispy](http://vispy.org) _(OpenGL)_

![Mesh Viewer screenshot](https://raw.githubusercontent.com/precise-simulation/mesh-viewer/master/meshviewer-screenshot.jpg)

The _vispy/opengl_ backend seems to be the best choice overall with
respect to performance and packaged size (~35 MB), while _plotly_
(subjectively) looks the best but leads to large binaries due to
embedding the Chromium framework (~70-90 MB), _matplotlib_ is the
simplest backend but suffers from slow performance for larger
visualizations.


# Python Script Use

Simply downloading and running the corresponding Python scripts should
start both the GUI and mesh viewer application. The examples below
show how to set up a new
[conda](https://docs.conda.io/en/latest/miniconda.html) Python
environment with the required dependencies.

## mesh-viewer with matplotlib backend

    conda create -n mpl python=3.7
    conda activate mpl
    conda install conda-forge::blas=*=openblas numpy
    pip install matplotlib==3.2.2

    python meshviewer_mpl_tk.py

## mesh-viewer with plotly/cefpython backend

    conda create -n plotly python=3.7
    conda activate plotly
    conda install conda-forge::blas=*=openblas numpy
    pip install cefpython3

    python meshviewer_plotly_cef_tk.py

## mesh-viewer with vispy/pyopengltk backend

    conda create -n vispy python=3.7
    conda activate vispy
    conda install conda-forge::blas=*=openblas numpy
    pip install cython
    pip install pyopengltk
    git clone --recurse-submodules https://github.com/Wosser1sProductions/vispy.git
    cd vispy
    git submodule update --init --recursive
    pip install . --no-use-pep517
    cd ..

    python meshviewer_vispy_tk.py


# Pre-Built Binaries

The
[releases](https://github.com/precise-simulation/mesh-viewer/releases/latest)
include stand-alone and pre-compiled executable _one-click_ binaries
_(exe)_ for Windows systems (note that it may take several seconds to
load/start due to extracting all resources, and that the _plotly_
backed required an internet connection and accepting a
Microsoft/Windows certificate to download the [plotly
javascript](https://github.com/plotly/plotly.js) library). Building
stand-alone executables can be done with
[pyinstaller](https://www.pyinstaller.org) as described below.

## build mesh-viewer with matplotlib backend

    conda create -n mpl python=3.7
    conda activate mpl
    conda install conda-forge::blas=*=openblas numpy
    pip install matplotlib==3.2.2
    pip install pyinstaller

    pyinstaller --onefile --windowed --noupx meshviewer_mpl_tk.py

    conda env remove -n mpl

## build mesh-viewer with plotly/cefpython backend

    conda create -n plotly python=3.7
    conda activate plotly
    conda install conda-forge::blas=*=openblas numpy
    pip install cefpython3
    pip install pyinstaller==3.6

    cd build
    python build.py --onefile

    conda env remove -n plotly

## build mesh-viewer with vispy/pyopengltk backend

    conda create -n vispy python=3.7
    conda activate vispy
    conda install conda-forge::blas=*=openblas numpy
    pip install cython
    pip install pyopengltk
    git clone --recurse-submodules https://github.com/Wosser1sProductions/vispy.git
    cd vispy
    git submodule update --init --recursive
    pip install . --no-use-pep517
    pip install pyinstaller

    cd ../build
    pyinstaller --onefile meshviewer_vispy_tk.spec

    conda env remove -n vispy


# Note

This is just a simple prototype/proof-of-concept and not intended to
be a full fledged application. If you are interested in custom CAE and
simulation tools such as this app and
[FEATool Multiphysics](https://www.featool.com) please feel free to
get in touch with [Precise Simulation](https://www.precisesimulation.com).


# License

AGPL v3, see LICENSE for more details.

Copyright (C) 2020 Precise Simulation Ltd.
