import os
import PySimpleGUI as sg
import pandas as pd
import matplotlib.pyplot as plt
from tkinter.filedialog import askdirectory
from gui_utility.find_station_matches import find_station_matches
from layout import create_layout
from plot_source import plot_source
from init import find_datapoints, find_stations


class list_box_element:
    # Class for representing the sources in the list box
    def __init__(self, name, observations):
        self.name = name
        self.observations = observations

    def __str__(self):
        return f"{self.name} [{self.observations}]"


def update_station_table(station_information, stations):
    """
    Generates a table that can be used in the GUI

    Parameters:
    station_information(DataFrame): Information regarding *all* stations
    stations(dict): A dictionary with the wanted stations as keys

    Returns:
    A list of lists for the table
    """
    new_table = []
    for station in stations:
        activated = "X" if station_information[station_information['name']
                                               == station]["selected"].values[0] else ""
        a_sefd = station_information[station_information['name']
                                     == station]['A_SEFD'].values[0]
        b_sefd = station_information[station_information['name']
                                     == station]['B_SEFD'].values[0]
        c_sefd = station_information[station_information['name']
                                     == station]['C_SEFD'].values[0]
        d_sefd = station_information[station_information['name']
                                     == station]['D_SEFD'].values[0]
        new_table.append(
            [activated, station, stations[station], a_sefd, b_sefd, c_sefd, d_sefd])
    return new_table


