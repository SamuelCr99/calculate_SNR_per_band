import sys
import argparse
import matplotlib.pyplot as plt
from utility.gui.gui import run_gui
from utility.wrappers.data_wrapper import DataWrapper
from utility.plot.plot_source import plot_source
from utility.calc.least_square_fit import least_square_fit, model_source_map
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

        prepare_parser = subparsers.add_parser('prepare', help="prepare the session data for analysis")
        plot_parser = subparsers.add_parser('plot', help="plot flux density in u-v coordinates of a source")
        lsf_parser = subparsers.add_parser('lsf', help="find the SEFD values of the stations using least-squares-fit")

        prepare_parser.add_argument('type', type=str, help="type of information to process, either 'band-data', 'SEFD' or 'all'")
        prepare_parser.add_argument('session_dir', type=str, help="relative or absolute path to the session folder")
        prepare_parser.add_argument('--save_dir', type=str, help="relative or absolute path to save the prepared data to", default="")

        plot_parser.add_argument('source', type=str, help="source name or comma separated list of sources")
        plot_parser.add_argument('--bands', type=str, help="band name or comma separated list of bands", default=[])
        plot_parser.add_argument('--ignored_bands', type=str, help="band name or comma separated list of bands to ignore", default=[])
        plot_parser.add_argument('--highlighted_stations', type=str, help="comma separated list of stations to highlight", default=[])
        plot_parser.add_argument('--stations', type=str, help="comma separated list of stations", default=[])
        plot_parser.add_argument('--ignored_stations', type=str, help="comma separated list of stations to ignore", default=[])
        plot_parser.add_argument('--baselines', type=str, help="comma separated list of baselines to show", default=[])
        plot_parser.add_argument('--ignored_baselines', type=str, help="comma separated list of baselines to ignore", default=[])
        plot_parser.add_argument('--fits_file', type=str, help="relative or absolute path to the fits file")
        plot_parser.add_argument('--model', type=str, help="which model to use for prediction. Can be either 'img' or 'raw', or unspecified", default="img")
        plot_parser.add_argument('--scale_uv', type=float, help="the scale used to adjust the model in the u-v plane", default=1)
        plot_parser.add_argument('--scale_flux', type=float, help="the scale used to adjust the model in the flux density", default=1)
        plot_parser.add_argument('--data', type=str, help="relative or absolute path to the data file to use. Only needed if other than default", default="")
        plot_parser.add_argument('--config', type=str, help="relative or absolute path to the config file to use. Only needed if other than default", default="")
        plot_parser.add_argument('--save_dir', type=str, help="relative or absolute path to save plots to", default="")

        lsf_parser.add_argument('--fits_file', type=str, help="relative or absolute path to the fits file. Mandatory to have one of fits_file or fits_folder")
        lsf_parser.add_argument('--fits_folder', type=str, help="relative or absolute path to the directory with fits files. Mandatory to have one of fits_file or fits_folder")
        lsf_parser.add_argument('--model', type=str, help="which model to use for prediction. Can be either 'img' or 'raw', or unspecified", default="img")
        lsf_parser.add_argument('--scale_uv', type=float, help="the scale used to adjust the model in the u-v plane", default=1)
        lsf_parser.add_argument('--scale_flux', type=float, help="the scale used to adjust the model in the flux density", default=1)
        lsf_parser.add_argument('--sources', type=str, help="source name or comma separated list of sources", default=[])
        lsf_parser.add_argument('--ignored_sources', type=str, help="source name or comma separated list of sources to ignore", default=[])
        lsf_parser.add_argument('--bands', type=str, help="band name or comma separated list of bands", default=[])
        lsf_parser.add_argument('--ignored_bands', type=str, help="band name or comma separated list of bands to ignore", default=[])
        lsf_parser.add_argument('--stations', type=str, help="comma separated list of stations to include", default=[])
        lsf_parser.add_argument('--ignored_stations', type=str, help="comma separated list of stations to ignore", default=[])
        lsf_parser.add_argument('--baselines', type=str, help="comma separated list of stations to include", default=[])
        lsf_parser.add_argument('--ignored_baselines', type=str, help="comma separated list of stations to ignore", default=[])
        lsf_parser.add_argument('--data', type=str, help="relative or absolute path to the data file to use. Only needed if other than default", default="")
        lsf_parser.add_argument('--config', type=str, help="relative or absolute path to the config file to use. Only needed if other than default", default="")

        args = parser.parse_args()

        if args.mode == "plot" or args.mode == "lsf":
            split_attribute("stations")
            split_attribute("ignored_stations")
            split_attribute("baselines")
            split_attribute("ignored_baselines")
            split_attribute("bands")
            split_attribute("ignored_bands")

        if args.mode == "prepare":
            if args.type.lower() == "band-data" or args.type.lower() == "all":
                data = DataWrapper(args.session_dir)
                
                session_dir = args.session_dir
                if session_dir[-1] != '/': session_dir += '/'
                session_name = session_dir.split("/")[-2]

                data.save(session_name, args.save_dir)
            
            if args.type.lower() == "sefd" or args.type.lower() == "all":
                dir = args.save_dir
                if dir:
                    if dir[-1] != '/': dir += '/'
                    path = f"{dir}config.csv"
                else:
                    path = ""
                config = StationsConfigWrapper(args.session_dir, path)
                config.delete()

        elif args.mode == "plot":

            split_attribute("highlighted_stations")

            data = DataWrapper(args.data)
            config = StationsConfigWrapper(args.config)
            
            source_model = SourceModelWrapper(args.fits_file, model=args.model, scale_uv=args.scale_uv, scale_flux=args.scale_flux) if args.fits_file else None
            plot_source(args.source, data.get(sources=args.source, 
                                               bands=args.bands, ignored_bands=args.ignored_bands, 
                                               stations=args.stations, ignored_stations=args.ignored_stations, 
                                               baselines=args.baselines, ignored_baselines=args.ignored_baselines), 
                        config, source_model=source_model, highlighted_stations=args.highlighted_stations)
            if args.save_dir:
                plt.figure(0).savefig(f"{args.save_dir}/flux_density_mes_{args.source}_{''.join(args.bands)}.png")
                plt.figure(3).savefig(f"{args.save_dir}/distance_{args.source}_{''.join(args.bands)}.png")
                if args.fits_file:
                    plt.figure(1).savefig(f"{args.save_dir}/flux_density_pred_{args.source}_{''.join(args.bands)}_fits.png")
                    plt.figure(2).savefig(f"{args.save_dir}/flux_density_ratio{args.source}_{''.join(args.bands)}_fits.png")
            else: 
                plt.show()

        elif args.mode == "lsf":
            if args.fits_file == None and args.fits_folder == None:
                raise ValueError("Either fits_file or fits_folder must be specified")
            
            if args.fits_file != None and args.fits_folder != None:
                raise ValueError("Both fits_file and fits_folder cannot be specified")

            split_attribute("sources")
            split_attribute("ignored_sources")

            if type(args.ignored_stations) == str:
                ignored_stations = args.ignored_stations.split(",")

            data = DataWrapper(args.session_folder)
            config = StationsConfigWrapper()

            if args.fits_file:
                source_model = SourceModelWrapper(args.fits_file, model=args.model, scale_uv=args.scale_uv, scale_flux=args.scale_flux)

            elif args.fits_folder:
                source_model = model_source_map(data.get(sources=args.sources, bands=args.bands, ignored_stations=args.ignored_stations), args.fits_folder)
            
            least_square_fit(data.get(sources=args.sources, bands=args.bands, ignored_stations=args.ignored_stations), source_model, config)
            config.save(args.save_dir)

        else:
            raise ValueError("Unknown mode, please select plot or lsf")