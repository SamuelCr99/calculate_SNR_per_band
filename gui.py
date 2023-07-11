import PySimpleGUI as sg
import pandas as pd
from gui_utility.find_station_matches import find_station_matches
from layout import create_layout
from plot_source_1_band import plot_source

def run_gui():
    

    sg.theme("DarkBlue")
    sg.SetOptions(font=("Andalde Mono", 10))
    source_dict = find_station_matches()
    
    sources = list(source_dict.keys())
    stations = list(set(pd.read_csv('data/derived/stations.csv')['name']))

    layout = create_layout(sources,stations)
    main_window = sg.Window('VLBI baseline viewer', layout,
                            margins=[20, 20], resizable=True, finalize=True)


    # Event loop for the GUI
    while True:
        window, event, values = sg.read_all_windows()
        
        if event == "source_list":
            for box in stations:
                main_window[box].update(visible=False)
                main_window[box].hide_row()
            
            for box in source_dict[values["source_list"]]:
                main_window[box].update(visible=True)
                main_window[box].unhide_row()
            main_window["check_box_col"].contents_changed()
            main_window.refresh()

        if event == sg.WIN_CLOSED or event == "cancel" or event == "Exit":
            break

        if event == "plot":
            # Todo: Add checks to that source and band are selected
            source = values["source_list"]
            ignored_stations = []
            band = [values['A_band'], values['B_band'], values['C_band'], values['D_band']].index(True)

            for box in stations:
                if not values[box]:
                    ignored_stations.append(box)

            plot_source(source, '', 'data/sessions/session1/', ignored_stations, band)


if __name__ == '__main__':
    run_gui()