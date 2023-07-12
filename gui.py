import PySimpleGUI as sg
import pandas as pd
from tkinter.filedialog import askdirectory
from gui_utility.find_station_matches import find_station_matches
from layout import create_layout
from plot_source_1_band import plot_source
from init import find_datapoints

def find_datapoints_threaded(dir):
    try:
        find_datapoints(dir)
    except:
        pass

def run_gui():
    
    sg.theme("DarkGrey5")
    sg.SetOptions(font=("Andalde Mono", 12))
    
    source_dict = {}
    sources = []
    dir = ""
    new_dir = ""
    scrollable = False

    stations = list(set(pd.read_csv('data/derived/stations.csv')['name']))

    layout = create_layout(stations)
    main_window = sg.Window('Quasar Viewer', layout,
                            margins=[20, 20], resizable=True, finalize=True, icon="images/favicon.ico")

    show_gif = False
    # Event loop for the GUI
    while True:
        # window, event, values = sg.read_all_windows()
        event, values = main_window.Read(timeout=25)

        if event == "source_list":
            if values["source_list"] == []:
                continue

            main_window["check_box_col"].update(visible=False)
            main_window["check_box_col_scroll"].update(visible=False)

            for box in stations:
                main_window[box].update(visible=False)
                main_window[box].hide_row()
                main_window[f"{box}_1"].update(visible=False)
                main_window[f"{box}_1"].hide_row()
            
            scrollable = len(source_dict[values["source_list"]]) > 9

            for box in source_dict[values["source_list"]]:
                if scrollable:
                    main_window[f"{box}_1"].update(visible=True)
                    main_window[f"{box}_1"].unhide_row()
                else:
                    main_window[box].update(visible=True)
                    main_window[box].unhide_row()
            
            if scrollable:
                main_window["check_box_col_scroll"].update(visible=True)
            else:
                main_window["check_box_col"].update(visible=True)
            
            main_window["check_box_col"].contents_changed()
            main_window["check_box_col_scroll"].contents_changed()
            main_window["stations_col"].contents_changed()
            main_window.refresh()

        if event == sg.WIN_CLOSED or event == "cancel" or event == "Exit":
            break

        if event == "plot":
            if not dir:
                sg.Popup("Please select a folder first!")
                continue

            source = values["source_list"]
            if source not in sources:
                sg.Popup("Source not found! Please select one from the list.")
                continue

            ignored_stations = []
            band = [values['A_band'], values['B_band'], values['C_band'], values['D_band']].index(True)

            for box in stations:
                if (not values[box]) and (not scrollable) :
                    ignored_stations.append(box)
                elif (not values[f"{box}_1"]) and (scrollable) :
                    ignored_stations.append(box)

            plot_source(source, '', dir, ignored_stations, band)

        if event == "Open folder":
            new_dir = askdirectory(initialdir="data/sessions")
            if new_dir != dir and new_dir:
                show_gif = True
                sg.PopupAnimated("images/loading.gif", background_color="black", time_between_frames=100)
                main_window.perform_long_operation(lambda : find_datapoints_threaded(new_dir),"load_done")

        if event == "About...":
            # Change title
            sg.Popup("About info")

        if event in stations:
            main_window[f"{event}_1"].update(value=values[event])
        if event[:-2] in stations:
            main_window[event[:-2]].update(value=values[event])

        if event == "load_done":
            for box in stations:
                main_window[box].update(visible=False)
                main_window[box].hide_row()
                main_window[f"{box}_1"].update(visible=False)
                main_window[f"{box}_1"].hide_row()
            main_window["check_box_col"].contents_changed()
            main_window["check_box_col_scroll"].contents_changed()

            source_dict = find_station_matches()
            sources = list(source_dict.keys())
            main_window["source_list"].update(values=sources)

            main_window.set_title(f"Quasar Viewer - {new_dir.split('/')[-1]}")
            main_window.refresh()
            dir = new_dir
            show_gif = False
            sg.PopupAnimated(None)

        if show_gif:
            sg.PopupAnimated("images/loading.gif", background_color="black", time_between_frames=50, grab_anywhere=False)

if __name__ == '__main__':
    run_gui()