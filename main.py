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

        prepare_parser = subparsers.add_parser('prepare', help="prepare the session data for analysis")
        list_parser = subparsers.add_parser('list', help="list quantities from a session")
        plot_parser = subparsers.add_parser('plot', help="plot flux density in u-v coordinates of a source")
        lsf_parser = subparsers.add_parser('lsf', help="find the SEFD values of the stations using least-squares-fit")

        prepare_parser.add_argument('type', type=str, help="type of information to process, either 'band-data', 'SEFD' or 'all'")
        prepare_parser.add_argument('session_dir', type=str, help="relative or absolute path to the session folder")
        prepare_parser.add_argument('--save_dir', type=str, help="relative or absolute path to save the prepared data to", default="")

        list_parser.add_argument('type', type=str, help="type of information to display, either 'sources', 'bands' or 'stations'")
        list_parser.add_argument('--data', type=str, help="relative or absolute path to the data file to use. Only needed if other than default", default="")

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
        plot_parser.add_argument('--scale_flux', type=str, help="the scale used to adjust the model in the flux density, or 'auto'", default=1)
        plot_parser.add_argument('--data', type=str, help="relative or absolute path to the data file to use. Only needed if other than default", default="")
        plot_parser.add_argument('--config', type=str, help="relative or absolute path to the config file to use. Only needed if other than default", default="")
        plot_parser.add_argument('--save_dir', type=str, help="relative or absolute path to save plots to", default="")

        lsf_parser.add_argument('source', type=str, help="source name or comma separated list of sources", default=[])
        lsf_parser.add_argument('--bands', type=str, help="band name or comma separated list of bands", default=[])
        lsf_parser.add_argument('--ignored_bands', type=str, help="band name or comma separated list of bands to ignore", default=[])
        lsf_parser.add_argument('--stations', type=str, help="comma separated list of stations to include", default=[])
        lsf_parser.add_argument('--ignored_stations', type=str, help="comma separated list of stations to ignore", default=[])
        lsf_parser.add_argument('--baselines', type=str, help="comma separated list of stations to include", default=[])
        lsf_parser.add_argument('--ignored_baselines', type=str, help="comma separated list of stations to ignore", default=[])
        lsf_parser.add_argument('fits_file', type=str, help="relative or absolute path to the fits file")
        lsf_parser.add_argument('--model', type=str, help="which model to use for prediction. Can be either 'img' or 'raw', or unspecified", default="img")
        lsf_parser.add_argument('--scale_uv', type=float, help="the scale used to adjust the model in the u-v plane", default=1)
        lsf_parser.add_argument('--scale_flux', type=str, help="the scale used to adjust the model in the flux density, or 'auto'", default=1)
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
                config = StationsConfigWrapper(session_dir=args.session_dir, path=path)
                config.delete()

        elif args.mode == "list":
            data = DataWrapper(args.data)
            
            print_data = []
            if args.type == "sources":
                print_data = data.get_sources()
            elif args.type == "bands":
                print_data = data.get_bands()
            elif args.type == "stations":
                print_data = data.get_stations()

            for elem in print_data:
                print(elem)

        elif args.mode == "plot":

            split_attribute("highlighted_stations")

            data = DataWrapper(args.data)
            data = data.get(sources=args.source,
                            bands=args.bands,
                            ignored_bands=args.ignored_bands,
                            stations=args.stations,
                            ignored_stations=args.ignored_stations, 
                            baselines=args.baselines,
                            ignored_baselines=args.ignored_baselines)
            
            config = StationsConfigWrapper(path=args.config)

            if args.fits_file:
                scale_flux = float(args.scale_flux) if args.scale_flux and args.scale_flux != "auto" else 1
                source_model = SourceModelWrapper(args.fits_file, model=args.model, scale_uv=args.scale_uv, scale_flux=scale_flux)
                if args.scale_flux == "auto": source_model.set_flux_scale(config, data)
            else:
                source_model = None

            plot_source(args.source, data, config, source_model=source_model,
                        highlighted_stations=args.highlighted_stations)
            
            if args.save_dir:
                plt.figure(0).savefig(f"{args.save_dir}/flux_density_mes_{args.source}_{''.join(args.bands)}.png")
                plt.figure(3).savefig(f"{args.save_dir}/distance_{args.source}_{''.join(args.bands)}.png")
                if args.fits_file:
                    plt.figure(1).savefig(f"{args.save_dir}/flux_density_pred_{args.source}_{''.join(args.bands)}_fits.png")
                    plt.figure(2).savefig(f"{args.save_dir}/flux_density_ratio{args.source}_{''.join(args.bands)}_fits.png")
            else: 
                plt.show()

        elif args.mode == "lsf":

            data = DataWrapper(args.data)
            data = data.get(sources=args.source,
                            bands=args.bands,
                            ignored_bands=args.ignored_bands,
                            stations=args.stations,
                            ignored_stations=args.ignored_stations, 
                            baselines=args.baselines,
                            ignored_baselines=args.ignored_baselines)
            
            config = StationsConfigWrapper(path=args.config)

            scale_flux = float(args.scale_flux) if args.scale_flux and args.scale_flux != "auto" else 1
            source_model = SourceModelWrapper(args.fits_file, model=args.model, scale_uv=args.scale_uv, scale_flux=scale_flux)
            if args.scale_flux == "auto": source_model.set_flux_scale(config, data)
            
            least_square_fit(data, source_model, config)
            config.save()

        else:
            raise ValueError("Unknown mode, please select plot or lsf")