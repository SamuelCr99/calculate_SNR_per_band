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
        parser = argparse.ArgumentParser(prog='SEFD Estimation Tool', description='Used for plotting sources in u-v space and estimate the SEFD values of the stations during the session.')

        subparsers = parser.add_subparsers(dest="mode")
        subparsers.metavar = ""
        plot_parser = subparsers.add_parser('plot', help="Plot u,v coordinates of a source")
        lsf_parser = subparsers.add_parser('lsf', help="Find the SEFD values of the stations using least square fit")

        plot_parser.add_argument('session_folder', type=str, help="Relative or absolute path to the session folder")
        plot_parser.add_argument('source', type=str, help="Source name or comma separated list of sources")
        plot_parser.add_argument('--band', type=str, help="Band name or comma separated list of bands")
        plot_parser.add_argument('--highlighted_station', type=str, help="Comma separated list of stations to highlight", default=[])
        plot_parser.add_argument('--ignored_stations', type=str, help="Comma separated list of stations to ignore", default=[])
        plot_parser.add_argument('--fits_file', type=str, help="Relative or absolute path to the fits file")

        lsf_parser.add_argument('session_folder', type=str, help="Relative or absolute path to the session folder")
        lsf_parser.add_argument('fits_file', type=str, help="Relative or absolute path to the fits file")
        lsf_parser.add_argument('--source', type=str, help="Source name or comma separated list of sources")
        lsf_parser.add_argument('--band', type=str, help="Band name or comma separated list of bands")
        lsf_parser.add_argument('--ignored_stations', type=str, help="Comma separated list of stations to ignore", default=[])

        args = parser.parse_args()

        if args.mode == "plot":

            if type(args.highlighted_station) == str:
                args.highlighted_stations = args.highlighted_station.split(",")

            if type(args.ignored_stations) == str:
                args.ignored_stations = args.ignored_stations.split(",")

            if type(args.band) == str:
                args.band = args.band.split(",")

            data = DataWrapper(args.session_folder)
            config = StationsConfigWrapper()
            plot_source(args.source, data.get(sources=args.source, bands=args.band, ignored_stations=args.ignored_stations), config, highlighted_stations=args.highlighted_station)
            plt.show()

        elif args.mode == "lsf":
            if args.fits_folder == None: raise ValueError("No source model folder given, this is needed for least square fit")

            if type(args.ignored_stations) == str:
                ignored_stations = args.ignored_stations.split(",")

            data = DataWrapper(args.session_folder)
            config = StationsConfigWrapper()
            source_model = SourceModelWrapper(args.fits_folder)
            least_square_fit(data.get(source=args.source, bands=args.band, ignored_stations=ignored_stations), source_model, config)

        else:
            raise ValueError("Unknown mode, please select plot or lsf")