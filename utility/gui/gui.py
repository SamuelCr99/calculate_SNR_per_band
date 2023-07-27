assert __name__ != '__main__', "Don't run this file, run main.py"

import os
import PySimpleGUI as sg
import pandas as pd
import matplotlib.pyplot as plt
import re
from tkinter.filedialog import askdirectory, askopenfilename
from find_station_matches import find_station_matches
from layout import create_layout
from calculate_flux import calculate_flux
from plot_source import plot_source
from init import find_datapoints, find_stations
from source_model_wrapper import SourceModelWrapper
from least_square_fit import least_square_fit
from data import DataWrapper
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

def repack(widget, option):
    pack_info = widget.pack_info()
    pack_info.update(option)
    widget.pack(**pack_info)

def draw_fig(canvas, fig, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    toolbar = Toolbar(figure_canvas_agg, canvas_toolbar)
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=1)
    figure_canvas_agg.draw()
    toolbar.update()

class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)

def update_station_table(station_information, stations, highlights, band):
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
        s_sefd = station_information[station_information['name']
                                     == station]['S_SEFD'].values[0]
        x_sefd = station_information[station_information['name']
                                     == station]['X_SEFD'].values[0]
        sefd = [a_sefd,b_sefd,c_sefd,d_sefd,s_sefd,x_sefd][band]
        highlight = "X" if station in highlights else ""
        new_table.append([activated, station, stations[station], sefd, highlight])
    return new_table

