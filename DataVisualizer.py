import numpy as np
import csv
import matplotlib.pyplot as plt
import matplotlib_scalebar.scalebar as sb
import contextily as ctx
from pyproj import Transformer


# - - - Interpret and sort data - - -
data_file = "Log Files/ts_1778241869.csv"
#data_file = "Log Files/demo.csv"

# GPS data
gps_data1 = []  # Time Epoch
gps_data2 = []  # Latitude
gps_data3 = []  # Longitude
gps_data4 = []  # Altitude (m)
gps_data5 = []  # Velocity (m/s)
gps_data6 = []  # Quality

# Accelerometer data
accel_data1 = []    # Time Epoch
accel_data2 = []    # Sample tick
accel_data3 = []    # Accel X
accel_data4 = []    # Accel Y
accel_data5 = []    # Accel Z

# Gyroscope data
gyro_data1 = []     # Time Epoch
gyro_data2 = []     # Sample tick
gyro_data3 = []     # Pitch
gyro_data4 = []     # Roll
gyro_data5 = []     # Yaw

# data
sensor4_data1 = []  # Time Epoch
sensor4_data2 = []
sensor4_data3 = []
sensor4_data4 = []
sensor4_data5 = []
sensor4_data6 = []

start_time = None
end_time = None

# Read data and sort
with open(data_file, "r") as f:
    reader = csv.reader(f)
    for row in reader:
        #print(row)
        sensor_type = int(row[0])

        if sensor_type == 0:
            gps_data1.append(int(row[1]))
            gps_data2.append(float(row[2]))
            gps_data3.append(float(row[3]))
            gps_data4.append(float(row[4]))
            gps_data5.append(float(row[5]))
            gps_data6.append(int(row[6]))
            
            if start_time is None:
                start_time = int(row[1])
            end_time = int(row[1])
        
        elif sensor_type == 1:
            accel_data1.append(int(row[1]))
            accel_data2.append(int(row[2]))
            accel_data3.append(float(row[3]))
            accel_data4.append(float(row[4]))
            accel_data5.append(float(row[5]))

        elif sensor_type == 2:
            gyro_data1.append(int(row[1]))
            gyro_data2.append(int(row[2]))
            gyro_data3.append(float(row[3]))
            gyro_data4.append(float(row[4]))
            gyro_data5.append(float(row[5]))

        else:
            sensor4_data1.append(int(row[1]))
            sensor4_data2.append(int(row[2]))
            sensor4_data3.append(float(row[3]))
            sensor4_data4.append(float(row[4]))
            sensor4_data5.append(float(row[5]))
            sensor4_data6.append(float(row[5]))

# Measure duration of logging session
duration = end_time - start_time
def print_log_duration():
    minutes, seconds = divmod(duration, 60)
    print(f"Logging lasted: {minutes} minutes and {seconds} seconds")

# - - - Plotting - - -
fig, axs = plt.subplots(3, 1, figsize=(10, 10))  # 3 rows, 1 column
linewidth = 0.5

# Plot GPS Velocity
gps_timestamps = np.linspace(0, duration, len(gps_data5)).tolist()

axs[0].plot(gps_timestamps, gps_data5, linewidth = linewidth, label="Velocity")
axs[0].set_title("Velocity")
axs[0].set_xlabel("( s )")
axs[0].set_ylabel("( km/h )")
axs[0].legend()
axs[0].grid(True)

# Plot Accelerometer
accel_timestamps = np.linspace(0, duration, len(accel_data3)).tolist()

axs[1].plot(accel_timestamps, accel_data3, linewidth = linewidth, label="X")
axs[1].plot(accel_timestamps, accel_data4, linewidth = linewidth, label="Y")
axs[1].plot(accel_timestamps, accel_data5, linewidth = linewidth, label="Z")
axs[1].set_title("Acceleration")
axs[1].set_xlabel("( s )")
axs[1].set_ylabel("( m^2/s )")
axs[1].legend()
axs[1].grid(True)

# Plot Gyro
gyro_timestamps = np.linspace(0, duration, len(gyro_data3)).tolist()

axs[2].plot(gyro_timestamps, gyro_data3, linewidth = linewidth, label="Pitch")
axs[2].plot(gyro_timestamps, gyro_data4, linewidth = linewidth, label="Roll")
axs[2].plot(gyro_timestamps, gyro_data5, linewidth = linewidth, label="Yaw")
axs[2].set_title("Orientation")
axs[2].set_xlabel("( s )")
axs[2].set_ylabel("( deg/s )")
axs[2].legend()
axs[2].grid(True)

plt.tight_layout()


# - - - Plot GPS points on  a map - - -
# Plot GPS track colored by speed on an OpenStreetMap basemap
def plot_gnss_track( latitudes, longitudes, speeds):
    # project the 3D spherical coordinates onto a 2D plane
    transformer = Transformer.from_crs( "EPSG:4326", "EPSG:3857", always_xy=True)
    x, y = transformer.transform(longitudes, latitudes)
    x, y = np.array(x), np.array(y)

    fig, ax = plt.subplots(figsize=(8, 10))
    ax.plot(x, y, color="blue", linewidth=1, alpha=0.7, zorder=3)
    sc = ax.scatter(x, y, c=speeds, s=4, cmap="plasma", zorder=2)
    ctx.add_basemap(ax, source=ctx.providers.Esri.WorldImagery, zoom=18)
    #ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, zoom=14) # need this for the demo data to load
    ax.set_aspect("equal", adjustable="box")
    scalebar = sb.ScaleBar(
        dx=1,              # 1 data unit = 1 meter (EPSG:3857)
        units="m",
        location="lower right",
        box_alpha=0.6
    )
    ax.add_artist(scalebar)
    ax.set_title("Path (colored by speed)")
    ax.set_axis_off() 
    fig.colorbar(sc, ax=ax, label="Speed(km/h)", shrink=0.8)
    fig.tight_layout()
    plt.show()

print_log_duration()
plot_gnss_track( gps_data2, gps_data3, gps_data5)
