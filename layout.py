import PySimpleGUI as sg


def create_layout(stations):
    """
    Creates the layout for the GUI

    Parameters:
    stations(list): A list of all stations

    Returns:
    The finished layout
    """
    stations.sort()
    headings = ["Sel.", "Stations", "Obs.", "A SEFD", "B SEFD", "C SEFD", "D SEFD"]
    table_col = sg.Table([[]],headings=headings, key="stations_table", enable_click_events=True, select_mode=sg.TABLE_SELECT_MODE_BROWSE, expand_x=True, expand_y=True, p=20, alternating_row_color="grey25")

    sources_col = sg.Column([[sg.Listbox([[]], key="source_list", size=(30, 10), enable_events=True, expand_x=True)],
                             [sg.Button("Sort alphabetical", key="sort_alph"),sg.Button("Sort numerical", key="sort_num"),sg.Push()]
                             ], expand_x=True, p=20)


    # Currently the only column
    left_col = [[sg.Frame("Source", [[sources_col]], expand_x=True)],
                [sg.Frame("Stations", [[table_col]], expand_x=True, expand_y=True)],
                [sg.Frame("Band", [[sg.Radio("A", "band", key='A_band', default=True), sg.Radio("B", "band", key="B_band"), sg.Radio(
                    "C", "band", key="C_band"), sg.Radio("D", "band", key="D_band")]], expand_x=True)],
                [sg.Text(text="", key="loading_text", text_color="white", font=("Andalde Mono", 16)), sg.Push(), sg.Button("Plot", key="plot"), sg.Button("Cancel", key="cancel")]]

    menu = [["&File", ["&Open folder", "&Save configuration","&Exit"]],
            ["&Help", "&About..."]]

    layout = [[sg.MenubarCustom(menu)],
              [sg.Column(left_col, expand_x=True, expand_y=True)]]

    return layout
