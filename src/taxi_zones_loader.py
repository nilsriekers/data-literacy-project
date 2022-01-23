from urllib.error import HTTPError
import pandas as pd

def taxi_zones_loader():
    '''
    Try to download taxi zones meta data from TLC website.
    '''
    
    url = 'https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv'
    try:
        df_zones_info = pd.read_csv(url, low_memory=False)
        # Drop unnecessary column and return resulting dataframe.
        df_zones_info.drop(columns='service_zone', inplace=True)
        return df_zones_info
    except HTTPError:
        print('ERROR: Could not access "{}"!'.format(url))
