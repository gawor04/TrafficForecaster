import datetime
import pandas
import io

def get_archive(path):

	if(len(path) >= 8):
		start = path[2] + '-' + path[3] + '-' + path[4]
		stop = path[5] + '-' + path[6] + '-' + path[7]
		dates = pandas.date_range(start, stop).tolist()
		
		archive_df = pandas.read_csv('/home/konrad/TrafficForecaster_DB/Archive.csv', index_col='date')
		archive_df.index = pandas.to_datetime(archive_df.index)
		range_archive_df = archive_df.ix[dates]
		
		range_archive_df['date'] = range_archive_df.index
		
		s = io.StringIO()
		range_archive_df.to_csv(s, index=False)
		
		print('Set-Cookie: fileDownload=true; path=/\r\nContent-type: text/csv\r\nContent-Disposition: attachment; filename=\"archive.csv\"\r\n')
		print(s.getvalue())

#get_archive([' ', ' ', '2018', '01' , '23' ,'2018', '10', '22'])		
