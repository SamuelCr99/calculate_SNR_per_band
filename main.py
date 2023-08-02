import sys
import argparse
import matplotlib.pyplot as plt
from utility.gui.gui import run_gui
from utility.wrappers.data_wrapper import DataWrapper
from utility.plot.plot_source import plot_source
from utility.calc.least_square_fit import least_square_fit
from utility.wrappers.stations_config_wrapper import StationsConfigWrapper
from utility.wrappers.source_model_wrapper import SourceModelWrapper


if __name__ == "__main__":
    # If no arguments are given, run the GUI
    if len(sys.argv) == 1:
        run_gui()

    else:
        # def plot_source(source, data, config, source_model = None, highlighted_stations = []):
        parser = argparse.ArgumentParser(prog='Plot source', description='')
        parser.add_argument('mode', type=str)
        parser.add_argument('session_folder', type=str)
        parser.add_argument('--source', type=str)
        parser.add_argument('--band', type=str)
        parser.add_argument('--highlighted_station', type=str, default="")
        parser.add_argument('--ignored_stations', type=str, default="")
        parser.add_argument('--fits_folder', type=str, default="")
        args = parser.parse_args()

        if args.mode == "plot":
            if type(args.highlighted_station) == str:
                highlighted_stations = args.highlighted_station.split(",")

            if type(args.ignored_stations) == str:
                ignored_stations = args.ignored_stations.split(",")

            data = DataWrapper(args.session_folder)
            config = StationsConfigWrapper()
            plot_source(args.source, data.get(sources=args.source, bands=args.band, ignored_stations=ignored_stations), config, highlighted_stations=highlighted_stations)
            plt.show()

        elif args.mode == "least_square_fit":
            if args.fits_folder == None: raise ValueError("No source model folder given, this is needed for least square fit")

            if type(args.ignored_stations) == str:
                ignored_stations = args.ignored_stations.split(",")

            data = DataWrapper(args.session_folder)
            config = StationsConfigWrapper()
            source_model = SourceModelWrapper(args.fits_folder)
            least_square_fit(data.get(source=args.source, bands=args.band, ignored_stations=ignored_stations), source_model, config)

        else:
            raise ValueError("Unknown mode, please select plot or least_square fit")