def run_gui():
    """
    Main function for the GUI. Creates the layout and runs the event loop.

    Parameters: 
    No parameters

    Returns:
    No return values
    """

    # Check that script is run from correct directory
    folders = os.listdir()
    if "data" not in folders:
        raise Exception("Data folder not found, make sure script is being run from correct path")


    # Launch the GUI window
    sg.theme("DarkGrey5")
    sg.SetOptions(font=("Andalde Mono", 12))

    # Retrieve config if it exists, else create one
    try:
        station_information = pd.read_csv('data/derived/stations.csv')
    except:
        find_stations()
        station_information = pd.read_csv('data/derived/stations.csv')
    saved_station_information = station_information.copy(deep=True)
    
    # Create the main GUI window
    stations = list(set(station_information['name']))
    layout = create_layout(stations)
    main_window = sg.Window('Quasar Viewer', layout,
                            margins=[0, 0], resizable=True, finalize=True,
                            icon="images/favicon.ico", enable_close_attempted_event=True)
    main_window.TKroot.minsize(630, 720)

    # Fixes issue with layout on Windows 11
    plt.figure()

    # Static variables for the event loop
    source_dict = {}
    sources = []
    source = None
    dir = ""
    sort_alph_reverse = False
    sort_num_reverse = True
    sort_stat_reverse = [False]*7

    # Event loop for the GUI
    while True:
        event, values = main_window.Read(timeout=25)

        ### Menu bar events ###

        # Open the vgosDB
        if event == "Open folder":
            new_dir = askdirectory(initialdir="data/sessions")
            if new_dir != dir and new_dir:
                # Tell the user that we are loading data
                main_window["loading_text"].update(value="Loading...")
                main_window.set_title(f"Quasar Viewer - Loading...")
                main_window.refresh()

                # Load data (takes time)
                datapoint_df = find_datapoints(new_dir)

                # Update source info
                source = None
                source_dict = find_station_matches(datapoint_df)
                sources = list(map(lambda s: list_box_element(
                    s, source_dict[s]['observations']), source_dict))
                sources.sort(key=lambda s: s.name)
                
                # Reset/update GUI
                dir = new_dir
                main_window["stations_table"].update([])
                main_window["source_list"].update(values=sources)
                main_window.set_title(f"Quasar Viewer - {new_dir.split('/')[-1]}")
                main_window["loading_text"].update(value="")
                main_window.refresh()

        # Save the stations info config
        if event == "Save configuration":
            station_information.to_csv(
                "data/derived/stations.csv", index=False)
            saved_station_information = station_information.copy(deep=True)

        # Restore old stations info config
        if event == "Restore":
            a = sg.popup_yes_no(
                "Restoring will remove all configurations set. Do you wish to continue?")
            if a == "Yes":
                find_stations()
                station_information = pd.read_csv("data/derived/stations.csv")
                saved_station_information = station_information.copy(deep=True)
                new_table = update_station_table(
                    station_information, source_dict[source.name]["stations"])
                main_window["stations_table"].update(new_table)
                main_window.refresh()

        # Display about info
        if event == "About...":
            sg.Popup("About info")

        # Close the program and save config
        if event == sg.WIN_CLOSE_ATTEMPTED_EVENT or event == "cancel" or event == "Exit":
            if not station_information.equals(saved_station_information):
                a,_ = sg.Window("Unsaved changes", [[sg.Text("You have unsaved changes. Do you wish to save?")],
                                                    [sg.Button("Yes",k="Yes"),sg.Button("No",k="No"),sg.Button("Cancel",k="Cancel")]], finalize=True, icon="images/favicon.ico", modal=True).read(close=True)
                if a == "Yes":
                    station_information.to_csv(
                        "data/derived/stations.csv", index=False)
                if a == "Cancel":
                    continue
            break

        ### Source list events ###

        # Source selected
        if event == "source_list":

            # Ignore event if no source was selected
            if not values["source_list"]:
                continue

            # Update the stations table
            source = values["source_list"][0]
            new_table = update_station_table(
                station_information, source_dict[source.name]["stations"])
            main_window["stations_table"].update(new_table)
            main_window.refresh()

        # Sort the sources by name
        if event == "sort_alph":
            sources.sort(key=lambda s: s.name, reverse=sort_alph_reverse)
            sort_alph_reverse = not sort_alph_reverse
            sort_num_reverse = True
            main_window["source_list"].update(values=sources)
            main_window["source_list"].set_value([source])

        # Sort the sources by observations
        if event == "sort_num":
            sources.sort(key=lambda s: s.observations,
                         reverse=sort_num_reverse)
            sort_num_reverse = not sort_num_reverse
            sort_alph_reverse = False
            main_window["source_list"].update(values=sources)
            main_window["source_list"].set_value([source])

        ### Plot event ###

        if event == "plot":
            # Check that user has selected a folder
            if not dir:
                sg.Popup("Please select a folder first!")
                continue

           # Check that user has selected a source
            if not values["source_list"]:
                sg.Popup("No source selected! Please select one from the list.")
                continue

            # Check that user has selected a valid source
            if source not in sources:
                sg.Popup("Source not found! Please select one from the list.")
                continue

            # Find which band the user has selected, selected station will have
            # a value of True, all others False
            band = [values['A_band'], values['B_band'],
                    values['C_band'], values['D_band']].index(True)

            # Ignore the stations that were unselected in the GUI
            ignored_stations = station_information.loc[station_information["selected"] == 0]["name"].to_list(
            )

            # Try to plot
            return_message = plot_source(
                source.name, datapoint_df, station_information, ignored_stations=ignored_stations, bands=band)
            if return_message == "no_data_found":
                sg.Popup(
                    "No data points found for this source using the selected stations and band.")

        ### Table click events ###

        if event[0] == "stations_table" and event[1] == "+CLICKED+":
            click_row, click_col = event[2]

            # Unusable clicks
            if click_row == None or click_col == None or click_col == -1:
                continue

            # Clicking when no data is in the table should do nothing
            if all(not e for e in main_window["stations_table"].get()):
                continue

            # Sort by columns
            elif click_row == -1:

                reverse = sort_stat_reverse[click_col]

                # Sort by selected
                if click_col == 0:
                    source_dict[source.name]["stations"] = dict(sorted(source_dict[source.name]["stations"].items(
                    ), key=lambda stat: station_information.loc[station_information["name"] == stat[0]]["selected"].iloc[0], reverse=reverse))

                # Sort by name
                if click_col == 1:
                    source_dict[source.name]["stations"] = dict(sorted(
                        source_dict[source.name]["stations"].items(), key=lambda stat: stat[0], reverse=reverse))

                # Sort by observations
                if click_col == 2:
                    source_dict[source.name]["stations"] = dict(sorted(
                        source_dict[source.name]["stations"].items(), key=lambda stat: int(stat[1]), reverse=reverse))

                # Sort by A SEFD
                if click_col == 3:
                    source_dict[source.name]["stations"] = dict(sorted(source_dict[source.name]["stations"].items(), key=lambda stat: float(
                        station_information.loc[station_information["name"] == stat[0]]["A_SEFD"].iloc[0]), reverse=reverse))

                # Sort by B SEFD
                if click_col == 4:
                    source_dict[source.name]["stations"] = dict(sorted(source_dict[source.name]["stations"].items(), key=lambda stat: float(
                        station_information.loc[station_information["name"] == stat[0]]["B_SEFD"].iloc[0]), reverse=reverse))

                # Sort by C SEFD
                if click_col == 5:
                    source_dict[source.name]["stations"] = dict(sorted(source_dict[source.name]["stations"].items(), key=lambda stat: float(
                        station_information.loc[station_information["name"] == stat[0]]["C_SEFD"].iloc[0]), reverse=reverse))

                # Sort by D SEFD
                if click_col == 6:
                    source_dict[source.name]["stations"] = dict(sorted(source_dict[source.name]["stations"].items(), key=lambda stat: float(
                        station_information.loc[station_information["name"] == stat[0]]["D_SEFD"].iloc[0]), reverse=reverse))

                # Update list
                sort_stat_reverse = [False]*7
                sort_stat_reverse[click_col] = not reverse

                # Update GUI
                new_table = update_station_table(
                    station_information, source_dict[source.name]["stations"])
                main_window["stations_table"].update(new_table)
                main_window.refresh()

            # Select/deselect station
            elif click_col == 0:
                # Update selection
                selected_station = main_window["stations_table"].get()[click_row][1]
                selected = station_information.loc[station_information["name"] == selected_station, "selected"].iloc[0]

                if selected:
                    station_information.loc[station_information["name"] == selected_station, "selected"] = 0
                else:
                    station_information.loc[station_information["name"] == selected_station, "selected"] = 1

                # Update GUI
                new_table = update_station_table(station_information, source_dict[source.name]["stations"])
                main_window["stations_table"].update(new_table)
                main_window.refresh()

            # Edit SEFD values
            elif click_col in [3, 4, 5, 6]:
                # Get stats of the selected cell
                selected_station = main_window["stations_table"].get()[click_row][1]
                selected_band = chr(65+click_col-3)
                click_col_name = f'{selected_band}_SEFD'
                orig_SEFD = station_information.loc[station_information["name"]
                                                    == selected_station, click_col_name].iloc[0]

                # Popup to ask user to fill in new value
                edit_popup = sg.Window("Edit...", [[sg.Text("Station:", s=(8, 1)), sg.Text(selected_station)],
                                                   [sg.Text("Band:", s=(8, 1)), sg.Text(
                                                       selected_band)],
                                                   [sg.Text("SEFD: ", s=(8, 1)), sg.Input(
                                                       default_text=orig_SEFD, key="new_SEFD_input"), sg.Button("Set", key="new_SEFD_set")],
                                                   [sg.Text("Invalid input!", key="invalid_input", visible=False, text_color="red")]], finalize=True, icon="images/favicon.ico", modal=True)
                edit_popup["new_SEFD_input"].bind("<Return>", "_enter")
                edit_popup["invalid_input"].hide_row()
                edit_popup["new_SEFD_input"].set_focus()

                # Event loop for popup
                while True:
                    event, values = edit_popup.Read()

                    if event == "new_SEFD_set" or event == "new_SEFD_input_enter":
                        new_SEFD = values["new_SEFD_input"]

                        # Only allow numbers
                        try:
                            if new_SEFD.isdigit():
                                new_SEFD = str(int(new_SEFD))
                            else:
                                new_SEFD = str(float(new_SEFD))
                                SEFD_int, SEFD_frac = new_SEFD.split(".")
                                if not int(SEFD_frac):
                                    new_SEFD = int(SEFD_int)
                        except:
                            edit_popup["invalid_input"].update(visible=True)
                            edit_popup["invalid_input"].unhide_row()
                            edit_popup.refresh()
                            continue

                        # Set new SEFD
                        station_information.loc[station_information["name"]
                                                == selected_station, click_col_name] = new_SEFD
                        
                        # Update GUI
                        new_table = update_station_table(
                            station_information, source_dict[source.name]["stations"])
                        main_window["stations_table"].update(new_table)
                        main_window.refresh()

                        # Close popup
                        edit_popup.close()
                    break


if __name__ == '__main__':
    run_gui()
