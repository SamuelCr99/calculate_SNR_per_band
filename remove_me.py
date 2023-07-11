import PySimpleGUI as sg

gif103 = 'images/gif103.gif'


layout = [  [sg.Text('Loading....', font='ANY 15')],
            [sg.Image(gif103, key='_IMAGE_')],
           [sg.Button('Cancel')]
         ]

window = sg.Window('My new window').Layout(layout)

while True:             # Event Loop
    event, values = window.Read(timeout=25)
    if event in (None, 'Exit', 'Cancel'):
        break
    window.Element('_IMAGE_').UpdateAnimation(gif103,  time_between_frames=50)