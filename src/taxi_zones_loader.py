def taxi_zones_loader():
    '''
    Try to download taxi zones meta data from TLC website.
    '''
    
    url = 'https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv'
    try:
        return pd.read_csv(url, low_memory=False)
    except HTTPError:
        print('ERROR: Could not access "{}"!'.format(url))