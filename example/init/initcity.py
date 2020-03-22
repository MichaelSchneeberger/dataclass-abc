from example.impl.cityimpl import CityImpl


def init_city(
        name: str,
        lon: float,
        lat: float,
):

    return CityImpl(
        city_name=name,
        lon=lon,
        lat=lat,
    )
