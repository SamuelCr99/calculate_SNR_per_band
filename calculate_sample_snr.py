import numpy as np
import netCDF4 as nc
import math
import time
import sys
import datetime
import argparse


def bytes_to_string(bytes):
    string = ""
    for byte in bytes:
        string += byte.decode("utf-8")
    return string

def time_to_string(time):
    h = time[3]
    m = time[4]
    if h<10: h = f"0{h}"
    if m<10: m = f"0{m}"
    return f"{time[0]}/{time[1]}/{time[2]}-{h}:{m}"

def dump(dir, remove_information):

    channelinfo = nc.Dataset(f'{dir}Observables/ChannelInfo_bX.nc', 'r')
    snr_info = nc.Dataset(f'{dir}Observables/SNR_bX.nc')
    timeutc_info = nc.Dataset(f'{dir}Observables/TimeUTC.nc')
    source_info = nc. Dataset(f'{dir}Observables/Source.nc')
    baseline_info = nc.Dataset(f'{dir}Observables/Baseline.nc')

    chanamp = np.ma.getdata(channelinfo['ChanAmpPhase'])
    snr = np.ma.getdata(snr_info['SNR'])
    timeutc = np.ma.getdata(timeutc_info['YMDHM'])
    second = np.ma.getdata(timeutc_info['Second'])
    source = np.ma.getdata(source_info['Source']).tolist()
    baseline = np.ma.getdata(baseline_info['Baseline']).tolist()

    
    lines = []

    if not remove_information:
        now = datetime.datetime.utcnow()
        header = f"""calculate_SNR_per_band
vgosDB: {dir}
TIMETAG: {now.strftime('%Y/%m/%d %H:%M:%S')} UTC
"""
        lines.append(header)

    lines.append(' \t'.join(["YMDHM","SECOND","SOURCE","BASELINE","SNR_A","SNR_B","SNR_C","SNR_D"]))
    for i in range (len(chanamp)):
        # Time tag, source, baseline, band SNRs

        amp = chanamp[i,:,0]
        phase = chanamp[i,:,1]

        cosines = list(map(lambda a,p: a*math.cos(math.radians(p)),amp,phase))
        sines = list(map(lambda a,p: a*math.sin(math.radians(p)),amp,phase))

        T = math.sqrt(pow(sum(cosines),2)+pow(sum(sines),2))
        A = math.sqrt(pow(sum(cosines[0:8]),2)+pow(sum(sines[0:8]),2))
        B = math.sqrt(pow(sum(cosines[8:16]),2)+pow(sum(sines[8:16]),2))
        C = math.sqrt(pow(sum(cosines[16:24]),2)+pow(sum(sines[16:24]),2))
        D = math.sqrt(pow(sum(cosines[24:32]),2)+pow(sum(sines[24:32]),2))

        # Count the number of data points in each channel which don't equal 0
        M = len(list(filter(lambda x: x != 0, amp)))
        N_A = len(list(filter(lambda x: x != 0, amp[0:8])))
        N_B = len(list(filter(lambda x: x != 0, amp[8:16])))
        N_C = len(list(filter(lambda x: x != 0, amp[16:24])))
        N_D = len(list(filter(lambda x: x != 0, amp[24:32])))

        A_SNR = str(A/T*snr[i]*math.sqrt(M/N_A))
        B_SNR = str(B/T*snr[i]*math.sqrt(M/N_B))
        C_SNR = str(C/T*snr[i]*math.sqrt(M/N_C))
        D_SNR = str(D/T*snr[i]*math.sqrt(M/N_D))

        t = time_to_string(timeutc[i])
        sec = str(second[i])
        s = bytes_to_string(source[i])
        stat1 = bytes_to_string(baseline[i][0])
        stat2 = bytes_to_string(baseline[i][1])
        b = f'{stat1.strip(" ")}/{stat2.strip(" ")}'
        line = " \t".join([t,sec,s,b,A_SNR,B_SNR,C_SNR,D_SNR])
        lines.append(line)

    with open('dump.txt', 'w') as f:
        f.write('\n'.join(lines))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        dump("data/", False)
        quit()

    parser = argparse.ArgumentParser(description='Calculate SNR per band')
    parser.add_argument('dir', type=str)
    parser.add_argument('--remove_information', action='store_true', help='Remove header information')
    args = parser.parse_args()

    dump(args.dir, args.remove_information)