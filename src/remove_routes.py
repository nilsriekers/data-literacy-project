def remove_routes(df_taxi_data):
    '''
    IDs 264 and 265 refer to locations outside the city.
    => Rows containing them need to be removed for interpretable results.
    ---------------------------------------------------------------------    
    INPUTS:
    
    df_taxi_data (Pandas dataframe): This data mus have been preprocessed using preprocess_data().
    
    OUTPUT:
    
    df_cleansed (Pandas dataframe ): Cleansed dataframe whose rows only contain pick-up and drop-off IDs within the city.
    '''
    
    # Remember initial number of trips.
    n_rows_total = df_taxi_data.shape[0]
    
    # IDs that refer to locations outside the city.
    idx_outside = [264, 265]
    
    # Only keep rows that contain trips coming from or going to locations within the city.
    df_taxi_data = df_taxi_data[(df_taxi_data['PULocationID'] != idx_outside[0]) & (df_taxi_data['DOLocationID'] != idx_outside[0]) & \
                                (df_taxi_data['PULocationID'] != idx_outside[1]) & (df_taxi_data['DOLocationID'] != idx_outside[1])]
    
    # Show preprocessing result
    print('About {:.4f}% of the entire data could not be used because "PULocationID" or "DOLocationID" are outside the city.'.format(100*(1-df_taxi_data.shape[0]/n_rows_total)))
    
    return df_taxi_data