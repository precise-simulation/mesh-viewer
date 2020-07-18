"""STL/OBJ Python Mesh Viewer prototype with Plotly/CEF Webview/Tkinter
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

from cefpython3 import cefpython as cef
import ctypes
import sys
import os
import platform

g_multi_threaded = True
if not platform.system() == "Windows":
    g_multi_threaded = False


class Model():

    def __init__(self, file_name=None):

        self.data = []
        if file_name is None:
            # Define unit cube.
            vertices = [[0,0,0], [1,0,0], [1,1,0], [0,1,0],
                        [0,0,1], [1,0,1], [1,1,1], [0,1,1]]
            faces = [[1,2,3], [1,3,4], [1,2,6], [1,6,5], [2,3,7], [2,7,6], \
                     [3,4,8], [3,8,7], [4,1,5], [4,5,8], [5,6,7], [5,7,8]]
            data = Mesh(vertices, faces)

            self.data = [data]
        else:
            self.load_file(file_name)

    def clear(self):
        self.data = []

    def load_file(self, file_name):
        '''Load mesh from file
        '''
        if file_name.lower().endswith(('.stl','.stla','.stlb')):
            self.load_stl(file_name)

        elif file_name.lower().endswith('.obj'):
            self.load_obj(file_name)

    def load_stl(self, file_name):
        '''Load STL CAD file
        '''
        try:
            with open(file_name, 'r') as f:
                data = f.read()

            self.load_stl_ascii(data)

        except:
            self.load_stl_binary(file_name)

    def load_stl_ascii(self, data):
        '''Load ASCII STL CAD file
        '''
        vertices = []
        faces = []
        v = []
        for i, line in enumerate(data.splitlines()):
            if i == 0 and line.strip() != 'solid':
                raise ValueError('Not valid ASCII STL file.')

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

        self.data.append(Mesh(vertices, faces))

    def load_stl_binary(self, file_name):
        '''Load binary STL CAD file
        '''
        from struct import unpack
        vertices = []
        faces = []
        with open(file_name, 'rb') as f:
            header = f.read(80)
            # name = header.strip()
            n_tri = unpack('<I', f.read(4))[0]
            for i in range(n_tri):
                _normals = f.read(3*4)
                for j in range(3):
                    x = unpack('<f', f.read(4))[0]
                    y = unpack('<f', f.read(4))[0]
                    z = unpack('<f', f.read(4))[0]
                    vertices.append([x, y, z])

                j = 3*i + 1
                faces.append([j, j+1, j+2])
                _attr = f.read(2)

        self.data.append(Mesh(vertices, faces))

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
        self.browserframe = None
        self.browser = None

    def clear(self):
        s_cmd = 'Plotly.deleteTraces("canvas", [...data.keys()]);'
        self.browser.ExecuteJavascript(s_cmd)

    def update(self):
        s_cmd = self.get_plot_cmd()
        self.browser.ExecuteJavascript(s_cmd)

    def plot(self, types="solid + wireframe"):
        self.clear()
        if len(self.model.data) >= 1:
            s_cmd = self.get_model_data(types)
            self.browser.ExecuteJavascript(s_cmd)
            self.update()

    def get_plot_cmd(self):
        s_layout = '{"showlegend": false, "scene": {"aspectratio": {"x": 1, "y": 1, "z": 1}, "aspectmode": "manual"}}'
        s_config = '{"responsive": true}'
        s = 'Plotly.plot("canvas", data, ' + s_layout + ', ' + s_config +');'
        return s

    def get_model_data(self, types="solid + wireframe"):

        if isinstance(types, (str,)):
            types = [s.strip() for s in types.split('+')]

        s = 'var data = ['
        for mesh in self.model.data:
            for type in types:

                if type=="solid":
                    s += self.get_plotly_mesh3d_data(mesh) + ', '

                elif type=="wireframe":
                    s += self.get_plotly_scatter3d_data(mesh) + ', '

                else:
                    # Unknown plot type
                    return None

        s = s[:-2] + '];'
        return s

    def get_plotly_mesh3d_data(self, mesh):
        s_x = str([x[0] for x in mesh.vertices])
        s_y = str([x[1] for x in mesh.vertices])
        s_z = str([x[2] for x in mesh.vertices])
        s_i = str([f[0]-1 for f in mesh.faces])
        s_j = str([f[1]-1 for f in mesh.faces])
        s_k = str([f[2]-1 for f in mesh.faces])
        s = '{"type": "mesh3d", "name": "faces", "hoverinfo": "x+y+z", ' + \
            '"x": ' + s_x + ', "y": ' + s_y + ', "z": ' + s_z + ', ' \
            '"i": ' + s_i + ', "j": ' + s_j + ', "k": ' + s_k + ', ' \
            '"showscale": false, "color": "rgb(204,204,255)"}'
        return s

    def get_plotly_scatter3d_data(self, mesh):
        s_x = ''
        s_y = ''
        s_z = ''
        for line in mesh.get_line_segments():
            s_x += str(line[0][0]) + ', ' + str(line[1][0]) + ', null, '
            s_y += str(line[0][1]) + ', ' + str(line[1][1]) + ', null, '
            s_z += str(line[0][2]) + ', ' + str(line[1][2]) + ', null, '

        s_x = s_x[:-8]
        s_y = s_y[:-8]
        s_z = s_z[:-8]

        s = '{"type": "scatter3d", "name": "", "mode": "lines", "hoverinfo": "x+y+z", ' + \
            '"x": [' + s_x + '], "y": [' + s_y + '], "z": [' + s_z + '], "showlegend": false, ' + \
            '"line": {"color": "rgb(0,0,0)", "width": 2, "dash": "solid", "showscale": false}}'
        return s

    def get_plotly_html_canvas(self):
        s_title = 'Mesh Viewer'

        s_body = '<div id="load" style="margin:0.5em">Loading Plotly ...</div>' + \
            '<div id="canvas" style="width:100vw; height:100vh;" class="plotly-graph-div"></div>' + \
            '<script src="https://cdn.plot.ly/plotly-latest.min.js" charset="utf-8"></script>' + \
            '<script>' + \
            self.get_model_data() + \
            'var elem = document.getElementById("load"); elem.parentNode.removeChild(elem);' + \
            self.get_plot_cmd() + \
            '</script>'

        s_html = '<!DOCTYPE HTML><html"><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><title>' + s_title +'</title></head><body style="margin:0">' + \
            s_body + '</body></html>'

        return s_html

    def set_html(self, s_html):

        s_cmd = 'document.open("text/html");' + \
            'document.write(\'' + s_html + '\');' + \
            'document.close();'

        self.browser.ExecuteJavascript(s_cmd)

    def xy(self):
        bbox = self.model.get_bounding_box()
        d = 2*(bbox[2][1] - bbox[2][0])
        s_cmd = 'Plotly.relayout("canvas", {"scene":{"camera":{"eye":{"x":0, "y":0, "z":' + str(d) + '}}}});'
        self.browser.ExecuteJavascript(s_cmd)

    def xz(self):
        bbox = self.model.get_bounding_box()
        d = 2*(bbox[1][1] - bbox[1][0])
        s_cmd = 'Plotly.relayout("canvas", {"scene":{"camera":{"eye":{"x":0, "y":' + str(d) + ', "z":0}}}});'
        self.browser.ExecuteJavascript(s_cmd)

    def yz(self):
        bbox = self.model.get_bounding_box()
        d = 2*(bbox[0][1] - bbox[0][0])
        s_cmd = 'Plotly.relayout("canvas", {"scene":{"camera":{"eye":{"x":' + str(d) + ', "y":0, "z":0}}}});'
        self.browser.ExecuteJavascript(s_cmd)

    def reset(self):
        s_cmd = 'Plotly.relayout("canvas", {"scene": {"aspectratio": {"x": 1, "y": 1, "z": 1}, "aspectmode": "manual"}});'
        self.browser.ExecuteJavascript(s_cmd)


class Controller():

    def __init__(self, view=None):

        root = tk.Tk()
        root.geometry("600x550")
        root.title("Mesh Viewer")
        root.protocol("WM_DELETE_WINDOW", self.exit)

        if view is None:
            view = View(None, root)

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

        f3 = tk.Frame(root)
        f3.bind("<Configure>", self.on_configure)
        f3.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        view.browserframe = BrowserFrame(f3, view)
        view.browserframe.pack(fill=tk.BOTH, expand=True)

        menubar = tk.Menu( root )
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open...", command=lambda: self.open(var))
        file_menu.add_command(label="Exit", command=self.exit)
        menubar.add_cascade(label="File", menu=file_menu)
        root.config(menu=menubar)

        self.root = root
        self.view = view
        self.model = view.model

    def render(self):
        if hasattr(sys, '_MEIPASS'):
            settings = {'multi_threaded_message_loop': g_multi_threaded,
                        'locales_dir_path': os.path.join(sys._MEIPASS, 'locales'),
                        'resources_dir_path': sys._MEIPASS,
                        'browser_subprocess_path': os.path.join(sys._MEIPASS, 'subprocess.exe'),
                        'log_file': os.path.join(sys._MEIPASS, 'debug.log')}
        else:
            settings = {'multi_threaded_message_loop': g_multi_threaded}

        cef.Initialize(settings=settings)
        self.root.mainloop()

    def open(self, var):
        file_name = askopenfilename( title = "Select file to open",
                                     filetypes = (("CAD files","*.obj;*.stl"),
                                                  ("all files","*.*")) )
        self.model.clear()
        self.model.load_file(file_name)
        self.view.plot(var.get())

    def on_configure(self, event):
        if self.view.browserframe:
            self.view.browserframe.on_mainframe_configure(event.width, event.height)

    def exit(self):
        self.model.clear()
        self.view.set_html('<!DOCTYPE HTML><html">Shutting down ...</html>')
        if g_multi_threaded:
            cef.Shutdown()
        if self.view.browserframe:
            self.view.browserframe.on_root_close()

        self.root.destroy()
        if not g_multi_threaded:
            cef.Shutdown()


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


class BrowserFrame(tk.Frame):

    def __init__(self, master, view=None):
        self.browser = None
        self.flag = 0
        self.view = view
        tk.Frame.__init__(self, master)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<Configure>", self.on_configure)
        self.focus_set()

    def embed_browser(self):
        window_info = cef.WindowInfo()
        rect = [0, 0, self.winfo_width(), self.winfo_height()]
        window_info.SetAsChild(self.get_window_handle(), rect)
        if g_multi_threaded:
            cef.PostTask(cef.TID_UI,
                         self.create_browser,
                         window_info,
                         {},
                         "about:blank")
        else:
            self.create_browser(window_info=window_info,
                                settings={},
                                url="about:blank")

        self.browser_setup()

    def create_browser(self, window_info, settings, url):
        assert(cef.IsThread(cef.TID_UI))
        self.browser = cef.CreateBrowserSync(window_info=window_info,
                                             settings=settings,
                                             url=url)

    def browser_setup(self):
        """Wait for browser object before calling setup. """
        if self.browser is None:
            self.after(10, self.browser_setup)
        elif self.flag == 0:
            assert self.browser
            self.flag = -1;
            self.browser.SetClientHandler(LoadHandler(self))
            self.browser.SetClientHandler(FocusHandler(self))
            self.view.browser = self.browser
            self.view.set_html(self.view.get_plotly_html_canvas())
            if not g_multi_threaded:
                self.message_loop_work()

    def get_window_handle(self):
        if self.winfo_id() > 0:
            return self.winfo_id()
        elif platform.system() == "Darwin":
            from AppKit import NSApp
            import objc
            return objc.pyobjc_id(NSApp.windows()[-1].contentView())
        else:
            raise Exception("Couldn't obtain window handle")

    def message_loop_work(self):
        cef.MessageLoopWork()
        self.after(10, self.message_loop_work)

    def on_configure(self, _):
        if not self.browser:
            self.embed_browser()

    def on_root_configure(self):
        if self.browser:
            self.browser.NotifyMoveOrResizeStarted()

    def on_mainframe_configure(self, width, height):
        if self.browser:
            if platform.system() == "Windows":
                ctypes.windll.user32.SetWindowPos(
                    self.browser.GetWindowHandle(), 0,
                    0, 0, width, height, 0x0002)
            elif platform.system() == "Linux":
                self.browser.SetBounds(0, 0, width, height)

            self.browser.NotifyMoveOrResizeStarted()

    def on_focus_in(self, _):
        if self.browser:
            self.browser.SetFocus(True)

    def on_focus_out(self, _):
        if self.browser:
            self.browser.SetFocus(False)

    def on_root_close(self):
        if self.browser:
            self.browser.CloseBrowser(True)
            self.browser = None

        self.destroy()

class LoadHandler(object):

    def __init__(self, browser_frame):
        self.browser_frame = browser_frame

    def OnLoadStart(self, browser, **_):
        pass

class FocusHandler(object):

    def __init__(self, browser_frame):
        self.browser_frame = browser_frame

    def OnTakeFocus(self, next_component, **_):
        pass

    def OnSetFocus(self, source, **_):
        return False

    def OnGotFocus(self, **_):
        self.browser_frame.focus_set()


if __name__ == "__main__":

    assert cef.__version__ >= "55.3", "CEF Python v55.3+ required to run this"
    sys.excepthook = cef.ExceptHook
    app = App()
    app.start()
