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
    class MockDatetime():
        @staticmethod
        def now(tz=None):
            return mock_now

    return MockDatetime
