from math import *
import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple

DATA_TYPE_CATEGORICAL = "CAT"
DATA_TYPE_TEXT = "TXT"
DATA_TYPE_NUMERICAL = "NUM"
DATA_TYPE_INDEX = "INDEX"
DATA_TYPE_DATE = "DATE"

MAX_CATEGORICAL_VALUES = 32

DISPLAY_VALUES = 5
MAX_PIE_BINS = 10


def readcsv(filename, delimiter, encoding) -> pd.DataFrame:
    df = pd.read_csv(filename, delimiter=delimiter, encoding=encoding)
    return df


def data_conversation(data: pd.DataFrame) -> Tuple[pd.DataFrame, str]:
    int_data = pd.to_numeric(data, errors="coerce")
    float_data = pd.to_numeric(data.replace(",", "."), errors="coerce")
    str_data = data.astype(str)
    date_data = pd.to_datetime(str_data, errors="coerce")
    data_unique = data.nunique()

    if data_unique == len(data):
        datatype = "INDEX"
    elif data_unique <= MAX_CATEGORICAL_VALUES and not int_data.isna().any():
        datatype = "CATEGORICAL"
        data = int_data.replace(-1, pd.NaT)
    elif not float_data.isna().any():
        datatype = "NUMERICAL"
        data = float_data.replace(-1, pd.NaT)
    elif not str_data.isna().any():
        datatype = "TEXT"
        data = date_data.dt.year
    else:
        datatype = "DATE"

    return data, datatype


def printing(dataset: pd.DataFrame, column: str, datatype: str) -> None:
    histogram = dataset.value_counts()

    if datatype != DATA_TYPE_CATEGORICAL:
        dataset.nunique()
    else:
        median = dataset.median()
        mean = dataset.mean()
        kurtosis = dataset.kurtosis()
        skew = dataset.skew()

        print(
            f"""Kurtosis: {kurtosis}
                        \nSkew: {skew}"""
        )
