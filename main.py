from ReadData import read_data
from CropData import crop_data
from DataVisualizer import plot_gnss_track

# 1. Read Log data and create log objects
data_file_1 = "Log Files/ts_1778239915.csv"
data_file_2 = "Log Files/ts_1778241869.csv"

log1 = read_data(data_file_1)
log2 = read_data(data_file_2)


# 2. Crop the files down into their respective throttle sweeps
sweep_25_1 = crop_data(log1, 491, 498)
sweep_50_1 = crop_data(log1, 505, 508)
sweep_75_1 = crop_data(log1, 516, 518)
sweep_100_1 = crop_data(log1, 527, 528)

sweep_25_2 = crop_data(log2, 203, 206)
sweep_50_2 = crop_data(log2, 212, 219)
sweep_75_2 = crop_data(log2, 225, 228)
sweep_100_2 = crop_data(log2, 234, 237)


# 3. (OPTIONAL) View Gps plot if we want i guess
plot_gnss_track(sweep_25_1)


# 4. Convert to FFT and run Welch filtering


# 5. Combine and average throttle sweeps form different logging sessions


# 6. profit