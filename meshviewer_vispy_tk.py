"""STL/OBJ Python Mesh Viewer prototype with Vispy/OpenGL/Tkinter
using a Model View Controller (MVC) design.

This is just a simple prototype/proof-of-concept and not intended to
be a full fledged application. If you are interested in custom CAE and
simulation tools such as this app and
[FEATool Multiphysics](https://www.featool.com) please feel free to
get in touch with [Precise Simulation](https://www.precisesimulation.com).

:license: AGPL v3, see LICENSE for more details or contact
          Precise Simulation for alternative licensing options.
:copyright: 2020 Precise Simulation Ltd.

"""

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
from tkinter.filedialog import askopenfilename

import vispy
import vispy.scene
# import vispy.visuals
vispy.use(app='tkinter')

import numpy as np

import sys
import os
if os.name == 'nt':
    from ctypes import windll, pointer, wintypes
    try:
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass  # this will fail on Windows Server and maybe early Windows


class Model():

    def __init__(self, file_name=None):

        self.data = []
        if file_name is None:
            # Define unit cube.
            vertices = [[0,1,0], [1,1,0], [1,0,0], [0,0,0],
                        [1,0,1], [0,0,1], [1,1,1], [0,1,1]]
            faces = [[0,1,2], [0,2,3], [2,4,5], [2,5,3], [4,2,1], [4,1,6],
                     [6,1,0], [6,0,7], [3,5,7], [3,7,0], [6,5,4], [6,7,5]]
            data = Mesh(np.asarray(vertices, dtype='float32'), np.asarray(faces,dtype='uint32'))

            self.data = [data]
        else:
            self.load_file(file_name)

    def clear(self):
        self.data = []

    def load_file(self, file_name):
        '''Load mesh from file
        '''
        vertices, faces, _, _ = vispy.io.read_mesh(file_name)
        self.data.append(Mesh(vertices, faces))

    def get_bounding_box(self):
        bbox = self.data[0].bounding_box
        for mesh in self.data[1:]:
            for i in range(len(bbox)):
                x_i = mesh.bounding_box[i]
                bbox[i][0] = min([bbox[i][0], min(x_i)])
                bbox[i][1] = max([bbox[i][1], max(x_i)])

        return bbox


class Mesh():

    def __init__(self, vertices, faces):
        self.vertices = vertices
        self.faces = faces
        self.bounding_box = self.get_bounding_box()

    def get_vertices(self):
        vertices = []
        for face in self.faces:
            vertices.append([self.vertices[ivt] for ivt in face])

        return vertices

    def get_line_segments(self):
        line_segments = set()
        for face in self.faces:
            for i in range(len(face)):
                iv = face[i]
                jv = face[(i+1)%len(face)]
                if jv > iv:
                    edge = (iv, jv)
                else:
                    edge = (jv, iv)

                line_segments.add(edge)

        return [[self.vertices[edge[0]-1], self.vertices[edge[1]-1]] for edge in line_segments]

    def get_bounding_box(self):
        v = [vti for face in self.get_vertices() for vti in face]
        bbox = []
        for i in range(len(self.vertices[0])):
            x_i = [p[i] for p in v]
            bbox.append([min(x_i), max(x_i)])

        return bbox


