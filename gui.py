import PySimpleGUI as sg
import pandas as pd
from tkinter.filedialog import askdirectory
from gui_utility.find_station_matches import find_station_matches
from layout import create_layout
from plot_source import plot_source
from init import find_datapoints
import matplotlib.pyplot as plt
import threading


class list_box_element:
    def __init__(self, name, observations):
        self.name = name
        self.observations = observations
    
    def __str__(self):
        return f"{self.name} [{self.observations}]"

def find_datapoints_threaded(dir, window):
    """
    Asynchronous function for finding datapoints in the background. 

    Parameters:
    dir (str): Path to the folder containing the data

    returns:
    No return values
    """
    find_datapoints(dir)
    window.write_event_value("load_done",0)


def run_gui():
    """
    Main function for the GUI. Creates the layout and runs the event loop.

    Parameters: 
    No parameters

    Returns:
    No return values
    """

    # Launch the GUI window
    sg.theme("DarkGrey5")
    sg.SetOptions(font=("Andalde Mono", 12))

    stations = list(set(pd.read_csv('data/derived/stations.csv')['name']))
    layout = create_layout(stations)
    main_window = sg.Window('Quasar Viewer', layout,
                            margins=[0, 0], resizable=True, finalize=True, icon="images/favicon.ico")
    main_window.TKroot.minsize(380,620)

    # Fixes issue with layout on Windows 11
    plt.figure()

    # Static variables for the event loop
    source_dict = {}
    sources = []
    dir = ""
    new_dir = ""
    scrollable = False
    show_gif = False
    sort_alph_reverse = False
    sort_num_reverse = True

    # Event loop for the GUI
    while True:
        event, values = main_window.Read(timeout=25)

        ### Menu bar events ###

        if event == "Open folder":
            new_dir = askdirectory(initialdir="data/sessions")
            if new_dir != dir and new_dir:
                # If the user has selected a new folder, start the loading animation
                # and find the datapoints in the background
                show_gif = True
                thread_id = threading.Thread(target=find_datapoints_threaded,args=(new_dir,main_window),daemon=True)
                thread_id.start()
                #main_window.perform_long_operation(
                #    lambda: find_datapoints_threaded(new_dir), "load_done")

        if event == "About...":
            sg.Popup("About info")

        if event == sg.WIN_CLOSED or event == "cancel" or event == "Exit":
            break

        ### Settings events ###

        if event == "source_list":

            # Ignore event if no source was selected
            if values["source_list"] == []:
                continue
            source = values["source_list"][0].name

            # Make all check boxes and their columns invisible
            main_window["check_box_col"].update(visible=False)
            main_window["check_box_col_scroll"].update(visible=False)

            for box in stations:
                main_window[box].update(visible=False)
                main_window[box].hide_row()
                main_window[f"{box}_scroll"].update(visible=False)
                main_window[f"{box}_scroll"].hide_row()

            # Switch to scrollable column if more than 9 entries
            scrollable = len(source_dict[source]['stations']) > 9

            # Make only the available check boxes and the correct column visible
            for box in source_dict[source]['stations']:
                if scrollable:
                    main_window[f"{box}_scroll"].update(visible=True)
                    main_window[f"{box}_scroll"].unhide_row()
                else:
                    main_window[box].update(visible=True)
                    main_window[box].unhide_row()

            if scrollable:
                main_window["check_box_col_scroll"].update(visible=True)
            else:
                main_window["check_box_col"].update(visible=True)

            # Update the GUI
            main_window["check_box_col"].contents_changed()
            main_window["check_box_col_scroll"].contents_changed()
            main_window["stations_col"].contents_changed()
            main_window.refresh()

        # Keep the check boxes synchronized between scrollable and not
        # scrollable columns
        if event in stations:
            main_window[f"{event}_scroll"].update(value=values[event])

        if event[:-7] in stations:
            main_window[event[:-7]].update(value=values[event])

        ### Buttons events ###

        if event == "plot":
            # Check that user has selected a folder
            if not dir:
                sg.Popup("Please select a folder first!")
                continue

            source = values["source_list"][0]
            # Check that user has selected a source
            if source not in sources:
                sg.Popup("Source not found! Please select one from the list.")
                continue

            # Find which band the user has selected, selected station will have
            # a value of True, all others False
            band = [values['A_band'], values['B_band'],
                    values['C_band'], values['D_band']].index(True)

            # Ignore the stations that were unselected in the GUI
            ignored_stations = []
            for box in stations:
                if (not values[box]) and (not scrollable):
                    ignored_stations.append(box)
                elif (not values[f"{box}_scroll"]) and (scrollable):
                    ignored_stations.append(box)

            return_message = plot_source(source.name, ignored_stations=ignored_stations, bands=band)
            if return_message == "no_data_found":
                sg.Popup("No data points found for this source using the selected stations and band.")

        if event == "sort_alph": 
            sources.sort(key=lambda s: s.name, reverse= sort_alph_reverse)
            sort_alph_reverse = not sort_alph_reverse
            sort_num_reverse = True
            main_window["source_list"].update(values=sources)

        if event == "sort_num":
            sources.sort(key=lambda s: s.observations, reverse= sort_num_reverse)
            sort_num_reverse = not sort_num_reverse
            sort_alph_reverse = False
            main_window["source_list"].update(values=sources)
            

        ### Load events ###

        if event == "load_done":
            # When find datapoints is done, update the GUI, name of the window
            # and source list. Also stop the loading animation
            for box in stations:
                main_window[box].update(visible=False)
                main_window[box].hide_row()
                main_window[f"{box}_scroll"].update(visible=False)
                main_window[f"{box}_scroll"].hide_row()
            main_window["check_box_col"].contents_changed()
            main_window["check_box_col_scroll"].contents_changed()

            source_dict = find_station_matches()
            sources = list(map(lambda s: list_box_element(s,source_dict[s]['observations']), source_dict))

            sources.sort(key=lambda s: s.name)

            main_window["source_list"].update(values=sources)

            main_window.set_title(f"Quasar Viewer - {new_dir.split('/')[-1]}")
            main_window.refresh()
            dir = new_dir
            show_gif = False
            sg.PopupAnimated(None)


        if show_gif:
            sg.PopupAnimated("images/loading.gif", time_between_frames=50)


if __name__ == '__main__':
    run_gui()
