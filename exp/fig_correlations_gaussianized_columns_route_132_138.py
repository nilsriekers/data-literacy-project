# Plotting setup
import matplotlib.pyplot as plt
import seaborn as sns

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
from src.plot_regression_results import plot_regression_results
from src.sklearn_regression import sklearn_regression
from src.sklearn_regression_bf import sklearn_regression_bf
from src.ridge_regression_bf import ridge_regression_bf
from src.keep_correct_month import keep_correct_month

''' Retrieve data '''
# Read previously saved dataframe from csv file from disk (if available)
df_taxi_2019_01 = pd.read_csv('df_taxi_2019_01.csv')

# Download data from TLC
# df_taxi_2019_01 = load_taxi_data(['yellow', 'green', 'fhv'], [2019], [1])

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

# Transformations: "Gaussianization"
x0 = stats.boxcox(df_one_route_filtered['trip_duration_minutes'], -0.42)
x1 = stats.yeojohnson(np.cbrt(df_one_route_filtered['pickup_day_of_month']))[0]
x2 = (df_one_route_filtered['pickup_weekday']).values
x3 = df_one_route_filtered['pickup_hour']
x4 = (df_one_route_filtered['pickup_minute']).values

X = np.column_stack((x0, x1, x2, x3, x4))

df = pd.DataFrame(X, columns=df_one_route_filtered.columns)

''' Plot correlation matrix '''
sns_font = {'font':'serif'} # Font face

corr       = df.corr()
corr.index = df.columns
# Color blindness safe plot
sns.set(font_scale=1.3)
ax = sns.heatmap(
    corr, 
    vmin=-1, vmax=1, center=0,
    cmap=sns.diverging_palette(30, 250, s=100, l=40, as_cmap=True),
    square=True,
    annot=True,
    fmt=".1f"
)

plt.setp(ax.get_yticklabels(), **sns_font)
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor", **sns_font)
ax.tick_params(left=True, bottom=True)
plt.title("Correlations of filtered and \n gaussianized features", fontsize=16, pad=20, **sns_font)
plt.savefig('correlations_gaussianized_columns_route_132_138.pdf', bbox_inches='tight')
