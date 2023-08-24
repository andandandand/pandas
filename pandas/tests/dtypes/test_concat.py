import datetime

import numpy as np
import pytest

import pandas.core.dtypes.concat as _concat

import pandas as pd
from pandas import Series
import pandas._testing as tm


def test_concat_mismatched_categoricals_with_empty():
    ser1 = Series(["a", "b", "c"], dtype="category")
    ser2 = Series([], dtype="category")

    msg = "The behavior of array concatenation with empty entries is deprecated"
    with tm.assert_produces_warning(FutureWarning, match=msg):
        result = _concat.concat_compat([ser1._values, ser2._values])
    with tm.assert_produces_warning(FutureWarning, match=msg):
        expected = pd.concat([ser1, ser2])._values
    tm.assert_categorical_equal(result, expected)


@pytest.mark.parametrize("copy", [True, False])
def test_concat_single_dataframe_tz_aware(copy):
    # GH 25257
    df = pd.DataFrame(
        {"timestamp": [pd.Timestamp("2020-04-08 09:00:00.709949+0000", tz="UTC")]}
    )
    expected = df.copy()
    result = pd.concat([df], copy=copy)
    tm.assert_frame_equal(result, expected)


def test_concat_periodarray_2d():
    pi = pd.period_range("2016-01-01", periods=36, freq="D")
    arr = pi._data.reshape(6, 6)

    result = _concat.concat_compat([arr[:2], arr[2:]], axis=0)
    tm.assert_period_array_equal(result, arr)

    result = _concat.concat_compat([arr[:, :2], arr[:, 2:]], axis=1)
    tm.assert_period_array_equal(result, arr)

    msg = (
        "all the input array dimensions.* for the concatenation axis must match exactly"
    )
    with pytest.raises(ValueError, match=msg):
        _concat.concat_compat([arr[:, :2], arr[:, 2:]], axis=0)

    with pytest.raises(ValueError, match=msg):
        _concat.concat_compat([arr[:2], arr[2:]], axis=1)


def test_concatenate_datetime_and_category():
    # GH 33331
    np_datetimes = np.array([datetime.date(2010, 1, 1)], dtype="datetime64[D]")
    other = pd.array(["a", "b"], dtype="category")
    np_datetimes_series = Series(np_datetimes)
    result = pd.concat([np_datetimes_series, Series(other)], ignore_index=True)
    expected_result = Series([pd.Timestamp("2010-01-01"), "a", "b"])
    tm.assert_series_equal(result, expected_result)
