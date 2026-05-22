import numpy as np
import matplotlib.pyplot as plt
from ReadData import read_data
from CropData import crop_data

def perform_fft(time_array, signal_array):
    """
    Performs a Fast Fourier Transform on a time-domain signal.
    Applies detrending and windowing for cleaner data.
    """
    signal = np.array(signal_array)
    time = np.array(time_array)
    
    # 1. Detrending: Remove the DC offset (mean). 
    # This is crucial for the Z-axis to remove the constant 1g gravity pull.
    signal = signal - np.mean(signal)

    # 2. Windowing: Apply a Hanning window to reduce spectral leakage.
    # Because our cut time-span isn't perfectly periodic, this prevents smearing.
    N = len(signal)
    window = np.hanning(N)
    signal = signal * window

    # 3. Calculate time step (dt) and Sampling Frequency
    # Using the average time difference between ticks
    dt = np.mean(np.diff(time))
    
    # 4. Perform FFT
    yf = np.fft.fft(signal)
    xf = np.fft.fftfreq(N, dt)[:N//2]
    
    # 5. Calculate normalized magnitude
    magnitude = 2.0/N * np.abs(yf[0:N//2])
    
    return xf, magnitude

def plot_resonances(data):
    # Extract continuous time and signals
    accel_t = data["accel"]["time"]
    accel_z = data["accel"]["z"]
    
    gyro_t = data["gyro"]["time"]
    gyro_pitch = data["gyro"]["pitch"]
    gyro_roll = data["gyro"]["roll"]

    # Compute FFTs
    freq_z, mag_z = perform_fft(accel_t, accel_z)
    freq_pitch, mag_pitch = perform_fft(gyro_t, gyro_pitch)
    freq_roll, mag_roll = perform_fft(gyro_t, gyro_roll)

    # Plotting setup
    fig, axs = plt.subplots(3, 1, figsize=(10, 10), sharex=True)
    linewidth = 1.0

    # Plot Z-Axis Accel
    axs[0].plot(freq_z, mag_z, color='blue', linewidth=linewidth)
    axs[0].set_title("FFT: Accelerometer Z-Axis (Vertical Frame Bending)")
    axs[0].set_ylabel("Amplitude")
    axs[0].grid(True)

    # Plot Pitch Gyro
    axs[1].plot(freq_pitch, mag_pitch, color='red', linewidth=linewidth)
    axs[1].set_title("FFT: Gyroscope Pitch (Front/Back Motor Imbalance)")
    axs[1].set_ylabel("Amplitude")
    axs[1].grid(True)

    # Plot Roll Gyro
    axs[2].plot(freq_roll, mag_roll, color='green', linewidth=linewidth)
    axs[2].set_title("FFT: Gyroscope Roll (Left/Right Motor Imbalance)")
    axs[2].set_xlabel("Frequency (Hz)")
    axs[2].set_ylabel("Amplitude")
    axs[2].grid(True)

    # --- ADJUST FREQUENCY RANGE HERE ---
    # FPV Drone resonances typically fall between 50 Hz and 300 Hz.
    # You can zoom in on the relevant frequencies by uncommenting this:
    # for ax in axs:
    #     ax.set_xlim(0, 250) 

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # 1. Read the file
    data_file = "Log Files/ts_1778239915.csv" # Update to your actual log file
    log = read_data(data_file)
    
    # 2. CROP THE DATA (CRITICAL STEP)
    # You MUST isolate the exact seconds where the 0% to 100% throttle sweep occurs.
    # For example, if the sweep starts at 45 seconds and ends at 60 seconds:
    log = crop_data(log, delta_start=491, delta_end=498) 
    
    # 3. Plot the FFT
    plot_resonances(log)