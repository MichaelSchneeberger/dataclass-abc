from example.capitalcity import CapitalCity
from example.init.initcapitalcity import init_capital_city
from example.init.initcity import init_city

oslo = init_capital_city(
    name='Oslo',
    lon=10.8,
    lat=59.9,
    country='Norway',
)

madrid = init_capital_city(
    name='Madrid',
    lon=-3.7,
    lat=40.4,
    country='Spain',
)

zurich = init_city(
    name='Zurich',
    lon=8.6,
    lat=47.4,
)

cities = [oslo, madrid, zurich]

# pattern match on cities to filter capital cities
capitals = [city for city in cities if isinstance(city, CapitalCity)]

print(madrid.distance_to(zurich))
print(capitals)
