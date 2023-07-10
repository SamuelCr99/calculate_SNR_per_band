import netCDF4 as nc


dir = 'data/sessions/19JUL24XA/'
channel_info = nc.Dataset(f'{dir}Observables/ChannelInfo_bX.nc')

print(channel_info["ChannelFreq"][:])