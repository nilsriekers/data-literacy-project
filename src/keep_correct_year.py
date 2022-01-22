def keep_correct_year(df_taxi_data, year):
    '''
    Preprocess TLC taxi trip data: Only keep rows that contain the correct year.
    ----------------------------------------------------------------------------
    INPUTS:
    
    df_taxi_data (Pandas dataframe): This data mus have been preprocessed using preprocess_data().
    year   (int)                   : Year to be kept.
    
    OUTPUT:
    
    df_cleansed (Pandas dataframe ): Cleansed dataframe whose rows only come from the specified year.
    '''
    
    # Remember initial number of trips.
    n_rows_total = df_taxi_data.shape[0]
    
    # Convert to string to make string parsing possible.
    year = str(year)
    
    # Remove wrong years form pick-ups and rop-offs, i.e., only keep those of the specified year.
    # The or "|" is necessary to include fringe cases on new year's.
    df_taxi_data = df_taxi_data[df_taxi_data['pickup_datetime'].str.contains(year) | df_taxi_data['dropoff_datetime'].str.contains(year)]
    
    # Show preprocessing result
    print('About {:.4f}% of the entire data could not be used because they contained the wrong year.'.format(100*(1-df_taxi_data.shape[0]/n_rows_total)))
    
    return df_taxi_data
