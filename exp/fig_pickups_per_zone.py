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
PICKUP_ZONE = 132

DATA_PATH = '../dat/'
FIG_PATH = '../doc/fig/'


# plot interactive map
def plot_interactive_map(geodf, target_variable, title):
    # Set geometry such that geopandas knows which column to use for plotting polygons, ...
    geodf.set_geometry("geometry");

    # re-set coordinates / projection:
    geodf.crs

    # convert projection system / coordinates which is necessary for plotly
    geodf.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)

    # map as background
    fig = px.choropleth_mapbox(geodf, geojson=geodf.geometry,
                               locations=geodf.index, color=target_variable,
                               color_continuous_scale=px.colors.sequential.YlOrRd,
                               hover_data=['zone', 'borough'],
                               mapbox_style="open-street-map",
                               labels="test",
                               center={"lat": 40.75, "lon": -73.95},  # {"lat": 40.707, "lon": -73.98},
                               zoom=10.0,  # 9.4
                               opacity=0.6,
                               title=title)

    # update
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
        title={
            'text': title,
            'y': 0.895,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'})

    fig.update_layout(
        font_family="Times",
        font_color="black",
        title_font_size=25)

    file_name = title.lower()
    file_name = file_name.replace(" ", "-")
    file_name = file_name.replace("/", "-")
    file_path = FIG_PATH + '%s.pdf' % (file_name)
    fig.write_image(file_path, width='720', height='720', format='pdf')  # 820 720 width='1640', height='1440',

    fig.show()


def fill_empty_rows(dataframe):
    return (dataframe.reindex(list(range(dataframe.index.min(),dataframe.index.max()+1)),fill_value=0))


# get zone averges by taxi dataframe
def get_zone_stats(df_taxi, geodf_nyc):
    # count number of dropouts for each taxi zone
    df_dropouts = df_taxi.groupby('DOLocationID')['DOLocationID'].count()
    # fill empty rows with zero
    df_dropouts = fill_empty_rows(df_dropouts)
    # fix column names
    df_dropouts = df_dropouts.rename_axis('DOLocationID').reset_index(name='Dropouts')
    # merge datasets
    gdf_zone_stats = geodf_nyc.merge(left_on='LocationID', right=df_dropouts, right_on='DOLocationID')
    del df_dropouts

    # count number of pickups for each taxi zone
    df_pickups = df_taxi.groupby('PULocationID')['PULocationID'].count()
    # fill empty rows with zero
    df_pickups = fill_empty_rows(df_pickups)
    # fix column names
    df_pickups = df_pickups.rename_axis('PULocationID').reset_index(name='Pickups')
    # merge datasets
    gdf_zone_stats = gdf_zone_stats.merge(left_on='DOLocationID', right=df_pickups, right_on='PULocationID')
    del df_pickups

    # drop not needed columns
    gdf_zone_stats = gdf_zone_stats.drop(columns=['DOLocationID', 'PULocationID'])

    # return geodataframe
    return gdf_zone_stats


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

    gdf_zone_stats = get_zone_stats(df_taxi, geodf_nyc)
    plot_interactive_map(gdf_zone_stats, "Pickups", "Pickups per Zone in %s/%s"%(MONTH, YEAR))

if __name__ == "__main__":
    main()
