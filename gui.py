import PySimpleGUI as sg
import pandas as pd
from gui_utility.find_station_matches import find_station_matches
from layout import create_layout

def run_gui():
    

    sg.theme("DarkBlue")
    sg.SetOptions(font=("Andalde Mono", 12))
    source_dict = find_station_matches()
    
    sources = list(source_dict.keys())
    stations = list(set(pd.read_csv('data/derived/stations.csv')['name']))

    layout = create_layout(sources,stations)
    main_window = sg.Window('VLBI baseline viewer', layout,
                            margins=[20, 20], resizable=True, finalize=True)


    # Event loop for the GUI
    while True:
        window, event, values = sg.read_all_windows()

        if event == "temp":
            print("Button pressed")
            for box in sources:
                main_window[box].update(visible=True)
            main_window["right"].contents_changed()
            main_window.refresh()
        
        if event == "source_list":
            for box in source_dict[values["source_list"][0]]:
                main_window[box].update(visible=True)
            main_window["right"].contents_changed()
            main_window.refresh()

        if event == sg.WIN_CLOSED:
            break


if __name__ == '__main__':
    run_gui()