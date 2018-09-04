from pathlib import Path
import datetime
import json
import pandas
import io

def get_yday(path):
	
	forecasted_cars = 0
	forecasted_bikes = 0
	real_cars = 0
	real_bikes = 0
	
	yday = datetime.datetime.now() - datetime.timedelta(days=1)
	
	if Path('/home/konrad/TrafficForecaster_DB/ForecastArchive.csv').is_file():
		
		f_arch_df = pandas.read_csv('/home/konrad/TrafficForecaster_DB/ForecastArchive.csv', index_col='date')
		
		if not f_arch_df[f_arch_df.index.str.contains(yday.strftime('%Y-%m-%d'))].empty:
			forecasted_bikes = f_arch_df.loc[yday.strftime('%Y-%m-%d')]['bikes']
			forecasted_cars = f_arch_df.loc[yday.strftime('%Y-%m-%d')]['cars']
			
	if Path('/home/konrad/TrafficForecaster_DB/Archive.csv').is_file():
		
		arch_df = pandas.read_csv('/home/konrad/TrafficForecaster_DB/Archive.csv', index_col='date')
		
		if not arch_df[arch_df.index.str.contains(yday.strftime('%Y-%m-%d'))].empty:
			real_bikes = arch_df.loc[yday.strftime('%Y-%m-%d')]['bikes']
			real_cars = arch_df.loc[yday.strftime('%Y-%m-%d')]['cars']
	
	json_data = json.dumps({'forecasted_cars': int(forecasted_cars), 'forecasted_bikes': int(forecasted_bikes),
                                'real_cars': int(real_cars), 'real_bikes': int(real_bikes)})

	s = io.StringIO()
	json.dump(json_data, s)
                              
	print("Content-type: application/json; filename=\"table.json\"\r\n\n\n")
	print(s.getvalue())
