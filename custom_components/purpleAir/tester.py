from purpleAirData import purpleAirData

def main():
	conditions = []
	for condition in purpleAirData.conditions:
		conditions.append(condition)
	pad = purpleAirData("http://pa.willdarnell.net/json", 30, conditions)
	pad.refreshData()
	print(pad._values)
	
if __name__ == "__main__":
	main()