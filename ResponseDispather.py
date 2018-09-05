import os
import pandas
import datetime
import io
import sys
from flask import make_response

class ResponseDispatcher:

	self.__api = { 'get_archive': self.__get_archive,
				'get_json': self.__get_json,
				'get_csv': self.__get_csv,
				'get_yday': self.__get_yday,
	}

	self.__csv_api = {'bikes_temp.csv':self.__get_bikes_temp,
					'bikes_precip.csv':self.__get_bikes_precip,
					'cars_temp.csv':self.__get_cars_temp,
					'cars_precip.csv':self.__ger_cars_precip,
	}

	self.__path = './'

	set_path(self, path):
		self.__path  = path

	dispatch(self, address_path):
		return address_path.split(os.sep)[0]	
#		path_splitted = address_path.split(os.sep)		
#		path_splitted = path_splitted[4:]
#		if len(address_path) >= 2:
#			return self.__api[path_splitted[1]](path_splitted)

	__get_archive(self, address_splitted):


	if(len(address_splitte) >= 8):

		start = address_splitte[2] + '-' + address_splitte[3] + '-' + address_splitte[4]
		stop = address_splitte[5] + '-' + address_splitte[6] + '-' + address_splitte[7]
		dates = pandas.date_range(start, stop).tolist()
		
		archive_df = pandas.read_csv(self.__path + 'Archive.csv', index_col='date')
		archive_df.index = pandas.to_datetime(archive_df.index)
		range_archive_df = archive_df.ix[dates]
		
		range_archive_df['date'] = range_archive_df.index
		
		s = io.StringIO()
		range_archive_df.to_csv(s, index=False)

		output = make_response(s.getvalue())
		output.headers['Set-Cookie'] = 'fileDownload=true; path=/'
		output.headers['Content-type'] = 'text/csv'
		output.headers['Content-Disposition'] = 'attachment; filename=\"archive.csv\"'
		
		return output		

	__get_json(self, address_splitted):


		json = open(self.__path + 'forecaster.json', 'r')
	
		output = make_response(json.read())
		output.headers['Content-type'] = 'application/json; filename=\"forecaster.json\"'
		
		return output

	__get_csv(self, address_splitted):
		
		if	len(address_splitted) >= 3:
			return self.__csv_api[path[2]]()
		else
			return None

	__get_yday(self, address_splitted):

		forecasted_cars = 0
		forecasted_bikes = 0
		real_cars = 0
		real_bikes = 0
	
		yday = datetime.datetime.now() - datetime.timedelta(days=1)
	
		if Path(self.__path + 'ForecastArchive.csv').is_file():
		
			f_arch_df = pandas.read_csv(self.__path + 'ForecastArchive.csv', index_col='date')
		
			if not f_arch_df[f_arch_df.index.str.contains(yday.strftime('%Y-%m-%d'))].empty:
				forecasted_bikes = f_arch_df.loc[yday.strftime('%Y-%m-%d')]['bikes']
				forecasted_cars = f_arch_df.loc[yday.strftime('%Y-%m-%d')]['cars']
			
		if Path(self.__path + 'Archive.csv').is_file():
		
			arch_df = pandas.read_csv(self.__path + 'Archive.csv', index_col='date')
		
			if not arch_df[arch_df.index.str.contains(yday.strftime('%Y-%m-%d'))].empty:
				real_bikes = arch_df.loc[yday.strftime('%Y-%m-%d')]['bikes']
				real_cars = arch_df.loc[yday.strftime('%Y-%m-%d')]['cars']
	
		json_data = json.dumps({'forecasted_cars': int(forecasted_cars), 'forecasted_bikes': int(forecasted_bikes),
                                'real_cars': int(real_cars), 'real_bikes': int(real_bikes)})

		s = io.StringIO()
		json.dump(json_data, s)

		output = make_response(s.getvalue())
		
		output = make_response(json.read())
		output.headers['Content-type'] = 'application/json; filename=\"table.json\"'
	
		return output

	def __get_bikes_temp():
	
		archive_df = pandas.read_csv(self.__path + 'Archive.csv', index_col='date')
		del archive_df['cars']
		del archive_df['precip']
	
		archive_df = archive_df.dropna()
	
		s = io.StringIO()
		archive_df.to_csv(s, index=False)
	
		csv_str = s.getvalue()
		csv_str = csv_str[:-1]
		
		output = make_response(csv_str)
		output.headers['Content-type'] = 'text/csv'
		
		return output
	

	def __get_bikes_precip():
	
		archive_df = pandas.read_csv(self.__path + 'Archive.csv', index_col='date')
		del archive_df['cars']
		del archive_df['temp']
	
		archive_df = archive_df.dropna()
	
		s = io.StringIO()
		archive_df.to_csv(s, index=False)
	
		csv_str = s.getvalue()
		csv_str = csv_str[:-1]
	
		output = make_response(csv_str)
		output.headers['Content-type'] = 'text/csv'
		
		return output
	
	def __get_cars_temp():
	
		archive_df = pandas.read_csv(self.__path + 'Archive.csv', index_col='date')
		del archive_df['bikes']
		del archive_df['precip']
	
		archive_df = archive_df.dropna()
	
		s = io.StringIO()
		archive_df.to_csv(s, index=False)
	
		csv_str = s.getvalue()
		csv_str = csv_str[:-1]
	
		output = make_response(csv_str)
		output.headers['Content-type'] = 'text/csv'
		
		return output
	
	def __get_cars_precip():
	
		archive_df = pandas.read_csv(self.__path + 'Archive.csv', index_col='date')
		del archive_df['bikes']
		del archive_df['temp']
	
		archive_df = archive_df.dropna()
	
		s = io.StringIO()
		archive_df.to_csv(s, index=False)
	
		csv_str = s.getvalue()
		csv_str = csv_str[:-1]
		
		output = make_response(csv_str)
		output.headers['Content-type'] = 'text/csv'
		
		return output
