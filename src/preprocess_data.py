import pandas as pd
import numpy as np

def preprocess_data(df_taxi_data):
    '''
    Preprocess TLC taxi trip data: Remove NaN values and unnecssary columns.
    ------------------------------------------------------------------------
    INPUTS:
    
    df_taxi_data (Pandas dataframe): This data mus have been loaded using load_taxi_data().
    
    OUTPUT:
    
    df_cleansed (Pandas dataframe): Cleansed dataframe.
    '''
    n_rows_total = df_taxi_data.shape[0]
    
    # Remove unnecessary column to save space
    if 'Unnamed: 0' in df_taxi_data.columns:
        df_taxi_data.drop(columns='Unnamed: 0', inplace=True) # inplace=True modifies the dataframe itself, so no copying is necessary
    
    # Get names of indexes for which column LocationID has value 0 => This is an undefined location!
    indexNames = df_taxi_data[ (df_taxi_data['PULocationID'] == 0) | (df_taxi_data['DOLocationID'] == 0) ].index
    
    # Delete these row indexes from taxi trip data
    df_taxi_data.drop(indexNames , inplace=True)
    
    '''DEBUG - uncomment for state of preprocessing'''
    # print('There are {} rows with undefined location (i.e., DOLocationID = 0 or PULocationID = 0).'.format(df_taxi_data[df_taxi_data['DOLocationID'] == 0]
    
    # Identify all non-numeric values and convert them to NaN
    df_taxi_data['PULocationID'] = pd.to_numeric(df_taxi_data['PULocationID'], errors='coerce')
    df_taxi_data['DOLocationID'] = pd.to_numeric(df_taxi_data['DOLocationID'], errors='coerce')
    
    # Replace infinite values with the NaN values
    df_taxi_data.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # Drop all rows with NaN
    df_taxi_data.dropna(axis=0, inplace=True)
    
    # Some locations are stored as float but we need discrete int values for later grouping
    df_taxi_data['PULocationID'] = df_taxi_data['PULocationID'].astype(int)
    df_taxi_data['DOLocationID'] = df_taxi_data['DOLocationID'].astype(int)
    
    # Test: Are any NaN left?
    '''DEBUG - uncomment for state of preprocessing'''
    # print('There are {} rows with NaN values left.'.format(df_taxi_data[df_taxi_data['PULocationID'].isnull()].shape[0]))
    
    # Show preprocessing result
    print('About {:.4f}% of the entire data could not be used due to missing information (NaN).'.format(100*(1-df_taxi_data.shape[0]/n_rows_total)))
    
    return df_taxi_data
