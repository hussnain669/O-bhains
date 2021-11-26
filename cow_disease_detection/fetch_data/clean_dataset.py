"""This module is use to access data from google sheet, preprocess data, and stored in data folder.
Average data by days/hours (if you need).

Parameters
----------
arg1: string
    input string (days/hours/no_avg)

Returns
-------
dataframe
    Module return three types of datasets average by days, hours, and no average.

Example
-------
    $ python clean_dataset.py days/hours/no_avg
"""
import argparse
from datetime import datetime
import os
import pandas as pd
import gspread
from gspread_dataframe import get_as_dataframe


def get_data() -> pd.DataFrame:
    """This function get data form google sheet.

    Parameters
    ----------
    None

    Returns
    -------
    dataframe
        This function return a dataset.
    """
    google_credential: str = gspread.service_account(
        filename=os.path.join(os.path.dirname(__file__), "credentials.json")
    )
    google_sheet: str = google_credential.open_by_key(
        "1AJSGHiLQvwlPYY7RPyS7nlYwLmof70DC-NVHT-o7QtE"
    )
    worksheet = google_sheet.sheet1
    data_frame_1 = get_as_dataframe(worksheet)
    return data_frame_1


# data preprocessing
def data_preprocessing() -> pd.DataFrame:
    """This function preprocess data that get from google sheet.

    Parameters
    ----------
    None

    Returns
    -------
    dataframe
        This function return a dataset.
    """
    data_frame_2 = get_data()
    data_frame_2 = data_frame_2.iloc[:, :6]
    data_frame_2 = data_frame_2.dropna()
    data_frame_2["date"] = pd.to_datetime(
        data_frame_2["date"] + " " + data_frame_2["time"]
    )  # concatenate date and time column
    data_frame_2 = data_frame_2.drop("time", axis=1)
    data_frame_2 = data_frame_2.rename(columns={"date": "datetime"})
    return data_frame_2


# passing arguments to average dataset
parse: str = argparse.ArgumentParser(description="Modify/Average dataset")
parse.add_argument(
    "average_by",
    type=str,
    help="Average dataset by days/hours/no_average",
    choices=["days", "hours", "no_avg"],
)


def calculate_average(average: str) -> pd.DataFrame:
    """This function is used to average Temperature and movement of cow per days/per hours.

    Parameters
    ----------
    arg1 : string
        input data average by (days/hours/no_avg)

    Returns
    -------
    dataframe
        This function return dataset of days average, hours average, or no_average.
    """
    data_frame_3 = data_preprocessing()
    times = pd.DatetimeIndex(data_frame_3.datetime)
    if average == "days":  # Average Temperature and movement of cow per days
        data_frame_3 = data_frame_3.groupby([times.date])[
            ["temperature", "x_axix", "y_axix", "z_axix"]
        ].median()
        data_frame_3.index.name = "days"
        print("Dataset average by days:\n")
    elif average == "hours":  # Average Temperature and movement of cow per hours
        data_frame_3 = data_frame_3.groupby([times.date, times.hour])[
            ["temperature", "x_axix", "y_axix", "z_axix"]
        ].median()
        data_frame_3.to_csv(
            "./cow_disease_detection/data/from_fetch_data.csv", index=True
        )
        data_frame_3 = pd.read_csv(
            "./cow_disease_detection/data/from_fetch_data.csv",
            sep=",",
            names=["days", "hours", "temperature", "x_axix", "y_axix", "z_axix"],
        )
        data_frame_3.drop([0], inplace=True)
        print("Dataset average by hours:\n")
    else:
        print("No average dataset")
    return data_frame_3


def args_value(average: str) -> str:
    """This function get argument value.

    Parameters
    ----------
    arg1: average
        Get string value e.g days/hours/no_avg.

    Returns
    -------
    string
        Function return string value that pass AVG_VALUE variable.
    """
    return average


if __name__ == "__main__":
    args: str = parse.parse_args()
    AVG_VALUE: str = args_value(args.average_by)
    dataset = calculate_average(AVG_VALUE)

    # Display and store dataset
    print(dataset.head(10))
    if AVG_VALUE == "days":

        dataset.to_csv("./cow_disease_detection/data/from_fetch_data.csv", index=True)
    else:
        dataset.to_csv("./cow_disease_detection/data/from_fetch_data.csv", index=False)