class View():

    def __init__(self, model=None):

        if model is None:
            model = Model()
        self.model = model
        self.canvas = None
        self.vpview = None

    def clear(self):
        if self.vpview is not None:
            self.vpview.parent = None

        self.vpview = self.canvas.central_widget.add_view(bgcolor='white')
        # vispy.scene.visuals.XYZAxis(parent=self.vpview.scene)

    def plot(self, types="solid + wireframe"):
        self.clear()
        if isinstance(types, (str,)):
            types = [s.strip() for s in types.split('+')]

        for mesh in self.model.data:
            for type in types:

                if type=="solid":
                    msh = vispy.scene.visuals.Mesh(vertices=mesh.vertices, \
                                                   shading='smooth', faces=mesh.faces)
                    self.vpview.add(msh)

                elif type=="wireframe":
                    n_faces = len(mesh.faces)
                    ix = np.tile([0, 1, 1, 2, 2, 0], n_faces) + \
                        np.repeat(np.arange(0, 3*n_faces, 3), 6)
                    edges = mesh.faces.reshape(-1)[ix]
                    edg = vispy.scene.visuals.Line(pos=mesh.vertices[edges], connect="segments")
                    self.vpview.add(edg)

                else:
                    # Unknown plot type
                    return None

        self.vpview.camera = vispy.scene.TurntableCamera(parent=self.vpview.scene)

    def xy(self):
        self.vpview.camera.elevation = 90
        self.vpview.camera.azimuth = -90
        self.vpview.camera.roll = 0

    def xz(self):
        self.vpview.camera.elevation = 0
        self.vpview.camera.azimuth = -90
        self.vpview.camera.roll = 0

    def yz(self):
        self.vpview.camera.elevation = 0
        self.vpview.camera.azimuth = 0
        self.vpview.camera.roll = 0

    def reset(self):
        self.vpview.camera.reset()

class Controller():

    def __init__(self, view=None):

        root = tk.Tk()
        root.geometry("600x550")
        root.title("Mesh Viewer")

        if view is None:
            view = View()

        f1 = ttk.Frame(root)
        f1.pack(side=tk.TOP, anchor=tk.W)

        toolbar = [ tk.Button(f1, text="Open"),
                    tk.Button(f1, text="XY", command=view.xy),
                    tk.Button(f1, text="XZ", command=view.xz),
                    tk.Button(f1, text="YZ", command=view.yz),
                    tk.Button(f1, text="Reset", command=view.reset) ]

        f2 = tk.Frame(f1, highlightthickness=1, highlightbackground="gray")
        options = ["solid","wireframe","solid + wireframe"]
        var = tk.StringVar()
        o1 = ttk.OptionMenu(f2, var, options[len(options)-1], *options, command=lambda val: self.view.plot(val))
        o1["menu"].configure(bg="white")
        setMaxWidth(options, o1)
        o1.pack()
        toolbar.append(f2)

        toolbar[0].config(command=lambda: self.open(var))

        [obj.pack(side=tk.LEFT, anchor=tk.W) for obj in toolbar]

        canvas = vispy.scene.SceneCanvas(
            keys='interactive', show=True, parent=root)
        canvas.native.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        view.canvas = canvas
        root.update_idletasks()

        menubar = tk.Menu( root )
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open...", command=lambda: self.open(var))
        file_menu.add_command(label="Exit", command=self.exit)
        menubar.add_cascade(label="File", menu=file_menu)
        root.config(menu=menubar)

        self.root = root
        self.view = view
        self.model = view.model
        view.plot()

    def render(self):
        self.root.mainloop()

    def open(self, var):
        file_name = askopenfilename( title = "Select file to open",
                                     filetypes = (("CAD files","*.obj;*.stl"),
                                                  ("all files","*.*")) )
        self.model.clear()
        self.model.load_file(file_name)
        self.view.plot(var.get())

    def exit(self):
        self.model.clear()
        self.view.clear()
        self.root.destroy()


def setMaxWidth(stringList, element):
    try:
        f = tkfont.nametofont(element.cget("font"))
        zerowidth = f.measure("0")
    except:
        f = tkfont.nametofont(ttk.Style().lookup("TButton", "font"))
        zerowidth = f.measure("0") - 0.8

    w = max([f.measure(i) for i in stringList])/zerowidth
    element.config(width=int(w))


class App():

    def __init__(self, model=None, view=None, controller=None):
        file_name = None
        if len(sys.argv) >= 2:
            file_name = sys.argv[1]

        if model is None:
            model = Model(file_name)

        if view is None:
            view = View(model)

        if controller is None:
            controller = Controller(view)

        self.model = model
        self.view = view
        self.controller = controller

    def start(self):
        self.controller.render()


if __name__ == "__main__":

    app = App()
    app.start()
