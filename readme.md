# Source model evaluation tool

## Description
Application for finding optimal SEFD values based on VGOS DB sessions and source images. 
The program was developed at NVI Inc. by Filip Herbertsson and Samuel Collier 
Ryder during a summer internship in 2023.


![](images/gui_image.png "Image of the GUI")


## Approach

## How to install

To install the program, you need to clone the GitHub repository and install the 
required libraries. This can be done by running the following commands in the terminal:

```bash
$ git clone https://github.com/SamuelCr99/source_model_evaluation.git
$ pip install -r requirements.txt
```

## How to use the GUI
To run the program, run the main.py file: 

```bash
$ python3 main.py
```

Make sure this is done from the root directory of the repository, if not the program will not be able to find the required files.

### Load data

#### Load session 
To load a session into the gui, click on the "Load session" button under the "File"
tab. This session folder should be a VGOS DB.  

#### Load fits file
To load a fits into the gui, click on the "Load fits" button under the "File"
tab. 

### Plotting
After loading a session, click on one of the sources to plot information from the
source. To change which band is plotted simply click on one of the four radio 
buttons under band. There will be 4 different plots. 

1. The u, v coordinates and flux density of the source based on data from the session
folder. 
2. The u, v coordinates and flux density of the source based on data from the fits
file.
3. The ratio between the flux density of the source based on data from the session
folder and the flux density of the source based on data from the fits file.  
4. Flux density to the distance from the center of the source based on data from the
session folder.

#### Adjusting plot
There are a number of ways of adjusting the plot. 


- Adjust which stations are plotted by clicking the "Sel." column in the Stations
table.
- Adjust which station are highlighted by clicking the "★" column. This will cause
the points from that station to be highlighted with a star. If two stations are 
highlighted, the points where both stations are present will be highlighted.   
- Adjust the SEFD value of a station by clicking the "SEFD" column. This will change
the flux density for the points from that station. 

#### Setting optimal SEFD values automatically 
To find the optimal SEFD values for each station for that session and band click 
the "Fit SEFD" button. 

### Using the configuration settings

Changes made to the SEFD values for each station and band can be saved, so that they are consistent when using the program at different times.

* To save the changes made to the stations click the "Save" button under the
"Configuration" tab.

* To restore changes to latest save file click the "Restore to saved" button under
the "Configuration" tab.

* To restore all SEFD values to their original state, click the "Delete" button under
the "Configuration" tab.

## How to use the script mode

The script mode uses three commands:

* `prepare`: Prepares the band-data from a vgos session, as well as prepare a config-file containing the SEFD-values for all the stations present in the session.
* `plot`: Uses the prepared data and config file to generate plots for specific sources. There are four kinds of plots that can be created, depending on what other flags are provided:
    * A plot of the flux density, calculated from the measured SNR and the SEFD values of the stations.
    * A plot of the flux density, as predicted by a model.
    * A plot of the ratio between the predicted and the measured flux density.
    * A plot of the measured flux density as a function of the distance from the center of the source.
* `lsf`: Uses the prepared data and the SEFD config, as well as a model of a source provided with a FITS-file, to do a least-squares-fit of the SEFD values for each station, and updates the config file accordingly.

More information of which variables and flags are available for the different commands can be found by using

```bash
$ python3 main.py <command> --help
```

### Preparing a vgos session

In order to prepare the band-data from a session, the following command should be run

```bash
$ python3 main.py prepare band-data <session_dir>
```

If you want to prepare the config file containing SEFD values instead, you use

```bash
$ python3 main.py prepare sefd <session_dir>
```

In order to run the `plot` and the `lsf` command, you will need both files. Thus, you can prepare both using

```bash
$ python3 main.py prepare all <session_dir>
```

By default, the data is saved in the directory `data/derived`. If you want to save the data somewhere else for processing, you can use the `--save_dir` flag to specify the directory. The files are always named `datapoints.csv` and `config.csv`, and are CSV files.

### Plotting

One of the main uses of this utility is the ability to make plots of sources from data obtained in vgos (or S-X) sessions. After having prepared the session, this can be done by running the command

```bash
$ python3 main.py plot <source>
```

where `source` is the B1950 name of the source. The available sources can be found by checking the list in the GUI, or by looking in the data file that was prepared.

Different flags can adjust which observations should be included. This is useful if you for example want to look at a single band, or if you want to exclude a specific station. The flags are
* `--bands` to only look at specific bands
* `--ignored_bands` to exclude specific bands
* `--stations` to only look at specific stations
* `--ignored_stations` to exclude specific stations
* `--stations` to only look at specific stations
* `--ignored_stations` to exclude specific stations
* `--baselines` to only look at specific baselines
* `--ignored_baselines` to exclude specific baselines

An example of this would be running the following command

```bash
$ python3 main.py plot 1803+784 --bands A --ignored_stations KOKEE12M,ISHIOKA
```

which should plot the source __1803+784__ in the __A__ band, ignoring data obtained by stations __KOKEE12M__ and __ISHIOKA__.  

If you chose to prepare the data and config files in a different location than the default, you can specify the paths to these files using the `--data` and `--config` flags respectively. This would be the full paths, not only the directory.

Plots can also be saved instead of shown. This happens if you specify a `--save_dir`.

### Least-squares-fit of SEFD values



## Known issues and limitations
* Scaling of flux density between predicted and measured is inconsistent. 
