import os
import pandas
import datetime
import io
import sys
import json
from flask import make_response
from flask import Flask
from pathlib import Path

class ResponseDispatcher(object):

	__Path = './'

	@staticmethod
	def Set_path(path):
		ResponseDispatcher.__Path  = path

	@staticmethod
	def Dispatch(address_path):

		path_splitted = address_path.split(os.sep)

		if len(address_path) >= 2:
			return ResponseDispatcher.__Api[path_splitted[1]](path_splitted)

	@staticmethod
	def __get_archive(address_splitted):


		if(len(address_splitted) >= 8):

			start = address_splitted[2] + '-' + address_splitted[3] + '-' + address_splitted[4]
			stop = address_splitted[5] + '-' + address_splitted[6] + '-' + address_splitted[7]
			dates = pandas.date_range(start, stop).tolist()
		
			archive_df = pandas.read_csv(ResponseDispatcher.__Path + 'Archive.csv', index_col='date')
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

	@staticmethod
	def __get_json(address_splitted):


		json_str = open(ResponseDispatcher.__Path + 'forecaster.json', 'r')		

		output = make_response(json_str.read())
		output.headers['Content-type'] = 'application/json; filename=\"forecaster.json\"'
		
		return output

	@staticmethod
	def __get_csv(address_splitted):
		
		if	len(address_splitted) >= 3:
			return ResponseDispatcher.__Csv_api[address_splitted[2]]()
		else:
			return None

	@staticmethod
	def __get_yday(address_splitted):

		forecasted_cars = 0
		forecasted_bikes = 0
		real_cars = 0
		real_bikes = 0
	
		yday = datetime.datetime.now() - datetime.timedelta(days=1)
	
		if Path(ResponseDispatcher.__Path + 'ForecastArchive.csv').is_file():
		
			f_arch_df = pandas.read_csv(ResponseDispatcher.__Path + 'ForecastArchive.csv', index_col='date')
		
			if not f_arch_df[f_arch_df.index.str.contains(yday.strftime('%Y-%m-%d'))].empty:
				forecasted_bikes = f_arch_df.loc[yday.strftime('%Y-%m-%d')]['bikes']
				forecasted_cars = f_arch_df.loc[yday.strftime('%Y-%m-%d')]['cars']
			
		if Path(ResponseDispatcher.__Path + 'Archive.csv').is_file():
		
			arch_df = pandas.read_csv(ResponseDispatcher.__Path + 'Archive.csv', index_col='date')
		
			if not arch_df[arch_df.index.str.contains(yday.strftime('%Y-%m-%d'))].empty:
				real_bikes = arch_df.loc[yday.strftime('%Y-%m-%d')]['bikes']
				real_cars = arch_df.loc[yday.strftime('%Y-%m-%d')]['cars']
	
		json_data = json.dumps({'forecasted_cars': int(forecasted_cars), 'forecasted_bikes': int(forecasted_bikes),
                                'real_cars': int(real_cars), 'real_bikes': int(real_bikes)})

		s = io.StringIO()
		json.dump(json_data, s)

		output = make_response(s.getvalue())
		output.headers['Content-type'] = 'application/json; filename=\"table.json\"'
	
		return output

	@staticmethod
	def __get_bikes_temp():
	
		archive_df = pandas.read_csv(ResponseDispatcher.__Path + 'Archive.csv', index_col='date')
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
	
	@staticmethod
	def __get_bikes_precip():
	
		archive_df = pandas.read_csv(ResponseDispatcher.__Path + 'Archive.csv', index_col='date')
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
	
	@staticmethod
	def __get_cars_temp():
	
		archive_df = pandas.read_csv(ResponseDispatcher.__Path + 'Archive.csv', index_col='date')
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
	
	@staticmethod
	def __get_cars_precip():
	
		archive_df = pandas.read_csv(ResponseDispatcher.__Path + 'Archive.csv', index_col='date')
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

	__Api = { 'get_archive':__get_archive.__get__(object),
				'get_json':__get_json.__get__(object),
				'get_csv':__get_csv.__get__(object),
				'get_yday':__get_yday.__get__(object),
	}

	__Csv_api = {'bikes_temp.csv':__get_bikes_temp.__get__(object),
					'bikes_precip.csv':__get_bikes_precip.__get__(object),
					'cars_temp.csv':__get_cars_temp.__get__(object),
					'cars_precip.csv':__get_cars_precip.__get__(object),
	}

