import PySimpleGUI as sg
from init import find_datapoints
from tkinter.filedialog import askdirectory

gif103 = 'images/loading.gif'


layout = [
           [sg.Button('Cancel')],
           [sg.Button('qwe', key='find_datapoints')]
         ]

window = sg.Window('My new window').Layout(layout)

while True:             # Event Loop
    event, values = window.Read(timeout=25)
    if event in (None, 'Exit', 'Cancel'):
        break
    if event == 'find_datapoints':
        sg.popup_animated(gif103, time_between_frames=10)

    sg.popup_animated