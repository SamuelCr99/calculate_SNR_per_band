import PySimpleGUI as sg


def create_layout(sources, stations):

    check_boxes = list(map(lambda s: [sg.Checkbox(s,visible=False,key=s)],stations))

    left_col = [[sg.Listbox(sources, key="source_list", s=(30,30), enable_events=True)],
                [sg.Text("Band selection: "),sg.Radio("A","band"),sg.Radio("B","band"),sg.Radio("C","band"),sg.Radio("D","band")],
                [sg.Button("Temp button",key="temp")]]

    right_col = check_boxes

    layout = [[sg.Column(left_col),sg.Column(right_col, scrollable=True, vertical_scroll_only=True,expand_x=True,expand_y=True, key="right")]]

    return layout