import csv
import numpy as np
import time

# - - - Interpret and sort data by sensor- - -
def read_data(data_file):
    data = {
        "gps": {"time": [], "lat": [], "lon": [], "alt": [], "speed": [], "satellites": []}, # m, km/h
        "accel": {"time": [], "tick": [], "x": [], "y": [], "z": []},   # m/s^2
        "gyro": {"time": [], "tick": [], "roll": [], "pitch": [], "yaw": []}, # rad/s
        "rotation": {"time": [], "tick": [], "q_i": [], "q_j": [], "q_k": [], "q_real": []}, # quaternion components

        "meta": {}
    }

    with open(data_file, "r") as f:
        reader = csv.reader(f)

        for row in reader:
            sensor_type = int(row[0])

            if sensor_type == 0:
                data["gps"]["time"].append(int(row[1]))
                data["gps"]["lat"].append(float(row[2]))
                data["gps"]["lon"].append(float(row[3]))
                data["gps"]["alt"].append(float(row[4]))
                data["gps"]["speed"].append(float(row[5]))
                data["gps"]["satellites"].append(int(row[6]))
        
            elif sensor_type == 1:
                data["accel"]["time"].append(int(row[1]))
                data["accel"]["tick"].append(int(row[2]))
                data["accel"]["x"].append(float(row[3]))
                data["accel"]["y"].append(float(row[4]))
                data["accel"]["z"].append(float(row[5]))

            elif sensor_type == 2:
                data["gyro"]["time"].append(int(row[1]))
                data["gyro"]["tick"].append(int(row[2]))
                data["gyro"]["roll"].append(float(row[3]))
                data["gyro"]["pitch"].append(float(row[4]))
                data["gyro"]["yaw"].append(float(row[5]))

            else:
                data["rotation"]["time"].append(int(row[1]))
                data["rotation"]["tick"].append(int(row[2]))
                data["rotation"]["q_i"].append(float(row[3]))
                data["rotation"]["q_j"].append(float(row[4]))
                data["rotation"]["q_k"].append(float(row[5]))
                data["rotation"]["q_real"].append(float(row[5]))

    # Create Meta data
    data["meta"]["start_time"] = data["gps"]["time"][0]
    data["meta"]["end_time"] = data["gps"]["time"][-1]
    data["meta"]["duration"] = data["gps"]["time"][-1] - data["gps"]["time"][0]
    
    # Create unwrapped tick counters
    data["accel"]["tick_us"] = unwrap_tick(data["accel"])
    data["gyro"]["tick_us"] = unwrap_tick(data["gyro"])
    data["rotation"]["tick_us"] = unwrap_tick(data["rotation"])

    return data


# - - - Convert wrapped tick counter into continuous time - - -
def unwrap_tick(signal, tick_max=1000000):
    tick = np.array(signal["tick"])
    
    delta_tick = np.diff(tick)      # find change in tick
    wrap = delta_tick < 0           # find all locations where tick change is negative (i.e whenever it wraps back to zero)
    delta_tick[wrap] += tick_max    # add 1000000 to tick change everytime it resets (counteract wrapping)
    
    # rebuild the tick array without wrapping
    # start from the first tick value and for each element add the cumulative sum of delta_tick up to that point
    tick_us = np.concatenate(( [tick[0]], tick[0] + np.cumsum(delta_tick) )) 
    return tick_us


# - - - Test code - - -
if __name__ == "__main__": # this stops the code below from running from other files

    data_file = "Log Files/ts_1778241869.csv"
    log = read_data(data_file) 

    sensor = log["accel"]
    epoch = sensor["time"]
    tick = sensor["tick"]
    tick_us = sensor["tick_us"]

    start_time = epoch[0]

    for i in range(len(sensor["tick"])):
        print("epoch: ", epoch[i]-start_time)
        print("tick: ", tick[i])
        print("tick_us: ", tick_us[i]/1000000)
        print("=================")
        time.sleep(0.1)
