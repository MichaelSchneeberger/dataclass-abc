from example.impl.capitalcityimpl import CapitalCityImpl


def init_capital_city(
        name: str,
        lon: float,
        lat: float,
        country: str,
):

    return CapitalCityImpl(
        city_name=name,
        lon=lon,
        lat=lat,
        country_name=country
    )
