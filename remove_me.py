import PySimpleGUI as sg
import numpy as np
from matplotlib.widgets  import RectangleSelector
import matplotlib.figure as figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

# instantiate matplotlib figure
fig = figure.Figure()
ax = fig.add_subplot(111)
DPI = fig.get_dpi()
fig.set_size_inches(505 * 2 / float(DPI), 707 / float(DPI))

# ------------------------------- This is to include a matplotlib figure in a Tkinter canvas
def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)



class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)



layout = [
    [sg.B('start', key='start')],
    [sg.Canvas(key='controls_cv')],
    [sg.Column(
        layout=[
            [sg.Canvas(key='fig_cv',
                       # it's important that you set this size
                       size=(500 * 2, 700)
                       )]
        ]
    )],
]

window = sg.Window('Test', layout)

while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED:
        break
    elif event == 'start':
        x = np.linspace(0, 2 * np.pi)
        y = np.sin(x)
        ax.plot(x, y)
        draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)

window.close()