def update_sources_table(sources):
    new_table = []
    for source in sources: 
        new_table.append([source, sources[source]['observations']])
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
    layout = create_layout()
    main_window = sg.Window('Quasar Viewer', layout,
                            margins=[0, 0], resizable=True, finalize=True,
                            icon="images/favicon.ico", enable_close_attempted_event=True)
    main_window.TKroot.minsize(1320, 820)

    # Fixes so the left column doesn't expand
    repack(main_window["left_col"].Widget, {'fill':'y', 'expand':0, 'before':main_window["right_col"].Widget})

    # Fixes issue with layout on Windows 11
    plt.figure()

    # Static variables for the event loop
    dir = ""
    source_dict = {}
    source = ""
    source_model = None
    band = 0
    sort_stat_reverse = [True, False, True, True, True]
    sort_source_reverse = [False, True]
    highlights = []
    is_abcd = True
    fig1 = plt.figure(0)
    fig2 = plt.figure(1)
    fig3 = plt.figure(2)
    fig4 = plt.figure(3)

    # Event loop for the GUI
    while True:
        event, values = main_window.Read(timeout=25)

        ### Menu bar events ###

        # Open the vgosDB
        if event == "Open session":

            new_dir = askdirectory(initialdir="data/sessions")
            if new_dir != dir and new_dir:
                # Tell the user that we are loading data
                main_window["loading_text"].update(value="Loading...")
                main_window.set_title(f"Quasar Viewer - Loading...")
                main_window.refresh()

                # Check if it is a ABCD session or an SX session
                is_abcd = ("Observables" in os.listdir(f"{new_dir}/")) and (
                    "QualityCode_bS.nc" not in os.listdir(f"{new_dir}/Observables/"))

                # Load data (takes time)
                try:
                    datapoints = DataWrapper(find_datapoints(new_dir, is_abcd=is_abcd))
                except:
                    sg.Popup("Something went wrong! Please select a valid vgosDB directory.",
                             icon="images/favicon.ico")
                    main_window["loading_text"].update(value="")
                    main_window.set_title(f"Quasar Viewer")
                    main_window.refresh()
                    continue

                # Update static variables
                dir = new_dir
                source = None
                source_dict = datapoints.get_source_dict()
                highlights = []
                
                # Reset/update GUI
                main_window["stations_table"].update([])
                main_window["sources_table"].update(update_sources_table(source_dict))
                main_window.set_title(f"Quasar Viewer - {new_dir.split('/')[-1]}")
                main_window["loading_text"].update(value="")
                
                main_window["A_band"].update(visible=is_abcd)
                main_window["B_band"].update(visible=is_abcd)
                main_window["C_band"].update(visible=is_abcd)
                main_window["D_band"].update(visible=is_abcd)
                main_window["S_band"].update(visible=not is_abcd)
                main_window["X_band"].update(visible=not is_abcd)

                fig1.clf()
                fig2.clf()
                fig3.clf()
                fig4.clf()
                draw_fig(main_window["fig1"].TKCanvas, fig1, main_window["toolbar1"].TKCanvas)
                draw_fig(main_window["fig2"].TKCanvas, fig2, main_window["toolbar2"].TKCanvas)
                draw_fig(main_window["fig3"].TKCanvas, fig3, main_window["toolbar3"].TKCanvas)
                draw_fig(main_window["fig4"].TKCanvas, fig4, main_window["toolbar4"].TKCanvas)

                main_window.refresh()

        # Open fits file
        if event == "Open fits":
            new_dir = askopenfilename(initialdir="data/fits")

            # Tell the user that we are loading data
            main_window["loading_text"].update(value="Loading...")
            main_window.refresh()

            try:
                source_model = SourceModelWrapper(new_dir)
            except:
                sg.Popup("Something went wrong! Please select a valid fits file.",
                             icon="images/favicon.ico")

            main_window["loading_text"].update(value="")
            main_window.refresh()

            # Re-plot with new fits file
            main_window.write_event_value("plot", True)

        # Save the stations info config
        if event == "Save configuration":
            station_information.to_csv(
                "data/derived/stations.csv", index=False)
            saved_station_information = station_information.copy(deep=True)

        # Restore old stations info config
        if event == "Restore":
            a = sg.popup_yes_no(
                "Restoring will remove all configurations set. Do you wish to continue?",
                icon="images/favicon.ico")
            if a == "Yes":
                find_stations()
                station_information = pd.read_csv("data/derived/stations.csv")
                saved_station_information = station_information.copy(deep=True)
                new_table = update_station_table(
                    station_information, source_dict[source]["stations"],
                    highlights, band)
                main_window["stations_table"].update(new_table)
                main_window.write_event_value("plot", True)
                main_window.refresh()

        # Display about info
        if event == "About...":
            sg.Popup("About info",
                     icon="images/favicon.ico")

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

        ### Source selection events ###

        # Source selected
        if event[0] == "sources_table" and event[1] == "+CLICKED+":
            click_row, click_col = event[2]

            # Unusable clicks
            if click_row == None or click_col == None or click_col == -1:
                continue

            # Clicking when no data is in the table should do nothing
            elif all(not e for e in main_window["sources_table"].get()):
                continue

            elif click_row == -1:

                reverse = sort_source_reverse[click_col]

                # Sort by selected
                if click_col == 0:
                    source_dict = dict(sorted(source_dict.items(
                    ), key=lambda source: source[0], reverse=reverse))

                # Sort by name
                if click_col == 1:
                    source_dict = dict(sorted(source_dict.items(
                    ),key=lambda source: source[1]["observations"], reverse=reverse))

                reverse = not reverse
                sort_source_reverse = [False, True]
                sort_source_reverse[click_col] = reverse
                main_window["sources_table"].update(update_sources_table(source_dict))
                main_window.refresh()

            # Update the stations table
            else:
                highlights = []
                source = main_window["sources_table"].get()[click_row][0]
                new_table = update_station_table(
                    station_information, source_dict[source]["stations"],
                    highlights, band)
                main_window["stations_table"].update(new_table)
                main_window.write_event_value("plot", True)
                main_window.refresh()
                
        ### Band selection event ###
        
        if re.search("[A-DSX]_band",str(event)):
            band = ["A","B","C","D","S","X"].index(event.split("_")[0])

            # Update GUI (if table is set)
            if not all(not e for e in main_window["stations_table"].get()):
                new_table = update_station_table(
                    station_information, source_dict[source]["stations"],
                    highlights, band)
                main_window["stations_table"].update(new_table)
                main_window.write_event_value("plot", True)
                main_window.refresh()

        ### Station selection events ###

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
                    source_dict[source]["stations"] = dict(sorted(source_dict[source]["stations"].items(
                    ), key=lambda stat: station_information.loc[station_information["name"] == stat[0]]["selected"].iloc[0], reverse=reverse))

                # Sort by name
                if click_col == 1:
                    source_dict[source]["stations"] = dict(sorted(
                        source_dict[source]["stations"].items(), key=lambda stat: stat[0], reverse=reverse))

                # Sort by observations
                if click_col == 2:
                    source_dict[source]["stations"] = dict(sorted(
                        source_dict[source]["stations"].items(), key=lambda stat: int(stat[1]), reverse=reverse))

                # Sort by SEFD
                if click_col == 3:
                    selected_band = chr(65+click_col-3)
                    col_name = f'{selected_band}_SEFD'
                    source_dict[source]["stations"] = dict(sorted(source_dict[source]["stations"].items(), key=lambda stat: float(
                        station_information.loc[station_information["name"] == stat[0]][col_name].iloc[0]), reverse=reverse))

                # Sort by highlight
                if click_col == 4:
                    source_dict[source]["stations"] = dict(sorted(source_dict[source]["stations"].items(),
                                                                  key=lambda stat: stat[0] in highlights, reverse=reverse))

                # Update list
                sort_stat_reverse = [True, False, True, True, True]
                sort_stat_reverse[click_col] = not reverse

                # Update GUI
                new_table = update_station_table(
                    station_information, source_dict[source]["stations"],
                     highlights, band)
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
                new_table = update_station_table(
                    station_information, source_dict[source]["stations"],
                     highlights, band)
                main_window["stations_table"].update(new_table)
                main_window.write_event_value("plot", True)
                main_window.refresh()

            # Edit SEFD values
            elif click_col == 3:
                # Warn when changing S and X band SEFDs
                if band in [4,5]:
                    sg.Popup(f"You cannot change the SEFD value of the {['S','X'][band-4]} band!",
                            icon="images/favicon.ico")
                    continue

                # Get stats of the selected cell
                selected_station = main_window["stations_table"].get()[click_row][1]
                selected_band = ["A","B","C","D","S","X"][band]
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
                            station_information, source_dict[source]["stations"],
                            highlights, band)
                        main_window["stations_table"].update(new_table)
                        main_window.write_event_value("plot", True)
                        main_window.refresh()

                        # Close popup
                        edit_popup.close()
                    break

            # Select/deselect highlight
            elif click_col == 4:
                # Update selection
                selected_station = main_window["stations_table"].get()[click_row][1]

                if selected_station in highlights:
                    highlights.remove(selected_station)
                else:
                    # Check maximum two highlights
                    if len(highlights) > 1:
                        sg.Popup("You can only select two highlights!",
                                icon="images/favicon.ico")
                        continue
                    highlights.append(selected_station)

                # Update GUI
                new_table = update_station_table(station_information, source_dict[source]["stations"],
                                                 highlights, band)
                main_window["stations_table"].update(new_table)
                main_window.write_event_value("plot", True)
                main_window.refresh()

        ### Debug event ###

        if event == "set_scale":
            source_model.scale = float(values["scale"])
            main_window.write_event_value("plot", True)

        if event == "fit_SEFD":
            least_square_fit(source, source_model, station_information, datapoints, band, ignored_stations)

            # Update GUI
            new_table = update_station_table(
                station_information, source_dict[source]["stations"],
                highlights, band)
            main_window["stations_table"].update(new_table)
            main_window.write_event_value("plot", True)
            main_window.refresh()

        if event == "gauss":
            if source_model:
                sm = source_model.gauss_list[0]
                sg.Popup(f"a = {sm.a}\nb = {sm.b}\nA = {sm.amp}\nt = {sm.theta}\nx0 = {sm.x0}\ny0 = {sm.y0}")

        ### Plot event ###

        if event == "plot":
            # Check that user has selected a folder
            if not dir:
                continue

           # Check that user has selected a source
            if not source:
                continue

            # Check that user has selected a valid source
            if source not in source_dict:
                continue

            # Find which band the user has selected, selected station will have
            # a value of True, all others False
            band = [values['A_band'], values['B_band'],
                    values['C_band'], values['D_band'],
                    values['S_band'], values['X_band']].index(True)

            # Check that the selected band is in the currently visible list
            if (is_abcd and band in [4,5]) or (not is_abcd and band in [0,1,2,3]):
                continue

            # Ignore the stations that were unselected in the GUI
            ignored_stations = station_information.loc[station_information["selected"] == 0]["name"].to_list()

            # Plot
            plot_source(
                source, datapoints.get_df(), station_information, source_model=source_model, ignored_stations=ignored_stations, bands=band, highlighted_stations=highlights)

            # Display plots in canvases
            draw_fig(main_window["fig1"].TKCanvas, fig1, main_window["toolbar1"].TKCanvas)
            draw_fig(main_window["fig2"].TKCanvas, fig2, main_window["toolbar2"].TKCanvas)
            draw_fig(main_window["fig3"].TKCanvas, fig3, main_window["toolbar3"].TKCanvas)
            draw_fig(main_window["fig4"].TKCanvas, fig4, main_window["toolbar4"].TKCanvas)


