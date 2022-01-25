def keep_correct_month(df_taxi_data, month):
    '''
    Preprocess TLC taxi trip data: Only keep rows that contain the correct month.
    ----------------------------------------------------------------------------
    INPUTS:
    
    df_taxi_data (Pandas dataframe): This data mus have been preprocessed using preprocess_data().
    month   (str)                   : Month to be kept.
    
    OUTPUT:
    
    df_cleansed (Pandas dataframe ): Cleansed dataframe whose rows only come from the specified month.
    '''
    
    # Remember initial number of trips.
    n_rows_total = df_taxi_data.shape[0]
    
    # Convert to string to make string parsing possible.
    month = "-" + str(month) + "-"
    
    # Remove wrong month form pick-ups and rop-offs, i.e., only keep those of the specified month.
    # The or "|" is necessary to include fringe cases on new month's.
    df_taxi_data = df_taxi_data[df_taxi_data['pickup_datetime'].str.contains(month) & df_taxi_data['dropoff_datetime'].str.contains(month)]
    
    # Show preprocessing result
    print('About {:.4f}% of the entire data could not be used because they contained the wrong month.'.format(100*(1-df_taxi_data.shape[0]/n_rows_total)))
    
    return df_taxi_data
