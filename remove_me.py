import PySimpleGUI as sg

sources = ['hej', 'asd', 'lol']

left_col = [[sg.Listbox(sources, key="source_list", s=(30,30), enable_events=True)]]

layout = [[sg.Column(left_col)]]
main_window = sg.Window('VLBI baseline viewer', layout,
                        margins=[20, 20], resizable=True, finalize=True)


while True:
    window, event, values = sg.read_all_windows()
    if event == "source_list":
        print(values["source_list"])