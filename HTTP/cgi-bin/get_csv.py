import pandas
import io
import sys
import os

def get_bikes_temp():
	
	archive_df = pandas.read_csv('/home/konrad/TrafficForecaster_DB/Archive.csv', index_col='date')
	del archive_df['cars']
	del archive_df['precip']
	
	archive_df = archive_df.dropna()
	
	s = io.StringIO()
	archive_df.to_csv(s, index=False)
	
	csv_str = s.getvalue()
	csv_str = csv_str[:-1]
	
	print('Content-type: text/csv\r\n')
	print(csv_str)
	

def get_bikes_precip():
	
	archive_df = pandas.read_csv('/home/konrad/TrafficForecaster_DB/Archive.csv', index_col='date')
	del archive_df['cars']
	del archive_df['temp']
	
	archive_df = archive_df.dropna()
	
	s = io.StringIO()
	archive_df.to_csv(s, index=False)
	
	csv_str = s.getvalue()
	csv_str = csv_str[:-1]
	
	print('Content-type: text/csv\r\n')
	print(csv_str)
	
def get_cars_temp():
	
	archive_df = pandas.read_csv('/home/konrad/TrafficForecaster_DB/Archive.csv', index_col='date')
	del archive_df['bikes']
	del archive_df['precip']
	
	archive_df = archive_df.dropna()
	
	s = io.StringIO()
	archive_df.to_csv(s, index=False)
	
	csv_str = s.getvalue()
	csv_str = csv_str[:-1]
	
	print('Content-type: text/csv\r\n')
	print(csv_str)
	
def get_cars_precip():
	
	archive_df = pandas.read_csv('/home/konrad/TrafficForecaster_DB/Archive.csv', index_col='date')
	del archive_df['bikes']
	del archive_df['temp']
	
	archive_df = archive_df.dropna()
	
	s = io.StringIO()
	archive_df.to_csv(s, index=False)
	
	csv_str = s.getvalue()
	csv_str = csv_str[:-1]
	
	print('Content-type: text/csv\r\n')
	print(csv_str)

csv_api = { "bikes_temp.csv" : get_bikes_temp,
			"bikes_precip.csv" : get_bikes_precip,
			"cars_temp.csv" : get_cars_temp,
			"cars_precip.csv" : get_cars_precip,
}

def get_csv(path):
	
	if(len(path) >= 3):
		csv_api[path[2]]()
		
#get_csv([' ', ' ', 'cars_precip.csv', '01' , '23' ,'2018', '10', '22'])	
