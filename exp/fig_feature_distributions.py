# Plotting setup
import matplotlib.pyplot as plt

# Package imports
import numpy as np
import pandas as pd

from scipy import stats

# Allow import of own scripts #
import sys, os
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
###############################

# Own functions
from src.load_taxi_data import load_taxi_data
from src.taxi_zones_loader import taxi_zones_loader
from src.preprocess_data import preprocess_data
from src.keep_correct_year import keep_correct_year
from src.remove_routes import remove_routes
from src.temporal_preprocessing import temporal_preprocessing
from src.keep_correct_month import keep_correct_month

''' Retrieve data '''
# Read previously saved dataframe from csv file from disk (if available)
# df_taxi_2019_01 = pd.read_csv('df_taxi_2019_01.csv')

# Download data from TLC
df_taxi_2019_01 = load_taxi_data(['yellow', 'green', 'fhv'], [2019], [1])

# Save to disk (if desired)
# df_taxi_2019_01.to_csv('df_taxi_2019_01.csv', encoding='utf-8')

''' Pre-processing '''
# Remove invalid data
df_taxi_2019_01 = preprocess_data(df_taxi_2019_01)

# Remove rows with the wrong year
df_taxi_2019_01 = keep_correct_year(df_taxi_2019_01, 2019)

# Remove rows with wrong month
df_taxi_2019_01 = keep_correct_month(df_taxi_2019_01, '01')

# Remove routes that come from or go to locations outside the city
df_taxi_2019_01 = remove_routes(df_taxi_2019_01)

print('Number of entries in the data set after pre-processing: {} rows'.format(df_taxi_2019_01.shape[0]))

''' Extract temporal features '''
df_taxi_2019_01 = temporal_preprocessing(df_taxi_2019_01)

''' Drop columns of wrong datatype which cannot be used in the calculation of the correlation matrix: '''
# 'pickup_month' is dropped because we only have data of January 2019.
excluded_clms = ['pickup_datetime', 'dropoff_datetime', 'fleet', 'trip_duration', 'pickup_month']
df_taxi_2019_01 = df_taxi_2019_01.drop(columns=excluded_clms, inplace=False)

''' Restrict to single route: JFK Airport (Queens) to LaGuardia Airport (Queens) '''
pickup_id  = 132   # JFK Airport (Queens)
dropoff_id = 138   # LaGuardia Airport (Queens)

# Set route fixed but leave all other columns the way they are
df_taxi_2019_01_unfiltered = df_taxi_2019_01[(df_taxi_2019_01['PULocationID'] == pickup_id) &
                                             (df_taxi_2019_01['DOLocationID'] == dropoff_id)]
                                             
df_taxi_2019_01_unfiltered = df_taxi_2019_01_unfiltered.drop(columns=['PULocationID', 'DOLocationID'], inplace=False)

''' Filter and transform data '''
t_lower = 8        # Minimum: 8 minutes.
t_upper = 60       # Maximum: 1 hour => Average longest trip duration according to Google maps is 40 minutes.

# Filter routes
df_one_route_filtered = df_taxi_2019_01[(df_taxi_2019_01['PULocationID'] == pickup_id)         & \
                                        (df_taxi_2019_01['DOLocationID'] == dropoff_id)        & \
                                        (df_taxi_2019_01['trip_duration_minutes'] < t_upper)   & \
                                        (df_taxi_2019_01['trip_duration_minutes'] > t_lower)]
                                        
df_one_route_filtered = df_one_route_filtered.drop(columns=['PULocationID', 'DOLocationID'], inplace=False)

''' Plot histograms of filtered data and filtere data after gaussianization '''
fsize_title = 25    # Subtitle font size
fsize_label = 19    # Label font size
fsize_ticks = 16    # Tick font size
label_vert_pad = 25 # Vertical padding for x-axis labels
font = {'fontname':'serif'}

fig = plt.figure(constrained_layout=True, figsize=(13, 6))

(subfig1, subfig2) = fig.subfigures(2, 1, wspace=0.07, hspace=0.1)
axs1 = subfig1.subplots(1, 5)                          # create 1x5 subplots on subfig1
axs2 = subfig2.subplots(1, 5)                          # create 1x5 subplots on subfig2

# Plot first row: UNtransformed features
subfig1.suptitle('Distribution of filtered features (not gaussianized)', fontsize=fsize_title, **font)
axs1[0].hist(df_one_route_filtered['pickup_day_of_month'], bins='scott', color='tab:orange', edgecolor='#303030')
axs1[0].set_ylabel('Frequency', fontsize=fsize_label, **font)

axs1[1].hist(df_one_route_filtered['pickup_minute'], bins='scott', color='tab:orange', edgecolor='#303030')

axs1[2].hist(df_one_route_filtered['trip_duration_minutes'], bins='scott', color='tab:orange', edgecolor='#303030')

axs1[3].hist(df_one_route_filtered['pickup_weekday'], bins='scott', color='tab:orange', edgecolor='#303030')

axs1[4].hist(df_one_route_filtered['pickup_hour'], bins='scott', color='tab:orange', edgecolor='#303030')

# Plot second row: Partly Gaussianized features
subfig2.suptitle('Distribution of filtered and partially gaussianized features', fontsize=fsize_title, **font)
axs2[0].hist( stats.yeojohnson(np.cbrt(df_one_route_filtered['pickup_day_of_month']))[0], color='tab:purple', bins='scott', edgecolor='#303030')
axs2[0].set_ylabel('Frequency', fontsize=fsize_label, **font)
axs2[0].set_xlabel('pickup_day_of_month', fontsize=fsize_label, **font)

axs2[1].hist( df_one_route_filtered['pickup_minute'], bins='scott', color='tab:purple', edgecolor='#303030')
axs2[1].set_xlabel('pickup_minute *', fontsize=fsize_label, labelpad=label_vert_pad, **font)

axs2[2].hist( stats.boxcox(df_one_route_filtered['trip_duration_minutes'], -0.42) , bins='scott', color='tab:purple', edgecolor='#303030')
axs2[2].set_xlabel('trip_duration_minutes', fontsize=fsize_label, **font)

axs2[3].hist( df_one_route_filtered['pickup_weekday'], bins='scott', color='tab:purple', edgecolor='#303030')
axs2[3].set_xlabel('pickup_weekday *', fontsize=fsize_label, labelpad=label_vert_pad, **font)

axs2[4].hist( df_one_route_filtered['pickup_hour'], bins='scott', color='tab:purple', edgecolor='#303030')
axs2[4].set_xlabel('pickup_hour *', fontsize=fsize_label, **font)

fig.suptitle(' ', fontsize='xx-large')

# Increase tick font size
plt.setp(axs1[0].get_xticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs1[1].get_xticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs1[2].get_xticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs1[3].get_xticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs1[4].get_xticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs2[0].get_xticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs2[1].get_xticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs2[2].get_xticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs2[3].get_xticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs2[4].get_xticklabels(), fontsize=fsize_ticks, **font)

plt.setp(axs1[0].get_yticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs1[1].get_yticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs1[2].get_yticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs1[3].get_yticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs1[4].get_yticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs2[0].get_yticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs2[1].get_yticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs2[2].get_yticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs2[3].get_yticklabels(), fontsize=fsize_ticks, **font)
plt.setp(axs2[4].get_yticklabels(), fontsize=fsize_ticks, **font)

plt.savefig('feature_distributions.pdf', bbox_inches='tight')
