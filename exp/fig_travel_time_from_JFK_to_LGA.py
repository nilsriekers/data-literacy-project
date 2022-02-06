# Package imports
import pandas as pd
import ssl
import matplotlib.pyplot as plt
from tqdm import tqdm
from tueplots import bundles
from calendar import monthrange
from datetime import datetime

# from IPython.display import set_matplotlib_formats
import matplotlib_inline.backend_inline

# allow import of own scripts
import sys, os
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

# import own functions
from src.load_taxi_data import load_taxi_data
from src.preprocess_data import preprocess_data
from src.keep_correct_year import keep_correct_year
from src.remove_routes import remove_routes

# disable_certificate_check
ssl._create_default_https_context = ssl._create_unverified_context
# set matplotlib formats
matplotlib_inline.backend_inline.set_matplotlib_formats("pdf", "svg")


# variables
DATA_PATH = '../dat/'
FIG_PATH = '../doc/fig/'


# function to download all necessary data
def download_all_taxi_data():
    # download data for years between 2015 and 2021
    for year in range(2019, 2020):
        # download data for months between 01 and 12
        for month in tqdm(range(1, 13), desc="Downloading data from the year: %s"%(year)):
            # skip months after june 2021, because data is not available
            if not (year == 2021 and month >= 7):
                # leading zero if number as only one digit
                month = "%02d" % (month,)
                if os.path.isfile(DATA_PATH + 'df_taxi_%s_%s.csv'%(year, month)):
                    print("Dataset %s already downloaded."%'df_taxi_%s_%s.csv'%(year, month))
                else:
                    # download taxi data for given month and year
                    df_taxi = load_taxi_data(['yellow', 'green', 'fhv', 'fhvhv'], [int(year)], [int(month)])
                    # save data as csv on disk
                    df_taxi.to_csv('../dat/df_taxi_%s_%s.csv'%(year, month), encoding='utf-8')


# preprocessing of dataset
def dataset_preprocessing(df, year):
    # remove nan values
    df = preprocess_data(df)
    # remove rides outside nyc
    df = remove_routes(df)
    # remove wrong years from data set
    df = keep_correct_year(df, year)
    return df


# data preparation
def prepare_data_for_route_between_two_zones(df_taxi):
    # JFK Airport (Queens)
    pickup_zone = 132
    # LaGuardia Airport (Queens)
    dropout_zone = 138

    # only keep rides starting from JFK Airport going to LaGuardia Airport
    df_route_subset = df_taxi[df_taxi["PULocationID"] == pickup_zone]
    df_route_subset = df_route_subset[df_route_subset["DOLocationID"] == dropout_zone]

    # remove outlier
    Q1 = df_route_subset.quantile(0.25)
    Q3 = df_route_subset.quantile(0.75)
    IQR = Q3 - Q1
    df_route_subset = df_route_subset[
        ~((df_route_subset < (Q1 - 1.5 * IQR)) | (df_route_subset > (Q3 + 1.5 * IQR))).any(axis=1)]

    return df_route_subset


# get dataframe with pickup times in bins
def get_df_with_pickup_times_in_bins(df_route_subset):
    # convert string into datetime format to only keep date
    df_route_subset['pickup_datetime'] = pd.to_datetime(df_route_subset['pickup_datetime'], format='%Y-%m-%d')

    # define the bins
    bins = list(range(0, 24 + 1))

    # custom labels
    labels = []
    for hour in bins:
        if hour != 24:
            hour = "%02d" % (hour,)
            labels.append("%s:00-%s:59" % (hour, hour))

    # add the bins to the dataframe
    df_route_subset['time bin'] = pd.cut(df_route_subset.pickup_datetime.dt.hour, bins, labels=labels, right=False)

    # groupby Time Bin and aggregate a list for the observations, and mean
    df_route_subset = df_route_subset.groupby('time bin', as_index=False)['trip_duration'].agg([list, 'mean'])

    return df_route_subset


