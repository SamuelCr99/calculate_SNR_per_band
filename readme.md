# SEFD Estimation Tool

## Description
GUI for finding optimal SEFD values based on VGOS DB sessions and source images. 
The program was developed at NVI Inc. by Filip Herbertsson and Samuel Collier 
Ryder during a summer internship in 2023.


![](images/gui_image.png "Image of the GUI")


## Approach

## How to install

To install the program, you need to clone the GitHub repository and install the 
required libraries. This can be done by running the following commands in the terminal:

```bash
$ git clone https://github.com/SamuelCr99/VLBI_baseline_movement_plotter.git
$ pip install -r requirements.txt
```

## How to use
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

#### Save changes made to the stations
To save the changes made to the stations click the "Save" button under the
"Configuration" tab.

#### Restore changes to latest saved file 
To restore changes to latest save file click the "Restore to saved" button under
the "Configuration" tab.

#### Restore changes to original file 
To restore all SEFD values to their original state, click the "Delete" button under
the "Configuration" tab.

## Known issues
* Program doesn't work