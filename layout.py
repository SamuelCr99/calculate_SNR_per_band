import PySimpleGUI as sg


def create_layout(sources, stations):
    stations.sort()

    check_boxes = list(map(lambda s: [sg.Checkbox(s,default=True,visible=False,key=s),sg.Push()],stations))

    left_col = [[sg.Frame("Source",[[sg.Combo(sources, key="source_list", size=(30,30), enable_events=True, expand_x=True,p=20)]], expand_x=True)],
                [sg.Frame("Stations",[[sg.Column(check_boxes, s=(300,300), scrollable=True, vertical_scroll_only=True,key="check_box_col",element_justification="left",sbar_relief="RELIEF_FLAT",expand_x=True,expand_y=True,p=20)]],expand_x=True,expand_y=True)],
                [sg.Frame("Band",[[sg.Radio("A","band", key='A_band', default=True),sg.Radio("B","band", key="B_band"),sg.Radio("C","band", key="C_band"),sg.Radio("D","band", key="D_band")]],expand_x=True)],
                [sg.Push(),sg.Button("Plot",key="plot"),sg.Button("Cancel",key="cancel")]]

    right_col = [[sg.Canvas(key="canvas")]]
    # right_col = [[sg.Text("Right col")]]

    menu = [["File", ["Open", "Exit"]],
            ["Edit", "Settings"],
            ["Help", "About..."]]

    layout = [[sg.Menu(menu, key="menu")],
              [sg.Column(left_col,expand_x=True,expand_y=True)]]

    return layout