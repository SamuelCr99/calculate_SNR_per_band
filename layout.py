import PySimpleGUI as sg


def create_layout(sources, stations):
    stations.sort()

    check_boxes = list(map(lambda s: [sg.Checkbox(s,default=True,visible=False,key=s)],stations))

    left_col = [[sg.Combo(sources, key="source_list", s=(30,30), enable_events=True)],
                [sg.Column(check_boxes, s=(300,300), scrollable=True, vertical_scroll_only=True,key="check_box_col")],
                [sg.Text("Band selection: "),sg.Radio("A","band", key='A_band', default=True),sg.Radio("B","band", key="B_band"),sg.Radio("C","band", key="C_band"),sg.Radio("D","band", key="D_band")],
                [sg.Button("Plot",key="plot"),sg.Button("Cancel",key="cancel")]]

    right_col = [[sg.Canvas(key="canvas")]]
    # right_col = [[sg.Text("Right col")]]

    menu = [["File", ["Open", "Exit"]],
            ["Edit", "Settings"],
            ["Help", "About..."]]

    layout = [[sg.Menu(menu, key="menu")],
              [sg.Column(left_col),sg.Column(right_col,expand_x=True,expand_y=True, key="right")]]

    return layout