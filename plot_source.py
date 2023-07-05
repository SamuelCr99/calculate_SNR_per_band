import matplotlib.pyplot as plt
# from find_station_baseline_match import find_station_baseline_match
# from to_uv import to_uv
import pandas as pd

# def plot_source(source,baseline):

#     baseline_matches = find_station_baseline_match(source,baseline)

#     coords_u = []
#     coords_v = []
#     for point in baseline_matches:
#         u,v = to_uv(point)
#         coords_u.append(u)
#         coords_v.append(v)
    
#     plt.plot(coords_u,coords_v)

# if __name__ == '__main__':
#     source = "1803+784"
#     baseline = "GGAO12M/ISHIOKA"
#     plot_source(source,baseline)


df = pd.read_csv('ggao12m_baseline_match.txt')
plt.plot(df['u'],df['v'], 'o')
plt.xlabel('u')
plt.ylabel('v')
plt.show()