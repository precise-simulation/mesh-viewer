"""STL/OBJ Python Mesh Viewer prototype with Matplotlib/Tkinter
using a Model View Controller (MVC) design.

:license: AGPL v3, see LICENSE for more details.
:copyright: 2020 Precise Simulation Ltd.

"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
from tkinter.filedialog import askopenfilename

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from mpl_toolkits import mplot3d


class Model():

    def __init__(self, data=None):

        # Define unit cube.
        if data is None:
            vertices = [[0,0,0], [1,0,0], [1,1,0], [0,1,0],
                        [0,0,1], [1,0,1], [1,1,1], [0,1,1]]
            faces = [[1,2,3,4], [1,2,6,5], [2,3,7,6], [3,4,8,7], [4,1,5,8], [5,6,7,8]]
            data = Mesh(vertices, faces)

        self.data = [data]

    def clear(self):
        self.data = []

    def load_file(self, file_name):
        '''Load mesh from file
        '''
        if file_name.endswith(('.stl','.stla')):
            mesh = self.load_stl(file_name)

        elif file_name.lower().endswith('.obj'):
            mesh = self.load_obj(file_name)

        self.data.append(mesh)

    def load_stl(self, file_name):
        '''Load ASCII STL CAD file
        '''
        with open(file_name, 'r') as f:
            data = f.read()

        vertices = []
        faces = []
        v = []
        for line in data.splitlines():
            line_data = line.split()

            if line_data[0]=='facet':
                v = []

            elif line_data[0]=='vertex':
                v.append([float(line_data[1]), float(line_data[2]), float(line_data[3])])

            elif line_data[0]=='endloop':
                if len(v)==3:
                    vertices.extend(v)
                    ind = 3*len(faces)+1
                    faces.append([ind, ind+1, ind+2])

        return Mesh(vertices, faces)


    def load_obj(self, file_name):
        '''Load ASCII Wavefront OBJ CAD file
        '''
        with open(file_name, 'r') as f:
            data = f.read()

        vertices = []
        faces = []
        for line in data.splitlines():
            line_data = line.split()
            if line_data:
                if line_data[0] == 'v':
                    v = [float(line_data[1]), float(line_data[2]), float(line_data[3])]
                    vertices.append(v)
                elif line_data[0] == 'f':
                    face = []
                    for i in range(1, len(line_data)):
                        s = line_data[i].replace('//','/').split('/')
                        face.append(int(s[0]))

                    faces.append(face)

        return Mesh(vertices, faces)

    def get_bounding_box(self):
        bbox = []
        for i in range(len(self.data[0].vertices[0])):
            x_i = [mesh.bounding_box[i] for mesh in self.data]
            bbox.append([min(x_i), max(x_i)])

        return bbox


class Mesh():

    def __init__(self, vertices, faces):
        self.vertices = vertices
        self.faces = faces
        self.bounding_box = self.get_bounding_box()

    def get_vertices(self):
        vertices = []
        for face in self.faces:
            vertices.append([self.vertices[ivt-1] for ivt in face])

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

        figure = Figure()
        axes = mplot3d.Axes3D(figure)

        self.figure = figure
        self.axes = axes
        self.canvas = None
        self.toolbar = None

        self.plot()

    def clear(self):
        self.axes.clear()
        self.update()

    def update(self):
        if self.canvas is not None:
            self.canvas.draw()

    def plot(self, types="solid + wireframe"):
        self.clear()
        if isinstance(types, (str,)):
            types = [s.strip() for s in types.split('+')]

        for mesh in self.model.data:
            for type in types:

                if type=="solid":
                    self.axes.add_collection3d(mplot3d.art3d.Poly3DCollection(mesh.get_vertices()))

                elif type=="wireframe":
                    self.axes.add_collection3d(mplot3d.art3d.Line3DCollection(mesh.get_line_segments(),
                                                                              colors=(0.1, 0.1, 0.35, 1)))

                else:
                    # Unknown plot type
                    return None

        self.axes.auto_scale_xyz(*self.model.get_bounding_box())
        self.update()

    def xy(self):
        self.axes.view_init(elev=90, azim=-90)
        self.update()

    def xz(self):
        self.axes.view_init(elev=0, azim=-90)
        self.update()

    def yz(self):
        self.axes.view_init(elev=0, azim=0)
        self.update()

    def reset(self):
        self.axes.view_init()
        self.update()


class Controller():

    def __init__(self, view=None):

        root = tk.Tk()
        root.title("Mesh Viewer")

        if view is None:
            view = View()

        f1 = ttk.Frame(root)
        f1.pack(side=tk.TOP, anchor=tk.W)

        toolbar = [ tk.Button(f1, text="Open", command=self.open),
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

        [obj.pack(side=tk.LEFT, anchor=tk.W) for obj in toolbar]

        canvas = FigureCanvasTkAgg(view.figure, root)
        canvas.mpl_connect('button_press_event', view.axes._button_press)
        canvas.mpl_connect('button_release_event', view.axes._button_release)
        canvas.mpl_connect('motion_notify_event', view.axes._on_move)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        mpl_toolbar = NavigationToolbar2Tk(canvas, root)
        mpl_toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        menubar = tk.Menu( root )
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open...", command=self.open)
        file_menu.add_command(label="Exit", command=self.exit)
        menubar.add_cascade(label="File", menu=file_menu)
        root.config(menu=menubar)

        self.root = root
        view.canvas = canvas
        view.toolbar = mpl_toolbar
        self.view = view
        self.model = view.model

    def render(self):
        self.root.mainloop()

    def open(self):
        file_name = askopenfilename( title = "Select file to open",
                                     filetypes = (("CAD files","*.obj;*.stl"),
                                                  ("all files","*.*")) )
        self.model.clear()
        self.model.load_file(file_name)
        self.view.plot()

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
        if model is None:
            model = Model()

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
