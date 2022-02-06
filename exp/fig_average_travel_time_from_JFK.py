# Package imports
import numpy as np
import pandas as pd
import geopandas as gpd
import ssl
import datetime

# from IPython.display import set_matplotlib_formats
import matplotlib_inline.backend_inline

# plotting setup
import matplotlib.pyplot as plt
import plotly.express as px
import contextily as cx
import pyproj
from matplotlib import rcParams

# allow import of own scripts
import sys, os
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

# import own functions
from src.load_taxi_data import load_taxi_data
from src.taxi_zones_loader import taxi_zones_loader
from src.preprocess_data import preprocess_data
from src.keep_correct_year import keep_correct_year
from src.keep_correct_month import keep_correct_month
from src.remove_routes import remove_routes

# disable_certificate_check
ssl._create_default_https_context = ssl._create_unverified_context
# set matplotlib formats
matplotlib_inline.backend_inline.set_matplotlib_formats("pdf", "svg")

# variables
YEAR = "2019"
MONTH = "01"
PICKUP_ZONE = 132 # JFK

DATA_PATH = '../dat/'
FIG_PATH = '../doc/fig/'


# plot advanced map
def plot_advanced_map(geodf, target_variable, title):
    # Re-set projection of geodata
    geodf = geodf.to_crs(epsg=3857)

    ax = geodf.plot(figsize=(7.5, 7.5),
                    column=target_variable,
                    legend="true",
                    legend_kwds={'shrink': 0.8},
                    alpha=0.6,
                    edgecolor='k',
                    cmap='hot_r')
    #leg = ax.get_legend()
    #leg.set_bbox_to_anchor((1.15, 0.5))

    cx.add_basemap(ax, source=cx.providers.Stamen.TonerLite)
    ax.set_axis_off()

    ax.set_title("           " + title + " in minutes", fontsize=15)

    file_name = title.lower()
    file_name = file_name.replace(" ", "-")
    file_name = file_name.replace("/", "-")

    plt.savefig(FIG_PATH + '%s.pdf' % (file_name), format='pdf', dpi=1200)


def fill_empty_rows(dataframe):
    return (dataframe.reindex(list(range(dataframe.index.min(), dataframe.index.max() + 1)), fill_value=0))


# get average ride time
def get_average_ride_time(df_taxi, geodf_nyc, pickup_zone):
    # get subset of all rides startng in given pickup zone
    subset = df_taxi[df_taxi["PULocationID"] == pickup_zone]

    gdf_average_ride_time = subset.groupby(['DOLocationID'])['trip_duration'].mean()

    # gdf_average_ride_time = fill_empty_rows(gdf_average_ride_time)
    gdf_average_ride_time.reindex(list(range(gdf_average_ride_time.index.min(), gdf_average_ride_time.index.max() + 1)),
                                  fill_value=np.nan)

    # fix column names
    gdf_average_ride_time = gdf_average_ride_time.rename_axis('DOLocationID').reset_index(name='AverageRideTime')

    # merge
    gdf_average_ride_time = geodf_nyc.merge(left_on='LocationID', right=gdf_average_ride_time, right_on='DOLocationID')

    return gdf_average_ride_time


def main():
    # get taxi data
    if os.path.isfile(DATA_PATH + 'df_taxi_%s_%s.csv' % (YEAR, MONTH)):
        print("Dataset %s already downloaded." % 'df_taxi_%s_%s.csv' % (YEAR, MONTH))
    else:
        # download taxi data for given month and year
        df_taxi = load_taxi_data(['yellow', 'green', 'fhv', 'fhvhv'], [int(YEAR)], [int(MONTH)])
        # save data as csv on disk
        df_taxi.to_csv(DATA_PATH + 'df_taxi_%s_%s.csv' % (YEAR, MONTH), encoding='utf-8')

    # read previously saved dataframe from csv file from disk
    df_taxi_raw = pd.read_csv(DATA_PATH + 'df_taxi_%s_%s.csv' % (YEAR, MONTH))
    print(df_taxi_raw.head())

    # preprocessing
    df_taxi = preprocess_data(df_taxi_raw)
    # remove rides outside nyc
    df_taxi = remove_routes(df_taxi)
    # remove wrong years from data set
    df_taxi = keep_correct_year(df_taxi, YEAR)

    print(df_taxi.head())

    # get trip duration (target variable)
    trip_duration = (pd.to_datetime(df_taxi['dropoff_datetime'], format='%Y-%m-%d %H:%M:%S')) - (
        pd.to_datetime(df_taxi['pickup_datetime'], format='%Y-%m-%d %H:%M:%S'))
    # add trip duration to dataframe
    df_taxi.insert(len(df_taxi.columns), 'trip_duration', trip_duration.astype('timedelta64[m]'))
    # filter negative values out
    df_taxi = df_taxi[df_taxi['trip_duration'] > 0]


    # read SHP data from file and plot head
    geodf_nyc = gpd.read_file("../dat/taxi_zones/taxi_zones.shp")
    # rest index to later get interpretable results
    geodf_nyc.set_index('LocationID', inplace=True);


    print(geodf_nyc.head())

    rcParams['font.family'] = 'Times'
    gdf_average_ride_time = get_average_ride_time(df_taxi, geodf_nyc, PICKUP_ZONE)
    plot_advanced_map(gdf_average_ride_time, "AverageRideTime", "Average travel time from JFK to other Zones in %s/%s"%(MONTH, YEAR))


if __name__ == "__main__":
    main()
