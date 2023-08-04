import sys
import argparse
import matplotlib.pyplot as plt
from utility.gui.gui import run_gui
from utility.wrappers.data_wrapper import DataWrapper
from utility.plot.plot_source import plot_source
from utility.calc.least_square_fit import least_square_fit
from utility.wrappers.stations_config_wrapper import StationsConfigWrapper
from utility.wrappers.source_model_wrapper import SourceModelWrapper

def split_attribute(attr):
    # Splits a string containing some attribute into a list
    attribute = getattr(args,attr)
    if type(attribute) == str:
        setattr(args,attr, attribute.split(","))

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
        plot_parser.add_argument('sources', type=str, help="Source name or comma separated list of sources")
        plot_parser.add_argument('--ignored_sources', type=str, help="Source name or comma separated list of sources to ignore", default=[])
        plot_parser.add_argument('--bands', type=str, help="Band name or comma separated list of bands", default=[])
        plot_parser.add_argument('--ignored_bands', type=str, help="Band name or comma separated list of bands to ignore", default=[])
        plot_parser.add_argument('--highlighted_stations', type=str, help="Comma separated list of stations to highlight", default=[])
        plot_parser.add_argument('--stations', type=str, help="Comma separated list of stations", default=[])
        plot_parser.add_argument('--ignored_stations', type=str, help="Comma separated list of stations to ignore", default=[])
        plot_parser.add_argument('--baselines', type=str, help="Comma separated list of baselines to show", default=[])
        plot_parser.add_argument('--ignored_baselines', type=str, help="Comma separated list of baselines to ignore", default=[])
        plot_parser.add_argument('--fits_file', type=str, help="Relative or absolute path to the fits file")
        plot_parser.add_argument('--save_dir', type=str, help="Relative or absolute path to save plots to")

        lsf_parser.add_argument('session_folder', type=str, help="Relative or absolute path to the session folder")
        lsf_parser.add_argument('fits_file', type=str, help="Relative or absolute path to the fits file")
        lsf_parser.add_argument('--sources', type=str, help="Source name or comma separated list of sources", default=[])
        lsf_parser.add_argument('--ignored_sources', type=str, help="Source name or comma separated list of sources to ignore", default=[])
        lsf_parser.add_argument('--bands', type=str, help="Band name or comma separated list of bands", default=[])
        lsf_parser.add_argument('--ignored_bands', type=str, help="Band name or comma separated list of bands to ignore", default=[])
        lsf_parser.add_argument('--stations', type=str, help="Comma separated list of stations to include", default=[])
        lsf_parser.add_argument('--ignored_stations', type=str, help="Comma separated list of stations to ignore", default=[])
        lsf_parser.add_argument('--baselines', type=str, help="Comma separated list of stations to include", default=[])
        lsf_parser.add_argument('--ignored_baselines', type=str, help="Comma separated list of stations to ignore", default=[])
        lsf_parser.add_argument('--save_dir', type=str, help="Relative or absolute path to save the updates config CSV file to", default="")

        args = parser.parse_args()

        split_attribute("sources")
        split_attribute("ignored_sources")
        split_attribute("stations")
        split_attribute("ignored_stations")
        split_attribute("baselines")
        split_attribute("ignored_baselines")
        split_attribute("bands")
        split_attribute("ignored_bands")

        if args.mode == "plot":

            split_attribute("highlighted_stations")

            data = DataWrapper(args.session_folder)
            config = StationsConfigWrapper()
            plot_source(args.sources, data.get(sources=args.sources, ignored_sources=args.ignored_sources, 
                                               bands=args.bands, ignored_bands=args.ignored_bands, 
                                               stations=args.stations, ignored_stations=args.ignored_stations, 
                                               baselines=args.baselines, ignored_baselines=args.ignored_baselines), 
                        config, highlighted_stations=args.highlighted_stations)
            if args.save_dir:
                plt.figure(0).savefig(f"{args.save_dir}/flux_density_mes_{args.source}_{''.join(args.bands)}.png")
                plt.figure(3).savefig(f"{args.save_dir}/distance_{args.source}_{''.join(args.bands)}.png")
                if args.fits_file:
                    plt.figure(1).savefig(f"{args.save_dir}/flux_density_pred_{args.source}_{''.join(args.bands)}_fits.png")
                    plt.figure(2).savefig(f"{args.save_dir}/flux_density_ratio{args.source}_{''.join(args.bands)}_fits.png")
            else: # Maybe remove this, as showing plots is rarely the desired behavior  
                plt.show()

        elif args.mode == "lsf":
            if args.fits_file == None: raise ValueError("No source model folder given, this is needed for least square fit")

            if type(args.ignored_stations) == str:
                ignored_stations = args.ignored_stations.split(",")

            data = DataWrapper(args.session_folder)
            config = StationsConfigWrapper()
            source_model = SourceModelWrapper(args.fits_file)
            least_square_fit(data.get(source=args.sources, bands=args.bands, ignored_stations=ignored_stations), source_model, config)
            config.save(args.save_dir)

        else:
            raise ValueError("Unknown mode, please select plot or lsf")