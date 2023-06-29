import netCDF4 as nc

channelinfo = nc.Dataset('data/Observables/ChannelInfo_bX.nc', 'r')
corrinfo = nc.Dataset('data/Observables/CorrInfo-difx_bX.nc')
quality_code = nc.Dataset('data/Observables/QualityCode_bX.nc')
baseline = nc.Dataset('data/Observables/Baseline.nc')
timeutc = nc.Dataset('data/Observables/TimeUTC.nc')
source = nc. Dataset('data/Observables/Source.nc')
groupdelay = nc.Dataset('data/Observables/GroupDelay_bX.nc')
snr = nc.Dataset('data/Observables/SNR_bX.nc')

lines = []
lines.append(
"""vgosDB_dump_extreme_edition\tv2023Jun29\tSummer Swedes
Data taken from: Space
BEGIN OBSERVATION #1
# YMDHM SECOND SOURCE BASELINE GROUPDELAY-X GROUPDELAYSIG-X SNR-X FRNGERR QUALITYCODE CHANNELFREQ CHANAMPPHASE-X
""")

for i in range(len(channelinfo['ChanAmpPhase'])):
    ymdhm_s = timeutc['YMDHM'][i]
    second_s = timeutc['Second'][i]
    source_s = source['Source'][i]
    baseline_s = baseline['Baseline'][i]
    groupdelay_s = groupdelay['GroupDelay'][i]
    groupdelaysig_s = groupdelay['GroupDelaySig'][i]
    snr_s = snr['SNR'][i]
    frngerr_s = corrinfo['FRNGERR'][i]
    qualitycode_s = quality_code['QualityCode'][i]
    channelfreq_s = channelinfo['ChannelFreq'][i]
    chanampphase_s = channelinfo['ChanAmpPhase'][i]
    vars = [i,ymdhm_s,second_s,source_s,baseline_s,groupdelay_s,groupdelaysig_s,snr_s,frngerr_s,qualitycode_s,channelfreq_s,chanampphase_s]
    lines_i = "    "
    for var in vars:
        if type(var) != list:
            lines_i += " " + str(var)
        else: 
            quit()
            for val in var:
                lines_i += " " + str(val)
    lines.append(lines_i)
    lines.append('\n ----------------------------- \n')


with open('dump.txt', 'w') as file:
    file.write('\n'.join(lines))