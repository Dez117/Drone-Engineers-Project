import numpy as np
import matplotlib.pyplot as plt
import matplotlib_scalebar.scalebar as sb
import contextily as ctx
from pyproj import Transformer
import time

from ReadData import read_data
from CropData import crop_data

# - - - Plotting - - -
def plot_data(data):
    fig, axs = plt.subplots(3, 1, figsize=(7, 7))  # 3 rows, 1 column
    linewidth = 0.5

    duration = data["meta"]["duration"]


    # - Plot GPS Speed -
    gps = data["gps"]
    gps_timestamps = np.linspace(0, duration, len(gps["speed"]))

    axs[0].plot(gps_timestamps, gps["speed"], linewidth=linewidth, label="Speed")

    axs[0].set_title(" Speed ")
    axs[0].set_xlabel(" seconds ")
    axs[0].set_ylabel(" km/h ")
    axs[0].legend()
    axs[0].grid(True)


    # - Plot Accelerometer -
    accel = data["accel"]
    accel_timestamps = accel["time"]

    axs[1].plot(accel_timestamps, accel["x"], linewidth=linewidth, label="X")
    axs[1].plot(accel_timestamps, accel["y"], linewidth=linewidth, label="Y")
    axs[1].plot(accel_timestamps, accel["z"], linewidth=linewidth, label="Z")

    axs[1].set_title(" Acceleration ")
    axs[1].set_xlabel(" seconds ")
    axs[1].set_ylabel(" m/s^2 ")
    axs[1].legend()
    axs[1].grid(True)


    # - Plot Gyro -
    gyro = data["gyro"]
    gyro_timestamps = gyro["time"]

    axs[2].plot(gyro_timestamps, gyro["roll"], linewidth=linewidth, label="Roll")
    axs[2].plot(gyro_timestamps, gyro["pitch"], linewidth=linewidth, label="Pitch")
    axs[2].plot(gyro_timestamps, gyro["yaw"], linewidth=linewidth, label="Yaw")
    axs[2].set_title(" Orientation ")
    axs[2].set_xlabel(" seconds ")
    axs[2].set_ylabel(" rad/s ")
    axs[2].legend()
    axs[2].grid(True)

    plt.tight_layout()


# - - - Plot GPS points on  a map - - -
# Plot GPS track colored by speed on an OpenStreetMap basemap
def plot_gnss_track(data):
    # import data
    gps = data["gps"]
    latitudes = gps["lat"]
    longitudes = gps["lon"]
    speeds = gps["speed"]

    # project the 3D spherical coordinates onto a 2D plane
    transformer = Transformer.from_crs( "EPSG:4326", "EPSG:3857", always_xy=True)
    x, y = transformer.transform(longitudes, latitudes)
    x, y = np.array(x), np.array(y)

    fig, ax = plt.subplots(figsize=(6, 7))
    ax.plot(x, y, color="white", linewidth=1, alpha=0.7, zorder=2)
    sc = ax.scatter(x, y, c=speeds, s=60, cmap="plasma", zorder=3)
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


# - - - Test code - - -
data_file_1 = "Log Files/ts_1778239915.csv"
data_file_2 = "Log Files/ts_1778241869.csv"
log1 = read_data(data_file_1)


log = log1
log = crop_data(log, 450, 580)
#log = crop_data(log, 491, 498)

minutes, seconds = divmod(log["meta"]["duration"], 60)
print(f"Logging lasted: {minutes} minutes and {seconds} seconds")

plot_data(log)
plot_gnss_track(log)
plt.show()