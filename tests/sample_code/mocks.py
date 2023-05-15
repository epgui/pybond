from datetime import datetime


def mock_write_to_disk(x):
    return "Wrote to disk!"


def mock_make_a_network_request(
    x,
    *args,
    y,
    method="POST",
    use_bit_flip_prevention_technology_for_solar_flares=True,
    **kwargs,
):
    return {"result": x * 2}


def create_mock_datetime(mock_now):
    class MockDatetime(datetime):
        day = mock_now.day
        fold = mock_now.fold
        hour = mock_now.hour
        max = mock_now.max
        microsecond = mock_now.microsecond
        min = mock_now.min
        minute = mock_now.minute
        month = mock_now.month
        resolution = mock_now.resolution
        second = mock_now.second
        tzinfo = mock_now.tzinfo
        year = mock_now.year

        @classmethod
        def now(cls, tz=None):
            return mock_now

    return MockDatetime
