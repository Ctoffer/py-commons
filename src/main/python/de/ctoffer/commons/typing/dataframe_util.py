import functools
import inspect

import numpy as np
import pandas as pd


def requires_columns(data_frame, data_types):
    def outer_wrapper(func):
        @functools.wraps(func)
        def inner_wrapper(*args, **kwargs):
            arguments = inspect.signature(func).bind(*args, **kwargs).arguments
            _check_data_frame(arguments[data_frame], data_types)
            return func(*args, **kwargs)

        return inner_wrapper

    return outer_wrapper


def _check_data_frame(data_frame, data_types):
    for column_name, column_type in data_types.items():
        if type(column_type) == tuple and column_type[0] == np.object:
            matches_type = data_frame[column_name].apply(lambda e: type(e) == column_type[1]).all()
            column_type = column_type[1]
        else:
            data_type = data_frame[column_name].dtype
            matches_type = column_type == data_type

        if not matches_type:
            raise TypeError(f"The column '{column_name}' is not of type {column_type.__name__}")


def returns_columns(data_types):
    def outer_wrapper(func):
        @functools.wraps(func)
        def inner_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            _check_data_frame(result, data_types)
            return result

        return inner_wrapper

    return outer_wrapper


@requires_columns(data_frame="data_frame", data_types={
    "id": np.int64,
    "x": np.int64,
    "y": np.float64
})
@returns_columns(data_types={
    "id": np.int64,
    "x": (np.object, str),
    "y": np.object
})
def my_function(data_frame: pd.DataFrame):
    data_frame["x"] = data_frame["x"].apply(lambda e: str(e))
    data_frame["y"] = data_frame["y"].apply(lambda e: str(e))

    return data_frame


input_data = pd.DataFrame({"id": [0, 1, 2, 3, 4], "x": [-13, 7, 18, 20, -5], "y": [1.2, 0.4, -0.3, 0.7, 8.2]})
output_data = my_function(input_data)
print(output_data)
