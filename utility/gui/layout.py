import PySimpleGUI as sg


def create_layout():
    """
    Creates the layout for the GUI

    Parameters:
    stations(list): A list of all stations

    Returns:
    The finished layout
    """
    station_headings = ["Sel.", "Stations", "Obs.", "SEFD", "★"]
    col_widths = [4,10,4,10,4]
    stations_col = sg.Table([], headings=station_headings, col_widths=col_widths, auto_size_columns=False, key="stations_table", enable_click_events=True, select_mode=sg.TABLE_SELECT_MODE_NONE,
                         expand_x=True, expand_y=True, p=20, alternating_row_color="grey25", justification="center")

    source_headings = ["Source", "Obs."]
    sources_col = sg.Table([], headings=source_headings, key="sources_table", enable_click_events=True, select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                         expand_x=True, expand_y=True, p=20, alternating_row_color="grey25", justification="center")

    debug_buttons = sg.Column([[sg.Push(), sg.Button("Fit SEFD", key="fit_SEFD"), sg.Button("Get Gauss.", key="gauss")]], p=[[0,0],[20,0]], expand_x=True)

    debug_layout = [[sg.Text("u-v scale:", s=15), sg.Input(default_text="1", s=15, key="scale_uv"), sg.Button("Set", key="set_scale_uv")],
                    [sg.Text("Flux scale:", s=15), sg.Input(default_text="1", s=15, key="scale_flux"), sg.Button("Set", key="set_scale_flux"), sg.Button("Automatic", key="set_scale_flux_auto")],
                    [sg.Text("Source model:", s=15), sg.Combo(["QuasarModelImg","QuasarModelRaw"], s=15, default_value=["QuasarModelImg"], key="model_type", enable_events=True)],
                    [debug_buttons]]
    debug_col = sg.Column(debug_layout, p=20, expand_x=True)

    # Currently the only column
    left_col = [[sg.Frame("Source", [[sources_col]], expand_x=True, expand_y=True)],
                [sg.Frame("Band", [[sg.Radio("A", "band", key='A_band', enable_events=True, default=True),
                                    sg.Radio("B", "band", key="B_band", enable_events=True),
                                    sg.Radio("C", "band", key="C_band", enable_events=True),
                                    sg.Radio("D", "band", key="D_band", enable_events=True),
                                    sg.Radio("S", "band", key="S_band", enable_events=True, visible=False),
                                    sg.Radio("X", "band", key="X_band", enable_events=True, visible=False)]], expand_x=True)],
                [sg.Frame("Stations", [[stations_col]],
                          expand_x=True, expand_y=True)],
                [sg.Frame("Debug", [[debug_col]], expand_x=True)],
                [sg.Text(text="", key="loading_text", text_color="white", font=("Andalde Mono", 16))]]

    figure1_tab = [[sg.Canvas(key="fig1", background_color="white", expand_x=True, expand_y=True)],
                   [sg.Canvas(key="toolbar1",background_color="white", expand_x=True)]]
    
    figure2_tab = [[sg.Canvas(key="fig2", background_color="white", expand_x=True, expand_y=True)],
                   [sg.Canvas(key="toolbar2", background_color="white", expand_x=True)]]

    figure3_tab = [[sg.Canvas(key="fig3", background_color="white", expand_x=True, expand_y=True)],
                   [sg.Canvas(key="toolbar3", background_color="white", expand_x=True)]]

    figure4_tab = [[sg.Canvas(key="fig4", background_color="white", expand_x=True, expand_y=True)],
                   [sg.Canvas(key="toolbar4", background_color="white", expand_x=True)]]
    
    figure_tabgroup = [[sg.Tab("Flux density (meas.)", figure1_tab, background_color="white")],
                       [sg.Tab("Flux density (pred.)", figure2_tab, background_color="white")],
                       [sg.Tab("Flux density ratio", figure3_tab, background_color="white")],
                       [sg.Tab("Radial", figure4_tab, background_color="white")]]
    
    right_col = [[sg.TabGroup(figure_tabgroup, expand_x=True, expand_y=True)]]

    menu = [["&File", ["&Open session", "&Open fits", "&Exit"]],
            ["&Configuration", ["&Save", "&Restore" , "&Delete"]],
            ["&Help", "&About..."]]

    layout = [[sg.MenubarCustom(menu, text_color="black", bar_background_color="white", background_color="white", bar_text_color="black")],
              [sg.Column(left_col, expand_x=True, expand_y=True, key="left_col"),sg.Column(right_col, expand_x=True, expand_y=True, key="right_col")]]

    return layout
