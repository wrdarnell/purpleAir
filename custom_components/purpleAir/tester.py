from purpleAirData import purpleAirData
import time

def main():
	conditions = []
	for condition in purpleAirData.conditions:
		conditions.append(condition)
	pad = purpleAirData("http://pa.willdarnell.net/json", 30, conditions)

	while (1==1):
		print(pad.readings)
		time.sleep(2)
	
if __name__ == "__main__":
	main()