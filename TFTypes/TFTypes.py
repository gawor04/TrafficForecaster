from collections import namedtuple

IntensityRow = namedtuple('IntensityRow', 'date intensity')
WeatherRow = namedtuple('WeatherRow', 'date temp precip')

ArchiveRow = namedtuple('ArchiveRow', 'date cars bikes temp precip')
ForecastArchiveRow = namedtuple('ForecastArchiveRow', 'date cars bikes')
