

def get_json(path):
	
	json = open('/home/konrad/TrafficForecaster_DB/forecaster.json', 'r')
	
	print("Content-type: application/json; filename=\"forecaster.json\"\r\n\n\n")
	print(json.read())
