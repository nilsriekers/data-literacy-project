from urllib.error import HTTPError
import pandas as pd

def load_taxi_data(fleets=['yellow'], years=[2021], months=[1]):
    '''
    Load TLC Trip Record Data for New York taxis
    --------------------------------------------
    INPUTS:
    
    fleets (string[]): 'yellow', 'green', 'fhv'
                           List of taxi companies whose data will be retrieved.
                           'fhv' = Uber, Lyft, etc.
    years (int[])    : 2009...2021
                           Array containing all years to be retrieved.
    months (int[])   : 1 ... 12
                           Array containing the months to be retrieved coded as integers.
    
    OUTPUT:
    
    df_trips: pandas dataframe with columns features_common (see list below).
    '''
    url_prefix = 'https://nyc-tlc.s3.amazonaws.com/trip+data/'
    
    # A small subset of features is selected when FHV data is requested.
    if 'fhv' in fleets:
        features_common = ['pickup_datetime', 'dropoff_datetime', 'PULocationID', 'DOLocationID', 'fleet']
        # Empty dataframe
        df_trips = pd.DataFrame(columns=features_common)

        for fleet in fleets:
            for year in years:
                for month in months:
                    # Create file name
                    if month < 10:
                        url_data = fleet + '_tripdata_' + str(year) + '-0' + str(month) + '.csv' # Caution: Leading 0
                    else:
                        url_data = fleet + '_tripdata_' + str(year) + '-' + str(month) + '.csv'
                    # Try to download file
                    try:
                        print('Will download... ' + url_data)
                        df = pd.read_csv(url_prefix + url_data, low_memory=False)
                    except HTTPError:
                        print('ERROR: There is no data available for fleet={}, years={}, months={}!'.format(fleet, years, months))
                        continue
                    # Set Yellow taxi dataframe columns
                    if fleet == 'yellow':
                        # Features that all Yellow fleet data sets have in common
                        features = ['tpep_pickup_datetime', 'tpep_dropoff_datetime', 'PULocationID', 'DOLocationID']
                    # Set Green taxi dataframe columns
                    if fleet == 'green':
                        # Features that all Green fleet data sets have in common
                        features = ['lpep_pickup_datetime', 'lpep_dropoff_datetime', 'PULocationID', 'DOLocationID']
                    # Set FHV dataframe columns
                    if fleet == 'fhv':
                        # Features that all FHV data sets have in common
                        features = ['pickup_datetime', 'dropoff_datetime', 'PULocationID', 'DOLocationID']
                    # Create dataframe => Only use relevant features and drop rest
                    df.drop(columns=df.columns.difference(features), inplace=True)
                    # Add column to identify fleet
                    df['fleet'] = fleet
                    # Standardize pick-up and drop-off columns for all fleets, i.e., rename them
                    df.columns = features_common
                    # Aggregate all dataframes
                    df_trips = pd.concat([df_trips, df], axis=0)
        return df_trips
    # If no FHV: Use large set of features.
    else:
        features_common = ['pickup_datetime', 'dropoff_datetime', 'PULocationID', 'DOLocationID', 'passenger_count', 'trip_distance', 'tip_amount', 'total_amount', 'fleet']
        # Empty dataframe
        df_trips = pd.DataFrame(columns=features_common)
        
        for fleet in fleets:
            for year in years:
                for month in months:
                    # Create file name
                    if month < 10:
                        url_data = fleet + '_tripdata_' + str(year) + '-0' + str(month) + '.csv' # Caution: Leading 0
                    else:
                        url_data = fleet + '_tripdata_' + str(year) + '-' + str(month) + '.csv'
                    # Try to download file
                    try:
                        print('Will download... ' + url_data)
                        df = pd.read_csv(url_prefix + url_data, low_memory=False)
                    except HTTPError:
                        print('ERROR: There is no data available for fleet={}, years={}, months={}!'.format(fleet, years, months))
                        continue
                    # Set Yellow taxi dataframe columns
                    if fleet == 'yellow':
                        # Features that all Yellow fleet data sets have in common
                        features = ['tpep_pickup_datetime', 'tpep_dropoff_datetime', 'PULocationID', 'DOLocationID', 'passenger_count', 'trip_distance', 'tip_amount', 'total_amount']
                    # Set Green taxi dataframe columns
                    if fleet == 'green':
                        # Features that all Green fleet data sets have in common
                        features = ['lpep_pickup_datetime', 'lpep_dropoff_datetime', 'PULocationID', 'DOLocationID', 'passenger_count', 'trip_distance', 'tip_amount', 'total_amount']
                    # Create dataframe => Only use relevant features and drop rest
                    df.drop(columns=df.columns.difference(features), inplace=True)
                    # Add column to identify fleet
                    df['fleet'] = fleet
                    # Standardize pick-up and drop-off columns for all fleets, i.e., rename them
                    df.columns = features_common
                    # Aggregate all dataframes
                    df_trips = pd.concat([df_trips, df], axis=0)
        return df_trips

    '''
    Load TLC Trip Record Data for New York taxis
    --------------------------------------------
    INPUTS:
    
    fleets (string[]): 'yellow', 'green', 'fhv'
                           List of taxi companies whose data will be retrieved.
                           'fhv' = Uber, Lyft, etc.
    years (int[])    : 2009...2021
                           Array containing all years to be retrieved.
    months (int[])   : 1 ... 12
                           Array containing the months to be retrieved coded as integers.
    
    OUTPUT:
    
    df_trips: pandas dataframe with columns features_common (see list below).
    '''
    url_prefix = 'https://nyc-tlc.s3.amazonaws.com/trip+data/'
    features_common = ['pickup_datetime', 'dropoff_datetime', 'PULocationID', 'DOLocationID', 'fleet']
    # Empty dataframe
    df_trips = pd.DataFrame(columns=features_common)
        
    for fleet in fleets:
        for year in years:
            for month in months:
                # Create file name
                if month < 10:
                    url_data = fleet + '_tripdata_' + str(year) + '-0' + str(month) + '.csv' # Caution: Leading 0
                else:
                    url_data = fleet + '_tripdata_' + str(year) + '-' + str(month) + '.csv'
                # Try to download file
                try:
                    print('Will download... ' + url_data) # DEBUG
                    df = pd.read_csv(url_prefix + url_data, low_memory=False)
                except HTTPError:
                    print('ERROR: There is no data available for fleet={}, years={}, months={}!'.format(fleet, years, months))
                    continue
                # Set Yellow taxi dataframe columns
                if fleet == 'yellow':
                    # Features that all Yellow fleet data sets have in common
                    features = ['tpep_pickup_datetime', 'tpep_dropoff_datetime', 'PULocationID', 'DOLocationID']
                # Set Green taxi dataframe columns
                if fleet == 'green':
                    # Features that all Green fleet data sets have in common
                    features = ['lpep_pickup_datetime', 'lpep_dropoff_datetime', 'PULocationID', 'DOLocationID']
                # Set FHV dataframe columns
                if fleet == 'fhv':
                    # Features that all FHV data sets have in common
                    features = ['pickup_datetime', 'dropoff_datetime', 'PULocationID', 'DOLocationID']
                # Create dataframe => Only use relevant features and drop rest
                df.drop(columns=df.columns.difference(features), inplace=True)
                # Add column to identify fleet
                df['fleet'] = fleet
                # Standardize pick-up and drop-off columns for all fleets, i.e., rename them
                df.columns = features_common
                # Aggregate all dataframes
                df_trips = pd.concat([df_trips, df], axis=0)
    return df_trips
