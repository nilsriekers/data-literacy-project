import pandas as pd

def temporal_preprocessing(df_taxi_data):
    '''
    Add temporal information to the dataset:
        - Convert columns pickup_datetime, dropoff_datetime to type datetime64[ns].
        - Remove all rows that have negative trip duration.
        - Add column trip_duration       (datetime64[ns]): Duration of each trip in datetime64[ns] format.
        - Add column trip_duration_min   (float)         : Duration of each trip in minutes.
        - Add column pickup_minute       (int, 0 ... 59) : The minute within the hour the passenger was picked up.
        - Add column pickup_hour         (int, 0 ... 23) : The hour of the day in which the passenger was picked up.
        - Add column pickup_day_of_month (int, 1 ... 31) : The day of the month the passenger was picked up.
        - Add column pickup_weekday      (int, 0 ... 6)  : The day of the week the passenger was picket up. Monday=0, ..., Sunday=6. Seven days in total.
    -----------------------------------------------------------------------------------------------------------------------------------------------------
    INPUTS:
    
    df_taxi_data (Pandas dataframe): This data mus have been loaded using load_taxi_data().
    
    OUTPUT:
    
    df_enhanced (Pandas dataframe): Original dataframe with temporal information added.
    '''
    
    # Conversion to datetime64
    df_taxi_data['pickup_datetime'] = pd.to_datetime(df_taxi_data['pickup_datetime'], format='%Y-%m-%d %H:%M:%S')
    df_taxi_data['dropoff_datetime'] = pd.to_datetime(df_taxi_data['dropoff_datetime'], format='%Y-%m-%d %H:%M:%S')
    
    # Calculate trip duration
    df_taxi_data['trip_duration'] = df_taxi_data['dropoff_datetime'] - df_taxi_data['pickup_datetime']
    
    # Trip duration in minutes
    df_taxi_data['trip_duration_minutes'] = df_taxi_data['trip_duration'] / pd.Timedelta(minutes=1)
    
    # Extract month from timestamp
    df_taxi_data['pickup_month'] = df_taxi_data['pickup_datetime'].dt.month
    
    # Extract day of month from timestamp
    df_taxi_data['pickup_day_of_month'] = df_taxi_data['pickup_datetime'].dt.day
    
    # Extract day of week from timestamp => Monday=0, ..., Sunday=6 (i.e., 7 days in total)
    df_taxi_data['pickup_weekday'] = df_taxi_data['pickup_datetime'].dt.dayofweek
    
    # Extract hour from timestamp
    df_taxi_data['pickup_hour'] = df_taxi_data['pickup_datetime'].dt.hour
    
    # Extract minute from timestamp
    df_taxi_data['pickup_minute'] = df_taxi_data['pickup_datetime'].dt.minute
    
    # Remove negative trip duration
    df_taxi_data = df_taxi_data[df_taxi_data['trip_duration_minutes'] > 0]
    
    # DEBUG: Check data types after all conversions.
    #df_taxi_data.info()
    
    return df_taxi_data
