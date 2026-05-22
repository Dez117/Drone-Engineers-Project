import csv
import numpy as np
import time
from CropData import crop_data

# - - - Interpret and sort data by sensor- - -
def read_data(data_file):
    data = {
        "gps": {"epoch": [], "lat": [], "lon": [], "alt": [], "speed": [], "satellites": []}, # m, km/h
        "accel": {"epoch": [], "tick": [], "x": [], "y": [], "z": []},   # m/s^2
        "gyro": {"epoch": [], "tick": [], "roll": [], "pitch": [], "yaw": []}, # rad/s
        "rotation": {"epoch": [], "tick": [], "q_i": [], "q_j": [], "q_k": [], "q_real": []}, # quaternion components

        "meta": {}
    }

    with open(data_file, "r") as f:
        reader = csv.reader(f)

        for row in reader:
            sensor_type = int(row[0])

            if sensor_type == 0:
                data["gps"]["epoch"].append(int(row[1]))
                data["gps"]["lat"].append(float(row[2]))
                data["gps"]["lon"].append(float(row[3]))
                data["gps"]["alt"].append(float(row[4]))
                data["gps"]["speed"].append(float(row[5]))
                data["gps"]["satellites"].append(int(row[6]))
        
            elif sensor_type == 1:
                data["accel"]["epoch"].append(int(row[1]))
                data["accel"]["tick"].append(int(row[2]))
                data["accel"]["x"].append(float(row[3]))
                data["accel"]["y"].append(float(row[4]))
                data["accel"]["z"].append(float(row[5]))

            elif sensor_type == 2:
                data["gyro"]["epoch"].append(int(row[1]))
                data["gyro"]["tick"].append(int(row[2]))
                data["gyro"]["roll"].append(float(row[3]))
                data["gyro"]["pitch"].append(float(row[4]))
                data["gyro"]["yaw"].append(float(row[5]))

            else:
                data["rotation"]["epoch"].append(int(row[1]))
                data["rotation"]["tick"].append(int(row[2]))
                data["rotation"]["q_i"].append(float(row[3]))
                data["rotation"]["q_j"].append(float(row[4]))
                data["rotation"]["q_k"].append(float(row[5]))
                data["rotation"]["q_real"].append(float(row[5]))

    # Create Meta data
    data["meta"]["start_epoch"] = data["gps"]["epoch"][0]
    data["meta"]["end_epoch"] = data["gps"]["epoch"][-1]
    data["meta"]["duration"] = data["gps"]["epoch"][-1] - data["gps"]["epoch"][0]
    
    # Build continous time
    data["accel"]["time"] = data["accel"]["epoch"] + np.array(data["accel"]["tick"]) / 1e6 - data["accel"]["epoch"][0]
    data["gyro"]["time"] = data["gyro"]["epoch"] + np.array(data["gyro"]["tick"]) / 1e6 - data["gyro"]["epoch"][0]
    data["rotation"]["time"] = data["rotation"]["epoch"] + np.array(data["rotation"]["tick"]) / 1e6 - data["rotation"]["epoch"][0]

    return data


# - - - Test code - - -
if __name__ == "__main__": # this stops the code below from running from other files

    data_file = "Log Files/ts_1778239915.csv"
    log = read_data(data_file) 
    #log = crop_data(log, 100, 200)

    sensor = log["gyro"]
    epoch = sensor["epoch"]
    tick = sensor["tick"]
    time_s = sensor["time"]


    for i in range(len(sensor["tick"])):
        print("epoch: ", epoch[i])
        print("tick: ", tick[i])
        print("Time: ", time_s[i])
        print("=================")
        time.sleep(0.1)
