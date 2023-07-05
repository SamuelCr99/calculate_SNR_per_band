import netCDF4 as nc

folder_names = ['GGAO12M', 'ISHIOKA', 'KOKEE12M', 'MACGO12M', 'ONSA13NE', 
                'ONSA13SW', 'RAEGYEB', 'WESTFORD', 'WETTZ13S']

lines_to_write = []

for folder_name in folder_names:
    file_path = f'data/{folder_name}/AzEl_V001.nc'

    with nc.Dataset(file_path, 'r') as ds:
        azimuth = ds['AzTheo']
        elevation = ds['ElTheo']

        min_azimuth = 100 # Arbitrary large number
        min_elevation = 100 # Arbitrary large number
        max_azimuth = 0
        max_elevation = 0

        for i in range(0, len(azimuth)):
            if azimuth[i][0] > max_azimuth:
                max_azimuth = azimuth[i][0]
            if azimuth[i][0] < min_azimuth:
                min_azimuth = azimuth[i][0]
            if elevation[i][0] > max_elevation:
                max_elevation = elevation[i][0]
            if elevation[i][0] < min_elevation:
                min_elevation = elevation[i][0]

        lines_to_write.append(f'{folder_name} min azimuth: {min_azimuth}')
        lines_to_write.append(f'{folder_name} max azimuth: {max_azimuth}')
        lines_to_write.append(f'{folder_name} min elevation: {min_elevation}')
        lines_to_write.append(f'{folder_name} max elevation: {max_elevation}')
        lines_to_write.append('----------------')

with open('az_el_max_min.txt', 'w') as f:
    f.write('\n'.join(lines_to_write))