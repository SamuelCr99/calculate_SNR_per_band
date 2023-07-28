import pandas as pd

class DataWrapper:

    def __init__(self,df):
        if type(df) == pd.DataFrame:
            self.df = df
        elif type(df) == str:
            self.df = pd.read_csv(df)

    def get_index(self, source="", baseline="", station="", ignored_stations=[]):
        """
        Find all rows in a DataFrame that match a given source and/or baseline

        Gives the indices of the matching rows, excluding the rows that contains one
        of the ignored stations.

        Parameters:
        source(string): The B1950 name of the source to find
        df(DataFrame): A Pandas DataFrame to search through
        baseline(string): The baseline to search for, on the form "name/name"
        ignored_stations(list): A list with the names of the stations to ignore

        Returns:
        A list of indices of rows that match the given source and baseline.
        """
        
        # Find all rows that contain the selected source
        df = self.get_df(source=source, baseline=baseline, station=station, ignored_stations=ignored_stations)

        return df.index.tolist()
    
    def get_df(self, source="", baseline="", station="", ignored_stations=[], copy=False):
        """
        Find all rows in a DataFrame that match a given source and/or baseline

        Gives the indices of the matching rows, excluding the rows that contains one
        of the ignored stations.

        Parameters:
        source(string): The B1950 name of the source to find
        df(DataFrame): A Pandas DataFrame to search through
        baseline(string): The baseline to search for, on the form "name/name"
        ignored_stations(list): A list with the names of the stations to ignore

        Returns:
        A list of indices of rows that match the given source and baseline.
        """
        if copy:
            df = self.df.copy(deep=True)
        else:
            df = self.df
        
        # Find all rows that contain the selected source
        if source:
            df = df.loc[(df.Source == source)]
        
        # Find all rows that contains the specified baseline
        if baseline:
            if type(baseline) == str:
                station1 = baseline.split("/")[0]
                station2 = baseline.split("/")[1]
            if type(baseline) == list:
                station1 = baseline[0]
                station2 = baseline[1]
            
            df = df.loc[((df['Station1'] == station1) & (df['Station2'] == station2)) |
                        ((df['Station1'] == station2) & (df['Station2'] == station1))]

            
        # Find all rows that include the specified station
        if station:
            df = df.loc[(df.Station1 == station) | (df.Station2 == station)] 
        
        # Find all rows that don't contain the stations in ignored_stations
        for station in ignored_stations:
            df = df.loc[(df.Station1 != station) & (df.Station2 != station)]
    
        return df
    
    def get(self, source="", baseline="", station="", ignored_stations=[], copy=False):

        return DataWrapper(self.get_df(source=source, baseline=baseline, station=station, ignored_stations=ignored_stations, copy=copy))

    def get_source_dict(self):
        """
        Creates a dictionary mapping every source to a list of stations that have 
        data for that source. 

        Parameters:
        No parameters

        Returns:
        d (dict): Dictionary mapping every source to a list of stations that have 
        data for that source.

        """
        d = {}
        for _, row in self.df.iterrows():
            source = row['Source']
            station1 = row['Station1']
            station2 = row['Station2']

            if source not in d:
                d[source] = {'stations': {},
                            'observations': 0}

            if station1 not in d[source]['stations']:
                d[source]['stations'][station1] = 0
            d[source]['stations'][station1] += 1

            if station2 not in d[source]['stations']:
                d[source]['stations'][station2] = 0
            d[source]['stations'][station2] += 1

            d[source]['observations'] += 1

        return d
    
    def iterrows(self):
        return self.df.iterrows()