def main():
    # create a lot of empty data frames
    df_monday_travel_time = pd.DataFrame()
    df_tuesday_travel_time = pd.DataFrame()
    df_wednesday_travel_time = pd.DataFrame()
    df_thursday_travel_time = pd.DataFrame()
    df_friday_travel_time = pd.DataFrame()
    df_saturday_travel_time = pd.DataFrame()
    df_sunday_travel_time = pd.DataFrame()

    # download data for years between 2015 and 2021
    for year in range(2019, 2020):
        # download data for months between 01 and 12
        for month in tqdm(range(1, 13), desc="Loading data from disk of year: %s" % (year)):
            # skip months after june 2021, because data is not available
            if not (year == 2021 and month >= 7):
                # leading zero if number as only one digit
                month = "%02d" % (month,)
                if os.path.isfile('../dat/df_taxi_%s_%s.csv' % (year, month)):
                    # read dataframe
                    df_taxi = pd.read_csv("../dat/df_taxi_%s_%s.csv" % (str(year), str(month)))
                    # dataset preprocessing
                    df_taxi = dataset_preprocessing(df_taxi, year)
                    # get trip duration (target variable)
                    trip_duration = (pd.to_datetime(df_taxi['dropoff_datetime'], format='%Y-%m-%d %H:%M:%S')) - (
                        pd.to_datetime(df_taxi['pickup_datetime'], format='%Y-%m-%d %H:%M:%S'))
                    # add trip duration to dataframe
                    df_taxi.insert(len(df_taxi.columns), 'trip_duration', trip_duration.astype('timedelta64[m]'))

                    # prepare data for route between two zones
                    df_route_subset = prepare_data_for_route_between_two_zones(df_taxi)

                    # convert string into datetime format to only keep date
                    df_route_subset['aux_date'] = pd.to_datetime(df_route_subset['pickup_datetime'],
                                                                 format='%Y-%m-%d').dt.date
                    # store date as string
                    df_route_subset['aux_date'] = df_route_subset['aux_date'].astype(str)

                    # convert string into datetime format to only keep date
                    df_route_subset['aux_time'] = pd.to_datetime(df_route_subset['pickup_datetime'],
                                                                 format='%Y-%m-%d').dt.date
                    # store date as string
                    df_route_subset['aux_time'] = df_route_subset['aux_date'].astype(str)

                    # get amount of days of month X in year Y
                    days = monthrange(int(year), int(month))[1]
                    # for every day in the month
                    for day in range(1, days + 1):
                        # leading zero if number as only one digit
                        day = "%02d" % (day,)
                        # composite date from loop
                        date = '%s-%s-%s' % (year, month, day)

                        df_day_subset = df_route_subset[df_route_subset['aux_date'] == date]

                        ### get dataframe with pickup times in bins
                        ###df_pickup_times_in_bins = get_df_with_pickup_times_in_bins(df_route_subset, date)
                        # get weekday of date
                        weekday = datetime.strptime(date, '%Y-%m-%d').weekday()

                        if weekday == 0:
                            df_monday_travel_time = df_monday_travel_time.append(df_day_subset)
                        elif weekday == 1:
                            df_tuesday_travel_time = df_tuesday_travel_time.append(df_day_subset)
                        elif weekday == 2:
                            df_wednesday_travel_time = df_wednesday_travel_time.append(df_day_subset)
                        elif weekday == 3:
                            df_thursday_travel_time = df_thursday_travel_time.append(df_day_subset)
                        elif weekday == 4:
                            df_friday_travel_time = df_friday_travel_time.append(df_day_subset)
                        elif weekday == 5:
                            df_saturday_travel_time = df_saturday_travel_time.append(df_day_subset)
                        elif weekday == 6:
                            df_sunday_travel_time = df_sunday_travel_time.append(df_day_subset)
                else:
                    print("File does not exist!")

    # edit dataframes
    df_monday_travel_time = get_df_with_pickup_times_in_bins(df_monday_travel_time)
    df_tuesday_travel_time = get_df_with_pickup_times_in_bins(df_tuesday_travel_time)
    df_wednesday_travel_time = get_df_with_pickup_times_in_bins(df_wednesday_travel_time)
    df_thursday_travel_time = get_df_with_pickup_times_in_bins(df_thursday_travel_time)
    df_friday_travel_time = get_df_with_pickup_times_in_bins(df_friday_travel_time)
    df_saturday_travel_time = get_df_with_pickup_times_in_bins(df_saturday_travel_time)
    df_sunday_travel_time = get_df_with_pickup_times_in_bins(df_sunday_travel_time)

    # plotting
    with plt.rc_context(bundles.neurips2021()):
        # initiate plot
        ax = df_monday_travel_time.plot(label="Monday")
        df_tuesday_travel_time.plot(ax=ax, label="Tuesday")
        df_wednesday_travel_time.plot(ax=ax, label="Wednesday")
        df_thursday_travel_time.plot(ax=ax, label="Thursday")
        df_friday_travel_time.plot(ax=ax, label="Friday")
        df_saturday_travel_time.plot(ax=ax, label="Saturday")
        df_sunday_travel_time.plot(ax=ax, label="Sunday")

        # legend settings
        ax.legend(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], prop={'size': 7.5},
                  loc='center left', bbox_to_anchor=(1, 0.5))

        # set title
        ax.set_title('Average travel time between JFK and LaGuardia Airport by day of week in 2019')
        # set x label
        ax.set_xlabel('time bin with the hour of the day')
        # set y label
        ax.set_ylabel('travel time (min)')

        fig = plt.gcf()
        # show plot
        plt.show()
        # save figure
        fig.savefig(FIG_PATH + 'travel-time-from-JFK-to-LGA.pdf', bbox_inches='tight', dpi=400)


if __name__ == "__main__":
    main()
